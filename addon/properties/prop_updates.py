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
    Context,
    PropertyGroup,
    bpy_prop_collection as Collection,
)


def _drag_empty_eval(self: PropertyGroup, data: PropertyGroup,
                     containers: Collection, data_name: str) -> None:

    if self.get_is_last(data, data_name):
        self.is_drag_empty = True
    elif self.get_next_item(containers).ui_indent_level < self.ui_indent_level:
        self.is_drag_empty = True


def _is_drag_group_into_itself(
        self: PropertyGroup, bakemaster: PropertyGroup, data: PropertyGroup,
        containers: Collection, data_name: str) -> bool:
    """Skip dragging group inside itself."""

    if data_name != bakemaster.drag_data_from:
        return False

    # If no multi selection, self = self, check drag_from_index,
    # otherwise self = first selected item, check first selected item index.
    has_ms = bakemaster.wh_has_ms(data, data_name)

    abort_if_not_group = False
    if has_ms:
        for container in containers:
            if container.has_drop_prompt or not container.is_selected:
                continue
            elif not container.is_group:
                continue
            drag_from_index = container.index
            break
        else:
            drag_from_index = bakemaster.drag_from_index
            abort_if_not_group = True
    else:
        drag_from_index = bakemaster.drag_from_index
        abort_if_not_group = True

    if abort_if_not_group and not containers[drag_from_index].is_group:
        return False

    if not all([self.index > drag_from_index,
                data_name == bakemaster.drag_data_from]):
        return False

    m_gi, m_gl = data.resolve_mutual_group(
        containers, self.index, self.ui_indent_level,
        drag_from_index, containers[drag_from_index].ui_indent_level)

    if m_gi == -1:
        return False

    if all([any([m_gi == drag_from_index,
                 m_gi == containers[drag_from_index].parent_group_index]),
            any([m_gl >= containers[drag_from_index].ui_indent_level,
                 m_gl >= containers[drag_from_index].ui_indent_level - 1])
            ]):
        return True
    return False


def _generic_ticker_Update(self: PropertyGroup, context: Context,
                           walk_data: str, double_click_ot_idname="") -> None:
    """
    Generic ticker property update.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - current data context.

        walk_data - attribute name of Collection Property that
                has uilist walk features.

        double_click_ot - bl_idname of an operator that will be called on
                double click event caught.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data
    bakemaster.is_drag_lowpoly_data = False

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, attr = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    if all([bakemaster.is_double_click,
            bakemaster.last_left_click_ticker != self.ticker,
            self.index == getattr(data, "%s_active_index" % attr),
            not self.has_drop_prompt,
            double_click_ot_idname != ""]):

        double_click_ot = getattr(bpy_ops.bakemaster, double_click_ot_idname)
        double_click_ot('INVOKE_DEFAULT', index=self.index)

        bakemaster.is_double_click = False
        return

    # Do not manage multi_select on drag transition.
    # But do manage if there's a multi_select_event.
    if all([bakemaster.allow_multi_select,
            any([not bakemaster.allow_drag_trans,
                 bakemaster.multi_select_event != ''])]):
        _generic_multi_select(self, bakemaster, walk_data)
        return

    if not bakemaster.allow_drag:
        setattr(data, "%s_active_index" % attr, self.index)
        self.has_drag_prompt = False
        return

    if bakemaster.drag_from_index == -1:
        setattr(data, "%s_active_index" % attr, self.index)
        self.has_drag_prompt = True
        bakemaster.drag_from_index = self.index
        bakemaster.drag_data_from = walk_data
        bakemaster.drag_from_ticker = self.ticker

        # Define bakemaster.allow_multi_selection_drag
        # (if one-block selection)
        setattr(bakemaster, "allow_multi_selection_drag",
                bakemaster.wh_is_oneblock_ms(
                    bakemaster, containers, attr))
        return

    # Skip when dragging to invalid datas
    if any([all([not bakemaster.allow_drag_trans,
                 walk_data != bakemaster.drag_data_from]),
            all([
                bakemaster.allow_drag_trans,
                bakemaster.get_wh_childs_name(
                    walk_data) != bakemaster.drag_data_from,
                not bakemaster.allow_multi_selection_drag,
                ])]):
        return

    # Skip one-block multi selection drag
    # if bakemaster.allow_multi_selection_drag:
    #     return

    # Skip trans drag to the container the containers were dragged from
    # if all([bm_get.walk_data_child(walk_data) == bakemaster.drag_data_from,
    #         self.index == getattr(data, "%s_active_index" % attr)]):
    #     return

    if _is_drag_group_into_itself(self, bakemaster, data, containers,
                                  walk_data):
        return

    drag_to_index = bakemaster.get_drag_to_index(walk_data)
    if drag_to_index != -1:
        containers[drag_to_index].is_drag_placeholder = False
        containers[drag_to_index].is_drag_empty_placeholder = False
        containers[drag_to_index].is_lowpoly_placeholder = False
        containers[drag_to_index].is_drag_empty = False
    self.is_drag_placeholder = True
    self.is_drag_empty_placeholder = False
    self.is_lowpoly_placeholder = False
    _drag_empty_eval(self, data, containers, walk_data)

    bakemaster.set_drag_to_index(walk_data, self.index)
    bakemaster.drag_data_to = walk_data

    ticker_old = bakemaster.drag_from_ticker
    if self.ticker == ticker_old:
        self.ticker = not ticker_old


def _generic_drag_empty_ticker_Update(self: PropertyGroup, context: Context,
                                      walk_data: str) -> None:
    """
    Generic drag_empty_ticker property update.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data
    bakemaster.is_drag_lowpoly_data = False

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, _ = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    if _is_drag_group_into_itself(self, bakemaster, data, containers,
                                  walk_data):
        return

    drag_to_index = bakemaster.get_drag_to_index(walk_data)
    if drag_to_index != -1:
        containers[drag_to_index].is_drag_placeholder = False
        containers[drag_to_index].is_drag_empty_placeholder = False
        containers[drag_to_index].is_lowpoly_placeholder = False
        containers[drag_to_index].is_drag_empty = False
    self.is_drag_placeholder = False
    self.is_drag_empty_placeholder = True
    self.is_lowpoly_placeholder = False
    _drag_empty_eval(self, data, containers, walk_data)

    bakemaster.set_drag_to_index(walk_data, self.index)
    bakemaster.drag_data_to = walk_data

    ticker_old = bakemaster.drag_from_ticker
    if self.drag_empty_ticker == ticker_old:
        self.drag_empty_ticker = not ticker_old


def _generic_lowpoly_ticker_Update(self: PropertyGroup, context: Context,
                                   walk_data: str) -> None:
    """
    Generic lowpoly_ticker property update.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.
    """

    bakemaster = context.scene.bakemaster

    # lowpoly_ticker is for Objects exclusively
    if walk_data != self.get_bm_name(bakemaster, walk_data) != "objects":
        return

    bakemaster.walk_data_name = walk_data

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, _ = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    if _is_drag_group_into_itself(self, bakemaster, data, containers,
                                  walk_data):
        return

    bakemaster.is_drag_lowpoly_data = True

    drag_to_index = bakemaster.get_drag_to_index(walk_data)
    if drag_to_index != -1:
        containers[drag_to_index].is_drag_placeholder = False
        containers[drag_to_index].is_drag_empty_placeholder = False
        containers[drag_to_index].is_lowpoly_placeholder = False
        containers[drag_to_index].is_drag_empty = False
    self.is_drag_placeholder = False
    self.is_drag_empty_placeholder = False
    self.is_lowpoly_placeholder = True

    bakemaster.set_drag_to_index(walk_data, self.index)
    bakemaster.drag_data_to = walk_data

    ticker_old = bakemaster.drag_from_ticker
    if self.lowpoly_ticker == ticker_old:
        self.lowpoly_ticker = not ticker_old


def _generic_active_index_Update(self: PropertyGroup, context: Context,
                                 walk_data: str) -> None:
    """
    Generic active_index property update.
    Revert to active_index_old when setting props of drop_prompt
    containers.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, attr = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return
    active_index = getattr(data, "%s_active_index" % attr)

    if active_index == getattr(data, "%s_active_index_old" % attr):
        return

    if active_index == -1:
        return
    try:
        containers[active_index]
    except IndexError:
        setattr(data, "%s_active_index" % attr,
                getattr(data, "%s_active_index_old" % attr))
        return
    if containers[active_index].has_drop_prompt:
        setattr(data, "%s_active_index" % attr,
                getattr(data, "%s_active_index_old" % attr))
        return

    setattr(data, "%s_active_index_old" % attr, active_index)

    has_ms = bakemaster.wh_has_ms(data, walk_data)
    if has_ms:
        containers[active_index].is_selected = True


def _generic_drop_name_Update(self: PropertyGroup, context: Context,
                              walk_data: str) -> None:
    """
    Generic drop_name property update.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    if self.drop_name_old == self.drop_name:
        return

    self.drop_name_old = self.drop_name
    bpy_ops.bakemaster.BM_OT_WalkData_AddDropped(
        'INVOKE_DEFAULT', walk_data=walk_data, index=self.index,
        drop_name=self.drop_name)


def _generic_multi_select(self: PropertyGroup, bakemaster: PropertyGroup,
                          walk_data: str) -> None:
    """
    Generic multiple selection manifestor.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        bakemaster - main PropertyGroup.

        walk_data - attribute name of Collection Property that
                has uilist walk features.

    Call with None self to clear multi selection.
    """

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, attr = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return
    active_index = getattr(data, "%s_active_index" % attr)

    # multi selection viz allowed in the walk_data only
    # limited to only one parent (if one bakejob has multi selected containers,
    # other bakejobs may not have them visualized)
    if hasattr(data, "index"):
        parent_index = data.index
    else:
        parent_index = ""
    our_multi_selection_data = f"{walk_data}_{parent_index}"

    # do not visualize multi selection if the previous one is not cleared
    if all([bakemaster.multi_selection_data != "",
            bakemaster.multi_selection_data != our_multi_selection_data,
            self is not None]):
        setattr(data, "%s_active_index" % attr, self.index)
        return

    if all([bakemaster.multi_select_event != 'CTRL',
            bakemaster.multi_select_event != 'SHIFT']):

        bakemaster.allow_multi_select = False
        bakemaster.is_multi_selection_empty = True
        bakemaster.multi_selection_data = ""  # free reserve
        containers.foreach_set("is_selected",
                               [False] * getattr(data, "%s_len" % attr))

    if self is None:
        return
    self.is_selected = True
    bakemaster.is_multi_selection_empty = False
    bakemaster.multi_selection_data = our_multi_selection_data  # reserve

    if bakemaster.multi_select_event == 'CTRL':
        if active_index == self.index:
            self.is_selected = False
            setattr(data, "%s_active_index" % attr, -1)
            return

        setattr(data, "%s_active_index" % attr, self.index)

    elif bakemaster.multi_select_event == 'SHIFT':
        if active_index == -1:
            setattr(data, "%s_active_index" % attr, self.index)

        if active_index < self.index:
            selection_range = range(active_index, self.index + 1, 1)
        else:
            selection_range = range(active_index, self.index - 1, -1)

        for container in containers:
            container.is_selected = container.index in selection_range


def _generic_property_in_multi_selection_Update(
        self: PropertyGroup, context: Context, walk_data: str, prop_name: str
        ) -> None:
    """
    Generic property in multi selection update function. Lets set prop_name's
    property values in data's containers that are in multi selection.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.

        prop_name - name of the property to update value of.
    """

    bakemaster = context.scene.bakemaster

    if not bakemaster.allow_prop_in_multi_selection_update:
        return

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, _ = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    has_ms = bakemaster.wh_has_ms(data, walk_data)
    if not has_ms:
        return

    bakemaster.walk_data_name = walk_data
    bakemaster.multi_select_event = 'CTRL'

    # no recursive updates
    bakemaster.allow_prop_in_multi_selection_update = False

    # foreach_get/set does not work for enum
    # see https://projects.blender.org/blender/blender/issues/92621
    #
    # values = data.get_seq(attr, prop_name, prop_type)
    # mask = data.get_seq(attr, "is_selected", bool)
    # values[mask] = getattr(self, prop_name)
    # containers.foreach_set(prop_name, values)
    #
    # simple loop is faster than several numpy arrays
    prop_val = getattr(self, prop_name)
    for container in containers:
        if not container.is_selected:
            continue

        # skip setting group prop value if container isn't a group
        elif prop_name.find("group") == 0 and not container.is_group:
            continue
        # skip setting props for decorator group
        elif container.is_group and container.group_type == 'DECORATOR':
            continue

        setattr(container, prop_name, prop_val)

    bakemaster.allow_prop_in_multi_selection_update = True


def _generic_group_type_change_Update(self: PropertyGroup, context: Context,
                                      walk_data: str) -> None:
    """
    If group_type changed to Decorator, copy settings from group to all its
    childs. If changed to Dictator, copy settings from the first child.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - context the prop update was called from.

        walk_data - attribute name of Collection Property that
                has uilist walk features.
    """

    if self.group_old_type == self.group_type or not self.is_group:
        return
    self.group_old_type = self.group_type

    bakemaster = context.scene.bakemaster

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)

    kwargs = {}
    if hasattr(self, "bakejob_index"):
        kwargs["bakejob_index"] = self.bakejob_index
    if hasattr(self, "container_index"):
        kwargs["container_index"] = self.container_index
    data, containers, attr = walk_data_getter(kwargs)
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    exclude_copy = {
        "name": True,
        "index": True,
        "bakejob_index": True,
        "is_group": True,
        "is_expanded": True,
        "group_type": True,
        "group_is_texset": True,
        "group_color_tag": True,
        "lowpoly_index": True,
        "lowpoly_name": True,
        "is_cage": True,
        "is_decal": True
    }

    # changed to dictator
    if self.group_type == 'DICTATOR':
        if self.get_is_last(data, attr):
            return
        container = self.get_next_item(containers)
        if container.ui_indent_level <= self.ui_indent_level:
            return

        _ = bakemaster.wh_copy(container, containers, self.index, exclude_copy)
        return

    # changed to decorator
    forbid_copy_cache = {}

    for index in range(self.index + 1, getattr(data, "%s_len" % attr)):
        container = containers[index]

        if container.ui_indent_level <= self.ui_indent_level:
            break

        # skip copying to items that have their own dictator groups
        elif container.is_group and container.group_type == 'DICTATOR':
            forbid_copy_cache[str(index)] = True
            continue
        elif forbid_copy_cache.get(str(container.parent_group_index), False):
            forbid_copy_cache[str(index)] = True
            continue

        _ = bakemaster.wh_copy(self, containers, index, exclude_copy)

        if container.is_group and container.group_type == 'DECORATOR':
            container.use_bake = True

    # because group_type changed to Decorator and we don't need inactive ui
    self.use_bake = True
    # also reset group_color_tag to default white for Decorator Group
    self.group_color_tag = ""


def Global_bakejobs_active_index_Update(self, context):
    _generic_active_index_Update(self, context, "bakejobs")


def BakeJob_drop_name_Update(self, context):
    _generic_drop_name_Update(self, context, walk_data="bakejobs")


def BakeJob_containers_active_index_Update(self, context):
    _generic_active_index_Update(self, context, "containers")


def BakeJob_ticker_Update(self, context):
    _generic_ticker_Update(self, context, walk_data="bakejobs",
                           double_click_ot_idname="bakejob_rename")


def BakeJob_drag_empty_ticker_Update(self, context):
    _generic_drag_empty_ticker_Update(self, context, "bakejobs")


def BakeJob_lowpoly_ticker_Update(self, context):
    _generic_lowpoly_ticker_Update(self, context, "bakejobs")


def BakeJob_group_type_Update(self, context):
    _generic_group_type_change_Update(self, context, "bakejobs")


def Container_drop_name_Update(self, context):
    _generic_drop_name_Update(self, context, walk_data="containers")


def Container_subcontainers_active_index_Update(self, context):
    _generic_active_index_Update(self, context, "subcontainers")


def Container_ticker_Update(self, context):
    _generic_ticker_Update(self, context, walk_data="containers",
                           double_click_ot_idname="container_rename")


def Container_drag_empty_ticker_Update(self, context):
    _generic_drag_empty_ticker_Update(self, context, "containers")


def Container_lowpoly_ticker_Update(self, context):
    _generic_lowpoly_ticker_Update(self, context, "containers")


def Container_group_type_Update(self, context):
    _generic_group_type_change_Update(self, context, "containers")


def Subcontainer_ticker_Update(self, context):
    _generic_ticker_Update(self, context, walk_data="subcontainers")


def Subcontainer_drag_empty_ticker_Update(self, context):
    _generic_drag_empty_ticker_Update(self, context, "subcontainers")


def Subcontainer_lowpoly_ticker_Update(self, context):
    _generic_lowpoly_ticker_Update(self, context, "subcontainers")


def Subcontainer_group_type_Update(self, context):
    _generic_group_type_change_Update(self, context, "subcontainers")


# UI Props' Updates

def BakeJob_use_bake_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "bakejobs", "use_bake")


def BakeJob_type_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "bakejobs", "type")


def BakeJob_group_is_texset_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "bakejobs", "group_is_texset")


def Container_use_bake_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "containers", "use_bake")


def Container_group_is_texset_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "containers", "group_is_texset")


def Subcontainer_use_bake_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "subcontainers", "use_bake")


def Subcontainer_group_is_texset_Update(self, context):
    _generic_property_in_multi_selection_Update(
        self, context, "subcontainers", "group_is_texset")
