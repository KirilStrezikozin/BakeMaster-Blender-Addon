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

    from datetime import datetime
    new_item.time_stamp = str(datetime.now())


def bakehistory_remove(bakemaster, remove_index):
    for index in range(remove_index + 1, bakemaster.bakehistory_len):
        bakemaster.bakehistory[index].index -= 1
    bakemaster.bakehistory.remove(remove_index)
    bakemaster.bakehistory_len -= 1


def bakehistory_unreserve(bakemaster):
    bakemaster.bakehistory_reserved_index = -1
