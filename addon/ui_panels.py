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

from .ui_base import (
    BM_PT_BakeJobsBase,
    BM_PT_BakeControlsBase,
    BM_PT_BakeHistoryBase,
    BM_PT_BakeBase,
    bm_ui_utils,
)
from bpy.types import (
    UIList,
    AddonPreferences,
)

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_BakeJobs(BM_PT_BakeJobsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Bake(BM_PT_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_BakeControls(BM_PT_BakeControlsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Bake.bl_idname


class BM_PT_BakeHistory(BM_PT_BakeHistoryBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Bake.bl_idname


class BM_PREFS_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    def poll(self, context):
        return hasattr(context.scene, "bakemaster")

    def draw(self, context):
        bakemaster = context.scene.bakemaster
        col = self.layout.column(align=True)
        col.prop(bakemaster, "prefs_use_show_help")


class BM_UL_BakeJobs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        layout.emboss = 'NONE'

        if item.type == 'OBJECTS':
            type_icon = bm_ui_utils.get_icon_id(bakemaster,
                                                "bakemaster_objects.png")
            type_ot = layout.operator('bakemaster.bakejob_toggletype',
                                      text="", icon_value=type_icon,
                                      emboss=False)
        else:
            type_ot = layout.operator('bakemaster.bakejob_toggletype',
                                      text="", icon='RENDERLAYERS',
                                      emboss=False)
        type_ot.index = item.index

        layout.prop(item, "name", text="")

        icon = 'RESTRICT_RENDER_OFF' if item.use_bake else 'RESTRICT_RENDER_ON'
        layout.prop(item, 'use_bake', text="", icon=icon, emboss=False)

        if item.index == bakemaster.bakejobs_active_index:
            layout.operator('bakemaster.bakejob_rename', text="",
                            icon='GREASEPENCIL').index = item.index

        layout.active = item.use_bake

    def invoke(self, context, event):
        pass


class BM_UL_BakeHistory(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        timestamp = bm_ui_utils.bakehistory_timestamp_get_label(bakemaster,
                                                                item)

        row = layout.row()
        row.prop(item, 'name', text="", emboss=False, icon='RENDER_STILL')
        row.label(text=timestamp)

        row.operator('bakemaster.bakehistory_rebake', text="",
                     icon='RECOVER_LAST').index = item.index
        row.operator('bakemaster.bakehistory_config', text="",
                     icon='FOLDER_REDIRECT').index = item.index
        row.operator('bakemaster.bakehistory_remove', text="",
                     icon='TRASH').index = item.index

        if bakemaster.bakehistory_reserved_index == item.index:
            row.active = False

    def draw_filter(self, context, layout):
        pass

    def filter_items(self, context, data, propname):
        """Draw Bake History in reversed order"""

        flt_flags = [self.bitflag_filter_item] * data.bakehistory_len
        flt_neworder = [index for index in reversed(
            range(data.bakehistory_len))]
        return flt_flags, flt_neworder

    def invoke(self, context, event):
        pass
