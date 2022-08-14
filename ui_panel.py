# ##### BEGIN GPL LICENSE BLOCK #####
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

import bpy
from .ui_panel_base import *

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"

class BM_PT_Main(BM_PT_MainBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category

class BM_PT_Item(BM_PT_ItemBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname

class BM_PT_Item_STT(BM_PT_Item_STTBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_Item_UVMap(BM_PT_Item_UVMapBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_Item_Output(BM_PT_Item_OutputBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_Item_MapList(BM_PT_Item_MapListBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname

class BM_PT_Item_Map(BM_PT_Item_MapBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item_MapList.bl_idname

class BM_PT_Item_MainBake(BM_PT_Item_MainBakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname

class BM_PT_Item_Bake(BM_PT_Item_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item_MainBake.bl_idname

class BM_PT_Item_MainBakeSettings(BM_PT_Item_MainBakeSettingsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item_MainBake.bl_idname

class BM_PT_Main_Help(BM_PT_Main_HelpBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname