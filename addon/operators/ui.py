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

from bpy.types import (
    Operator,
)
from bpy.props import (
    EnumProperty,
    IntProperty,
)
from ..utils import get as bm_get
from ..utils import operators as bm_ots_utils
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


class BM_OT_Pipeline_Config(Operator):
    bl_idname = 'bakemaster.pipeline_config'
    bl_label = "Config"
    bl_description = "Load/Save/Detach Bake Configuration data. You can use config as a super preset to save all tables data and items, presets, settings, bake jobs etc. of the current BakeMaster session"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        default='LOAD',
        items=[('LOAD', "Load", ""),
               ('SAVE', "Save", ""),
               ('DETACH', "Detach", "")],
        options={'SKIP_SAVE'})

    include: EnumProperty(
        name="Include",
        description="Data to include when loading/saving the config",
        default='ALL',
        items=[('ALL', "Setup & Presets", "Save/load both settings and presets as a config"),  # noqa: E501
               ('SETUP', "Setup only", "Save/load settings only as a config"),
               ('PRESETS', "Presets only", "Save/load presets only as a config")],  # noqa: E501
        options={'SKIP_SAVE'})

    def invoke(self, context, event):
        if self.action == 'DETACH':
            return self.execute(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster

        bakemaster.pipeline_config_is_attached = self.action != 'DETACH'
        bakemaster.pipeline_config_include = self.include
        print(self.action)
        print(self.include)

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        row = layout.row()
        row.prop(self, 'include')


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
        from bpy import ops

        self.report({'WARNING'}, "Not implemented")
        ops.bakemaster.bake_all('INVOKE_DEFAULT')
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
        default='LOAD',
        items=[('LOAD', "Load", "Load all settings of this bake into the addon (e.g. bake jobs, objects, maps)"),  # noqa: E501
               ('SAVE', "Save", "Save all addon settings of this bake into as a config file on the disk")])  # noqa: E501

    include: EnumProperty(
        name="Include",
        description="Data to include when loading/saving the config",
        default='ALL',
        items=[('ALL', "Setup & Presets", "Save/load both settings and presets as a config"),  # noqa: E501
               ('SETUP', "Setup only", "Save/load settings only as a config"),
               ('PRESETS', "Presets only", "Save/load presets only as a config")])  # noqa: E501

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
        from bpy import ops

        self.report({'WARNING'}, "Not implemented")
        ops.bakemaster.pipeline_config('EXEC_DEFAULT', action=self.action,
                                       include=self.include)
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
        layout.prop(self, 'include')


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
