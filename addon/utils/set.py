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

from .properties import Generic_multi_select as clear_multi_selection


def disable_drag(bakemaster, containers, data_name: str):
    bakemaster.allow_drag = False
    bakemaster.drag_from_index = -1
    bakemaster.drag_to_index = -1
    bakemaster.drag_from_ticker = False

    if bakemaster.allow_drag_trans:
        clear_multi_selection(None, bakemaster, data_name)
    bakemaster.allow_drag_trans = False

    to_remove = []
    index = 0
    for container in containers:
        container.has_drag_prompt = False
        container.is_drag_placeholder = False
        if container.is_drag_empty:
            to_remove.append(container.index)
            continue
        container.index = index
        index += 1
    for index in reversed(to_remove):
        containers.remove(index)
