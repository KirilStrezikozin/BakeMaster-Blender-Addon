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

__all__ = ["Subcontainer", "Container", "BakeJob", "Global"]

import typing

from os import (
    path as os_path,
    listdir as os_listdir,
)

import bpy.utils.previews

from bpy.types import (
    Context,
    Object,
    PropertyGroup,
    bpy_prop_collection as Collection,
)
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    BoolProperty,
    EnumProperty,
)

from numpy import (
    ndarray as numpy_ndarray,
    zeros as numpy_zeros,
    array as numpy_array,
)

from . import prop_updates


# class F():


_ui_pcoll_open = {}

_walk_data_literal = {
    "bakejobs": True,
    "containers": True,
    "subcontainers": True,
}


def _check_walk_data_safety(data_name: str) -> None:

    if _walk_data_literal.get(data_name, False):
        return
    raise NameError(f"BakeMaster: Internal Error: {data_name} walk_data name does not meet the literal criteria")  # noqa: E501


def _load_preview_collections() -> bpy.utils.previews.ImagePreviewCollection:
    """
    Load custom icons into bakemaster.__preview_collections.
    """

    icons_dir = os_path.join(
            os_path.dirname(os_path.dirname(__file__)),
            "icons")

    if not os_path.exists(icons_dir):
        print("BakeMaster: Internal Warning: custom icons weren't found")
        return dict()

    # To avoid ResourceWarning on loading previously initialized instance
    pcoll = _ui_pcoll_open.get("main")
    if pcoll is not None:
        return pcoll

    pcoll = bpy.utils.previews.new()
    _ui_pcoll_open["main"] = pcoll

    for filename in os_listdir(icons_dir):
        filepath = os_path.join(icons_dir, filename)
        pcoll.load(filename, filepath, 'IMAGE')

    return pcoll


class BM_PropertyGroup_Helper(PropertyGroup):
    """
    BakeMaster PropertyGroup Helper class providing PropertyGroup utilities.
    """

    def get_seq(self, data: PropertyGroup, attr: str, dtype: type
                ) -> numpy_ndarray:
        """
        Get a numpy array of len count containing a sequence of attrs' values
        in data.
        """

        data_prop = getattr(self, data)
        seq = numpy_zeros(len(data_prop), dtype=dtype)
        data_prop.foreach_get(attr, seq)
        return seq

    def set_seq(self, data: PropertyGroup, attr: str, value: typing.Any
                ) -> None:
        """
        Set each item's property of name attr to the given value.
        """

        data_prop = getattr(self, data)
        seq = numpy_array([value] * len(data_prop))
        data_prop.foreach_set(attr, seq)

    def get_bm_name(self, bakemaster: PropertyGroup, data_name: str) -> str:
        """
        Get bm_name representing the UI name of the iterable walk_data
        of data_name.
        """

        _check_walk_data_safety(data_name)

        if data_name == "bakejobs":
            return "bakejobs"

        if hasattr(self, "bakejob_index"):
            bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        else:
            bakejob = bakemaster.get_bakejob(bakemaster, self.index)
        if bakejob is None:
            return "none"

        if data_name == "containers":
            return bakejob.type.lower()

        elif data_name == "subcontainers":
            if bakejob.type == 'OBJECTS':
                return "maps"
            else:
                return "objects"

    def resolve_mutual_group(self, containers: Collection, index_1: int,
                             index_2: int) -> typing.Tuple[int, int]:
        """
        Get index and ui_indent_level of a group that contains both
        containers of index_1, index_2.

        Call on data is preferred but isn't mandatory since self is unused here
        Example: mg = data.resolve_mutual_group(...).
        """

        while True:
            c1 = containers[index_1]
            c2 = containers[index_2]

            if c1.index == c2.index:
                return c1.index, c1.ui_indent_level

            elif c1.parent_group_index == -1 or c2.parent_group_index == -1:
                return -1, 0

            if index_1 > index_2:
                index_1 = c1.parent_group_index
            elif index_2 > index_1:
                index_2 = c2.parent_group_index

    def resolve_top_group(self, containers: Collection,
                          container: PropertyGroup = None) -> PropertyGroup:

        if container is None:
            return self.resolve_top_group(self, containers, self)

        if not hasattr(container, "parent_group_index"):
            return container

        if container.parent_group_index == -1:
            return container
        try:
            group = containers[container.parent_group_index]
        except IndexError:
            return container
        else:
            self.resolve_top_group(containers, group)

    def get_parent_group(
            self, containers: Collection,
            stop_at_prop_name: str, stop_at_prop_value: typing.Any,
            return_at_prop_name: str, return_at_prop_value: typing.Any
            ) -> typing.Tuple[typing.Optional[PropertyGroup], bool]:
        """
        Get container's parent group.

        Returned container has attribute of stop_at_prop_name equal
        to stop_at_prop_value.

        Climb up until condition above is met and parent's attribute
        of return_at_prop_name equals return_at_prop_value.

        The second return value defines whether the last condition was met.
        """

        container = self

        explicit_none = False
        if container.is_group and container.group_type == 'DICTATOR':
            explicit_none = True

        if container.parent_group_index == -1:
            return None, False

        s_parent = None  # parent to get settings from

        while True:
            if container.parent_group_index != -1 and not container.is_group:
                container = containers[container.parent_group_index]

            if s_parent is None and getattr(
                    container, stop_at_prop_name) == stop_at_prop_value:
                s_parent = container

            if s_parent is not None and all(
                    [getattr(container,
                             return_at_prop_name) == return_at_prop_value,
                     getattr(container,
                             stop_at_prop_name) == stop_at_prop_value]):
                if explicit_none:
                    return None, True
                return s_parent, True

            if container.parent_group_index == -1:
                if explicit_none:
                    return None, False
                return s_parent, False

            container = containers[container.parent_group_index]

    def group_has_childs(self, data: PropertyGroup, containers: Collection,
                         data_name: str) -> bool:
        """
        Return True if group has childs or self is not group.
        """

        _check_walk_data_safety(data_name)

        if not self.is_group:
            return True

        if self.get_is_last(data, data_name):
            return False
        elif self.get_next_item(containers).parent_group_index != self.index:
            return False
        else:
            return True

    def get_group_icon(self, bakemaster: PropertyGroup, all=False
                       ) -> typing.Union[int, list]:

        if self.group_type == 'DECORATOR':
            return bakemaster.get_icon('COLLECTION')

        color_tags = ["", "_color_01", "_color_02", "_color_03", "_color_04",
                      "_color_05", "_color_06", "_color_07", "_color_08"]

        icon_raw = r'COLLECTION%s'

        if not all:
            return bakemaster.get_icon(icon_raw % self.group_color_tag)

        icons_all = []
        for color_tag in color_tags:
            icons_all.append([
                color_tag,
                bakemaster.get_icon(icon_raw % color_tag)])
        return icons_all

    def get_is_last(self, data: PropertyGroup, data_name: str,
                    index: typing.Optional[int] = -1) -> bool:
        """
        Return True if self is the last item in data_name Collection.
        Compare index if given.
        """

        _check_walk_data_safety(data_name)

        last_index = getattr(data, "%s_len" % data_name) - 1
        index = self.index if index == -1 else index

        if last_index == index:
            return True
        elif last_index <= index:
            print(f"BakeMaster: Internal Warning: {self} index {index} exceeds last possible index {last_index}")  # noqa: E501
            # bakemaster.log("mbx0004", last_index, index)

    def get_next_item(self, containers: Collection, step=1) -> PropertyGroup:
        """
        Get next item in containers. If self is last, return first
        in containers.
        Next item index will be self.index + step.
        """

        try:
            return containers[self.index + step]
        except IndexError:
            return containers[0]

    def get_is_object(self, bakemaster: PropertyGroup, data_name: str) -> bool:
        """
        Return True if self is an Object.
        """

        _check_walk_data_safety(data_name)

        return self.get_bm_name(
            bakemaster, data_name) == "objects" and not self.is_group

    def get_is_lowpoly(self) -> bool:
        """
        Return True if self is lowpoly.
        """

        return not self.is_group and self.lowpoly_index == -1

    def get_is_highpoly(self) -> bool:
        """
        Return True if self is highpoly.
        """

        return self.lowpoly_index != -1 and not any(
            [self.is_cage, self.is_decal])

    def get_is_cage(self) -> bool:
        """
        Return True if self is cage.
        """

        return self.lowpoly_index != -1 and self.is_cage

    def get_is_decal(self) -> bool:
        """
        Return True if self is decal.
        """

        return self.lowpoly_index != -1 and self.is_decal

    def make_lowpoly(self) -> None:
        """
        Make container a lowpoly.
        """

        self.lowpoly_index = -1
        self.is_group = False

    def make_highpoly(self, lowpoly_index: int) -> None:
        """
        Make container a highpoly for lowpoly of given lowpoly_index.
        """

        self.lowpoly_index = lowpoly_index
        self.is_cage = False
        self.is_decal = False
        self.is_group = False

    def make_cage(self, lowpoly_index: int) -> None:
        """
        Make container a cage for lowpoly of given lowpoly_index.
        """

        self.lowpoly_index = lowpoly_index
        self.is_cage = True
        self.is_decal = False
        self.is_group = False

    def make_decal(self, lowpoly_index: int) -> None:
        """
        Make container a decal for lowpoly of given lowpoly_index.
        """

        self.lowpoly_index = lowpoly_index
        self.is_cage = False
        self.is_decal = True
        self.is_group = False

    def get_lowpoly(self, containers: Collection) -> PropertyGroup:
        """
        Get self's lowpoly. Return self if no lowpoly assigned.
        """

        if self.lowpoly_index == -1:
            return self
        else:
            return containers[self.lowpoly_index]

    def __generic_get(self, data: PropertyGroup, containers: Collection,
                      data_name: str, index: int, type: str
                      ) -> typing.Union[PropertyGroup, None]:
        """
        Pseudo-private method. Call get_highpoly(...), get_cage(...),
        get_decal(...) instead.

        Receives type in {"highpoly", "cage", "decal"}.
        """

        _check_walk_data_safety(data_name)

        if not self.get_is_lowpoly():
            return None

        elif index < 0:
            return None

        elif self.get_is_last(data, data_name):
            return None

        elif self.get_next_item(containers).lowpoly_index != self.index:
            return None

        count = 0
        container = self.get_next_item(containers)

        while count != index:
            count += 1

            if self.get_is_last(data, data_name, self.index + 1 + count):
                return None

            elif not getattr(self.get_next_item(containers, 1 + count),
                             "get_is_%s" % type)():
                continue

            container = self.get_next_item(containers, 1 + count)
            if container.lowpoly_index != self.index:
                return None

        else:
            return container

    def get_highpoly(self, data: PropertyGroup, containers: Collection,
                     data_name: str, index: int
                     ) -> typing.Union[PropertyGroup, None]:
        """
        Get container's highpoly of given index.
        Returns None if invalid.
        """

        return self.__generic_get(data, containers, data_name, index,
                                  "highpoly")

    def get_cage(self, data: PropertyGroup, containers: Collection,
                 data_name: str, index: int
                 ) -> typing.Union[PropertyGroup, None]:
        """
        Get container's cage of given index.
        Returns None if invalid.
        """

        return self.__generic_get(data, containers, data_name, index,
                                  "cage")

    def get_decal(self, data: PropertyGroup, containers: Collection,
                  data_name: str, index: int
                  ) -> typing.Union[PropertyGroup, None]:
        """
        Get container's decal of given index.
        Returns None if invalid.
        """

        return self.__generic_get(data, containers, data_name, index,
                                  "decal")

    def __generic_index_in(self, data: PropertyGroup, containers: Collection,
                           data_name: str, type: str) -> int:
        """
        Pseudo-private method. Call index_in_highpolies(...),
        index_in_cages(...), index_in_decals(...) instead.

        Receives type in {"highpoly", "cage", "decal"}.
        """

        _check_walk_data_safety(data_name)

        if not getattr(self, "get_is_%s" % type)():
            return -1

        lowpoly = self.get_lowpoly(containers)
        first_hcd = getattr(lowpoly, "get_%s" % type)(
                data, containers, data_name, 0)
        if first_hcd is None:
            return -1

        return self.index - first_hcd.index

    def index_in_highpolies(self, data: PropertyGroup, containers: Collection,
                            data_name: str) -> int:

        return self.__generic_index_in(data, containers, data_name,
                                       type="highpoly")

    def index_in_cages(self, data: PropertyGroup, containers: Collection,
                       data_name: str) -> int:

        return self.__generic_index_in(data, containers, data_name,
                                       type="cages")

    def index_in_decals(self, data: PropertyGroup, containers: Collection,
                        data_name: str) -> int:

        return self.__generic_index_in(data, containers, data_name,
                                       type="decals")


class Subcontainer(BM_PropertyGroup_Helper):
    name: StringProperty(
        default="Map")

    index: IntProperty(default=-1)
    container_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    is_group: BoolProperty(default=False)
    parent_group_index: IntProperty(default=-1)
    ui_indent_level: IntProperty(default=0)

    is_expanded: BoolProperty(
        name="Expand/Collapse",
        default=True)

    group_color_tag: StringProperty(default="")

    group_old_type: StringProperty(default="DICTATOR")
    group_type: EnumProperty(
        name="Group Type",
        description="Choose Group Type. Hover over values to see descriptions",
        default='DICTATOR',
        items=[('DICTATOR', "Dictator", "Group will dictate all settigs to its childs"),  # noqa: E501
               ('DECORATOR', "Decorator", "Make the Group for beauty only, it won't dictate any settings")],  # noqa: E501
        update=prop_updates.Subcontainer_group_type_Update)

    lowpoly_index: IntProperty(default=-1)
    lowpoly_name: StringProperty(default="")
    is_cage: BoolProperty(default=False)
    is_decal: BoolProperty(default=False)

    # UI Props
    group_is_texset: BoolProperty(
        name="Texture Set",
        description="Make this Group a Texture Set where all child objects will share the same image for each map",  # noqa: E501
        default=False,
        update=prop_updates.Subcontainer_group_is_texset_Update)

    use_bake: BoolProperty(
        name="Include/Exclude Item from bake",
        default=True,
        update=prop_updates.Subcontainer_use_bake_Update)

    ###

    # WalkHandler Props

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    ticker: BoolProperty(
        name="Item",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.Subcontainer_ticker_Update)

    drag_empty_ticker: BoolProperty(
        name="Item",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.Subcontainer_drag_empty_ticker_Update)

    lowpoly_ticker: BoolProperty(
        name="Add data...",
        description="Drag over and release to add Highpoly, Cage, or Decal for this Object",  # noqa: E501
        default=False,
        update=prop_updates.Subcontainer_lowpoly_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)
    is_drag_empty_placeholder: BoolProperty(default=False)
    is_lowpoly_placeholder: BoolProperty(default=False)

    is_selected: BoolProperty(default=True)

    ###


class Container(BM_PropertyGroup_Helper):
    name: StringProperty(
        default="Object")

    index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    is_group: BoolProperty(default=False)
    parent_group_index: IntProperty(default=-1)
    ui_indent_level: IntProperty(default=0)

    is_expanded: BoolProperty(
        name="Expand/Collapse",
        default=True)

    group_color_tag: StringProperty(default="")

    group_old_type: StringProperty(default="DICTATOR")
    group_type: EnumProperty(
        name="Group Type",
        description="Choose Group Type. Hover over values to see descriptions",
        default='DICTATOR',
        items=[('DICTATOR', "Dictator", "Group will dictate all settigs to its childs"),  # noqa: E501
               ('DECORATOR', "Decorator", "Make the Group for beauty only, it won't dictate any settings")],  # noqa: E501
        update=prop_updates.Container_group_type_Update)

    lowpoly_index: IntProperty(default=-1)
    lowpoly_name: StringProperty(default="")
    is_cage: BoolProperty(default=False)
    is_decal: BoolProperty(default=False)

    # UI Props
    group_is_texset: BoolProperty(
        name="Texture Set",
        description="Make this Group a Texture Set where all child objects will share the same image for each map",  # noqa: E501
        default=False,
        update=prop_updates.Container_group_is_texset_Update)

    use_bake: BoolProperty(
        name="Include/Exclude Item from bake",
        default=True,
        update=prop_updates.Container_use_bake_Update)

    ###

    subcontainers: CollectionProperty(type=Subcontainer)

    subcontainers_active_index: IntProperty(
        name="Active item",
        description="Click to configure settings",
        default=-1,
        update=prop_updates.Container_subcontainers_active_index_Update)

    subcontainers_active_index_old: IntProperty(default=-1)

    subcontainers_len: IntProperty(default=0)

    # WalkHandler Props

    drop_name: StringProperty(
        name="New Object",
        description="Drop objects here to put them into selected Bake Jobs",
        default="new Object...",
        update=prop_updates.Container_drop_name_Update)

    drop_name_old: StringProperty(default="new Object...")

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    ticker: BoolProperty(
        name="Item",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.Container_ticker_Update)

    drag_empty_ticker: BoolProperty(
        name="Item",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.Container_drag_empty_ticker_Update)

    lowpoly_ticker: BoolProperty(
        name="Add data...",
        description="Drag over and release to add Highpoly, Cage, or Decal for this Object",  # noqa: E501
        default=False,
        update=prop_updates.Container_lowpoly_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)
    is_drag_empty_placeholder: BoolProperty(default=False)
    is_lowpoly_placeholder: BoolProperty(default=False)

    is_selected: BoolProperty(default=True)

    ###


class BakeJob(BM_PropertyGroup_Helper):
    name: StringProperty(
        name="Bake Job",
        description="Double click to rename",
        default="Bake Job")

    index: IntProperty(default=-1)

    is_group: BoolProperty(default=False)
    parent_group_index: IntProperty(default=-1)
    ui_indent_level: IntProperty(default=0)

    is_expanded: BoolProperty(
        name="Expand/Collapse",
        default=True)

    group_color_tag: StringProperty(default="")

    group_old_type: StringProperty(default="DICTATOR")
    group_type: EnumProperty(
        name="Group Type",
        description="Choose Group Type. Hover over values to see descriptions",
        default='DICTATOR',
        items=[('DICTATOR', "Dictator", "Group will dictate all settigs to its childs"),  # noqa: E501
               ('DECORATOR', "Decorator", "Make the Group for beauty only, it won't dictate any settings")],  # noqa: E501
        update=prop_updates.BakeJob_group_type_Update)

    lowpoly_index: IntProperty(default=-1)
    lowpoly_name: StringProperty(default="")
    is_cage: BoolProperty(default=False)
    is_decal: BoolProperty(default=False)

    # UI Props
    group_is_texset: BoolProperty(
        name="Texture Set",
        description="Make this Group a Texture Set where all child objects will share the same image for each map",  # noqa: E501
        default=False,
        update=prop_updates.BakeJob_group_is_texset_Update)

    type: EnumProperty(
        name="Bake Job Type",
        description="Choose a Bake Job type. Hover over type values to see descriptions",  # noqa: E501
        default='OBJECTS',
        items=[('OBJECTS', "Objects", "Bake Job will contain Objects, where each of them will contain Maps to bake"),  # noqa: E501
               ('MAPS', "Maps", "Bake Job will contain Maps, where each of them will contain Objects the map should be baked for")],  # noqa: E501
        update=prop_updates.BakeJob_type_Update)

    use_bake: BoolProperty(
        name="Include/Exclude Bake Job from bake",
        default=True,
        update=prop_updates.BakeJob_use_bake_Update)

    ###

    containers: CollectionProperty(type=Container)

    containers_active_index: IntProperty(
        name="Active item",
        description="Click to configure settings",
        default=-1,
        update=prop_updates.BakeJob_containers_active_index_Update)

    containers_active_index_old: IntProperty(default=-1)

    containers_len: IntProperty(default=0)

    # WalkHandler Props

    drop_name: StringProperty(
        name="New Bake Job",
        description="Drop objects here to create a new Bake Job with them",
        default="new Bake Job...",
        update=prop_updates.BakeJob_drop_name_Update)

    drop_name_old: StringProperty(default="new Bake Job...")

    has_drop_prompt: BoolProperty(default=False)
    has_drag_prompt: BoolProperty(default=False)

    ticker: BoolProperty(
        name="Bake Job",
        description="Double click to rename.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.BakeJob_ticker_Update)

    drag_empty_ticker: BoolProperty(
        name="Bake Job",
        description="Double click to change.\nPress and drag to move.\nUse Shift, Ctrl to select multiple",  # noqa: E501
        default=False,
        update=prop_updates.BakeJob_drag_empty_ticker_Update)

    lowpoly_ticker: BoolProperty(
        name="Add data...",
        description="Drag over and release to add Highpoly, Cage, or Decal for this Object",  # noqa: E501
        default=False,
        update=prop_updates.BakeJob_lowpoly_ticker_Update)

    is_drag_empty: BoolProperty(default=False)
    is_drag_placeholder: BoolProperty(default=False)
    is_drag_empty_placeholder: BoolProperty(default=False)
    is_lowpoly_placeholder: BoolProperty(default=False)

    is_selected: BoolProperty(default=True)

    ###


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
    # BakeJobs Props

    bakejobs: CollectionProperty(type=BakeJob)

    bakejobs_active_index: IntProperty(
        name="Bake Job",
        description="Active Bake Job",
        default=-1,
        update=prop_updates.Global_bakejobs_active_index_Update)

    bakejobs_active_index_old: IntProperty(default=-1)

    bakejobs_len: IntProperty(default=0)

    # WalkHandler Props

    walk_data_name: StringProperty(
        default="",
        options={'SKIP_SAVE'})

    allow_drop: BoolProperty(default=False, options={'SKIP_SAVE'})

    allow_drag: BoolProperty(default=False, options={'SKIP_SAVE'})
    drag_from_index: IntProperty(default=-1, options={'SKIP_SAVE'})
    drag_to_index: IntProperty(default=-1, options={'SKIP_SAVE'})
    drag_to_index_temp: IntProperty(default=-1, options={'SKIP_SAVE'})
    drag_data_from: StringProperty(default="", options={'SKIP_SAVE'})
    drag_data_to: StringProperty(default="", options={'SKIP_SAVE'})
    allow_drag_trans: BoolProperty(default=False, options={'SKIP_SAVE'})
    drag_from_ticker: BoolProperty(default=False, options={'SKIP_SAVE'})
    allow_multi_selection_drag: BoolProperty(
        default=False, options={'SKIP_SAVE'})
    is_drag_lowpoly_data: BoolProperty(default=False, options={'SKIP_SAVE'})

    allow_multi_select: BoolProperty(default=False, options={'SKIP_SAVE'})
    multi_select_event: StringProperty(default="", options={'SKIP_SAVE'})
    is_multi_selection_empty: BoolProperty(default=True, options={'SKIP_SAVE'})
    multi_selection_data: StringProperty(default="", options={'SKIP_SAVE'})
    allow_prop_in_multi_selection_update: BoolProperty(
        default=True, options={'SKIP_SAVE'})

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
        description="Press `ESC` key to cancel baking current map iteration.\n\nOpen Blender Console to see more information about the baking process and, if you face an unexpected Blender freeze, be able to press `Ctrl + C` (Windows), `Cmd + C` (Mac), `Super + C` (Linux) to abort the bake. Enable Prompt before freeze for more control",  # noqa: E501
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

    # Preview Collections - Custom Icons Props

    __preview_collections = {
        "main": _load_preview_collections(),
    }

    # Helper Funcs

    def __get_package_name(self) -> str:

        return __package__.split(".")[0]

    def log(self, log_id: str, *args) -> None:

        log_ids = {
            "mbx0001": r"BakeMaster: Internal Warning: file %s with %s icon isn't loaded",  # noqa: E501
            "mbx0002": r"BakeMaster: Internal Warning: no icons loaded to close",  # noqa: E501
            "mbx0003": r"BakeMaster: Internal Warning: %s while setting %s attribute for %s",  # noqa: E501
            "mbx0004": r"BakeMaster: Internal Warning: %s index %s exceeds last possible index %s",  # noqa: E501
            "pux0000": r"BakeMaster: Internal Error: cannot resolve %s walk data at %s",  # noqa: E501
            "o0x0000": r"BakeMaster: Internal Error: cannot resolve %s walk data at %s",  # noqa: E501
            "o0x0001": r"BakeMaster: Internal Error: not enough data at %s",
            "o0x0002": r"BakeMaster: Internal warning: cannot resolve container at %s",  # noqa: E501
        }

        try:
            message = log_ids[log_id]
        except KeyError:
            print(f"BakeMaster: Internal Error: invalid {log_id} log id")
            return

        if len(args):
            print(message % tuple([str(arg) for arg in args]))
        else:
            if message.count(r"%s") > 0:
                print(f"BakeMaster: Internal Warning: {log_id} log id didn't receive anough arguments")  # noqa: E501
            print(message)

    def get_icon(self, icon_id: str, reg=False
                 ) -> typing.Union[int, typing.Dict]:

        if reg:
            return self.__preview_collections

        icon_name = "bakemaster_%s.png" % icon_id.lower()
        try:
            thumb = self.__preview_collections["main"].get(icon_name)
            if thumb is None:
                raise KeyError
        except (KeyError, AttributeError):
            self.log("mbx0001", icon_name, icon_id)
            return 0
        else:
            return thumb.icon_id

    def get_bakejob(self, bkm: PropertyGroup, index=-1
                    ) -> typing.Union[BakeJob, None]:

        if bkm is None:
            return None
        if index == -1:
            index = bkm.bakejobs_active_index
        try:
            bj = bkm.bakejobs[index]
        except IndexError:
            return None

        if bj.has_drop_prompt:
            return None
        else:
            return bj

    def get_container(self, bj: typing.Union[BakeJob, None], index=-1
                      ) -> typing.Union[Container, None]:

        if bj is None:
            return None
        if index == -1:
            index = bj.containers_active_index
        try:
            ctnr = bj.containers[index]
        except IndexError:
            return None

        if ctnr.has_drop_prompt:
            return None
        else:
            return ctnr

    def get_subcontainer(self, ctnr: typing.Union[Container, None], index=-1
                         ) -> typing.Union[Subcontainer, None]:

        if ctnr is None:
            return None
        if index == -1:
            index = ctnr.subcontainers_active_index
        try:
            subctnr = ctnr.subcontainers[index]
        except IndexError:
            return None

        if subctnr.has_drop_prompt:
            return None
        else:
            return subctnr

    def get_active_bakejobs(self, **_
                            ) -> typing.Tuple[PropertyGroup, Collection, str]:
        """Get data, containers, data_name representing bakejobs."""

        return self, self.bakejobs, "bakejobs"

    def get_active_containers(self, **kwargs
                              ) -> typing.Tuple[BakeJob, Collection, str]:
        """
        Get data, containers, data_name representing containers.
        bakejobs_index parameter is optional.
        """

        bj = self.get_bakejob(self, kwargs.get("bakejob_index", -1))
        if bj is None:
            return None, [], "containers"
        return bj, bj.containers, "containers"

    def get_active_subcontainers(self, **kwargs
                                 ) -> typing.Tuple[Container, Collection, str]:
        """
        Get data, containers, data_name representing subcontainers.
        bakejobs_index, container_index parameters are optional.
        """

        bj = self.get_bakejob(self, kwargs.get("bakejob_index", -1))
        ctnr = self.get_container(bj, kwargs.get("container_index", -1))
        if ctnr is None:
            return None, [], "subcontainers"
        return ctnr, ctnr.subcontainers, "subcontainers"

    def wh_recalc_indexes(self, data: PropertyGroup, attr: str,
                          childs_recursive=True, groups=True, parent_props=[]
                          ) -> None:
        """
        Recalculate items' indexes.
        Continues recalculating childs' indexes recursively and
        updating childs' parent indexes props.

        if groups is True, recalculate items' parent_group_indexes based
        on their ui_indent_levels.

        Explicit parent_props[] can be given. Example:
            ...

            bm_ots_utils.indexes_recalc(
                bakejob, "containers", parent_props=[
                    ["bakejob_index", bakejob.index]])

            ...
        """

        if not hasattr(data, attr):
            return

        containers = getattr(data, attr)
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
                        containers, group_index, container.index)

                container.parent_group_index = group_index
                group_level = container.ui_indent_level

                if container.is_group:
                    group_index = container.index

            # assign parent's props
            for prop_name, prop_val in parent_props:
                if hasattr(container, prop_name):
                    setattr(container, prop_name, prop_val)
                else:
                    self.log("mbx0003", AttributeError, prop_name, container)

            if childs_recursive:
                self.wh_recalc_indexes(
                    container, self.get_wh_child_name[attr], childs_recursive,
                    groups, parent_props + [["%s_index" % attr[:-1],
                                             container.index]])
            index += 1

    def wsh_disable_drag(self, data: PropertyGroup, data_name: str,
                         clear_selection=True) -> None:
        """
        Turn off drag.
        If clear_selection is True, unset multi selection.
        """

        _check_walk_data_safety(data_name)

        self.allow_drag = False
        self.drag_from_index = -1
        self.drag_to_index = -1
        self.drag_to_index_temp = -1
        self.drag_from_ticker = False
        self.allow_multi_selection_drag = False
        self.is_drag_lowpoly_data = False

        if self.allow_drag_trans and clear_selection:
            self.__wh_clear_ms(data, data_name)
        self.allow_drag_trans = False

        containers = getattr(data, data_name)
        containers_len = len(containers)

        # No loop, foreach only
        containers.foreach_set("has_drag_prompt", [False] * containers_len)
        containers.foreach_set("is_drag_placeholder", [False] * containers_len)
        containers.foreach_set("is_drag_empty_placeholder",
                               [False] * containers_len)
        containers.foreach_set("is_lowpoly_placeholder",
                               [False] * containers_len)
        containers.foreach_set("is_drag_empty", [False] * containers_len)

    def __wh_clear_ms(self, _: typing.Union[None, PropertyGroup],
                      data_name: str) -> None:

        _check_walk_data_safety(data_name)
        prop_updates._generic_multi_select(None, self, data_name)

    def wh_disable_ms(self, data_name: str) -> None:
        """ Turn off and clear multi selection."""

        _check_walk_data_safety(data_name)
        self.__wh_clear_ms(None, data_name)

        self.allow_multi_select = False
        self.is_multi_selection_empty = True
        self.multi_select_event = ''

    def wh_has_ms(self, data: PropertyGroup, data_name: str) -> bool:

        _check_walk_data_safety(data_name)

        has_ms, _ = self.wh_ms_id(data, data_name)
        return has_ms

    def wh_ms_id(self, data: PropertyGroup, data_name: str
                 ) -> typing.Tuple[bool, str]:

        _check_walk_data_safety(data_name)

        if not all([self.allow_multi_select,
                    not self.is_multi_selection_empty]):
            multi_selection_exists = False
        else:
            multi_selection_exists = True

        if data is None:
            self.log("mbx0000")
            return False, ""

        if hasattr(data, "index"):
            parent_index = data.index
        else:
            parent_index = ""
        our_multi_selection_data = f"{data_name}_{parent_index}"

        return all([self.multi_selection_data == our_multi_selection_data,
                    multi_selection_exists]), our_multi_selection_data

    def wh_is_oneblock_ms(self, data: PropertyGroup, containers: Collection,
                          data_name: str) -> bool:
        """
        Evaluate bakemaster.allow_multi_selection_drag and return True based
        on that and whether multi selection is one-block.
        """

        _check_walk_data_safety(data_name)

        has_ms = self.wh_has_ms(data, data_name)

        if not has_ms:
            return False

        is_oneblock = has_ms
        old_selected_index = -1
        first_ui_indent_level = 0

        for container in containers:
            if any([not container.is_selected,
                    container.has_drop_prompt]):
                continue

            if old_selected_index == -1:
                old_selected_index = container.index
                first_ui_indent_level = container.ui_indent_level
                continue
            if container.index != old_selected_index + 1:
                is_oneblock = False
                break
            elif container.ui_indent_level < first_ui_indent_level:
                is_oneblock = False
                break
            old_selected_index = container.index

        return is_oneblock

    def get_wh_child_name(self, data_name: str) -> str:

        datas = {
            "bakejobs": "containers",
            "containers": "subcontainers",
            "subcontainers": "",
            "bakehistory": ""
        }
        return datas.get(data_name, "")

    def get_wh_parent_name(self, data_name: str) -> str:

        datas = {
            "bakejobs": "",
            "containers": "bakejobs",
            "subcontainers": "containers",
            "bakehistory": ""
        }
        return datas.get(data_name, "")

    def wh_remove(self, data: PropertyGroup, attr: str, index=-1
                  ) -> typing.Tuple[set, str]:
        """
        Wrapper around data.remove(index). Takes Multi Selection into account.
        Return status set and a message.

        Parameters:
            data: data that holds iterable collection with walk features,
            attr: name of the iterable collection attribute,
            index (Optional): if no Multi Selection, remove item of this index.
        """

        if data is None:
            self.log("mbx0000")
            return {'CANCELLED'}, ""

        _check_walk_data_safety(attr)

        has_ms = self.wh_has_ms(data, attr)

        if has_ms:
            mask = data.get_seq(attr, "is_selected", bool)
            to_remove = data.get_seq(attr, "index", int)[mask]
            size = to_remove.size
        else:
            bakejob = self.get_bakejob(data, index)
            if bakejob is None:
                return {'CANCELLED'}, ""
            to_remove = [bakejob.index]
            size = 1

        if size < 1:
            return {'CANCELLED'}, "Nothing to remove"

        for index in reversed(to_remove):
            data.getattr(attr).remove(index)

        self.wh_recalc_indexes(data, attr)
        self.wh_disable_ms(data, attr)

        containers_len = getattr(data, "%s_len" % attr)
        setattr(data, "%s_len" % attr, containers_len - size)
        containers_len = getattr(data, "%s_len" % attr)

        active_index = getattr(data, "%s_active_index" % attr)
        if active_index > containers_len:
            setattr(data, "%s_active_index" % attr, containers_len - 1)

        return {'FINISHED'}, ""

    def wh_trash(self, data: PropertyGroup, attr: str) -> set:
        """
        Wrapper around data.remove(index) for all indexes.
        Returns status set.

        Parameters:
            data: data that holds iterable collection with walk features,
            attr: name of the iterable collection attribute,
        """

        if data is None:
            self.log("mbx0000")

        _check_walk_data_safety(attr)

        [data.getattr(attr).remove(index) for index in
         reversed(range(getattr(data, "%s_len" % attr)))]

        setattr(data, "%s_active_index" % attr, -1)
        setattr(data, "%s_len" % attr, 0)
        return {'FINISHED'}

    def wh_copy(
            self, item_from: typing.Union[BakeJob, Container, Subcontainer],
            data_to: PropertyGroup, to_index=-1,
            exclude: typing.Dict[str, bool] = {}
            ) -> typing.Union[BakeJob, Container, Subcontainer]:
        """
        Copy item_from data-block to item of to_index in iterable data_to.
        If to_index is not given, a new data-block will be instanced.

        Provide exclude{} dictionary with names of attrs to exclude.
        Example (use when copying settings from parent group,
        parent_group_index and ui_indent_level excluded by default):
            {
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
        Default exlude{} is:
            {
                "__annotations__": True,
                "__doc__": True,
                "__module__": True,
                "bl_rna": True,
                "id_data": True,
                "rna_type": True,
                "drop_name": True,
                "drop_name_old": True,
                "parent_group_index": True,
                "ui_indent_level": True,
                "has_drag_prompt": True,
                "has_drop_prompt": True,
                "is_drag_empty": True,
                "is_drag_placeholder": True,
                "is_drag_empty_placeholder": True,
                "is_lowpoly_placeholder": True,
                "ticker": True,
                "drag_empty_ticker": True,
                "lowpoly_ticker": True,
                "is_selected": True
            }
        """

        exclude_attrs = {
            "__annotations__": True,
            "__doc__": True,
            "__module__": True,
            "bl_rna": True,
            "id_data": True,
            "rna_type": True,
            "drop_name": True,
            "drop_name_old": True,
            "parent_group_index": True,
            "ui_indent_level": True,
            "has_drag_prompt": True,
            "has_drop_prompt": True,
            "is_drag_empty": True,
            "is_drag_placeholder": True,
            "is_drag_empty_placeholder": True,
            "is_lowpoly_placeholder": True,
            "ticker": True,
            "drag_empty_ticker": True,
            "lowpoly_ticker": True,
            "is_selected": True
        }

        data_attrs = {
            "bakejobs": True,
            "containers": True,
            "subcontainers": True,
            "bakehistory": True
        }

        if to_index != -1:
            item_to = data_to[to_index]
        else:
            item_to = data_to.add()

        for attr in dir(item_from):
            if exclude_attrs.get(attr, False) or exclude.get(attr, False):
                continue

            if not data_attrs.get(attr, False):
                try:
                    setattr(item_to, attr, getattr(item_from, attr))
                except (AttributeError, IndexError, TypeError,
                        ValueError) as error:
                    self.log("mbx0003", error, attr, item_to)
                continue

            # recursive copy to copy subitems
            containers = getattr(item_from, attr)
            for container in containers:
                _ = self.wh_copy(container, containers)

        return item_to

    def get_object_info(self, objects: Collection, name: str
                        ) -> typing.Tuple[typing.Union[Object, None], str, str,
                                          str, typing.Optional[str], str]:
        """
        Get object info given its name.

        Return values are:
        object, obj_type, obj_icon_type, obj_icon, error_id, error_message.
        """

        errors = {
            'NOTFOUND': f"{name} Object wasn't found",
            'INVALID': "Allowed Objects are: Mesh, Curve, Metaball, Text, Image",  # noqa: E501
            'NOIMAGE': f"{name} Image has no image attached",
        }

        try:
            object = objects[name]
        except KeyError:
            return None, '', '', '', 'NOTFOUND', errors['NOTFOUND']

        if self.prefs_developer_use_orange_ob_icons:
            icon_type = 'ICON_VALUE'
            info = {
                'MESH': self.get_icon('OBJECT'),
                'CURVE': self.get_icon('CURVE'),
                'META': self.get_icon('META'),
                'FONT': self.get_icon('FONT'),
                'EMPTY': self.get_icon('IMAGE'),
            }
        else:
            icon_type = 'ICON'
            info = {
                'MESH': 'OUTLINER_OB_MESH',
                'CURVE': 'OUTLINER_OB_CURVE',
                'META': 'OUTLINER_OB_META',
                'FONT': 'OUTLINER_OB_FONT',
                'EMPTY': 'OUTLINER_OB_IMAGE'
            }

        try:
            info[object.type]
        except KeyError:
            return None, '', '', '', 'INVALID', errors['INVALID']

        if object.type == 'EMPTY':
            if object.empty_display_type != 'IMAGE':
                return None, '', '', '', 'INVALID', errors['INVALID']
            elif object.data is None:
                return None, '', '', '', 'NOIMAGE', errors['NOIMAGE']

        return object, object.type, icon_type, info[object.type], None, ""

    def get_drag_to_index(self, data_name: str, get_name=False) -> int:
        """
        Get drag_to_index value and name based of the currently
        dragged walk_data.
        """

        _check_walk_data_safety(data_name)

        drag_to_index_name = "drag_to_index"

        if all([self.allow_drag_trans,
                data_name == self.drag_data_from]):
            drag_to_index_name = "drag_to_index_temp"

        if not get_name:
            return getattr(self, drag_to_index_name)
        return getattr(self, drag_to_index_name), drag_to_index_name

    def set_drag_to_index(self, data_name: str, value: int) -> int:
        """
        Set drag_to_index value name based of the currently dragged walk_data.
        """

        _check_walk_data_safety(data_name)

        _, drag_to_index_name = self.get_drag_to_index(
            data_name, get_name=True)
        setattr(self, drag_to_index_name, value)

    def get_pref(self, context: Context, propname: str) -> typing.Any:
        """
        Get value of propname addon's preference property.

        Parameters:
            context - active context (to get addon package preferences).

            propname - name of the property.
        """

        package_name = self.__get_package_name()
        pref_value = getattr(
                context.preferences.addons[package_name].preferences,
                propname)
        return pref_value

    def get_addon_version(self, use_tuple=False
                          ) -> typing.Union[str, typing.Tuple[int]]:

        if use_tuple:
            return (3, 0, 0)
        else:
            return "3.0.0"

    def check_walk_data_safety(self, data_name: str) -> None:
        """
        Wrapper around pseudo-private _check_walk_data_safety()
        for calls in other places.
        """

        _check_walk_data_safety(data_name)
