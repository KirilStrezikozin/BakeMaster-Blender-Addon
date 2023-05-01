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


def get_uilist_rows(len_of_idprop, min_rows: int, max_rows: int):
    return min(max_rows, max(min_rows, len_of_idprop))


def get_icon_id(bakemaster, icon_name: str):
    try:
        thumb = bakemaster.preview_collections["main"].get(icon_name)
        if thumb is None:
            raise AttributeError
    except (KeyError, AttributeError):
        print("BakeMaster Internal Warning: icon %s not loaded" % icon_name)
        return 0
    else:
        return thumb.icon_id


def get_group_icon(bakemaster, container, all=False):
    if container.group_type == 'DECORATOR':
        return get_icon_id(bakemaster, "bakemaster_collection.png")

    color_tags = ["", "_color_01", "_color_02", "_color_03", "_color_04",
                  "_color_05", "_color_06", "_color_07", "_color_08"]

    if container.group_type == 'DICTATOR':
        icon_raw = r"bakemaster_collection%s.png"
    else:
        icon_raw = r"bakemaster_smartgroup%s.png"

    if all:
        icons_all = []
        for color_tag in color_tags:
            icons_all.append([
                color_tag,
                get_icon_id(bakemaster, icon_raw % color_tag)])
        return icons_all
    else:
        return get_icon_id(bakemaster, icon_raw % container.group_color_tag)


def bakehistory_timestamp_get_label(bakemaster, bakehistory):
    if bakehistory.index == bakemaster.bakehistory_reserved_index:
        return "in progress..."

    try:
        timediff = datetime.now() - datetime.strptime(bakehistory.time_stamp,
                                                      "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return ""
    seconds = timediff.total_seconds()
    if seconds < 1:
        return "in progress..."
    elif seconds < 60:
        return "%dsec ago" % seconds.__int__()
    minutes = seconds / 60
    if minutes < 60:
        return "%dmin ago" % minutes.__int__()
    hours = minutes / 60
    if hours < 24:
        return "%dh ago" % hours.__int__()
    days = hours / 24
    ending = "s" if days.__int__() > 1 else ""
    if days < 30:
        return "%dday%s ago" % (days.__int__(), ending)
    months = days / 30
    ending = "s" if months.__int__() > 1 else ""
    if months < 12:
        return "%dmonth%s ago" % (months.__int__(), ending)
    years = months / 12
    ending = "s" if years.__int__() > 1 else ""
    return "%dyear%s ago" % (years.__int__(), ending)
