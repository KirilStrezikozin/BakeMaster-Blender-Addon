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


class BM_PT_Helper(Panel):
    """BakeMaster UI Panel Helper class"""

    @classmethod
    def poll(cls, context):
        # Default poll (determine whether able to draw a panel)
        return all([hasattr(context.scene, "bakemaster"),
                    cls.panel_poll(context)])

    @classmethod
    def panel_poll(cls, _):
        # Default empty panel_poll for additional poll checks
        return True

    def draw_header_layout(self, context, help_action='INDEX'):
        # Draw default header layout

        bakemaster = context.scene.bakemaster
        row = self.layout.row()

        if bakemaster.prefs_use_show_help:
            row.operator('bakemaster.help', text="",
                         icon='HELP').action = help_action


class BM_PT_BakeJobsBase(BM_PT_Helper):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobs'

    def draw_header_preset(self, context):
        self.draw_header_layout(context, help_action='BAKEJOBS')

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        box = layout.box()
        row = box.row()
        min_rows = 2 if bakemaster.bakejobs_len < 2 else 4
        rows = bm_ui_utils.get_uilist_rows(bakemaster.bakejobs_len, min_rows,
                                           4)
        row.template_list('BM_UL_BakeJobs', "", bakemaster,
                          'bakejobs', bakemaster,
                          'bakejobs_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.bakejobs_addremove', text="",
                     icon='ADD').action = 'ADD'

        if bakemaster.bakejobs_len > 0:
            col.operator('bakemaster.bakejobs_addremove', text="",
                         icon='REMOVE').action = 'REMOVE'

        col.emboss = 'NONE'
        if bakemaster.bakejobs_len > 1:
            col.separator(factor=1.0)
            col.operator('bakemaster.bakejobs_trash', text="", icon='TRASH')
        col.separator(factor=1.0)
        col.operator('bakemaster.setup', text="", icon='PREFERENCES')


class BM_PT_BakeBase(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'

    def draw_header(self, _):
        label = "Bake"
        icon = 'RENDER_STILL'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        self.draw_header_layout(context, help_action='BAKE')

    def draw(self, _):
        pass


class BM_PT_BakeControlsBase(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_BakeControls'
    bl_options = {'HIDE_HEADER'}

    def draw_header(self, _):
        pass

    def draw_header_preset(self, _):
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


class BM_PT_BakeHistoryBase(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_BakeHistory'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, _):
        label = "Bake History"
        icon = 'TIME'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        self.draw_header_layout(context, help_action='BAKEHISTORY')

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
