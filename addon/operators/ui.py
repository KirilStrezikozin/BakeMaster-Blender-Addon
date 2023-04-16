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


_walk_handler_invoked = False
_walk_handler_invoke_time = 0


class BM_OT_Help(Operator):
    bl_idname = 'bakemaster.help'
    bl_label = "Help"
    bl_description = "Press to visit the according BakeMaster's online documentation page"  # noqa: E501
    bl_options = {'INTERNAL'}

    id: StringProperty(default="")

    def invoke(self, context, _):
        self.url = BM_URLs("latest").get(self.id)
        return self.execute(context)

    def execute(self, _):
        from webbrowser import open as webbrowser_open
        webbrowser_open(self.url)
        return {'FINISHED'}


class BM_OT_UIList_Walk_Handler(Operator):
    bl_idname = 'bakemaster.uilist_walk_handler'
    bl_label = "BakeMaster Walk Handler"
    bl_description = "User Interface Walk Handler for operating Drag, Drop, Multi Selection"  # noqa: E501
    bl_options = {'INTERNAL'}

    _handler = None

    def cancel(self, _):
        cls = self.__class__
        cls._handler = None

        global _walk_handler_invoked
        _walk_handler_invoked = False

    def handler_poll(self):
        cls = self.__class__
        if cls._handler is not None:
            return False
        cls._handler = self

        global _walk_handler_invoked
        return not _walk_handler_invoked

    def get_containers(self, bakemaster: not None):
        if bakemaster.walk_data_name == "":
            return None

        data, containers, attr = getattr(
            bm_get, "walk_data_get_%s" % bakemaster.walk_data_name)(
                bakemaster)
        if data is None:
            return None
        return data, containers, attr

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
        bakemaster.drad_data_from = ""
        bakemaster.drad_data_to = ""
        bakemaster.allow_drag_trans = False
        bakemaster.drag_from_ticker = False

        bakemaster.allow_multi_select = False
        bakemaster.multi_select_event = ''
        bakemaster.is_multi_selection_empty = True
        bakemaster.multi_selection_data = ""

        self.is_left_click = False
        self.last_left_click_time = 0
        bakemaster.is_double_click = False
        bakemaster.last_left_click_ticker = False

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

    def reset_all_tickers(self, bakemaster):
        # Reset tickers in every walk_data -> drag to other data with no errors

        datas = ["bakejobs", "containers", "subcontainers"]

        for data_name in datas:
            walk_data_getter = getattr(bm_get, "walk_data_get_%s" % data_name)
            data, containers, _ = walk_data_getter(bakemaster)
            if data is None:
                # print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")  # noqa: E501
                continue

            # len(containers) is used because containers_len doesn't
            # cover drag_empty
            containers.foreach_set("ticker", [False] * len(containers))
            containers.foreach_set("is_drag_placeholder",
                                   [False] * len(containers))

    def evaluate_data_trans(self, bakemaster, data, containers, attr):
        """
        Set bakemaster.allow_drag_trans to True if dragged data has a multi
        selection. Subsequently allow drag to parent walk_data.

        In the UI can check for bakemaster.allow_drag_trans value and
        'child of drawn data == drag_data_from' to draw "move here..." label.
        """

        bakemaster.allow_drag_trans, _ = bm_get.walk_data_multi_selection_data(
            bakemaster, attr)
        if not bakemaster.allow_drag_trans:
            return

        # disallow drag (ticker update) inside data
        # containers.foreach_set("ticker",
        #                   [True] * getattr(data, "%s_len" % attr))

    def add_drag_empty(self, data, containers, attr):
        # ensure there's only one drag_empty
        drag_empties = data.get_seq(attr, "is_drag_empty", bool)
        if drag_empties[drag_empties].size == 0:
            drag_empty = containers.add()
            drag_empty.index = getattr(data, "%s_len" % attr)
            drag_empty.is_drag_empty = True

    def add_drop_prompt(self, data, containers, attr):
        # ensure there's only one drop_prompt
        drop_prompts = data.get_seq(attr, "has_drop_prompt", bool)
        if drop_prompts[drop_prompts].size == 0:
            drop_prompt = containers.add()
            drop_prompt.index = getattr(data, "%s_len" % attr)
            drop_prompt.has_drop_prompt = True

    def drop_init(self, bakemaster):
        if self.is_dropping or self.get_containers(bakemaster) is None:
            return

        datas = ["bakejobs", "containers", "subcontainers"]

        for data_name in datas:
            walk_data_getter = getattr(bm_get, "walk_data_get_%s" % data_name)
            data, containers, attr = walk_data_getter(bakemaster)
            if data is None:
                # print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")  # noqa: E501
                continue

            # remove drag_empties
            bm_set.disable_drag(bakemaster, data, containers, attr)

            if data.get_bm_name(bakemaster, attr) == "maps":
                continue

            self.add_drop_prompt(data, containers, attr)

        bakemaster.allow_drop = True
        self.is_dropping = True
        self.wait_events_end = False

    def drag_init(self, bakemaster):
        if self.is_dragging or self.get_containers(bakemaster) is None:
            return

        self.remove_drop_prompts(bakemaster)

        data, containers, attr = self.get_containers(bakemaster)

        # Add drag_empty to parent walk_data
        try:
            parent_data, parent_containers, parent_attr = getattr(
                bm_get, "walk_data_get_%s" % bm_get.walk_data_parent(
                    bakemaster.walk_data_name))(bakemaster)
        except (AttributeError, KeyError):
            parent_data = None
            parent_containers = None
            parent_attr = None

        containers_active_index = getattr(data, "%s_active_index" % attr)
        self.drag_end(bakemaster)

        self.add_drag_empty(data, containers, attr)
        if parent_data is not None:
            self.add_drag_empty(parent_data, parent_containers, parent_attr)

        self.reset_all_tickers(bakemaster)
        self.evaluate_data_trans(bakemaster, data, containers, attr)

        setattr(data, "%s_active_index" % attr, containers_active_index)

        bakemaster.allow_drag = True
        self.is_dragging = True

    def remove_drop_prompts(self, bakemaster):
        if self.get_containers(bakemaster) is None:
            return

        datas = ["bakejobs", "containers", "subcontainers"]

        for data_name in datas:
            walk_data_getter = getattr(bm_get, "walk_data_get_%s" % data_name)
            data, containers, attr = walk_data_getter(bakemaster)
            if data is None:
                # print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")  # noqa: E501
                continue
            if data.get_bm_name(bakemaster, attr) == "maps":
                continue

            mask = data.get_seq(attr, "has_drop_prompt", bool)
            to_remove = data.get_seq(attr, "index", int)[mask]

            for index in reversed(to_remove):
                containers.remove(index)

    def drop_end(self, _):
        if self.is_dropping:
            self.query_events_end = True
        self.is_dropping = False
        self.wait_events_end = False

    def drag_end(self, bakemaster):
        self.is_dragging = False

        if self.get_containers(bakemaster) is None:
            return
        data, containers, attr = self.get_containers(bakemaster)

        bm_set.disable_drag(bakemaster, data, containers, attr)

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
                    self.get_containers(bakemaster) is not None]):
            return

        data, containers, attr = self.get_containers(bakemaster)
        try:
            active_index = getattr(data, "%s_active_index" % attr)
            if active_index == -1:
                raise IndexError
            bakemaster.last_left_click_ticker = containers[active_index].ticker
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
        bakemaster.drag_to_index, values of which are set in container.ticker
        Updates.
        The Collection Property is determined by calling self.get_containers.

        Walk Data Transition is responsible for moving containers to another
        datas.
        """

        if bakemaster.drag_to_index > bakemaster.drag_from_index:
            new_index = bakemaster.drag_to_index - 1
        else:
            new_index = bakemaster.drag_to_index

        if self.get_containers(bakemaster) is not None:
            data, _, attr = self.get_containers(bakemaster)

            if bakemaster.allow_drag_trans:
                # move across walk_datas
                bpy_ops.bakemaster.walk_data_move_trans(
                    'INVOKE_DEFAULT',
                    drag_from_index=bakemaster.drag_from_index,
                    drag_to_index=bakemaster.drag_to_index)

            else:
                move_ot = getattr(bpy_ops.bakemaster, "%s_move" % attr)
                move_ot('INVOKE_DEFAULT', index=bakemaster.drag_from_index,
                        new_index=new_index)

                # no undo event:
                # containers.move(bakemaster.drag_from_index, new_index)

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
                bakemaster.drag_to_index != -1,
                event.type != 'NONE']):
            self.drag(bakemaster)
        elif bakemaster.allow_drag and bakemaster.drag_from_index == -1:
            self.drag_end(bakemaster)

        is_drop_available = self.is_drop_available(context, event, bakemaster)
        is_drag_available = self.is_drag_available(context, event, bakemaster)

        self.evaluate_double_click(event, bakemaster, is_drag_available)

        self.evaluate_multi_select(event, bakemaster, is_drag_available)

        if not any([is_drop_available, is_drag_available,
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

        global _walk_handler_invoked
        _walk_handler_invoked = True
        global _walk_handler_invoke_time
        _walk_handler_invoke_time = time()

        wm = context.window_manager
        wm.modal_handler_add(self)
        self.reset_props(context.scene.bakemaster)
        return {'RUNNING_MODAL'}


class BM_OT_Generic_AddDropped(Operator):
    """
    Generic AddDropped Operator with an execute method for faster AddDropped
    Operators.

    Requires invoke, add, remove methods dependant on the data an
    Operator is invoked on.
    """

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if bakemaster.allow_drop:
            self.remove()
            return {'CANCELLED'}

        add_names = []
        proceed = False

        for selected_object in context.selected_objects:
            add_names.append(selected_object.name)
            if selected_object.name == self.drop_name:
                proceed = True

        if not proceed:
            self.remove()
            return {'CANCELLED'}

        self.add(bakemaster, add_names)
        return {'FINISHED'}


class BM_OT_WalkData_Trans(Operator):
    """
    Move multi selection across walk_datas.
    """

    bl_idname = 'bakemaster.walk_data_move_trans'
    bl_label = "Move or copy"
    bl_description = "Move or copy containers to another place"
    bl_options = {'INTERNAL', 'UNDO'}

    use_copy: BoolProperty(
        name="Copy",
        description="Copy moved items here instead of moving",
        default=False)

    drag_from_index: IntProperty(default=-1)
    drag_to_index: IntProperty(default=-1)

    def trans_poll(self, bakemaster):
        if any([self.drag_from_index == -1, self.drag_to_index == -1]):
            return False, ""

        if self.get_destination_data(bakemaster) is None:
            return False, "Drag was cancelled"

        if not bakemaster.drag_data_from == bm_get.walk_data_child(
                bakemaster.drag_data_to):
            return False, ""

        # Reset in disable_drag()
        # has_selection, _ = bm_get.walk_data_multi_selection_data(
        #     bakemaster, bakemaster.drag_data_from)
        # return has_selection and bakemaster.allow_drag_trans, ""
        return True, ""

    def get_destination_data(self, bakemaster):
        drag_data_to_getter = getattr(
            bm_get, "walk_data_get_%s" % bakemaster.drag_data_to)
        data_to, containers_to, _ = drag_data_to_getter(bakemaster)

        destination_data = containers_to[self.drag_to_index]
        if destination_data.has_drop_prompt:
            destination_data = None
        elif destination_data.index == getattr(
                data_to, "%s_active_index" % bakemaster.drag_data_to):
            destination_data = None

        elif destination_data.is_drag_empty:
            add_ot = getattr(bpy_ops.bakemaster,
                             "%s_add" % bakemaster.drag_data_to)
            add_ot('INVOKE_DEFAULT')

            parent_data, parent_containers, parent_attr = getattr(
                bm_get, "walk_data_get_%s" % bakemaster.drag_data_to)(
                    bakemaster)
            active_index = getattr(parent_data,
                                   "%s_active_index" % parent_attr)
            try:
                if active_index == -1:
                    raise IndexError
                destination_data = parent_containers[-1]
            except IndexError:
                destination_data = None

        return destination_data

    def get_source(self, bakemaster):
        drag_data_from_getter = getattr(
            bm_get, "walk_data_get_%s" % bakemaster.drag_data_from)
        data_from, containers_from, attr_from = drag_data_from_getter(
            bakemaster)

        all_indexes = data_from.get_seq(attr_from, "index", int)
        selection_mask = data_from.get_seq(attr_from, "is_selected", bool)

        selected_indexes = all_indexes[:selection_mask.size][selection_mask]

        return containers_from, attr_from, selected_indexes

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        containers_from, attr_from, selected_indexes = self.get_source(
            bakemaster)

        destination_data = self.get_destination_data(bakemaster)
        if destination_data is None:
            return {'CANCELLED'}

        destination_containers = getattr(destination_data, attr_from)

        # add_ot = getattr(bpy_ops.bakemaster,
        #                  "%s_add" % bakemaster.drag_data_from)
        setattr(destination_data,
                "%s_active_index" % bakemaster.drag_data_to,
                self.drag_from_index)

        to_remove = []
        for index in selected_indexes:
            container_from = containers_from[index]
            if any([container_from.is_drag_empty,
                    container_from.has_drop_prompt]):
                continue

            new_container = destination_containers.add()
            # add_ot('INVOKE_DEFAULT')
            # new_container = destination_containers[:-1]
            setattr(destination_data, "%s_len" % bakemaster.drag_data_from,
                    getattr(destination_data,
                            "%s_len" % bakemaster.drag_data_from) + 1)

            attrs = bm_get.data_attrs(container_from)
            for attr in attrs:
                try:
                    setattr(new_container, attr, getattr(container_from, attr))
                except (AttributeError, IndexError, TypeError, ValueError):
                    pass

            new_container.is_drag_empty = False
            new_container.has_drop_prompt = False

            if not self.use_copy:
                to_remove.append(index)

        for index in reversed(to_remove):
            remove_ot = getattr(bpy_ops.bakemaster,
                                "%s_remove" % bakemaster.drag_data_from)
            remove_ot('INVOKE_DEFAULT', index=index)

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")

        return {'FINISHED'}

    def invoke(self, context, _):
        ok, message = self.trans_poll(context.scene.bakemaster)
        if not ok:
            if message != "":
                self.report({'INFO'}, message)
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=100)

    def draw(self, _):
        self.layout.prop(self, "use_copy")


class BM_OT_BakeJobs_Add(Operator):
    bl_idname = 'bakemaster.bakejobs_add'
    bl_label = "Add"
    bl_description = "Add a new Bake Job"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    def invoke(self, context, _):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakemaster, bakemaster.bakejobs,
                            "bakejobs")

        new_bakejob = bakemaster.bakejobs.add()
        new_bakejob.index = bakemaster.bakejobs_len
        new_bakejob.name = "Bake Job %d" % (new_bakejob.index + 1)
        new_bakejob.type = bakemaster.prefs_default_bakejob_type

        bakemaster.bakejobs_active_index = new_bakejob.index
        bakemaster.bakejobs_len += 1

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakemaster, bakemaster.bakejobs,
                            "bakejobs")
        return {'FINISHED'}


class BM_OT_BakeJobs_Remove(Operator):
    bl_idname = 'bakemaster.bakejobs_remove'
    bl_label = "Remove"
    bl_description = "Remove selected Bake Jobs from the list on the left"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    def invoke(self, context, _):
        if self.index == -1:
            self.index = context.scene.bakemaster.bakejobs_active_index
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakemaster, bakemaster.bakejobs,
                            "bakejobs")

        bakejob = bm_get.bakejob(bakemaster, self.index)
        if bakejob is None:
            return {'CANCELLED'}

        for index in range(bakejob.index + 1, bakemaster.bakejobs_len):
            try:
                bakemaster.bakejobs[index].index -= 1
            except IndexError:
                continue

        bakemaster.bakejobs.remove(bakejob.index)

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")

        bakemaster.bakejobs_len -= 1
        if not bakemaster.bakejobs_active_index < bakemaster.bakejobs_len:
            bakemaster.bakejobs_active_index = bakemaster.bakejobs_len - 1
        return {'FINISHED'}


class BM_OT_BakeJobs_Move(Operator):
    """
    Internal Bake Jobs Move Operator to move a Bake Job container inside Bake
    Jobs Collection. Not used in the UI but called in
    BM_OT_UIList_Walk_Handler.
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

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_BakeJobs_AddDropped(BM_OT_Generic_AddDropped):
    """
    Internal, not used in the UI, invoked from drop_name_Update.
    """

    bl_idname = 'bakemaster.bakejobs_adddropped'
    bl_label = "New Bake Job.."
    bl_description = "Add dropped objects into a new Bake Job"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    drop_name: StringProperty(default="")

    def remove(self):
        bpy_ops.bakemaster.bakejobs_remove('INVOKE_DEFAULT', index=self.index)

    def add(self, bakemaster, add_names: list):
        bpy_ops.bakemaster.bakejobs_add('INVOKE_DEFAULT', index=self.index)

        new_bakejob = bakemaster.bakejobs[bakemaster.bakejobs_len - 1]
        for name in add_names:
            bpy_ops.bakemaster.containers_add('INVOKE_DEFAULT',
                                              bakejob_index=new_bakejob.index,
                                              name=name)

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

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakemaster, bakemaster.bakejobs,
                            "bakejobs")

        [bakemaster.bakejobs.remove(index) for index in
         reversed(range(bakemaster.bakejobs_len))]
        bakemaster.bakejobs_active_index = -1
        bakemaster.bakejobs_len = 0

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")
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
        selection_seq = bakemaster.get_seq("bakejobs", "is_selected", bool)

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

        bm_ots_utils.indexes_recalc(bakemaster, "bakejobs")

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


class BM_OT_Containers_Add(Operator):
    bl_idname = 'bakemaster.containers_add'
    bl_label = "Add"
    bl_description = "Add new Item to selected Bake Jobs.\nIf active Bake Job type is Objects, pressing this button will add all valid selected Objects in the scene to the list"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    name: StringProperty(default="")

    def add(self, bakejob, name: str):
        new_container = bakejob.containers.add()
        new_container.index = bakejob.containers_len
        new_container.bakejob_index = bakejob.index
        new_container.name = name

        bakejob.containers_active_index = new_container.index
        bakejob.containers_len += 1

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        if self.bakejob_index == -1:
            self.bakejob_index = bakemaster.bakejobs_active_index
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bm_get.bakejob(bakemaster, self.bakejob_index)
        if bakejob is None:
            return {'CANCELLED'}

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakemaster, bakemaster.bakejobs,
                            "bakejobs")

        errors = 0

        if self.name == "":
            names = context.selected_objects
        else:
            names = [self]

        if len(names) == 0:
            self.report({'INFO'}, "Nothing is selected to add")
            return {'CANCELLED'}

        for name_holder in names:
            object, _, _, _, error_message = bm_get.object_ui_info(
                context.scene.objects, name_holder.name)

            if object is None:
                print("BakeMaster Object Add Error: %s" % error_message)
                errors += 1
                continue

            self.add(bakejob, name_holder.name)

        if errors:
            self.report({'WARNING'},
                        f"{errors} Object(s) could not be added (see Console)")

        bm_ots_utils.indexes_recalc(bakejob, "containers")

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakejob, bakejob.containers,
                            "containers")
        return {'FINISHED'}


class BM_OT_Containers_Remove(Operator):
    bl_idname = 'bakemaster.containers_remove'
    bl_label = "Remove"
    bl_description = "Remove selected Items from the list on the left"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster
        if self.bakejob_index == -1:
            self.bakejob_index = bakemaster.bakejobs_active_index

        if self.index == -1:
            container = bm_get.container(bm_get.bakejob(bakemaster))
            if container is not None:
                self.index = container.index

        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bm_get.bakejob(bakemaster, self.bakejob_index)
        container = bm_get.container(bakejob, self.index)
        if container is None or bakejob is None:
            return {'CANCELLED'}

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakejob, bakejob.containers,
                            "containers")

        for index in range(container.index + 1, bakejob.containers_len):
            try:
                bakejob.containers[index].index -= 1
            except IndexError:
                continue
        bakejob.containers.remove(container.index)

        bm_ots_utils.indexes_recalc(bakejob, "containers")

        bakejob.containers_len -= 1
        if not bakejob.containers_active_index < bakejob.containers_len:
            bakejob.containers_active_index = bakejob.containers_len - 1
        return {'FINISHED'}


class BM_OT_Containers_Move(Operator):
    """
    Internal Containers Move Operator to move an Container inside Bake Job's
    Containers Collection. Not used in the UI but called in
    BM_OT_UIList_Walk_Handler. This Operator exists only for the sake of a
    Move Undo event.

    Call with providing the index of the Container and its new_index.
    """

    bl_idname = 'bakemaster.containers_move'
    bl_label = "Move an Item (Internal)"
    bl_description = "Move Item's bake order up or down"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)
    new_index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bm_get.bakejob(bakemaster)
        if bakejob is None:
            return {'CANCELLED'}

        try:
            if any([self.index == -1, self.new_index == -1]):
                raise IndexError
            bakejob.containers[self.index]
            bakejob.containers[self.new_index]
        except IndexError:
            print("BakeMaster: Internal warning: cannot resolve Bake Job")
            return {'CANCELLED'}

        bakejob.containers.move(self.index, self.new_index)

        bm_ots_utils.indexes_recalc(bakejob, "containers")
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_Containers_AddDropped(BM_OT_Generic_AddDropped):
    """
    Internal, not used in the UI, invoked from drop_name_Update.
    """

    bl_idname = 'bakemaster.containers_adddropped'
    bl_label = "New Object..."
    bl_description = "Add dropped Objects into the table"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    drop_name: StringProperty(default="")

    def remove(self, bakemaster):
        remove_ot = bpy_ops.bakemaster.containers_remove
        remove_ot('INVOKE_DEFAULT',
                  bakejob_index=bakemaster.bakejobs_active_index,
                  index=self.index)

    def add(self, bakemaster, add_names: list):
        add_ot = bpy_ops.bakemaster.containers_add
        for name in add_names:
            add_ot('INVOKE_DEFAULT',
                   bakejob_index=bakemaster.bakejobs_active_index,
                   name=name)

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        bakejob = bm_get.bakejob(bakemaster)
        if bakejob is None:
            return {'CANCELLED'}

        try:
            bakejob.containers[self.index]
            if self.index == -1:
                raise IndexError
        except IndexError:
            return self.execute(context)
        else:
            self.remove()
            return {'CANCELLED'}


class BM_OT_Containers_Trash(Operator):
    bl_idname = 'bakemaster.containers_trash'
    bl_label = "Trash"
    bl_description = "Remove all Items from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, _):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bm_get.bakejob(bakemaster)
        if bakejob is None:
            return {'CANCELLED'}

        # reduce flicker and hidden containers on add (uilist mess)
        bm_set.disable_drag(bakemaster, bakejob, bakejob.containers,
                            "containers")

        [bakejob.containers.remove(index) for index in
         reversed(range(bakejob.containers_len))]
        bakejob.containers_active_index = -1
        bakejob.containers_len = 0

        bm_ots_utils.indexes_recalc(bakejob, "containers")
        return {'FINISHED'}


class BM_OT_Container_Rename(Operator):
    bl_idname = 'bakemaster.container_rename'
    bl_label = "Relink the Object to the new one"
    bl_description = "Click to rename the Object"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    name: StringProperty(
        name="New name",
        description="Enter new name",
        default="",
        options={'SKIP_SAVE'})

    container = None
    bakejob_type = ''

    def execute(self, context):
        if self.container is None:
            return {'CANCELLED'}

        if self.bakejob_type == 'OBJECTS':
            object, _, _, _, error_message = bm_get.object_ui_info(
                context.scene.objects, self.name)

            if object is None:
                self.report({'ERROR'}, error_message)
                return {'CANCELLED'}

            self.container.obj_name = self.name

        elif self.bakejob_type == 'MAPS':
            pass

        self.container.name = self.name
        return {'FINISHED'}

    def invoke(self, context, _):
        bakejob = bm_get.bakejob(context.scene.bakemaster)
        self.container = bm_get.container(bakejob, self.index)

        if self.container is None or bakejob is None:
            self.report({'WARNING',
                         "Internal error: Cannot resolve Container"})
            return {'CANCELLED'}

        self.name = self.container.name
        self.bakejob_type = bakejob.type

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.prop(self, "name")


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
