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

from .ui_base import (
    BM_PT_BakeJobsBase,
    BM_PT_PipelineBase,
    BM_PT_ManagerBase,
    BM_PT_ObjectsBase,
    BM_PT_MapsBase,
    BM_PT_OutputBase,
    BM_PT_TextureSetsBase,
    BM_PT_BakeBase,
)
from bpy.types import (
    UIList,
)

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_BakeJobs(BM_PT_BakeJobsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Pipeline(BM_PT_PipelineBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Manager(BM_PT_ManagerBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Objects(BM_PT_ObjectsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Maps(BM_PT_MapsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Output(BM_PT_OutputBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_TextureSets(BM_PT_TextureSetsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Bake(BM_PT_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_UL_BakeJobs_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.emboss = 'NONE'
        layout.prop(item, "name", text="", icon='SEQUENCE')
        icon = 'RESTRICT_RENDER_OFF' if item.use_bake else 'RESTRICT_RENDER_ON'
        layout.prop(item, 'use_bake', text="", icon=icon, emboss=False)
        layout.active = item.use_bake

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass
