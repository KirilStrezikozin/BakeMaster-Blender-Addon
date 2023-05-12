# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This License permits you to use this software for any purpose including
# personal, educational, and commercial; You are allowed to modify it to suit
# your needs, and to redistribute the software or any modifications you make
# to it, as long as you follow the terms of this License and the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This License grants permission to redistribute this software to
# UNLIMITED END USER SEATS (OPEN SOURCE VARIANT) defined by the
# acquired License type. A redistributed copy of this software
# must follow and share similar rights of free software and usage
# specifications determined by the GNU General Public License.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License in
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# ##### END LICENSE BLOCK #####

from bpy.types import Operator
from bpy.props import (
    IntProperty,
    BoolProperty,
    StringProperty,
)


class BM_OT_BakeJob_Add(Operator):
    bl_idname = 'bakemaster.bakejob_add'
    bl_label = "Add"
    bl_description = "Add a new BakeJob"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakemaster.wh_disable_drag(bakemaster, "bakejobs")

        new_bakejob = bakemaster.bakejobs.add()
        new_bakejob.index = bakemaster.bakejobs_len
        new_bakejob.name = "BakeJob %d" % (new_bakejob.index + 1)
        new_bakejob.type = bakemaster.get_pref(context, 'bakejob_type')

        bakemaster.bakejobs_active_index = new_bakejob.index
        bakemaster.bakejobs_len += 1

        bakemaster.wh_recalc_indexes(bakemaster, "bakejobs")
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_BakeJob_Remove(Operator):
    bl_idname = 'bakemaster.bakejob_remove'
    bl_label = "Remove"
    bl_description = "Remove selected BakeJobs from the list on the left"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        status, message = bakemaster.wh_remove(bakemaster, "bakejobs",
                                               self.index)

        if message:
            self.report({'INFO'}, message)
        return status

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_BakeJob_Trash(Operator):
    bl_idname = 'bakemaster.bakejob_trash'
    bl_label = "Trash"
    bl_description = "Remove all BakeJobs from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, _):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        return bakemaster.wh_trash(bakemaster, "bakejobs")


class BM_OT_BakeJob_Rename(Operator):
    bl_idname = 'bakemaster.bakejob_rename'
    bl_label = "Rename"
    bl_description = "Double click to rename the BakeJob"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    new_name: StringProperty(
        name="New name",
        description="Enter new name",
        default="",
        options={'SKIP_SAVE'})

    bakejob = None

    def execute(self, _):
        if self.bakejob is None:
            return {'CANCELLED'}

        self.bakejob.name = self.new_name
        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        self.bakejob = bakemaster.get_bakejob(bakemaster, self.index)
        if self.bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}

        self.new_name = self.bakejob.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        self.layout.prop(self, "new_name")


class BM_OT_BakeJob_Change_Type(Operator):
    bl_idname = 'bakemaster.bakejob_change_type'
    bl_label = "BakeJob Type"
    bl_description = "Change BakeJob type"
    bl_options = {'INTERNAL', 'UNDO'}

    def type_objects_update(self, _):
        if self.type_maps is not self.type_objects:
            return
        self.type_maps = not self.type_objects

    def type_maps_update(self, _):
        if self.type_objects is not self.type_maps:
            return
        self.type_objects = not self.type_maps

    index: IntProperty(default=-1)

    type_objects: BoolProperty(
        name="Objects",
        description="BakeJob will contain Objects, where each of them will contain Maps",  # noqa: E501
        default=True,
        update=type_objects_update,
        options={'SKIP_SAVE'})

    type_maps: BoolProperty(
        name="Maps",
        description="BakeJob will contain Maps, where each of them will contain Objects the Map will be baked for",  # noqa: E501
        default=False,
        update=type_maps_update,
        options={'SKIP_SAVE'})

    bakejob = None

    def execute(self, _):
        if self.bakejob is None:
            return {'CANCELLED'}

        if self.type_objects:
            self.bakejob.type = 'OBJECTS'
        else:
            self.bakejob.type = 'MAPS'
        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        self.bakejob = bakemaster.get_bakejob(bakemaster, self.index)
        if self.bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}

        if self.bakejob.type == 'OBJECTS':
            self.type_objects = True
            self.type_maps = False
        else:
            self.type_objects = False
            self.type_maps = True

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=100)

    def draw(self, context):
        bakemaster = context.scene.bakemaster

        icon_objects = bakemaster.get_icon('OBJECTS')

        col = self.layout.column(align=True)
        col.prop(self, "type_objects", icon_value=icon_objects)
        col.prop(self, "type_maps", icon='RENDERLAYERS')


class BM_OT_BakeJob_Merge(Operator):
    bl_idname = 'bakemaster.bakejob_merge'
    bl_label = "Merge selected BakeJobs"
    bl_description = "Merge selected BakeJobs into the active one that will contain all the items"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob = None

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        if self.bakejob is None:
            return {'CANCELLED'}

        to_remove = []
        for bakejob in bakemaster.bakejobs:
            if not bakejob.is_selected:
                continue
            elif bakejob.index == self.bakejob.index:
                continue
            elif bakejob.type != self.bakejob.type:
                self.report({'INFO'},
                            "Selected BakeJobs must be of the same type")
                return {'CANCELLED'}

            to_remove.append(bakejob.index)

        if len(to_remove) < 2:
            self.report({'INFO'},
                        "Merge requires two or more selected BakeJobs")
            return {'CANCELLED'}

        for index in reversed(to_remove):
            for container in bakemaster.bakejobs[index]:
                _ = bakemaster.wh_copy(container, self.bakejob.containers)
            bakemaster.bakejobs.remove(index)

        bakemaster.bakejobs_active_index = self.bakejob.index
        bakemaster.bakejobs_len = len(bakemaster.bakejobs)

        bakemaster.wh_disable_ms("bakejobs")
        bakemaster.wh_recalc_indexes(bakemaster, "bakejobs")
        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        if not bakemaster.wh_has_ms(bakemaster, "bakejobs"):
            self.report({'INFO'},
                        "Select BakeJobs with Shift, Ctrl")
            return {'CANCELLED'}

        self.bakejob = bakemaster.get_bakejob(bakemaster)
        if self.bakejob is None:
            self.report({'INFO'},
                        "No active BakeJob (select it with Ctrl)")
            return {'CANCELLED'}

        return self.execute(context)
