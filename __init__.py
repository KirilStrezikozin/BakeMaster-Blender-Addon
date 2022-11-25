# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on
# Copyright (C) 2022 Kiril Strezikozin aka kemplerart
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

bl_info = {
    "name" : "BakeMaster",
    "description" : "Bake various PBR-based or Cycles maps with ease and comfort",
    "author" : "kemplerart",
    "version" : (1, 5, 0),
    "blender" : (2, 83, 0),
    "location" : "View3D > Sidebar > BakeMaster",
    "warning" : "",
    "wiki_url": "",
    "tracker_url": "",
    "category" : "Material"
}

if "bpy" in locals():
    from .ui_panel import *
    from .operators import *
    from .properties import *
    from .operator_bake import *
    from .presets import *

    from . import ui_panel
    from . import operators
    from . import properties
    from . import operator_bake
    from . import presets

    import importlib
    importlib.reload(ui_panel)
    importlib.reload(operators)
    importlib.reload(properties)
    importlib.reload(operator_bake)
    importlib.reload(presets)

else:
    from .ui_panel import *
    from .operators import *
    from .properties import *
    from .operator_bake import *
    from .presets import *
    
import bpy

classes = (
    BM_PREFS_Addon_Preferences,

    BM_ALEP_UL_Objects_Item,
    BM_ALEP_UL_Maps_Item,
    BM_CAUC_UL_Objects_Item,
    BM_UL_Table_of_Objects_Item,
    BM_UL_Table_of_Objects_Item_Highpoly,
    BM_UL_Table_of_Maps_Item,
    BM_UL_Table_of_Maps_Item_Highpoly,
    BM_UL_Table_of_Objects_Item_ChannelPack,
    BM_UL_Table_of_TextureSets,
    BM_UL_TextureSets_Objects_Table_Item,
    BM_UL_TextureSets_Objects_Table_Item_SubItem,
    BM_UL_Table_of_Objects_Item_BatchNamingTable_Item,

    BM_PT_Main,
    BM_PT_Item,
    BM_PT_Item_Object,
    BM_PT_Item_Maps,
    BM_PT_Item_Output,
    BM_PT_TextureSets,
    BM_PT_Bake,

    #BM_PT_Item_STT,
    #BM_PT_Item_UVMap,
    #BM_PT_Item_Output,

    #BM_PT_Item_MapList,
    #BM_PT_Item_Map,

    #BM_PT_Item_MainBake,
    #BM_PT_Item_Bake,
    #BM_PT_Item_MainBakeSettings,

    #BM_PT_Main_Help,

    BM_PT_FULL_OBJECT_Presets,
    BM_MT_FULL_OBJECT_Presets,
    BM_PT_OBJECT_Presets,
    BM_MT_OBJECT_Presets,
    BM_PT_DECAL_Presets,
    BM_MT_DECAL_Presets,
    BM_PT_HL_Presets,
    BM_MT_HL_Presets,
    BM_PT_UV_Presets,
    BM_MT_UV_Presets,
    BM_PT_CSH_Presets,
    BM_MT_CSH_Presets,
    BM_PT_OUT_Presets,
    BM_MT_OUT_Presets,
    BM_PT_FULL_MAP_Presets,
    BM_MT_FULL_MAPS_Presets,
    BM_PT_MAP_Presets,
    BM_MT_MAP_Presets,
    BM_PT_CHNLP_Presets,
    BM_MT_CHNLP_Presets,
    BM_PT_BAKE_Presets,
    BM_MT_BAKE_Presets,

    BM_OT_Table_of_Objects,
    BM_OT_Table_of_Objects_Add,
    BM_OT_Table_of_Objects_Remove,
    BM_OT_Table_of_Objects_Refresh,
    BM_OT_Table_of_Objects_Trash,
    BM_OT_ITEM_Highpoly_Table_Add,
    BM_OT_ITEM_Highpoly_Table_Remove,
    BM_OT_MAP_Highpoly_Table_Add,
    BM_OT_MAP_Highpoly_Table_Remove,
    BM_OT_ITEM_ChannelPack_Table_Add,
    BM_OT_ITEM_ChannelPack_Table_Remove,
    BM_OT_ITEM_ChannelPack_Table_Trash,
    BM_OT_SCENE_TextureSets_Table_Add,
    BM_OT_SCENE_TextureSets_Table_Remove,
    BM_OT_SCENE_TextureSets_Table_Trash,
    BM_OT_SCENE_TextureSets_Objects_Table_Add,
    BM_OT_SCENE_TextureSets_Objects_Table_Remove,
    BM_OT_SCENE_TextureSets_Objects_Table_Trash,
    BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems,
    # BM_OT_ITEM_BatchNamingTable_Add,
    # BM_OT_ITEM_BatchNamingTable_Remove,
    # BM_OT_ITEM_BatchNamingTable_Trash,
    BM_OT_ITEM_BatchNaming_Preview,
    BM_OT_ITEM_Maps,
    BM_OT_ITEM_Bake,
    BM_OT_ApplyLastEditedProp_SelectAll,
    BM_OT_ApplyLastEditedProp_InvertSelection,
    BM_OT_ApplyLastEditedProp,
    BM_OT_CreateArtificialUniContainer_DeselectAll,
    BM_OT_CreateArtificialUniContainer,
    BM_OT_Help,

    BM_OT_FULL_OBJECT_Preset_Add,
    BM_OT_OBJECT_Preset_Add,
    BM_OT_DECAL_Preset_Add,
    BM_OT_HL_Preset_Add,
    BM_OT_UV_Preset_Add,
    BM_OT_CSH_Preset_Add,
    BM_OT_OUT_Preset_Add,
    BM_OT_FULL_MAP_Preset_Add,
    BM_OT_MAP_Preset_Add,
    BM_OT_CHNLP_Preset_Add,
    BM_OT_BAKE_Preset_Add,

    BM_ALEP_Object,
    BM_ALEP_Map,
    BM_CAUC_Object,
    BM_Map_Highpoly,
    BM_Map,
    BM_Object_Highpoly,
    BM_Object_ChannelPack,
    # BM_Object_BatchNamingKeyword,
    BM_Object,
    BM_SceneProps_TextureSet_Object_SubObject,
    BM_SceneProps_TextureSet_Object,
    BM_SceneProps_TextureSet,
    BM_SceneProps)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bm_table_of_objects = bpy.props.CollectionProperty(type=BM_Object)
    bpy.types.Scene.bm_props = bpy.props.PointerProperty(type=BM_SceneProps)

    BM_Presets_FolderSetup()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bm_table_of_objects
    del bpy.types.Scene.bm_props

if __name__ == "__main__":
    register()
