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

from bpy.utils import (
    register_class as bpy_utils_register_class,
    unregister_class as bpy_utils_unregister_class,
)
from bpy.types import Scene as bpy_types_Scene
from bpy.props import PointerProperty

from . import ui_panels
from . import properties
from . import presets
from . import operators

if "bpy_utils_register_class" in locals():
    from importlib import reload as module_reload

    module_reload(ui_panels)
    module_reload(properties)
    module_reload(presets)
    module_reload(operators)

bl_info = {
    "name": "BakeMaster",
    "description":
        "Bake various PBR-based or Cycles maps with ease and comfort",
    "author": "kemplerart",
    "version": (3, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > BakeMaster",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}

classes = (
    ui_panels.BM_PT_BakeJobs,
    ui_panels.BM_PT_Pipeline,
    ui_panels.BM_PT_Manager,
    ui_panels.BM_PT_Objects,
    ui_panels.BM_PT_Object,
    ui_panels.BM_PT_Maps,
    ui_panels.BM_PT_Output,
    ui_panels.BM_PT_TextureSets,
    ui_panels.BM_PT_Bake,

    ui_panels.BM_PREFS_AddonPreferences,
    ui_panels.BM_UL_BakeJobs_Item,
    ui_panels.BM_UL_Redolastaction_Objects_Item,
    ui_panels.BM_UL_Redolastaction_Maps_Item,
    ui_panels.BM_UL_BakeGroups_Item,
    ui_panels.BM_UL_Matchres_Item,
    ui_panels.BM_UL_BakeJob_Objects_Item,
    ui_panels.BM_UL_Highpolies_Item,
    ui_panels.BM_UL_MatGroups_Item,
    ui_panels.BM_UL_Maps_Item,
    ui_panels.BM_UL_ChannelPacks_Item,
    ui_panels.BM_UL_TextureSets_Item,
    ui_panels.BM_UL_TextureSets_Objects_Item,
    ui_panels.BM_UL_TextureSets_Objects_Subitems_Item,

    presets.BM_PT_FULL_OBJECT_Presets,
    presets.BM_PT_OBJECT_Presets,
    presets.BM_PT_DECAL_Presets,
    presets.BM_PT_HL_Presets,
    presets.BM_PT_UV_Presets,
    presets.BM_PT_CSH_Presets,
    presets.BM_PT_OUT_Presets,
    presets.BM_PT_FULL_MAP_Presets,
    presets.BM_PT_MAP_Presets,
    presets.BM_PT_CHNLP_Presets,
    presets.BM_PT_BAKE_Presets,
    presets.BM_MT_FULL_OBJECT_Presets,
    presets.BM_MT_OBJECT_Presets,
    presets.BM_MT_DECAL_Presets,
    presets.BM_MT_HL_Presets,
    presets.BM_MT_UV_Presets,
    presets.BM_MT_CSH_Presets,
    presets.BM_MT_OUT_Presets,
    presets.BM_MT_FULL_MAP_Presets,
    presets.BM_MT_MAP_Presets,
    presets.BM_MT_CHNLP_Presets,
    presets.BM_MT_BAKE_Presets,

    operators.ui.BM_OT_Help,
    operators.ui.BM_OT_BakeJobs_AddRemove,
    operators.ui.BM_OT_BakeJobs_Move,
    operators.ui.BM_OT_BakeJobs_Trash,
    operators.ui.BM_OT_Pipeline_Config,
    operators.ui.BM_OT_Pipeline_Import,
    operators.ui.BM_OT_Pipeline_Analyse_Edits,

    operators.ui.BM_OT_Table_of_Objects,
    operators.ui.BM_OT_Table_of_Objects_Add,
    operators.ui.BM_OT_Table_of_Objects_Remove,
    operators.ui.BM_OT_Table_of_Objects_Refresh,
    operators.ui.BM_OT_Table_of_Objects_Trash,
    operators.ui.BM_OT_ITEM_Highpoly_Table_Add,
    operators.ui.BM_OT_ITEM_Highpoly_Table_Remove,
    operators.ui.BM_OT_MAP_Highpoly_Table_Add,
    operators.ui.BM_OT_MAP_Highpoly_Table_Remove,
    operators.ui.BM_OT_ITEM_MatGroups_Table_Refresh,
    operators.ui.BM_OT_ITEM_MatGroups_Table_EqualizeGroups,
    operators.ui.BM_OT_ITEM_MatGroups_Table_UnequalizeGroups,
    operators.ui.BM_OT_ITEM_ChannelPack_Table_Add,
    operators.ui.BM_OT_ITEM_ChannelPack_Table_Remove,
    operators.ui.BM_OT_ITEM_ChannelPack_Table_Trash,
    operators.ui.BM_OT_SCENE_TextureSets_Table_Add,
    operators.ui.BM_OT_SCENE_TextureSets_Table_Remove,
    operators.ui.BM_OT_SCENE_TextureSets_Table_Trash,
    operators.ui.BM_OT_SCENE_TextureSets_Objects_Table_Add,
    operators.ui.BM_OT_SCENE_TextureSets_Objects_Table_Remove,
    operators.ui.BM_OT_SCENE_TextureSets_Objects_Table_Trash,
    operators.ui.BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems,
    operators.ui.BM_OT_ITEM_BatchNaming_Preview,
    operators.ui.BM_OT_ITEM_Maps,
    operators.ui.BM_OT_Bake,
    operators.ui.BM_OT_ApplyLastEditedProp_SelectAll,
    operators.ui.BM_OT_ApplyLastEditedProp_InvertSelection,
    operators.ui.BM_OT_ApplyLastEditedProp,
    operators.ui.BM_OT_CreateArtificialUniContainer_DeselectAll,
    operators.ui.BM_OT_CreateArtificialUniContainer,
    operators.ui.BM_OT_ITEM_and_MAP_Format_MatchResolution,
    operators.ui.BM_OT_ReportMessage,

    presets.BM_OT_FULL_OBJECT_Preset_Add,
    presets.BM_OT_OBJECT_Preset_Add,
    presets.BM_OT_DECAL_Preset_Add,
    presets.BM_OT_HL_Preset_Add,
    presets.BM_OT_UV_Preset_Add,
    presets.BM_OT_CSH_Preset_Add,
    presets.BM_OT_OUT_Preset_Add,
    presets.BM_OT_FULL_MAP_Preset_Add,
    presets.BM_OT_MAP_Preset_Add,
    presets.BM_OT_CHNLP_Preset_Add,
    presets.BM_OT_BAKE_Preset_Add,

    properties.Map_Highpoly,
    properties.Map,
    properties.Object_Highpoly,
    properties.Object_ChannelPack,
    properties.MatGroups_Item,
    properties.Object,
    properties.RedoLastAction_Object,
    properties.RedoLastAction_Map,
    properties.BakeGroup,
    properties.MatchRes,
    properties.TexSet_Object_Subitem,
    properties.TexSet_Object,
    properties.TexSet,
    properties.BakeJob,
    properties.Global,
)


def register():
    for cls in classes:
        bpy_utils_register_class(cls)
    bpy_types_Scene.bakemaster = PointerProperty(
            type=properties.Global)


def unregister():
    for cls in reversed(classes):
        bpy_utils_unregister_class(cls)
    del bpy_types_Scene.bakemaster


if __name__ == "__main__":
    register()
