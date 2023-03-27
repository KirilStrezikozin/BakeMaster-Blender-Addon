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

from bpy import ops as bpy_ops
from bpy.types import (
    Operator,
)
from bpy.props import (
    EnumProperty,
    IntProperty,
    StringProperty,
    BoolProperty,
)
from ..utils import (
    get as bm_get,
    operators as bm_ots_utils,
)
from ..utils.ui import get_icon_id as bm_ui_utils_get_icon_id
from ..labels import (
    BM_URLs,
)


class BM_OT_Help(Operator):
    bl_idname = 'bakemaster.help'
    bl_label = "Help"
    bl_description = "Press to visit the according BakeMaster's online documentation page"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        default='INDEX',
        items=[('INDEX', "Index", ""),
               ('BAKEJOBS', "Bake Jobs", ""),
               ('PIPELINE', "Pipeline", ""),
               ('MANAGER', "Manager", ""),
               ('OBJECTS', "Objects", ""),
               ('MAPS', "Maps", ""),
               ('OUTPUT', "Output", ""),
               ('TEXSETS', "Texture Sets", ""),
               ('BAKE', "Bake", ""),
               ('BAKEHISTORY', "Bake History", "")])

    def invoke(self, context, event):
        self.url = BM_URLs("latest").get(self.action)
        return self.execute(context)

    def execute(self, context):
        from webbrowser import open as webbrowser_open
        webbrowser_open(self.url)
        return {'FINISHED'}


class BM_OT_BakeJobs_AddRemove(Operator):
    bl_idname = 'bakemaster.bakejobs_addremove'
    bl_label = "Add/Remove"
    bl_description = "Add/Remove Bake Job from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=[('ADD', "Add", ""),
               ('REMOVE', "Remove", "")])

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if self.action == 'ADD':
            new_bakejob = bakemaster.bakejobs.add()
            new_bakejob.index = bakemaster.bakejobs_len
            new_bakejob.name = "Bake Job %d" % (new_bakejob.index + 1)
            bakemaster.bakejobs_active_index = new_bakejob.index
            bakemaster.bakejobs_len += 1
            return {'FINISHED'}

        bakejob = bm_get.bakejob(bakemaster)
        if bakejob is None:
            return {'CANCELLED'}

        if self.action == 'REMOVE':
            for index in range(bakejob.index + 1, bakemaster.bakejobs_len):
                bakemaster.bakejobs[index].index -= 1
            bakemaster.bakejobs.remove(bakejob.index)
            bakemaster.bakejobs_len -= 1
            if not bakemaster.bakejobs_active_index < bakemaster.bakejobs_len:
                bakemaster.bakejobs_active_index = bakemaster.bakejobs_len - 1
            return {'FINISHED'}


class BM_OT_BakeJobs_Trash(Operator):
    bl_idname = 'bakemaster.bakejobs_trash'
    bl_label = "Trash"
    bl_description = "Remove all Bake Jobs from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        [bakemaster.bakejobs.remove(index) for index in
         reversed(range(bakemaster.bakejobs_len))]
        bakemaster.bakejobs_active_index = -1
        bakemaster.bakejobs_len = 0
        return {'FINISHED'}


class BM_OT_BakeJob_ToggleType(Operator):
    bl_idname = 'bakemaster.bakejob_toggletype'
    bl_label = "Bake Job Type"
    bl_description = "Click to choose the Bake Job type"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    def type_objects_update(self, context):
        if self.type_maps is not self.type_objects:
            return
        self.type_maps = not self.type_objects

    def type_maps_update(self, context):
        if self.type_objects is not self.type_maps:
            return
        self.type_objects = not self.type_maps

    index: IntProperty(default=-1)

    type_objects: BoolProperty(
        name="Objects",
        description="Bake Job will contain Objects, where each of them will contain Maps to bake",  # noqa: E501
        default=True,
        update=type_objects_update,
        options={'SKIP_SAVE'})

    type_maps: BoolProperty(
        name="Maps",
        description="Bake Job will contain Maps, where each of them will contain Objects the map should be baked for",  # noqa: E501
        default=False,
        update=type_maps_update,
        options={'SKIP_SAVE'})

    bakejob = None

    def execute(self, context):
        if self.bakejob is None:
            return {'CANCELLED'}
        if self.type_objects:
            self.bakejob.type = 'OBJECTS'
        else:
            self.bakejob.type = 'MAPS'
        return {'FINISHED'}

    def invoke(self, context, event):
        if self.index == -1:
            self.report({'WARNING', "Internal error: Cannot resolve Bake Job"})
            return {'CANCELLED'}
        self.bakejob = bm_get.bakejob(context.scene.bakemaster, self.index)
        if self.bakejob is None:
            self.report({'WARNING', "Internal error: Cannot resolve Bake Job"})
            return {'CANCELLED'}
        if self.bakejob.type == 'OBJECTS':
            self.type_objects = True
            self.type_maps = False
        else:
            self.type_objects = False
            self.type_maps = True

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        icon_objects = bm_ui_utils_get_icon_id(context.scene.bakemaster,
                                               "bakemaster_objects.png")

        col = layout.column(align=True)
        col.prop(self, "type_objects", icon_value=icon_objects)
        col.prop(self, "type_maps", icon='RENDERLAYERS')


class BM_OT_Setup(Operator):
    bl_idname = 'bakemaster.setup'
    bl_label = "Setup"
    bl_description = "Choose a filepath for presets, manage addon config (load/save all settings into a file)"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    def config_run_save_update(self, context):
        if not self.config_run_save:
            return
        bpy_ops.bakemaster.config('INVOKE_DEFAULT', action='SAVE',
                                  filepath=self.config_filepath)
        self.config_run_save = False

    def config_run_detach_update(self, context):
        if not self.config_run_detach:
            return
        bpy_ops.bakemaster.config('INVOKE_DEFAULT', action='DETACH',
                                  filepath=self.config_filepath)
        self.config_run_detach = False

    config_action: EnumProperty(
        name="Config",
        description="Choose an action for the config. Hover over values to see descriptions",  # noqa: E501
        default='SAVE',
        items=[('LOAD', "Load", "Load all addon settings from a config file on the disk"),  # noqa: E501
               ('SAVE', "Save", "Save all addon settings into a config file on the disk")])  # noqa: E501

    config_filepath: StringProperty(
        name="Config Filepath",
        description="Where to Save/Load a config from. // is relative to this .blend file",  # noqa: E501
        default="",
        subtype='DIR_PATH')

    config_run_save: BoolProperty(
        name="Save Config",
        description="Save all addon settings and tables' items into a config file on the disk",  # noqa: E501
        default=False,
        update=config_run_save_update,
        options={'SKIP_SAVE'})

    config_run_detach: BoolProperty(
        name="Detach Config",
        description="Unlink current attached config. Leave all addon settings as is",  # noqa: E501
        default=False,
        update=config_run_detach_update,
        options={'SKIP_SAVE'})

    presets_filepath: StringProperty(
        name="Presets Filepath",
        description="Choose a folder on the disk containing presets for BakeMaster (leave empty for default path). // is relative to this .blend file",  # noqa: E501
        default="",
        subtype='DIR_PATH')

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        bakemaster.presets_filepath = self.presets_filepath

        bpy_ops.bakemaster.config('INVOKE_DEFAULT', action=self.config_action,
                                  filepath=self.config_filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        bakemaster = context.scene.bakemaster
        self.presets_filepath = bakemaster.presets_filepath
        self.config_filepath = bakemaster.config_filepath

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        bakemaster = context.scene.bakemaster
        layout = self.layout

        layout.use_property_split = False
        layout.use_property_decorate = False

        layout.prop(self, 'presets_filepath')

        col = layout.column(align=True)

        if bakemaster.config_is_attached:
            cf_row = col.row()
            cf_row.prop(self, 'config_filepath')
            cf_row.enabled = False

            row = col.row(align=True)
            row.prop(self, 'config_run_save')
            row.prop(self, 'config_run_detach', text="", icon='UNLINKED')
            return

        col.prop(self, 'config_action')
        if self.config_action == 'LOAD':
            text = "Load from"
        else:
            text = "Save to"
        col.prop(self, 'config_filepath', text=text)


class BM_OT_Config(Operator):
    bl_idname = 'bakemaster.config'
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

    filepath: StringProperty(
        name="Filepath",
        description="Where to Save/Load a config from",
        default="",
        subtype='DIR_PATH')

    def execute(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster

        bakemaster.config_is_attached = self.action != 'DETACH'
        bakemaster.config_filepath = self.filepath
        print(self.action)
        print(self.filepath)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class BM_OT_Bake_One(Operator):
    bl_idname = 'bakemaster.bake_one'
    bl_label = "Bake One"
    bl_description = "Choose to bake the active selected Map, Object, or Bake Job"  # noqa: E501
    bl_options = {'INTERNAL'}

    action: EnumProperty(
        name="Choose an operation",
        description="Choose an operation",
        default='BAKEJOB',
        items=[('MAP', "Map", "Bake the current active map"),
               ('OBJECT', "Object", "Bake the current active object"),
               ('BAKEJOB', "Bake Job", "Bake the current active bake job")])

    def bake_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          bake_is_running)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = True

    def invoke(self, context, event):
        if not self.bake_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        bm_ots_utils.bakehistory_add(bakemaster)
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def draw(self, context):
        row = self.layout.row(align=True)
        row.prop(self, 'action', expand=True)


class BM_OT_Bake_All(Operator):
    bl_idname = 'bakemaster.bake_all'
    bl_label = "Bake All"
    bl_description = "Bake the whole setup (all bake jobs, all maps for all objects)"  # noqa: E501
    bl_options = {'INTERNAL'}

    def bake_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          bake_is_running)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = True

    def invoke(self, context, event):
        if not self.bake_poll(context):
            return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        bm_ots_utils.bakehistory_add(bakemaster)
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}


class BM_OT_Bake_Pause(Operator):
    bl_idname = 'bakemaster.bake_pause'
    bl_label = "Pause/Resume"
    bl_description = "Pause/Resume the bake"
    bl_options = {'INTERNAL'}

    def pause_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        is_paused = bakemaster.bake_hold_on_pause
        bakemaster.bake_hold_on_pause = not is_paused

    def invoke(self, context, event):
        if not self.pause_poll(context):
            return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):
        self.props_set_explicit(context.scene.bakemaster)
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}


class BM_OT_Bake_Stop(Operator):
    bl_idname = 'bakemaster.bake_stop'
    bl_label = "Stop"
    bl_description = "Stop and save what's been baked"
    bl_options = {'INTERNAL'}

    def stop_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = True
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def invoke(self, context, event):
        if not self.stop_poll(context):
            return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        bm_ots_utils.bakehistory_unreserve(bakemaster)
        bakemaster.bake_trigger_stop = False
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}


class BM_OT_Bake_Cancel(Operator):
    bl_idname = 'bakemaster.bake_cancel'
    bl_label = "Cancel"
    bl_description = "Cancel - stop and erase what's been baked"
    bl_options = {'INTERNAL'}

    def cancel_poll(self, context):
        bakemaster = context.scene.bakemaster
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = True
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def invoke(self, context, event):
        if not self.cancel_poll(context):
            return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        self.props_set_explicit(bakemaster)
        bm_ots_utils.bakehistory_unreserve(bakemaster)
        bakemaster.bake_trigger_cancel = False
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}


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
               ('FULL_OVERWRITE', "Full Overwrite", "Rebake and overwrite all content of this bake in the history by the current addon setup and settings"),  # noqa: E501
               ('SMART_OVERWRITE', "Smart Overwrite", "Rebake and overwrite only what differs from this bake in the history and the current addon setup and settings. Visit Pipeline for advanced controls")])  # noqa: E501

    def rebake_poll(self, context):
        bakemaster = context.scene.bakemaster
        poll_success, message = bm_ots_utils.ui_bakehistory_poll(self,
                                                                 bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        bake_is_running = bakemaster.bake_is_running
        poll_success, message = bm_ots_utils.ui_bake_poll(bakemaster,
                                                          bake_is_running)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def execute(self, context):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.rebake_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, 'action')


class BM_OT_BakeHistory_Config(Operator):
    bl_idname = 'bakemaster.bakehistory_config'
    bl_label = "Save/Load Config"
    bl_description = "Save/Load configuration (all addon settings) of this bake in the history"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    action: EnumProperty(
        name="Action",
        description="Choose an action for the config. Hover over values to see descriptions",  # noqa: E501
        default='LOAD',
        items=[('LOAD', "Load", "Load all settings of this bake into the addon (e.g. bake jobs, objects, maps)"),  # noqa: E501
               ('SAVE', "Save", "Save all addon settings of this bake into a config file on the disk")])  # noqa: E501

    filepath: StringProperty(
        name="Filepath",
        description="Where to save a config file",
        default="",
        subtype='DIR_PATH')

    def config_poll(self, context):
        bakemaster = context.scene.bakemaster
        poll_success, message = bm_ots_utils.ui_bakehistory_poll(self,
                                                                 bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        if bakemaster.bake_is_running:
            self.report({'ERROR'}, "Another bake is running")
            return False
        return True

    def execute(self, context):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.config_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, 'action')
        if self.action == 'SAVE':
            layout.prop(self, 'filepath')


class BM_OT_BakeHistory_Remove(Operator):
    bl_idname = 'bakemaster.bakehistory_remove'
    bl_label = "Remove"
    bl_description = "Remove this bake from the history (its baked content will remain)"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    def remove_poll(self, context):
        bakemaster = context.scene.bakemaster
        poll_success, message = bm_ots_utils.ui_bakehistory_poll(self,
                                                                 bakemaster)
        if not poll_success:
            self.report({'ERROR'}, message)
            return False
        return True

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        bm_ots_utils.bakehistory_remove(bakemaster, self.index)
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.remove_poll(context):
            return {'CANCELLED'}

        return self.execute(context)
