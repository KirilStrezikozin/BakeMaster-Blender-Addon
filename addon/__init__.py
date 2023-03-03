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

from bpy.utils import (
    register_class as bpy_utils_register_class,
    unregister_class as bpy_utils_unregister_class,
)
from bpy.types import Scene as bpy_types_Scene
from bpy.props import PointerProperty

from . import ui_panels
from . import properties
from . import presets
from .operators import (
    ui as operators_ui,
)

if "bpy_utils_register_class" in locals():
    from importlib import reload as module_reload

    module_reload(ui_panels)
    module_reload(properties)
    module_reload(presets)
    module_reload(operators_ui)

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

    properties.BM_PROPS_Local_bakejob,
    properties.BM_PROPS_Global,

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

    operators_ui.BM_OT_BakeJobs_AddRemove,
    operators_ui.BM_OT_BakeJobs_Move,
    operators_ui.BM_OT_BakeJobs_Trash,
    operators_ui.BM_OT_Help,
)


def register():
    for cls in classes:
        bpy_utils_register_class(cls)
    bpy_types_Scene.bakemaster = PointerProperty(
            type=properties.BM_PROPS_Global)


def unregister():
    for cls in reversed(classes):
        bpy_utils_unregister_class(cls)
    del bpy_types_Scene.bakemaster


if __name__ == "__main__":
    register()
