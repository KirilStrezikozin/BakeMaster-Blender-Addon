# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 2.5.1)
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

class BM_PT_Item_Object(BM_PT_Item_ObjectBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_Item_Maps(BM_PT_Item_MapsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_Item_Output(BM_PT_Item_OutputBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Item.bl_idname

class BM_PT_TextureSets(BM_PT_TextureSetsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname

class BM_PT_Bake(BM_PT_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname

class BM_PT_Help(BM_PT_HelpBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Main.bl_idname
