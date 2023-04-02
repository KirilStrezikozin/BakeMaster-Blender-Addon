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


def load_preview_collections():
    """
    Load custom icons into preview_collections.

    Raises ResourceWarning(ImagePreviewCollection left open).
    Warning is handled with bpy.ops.bakemaster.previewcollectionsremove()
    by removing preview collections in unregister().
    """

    pcoll = bpy_utils_previews.new()
    icons_dir = os_path.join(os_path.dirname(os_path.dirname(__file__)),
                             "icons")  # no check if path doesn't exist
    for filename in os_listdir(icons_dir):
        filepath = os_path.join(icons_dir, filename)
        pcoll.load(filename, filepath, 'IMAGE')

    return pcoll


def BakeJob_drop_name_Update(self, _):
    if self.drop_name_old == self.drop_name:
        return

    self.name_old = self.name
    bpy_ops.bakemaster.bakejobs_adddropped('INVOKE_DEFAULT', index=self.index)


def BakeJob_drag_ticker_Update(self, context):
    bakemaster = context.scene.bakemaster

    if not bakemaster.is_drag_possible or bakemaster.drag_from_index == -1:
        bakemaster.bakejobs_active_index = self.index
        bakemaster.drag_from_index = self.index
        self.has_drag_prompt = True
        bpy_ops.bakemaster.uilist_walk_drag('INVOKE_DEFAULT')
        return

    if bakemaster.drag_to_index != -1:
        bakemaster.bakejobs[bakemaster.drag_to_index
                            ].is_drag_placeholder = False
    bakemaster.drag_to_index = self.index
    self.is_drag_placeholder = True

    ticker_old = bakemaster.bakejobs[bakemaster.drag_from_index].drag_ticker
    if self.drag_ticker == ticker_old:
        self.drag_ticker = not ticker_old
