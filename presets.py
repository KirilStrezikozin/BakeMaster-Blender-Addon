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
import os
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

def presets_makedir(path: str, name: str):
    path_dir = os.path.join(path, name)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

# directory setup for presets
def BM_Presets_FolderSetup():
    bm_presets_subdir = "bakemaster_presets"
    bm_presets_dir_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", bm_presets_subdir)
    bm_presets_paths = bpy.utils.preset_paths(bm_presets_subdir)

    ###########################################################
    # bakemaster_presets main dir
    if bm_presets_dir_path not in bm_presets_paths and not os.path.exists(bm_presets_dir_path):
        os.makedirs(bm_presets_dir_path)

    ###########################################################
    # bakemaster full configurator presets
    presets_makedir(bm_presets_dir_path, "full_configurator_presets")
    ###########################################################
    # object settings presets and subdirs for stt, uv, output presets
    presets_makedir(bm_presets_dir_path, "all_object_settings_presets")
    # stt settings presets subdir
    presets_makedir(bm_presets_dir_path, "stt_settings_presets")
    # uv settings presets subdir
    presets_makedir(bm_presets_dir_path, "uv_settings_presets")
    # output settings presets subdir
    presets_makedir(bm_presets_dir_path, "output_settings_presets")
    ###########################################################
    # map configurator presets and subdir for map settings presets
    presets_makedir(bm_presets_dir_path, "all_map_settings_presets")
    # map settings presets subdir
    presets_makedir(bm_presets_dir_path, "map_settings_presets")
    ###########################################################
    # bake settings presets subdir
    presets_makedir(bm_presets_dir_path, "all_bake_settings_presets")

### PRESET BASES ###

# bake settings preset base
class BM_OT_BakeSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.bakesettings_preset_add"
    bl_label = "Add Bake Settings Preset"
    bl_description = "Add or Remove Bake Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_BakeSettings_Presets'
    preset_subdir = 'bakemaster_presets\\bake_settings_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        "bm_item.use_internal",
        "bm_item.output_filepath",
        "bm_item.use_subfolder",
        "bm_item.subfolder_name",
        "bm_item.batch_name",
        "bm_item.use_material",
        "bm_item.bake_samples",
        "bm_item.bake_use_adaptive_sampling",
        "bm_item.bake_adaptive_threshold",
        "bm_item.bake_min_samples",
        "bm_item.bake_device"
    ]

### UI ###

# bake settings preset panel and menu
class BM_PT_BakeSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Bake Settings Presets"
    preset_subdir = "bakemaster_presets\\bake_settings_presets\\"
    preset_operator = "script.execute_preset"
    preset_add_operator = "bakemaster.bakesettings_preset_add"
    
class BM_MT_BakeSettings_Presets(bpy.types.Menu):
    bl_label = "Bake Settings Presets"
    bl_idname = "BM_MT_BakeSettings_Presets"
    preset_subdir = "bakemaster_presets\\bake_settings_presets\\"
    preset_operator = "script.execute_preset"
    
    draw = bpy.types.Menu.draw_preset