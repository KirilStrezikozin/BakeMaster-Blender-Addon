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

from datetime import datetime
from .properties import Generic_multi_select as clear_multi_selection


def ui_bake_poll(bakemaster, bake_is_running):
    if bake_is_running:
        return False, "Another bake is running"
    if any([bakemaster.bake_trigger_cancel,
            bakemaster.bake_trigger_stop]):
        return False, "Bake is not available"
    return True, ""


def ui_bakehistory_poll(cls_instance, bakemaster):
    if cls_instance.index == -1:
        return False, "Internal Error: Cannot resolve item in Bake History"
    try:
        bakehistory = bakemaster.bakehistory[cls_instance.index]
    except IndexError:
        return False, "Internal Error: Cannot resolve item in Bake History"
    if bakemaster.bakehistory_reserved_index == bakehistory.index:
        return False, "Item in Bake History is currently baking"
    return True, ""


def bakehistory_add(bakemaster):
    new_item = bakemaster.bakehistory.add()
    new_item.index = bakemaster.bakehistory_len
    new_item.name += " %d" % (new_item.index + 1)
    bakemaster.bakehistory_len += 1
    bakemaster.bakehistory_reserved_index = new_item.index


def bakehistory_remove(bakemaster, remove_index):
    if bakemaster.bakehistory_reserved_index > remove_index:
        bakemaster.bakehistory_reserved_index -= 1
    for index in range(remove_index + 1, bakemaster.bakehistory_len):
        bakemaster.bakehistory[index].index -= 1
    bakemaster.bakehistory.remove(remove_index)
    bakemaster.bakehistory_len -= 1


def bakehistory_unreserve(bakemaster):
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


def disable_drag(bakemaster, _, containers, attr, clear_selection=True):
    """
    Turn off drag and remove drag_empties.
    If clear_selection is True, unset multi selection.

    Call before adding items to collections to reduce flicker of undrawn
    containers. Call when removing items from collections to not take
    drag_empty away by mistake.
    """

    bakemaster.allow_drag = False
    bakemaster.drag_from_index = -1
    bakemaster.drag_to_index = -1
    bakemaster.drag_to_index_temp = -1
    bakemaster.drag_from_ticker = False
    bakemaster.allow_multi_selection_drag = False
    bakemaster.is_drag_lowpoly_data = False

    if bakemaster.allow_drag_trans and clear_selection:
        clear_multi_selection(None, bakemaster, attr)
    bakemaster.allow_drag_trans = False

    containers.foreach_set("has_drag_prompt", [False] * len(containers))
    containers.foreach_set("is_drag_placeholder",
                           [False] * len(containers))
    containers.foreach_set("is_drag_empty_placeholder",
                           [False] * len(containers))
    containers.foreach_set("is_lowpoly_placeholder",
                           [False] * len(containers))
    containers.foreach_set("is_drag_empty",
                           [False] * len(containers))
    # XXX
    # seemed to be faster but breaks everything
    # for container in containers:
    #     container.has_drag_prompt = False
    #     container.is_drag_placeholder = False
    #     container.is_drag_empty_placeholder = False
    #     container.is_lowpoly_placeholder = False
    #     container.is_drag_empty = False


def indexes_recalc(data, items_name: str, childs_recursive=True, groups=True,
                   parent_props=[]):
    """
    Recalculate items' indexes.
    Continues recalculating childs' indexes recursively and updating childs'
    pointers to parent indexes.

    if groups is True, recalculate items' parent_group_indexes based on their
    ui_indent_levels.

    Explicit parent_props[] can be given. Example:
        ...

        bm_ots_utils.indexes_recalc(
            bakejob, "containers", parent_props=[
                ["bakejob_index", bakejob.index]])

        ...
    """

    child = {
        "bakejobs": "containers",
        "containers": "subcontainers",
        "subcontainers": "",
        "bakehistory": ""
    }

    if not hasattr(data, items_name):
        return

    containers = getattr(data, items_name)
    group_index = -1
    group_level = -1

    index = 0
    for container in containers:
        container.index = index

        # if container.has_drop_prompt:
        #     continue

        # assign parent_group_index
        if groups:
            if not container.ui_indent_level >= group_level:
                group_index, _ = data.resolve_mutual_group(
                    containers, group_index, group_level, container.index,
                    container.ui_indent_level)

            container.parent_group_index = group_index
            group_level = container.ui_indent_level

            if container.is_group:
                group_index = container.index

        # assign parent's props
        for prop_name, prop_val in parent_props:
            if hasattr(container, prop_name):
                setattr(container, prop_name, prop_val)
            else:
                print(f"BakeMaster Internal AttributeError: {container} has no {prop_name} attribute")  # noqa: E501

        if childs_recursive:
            indexes_recalc(
                container, child[items_name], childs_recursive, groups,
                parent_props + [["%s_index" % items_name[:-1],
                                 container.index]])
        index += 1
