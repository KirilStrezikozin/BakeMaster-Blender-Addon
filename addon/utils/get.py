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
from numpy import (
    array as numpy_array,
    isin as numpy_isin,
)


def bakejob(bakemaster: not None, index=-1):
    if index == -1:
        index = bakemaster.bakejobs_active_index
    try:
        bj = bakemaster.bakejobs[index]
    except IndexError:
        return None

    if any([bj.is_drag_empty, bj.has_drop_prompt]):
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

    if any([ctnr.is_drag_empty, ctnr.has_drop_prompt]):
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

    if any([subctnr.is_drag_empty, subctnr.has_drop_prompt]):
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


def object_ui_info(objects, name: str):
    """
    Get object info given its name.

    Return values are:
    object, obj_type, obj_icon, error_id, error_message.
    """

    errors = {
        'NOTFOUND': f"{name} Object wasn't found",
        'INVALID': "Allowed Objects are: Mesh, Curve, Metaball, Text, Image",
        'NOIMAGE': f"{name} Image has no image attached",
    }

    try:
        object = objects[name]
    except KeyError:
        return None, '', '', 'NOTFOUND', errors['NOTFOUND']

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
        return None, '', '', 'INVALID', errors['INVALID']

    if object.type == 'EMPTY':
        if object.empty_display_type != 'IMAGE':
            return None, '', '', 'INVALID', errors['INVALID']
        elif object.data is None:
            return None, '', '', 'NOIMAGE', errors['NOIMAGE']

    return object, object.type, info[object.type], None, ""
