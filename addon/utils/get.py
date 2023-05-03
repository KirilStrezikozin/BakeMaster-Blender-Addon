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

from .ui import get_icon_id as bm_ui_utils_get_icon_id


def bakejob(bakemaster: not None, index=-1):
    if index == -1:
        index = bakemaster.bakejobs_active_index
    try:
        bj = bakemaster.bakejobs[index]
    except IndexError:
        return None

    if bj.has_drop_prompt:
        return None
    else:
        return bj


def container(bj, index=-1):
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


def subcontainer(ctnr, index=-1):
    if container is None:
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


def walk_data_get_bakejobs(bakemaster):
    return bakemaster, bakemaster.bakejobs, "bakejobs"


# memleak
def walk_data_get_containers(bakemaster):
    bj = bakejob(bakemaster)
    if bj is None:
        return None, [], "containers"
    return bj, bj.containers, "containers"


def walk_data_get_subcontainers(bakemaster):
    ctnr = container(bakejob(bakemaster))
    if ctnr is None:
        return None, [], "subcontainers"
    return ctnr, ctnr.subcontainers, "subcontainers"


def walk_data_multi_selection_data(bakemaster, data_name: str):
    if not all([bakemaster.allow_multi_select,
                not bakemaster.is_multi_selection_empty]):
        multi_selection_exists = False
    else:
        multi_selection_exists = True

    walk_data_getter = globals()["walk_data_get_%s" % data_name]
    data, _, _ = walk_data_getter(bakemaster)
    if data is None:
        # print(f"BakeMaster Internal Error: cannot resolve walk data at {walk_data_multi_selection_data}")  # noqa: E501
        return False, ""

    if hasattr(data, "index"):
        parent_index = data.index
    else:
        parent_index = ""
    our_multi_selection_data = f"{data_name}_{parent_index}"

    return all([bakemaster.multi_selection_data == our_multi_selection_data,
                multi_selection_exists]), our_multi_selection_data


def is_oneblock_multi_selection(bakemaster, containers, attr):
    # Define bakemaster.allow_multi_selection_drag
    # (if one-block selection)

    has_selection, _ = walk_data_multi_selection_data(
        bakemaster, attr)
    is_oneblock = has_selection

    if not has_selection:
        return False

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


def walk_data_child(data_name: str):
    datas = {
        "bakejobs": "containers",
        "containers": "subcontainers",
        "subcontainers": ""
    }
    return datas[data_name]


def walk_data_parent(data_name: str):
    datas = {
        "bakejobs": "",
        "containers": "bakejobs",
        "subcontainers": "containers"
    }
    return datas[data_name]


def object_ui_info(bakemaster, objects, name: str):
    """
    Get object info given its name.

    Return values are:
    object, obj_type, obj_icon_type, obj_icon, error_id, error_message.
    """

    errors = {
        'NOTFOUND': f"{name} Object wasn't found",
        'INVALID': "Allowed Objects are: Mesh, Curve, Metaball, Text, Image",
        'NOIMAGE': f"{name} Image has no image attached",
    }

    try:
        object = objects[name]
    except KeyError:
        return None, '', '', '', 'NOTFOUND', errors['NOTFOUND']

    if bakemaster.prefs_developer_use_orange_ob_icons:
        icon_type = 'ICON_VALUE'
        info = {
            'MESH': bm_ui_utils_get_icon_id(
                bakemaster, "bakemaster_ob_mesh.png"),
            'CURVE': bm_ui_utils_get_icon_id(
                bakemaster, "bakemaster_ob_curve.png"),
            'META': bm_ui_utils_get_icon_id(
                bakemaster, "bakemaster_ob_meta.png"),
            'FONT': bm_ui_utils_get_icon_id(
                bakemaster, "bakemaster_ob_font.png"),
            'EMPTY': bm_ui_utils_get_icon_id(
                bakemaster, "bakemaster_ob_image.png"),
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


def parent_group(container: not None, containers,
                 stop_at_prop_name: str, stop_at_prop_value,
                 return_at_prop_name: str, return_at_prop_value):
    """
    Get container's parent group.

    Returned container has attribute of stop_at_prop_name equal
    to stop_at_prop_value.

    Climb up until condition above is met and parent's attribute
    of return_at_prop_name equals return_at_prop_value.

    The second return value defines whether the last condition was met.
    """

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
                 getattr(container, stop_at_prop_name) == stop_at_prop_value]):
            if explicit_none:
                return None, True
            return s_parent, True

        if container.parent_group_index == -1:
            if explicit_none:
                return None, False
            return s_parent, False

        container = containers[container.parent_group_index]
