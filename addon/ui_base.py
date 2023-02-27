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


class BM_PT_BakeJobsBase(Panel):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKEJOBS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        box = layout.box()
        row = box.row()
        min_rows = 1 if bakemaster.bakejobs_len < 2 else 5
        rows = bm_utils_ui_get_uilist_rows(bakemaster.bakejobs_len,
                                           min_rows=min_rows,
                                           max_rows=5)
        row.template_list('BM_UL_BakeJobs_Item', "", bakemaster,
                          'bakejobs', bakemaster,
                          'bakejobs_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.bakejobs_addremove', text="",
                     icon='ADD').action = 'ADD'

        if bakemaster.bakejobs_len < 1:
            return

        col.operator('bakemaster.bakejobs_addremove', text="",
                     icon='REMOVE').action = 'REMOVE'

        if bakemaster.bakejobs_len < 2:
            return

        col.separator(factor=1.0)
        move_up_row = col.row()
        move_up_row.operator('bakemaster.bakejobs_move', text="",
                             icon='TRIA_UP').action = 'MOVE_UP'
        move_up_row.active = bakemaster.bakejobs_active_index - 1 >= 0
        move_down_row = col.row()
        move_down_row.operator('bakemaster.bakejobs_move', text="",
                               icon='TRIA_DOWN').action = 'MOVE_DOWN'
        move_down_row.active = False
        if bakemaster.bakejobs_active_index + 1 < bakemaster.bakejobs_len:
            move_down_row.active = True
        col.separator(factor=1.0)
        col.emboss = 'NONE'
        col.operator('bakemaster.bakejobs_trash', text="", icon='TRASH')


class BM_PT_PipelineBase(Panel):
    bl_label = "Pipeline"
    bl_idname = 'BM_PT_PipelineBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'PIPELINE'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_ManagerBase(Panel):
    bl_label = "Manager"
    bl_idname = 'BM_PT_ManagerBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MANAGER'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_ObjectsBase(Panel):
    bl_label = "Objects"
    bl_idname = 'BM_PT_ObjectsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'OBJECTS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_MapsBase(Panel):
    bl_label = "Maps"
    bl_idname = 'BM_PT_MapsBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MAPS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_OutputBase(Panel):
    bl_label = "Output"
    bl_idname = 'BM_PT_OutputBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'OUTPUT'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_TextureSetsBase(Panel):
    bl_label = "Texture Sets"
    bl_idname = 'BM_PT_TextureSetsBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'TEXSETS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_BakeBase(Panel):
    bl_label = "Bake"
    bl_idname = 'BM_PT_BakeBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKE'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout
