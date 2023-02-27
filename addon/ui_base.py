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

        len_of_bakejobs = len(bakemaster.bakejobs)

        box = layout.box()
        row = box.row()
        min_rows = 1 if len_of_bakejobs < 2 else 5
        rows = bm_utils_ui_get_uilist_rows(len_of_bakejobs,
                                           min_rows=min_rows,
                                           max_rows=5)
        row.template_list('BM_UL_BakeJobs_Item', "", bakemaster,
                          'bakejobs', bakemaster,
                          'bakejobs_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.bakejobs', text="",
                     icon='ADD').action = 'ADD'
        if len_of_bakejobs >= 2:
            col.operator('bakemaster.bakejobs', text="",
                         icon='REMOVE').action = 'REMOVE'
            col.separator(factor=1.0)

            is_move_up_active = bakemaster.bakejobs_active_index - 1 >= 0
            is_move_down_active = bakemaster.bakejobs_active_index + 1 < len(
                    bakemaster.bakejobs)
            move_up_row = col.row()
            move_up_row.operator('bakemaster.bakejobs', text="",
                                 icon='TRIA_UP').action = 'MOVE_UP'
            move_up_row.active = is_move_up_active
            move_down_row = col.row()
            move_down_row.operator('bakemaster.bakejobs', text="",
                                   icon='TRIA_DOWN').action = 'MOVE_DOWN'
            move_down_row.active = is_move_down_active

            col.separator(factor=1.0)
            col.emboss = 'NONE'
            col.operator('bakemaster.bakejobs', text="",
                         icon='TRASH').action = 'TRASH'
