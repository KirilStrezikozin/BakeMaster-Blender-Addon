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

from numpy import (
    zeros as numpy_zeros,
    array as numpy_array,
)
from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    BoolProperty,
    EnumProperty,
)
from .utils import (
    properties as bm_props_utils,
)
from .labels import BM_LABELS_Props


# class F():


class BM_PropertyGroup_Helper(PropertyGroup):
    """
    BakeMaster PropertyGroup Helper class providing PropertyGroup utilities.

    If PropertyGroup has iterable data for UIList Walk Handler,
    add active_index_old property alongside active_index.
    """

    def get_seq(self, data, attr, dtype: type):
        """
        Get a numpy array of len count containing a sequence of attrs' values
        in data.
        """

        data_prop = getattr(self, data)
        seq = numpy_zeros(len(data_prop), dtype=dtype)
        data_prop.foreach_get(attr, seq)
        return seq

    def set_seq(self, data, attr, value):
        """
        Set each item's property of name attr to the given value
        (items are in iterable data property).
        """

        data_prop = getattr(self, data)
        seq = numpy_array([value] * len(data_prop))
        data_prop.foreach_set(attr, seq)


class Subcontainer(BM_PropertyGroup_Helper):
    name: StringProperty(
        default="Map")


class Container(BM_PropertyGroup_Helper):
    name: StringProperty(
        default="Object")

    drop_name: StringProperty(
        name="New Object",
        description="Drop objects here to put them into selected Bake Jobs",
        default="new Object...",
        update=bm_props_utils.Container_drop_name_Update)

    drop_name_old: StringProperty(default="new Object...")

    index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    use_bake: BoolProperty(
        name="Include/Exclude Container from bake",
        default=True)

    subcontainers: CollectionProperty(type=Subcontainer)

    subcontainers_active_index: IntProperty(
        name="Active item",
        description="Click to configure settings",
        default=-1,
        update=bm_props_utils.Container_subcontainers_active_index_Update)

    subcontainers_active_index_old: IntProperty(default=-1)

    subcontainers_len: IntProperty(default=0)

    # UIList Walk Handler Props

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    ticker: BoolProperty(
        name="Item",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=bm_props_utils.Container_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)

    is_selected: BoolProperty(default=True)


class BakeJob(BM_PropertyGroup_Helper):
    name: StringProperty(
        name="Bake Job",
        description="Double click to rename",
        default="Bake Job")

    drop_name: StringProperty(
        name="New Bake Job",
        description="Drop objects here to create a new Bake Job with them",
        default="new Bake Job...",
        update=bm_props_utils.BakeJob_drop_name_Update)

    drop_name_old: StringProperty(default="new Bake Job...")

    index: IntProperty(default=-1)

    type: EnumProperty(
        name="Bake Job Type",
        description="Choose a Bake Job type. Hover over type values to see descriptions",  # noqa: E501
        default='OBJECTS',
        items=[('OBJECTS', "Objects", "Bake Job will contain Objects, where each of them will contain Maps to bake"),  # noqa: E501
               ('MAPS', "Maps", "Bake Job will contain Maps, where each of them will contain Objects the map should be baked for")])  # noqa: E501

    use_bake: BoolProperty(
        name="Include/Exclude Bake Job from bake",
        default=True)

    containers: CollectionProperty(type=Container)

    containers_active_index: IntProperty(
        name="Active item",
        description="Click to configure settings",
        default=-1,
        update=bm_props_utils.BakeJob_containers_active_index_Update)

    containers_active_index_old: IntProperty(default=-1)

    containers_len: IntProperty(default=0)

    # UIList Walk Handler Props

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    ticker: BoolProperty(
        name="Bake Job",
        description="Double click to rename.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=bm_props_utils.BakeJob_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)

    is_selected: BoolProperty(default=True)


class BakeHistory(BM_PropertyGroup_Helper):
    name: StringProperty(
        name="Name of this recent bake",
        description="Double click to rename",
        default="Bake")

    index: IntProperty(default=-1)

    time_stamp: StringProperty(
        name="yyyyyy:mmmmm:dddd:hhh:mm:s",
        default="")


class Global(BM_PropertyGroup_Helper):
    # Bake Jobs Props

    bakejobs: CollectionProperty(type=BakeJob)

    bakejobs_active_index: IntProperty(
        name="Bake Job",
        description="Active Bake Job",
        default=-1,
        update=bm_props_utils.Global_bakejobs_active_index_Update)

    bakejobs_active_index_old: IntProperty(default=-1)

    bakejobs_len: IntProperty(default=0)

    # UIList Walk Handler Props

    walk_data_name: StringProperty(
        default="",
        options={'SKIP_SAVE'})

    allow_drop: BoolProperty(default=False, options={'SKIP_SAVE'})

    allow_drag: BoolProperty(default=False, options={'SKIP_SAVE'})
    drag_from_index: IntProperty(default=-1, options={'SKIP_SAVE'})
    drag_to_index: IntProperty(default=-1, options={'SKIP_SAVE'})
    drag_data_from: StringProperty(default="", options={'SKIP_SAVE'})
    drag_data_to: StringProperty(default="", options={'SKIP_SAVE'})
    allow_drag_trans: BoolProperty(default=False, options={'SKIP_SAVE'})
    drag_from_ticker: BoolProperty(default=False, options={'SKIP_SAVE'})

    allow_multi_select: BoolProperty(default=False, options={'SKIP_SAVE'})
    multi_select_event: StringProperty(default="", options={'SKIP_SAVE'})
    is_multi_selection_empty: BoolProperty(default=True, options={'SKIP_SAVE'})
    multi_selection_data: StringProperty(default="", options={'SKIP_SAVE'})

    is_double_click: BoolProperty(default=False, options={'SKIP_SAVE'})
    last_left_click_ticker: BoolProperty(default=False, options={'SKIP_SAVE'})

    # Bake Props

    bake_wait_user: BoolProperty(
        name="Prompt before freeze",
        description="While baking, when a hard operation is about to be executed and freeze the interface, a prompt will appear and wait for your response to continue. Suitable when running bakes parallel to other processes, providing a secure control.\n\nInterface freezes are expected when preparing maps for meshes with huge amount of geometry, baking map result to modifiers, denoising or channel packing baked result, or UV unwrapping and packing",  # noqa: E501
        default=False)

    bake_hold_on_pause: BoolProperty(default=False)

    bake_trigger_stop: BoolProperty(default=False)

    bake_trigger_cancel: BoolProperty(default=False)

    bake_is_running: BoolProperty(default=False)

    short_bake_instruction: StringProperty(
        name="Short Bake Instruction",
        description=BM_LABELS_Props("Global", "short_bake_instruction", "description").get(),  # noqa: E501
        default="Short Bake Instruction",
        options={'SKIP_SAVE'})

    # BakeHistory Props

    bakehistory: CollectionProperty(type=BakeHistory)

    bakehistory_active_index: IntProperty(
        name="Bake History of recent bakes",
        default=-1)

    bakehistory_len: IntProperty(default=0)

    bakehistory_reserved_index: IntProperty(default=-1)

    # Configuration Props

    config_is_attached: BoolProperty(default=False)

    config_filepath: StringProperty(
        name="Filepath",
        description="Where to Save/Load a config from. // is relative to this .blend file",  # noqa: E501
        default="")

    presets_filepath: StringProperty(
        name="Presets Filepath",
        description="Choose a folder on the disk containing Presets for BakeMaster (leave empty for default path). // is relative to this .blend file",  # noqa: E501
        default="")

    # Addon Preferences Props

    prefs_use_show_help: BoolProperty(
        name="Show Help buttons",
        description="Allow help buttons in panels' headers",
        default=True)

    # Preview Collections - Custom Icons Props

    preview_collections = {
        "main": bm_props_utils.load_preview_collections(),
    }
