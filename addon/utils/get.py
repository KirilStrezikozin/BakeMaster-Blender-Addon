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

def bakejob(bakemaster: not None, index=-1):
    if index == -1:
        index = bakemaster.bakejobs_active_index
    try:
        bakejob = bakemaster.bakejobs[index]
    except IndexError:
        return None

    if any([bakejob.is_drag_empty, bakejob.has_drop_prompt]):
        return None
    else:
        return bakejob


def item(bakejob, index=-1):
    if bakejob is None:
        return None
    if index == -1:
        index = bakejob.items_active_index
    try:
        item = bakejob.items[index]
    except IndexError:
        return None

    if any([item.is_drag_empty, item.has_drop_prompt]):
        return None
    else:
        return item


def subitem(item, index=-1):
    if item is None:
        return None
    if index == -1:
        index = item.subitems_active_index
    try:
        subitem = item.subitems[index]
    except IndexError:
        return None

    if any([subitem.is_drag_empty, subitem.has_drop_prompt]):
        return None
    else:
        return subitem


def walk_data_get_bakejobs(bakemaster):
    return bakemaster, bakemaster.bakejobs, "bakejobs"


def walk_data_get_items(bakemaster):
    bj = bakejob(bakemaster)
    if bj is None:
        return None, [], "items"
    return bj, bj.items, "items"


def walk_data_get_subitems(bakemaster):
    itm = item(bakejob(bakemaster))
    if itm is None:
        return None, [], "subitems"
    return itm, itm.items, "subitems"
