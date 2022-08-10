# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from .utils import BM_ITEM_OverwriteUpdate, BM_ITEM_RemoveLocalPreviews
from .labels import BM_Labels

class BM_OT_AOL(bpy.types.Operator):
    bl_idname = 'bakemaster.aol'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_AOL_SELF_DESCRIPTION

    control : bpy.props.EnumProperty(
        items = [('UP', "Up", ""), ('DOWN', "Down", "")])

    def invoke(self, context, event):
        scene = context.scene
        a_index = scene.bm_props.active_index

        try:
            scene.bm_aol[a_index]
        except IndexError:
            pass
        else:
            if self.control == 'UP' and a_index >= 1:
                scene.bm_aol.move(a_index, a_index - 1)
                scene.bm_props.active_index -= 1

            elif self.control == 'DOWN' and a_index < len(scene.bm_aol) - 1:
                scene.bm_aol.move(a_index, a_index + 1)
                scene.bm_props.active_index += 1
        return {'FINISHED'}

class BM_OT_AOL_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.aol_add'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_AOL_ADD_DESCRIPTION

    def execute(self, context):
        scene = context.scene
        mesh = True
        exists = False

        if context.object:
            for ob in context.selected_objects:
                if ob.type == 'MESH':
                    items = []
                    items_data = []

                    for index, item in enumerate(scene.bm_aol):
                        items.append(item.object_pointer)
                        items_data.append(item.object_pointer.data)

                    if ob not in items and ob.data not in items_data:
                        new_item = scene.bm_aol.add()
                        new_item.object_pointer = ob
                        scene.bm_props.active_index = len(scene.bm_aol) - 1
                    else:
                        exists = True
                else:
                    mesh = False

            if exists:
                self.report({'INFO'}, BM_Labels.INFO_ITEM_EXISTS)               
            if not mesh:
                self.report({'INFO'}, BM_Labels.INFO_ITEM_NONMESH)
            if len(context.selected_objects) == 0:
                self.report({'INFO'}, "")
        return {'FINISHED'}

class BM_OT_AOL_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.aol_remove'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_AOL_REMOVE_DESCRIPTION

    def execute(self, context):
        scene = context.scene
        a_index = scene.bm_props.active_index

        if len(scene.bm_aol):
            if scene.bm_props.active_index != 0:
                scene.bm_props.active_index -= 1

            item = scene.bm_aol[a_index]
            item.use_target = False
            
            if item.use_source:
                for index1, item1 in enumerate(scene.bm_aol):
                        if item.source_name == item1.object_pointer.name:
                            item1.source = 'NONE'
                            break

            scene.bm_aol.remove(a_index)
        return {'FINISHED'}

class BM_OT_AOL_Refresh(bpy.types.Operator):
    bl_idname = 'bakemaster.aol_refresh'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_AOL_REFRESH_DESCRIPTION

    def execute(self, context):
        scene = context.scene
        to_remove = []

        for index, item in enumerate(scene.bm_aol):
            try:
                scene.objects[item.object_pointer.name]
            except (KeyError, AttributeError):
                to_remove.append(index)
                item.use_target = False

                if item.use_source:
                    for index1, item1 in enumerate(scene.bm_aol):
                        if item.source_name == item1.object_pointer.name:
                            item1.source = 'NONE'
                            break

        to_remove.sort(reverse = True)

        for index in to_remove[::1]:
            scene.bm_aol.remove(index)

        a_index = scene.bm_props.active_index
        a_len = len(scene.bm_aol) - 1
        scene.bm_props.active_index = a_len if a_index > a_len else a_index
        return {'FINISHED'}

class BM_OT_AOL_Trash(bpy.types.Operator):
    bl_idname = 'bakemaster.aol_trash'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_AOL_TRASH_DESCRIPTION

    def execute(self, context):
        to_remove = []

        for index, item in enumerate(context.scene.bm_aol):
            to_remove.append(index)

        for index in to_remove[::-1]:
            context.scene.bm_aol.remove(index)

        context.scene.bm_props.active_index = 0
        context.scene.bm_props.bake_available = True
        return {'FINISHED'}

class BM_OT_ITEM_Maps(bpy.types.Operator):
    bl_idname = 'bakemaster.item_maps'
    bl_label = ""
    bl_description = BM_Labels.OPERATOR_ITEM_MAPS_DESCRIPTION

    control : bpy.props.EnumProperty(
        items = [('ADD', "Add", ""), ('REMOVE', "Remove", ""), ('TRASH', "Trash", "")])

    def invoke(self, context, event):
        item = context.scene.bm_aol[context.scene.bm_props.active_index]
        a_index = item.maps_active_index

        try:
            item.maps[a_index]
        except IndexError:
            pass
        else:
            if self.control == 'REMOVE' or self.control == 'TRASH':
                BM_ITEM_RemoveLocalPreviews(item, context)

            if self.control == 'REMOVE':
                if item.maps_active_index != 0:
                    item.maps_active_index -= 1

                item.maps.remove(a_index)
                
            elif self.control == 'TRASH':
                to_remove = []

                for index, map in enumerate(item.maps):
                    to_remove.append(index)

                for index in to_remove[::-1]:
                    item.maps.remove(index)

                item.maps_active_index = 0

        if self.control == 'ADD':
            new_pass = item.maps.add()
            new_pass.map_type = 'ALBEDO'
            item.maps_active_index = len(item.maps) - 1
            BM_ITEM_OverwriteUpdate(item, context)

        return {'FINISHED'}