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

from bpy.types import (
    Panel,
)
from .utils import (
    ui as bm_ui_utils,
)


class BM_PT_BakeJobsBase(Panel):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKEJOBS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        box = layout.box()
        row = box.row()
        min_rows = 1 if bakemaster.bakejobs_len < 2 else 3
        rows = bm_ui_utils.get_uilist_rows(bakemaster.bakejobs_len, min_rows,
                                           3)
        row.template_list('BM_UL_BakeJobs', "", bakemaster,
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
        col.emboss = 'NONE'
        col.operator('bakemaster.bakejobs_trash', text="", icon='TRASH')


class BM_PT_BakeBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header(self, context):
        label = "Bake"
        icon = 'RENDER_STILL'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKE'

    def draw(self, context):
        pass


class BM_PT_BakeControlsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_BakeControls'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header(self, context):
        pass

    def draw_header_preset(self, context):
        pass

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(bakemaster, "bake_wait_user")

        col = layout.column(align=True)
        col.operator('bakemaster.bake_one')
        row = col.row()
        row.operator('bakemaster.bake_all')
        row.scale_y = 1.5
        col.active = not bakemaster.bake_is_running

        row = layout.row(align=True)
        if bakemaster.bake_hold_on_pause:
            text = "Resume"
            icon = 'PLAY'
        else:
            text = "Pause"
            icon = 'PAUSE'
        row.operator('bakemaster.bake_pause', text=text, icon=icon)
        row.operator('bakemaster.bake_stop', icon='QUIT')
        row.operator('bakemaster.bake_cancel', icon='CANCEL')
        row.active = bakemaster.bake_is_running

        row = layout.row()
        row.prop(bakemaster, "short_bake_instruction", text="", icon='INFO')
        row.enabled = False

        layout.separator(factor=1.5)


class BM_PT_BakeHistoryBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_BakeHistory'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header(self, context):
        label = "Bake History"
        icon = 'TIME'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKEHISTORY'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        if bakemaster.bakehistory_len == 0:
            row.label(text="No bakes in the history")
            return
        rows = bm_ui_utils.get_uilist_rows(bakemaster.bakehistory_len, 1, 10)
        row.template_list('BM_UL_BakeHistory', "", bakemaster,
                          'bakehistory', bakemaster,
                          'bakehistory_active_index', rows=rows)
