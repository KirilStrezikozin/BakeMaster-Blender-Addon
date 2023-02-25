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
    BM_PT_MainBase,
)
from bpy.types import (
    UIList,
)

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_Main(BM_PT_MainBase):
    """
    BakeMaster panel for Bake Jobs and all subpanels.
    """
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_UL_BakeJobs_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        self.layout.prop(item, "name")

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass
