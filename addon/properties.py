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


class Item(PropertyGroup):
    name: StringProperty(
        default="Object")

    index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    use_bake: BoolProperty(
        name="Include/Exclude Item from bake",
        default=True)


class BakeJob(PropertyGroup):
    name: StringProperty(
        name="Bake Job",
        description="Double click to rename",
        default="Bake Job")

    drop_name: StringProperty(
        name="New Bake Job",
        description="Drop objects here to create a new Bake Job with them",
        default="New Bake Job...",
        update=bm_props_utils.BakeJob_drop_name_Update)

    drop_name_old: StringProperty(default="Bake Job")

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

    items: CollectionProperty(type=Item)

    items_active_index: IntProperty(
        name="Active item",
        description="Click to configure settings",
        default=0)

    items_len: IntProperty(default=0)

    # UIList Walk Handler Props

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    drag_ticker: BoolProperty(
        default=False,
        update=bm_props_utils.BakeJob_drag_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)


class BakeHistory(PropertyGroup):
    name: StringProperty(
        name="Name of this recent bake",
        description="Double click to rename",
        default="Bake")

    index: IntProperty(default=-1)

    time_stamp: StringProperty(
        name="yyyyyy:mmmmm:dddd:hhh:mm:s",
        default="")


class Global(PropertyGroup):
    # Bake Jobs Props

    bakejobs: CollectionProperty(type=BakeJob)

    bakejobs_active_index: IntProperty(
        name="Bake Job",
        description="Active Bake Job",
        default=-1)

    bakejobs_len: IntProperty(default=0)

    # UIList walk handler Props

    allow_drop_prompt: BoolProperty(default=False)

    is_drag_possible: BoolProperty(default=False)
    drag_from_index: IntProperty(default=-1)
    drag_to_index: IntProperty(default=-1)

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

    # UI Walker Props

    walker_is_running: BoolProperty(
        name="Drag & Drop interface is activated",
        default=False)

    # Addon Preferences Props

    prefs_use_show_help: BoolProperty(
        name="Show Help buttons",
        description="Allow help buttons in panels' headers",
        default=True)

    # Preview Collections - Custom Icons Props

    preview_collections = {
        "main": bm_props_utils.load_preview_collections(),
    }
