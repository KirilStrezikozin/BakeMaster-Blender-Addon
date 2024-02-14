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
import numpy as np
from math import inf, pi
from mathutils import Euler, Vector
from typing import Optional, Set, Tuple

LOT_Status = Tuple[Set[str], Tuple[Set[str], str] | Tuple[()]]
NegInfinity = -inf

_use_debug = False  # internal constant

_decal_view = set()


class BM_OT_DECAL_Enable(bpy.types.Operator):
    bl_label = "Decal Object"
    bl_idname = "bakemaster.decal_enable"
    bl_description = ("Transform the current object into Decal object. Maps "
                      + "will be baked using the custom projection view")
    bl_options = {'UNDO', 'INTERNAL'}

    bm_obj_i: bpy.props.IntProperty(options={'SKIP_SAVE'})  # noqa: F821

    __bm_obj = None
    __message = ("Enabling Decal Object will reset object's\nHigh to Lowpoly "
                 + "configurations.\nContinue?")

    def __unused(self, *args) -> None:
        _ = args

    def show_warning(self, bm_obj) -> bool:
        if bm_obj.hl_use_unique_per_map:
            for map in bm_obj.global_maps:
                if len(map.hl_highpoly_table):
                    return True
        elif len(bm_obj.hl_highpoly_table):
            return True
        return False

    def execute(self, context: bpy.types.Context) -> Set[str] | Set[int]:
        self.__unused(context)

        if self.__bm_obj is None:
            return {'CANCELLED'}

        self.__bm_obj.decal_is_decal = not self.__bm_obj.decal_is_decal
        return {'FINISHED'}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event
               ) -> Set[str] | Set[int]:
        self.__unused(event)

        bm_objs = context.scene.bm_table_of_objects
        assert self.bm_obj_i != -1 and self.bm_obj_i < len(bm_objs)

        self.__bm_obj = bm_objs[self.bm_obj_i]

        if (self.__bm_obj.decal_is_decal
                or not self.show_warning(self.__bm_obj)):
            return self.execute(context)

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context: bpy.types.Context) -> None:
        self.__unused(context)
        col = self.layout.column(align=True)
        for line in self.__message.splitlines():
            col.label(text=line)


class BM_LOT_DECAL_View():
    """
    Decal View Local Operator provides a class-wrapped methods for operating
    Decal Frame Preview. Use by instancing a class and calling its methods.

    Usage:
        1. Call invoke() on instance once to create a decal view.
        2. Call modal() to update the view.
        3. Both invoke() and modal() will cancel the view in case of any error.
            The error message is passed via return status.
        4. Concurrent decal view instances are not allowed, any consequent
            invoke() call will request the first instance to cancel.
        5. To cancel a view, first call request_cancel() on any instance. Then
            call modal() on the instance with the active decal view. Or just
            call cancel() on the instance with active decal view.
        6. When a new active decal view instance is needed, call
            request_cancel() on any and then modal() on the previous active
            instance. If no previous active instance was present, invoke() can
            be just called.

    Accessed by BM_OT_DECAL_View and operator_bake module.
    """

    bm_obj_i = -1
    bm_ctnr_i = -1
    use_obj_res = False

    __user_cam_scale = Vector((1, 1, 1))
    __is_new_cam = True
    __is_cam_removed = False
    __has_r_restore = False

    __old_x = 1
    __old_y = 1
    __old_ax = 1
    __old_ay = 1

    __calc_bounds = True

    def __init__(self, bm_obj_i: int, bm_ctnr_i: int,
                 use_obj_res: bool = False) -> None:
        self.bm_obj_i = bm_obj_i
        self.bm_ctnr_i = bm_ctnr_i
        self.use_obj_res = use_obj_res
        return None

    @classmethod
    def is_running(cls) -> bool:
        global _decal_view
        return len(_decal_view) != 0

    @classmethod
    def is_running_for(cls, obj_name: int) -> bool:
        global _decal_view
        return obj_name in _decal_view

    @classmethod
    def request_cancel(cls) -> None:
        """
        Request the Decal Frame Preview (if any is active) to be cancelled on
        the next modal call.
        """

        global _decal_view
        if len(_decal_view):
            _ = _decal_view.pop()
        return None

    def __unused(self, *args) -> None:
        _ = args
        return None

    def __debug(self, *args, **kwargs) -> None:
        global _use_debug
        if not _use_debug:
            return None
        print(*args, **kwargs)
        return None

    def cancel(self, context: bpy.types.Context) -> None:
        cls = self.__class__
        if cls.is_running():
            self.__view_cancel(context)
        return None

    def __view_poll(self) -> bool:
        cls = self.__class__
        return not cls.is_running()

    def __view_cancel(self, ctx: bpy.types.Context, no_delete: bool = False
                      ) -> None:
        global _decal_view

        self.__toggle_camera(ctx, 'UNSET')
        self.__render_settings(ctx, 'UNSET')

        if len(_decal_view):
            _ = _decal_view.pop()

        self.__debug("Decal view cancelled")
        if not self.__is_new_cam or self.__is_cam_removed or no_delete:
            return None

        try:
            assert isinstance(self.__cam.data, bpy.types.Camera)
            bpy.data.objects.remove(self.__cam)
            # bpy.data.cameras.remove(self.__cam.data)
        except ReferenceError:
            self.__debug("Decal view camera already removed")

        self.__is_cam_removed = True
        return None

    def __render_settings(self, ctx: bpy.types.Context, action: str = 'SET'
                          ) -> None:
        sc = ctx.scene
        r = sc.render

        assert action in {'SET', 'UNSET'}

        if action == 'SET' and not self.__has_r_restore:
            self.__old_x = r.resolution_x
            self.__old_y = r.resolution_y
            self.__old_ax = r.pixel_aspect_x
            self.__old_ay = r.pixel_aspect_y
            self.__old_cam = ctx.scene.camera
            self.__has_r_restore = True
            return None

        if action != 'UNSET' or not self.__has_r_restore:
            return None

        r.resolution_x = self.__old_x
        r.resolution_y = self.__old_y
        r.pixel_aspect_x = self.__old_ax
        r.pixel_aspect_y = self.__old_ay
        sc.camera = self.__old_cam

        if not self.__is_cam_removed:
            try:
                self.__cam.scale = self.__user_cam_scale
            except ReferenceError:
                pass

        self.__has_r_restore = False
        return None

    def __is_camera_view(self, ctx: bpy.types.Context) -> bool:
        if ctx.area is None or ctx.area.type != 'VIEW_3D':
            return False

        space = ctx.area.spaces[0]
        return space.region_3d.view_perspective == 'CAMERA'

    def __toggle_camera(self, ctx: bpy.types.Context, action: str = 'TOGGLE'
                        ) -> None:
        assert action in {'TOGGLE', 'SET', 'UNSET'}

        is_cam_view = self.__is_camera_view(ctx)
        if (action == 'UNSET' and not is_cam_view) or (
                action == 'SET' and is_cam_view):
            return None

        space = ctx.area.spaces[0]
        if space.type != 'VIEW_3D':
            return None

        context_override = ctx.copy()
        assert context_override is not None
        context_override['area'] = ctx.area

        assert bpy.app.version is not None
        if bpy.app.version >= (3, 2, 0):
            with ctx.temp_override(**context_override):
                bpy.ops.view3d.view_camera()
        else:
            bpy.ops.view3d.view_camera(context_override)

        space.region_3d.view_camera_zoom = 0
        space.region_3d.view_camera_offset = Vector((0, 0))

        self.__debug("Decal view camera %s" % action)
        return None

    def __get_cam_scale(self) -> Vector:
        flip_v = (1, -1)[self.__bm_ctnr.decal_use_flip_vertical]
        flip_h = (1, -1)[self.__bm_ctnr.decal_use_flip_horizontal]

        if self.__is_new_cam:
            return Vector((flip_h, flip_v, 1))

        return Vector((self.__user_cam_scale[0] * flip_h,
                       self.__user_cam_scale[1] * flip_v,
                       self.__user_cam_scale[2]))

    def __get_res_container(self):
        if self.use_obj_res:
            bm_obj = self.__bm_obj
        else:
            bm_obj = self.__bm_ctnr

        out_container = bm_obj
        if (bm_obj.out_use_unique_per_map
                and len(bm_obj.global_maps)
                and bm_obj.global_maps_active_index != -1):
            out_container = bm_obj.global_maps[
                bm_obj.global_maps_active_index]

        return out_container

    def __measure_obj_aspect(self, measures: np.ndarray,
                             upper_coord_i: int) -> float:
        """
        Returns height / width aspect ratio.
        """

        if upper_coord_i == 0:
            aspect = measures[2] / measures[1]
        elif upper_coord_i == 1:
            aspect = measures[2] / measures[0]
        elif upper_coord_i == 2:
            aspect = measures[1] / measures[0]
        else:
            raise ValueError("upper_coord_i is invalid %d" % upper_coord_i)

        return float(aspect) or 0.0001  # aspect is of type numpy.float64

    def __get_max_measure(self, measures: np.ndarray,
                          upper_coord_i: int) -> float:
        measures[upper_coord_i] = NegInfinity
        measures[-1] = NegInfinity  # measures is 4d (probably optimization)
        return max(measures)

    def __get_res_aspect(self) -> float:
        """
        Get height / width aspect ratio.
        """

        out_container = self.__get_res_container()

        if out_container.out_res != 'CUSTOM':
            height = width = int(out_container.out_res)
        else:
            height = out_container.out_res_height
            width = out_container.out_res_width

        return height / width

    def __set_out_res(self, aspect: float) -> None:
        if self.__get_res_aspect() == aspect:
            return None

        out_container = self.__get_res_container()
        attr = out_container.decal_aspect_res_attr
        attr1 = 'out_res_%s' % attr

        if out_container.out_res != 'CUSTOM':
            value1 = int(out_container.out_res)
            out_container.out_res = 'CUSTOM'
        else:
            value1 = getattr(out_container, attr1)

        if attr1 == 'out_res_height':
            attr2 = 'out_res_width'
            value2 = int(value1 / aspect)
        elif attr1 == 'out_res_width':
            attr2 = 'out_res_height'
            value2 = int(value1 * aspect)
        else:
            raise ValueError("invalid attr1 value %s" % attr1)

        if getattr(out_container, attr1) != value1:
            setattr(out_container, attr1, value1)
        if getattr(out_container, attr2) != value2:
            setattr(out_container, attr2, value2)

        out_container.decal_aspect_res_attr = attr
        return None

    def __get_cam_res(self) -> Tuple[int, int]:
        out_container = self.__get_res_container()

        ssaa_scale_factor = int(out_container.out_super_sampling_aa)

        if out_container.out_res == 'CUSTOM':
            res_x = out_container.out_res_width
            res_y = out_container.out_res_height
        else:
            res_x = res_y = int(out_container.out_res)

        return res_x * ssaa_scale_factor, res_y * ssaa_scale_factor

    def __update_view(self, ctx: bpy.types.Context) -> LOT_Status:
        try:
            assert isinstance(self.__obj, bpy.types.Object)
            assert isinstance(self.__cam.data, bpy.types.Camera)

        except ReferenceError:
            return ({'CANCELLED'}, ())

        if (not self.__bm_obj.decal_is_decal
                or (self.__bm_ctnr.decal_use_custom_camera
                    and self.__is_new_cam)
                or (self.__bm_ctnr.decal_use_custom_camera
                    and not self.__is_new_cam
                    and self.__bm_ctnr.decal_custom_camera is None)
                or (not self.__bm_ctnr.decal_use_custom_camera
                    and not self.__is_new_cam)):
            return ({'CANCELLED'}, ())

        upper_coord = self.__bm_ctnr.decal_upper_coordinate
        upper_coord_i = ('X', 'Y', 'Z').index(upper_coord[1])

        if self.__calc_bounds:
            if self.__bm_ctnr.decal_use_precise_bounds:
                verts_n = len(self.__obj.data.vertices)

                verts = np.empty((verts_n, 3), dtype=np.float32)
                verts_4d = np.ones((verts_n, 4), dtype=np.float32)

                self.__obj.data.vertices.foreach_get('co', verts.ravel())
                verts_4d[:, :-1] = verts
                del verts

            else:
                verts_n = len(self.__obj.bound_box)
                verts_4d = np.ones((verts_n, 4), dtype=np.float32)

                verts_4d[:, :-1] = self.__obj.bound_box

            verts_4d_world = np.einsum(
                'ij,aj->ai',
                self.__obj.matrix_world,
                verts_4d,
                dtype=np.float64)  # cast to numpy.float32 is invalid

            minmax_coords = np.concatenate(
                [np.max(verts_4d_world, axis=0),
                 np.min(verts_4d_world, axis=0)])
            minmax_coords.shape = (2, 4)

            self.__cam_location = np.average(verts_4d_world, axis=0)[:-1]
            distance = minmax_coords[int(upper_coord[0] == '-')][upper_coord_i]
            self.__cam_location[upper_coord_i] = distance * 1.005

            measures = minmax_coords[0] - minmax_coords[1]
            self.__ortho_scale = self.__get_max_measure(
                measures, upper_coord_i)

            if self.__bm_ctnr.decal_use_adapt_res:
                self.__set_out_res(self.__measure_obj_aspect(
                    measures, upper_coord_i))

            del measures
            del minmax_coords
            del verts_4d

        self.__calc_bounds = not self.__bm_ctnr.decal_use_precise_bounds

        res_x, res_y = self.__get_cam_res()

        r = ctx.scene.render
        r.resolution_x = res_x
        r.resolution_y = res_y
        r.pixel_aspect_x = 1
        r.pixel_aspect_y = 1
        ctx.scene.camera = self.__cam

        self.__cam.scale = self.__get_cam_scale()

        if not self.__is_new_cam:
            return ({'FINISHED'}, ())

        deg_180 = pi
        deg_90 = pi / 2

        cam_rotation = {
            '+X': Vector((deg_90, 0, deg_90)),
            '+Y': Vector((deg_90, 0, deg_180)),
            '+Z': Vector((0, 0, 0)),
            '-X': Vector((deg_90, 0, -1 * deg_90)),
            '-Y': Vector((deg_90, 0, 0)),
            '-Z': Vector((deg_180, 0, 0)),
        }[upper_coord]

        cam_rotation[(1, 2)[upper_coord_i == 2]
                     ] += self.__bm_ctnr.decal_rotation

        self.__cam.location = self.__cam_location
        self.__cam.rotation_euler = Euler(cam_rotation, 'XYZ')
        self.__cam.data.type = 'ORTHO'
        self.__cam.data.clip_start = 0
        self.__cam.data.show_limits = True
        self.__cam.rotation_mode = 'XYZ'
        self.__cam.data.ortho_scale = self.__ortho_scale * (
            self.__bm_ctnr.decal_boundary_offset + 1)

        return ({'FINISHED'}, ())

    def modal(self, ctx: bpy.types.Context,
              event: Optional[bpy.types.Event] = None) -> LOT_Status:
        self.__unused(event)
        cls = self.__class__
        global _decal_view

        bm_active_i = ctx.scene.bm_props.global_active_index
        is_active_bm_obj = (bm_active_i == self.bm_obj_i
                            or bm_active_i == self.bm_ctnr_i)

        assert self.__obj is not None

        try:
            _ = self.__obj.name
        except ReferenceError:
            self.__view_cancel(ctx)
            return (
                {'CANCELLED'},
                ({'INFO'}, "Decal Frame Preview cancelled"))

        if (not cls.is_running_for(self.__obj.name)
                or not self.__is_camera_view(ctx)
                or not is_active_bm_obj):
            self.__view_cancel(ctx)
            return (
                {'CANCELLED'},
                ({'INFO'}, "Decal Frame Preview cancelled"))

        if self.__update_view(ctx)[0] != {'FINISHED'}:
            self.__view_cancel(ctx)
            return (
                {'CANCELLED'},
                ({'INFO'}, "Decal Frame Preview cancelled"))

        assert len(_decal_view) == 1
        return ({'PASS_THROUGH'}, ())

    def execute(self, ctx: bpy.types.Context) -> LOT_Status:
        bm_objs = ctx.scene.bm_table_of_objects

        assert self.bm_obj_i != -1 and self.bm_obj_i < len(bm_objs)
        assert self.bm_ctnr_i != -1 and self.bm_ctnr_i < len(bm_objs)
        self.__bm_obj = bm_objs[self.bm_obj_i]
        self.__bm_ctnr = bm_objs[self.bm_ctnr_i]

        if not self.__bm_obj.decal_is_decal:
            return (
                {'CANCELLED'},
                ({'INFO'}, "Enable Decal Object"))

        dp = ctx.evaluated_depsgraph_get()
        self.__obj = dp.objects.get(self.__bm_obj.global_object_name)

        if self.__obj is None:
            return (
                {'CANCELLED'},
                ({'INFO'}, "Cancelled. Decal object is hidden or invalid"))

        if not self.__bm_ctnr.decal_use_custom_camera:
            __cam_data = bpy.data.cameras.new("bm_camera")

            self.__cam = bpy.data.objects.new("bm_camera", __cam_data)
            self.__cam.rotation_euler = Euler()
            self.__cam.location = Vector()
            self.__is_new_cam = True

            ctx.scene.collection.objects.link(self.__cam)

        elif self.__bm_ctnr.decal_custom_camera is not None:
            self.__cam = self.__bm_ctnr.decal_custom_camera
            self.__user_cam_scale = Vector(self.__cam.scale[:])
            self.__is_new_cam = False

        else:
            return (
                {'CANCELLED'},
                ({'INFO'}, "Cancelled. Choose a camera"))

        self.__render_settings(ctx, 'SET')
        self.__toggle_camera(ctx, 'SET')
        return self.__update_view(ctx)

    def invoke(self, modal_self: bpy.types.Operator | None,
               ctx: bpy.types.Context, event: Optional[bpy.types.Event] = None
               ) -> LOT_Status:
        self.__unused(event)
        global _decal_view

        if not self.__view_poll():
            self.__view_cancel(ctx, no_delete=True)
            return (
                {'CANCELLED'},
                ({'INFO'}, "Another Decal Frame Preview is running"))

        status = self.execute(ctx)

        if status[0] != {'FINISHED'}:
            # self.__view_cancel(context)
            return status

        assert self.__obj is not None
        _decal_view.add(self.__obj.name)

        if modal_self is not None:
            ctx.window_manager.modal_handler_add(modal_self)
            return ({'RUNNING_MODAL'}, ())

        return ({'FINISHED'}, ())


class BM_OT_DECAL_View(bpy.types.Operator):
    bl_label = "Frame Preview"
    bl_idname = "bakemaster.decal_view"
    bl_description = "Preview capture view for this decal"
    bl_options = {'INTERNAL'}

    bm_obj_i: bpy.props.IntProperty(options={'SKIP_SAVE'})  # noqa: F821
    bm_ctnr_i: bpy.props.IntProperty(options={'SKIP_SAVE'})  # noqa: F821

    __lot: BM_LOT_DECAL_View

    @classmethod
    def is_running(cls) -> bool:
        global _decal_view
        return len(_decal_view) != 0

    @classmethod
    def is_running_for(cls, obj_name: int) -> bool:
        global _decal_view
        return obj_name in _decal_view

    @classmethod
    def is_running_for_ctnr(cls, bm_ctnr_i: int) -> bool:
        if not cls.is_running():
            return False

        return cls.__lot.bm_ctnr_i == bm_ctnr_i

    @classmethod
    def request_cancel(cls) -> None:
        """
        Request the Decal Frame Preview (if any is active) to be cancelled on
        the next modal call.
        """

        global _decal_view
        if len(_decal_view):
            _ = _decal_view.pop()
        return None

    def cancel(self, context: bpy.types.Context) -> None:
        cls = self.__class__
        if cls.is_running():
            cls.__lot.cancel(context)
        return None

    def modal(self, context: bpy.types.Context, event: bpy.types.Event
              ) -> Set[str] | Set[int]:
        cls = self.__class__

        status = cls.__lot.modal(context, event)
        if status[0] == {'PASS_THROUGH'}:
            return status[0]

        if status[1]:
            self.report(status[1][0], status[1][1])
        return status[0]

    def execute(self, context: bpy.types.Context) -> Set[str] | Set[int]:
        cls = self.__class__

        status = cls.__lot.execute(context)

        if status[0] == {'FINISHED'}:
            return status[0]

        if status[1]:
            self.report(status[1][0], status[1][1])
        return status[0]

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event
               ) -> Set[str] | Set[int]:
        cls = self.__class__

        if cls.is_running():
            cls.__lot.cancel(context)
            return {'CANCELLED'}

        cls.__lot = BM_LOT_DECAL_View(self.bm_obj_i, self.bm_ctnr_i)
        status = cls.__lot.invoke(self, context, event)

        if status[0] == {'RUNNING_MODAL'}:
            return {'RUNNING_MODAL'}

        if status[1]:
            self.report(status[1][0], status[1][1])
        return status[0]
