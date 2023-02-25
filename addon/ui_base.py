# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from bpy.types import (
    Panel,
)
from .utils.ui import (
    get_uilist_rows as bm_utils_ui_get_uilist_rows,
)


class BM_PT_MainBase(Panel):
    bl_label = "BakeMaster"
    bl_idname = 'BM_PT_MainBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        row = layout.row()
        rows = bm_utils_ui_get_uilist_rows(bakemaster.bm_bakejobs, min_rows=1,
                                           max_rows=5)
        row.template_list('BM_UL_BakeJobs_Item', "", bakemaster,
                          'bm_bakejobs', bakemaster,
                          'bm_bakejobs_active_index', rows=rows)
