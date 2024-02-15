# BEGIN LICENSE & COPYRIGHT BLOCK.
#
# Copyright (C) 2022-2024 Kiril Strezikozin
# BakeMaster Blender Add-on (version 2.6.0)
#
# This file is a part of BakeMaster Blender Add-on, a plugin for texture
# baking in open-source Blender 3d modelling software.
# The author can be contacted at <kirilstrezikozin@gmail.com>.
#
# Redistribution and use for any purpose including personal, educational, and
# commercial, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. The current acquired License allows copies/redistributions of this
#    software be made to UNLIMITED END USER SEATS (OPEN SOURCE LICENSE).
# 2. Redistributions of this source code or partial usage of this source code
#    must follow the terms of this license and retain the above copyright
#    notice, and the following disclaimer.
# 3. The name of the author may be used to endorse or promote products derived
#    from this software. In such a case, a prior written permission from the
#    author is required.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# You should have received a copy of the GNU General Public License in the
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# END LICENSE & COPYRIGHT BLOCK.

import bpy
import gpu
import numpy as np
from math import inf
from typing import Literal, Tuple, Set
from gpu_extras.batch import batch_for_shader


Infinity = inf

bpy_t = bpy.types
gpu_t = gpu.types
np_arr = np.ndarray

_cage_shaders = set()


def eval_mesh_data(context: bpy_t.Context, obj: bpy_t.Object
                   ) -> Tuple[np_arr, np_arr, np_arr, np_arr]:

    assert obj.type == 'MESH', "Object is not MESH at shader.eval_mesh_data()"

    dg = context.evaluated_depsgraph_get()
    obj_eval = dg.objects.get(obj.name)

    assert isinstance(obj_eval, bpy.types.Object)

    mesh = obj_eval.data
    mesh.calc_loop_triangles()

    coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', coords)
    coords.shape = (-1, 3)

    normals = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('normal', normals)
    normals.shape = (-1, 3)

    indices = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
    mesh.loop_triangles.foreach_get('vertices', indices)
    indices.shape = (-1, 3)

    edges = np.empty(len(mesh.edges) * 2, dtype=np.int32)
    mesh.edges.foreach_get("vertices", edges)
    edges.shape = (-1, 2)

    return coords, normals, indices, edges


def cage() -> gpu_t.GPUShader:
    vertex_source = """
    in vec3 position;
    in vec3 normal;

    uniform mat4 viewProjectionMatrix;
    uniform mat4 objProjectionMatrix;
    uniform float extrusion;
    uniform vec4 color;

    out vec4 fcolor;

    void main() {
      gl_Position = viewProjectionMatrix * objProjectionMatrix * vec4(
        position + normal * extrusion, 1.0f);

      fcolor = color;
    }
    """

    fragment_source = """
    in vec4 fcolor;
    out vec4 FragColor;

    void main() {
      FragColor = blender_srgb_to_framebuffer_space(fcolor);
    }
    """

    shader = gpu_t.GPUShader(vertex_source, fragment_source)
    return shader


def cage_batch(
        shader: gpu_t.GPUShader,
        coords: np_arr,
        normals: np_arr,
        indices: np_arr,
        draw_type: Literal['TRIS', 'LINES']) -> gpu_t.GPUBatch:

    batch = batch_for_shader(
        shader, draw_type,
        {"position": coords, "normal": normals},
        indices=indices)

    return batch


def cage_draw(
        _: bpy_t.Context,
        obj: bpy_t.Object,
        bm_struct: bpy_t.PropertyGroup | None,
        batch_solid: gpu_t.GPUBatch,
        batch_wire: gpu_t.GPUBatch,
        shader: gpu_t.GPUShader,
        color_solid: Tuple[float, float, float, float],
        color_wire: Tuple[float, float, float, float],
        dflt_extr: float) -> None:

    matrix = bpy.context.region_data.perspective_matrix

    shader.bind()
    shader.uniform_float("viewProjectionMatrix", matrix)
    shader.uniform_float("objProjectionMatrix", obj.matrix_world)

    extrusion = dflt_extr
    if bm_struct is not None:
        if bpy.app.version >= (2, 90, 0):
            extrusion = min(
                bm_struct.hl_cage_extrusion,
                bm_struct.hl_max_ray_distance or Infinity)
        else:
            extrusion = bm_struct.hl_cage_extrusion

    shader.uniform_float("extrusion", extrusion)

    gpu.state.depth_test_set('LESS')
    gpu.state.blend_set('NONE')

    shader.uniform_float("color", color_solid)
    batch_solid.draw(shader)

    gpu.state.line_width_set(2.0)
    shader.uniform_float("color", color_wire)
    batch_wire.draw(shader)
    gpu.state.line_width_set(1.0)

    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')

    global _cage_shaders
    assert len(_cage_shaders) == 1

    return None


class BM_OT_Shader_Cage(bpy_t.Operator):
    bl_idname = 'bakemaster.shader_cage'
    bl_label = "Cage Preview"
    bl_description = "Preview extruded cage in the viewport"
    bl_options = {'INTERNAL'}

    obj_name: bpy.props.StringProperty(
        default="",
        options={'SKIP_SAVE'})  # noqa: F821

    default_extrusion: bpy.props.FloatProperty(
        default=0.1,
        options={'SKIP_SAVE'})  # noqa: F821

    allow_switch: bpy.props.BoolProperty(
        default=False,
        options={'SKIP_SAVE'})  # noqa: F821

    bm_obj_i: bpy.props.IntProperty(
        default=-1,
        options={'SKIP_SAVE'})  # noqa: F821

    bm_map_i: bpy.props.IntProperty(
        default=-1,
        options={'SKIP_SAVE'})  # noqa: F821

    __obj = None
    __shader = None
    __bm_struct = None
    __batch_wire = None
    __batch_solid = None
    __obj_is_visible = False

    __draw_handler = None
    __debug = False  # internal constant

    @classmethod
    def is_running(cls) -> bool:
        global _cage_shaders
        return len(_cage_shaders) != 0

    @classmethod
    def is_running_for(cls, obj_name: str) -> bool:
        global _cage_shaders
        return obj_name in _cage_shaders

    def debug(self, *args, **kwargs) -> None:
        if not self.__debug:
            return None
        print(*args, **kwargs)
        return None

    def cancel(self, context: bpy_t.Context) -> None:
        cls = self.__class__
        if cls.is_running():
            self.draw_cancel(context)
        return None

    def get_colors(self, context: bpy_t.Context
                   ) -> Tuple[Tuple[float, float, float, float],
                              Tuple[float, float, float, float]]:
        color_solid = context.scene.bm_props.global_cage_color_solid
        color_wire = context.scene.bm_props.global_cage_color_wire
        return color_solid, color_wire

    def get_bm_struct(self, context: bpy_t.Context
                      ) -> bpy_t.PropertyGroup | None:
        if self.bm_obj_i == -1:
            self.report(
                {'WARNING'},
                (f"Cage Shader ({self}) expected bm_obj_i, extrusion value "
                 "will not update"))
            return None

        bm_objs = context.scene.bm_table_of_objects
        bm_obj = bm_objs[self.bm_obj_i]

        if not bm_obj.hl_use_unique_per_map:
            return bm_obj

        assert self.bm_map_i != -1, "Cage Shader expected bm_map_i"
        bm_map = bm_obj.global_maps[self.bm_map_i]
        return bm_map

    def draw_poll(self) -> bool:
        cls = self.__class__
        return not cls.is_running()

    def redraw(self, context: bpy_t.Context) -> None:
        for area in context.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            area.tag_redraw()
        return None

    def draw_cancel(self, context: bpy_t.Context) -> None:
        cls = self.__class__

        self.debug("Cage Preview handler is", cls.__draw_handler)

        if cls.__draw_handler is not None:
            bpy_t.SpaceView3D.draw_handler_remove(cls.__draw_handler, 'WINDOW')
            cls.__draw_handler = None
            self.debug("Cage Preview handler freed")
        else:
            self.debug("Cage Preview handler was already freed")

        self.redraw(context)

        global _cage_shaders
        if len(_cage_shaders):
            _ = _cage_shaders.pop()

        return None

    def update_cage(self, context: bpy_t.Context) -> Set[str]:
        if self.__bm_struct is None:
            return {'PASS_THROUGH'}

        bm_struct = self.__bm_struct
        has_cage = bm_struct.hl_use_cage and bm_struct.hl_cage != 'NONE'

        bm_obj = context.scene.bm_table_of_objects[self.bm_obj_i]
        obj_name = bm_obj.global_object_name
        req_name = bm_struct.hl_cage if has_cage else obj_name

        if req_name == self.__obj.name:
            return {'PASS_THROUGH'}

        self.draw_cancel(context)
        self.obj_name = req_name

        status = self.execute(context)

        if status == {'RUNNING_MODAL'}:
            status = {'PASS_THROUGH'}

        return status

    def modal(self, context: bpy_t.Context, _: bpy_t.Event) -> Set[str]:
        cls = self.__class__

        if (cls.__draw_handler is None
                or not cls.is_running_for(self.__obj.name)):
            # self.draw_cancel(context)
            self.debug("Cage Preview cancelled")
            return {'CANCELLED'}

        status = self.update_cage(context)

        global _cage_shaders
        assert len(_cage_shaders) == 1

        return status

    def execute(self, context: bpy_t.Context) -> Set[str]:
        cls = self.__class__
        assert cls.__draw_handler is None

        self.__obj = context.scene.objects.get(self.obj_name, None)
        if (self.__obj is None or self.__obj.type != 'MESH'):
            self.report({'ERROR'}, "Expected Mesh object")
            return {'CANCELLED'}

        self.debug("Cage Preview started")

        self.__bm_struct = self.get_bm_struct(context)

        self.__obj_is_visible = self.__obj.visible_get()
        self.__obj.hide_set(False)

        self.__shader = cage()
        co, nm, i, e = eval_mesh_data(context, self.__obj)
        self.__batch_solid = cage_batch(self.__shader, co, nm, i, 'TRIS')
        self.__batch_wire = cage_batch(self.__shader, co, nm, e, 'LINES')
        self.__obj.hide_set(not self.__obj_is_visible)

        color_solid, color_wire = self.get_colors(context)

        draw_args = (
            context,
            self.__obj,
            self.__bm_struct,
            self.__batch_solid,
            self.__batch_wire,
            self.__shader,
            color_solid,
            color_wire,
            self.default_extrusion)

        cls.__draw_handler = bpy_t.SpaceView3D.draw_handler_add(
            cage_draw,
            draw_args,
            'WINDOW',
            'POST_VIEW')

        self.redraw(context)

        global _cage_shaders
        _cage_shaders.add(self.__obj.name)
        return {'RUNNING_MODAL'}

    def invoke(self, context: bpy_t.Context, _: bpy_t.Event) -> Set[str]:
        shader_free = self.draw_poll()

        if not shader_free:
            self.draw_cancel(context)
            if not self.allow_switch:
                self.debug("Cage Preview turned off")
                return {'FINISHED'}

        status = self.execute(context)

        if status == {'RUNNING_MODAL'}:
            context.window_manager.modal_handler_add(self)

        return status


if __name__ == "__main__":
    bpy.utils.register_class(BM_OT_Shader_Cage)
    bpy.ops.bakemaster.shader_cage(
        'INVOKE_DEFAULT',
        obj_name=bpy.context.active_object.name,
        default_extrusion=0.1)
