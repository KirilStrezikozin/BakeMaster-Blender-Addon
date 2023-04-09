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
from time import time
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
    set as bm_set,
)
from ..utils.ui import get_icon_id as bm_ui_utils_get_icon_id
from ..labels import (
    BM_URLs,
)


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

    def invoke(self, context, _):
        self.url = BM_URLs("latest").get(self.action)
        return self.execute(context)

    def execute(self, _):
        from webbrowser import open as webbrowser_open
        webbrowser_open(self.url)
        return {'FINISHED'}


class BM_OT_UIList_Walk_Handler(Operator):
    bl_idname = 'bakemaster.uilist_walk_handler'
    bl_label = "Drag"
    bl_description = "Drag item to move it to a new location or to see other options"  # noqa: E501
    bl_options = {'INTERNAL'}

    _handler = None

    drop_new_label = "new Bake Job..."
    drop_in_label = "+"

    def handler_poll(self):
        cls = self.__class__
        if cls._handler is not None:
            return False
        cls._handler = self
        return True

    def get_items(self, bakemaster: not None):
        if bakemaster.walk_data_name == "":
            return None
        else:
            getter = getattr(bm_get,
                             "walk_data_get_%s" % bakemaster.walk_data_name)
            return getter(bakemaster)

    def reset_props(self, bakemaster):
        self.is_dropping = False
        self.is_dragging = False

        self.wait_events_end = False
        self.query_events_end = False

        bakemaster.walk_data_name = ""

        bakemaster.allow_drop = False
        bakemaster.allow_drag = False

        bakemaster.drag_from_index = -1
        bakemaster.drag_to_index = -1

        bakemaster.allow_multi_select = False
        bakemaster.multi_select_event = ''
        bakemaster.is_multi_selection_empty = True

        self.is_left_click = False
        self.last_left_click_time = 0
        bakemaster.last_left_click_ticker = False
        bakemaster.is_double_click = False

    def is_cursor_in_region(self, region, event):
        # area as region is acceptable
        if all([region.x <= event.mouse_x <= region.x + region.width,
                region.y <= event.mouse_y <= region.y + region.height]):
            return True
        else:
            return False

    def get_uiarea_of_type(self, screen: not None, area_type: str):
        for area in screen.areas:
            if area is None:
                continue
            if area.type == area_type:
                return area
        return None

    def is_drop_available(self, context, event, bakemaster):
        if self.is_dropping:
            return True
        elif event.type != 'LEFTMOUSE':
            self.drop_end(bakemaster)
            return False

        outliner_area = self.get_uiarea_of_type(context.screen, 'OUTLINER')

        if outliner_area is None:
            return False
        return self.is_cursor_in_region(outliner_area, event)

    def is_drag_available(self, context, event, bakemaster):
        if bakemaster.allow_drag:
            return True
        elif event.type != 'LEFTMOUSE':
            return False

        viewport_area = self.get_uiarea_of_type(context.screen, 'VIEW_3D')

        if viewport_area is None:
            return False
        for region in viewport_area.regions:
            if region is None:
                continue
            if region.type != 'UI':
                continue
            return self.is_cursor_in_region(region, event)
        return False

    def drop_init(self, bakemaster):
        if self.is_dropping or self.get_items(bakemaster) is None:
            return

        bakemaster.allow_drop = True
        self.is_dropping = True
        self.wait_events_end = False

        data, items, attr = self.get_items(bakemaster)
        items_len = getattr(data, "%s_len" % attr)

        new_item = items.add()
        new_item.index = items_len
        new_item.drop_name_old = self.drop_new_label
        new_item.drop_name = self.drop_new_label
        new_item.has_drop_prompt = True

        setattr(data, "%s_active_index" % attr, items_len)

    def drag_init(self, bakemaster):
        if self.is_dragging or self.get_items(bakemaster) is None:
            return

        data, items, attr = self.get_items(bakemaster)
        items_len = getattr(data, "%s_len" % attr)

        items_active_index = getattr(data, "%s_active_index" % attr)
        self.drag_end(bakemaster)

        drag_empty = items.add()
        drag_empty.index = items_len
        drag_empty.is_drag_empty = True

        for item in items:
            item.ticker = False

        setattr(data, "%s_active_index" % attr, items_active_index)

        bakemaster.allow_drag = True
        self.is_dragging = True

    def remove_drop_prompts(self, bakemaster):
        if self.get_items(bakemaster) is None:
            return

        _, items, _ = self.get_items(bakemaster)
        to_remove = []
        for item in items:
            if not item.has_drop_prompt:
                continue
            to_remove.append(item.index)
        for index in reversed(to_remove):
            items.remove(index)

    def drop_end(self, _):
        if self.is_dropping:
            self.query_events_end = True
        self.is_dropping = False
        self.wait_events_end = False

    def drag_end(self, bakemaster):
        self.is_dragging = False

        if self.get_items(bakemaster) is None:
            return
        _, items, _ = self.get_items(bakemaster)

        bm_set.disable_drag(bakemaster, items)

    def events_end(self, bakemaster):
        self.drop_end(bakemaster)
        self.drag_end(bakemaster)

    def events_init(self, bakemaster, is_drop_available, is_drag_available):
        if is_drop_available:
            self.drag_end(bakemaster)
            self.drop_init(bakemaster)
        elif is_drag_available:
            self.drop_end(bakemaster)
            self.drag_init(bakemaster)

    def evaluate_event(self, event, bakemaster, is_drop_available,
                       is_drag_available):
        """
        Start drag/drop events on Press,
        End on Click or Release.
        """

        if event.value == 'PRESS':
            self.events_init(bakemaster, is_drop_available, is_drag_available)
        elif event.value in ['CLICK', 'RELEASE']:
            self.events_end(bakemaster)

        if self.is_dropping and event.value == 'CLICK_DRAG':
            self.events_init(bakemaster, is_drop_available, is_drag_available)

            self.wait_events_end = True

    def set_last_left_click_ticker(self, bakemaster):
        if not all([self.is_left_click,
                    self.get_items(bakemaster) is not None]):
            return

        data, items, attr = self.get_items(bakemaster)
        try:
            active_index = getattr(data, "%s_active_index" % attr)
            if active_index == -1:
                raise IndexError
            bakemaster.last_left_click_ticker = items[active_index].ticker
        except IndexError:
            pass

    def evaluate_double_click(self, event, bakemaster, is_drag_available):
        if not is_drag_available or any([event.shift, event.ctrl]):
            return

        if event.type == 'LEFTMOUSE' and event.value in ['CLICK', 'PRESS']:
            if self.is_left_click and time() - self.last_left_click_time < 1:
                self.is_left_click = False
                self.last_left_click_time = 0
                bakemaster.is_double_click = True

            elif self.is_left_click:
                self.is_left_click = False
                self.last_left_click_time = 0
                bakemaster.is_double_click = False

            else:
                self.is_left_click = True
                self.set_last_left_click_ticker(bakemaster)
                self.last_left_click_time = time()
                bakemaster.is_double_click = False

        else:
            self.is_left_click = False
            self.last_left_click_time = 0
            bakemaster.is_double_click = False

    def evaluate_multi_select(self, event, bakemaster, is_drag_available):
        if not is_drag_available:
            return
        if event.shift:
            bakemaster.allow_multi_select = True
            bakemaster.multi_select_event = 'SHIFT'
        elif event.ctrl:
            bakemaster.allow_multi_select = True
            bakemaster.multi_select_event = 'CTRL'
        elif event.type == 'LEFTMOUSE':
            bakemaster.multi_select_event = ''

    def drag(self, bakemaster):
        """
        Invoke Collection Property Move.

        Moving is carried out with bakemaster.drag_from_index and
        bakemaster.drag_to_index, values of which are set in item.ticker
        Updates.
        The Collection Property is determined by calling self.get_items
        """

        if bakemaster.drag_to_index > bakemaster.drag_from_index:
            new_index = bakemaster.drag_to_index - 1
        else:
            new_index = bakemaster.drag_to_index

        if self.get_items(bakemaster) is not None:
            data, _, attr = self.get_items(bakemaster)

            move_ot = getattr(bpy_ops.bakemaster, "%s_move" % attr)
            move_ot('INVOKE_DEFAULT', index=bakemaster.drag_from_index,
                    new_index=new_index)
            # items.move(bakemaster.drag_from_index, new_index) - no undo event

            setattr(data, "%s_active_index" % attr, new_index)

        self.drag_end(bakemaster)

    def modal(self, context, event):
        if 'TIMER' in event.type:
            return {'PASS_THROUGH'}

        bakemaster = context.scene.bakemaster

        # reswitch is_dragging after Add OT
        if not bakemaster.allow_drag and self.is_dragging:
            self.is_dragging = False

        self.set_last_left_click_ticker(bakemaster)

        if self.query_events_end:
            self.remove_drop_prompts(bakemaster)
            self.query_events_end = False
            bakemaster.allow_drop = False

        if all([bakemaster.allow_drag,
                bakemaster.drag_from_index != -1,
                bakemaster.drag_to_index != -1]):
            self.drag(bakemaster)
        elif bakemaster.allow_drag and bakemaster.drag_from_index == -1:
            self.drag_end(bakemaster)

        is_drop_available = self.is_drop_available(context, event, bakemaster)
        is_drag_available = self.is_drag_available(context, event, bakemaster)

        self.evaluate_double_click(event, bakemaster, is_drag_available)

        self.evaluate_multi_select(event, bakemaster, is_drag_available)

        if any([not any([is_drop_available, is_drag_available,
                         bakemaster.allow_multi_select]),
                bakemaster.allow_multi_select]):
            return {'PASS_THROUGH'}

        if not self.wait_events_end:
            self.evaluate_event(event, bakemaster, is_drop_available,
                                is_drag_available)
            return {'PASS_THROUGH'}

        if all(['MOUSEMOVE' not in event.type,
                event.type != 'EVT_TWEAK_L',
                event.type != 'NONE']):
            self.events_end(bakemaster)
            return {'PASS_THROUGH'}

        self.wait_events_end = True
        if not bakemaster.allow_drag:
            self.is_dropping = True
        return {'PASS_THROUGH'}

    def invoke(self, context, _):
        if not self.handler_poll():
            return {'CANCELLED'}

        wm = context.window_manager
        wm.modal_handler_add(self)
        self.reset_props(context.scene.bakemaster)
        return {'RUNNING_MODAL'}


class BM_OT_BakeJobs_AddRemove(Operator):
    bl_idname = 'bakemaster.bakejobs_addremove'
    bl_label = "Add/Remove"
    bl_description = "Add a new Bake Job.\nRemove selected Bake Jobs from the list on the left"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=[('ADD', "Add", ""),
               ('REMOVE', "Remove", "")])

    index: IntProperty(default=-1)

    def invoke(self, context, _):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if self.action == 'ADD':
            new_bakejob = bakemaster.bakejobs.add()
            new_bakejob.index = bakemaster.bakejobs_len
            new_bakejob.name = "Bake Job %d" % (new_bakejob.index + 1)
            bakemaster.bakejobs_active_index = new_bakejob.index
            bakemaster.bakejobs_len += 1

            # reduce flicker and hidden items on add (uilist mess)
            bm_set.disable_drag(bakemaster, bakemaster.bakejobs)
            return {'FINISHED'}

        bakejob = bm_get.bakejob(bakemaster, self.index)
        if bakejob is None:
            return {'CANCELLED'}

        if self.action == 'REMOVE':
            if any([bakejob.is_drag_empty, bakejob.has_drop_prompt]):
                return {'CANCELLED'}

            for index in range(bakejob.index + 1, bakemaster.bakejobs_len):
                try:
                    bakemaster.bakejobs[index].index -= 1
                except IndexError:
                    continue
            bakemaster.bakejobs.remove(bakejob.index)
            bakemaster.bakejobs_len -= 1
            if not bakemaster.bakejobs_active_index < bakemaster.bakejobs_len:
                bakemaster.bakejobs_active_index = bakemaster.bakejobs_len - 1
            return {'FINISHED'}


class BM_OT_BakeJobs_Move(Operator):
    """
    Internal Bake Jobs Move Operator to move a Bake Job Item inside Bake Jobs
    Collection. Not used in the UI but called in BM_OT_UIList_Walk_Handler.
    This Operator exists only for the sake of a Move Undo event.

    Call with providing the index of the Bake Job and its new_index.
    """

    bl_idname = 'bakemaster.bakejobs_move'
    bl_label = "Move a Bake Job (Internal)"
    bl_description = "Move a Bake Job's bake order up or down"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)
    new_index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        try:
            if any([self.index == -1, self.new_index == -1]):
                raise IndexError
            bakemaster.bakejobs[self.index]
            bakemaster.bakejobs[self.new_index]
        except IndexError:
            print("BakeMaster: Internal warning: cannot resolve Bake Job")
            return {'CANCELLED'}

        bakemaster.bakejobs.move(self.index, self.new_index)
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_BakeJobs_AddDropped(Operator):
    bl_idname = 'bakemaster.bakejobs_adddropped'
    bl_label = "New Bake Job.."
    bl_description = "Add dropped objects into a new Bake Job"
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

    drop_name: StringProperty(default="")

    def remove(self):
        bpy_ops.bakemaster.bakejobs_addremove('INVOKE_DEFAULT',
                                              action='REMOVE',
                                              index=self.index)

    def add(self, bakemaster, add_names: list):
        bpy_ops.bakemaster.bakejobs_addremove('INVOKE_DEFAULT',
                                              action='ADD')
        _ = bakemaster.bakejobs[bakemaster.bakejobs_len - 1]
        print(f"adding {add_names}")

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if bakemaster.allow_drop:
            self.remove()
            return {'CANCELLED'}

        add_names = []
        proceed = False

        for object in context.selected_objects:
            if object.type == 'MESH':
                add_names.append(object.name)
            if object.name == self.drop_name:
                proceed = True

        if not proceed:
            self.remove()
            return {'CANCELLED'}

        self.add(bakemaster, add_names)
        return {'FINISHED'}

    def invoke(self, context, _):
        try:
            context.scene.bakemaster.bakejobs[self.index]
            if self.index == -1:
                raise IndexError
        except IndexError:
            return self.execute(context)
        else:
            self.remove()
            return {'CANCELLED'}


class BM_OT_BakeJobs_Trash(Operator):
    bl_idname = 'bakemaster.bakejobs_trash'
    bl_label = "Trash"
    bl_description = "Remove all Bake Jobs from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, _):
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
        description="Enter new name",
        default="",
        options={'SKIP_SAVE'})

    bakejob = None

    def execute(self, _):
        if self.bakejob is None:
            return {'CANCELLED'}
        self.bakejob.name = self.name
        return {'FINISHED'}

    def invoke(self, context, _):
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

    def draw(self, _):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, "name")


class BM_OT_BakeJob_ToggleType(Operator):
    bl_idname = 'bakemaster.bakejob_toggletype'
    bl_label = "Bake Job Type"
    bl_description = "Click to choose the Bake Job type"
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

    def execute(self, _):
        if self.bakejob is None:
            return {'CANCELLED'}
        if self.type_objects:
            self.bakejob.type = 'OBJECTS'
        else:
            self.bakejob.type = 'MAPS'
        return {'FINISHED'}

    def invoke(self, context, _):
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


class BM_OT_BakeJobs_Merge(Operator):
    bl_idname = 'bakemaster.bakejobs_merge'
    bl_label = "Merge selected Bake Jobs"
    bl_description = "Merge selected Bake Jobs into the active one to contain all their items"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        to_remove = []
        selection_seq = bakemaster.get_seq("bakejobs", "is_selected",
                                           bakemaster.bakejobs_len, bool)

        if selection_seq[selection_seq].size < 2:
            self.report({'INFO'},
                        "Merge requires two or more selected Bake Jobs")
            return {'CANCELLED'}

        for index, is_selected in enumerate(selection_seq):
            if not is_selected:
                continue
            if index == bakemaster.bakejobs_active_index:
                bakemaster.bakejobs[index].is_selected = False
            else:
                to_remove.append(index)

        # turn off multi select
        bakemaster.allow_multi_select = False
        bakemaster.is_multi_selection_empty = True
        bakemaster.multi_select_event = ''

        bakemaster.bakejobs_active_index = -1
        bakemaster.bakejobs_len -= len(to_remove)

        for index in reversed(to_remove):
            bakemaster.bakejobs.remove(index)

        for index, bakejob in enumerate(bakemaster.bakejobs):
            bakejob.index = index

        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        bakejob = bm_get.bakejob(context.scene.bakemaster)
        if bakejob is None:
            self.report({'WARNING', "Internal error: Cannot resolve Bake Job"})
            return {'CANCELLED'}

        if not bakejob.is_selected:
            self.report({'INFO'},
                        "No active Bake Job (select it with Ctrl)")
            return {'CANCELLED'}
        return self.execute(context)


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
    bl_description = "Choose a filepath for presets, manage the config (load/save all settings into a file)"  # noqa: E501
    bl_options = {'INTERNAL'}

    def config_instruction_update(self, _):
        default = "Config: save/load all settings & setup:"
        self.config_instruction = default

    config_instruction: StringProperty(
        name="What is Config?",
        description="Use config file as a super preset to save all settings, setup, presets, and tables items (e.g Bake Jobs, Objects, Maps...). BakeMaster Config file can be loaded in another .blend file, and it will still remember where to pick Objects from to bake",  # noqa: E501
        default="Config: save/load all settings & setup:",
        update=config_instruction_update)

    def execute(self, _):
        return {'FINISHED'}

    def invoke(self, context, _):
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

    def invoke(self, context, _):
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

    def invoke(self, context, _):
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

    def draw(self, _):
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

    def invoke(self, context, _):
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
        poll_success, _ = bm_ots_utils.ui_bake_poll(bakemaster,
                                                    not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        is_paused = bakemaster.bake_hold_on_pause
        bakemaster.bake_hold_on_pause = not is_paused

    def invoke(self, context, _):
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
        poll_success, _ = bm_ots_utils.ui_bake_poll(bakemaster,
                                                    not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = True
        bakemaster.bake_trigger_cancel = False
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def invoke(self, context, _):
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
        poll_success, _ = bm_ots_utils.ui_bake_poll(bakemaster,
                                                    not bake_is_running)
        return poll_success

    def props_set_explicit(self, bakemaster):
        bakemaster.bake_trigger_stop = False
        bakemaster.bake_trigger_cancel = True
        bakemaster.bake_hold_on_pause = False
        bakemaster.bake_is_running = False

    def invoke(self, context, _):
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
               ('FULL_OVERWRITE', "Full Overwrite", "Rebake and overwrite all initially baked content of this bake in the history"),  # noqa: E501
               ('SMART_OVERWRITE', "Smart Rebake", "Compare baked content of this bake in the history and the current setup and settings. Bake what's been added and rebake what's changed")])  # noqa: E501

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
    bl_description = "Replace all current settings and setup (e.g. bake jobs, objects, maps, all settings) with the settings and setup of this bake in the history"  # noqa: E501
    bl_options = {'INTERNAL'}

    index: IntProperty(default=-1)

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

    def execute(self, _):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        if not self.config_poll(context):
            return {'CANCELLED'}

        return self.execute(context)


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
        description="Leave baked files on the disk and only delete them from this .blend file",
        default=False)

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

    def invoke(self, context, _):
        if not self.remove_poll(context):
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, "use_delete")
        if self.use_delete:
            layout.prop(self, "use_delete_blender_only")
