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

from os import (
    path as os_path,
    listdir as os_listdir,
)
from bpy import ops as bpy_ops
import bpy.utils.previews as bpy_utils_previews
from . import get as bm_get

_ui_pcoll_open = {}


def load_preview_collections():
    """
    Load custom icons into preview_collections.
    """

    icons_dir = os_path.join(os_path.dirname(os_path.dirname(__file__)),
                             "icons")

    if not os_path.exists(icons_dir):
        print("BakeMaster: Internal warning: custom icons weren't found")
        return None

    # To avoid ResourceWarning on loading previously initialized instance
    pcoll = _ui_pcoll_open.get("main")
    if pcoll is not None:
        return pcoll

    pcoll = bpy_utils_previews.new()
    _ui_pcoll_open["main"] = pcoll

    for filename in os_listdir(icons_dir):
        filepath = os_path.join(icons_dir, filename)
        pcoll.load(filename, filepath, 'IMAGE')

    return pcoll


def Generic_ticker_Update(self, context: not None, walk_data: str,
                          double_click_ot_idname=""):
    """
    Generic ticker property update.

    walk_data is an attribute name of Collection Property that has uilist walk
    features.

    double_click_ot is a bl_idname of an operator that will be called on
    double click event caught.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    walk_data_getter = getattr(bm_get, "walk_data_get_%s" % walk_data)
    data, containers, attr = walk_data_getter(bakemaster)
    if data is None:
        print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")
        return

    if all([bakemaster.is_double_click,
            bakemaster.last_left_click_ticker != self.ticker,
            self.index == getattr(data, "%s_active_index" % attr),
            not self.is_drag_empty, not self.has_drop_prompt,
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
        Generic_multi_select(self, bakemaster, walk_data)
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
        return

    # Skip when dragging to other datas
    if any([all([not bakemaster.allow_drag_trans,
                 walk_data != bakemaster.drag_data_from]),
            all([bakemaster.allow_drag_trans,
                 bm_get.walk_data_child(walk_data) != bakemaster.drag_data_from
                 ])]):
        return

    # Skip trans drag to the container the containers were dragged from
    # if all([bm_get.walk_data_child(walk_data) == bakemaster.drag_data_from,
    #         self.index == getattr(data, "%s_active_index" % attr)]):
    #     return

    if bakemaster.drag_to_index != -1:
        containers[bakemaster.drag_to_index].is_drag_placeholder = False
    self.is_drag_placeholder = True
    bakemaster.drag_to_index = self.index
    bakemaster.drag_data_to = walk_data

    ticker_old = bakemaster.drag_from_ticker
    if self.ticker == ticker_old:
        self.ticker = not ticker_old


def Generic_active_index_Update(self, context: not None, walk_data: str):
    """
    Generic active_index property update.
    Revert to active_index_old when setting onto drag_emtpy and drop_prompt
    containers.

    walk_data is an attribute name of Collection Property that has uilist walk
    features.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    walk_data_getter = getattr(bm_get, "walk_data_get_%s" % walk_data)
    data, containers, attr = walk_data_getter(bakemaster)
    if data is None:
        print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")
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
    if any([containers[active_index].is_drag_empty,
            containers[active_index].has_drop_prompt]):
        setattr(data, "%s_active_index" % attr,
                getattr(data, "%s_active_index_old" % attr))
        return

    setattr(data, "%s_active_index_old" % attr, active_index)

    has_selection, _ = bm_get.walk_data_multi_selection_data(
        bakemaster, walk_data)
    if has_selection:
        containers[active_index].is_selected = True


def Generic_drop_name_Update(self, context: not None, walk_data: str,
                             adddropped_ot_idname: str):
    """
    Generic drop_name property update.

    walk_data is an attribute name of Collection Property that has uilist walk
    features.

    adddropped_ot_idname is a bl_idname of an operator that will be called on
    drop.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    if self.drop_name_old == self.drop_name:
        return

    self.drop_name_old = self.drop_name
    adddropped_ot = getattr(bpy_ops.bakemaster, adddropped_ot_idname)
    adddropped_ot('INVOKE_DEFAULT', index=self.index, drop_name=self.drop_name)


def Generic_multi_select(self, bakemaster, walk_data: str):
    """
    Generic multiple selection manifestor.

    walk_data is an attribute name of Collection Property that has uilist walk
    features.

    If called in drag_end() to clear selection, self is None.
    """

    walk_data_getter = getattr(bm_get, "walk_data_get_%s" % walk_data)
    data, containers, attr = walk_data_getter(bakemaster)
    if data is None:
        print(f"BakeMaster Internal Error: cannot resolve walk data at {self}")
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


def Generic_property_in_multi_selection_Update(self, context, walk_data: str,
                                               prop_name: str):
    """
    Generic property in multi selection update function. Lets set prop_name's
    property values in data's containers that are in multi selection.

    walk_data is an attribute name of Collection Property that has uilist walk
    features.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data

    if not bakemaster.allow_prop_in_multi_selection_update:
        return

    has_selection, _ = bm_get.walk_data_multi_selection_data(
        bakemaster, walk_data)
    if not has_selection:
        return

    # no recursive updates
    bakemaster.allow_prop_in_multi_selection_update = False

    walk_data_getter = getattr(bm_get, "walk_data_get_%s" % walk_data)
    _, containers, _ = walk_data_getter(bakemaster)

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
        setattr(container, prop_name, prop_val)

    bakemaster.allow_prop_in_multi_selection_update = True


def Global_bakejobs_active_index_Update(self, context):
    Generic_active_index_Update(self, context, "bakejobs")


def BakeJob_drop_name_Update(self, context):
    Generic_drop_name_Update(self, context, walk_data="bakejobs",
                             adddropped_ot_idname="bakejobs_adddropped")


def BakeJob_containers_active_index_Update(self, context):
    Generic_active_index_Update(self, context, "containers")


def BakeJob_ticker_Update(self, context):
    Generic_ticker_Update(self, context, walk_data="bakejobs",
                          double_click_ot_idname="bakejob_rename")


def Container_drop_name_Update(self, context):
    Generic_drop_name_Update(self, context, walk_data="containers",
                             adddropped_ot_idname="containers_adddropped")


def Container_subcontainers_active_index_Update(self, context):
    Generic_active_index_Update(self, context, "subcontainers")


def Container_ticker_Update(self, context):
    Generic_ticker_Update(self, context, walk_data="containers",
                          double_click_ot_idname="container_rename")

# UI Props' Updates


def BakeJob_use_bake_Update(self, context):
    Generic_property_in_multi_selection_Update(
        self, context, "bakejobs", "use_bake")


def BakeJob_type_Update(self, context):
    Generic_property_in_multi_selection_Update(
        self, context, "bakejobs", "type")


def Container_use_bake_Update(self, context):
    Generic_property_in_multi_selection_Update(
        self, context, "containers", "use_bake")
