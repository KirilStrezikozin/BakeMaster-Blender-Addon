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
from ..utils import (
    get as bm_get,
    operators as bm_ots_utils,
    ui as bm_ui_utils,
)
from ..utils.properties import copy as bm_props_utils_copy
from ..properties import (
    Container,
    BakeJob,
)

_walk_handler_invoked = False
_walk_handler_invoke_time = 0


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
        bakemaster.drag_to_index_temp = -1
        bakemaster.drad_data_from = ""
        bakemaster.drad_data_to = ""
        bakemaster.allow_drag_trans = False
        bakemaster.drag_from_ticker = False
        bakemaster.allow_multi_selection_drag = False
        bakemaster.is_drag_lowpoly_data = False

        bakemaster.allow_multi_select = False
        bakemaster.multi_select_event = ''
        bakemaster.is_multi_selection_empty = True
        bakemaster.multi_selection_data = ""
        bakemaster.allow_prop_in_multi_selection_update = True

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
        """
        Reset tickers in every walk_data as such drag to other data won't
        cause errors.
        """

        datas = ["bakejobs", "containers", "subcontainers"]

        for data_name in datas:
            walk_data_getter = getattr(bm_get, "walk_data_get_%s" % data_name)
            data, containers, _ = walk_data_getter(bakemaster)
            if data is None:
                # print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")  # noqa: E501
                continue

            containers.foreach_set("ticker", [False] * len(containers))
            containers.foreach_set("is_drag_empty", [False] * len(containers))
            containers.foreach_set("is_drag_placeholder",
                                   [False] * len(containers))
            containers.foreach_set("is_drag_empty_placeholder",
                                   [False] * len(containers))
            containers.foreach_set("is_lowpoly_placeholder",
                                   [False] * len(containers))

            # XXX
            # seemed to be faster but breaks everything
            # for container in containers:
            #     container.ticker = False
            #     container.drag_empty_ticker = False
            #     container.has_drag_prompt = False
            #     container.is_drag_placeholder = False
            #     container.is_drag_empty_placeholder = False
            #     container.is_lowpoly_placeholder = False
            #     container.is_drag_empty = False

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
            bm_ots_utils.disable_drag(bakemaster, data, containers, attr)

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
        containers_active_index = getattr(data, "%s_active_index" % attr)

        self.drag_end(bakemaster)
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

        bm_ots_utils.disable_drag(bakemaster, data, containers, attr)

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
        bakemaster.get_drag_to_index(), values of which are set in
        container.ticker Updates.
        The Collection Property is determined by calling self.get_containers.

        Walk Data Transition is responsible for moving containers to another
        datas.

        Move Lowpoly Data is responsible for adding HCDs (Highpolies, Cages,
        Decals) to a Lowpoly of bakemaster.get_drag_to_index().
        """

        data, containers, attr = self.get_containers(bakemaster)

        if data is None:
            print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")  # noqa: E501
            self.drag_end(bakemaster)
            return

        drag_to_index = bakemaster.get_drag_to_index(attr)
        if drag_to_index == -1 or drag_to_index >= getattr(data,
                                                           "%s_len" % attr):
            self.drag_end(bakemaster)
            return

        if containers[drag_to_index].is_drag_empty_placeholder:
            drag_to_index += 1

        # move across walk_datas
        if bakemaster.allow_drag_trans and attr != bakemaster.drag_data_from:
            bpy_ops.bakemaster.walk_data_move_trans(
                'INVOKE_DEFAULT',
                drag_from_index=bakemaster.drag_from_index,
                drag_to_index=bakemaster.drag_to_index)

        # move lowpoly data
        elif all([bakemaster.is_drag_lowpoly_data,
                  attr == bakemaster.drag_data_from]):
            bpy_ops.bakemaster.walk_data_move_lowpoly_data(
                'INVOKE_DEFAULT',
                index=bakemaster.drag_from_index, new_index=drag_to_index,
                data_name=attr,
                ml_drag=bakemaster.allow_multi_selection_drag)

        # default move, multi selection move
        # check if move is inside data
        elif attr == bakemaster.drag_data_from:
            bpy_ops.bakemaster.walk_data_move(
                    'INVOKE_DEFAULT',
                    index=bakemaster.drag_from_index, new_index=drag_to_index,
                    data_name=attr,
                    ml_drag=bakemaster.allow_multi_selection_drag)

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
                bakemaster.get_drag_to_index(bakemaster.walk_data_name) != -1,
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
            self.remove(bakemaster)
            return {'CANCELLED'}

        add_names = []
        proceed = False

        for selected_object in context.selected_objects:
            add_names.append(selected_object.name)
            if selected_object.name == self.drop_name:
                proceed = True

        if not proceed:
            self.remove(bakemaster)
            return {'CANCELLED'}

        self.add(bakemaster, add_names)
        return {'FINISHED'}


class BM_OT_WalkData_Move_Lowpoly_Data(Operator):
    """
    Add moved container(s) as HCDs (Highpolies, Cages, Decals) for the Lowpoly
    of given index inside data. Gets called in BM_OT_UIList_Walk_Handler
    based on walk_data identifier.
    Exists only for the sake of a Move Undo event.

    ml_drag equals to bakemaster.allow_multi_selection_drag (given to be safe
    from event handler calls).

    data_name is an identifier of walk_data with uilist walk features.
    """

    bl_idname = 'bakemaster.walk_data_move_lowpoly_data'
    bl_label = "Add data"
    bl_description = "Add Highpolies, Cages, and Decals for the Lowpoly"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)
    new_index: IntProperty(default=-1)
    data_name: StringProperty(default="")
    ml_drag: BoolProperty(default=False)

    def execute(self, context):
        self.report({'WARNING'}, "Not implemented")
        return {'FINISHED'}

    def invoke(self, context, _):
        pass


class BM_OT_WalkData_Trans(Operator):
    """
    Move multi selection across walk_datas.
    Gets called in BM_OT_UIList_Walk_Handler based on walk_data identifier.
    Exists only for the sake of a Move Undo event.
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

        elif destination_data.is_drag_empty_placeholder:
            old_active_index = getattr(
                data_to, "%s_active_index" % bakemaster.drag_data_to)

            add_ot = getattr(bpy_ops.bakemaster,
                             "%s_add" % bakemaster.drag_data_to)
            add_ot('INVOKE_DEFAULT')

            setattr(data_to, "%s_active_index" % bakemaster.drag_data_to,
                    old_active_index)

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

        # bm_ots_utils.disable_drag(bakemaster, data_to, containers_to,
        #                           bakemaster.drag_data_to)

        return destination_data

    def get_source(self, bakemaster):
        drag_data_from_getter = getattr(
            bm_get, "walk_data_get_%s" % bakemaster.drag_data_from)
        data_from, containers_from, attr_from = drag_data_from_getter(
            bakemaster)

        bm_ots_utils.disable_drag(bakemaster, data_from, containers_from,
                                  attr_from)

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
            if container_from.has_drop_prompt:
                continue

            # add_ot('INVOKE_DEFAULT')
            # new_container = destination_containers[:-1]
            new_container = bm_props_utils_copy(container_from,
                                                destination_containers)
            setattr(destination_data, "%s_len" % bakemaster.drag_data_from,
                    getattr(destination_data,
                            "%s_len" % bakemaster.drag_data_from) + 1)

            new_container.has_drop_prompt = False

            if not self.use_copy:
                to_remove.append(index)

        remove_ot = getattr(bpy_ops.bakemaster,
                            "%s_remove" % bakemaster.drag_data_from)
        for index in reversed(to_remove):
            remove_ot('INVOKE_DEFAULT', index=index)

        bm_ots_utils.disable_drag(bakemaster, destination_data,
                                  destination_containers,
                                  bakemaster.drag_data_from)
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


class BM_OT_WalkData_Move(Operator):
    """
    Move container(s) inside data. Gets called in BM_OT_UIList_Walk_Handler
    based on walk_data identifier.
    Exists only for the sake of a Move Undo event.

    ml_drag equals to bakemaster.allow_multi_selection_drag (given to be safe
    from event handler calls).

    data_name is an identifier of walk_data with uilist walk features.
    """

    bl_idname = 'bakemaster.walk_data_move'
    bl_label = "Move"
    bl_description = "Move item(s) bake order up or down"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)
    new_index: IntProperty(default=-1)
    data_name: StringProperty(default="")
    ml_drag: BoolProperty(default=False)

    def after_execute(self, bakemaster, data, containers, attr):
        """
        If inherited, overwrite this method for custom operations after
        execute.
        """

        setattr(data, "%s_active_index" % attr, self.new_index)
        bm_ots_utils.indexes_recalc(data, attr)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        data, containers, attr = getattr(
            bm_get, "walk_data_get_%s" % self.data_name)(bakemaster)

        if data is None or any([self.index == -1, self.new_index == -1]):
            print(f"BakeMaster Internal Error: not enough data at {self}")  # noqa: E501
            return {'CANCELLED'}

        # remove drag_empties for correct reindex
        bm_ots_utils.disable_drag(bakemaster, data, containers, attr,
                                  clear_selection=False)

        # default one-item drag
        if not self.ml_drag:
            try:
                containers[self.index]
                containers[self.new_index]
            except IndexError:
                print(f"BakeMaster: Internal warning: cannot resolve container at {self}")  # noqa: E501
                return {'CANCELLED'}

            containers.move(self.index, self.new_index)
            self.after_execute(bakemaster, data, containers, attr)
            return {'FINISHED'}

        # multi selection drag
        active_container = getattr(bm_get, attr[:-1])(data, self.new_index)
        if active_container is None:
            print(f"BakeMaster: Internal warning: cannot resolve container at {self}")  # noqa: E501
            return {'CANCELLED'}

        # skip if dragged onto selection itself
        if active_container.is_selected:
            return {'CANCELLED'}

        containers_len = getattr(data, "%s_len" % attr)
        is_index_set = False
        step = 0

        for container in containers:
            if any([container.index >= containers_len,
                    container.has_drop_prompt,
                    not container.is_selected]):
                continue

            # up
            if self.new_index <= self.index:
                containers.move(container.index, self.new_index + step)
                step += 1
                continue

            # down
            if not is_index_set:
                self.index = container.index
                is_index_set = True
            elif not containers[self.index].is_selected:
                continue
            containers.move(self.index, self.new_index)

        self.after_execute(bakemaster, data, containers, attr)
        return {'FINISHED'}

    def invoke(self, context, _):
        if self.new_index > self.index:
            self.new_index -= 1
        return self.execute(context)


class BM_OT_UI_Prop_Relinquish(Operator):
    bl_idname = 'bakemaster.ui_prop_relinquish'
    bl_label = "Set similar values"
    bl_description = "Each selected item will have the same value of this property"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    data_name: StringProperty(default="")
    prop_name: StringProperty(default="")

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        data, _, attr = getattr(
            bm_get, "walk_data_get_%s" % self.data_name)(bakemaster)
        if data is None:
            print(f"BakeMaster Internal Error: not enough data at {self}")  # noqa: E501
            return {'CANCELLED'}

        container = getattr(bm_get, attr[:-1])(data)
        setattr(container, self.prop_name, getattr(container, self.prop_name))
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)
