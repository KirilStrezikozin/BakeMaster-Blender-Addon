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

import typing

from datetime import datetime

from bpy.types import Context, Event, Operator

from bpy.props import (
    IntProperty,
    EnumProperty,
    BoolProperty,
)

from bpy_extras.io_utils import ImportHelper


# class F():


def _ui_bake_poll(bakemaster, bake_is_running: bool
                  ) -> typing.Tuple[bool, str]:
    if bake_is_running:
        message = "Another bake is running"
        bakemaster.log("o4x0000", message)
        return False, message

    if any([bakemaster.bake_trigger_cancel,
            bakemaster.bake_trigger_stop]):
        message = "Bake is not available"
        bakemaster.log("o4x0000", message)
        return False, message

    return True, ""


def _ui_bakehistory_poll(ot_instance, bakemaster) -> typing.Tuple[bool, str]:
    if ot_instance.index == -1:
        message = "Internal Error: Cannot resolve item in Bake History"
        bakemaster.log("o4x0001", message)
        return False, message

    try:
        bakehistory = bakemaster.bakehistory[ot_instance.index]
    except IndexError:
        message = "Internal Error: Cannot resolve item in Bake History"
        bakemaster.log("o4x0001", message)
        return False, message

    if bakemaster.bakehistory_reserved_index == bakehistory.index:
        message = "Item in Bake History is currently baking"
        bakemaster.log("o4x0001", message)
        return False, message

    return True, ""


def _bakehistory_add_entry(bakemaster):
    new_item = bakemaster.bakehistory.add()
    new_item.index = bakemaster.bakehistory_len
    new_item.name += " %d" % (new_item.index + 1)
    bakemaster.bakehistory_len += 1
    bakemaster.bakehistory_reserved_index = new_item.index


def _bakehistory_remove_entry(bakemaster, remove_index: int):
    if bakemaster.bakehistory_reserved_index > remove_index:
        bakemaster.bakehistory_reserved_index -= 1
    for index in range(remove_index + 1, bakemaster.bakehistory_len):
        bakemaster.bakehistory[index].index -= 1
    bakemaster.bakehistory.remove(remove_index)
    bakemaster.bakehistory_len -= 1


def _bakehistory_unblock_reserved_entry(bakemaster):
    if bakemaster.bakehistory_reserved_index == -1:
        return

    try:
        bakehistory = bakemaster.bakehistory[
            bakemaster.bakehistory_reserved_index]
    except IndexError:
        bakehistory = None

    if bakehistory is not None:
        bakehistory.time_stamp = str(datetime.now())

    bakemaster.bakehistory_reserved_index = -1


class BM_OT_UI_Bake_Generic(Operator):
    # For inheritance.

    bl_options = {'INTERNAL'}

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = True

    def bake_poll(self, context):
        bakemaster = context.scene.bakemaster

        bake_is_running = bakemaster.bake_is_running
        poll_success, message = _ui_bake_poll(bakemaster, bake_is_running)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True


class BM_OT_Bake_Config(Operator, ImportHelper):
    bl_idname = 'bakemaster.bake_config'
    bl_label = "Config"
    bl_description = "Load/Save/Detach Bake Configuration data. You can use config as a super preset that holds all settings and tables' items of the current BakeMaster session"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        name="Action",
        description="Choose an action for the config. Hover over values to see descriptions",  # noqa: E501
        default='LOAD',
        items=[('LOAD', "Load", ""),
               ('SAVE', "Save", ""),
               ('DETACH', "Detach", "")],
        options={'SKIP_SAVE'})

    # filepath: StringProperty(
    #     name="Filepath",
    #     description="Where to Save/Load a config from",
    #     default="",
    #     subtype='DIR_PATH')

    def execute(self, context: Context) -> set:
        bakemaster = context.scene.bakemaster

        bakemaster.config_is_attached = self.action != 'DETACH'
        if self.filepath != "":
            bakemaster.config_filepath = self.filepath

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context: Context, event: Event) -> set:
        if self.action == 'DETACH':
            return self.execute(context)

        return super().invoke(context, event)


class BM_OT_Bake_One(BM_OT_UI_Bake_Generic):
    bl_idname = 'bakemaster.bake_one'
    bl_label = "Bake One"
    bl_description = "Choose to bake only selected Maps, Objects, or BakeJobs"  # noqa: E501

    action: EnumProperty(
        name="Choose an operation",
        description="Choose what to bake",
        default='BAKEJOB',
        items=[('MAP', "Map", "Bake selected Maps"),
               ('OBJECT', "Object", "Bake selected Objects"),
               ('BAKEJOB', "Bake Job", "Bake selected BakeJobs")])

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        _bakehistory_add_entry(bakemaster)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.bake_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        row = self.layout.row(align=True)
        row.prop(self, 'action', expand=True)


class BM_OT_Bake_All(Operator):
    bl_idname = 'bakemaster.bake_all'
    bl_label = "Bake All"
    bl_description = "Bake the whole setup (all BakeJobs, all Maps for all Objects)"  # noqa: E501
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        _bakehistory_add_entry(bakemaster)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.bake_poll(context):
            return {'CANCELLED'}

        return self.execute(context)


class BM_OT_Bake_Toggle_Pause(Operator):
    bl_idname = 'bakemaster.bake_toggle_pause'
    bl_label = "Pause/Resume"
    bl_description = "Pause/Resume the bake"
    bl_options = {'INTERNAL'}

    def pause_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, _ = _ui_bake_poll(bakemaster, not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        is_paused = bakemaster.bake_hold_on_pause
        bakemaster.bake_hold_on_pause = not is_paused

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.pause_poll(context):
            return {'CANCELLED'}

        return self.execute(context)


class BM_OT_Bake_Stop(Operator):
    bl_idname = 'bakemaster.bake_stop'
    bl_label = "Stop"
    bl_description = "Stop and save what's been baked"
    bl_options = {'INTERNAL'}

    def stop_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, _ = _ui_bake_poll(bakemaster, not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = True
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        _bakehistory_unblock_reserved_entry(bakemaster)
        bakemaster.bake_trigger_stop = False

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.stop_poll(context):
            return {'CANCELLED'}

        return self.execute(context)


class BM_OT_Bake_Cancel(Operator):
    bl_idname = 'bakemaster.bake_cancel'
    bl_label = "Cancel"
    bl_description = "Cancel - stop and erase what's been baked"
    bl_options = {'INTERNAL'}

    def cancel_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, _ = _ui_bake_poll(bakemaster, not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = True
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        _bakehistory_unblock_reserved_entry(bakemaster)
        bakemaster.bake_trigger_cancel = False

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.cancel_poll(context):
            return {'CANCELLED'}

        return self.execute(context)


class BM_OT_BakeHistory_Rebake(Operator):
    bl_idname = 'bakemaster.bakehistory_rebake'
    bl_label = "Rebake"
    bl_description = "Rebake content of this bake in the history"
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    action: EnumProperty(
        name="Action",
        description="Choose how to rebake content of this bake in the history",  # noqa: E501
        default='NEW_BAKE',
        items=[('NEW_BAKE', "New Bake Output", "Rebake all content of this bake in the history without deleting its initially baked files"),  # noqa: E501
               ('FULL_OVERWRITE', "Full Overwrite", "Rebake and overwrite all initially baked content of this bake in the history"),  # noqa: E501
               ('SMART_OVERWRITE', "Smart Rebake", "Compare baked content of this bake in the history and the current setup and settings. Bake what's been added and rebake what's changed")])  # noqa: E501

    def rebake_poll(self, context):
        bakemaster = context.scene.bakemaster

        poll_success, message = _ui_bakehistory_poll(self, bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False

        bake_is_running = bakemaster.bake_is_running
        poll_success, message = _ui_bake_poll(bakemaster, bake_is_running)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def execute(self, _):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.rebake_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, 'action')


class BM_OT_BakeHistory_Config(Operator):
    bl_idname = 'bakemaster.bakehistory_config'
    bl_label = "Load Settings"
    bl_description = "Replace all current settings and setup (e.g. BakeJobs, Objects, Maps, all settings) or Save the settings and setup of this bake in the history"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    action: EnumProperty(
        name="Action",
        description="What to do with the settings and setup of this bake in the history",  # noqa: E501
        default='REPLACE',
        items=[('REPLACE', "Replace", "Replace all current settings and setup (e.g. BakeJobs, Objects, Maps, all settings) with the settings and setup of this bake in the history"),  # noqa: E501
               ('SAVE', "Save", "Save the settings and setup of this bake in the history to a separate file on your disk")])  # noqa: E501

    def config_poll(self, context):
        bakemaster = context.scene.bakemaster

        poll_success, message = _ui_bakehistory_poll(self, bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        if bakemaster.bake_is_running:
            self.report({'ERROR'}, "Another bake is running")
            return False
        return True

    def execute(self, _):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.config_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        self.layout.prop(self, "action", text="", expand=True)


class BM_OT_BakeHistory_Remove(Operator):
    bl_idname = 'bakemaster.bakehistory_remove'
    bl_label = "Remove"
    bl_description = "Remove this bake from the history (choose whether to leave its baked content)"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    use_delete: BoolProperty(
        name="Delete baked content",
        description="Delete all baked content files of this bake (cannot be undone). If unchecked, just remove from the history",  # noqa: E501
        default=False)

    use_delete_blender_only: BoolProperty(
        name="Blender only",
        description="Leave baked files on the disk and only delete them from this .blend file",  # noqa: E501
        default=False)

    def remove_poll(self, context):
        bakemaster = context.scene.bakemaster

        poll_success, message = _ui_bakehistory_poll(self, bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        _bakehistory_remove_entry(bakemaster, self.index)
        bakemaster.wh_recalc_indexes(bakemaster, "bakehistory",
                                     childs_recursive=False)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.remove_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        layout = self.layout

        layout.prop(self, "use_delete")
        if self.use_delete:
            layout.prop(self, "use_delete_blender_only")
