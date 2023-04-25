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
from .get import walk_data_parent
from bpy import ops as bpy_ops


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


def disable_drag(bakemaster, data, containers, attr, clear_selection=True):
    bakemaster.allow_drag = False
    bakemaster.drag_from_index = -1
    bakemaster.drag_to_index = -1
    bakemaster.drag_to_index_temp = -1
    bakemaster.drag_from_ticker = False
    bakemaster.allow_multi_selection_drag = False

    if bakemaster.allow_drag_trans and clear_selection:
        clear_multi_selection(None, bakemaster, attr)
    bakemaster.allow_drag_trans = False

    mask = data.get_seq(attr, "is_drag_empty", bool)
    to_remove = data.get_seq(attr, "index", int)[mask]

    data.set_seq(attr, "has_drag_prompt", False)
    data.set_seq(attr, "is_drag_placeholder", False)

    for index in reversed(to_remove):
        containers.remove(index)


def indexes_recalc(data, items_name: str, childs_recursive=True,
                   parent_props=[]):
    child = {
        "bakejobs": "containers",
        "containers": "subcontainers",
        "subcontainers": "",
        "bakehistory": ""
    }

    if not hasattr(data, items_name):
        return

    index = 0
    for item in getattr(data, items_name):
        item.index = index

        for prop_name, prop_val in parent_props:
            if hasattr(item, prop_name):
                setattr(item, prop_name, prop_val)
            else:
                print(f"BakeMaster Internal AttributeError: {item} has no {prop_name} attribute")  # noqa: E501

        if childs_recursive:
            indexes_recalc(
                item, child[items_name], childs_recursive,
                parent_props + [["%s_index" % items_name[:-1], item.index]])
        index += 1


def copy(item_from, data_to, to_index=-1):
    """
    Copy item_from data-block to item of to_index in iterable data_to.
    If to_index is not given, a new data-block will be instanced.

    Used with containers, subcontainers.
    """

    exclude_attrs = {
        "__annotations__": True,
        "__doc__": True,
        "__module__": True,
        "bl_rna": True,
        "id_data": True,
        "drop_name": True,
        "drop_name_old": True,
        "has_drag_prompt": True,
        "has_drop_prompt": True,
        "is_drag_placeholder": True,
        "is_selected": True,
        "parent_group_index": True,
        "rna_type": True,
        "ticker": True,
        "ui_indent_level": True
    }

    data_attrs = {
        "bakejobs": True,
        "containers": True,
        "subcontainers": True
    }

    if to_index != -1:
        item_to = data_to[to_index]
    else:
        item_to = data_to.add()

    for attr in dir(item_from):
        if exclude_attrs.get(attr, False):
            continue

        if not data_attrs.get(attr, False):
            try:
                setattr(item_to, attr, getattr(item_from, attr))
            except (AttributeError, IndexError, TypeError,
                    ValueError) as error:
                print(f"BakeMaster Internal Warning at {copy}: {error} while setting {attr} attribute for {item_to}")  # noqa: E501

            continue

        # for containers only (attr == subcontainers)
        # still, some safety adressed
        try:
            trash_ot = getattr(bpy_ops.bakemaster, '%s_trash' % attr)
        except AttributeError:
            continue
        kwargs = {}
        data_attr_parent = walk_data_parent(attr)
        if data_attr_parent != "":
            kwargs["%s_index" % data_attr_parent[:-1]] = item_from.index
            kwargs["bakejob_index"] = item_from.bakejob_index
        trash_ot('INVOKE_DEFAULT', **kwargs)

        # recursive copy to copy subcontainers from container
        containers = getattr(item_from, attr)
        for container in containers:
            _ = copy(container, containers)

    return item_to
