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

from os import path as os_path
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
from bpy_extras.io_utils import ImportHelper
from ..utils import (
    get as bm_get,
    operators as bm_ots_utils,
)
from ..utils.ui import get_icon_id as bm_ui_utils_get_icon_id
from ..labels import (
    BM_URLs,
)


class BM_OT_RemovePreviewCollections(Operator):
    bl_idname = 'bakemaster.removepreviewcollections'
    bl_label = "Remove Preview Collections"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        import bpy.utils.previews as bpy_utils_previews
        preview_collections = context.scene.bakemaster.preview_collections

        for pcoll in preview_collections.values():
            bpy_utils_previews.remove(pcoll)

        preview_collections.clear()
        return {'FINISHED'}


class BM_OT_Help(Operator):
    bl_idname = 'bakemaster.help'
    bl_label = "Help"
    bl_description = "Press to visit the according BakeMaster's online documentation page"  # noqa: E501
    bl_options = {'INTERNAL'}

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


class BM_OT_UIList_WalkHandler(Operator):
    bl_idname = 'bakemaster.uilist_walkhandler'
    bl_label = "Drag & Drop"
    bl_description = "Drag & Drop functionality was accidentally deactivated. Press to turn it back on"  # noqa: E501
    bl_options = {'INTERNAL'}

    _handler = None

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def execute(self, context):
        cls = self.__class__
        cls._handler = None
        print('FINISHED')
        return {'FINISHED'}

    def modal(self, context, event):
        print(context.region, event.type)
        if event.type == 'ESC':
            return self.execute(context)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        print('invoke')
        cls = self.__class__
        if cls._handler is not None:
            print('CANCELLED')
            return {'CANCELLED'}
        cls._handler = self

        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class BM_OT_BakeJobs_AddRemove(Operator):
    bl_idname = 'bakemaster.bakejobs_addremove'
    bl_label = "Add/Remove"
    bl_description = "Add/Remove Bake Job from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=[('ADD', "Add", ""),
               ('REMOVE', "Remove", "")])

    index: IntProperty(default=-1)

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

        bakejob = bm_get.bakejob(bakemaster, self.index)
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


class BM_OT_BakeJobs_AddDropped(Operator):
    bl_idname = 'bakemaster.bakejobs_adddropped'
    bl_label = "New Bake Job.."
    bl_description = "Add dropped objects into a new Bake Job"
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    bakejob = None

    def remove_bakejob(self):
        bpy_ops.bakemaster.bakejobs_addremove('INVOKE_DEFAULT',
                                              action='REMOVE',
                                              index=self.index)

    def invoke(self, context, event):
        if self.index == -1:
            return {'CANCELLED'}

        bakemaster = context.scene.bakemaster
        self.bakejob = bakemaster.bakejobs[self.index]

        if bakemaster.allow_drop_prompt:
            self.remove_bakejob()
            return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):
        if self.bakejob is None:
            return {'CANCELLED'}

        add_names = []
        proceed = False

        for object in context.selected_objects:
            if object.type == 'MESH':
                add_names.append(object.name)
            if object.name == self.bakejob.drop_name:
                proceed = True

        if not proceed:
            self.remove_bakejob()
            return {'FINISHED'}

        for name in add_names:
            print("adding %s" % name)

        self.bakejob.has_drop_prompt = False
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


class BM_OT_BakeJob_Rename(Operator):
    bl_idname = 'bakemaster.bakejob_rename'
    bl_label = "Rename the Bake Job"
    bl_description = "Click to rename the Bake Job"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    name: StringProperty(
        name="New name",
        default="",
        options={'SKIP_SAVE'})

    bakejob = None

    def execute(self, context):
        if self.bakejob is None:
            return {'CANCELLED'}
        self.bakejob.name = self.name
        return {'FINISHED'}

    def invoke(self, context, event):
        if self.index == -1:
            self.report({'WARNING', "Internal error: Cannot resolve Bake Job"})
            return {'CANCELLED'}
        self.bakejob = bm_get.bakejob(context.scene.bakemaster, self.index)
        if self.bakejob is None:
            self.report({'WARNING', "Internal error: Cannot resolve Bake Job"})
            return {'CANCELLED'}
        self.name = self.bakejob.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, "name")


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
        return wm.invoke_props_dialog(self, width=100)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        icon_objects = bm_ui_utils_get_icon_id(context.scene.bakemaster,
                                               "bakemaster_objects.png")

        col = layout.column(align=True)
        col.prop(self, "type_objects", icon_value=icon_objects)
        col.prop(self, "type_maps", icon='RENDERLAYERS')


class BM_OT_FileChooseDialog(Operator, ImportHelper):
    bl_idname = 'bakemaster.filechoosedialog'
    bl_label = "Choose a filepath"
    bl_description = "Open a file browser, hold Shift to open the file, Alt to browse containing directory"  # noqa: E501
    bl_options = {'INTERNAL'}

    prop_name: StringProperty(default="", options={'HIDDEN'})

    config_lookup: BoolProperty(default=False, options={'HIDDEN'})
    config_action: StringProperty(default="", options={'HIDDEN'})

    message: StringProperty(default="", options={'HIDDEN'})

    def process_exit(self):
        if self.message != "":
            self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def execute(self, context):
        if os_path.isfile(self.filepath):
            self.filepath = os_path.dirname(self.filepath)
        # no safe check if property is invalid
        setattr(context.scene.bakemaster, self.prop_name, self.filepath)

        if not self.config_lookup:
            return self.process_exit()

        bpy_ops.bakemaster.config('EXEC_DEFAULT', action=self.config_action)
        return self.process_exit()


class BM_OT_Setup(Operator):
    bl_idname = 'bakemaster.setup'
    bl_label = "Configure the Setup"
    bl_description = "Choose a filepath for presets, manage addon config (load/save all settings into a file)"  # noqa: E501
    bl_options = {'INTERNAL'}

    def config_instruction_update(self, context):
        default = "Config: save/load all addon settings & setup:"
        self.config_instruction = default

    config_instruction: StringProperty(
        name="What is Config?",
        description="Use config file as a super preset to save all addon settings, setup, presets, and tables items (e.g Bake Jobs, Objects, Maps...). BakeMaster Config file can be loaded in another .blend file, and it will still remember where to pick Objects from to bake",  # noqa: E501
        default="Config: save/load all addon settings & setup:",
        update=config_instruction_update)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        bakemaster = context.scene.bakemaster
        layout = self.layout

        layout.use_property_split = False
        layout.use_property_decorate = False

        if not bakemaster.config_is_attached:
            row = layout.row(align=True)
            row.prop(bakemaster, 'presets_filepath', text="Presets Dir")
            p_fc = row.operator('bakemaster.filechoosedialog', text="",
                                icon='FILEBROWSER')
            p_fc.filepath = bakemaster.presets_filepath
            p_fc.prop_name = "presets_filepath"
            p_fc.message = "Filepath for Presets set successfully"

            layout.separator(factor=1.0)

        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "config_instruction", text="")
        row.enabled = False
        c_load_text = "Load"

        if bakemaster.config_is_attached:
            cf_row = col.row(align=True)
            cf_row.prop(bakemaster, 'config_filepath')
            c_fc = cf_row.operator('bakemaster.filechoosedialog', text="",
                                   icon='FILEBROWSER')
            c_fc.filepath = bakemaster.config_filepath
            c_fc.prop_name = "config_filepath"
            c_fc.message = "Filepath for Config set successfully"
            cf_row.enabled = False

            c_load_text = "Reload"

        row = col.row(align=True)

        if bakemaster.config_is_attached:
            row.operator('bakemaster.config', text="Save").action = 'SAVE'
        else:
            c_save = row.operator('bakemaster.filechoosedialog', text="Save")
            c_save.filepath = bakemaster.config_filepath
            c_save.prop_name = "config_filepath"
            c_save.config_lookup = True
            c_save.config_action = 'SAVE'
            c_save.message = "Config saved successfully"

        c_load = row.operator('bakemaster.filechoosedialog', text=c_load_text)
        c_load.filepath = bakemaster.config_filepath
        c_load.prop_name = "config_filepath"
        c_load.config_lookup = True
        c_load.config_action = 'LOAD'
        c_load.message = "Config loaded successfully"

        if bakemaster.config_is_attached:
            row.operator('bakemaster.config', text="",
                         icon='UNLINKED').action = 'DETACH'


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
        if self.filepath != "":
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
    bl_label = "Load Config"
    bl_description = "Load all settings of this bake into the addon (e.g. bake jobs, objects, maps, all settings)"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    hard_load: BoolProperty(
        name="Replace settings",
        description="All current addon settings and setup will be replaced with the loaded config's",  # noqa: E501
        default=True)

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
        layout.prop(self, 'hard_load')


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
