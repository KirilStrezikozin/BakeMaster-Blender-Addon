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

import bpy
import os
# from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

###########################################################
### Presets Directory Setup ###
###########################################################
def presets_makedir(path: str, name: str):
    path_dir = os.path.join(path, name)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def BM_Presets_FolderSetup():
    bm_presets_subdir = "bakemaster_presets"
    bm_presets_dir_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", bm_presets_subdir)
    bm_presets_paths = bpy.utils.preset_paths(bm_presets_subdir)

    # bakemaster_presets main dir
    if bm_presets_dir_path not in bm_presets_paths and not os.path.exists(bm_presets_dir_path):
        os.makedirs(bm_presets_dir_path)

    presets_makedir(bm_presets_dir_path, "PRESETS_FULL_OBJECT_decal_hl_uv_csh_out_maps_chnlp_bake")
    presets_makedir(bm_presets_dir_path, "PRESETS_OBJECT_decal_hl_uv_csh")
    presets_makedir(bm_presets_dir_path, "PRESETS_DECAL_decal")
    presets_makedir(bm_presets_dir_path, "PRESETS_HL_hl")
    presets_makedir(bm_presets_dir_path, "PRESETS_UV_uv")
    presets_makedir(bm_presets_dir_path, "PRESETS_CSH_csh")
    presets_makedir(bm_presets_dir_path, "PRESETS_OUT_out")
    presets_makedir(bm_presets_dir_path, "PRESETS_FULL_MAP_maps_hl_uv_out")
    presets_makedir(bm_presets_dir_path, "PRESETS_MAP_map")
    presets_makedir(bm_presets_dir_path, "PRESETS_CHNLP_chnlp")
    presets_makedir(bm_presets_dir_path, "PRESETS_BAKE_bake")

###########################################################
### Presets Bases ###
###########################################################
# AddPresetBase script
# original from https://developer.blender.org/diffusion/B/browse/master/release/scripts/startup/bl_operators/presets.py%2424
# modified for bakemaster preset base
class BM_AddPresetBase():
    """BakeMaster Add Preset Base,
       for subclassing"""
    # class has to define:
    # preset_menu
    # preset_subdir
    # preset_defines
    # preset_values
    # optional and preset-dependant:
    # preset_tag

    # only because invoke_props_popup requires. Also do not add to search menu.
    bl_options = {'REGISTER', 'INTERNAL'}

    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the preset, used to make the path name",
        maxlen=64,
        options={'SKIP_SAVE'},
    )
    remove_name: bpy.props.BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    remove_active: bpy.props.BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @staticmethod
    def as_filename(name):  # could reuse for other presets

        # lazy init maketrans
        def maketrans_init():
            cls = BM_AddPresetBase
            attr = "_as_filename_trans"

            trans = getattr(cls, attr, None)
            if trans is None:
                trans = str.maketrans({char: "_" for char in " !@#$%^&*(){}:\";'[]<>,.\\/?"})
                setattr(cls, attr, trans)
            return trans

        name = name.strip()
        name = bpy.path.display_name_to_filepath(name)
        trans = maketrans_init()
        # Strip surrounding "_" as they are displayed as spaces.
        return name.translate(trans).strip("_")

    def execute(self, context):
        import os
        from bpy.utils import is_path_builtin

        if hasattr(self, "pre_cb"):
            self.pre_cb(context)

        preset_menu_class = getattr(bpy.types, self.preset_menu)

        is_xml = getattr(preset_menu_class, "preset_type", None) == 'XML'
        is_preset_add = not (self.remove_name or self.remove_active)

        if is_xml:
            ext = ".xml"
        else:
            ext = ".py"

        name = self.name.strip() if is_preset_add else self.name

        if is_preset_add:
            if not name:
                return {'FINISHED'}

            # Reset preset name
            wm = bpy.data.window_managers[0]
            if name == wm.preset_name:
                wm.preset_name = 'New Preset'

            filename = self.as_filename(name)

            target_path = os.path.join("presets", self.preset_subdir)
            target_path = bpy.utils.user_resource('SCRIPTS', path=target_path, create=True)

            if not target_path:
                self.report({'WARNING'}, "Failed to create presets path")
                return {'CANCELLED'}

            filepath = os.path.join(target_path, filename) + ext

            if hasattr(self, "add"):
                self.add(context, filepath)
            else:
                print("Writing Preset: %r" % filepath)

                if is_xml:
                    import rna_xml
                    rna_xml.xml_file_write(context,
                                           filepath,
                                           preset_menu_class.preset_xml_map)
                else:
                    # Custom for BakeMaster

                    def rna_recursive_attr_expand(value, rna_path_step, level, add_except, except_type, except_for):
                        if isinstance(value, bpy.types.PropertyGroup):
                            for sub_value_attr in value.bl_rna.properties.keys():
                                if sub_value_attr == "rna_type":
                                    continue
                                sub_value = getattr(value, sub_value_attr)
                                rna_recursive_attr_expand(sub_value, "%s.%s" % (rna_path_step, sub_value_attr), level)
                        elif type(value).__name__ == "bpy_prop_collection_idprop":  # could use nicer method
                            file_preset.write("%s.clear()\n" % rna_path_step)
                            for sub_value in value:
                                file_preset.write("item_sub_%d = %s.add()\n" % (level, rna_path_step))
                                rna_recursive_attr_expand(sub_value, "item_sub_%d" % level, level + 1)
                        else:
                            # convert thin wrapped sequences
                            # to simple lists to repr()
                            try:
                                value = value[:]
                            except:
                                pass
                            
                            if add_except and except_type and rna_path_step.find(except_for) != -1:
                                file_preset.write("try:\n")
                                file_preset.write("\t%s = %r\n" % (rna_path_step, value))
                                file_preset.write("except %s:\n" % except_type)
                                file_preset.write("\npass\n")
                            else:
                                file_preset.write("%s = %r\n" % (rna_path_step, value))

                    file_preset = open(filepath, 'w', encoding="utf-8")
                    file_preset.write("import bpy\n")

                    # if item has unique settings per map, append bm_map to preset_defines for hl, uv, out presets
                    preset_defines_bm_item = "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
                    exec(preset_defines_bm_item)
                    if hasattr(self, "preset_tag") and preset_defines_bm_item in self.preset_defines:
                        if getattr(bm_item, "%s_use_unique_per_map" % getattr(self, "preset_tag")) and len(bm_item.global_maps):
                            self.preset_defines.append("bm_map = bm_item.global_maps[bm_item.global_maps_active_index")
                        else:
                            self.preset_defines.append("bm_map = bm_item")

                    add_except = False
                    except_type = ""
                    except_for = ""
                    if hasattr(self, "preset_tag"):
                        # add try except TypeError for channel pack maps for chnl preset
                        if getattr(self, "preset_tag") in ["full_object", "chnlp"]:
                            add_except = True
                            except_type = "TypeError"
                            except_for = "_map_"
                        
                        # append each channel pack props to preset_values for full_object preset
                        if getattr(self, "preset_tag") == "full_object":
                            for channelpack_index, _ in enumerate(bm_item.chnlp_channelpacking_table):
                                channelpack_data = {
                                    "global_channelpack_name",
                                    "global_channelpack_type",
                                    "R1G1B_use_R",
                                    "R1G1B_map_R",
                                    "R1G1B_use_G",
                                    "R1G1B_map_G",
                                    "R1G1B_use_B",
                                    "R1G1B_map_B",
                                    "RGB1A_use_RGB",
                                    "RGB1A_map_RGB",
                                    "RGB1A_use_A",
                                    "RGB1A_map_A",
                                    "R1G1B1A_use_R",
                                    "R1G1B1A_map_R",
                                    "R1G1B1A_use_G",
                                    "R1G1B1A_map_G",
                                    "R1G1B1A_use_B",
                                    "R1G1B1A_map_B",
                                    "R1G1B1A_use_A",
                                    "R1G1B1A_map_A",
                                }
                                for key in channelpack_data:
                                    self.preset_values.append("bm_item.chnlp_channelpacking_table[%d].%s" % (channelpack_index, key))

                        # append each map props to preset_values for full_object, full_map preset
                        if getattr(self, "preset_tag") in ["full_object", "full_map"]:
                            for map_index, _ in enumerate(bm_item.global_maps):
                                map_data = {
                                    "global_map_index",
                                    "global_use_bake",
                                    "global_map_type",
                                    "global_affect_by_hl",

                                    "hl_cage_type",
                                    "hl_cage_extrusion",
                                    "hl_max_ray_distance",

                                    "uv_bake_data",
                                    "uv_bake_target",
                                    "uv_type",
                                    "uv_snap_islands_to_pixels",

                                    "out_use_denoise",
                                    "out_file_format",
                                    "out_exr_codec",
                                    "out_compression",
                                    "out_res",
                                    "out_res_height",
                                    "out_res_width",
                                    "out_margin",
                                    "out_margin_type",
                                    "out_use_32bit",
                                    "out_use_alpha",
                                    "out_use_transbg",
                                    "out_udim_start_tile",
                                    "out_udim_end_tile",
                                    "out_super_sampling_aa",
                                    "out_samples",
                                    "out_use_adaptive_sampling",
                                    "out_adaptive_threshold",
                                    "out_min_samples",

                                    "map_ALBEDO_prefix",

                                    "map_METALNESS_prefix",

                                    "map_ROUGHNESS_prefix",

                                    "map_DIFFUSE_prefix",

                                    "map_SPECULAR_prefix",

                                    "map_GLOSSINESS_prefix",

                                    "map_OPACITY_prefix",

                                    "map_EMISSION_prefix",

                                    "map_PASS_prefix",
                                    "map_pass_type",

                                    "map_DECAL_prefix",
                                    "map_decal_pass_type",
                                    "map_decal_height_opacity_invert",
                                    "map_decal_normal_preset",
                                    "map_decal_normal_custom_preset",
                                    "map_decal_normal_r",
                                    "map_decal_normal_g",
                                    "map_decal_normal_b",

                                    "map_VERTEX_COLOR_LAYER_prefix",
                                    "map_vertexcolor_layer",

                                    "map_C_COMBINED_prefix",

                                    "map_C_AO_prefix",

                                    "map_C_SHADOW_prefix",

                                    "map_C_NORMAL_prefix",

                                    "map_C_UV_prefix",

                                    "map_C_ROUGHNESS_prefix",

                                    "map_C_EMIT_prefix",

                                    "map_C_ENVIRONMENT_prefix",

                                    "map_C_DIFFUSE_prefix",

                                    "map_C_GLOSSY_prefix",

                                    "map_C_TRANSMISSION_prefix",

                                    "map_cycles_use_pass_direct",
                                    "map_cycles_use_pass_indirect",
                                    "map_cycles_use_pass_color",
                                    "map_cycles_use_pass_diffuse",
                                    "map_cycles_use_pass_glossy",
                                    "map_cycles_use_pass_transmission",
                                    "map_cycles_use_pass_ambient_occlusion",
                                    "map_cycles_use_pass_emit",

                                    "map_NORMAL_prefix",
                                    "map_normal_data",
                                    "map_normal_space",
                                    "map_normal_preset",
                                    "map_normal_custom_preset",
                                    "map_normal_r",
                                    "map_normal_g",
                                    "map_normal_b",

                                    "map_DISPLACEMENT_prefix",
                                    "map_displacement_data",
                                    "map_displacement_result",
                                    "map_displacement_subdiv_levels",

                                    "map_VECTOR_DISPLACEMENT_prefix",
                                    "map_vector_displacement_use_default",
                                    "map_vector_displacement_use_negative",
                                    "map_vector_displacement_result",
                                    "map_vector_displacement_subdiv_levels",

                                    "map_POSITION_prefix",

                                    "map_AO_prefix",
                                    "map_ao_use_default",
                                    "map_ao_samples",
                                    "map_ao_distance",
                                    "map_ao_black_point",
                                    "map_ao_white_point",
                                    "map_ao_brightness",
                                    "map_ao_contrast",
                                    "map_ao_opacity",
                                    "map_ao_use_local",
                                    "map_ao_use_invert",

                                    "map_CAVITY_prefix",
                                    "map_cavity_use_default",
                                    "map_cavity_black_point",
                                    "map_cavity_white_point",
                                    "map_cavity_power",
                                    "map_cavity_use_invert",

                                    "map_CURVATURE_prefix",
                                    "map_curv_use_default",
                                    "map_curv_samples",
                                    "map_curv_radius",
                                    "map_curv_black_point",
                                    "map_curv_mid_point",
                                    "map_curv_white_point",
                                    "map_curv_body_gamma",
                                    "map_curv_use_invert",

                                    "map_THICKNESS_prefix",
                                    "map_thick_use_default",
                                    "map_thick_samples",
                                    "map_thick_distance",
                                    "map_thick_black_point",
                                    "map_thick_white_point",
                                    "map_thick_brightness",
                                    "map_thick_contrast",
                                    "map_thick_use_invert",

                                    "map_ID_prefix",
                                    "map_matid_data",
                                    "map_matid_vertex_groups_name_contains",
                                    "map_matid_algorithm",

                                    "map_MASK_prefix",
                                    "map_mask_data",
                                    "map_mask_vertex_groups_name_contains",
                                    "map_mask_materials_name_contains",
                                    "map_mask_color1",
                                    "map_mask_color2",
                                    "map_mask_use_invert",

                                    "map_XYZMASK_prefix",
                                    "map_xyzmask_use_default",
                                    "map_xyzmask_use_x",
                                    "map_xyzmask_use_y",
                                    "map_xyzmask_use_z",
                                    "map_xyzmask_coverage",
                                    "map_xyzmask_saturation",
                                    "map_xyzmask_opacity",
                                    "map_xyzmask_use_invert",

                                    "map_GRADIENT_prefix",
                                    "map_gmask_use_default",
                                    "map_gmask_type",
                                    "map_gmask_location_x",
                                    "map_gmask_location_y",
                                    "map_gmask_location_z",
                                    "map_gmask_rotation_x",
                                    "map_gmask_rotation_y",
                                    "map_gmask_rotation_z",
                                    "map_gmask_scale_x",
                                    "map_gmask_scale_y",
                                    "map_gmask_scale_z",
                                    "map_gmask_coverage",
                                    "map_gmask_contrast",
                                    "map_gmask_saturation",
                                    "map_gmask_opacity",
                                    "map_gmask_use_invert",

                                    "map_EDGE_prefix",
                                    "map_edgemask_use_default",
                                    "map_edgemask_samples",
                                    "map_edgemask_radius",
                                    "map_edgemask_edge_contrast",
                                    "map_edgemask_body_contrast",
                                    "map_edgemask_use_invert",

                                    "map_WIREFRAME_prefix",
                                    "map_wireframemask_line_thickness",
                                    "map_wireframemask_use_invert",
                                }
                                for key in map_data:
                                    self.preset_values.append("bm_item.global_maps[%d].%s" % (map_index, key))

                    if hasattr(self, "preset_defines"):
                        for rna_path in self.preset_defines:
                            exec(rna_path)
                            file_preset.write("%s\n" % rna_path)
                        file_preset.write("\n")

                        if hasattr(self, "preset_tag"):
                            ad_lines = []

                            # write trash, add maps for full_object, full_map preset
                            if getattr(self, "preset_tag") in ["full_object", "full_map"]:
                                ad_lines = [
                                    "to_remove = []",
                                    "for index, _ in bm_item.global_maps:",
                                    "\tto_remove.append(index)",
                                    "bm_item.global_maps_active_index = 0"
                                    "for index in sorted(to_remove, reverse=True):",
                                    "\tbm_item.global_maps.remove(index)",
                                    "for i in range(%s):" % len(bm_item.global_maps),
                                    "\tbm_item.global_maps.add()",
                                ]
                            
                            # write trash, add channel packs for full_object preset
                            if getattr(self, "preset_tag") == "full_object":
                                ad_lines = [
                                    "to_remove = []",
                                    "for index, _ in bm_item.chnlp_channelpacking_table:",
                                    "\tto_remove.append(index)",
                                    "bm_item.chnlp_channelpacking_table_active_index = 0",
                                    "for index in sorted(to_remove, reverse=True):",
                                    "\tbm_item.chnlp_channelpacking_table.remove(index)",
                                    "for i in range(%s):" % len(bm_item.chnlp_channelpacking_table),
                                    "\tbm_item.chnlp_channelpacking_table.add()",
                                ]

                            for line in ad_lines:
                                file_preset.write("%s\n" % line)

                    for rna_path in self.preset_values:
                        value = eval(rna_path)
                        rna_recursive_attr_expand(value, rna_path, 1, add_except, except_type, except_for)

                    # Custom for BakeMaster ended

                    file_preset.close()

            preset_menu_class.bl_label = bpy.path.display_name(filename)
        
        # removing preset
        else:
            if self.remove_active is True:
                name = preset_menu_class.bl_label
            
            # fairly sloppy but convenient.
            filepath = bpy.utils.preset_find(name, self.preset_subdir, ext=ext)

            if not filepath:
                filepath = bpy.utils.preset_find(name, self.preset_subdir, display_name=True, ext=ext)

            if not filepath:
                return {'CANCELLED'}

            # Do not remove bundled presets
            if is_path_builtin(filepath):
                self.report({'WARNING'}, "Unable to remove default presets")
                return {'CANCELLED'}

            try:
                if hasattr(self, "remove"):
                    self.remove(context, filepath)
                else:
                    os.remove(filepath)
            except Exception as e:
                self.report({'ERROR'}, "Unable to remove preset: %r" % e)
                import traceback
                traceback.print_exc()
                return {'CANCELLED'}

            # XXX, stupid!
            preset_menu_class.bl_label = "Presets"

        return {'FINISHED'}

    def check(self, _context):
        self.name = self.as_filename(self.name.strip())

    def invoke(self, context, _event):
        # if not (self.remove_active or self.remove_name):
        #     wm = context.window_manager
        #     return wm.invoke_props_dialog(self)
        # else:
        return self.execute(context)

###########################################################
class BM_OT_FULL_OBJECT_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.full_object_preset_add"
    bl_label = "Full Object Preset"
    bl_description = "Add or Remove Full Object Preset"
    bl_opetions = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_FULL_OBJECT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh_out_maps_chnlp_bake\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_tag = "full_object"

    # maps and channel packs in addpresetbase,
    # depends on bm_item maps and channel packs
    preset_values = [
        "bm_item.decal_is_decal",
        "bm_item.decal_use_custom_camera",
        # "bm_item.decal_custom_camera",
        "bm_item.decal_upper_coordinate",
        "bm_item.decal_boundary_offset",

        # "bm_item.hl_use_unique_per_map"
        # "bm_item.hl_highpoly_table"
        "bm_item.hl_decals_use_separate_texset"
        # "bm_item.hl_use_cage"
        "bm_item.hl_cage_type"
        "bm_item.hl_cage_extrusion"
        "bm_item.hl_max_ray_distance"
        # "bm_item.hl_cage"

        "bm_item.uv_use_unique_per_map",
        "bm_item.uv_bake_data",
        "bm_item.uv_bake_target",
        # "bm_item.uv_active_layer",
        "bm_item.uv_type",
        "bm_item.uv_snap_islands_to_pixels",
        "bm_item.uv_use_auto_unwrap",
        "bm_item.uv_auto_unwrap_angle_limit",
        "bm_item.uv_auto_unwrap_island_margin",
        "bm_item.uv_auto_unwrap_use_scale_to_bounds",
        "bm_item.uv_use_unique_per_map",

        "bm_item.csh_use_triangulate_lowpoly",
        "bm_item.csh_use_lowpoly_reset_normals",
        "bm_item.csh_lowpoly_use_smooth",
        "bm_item.csh_lowpoly_smoothing_groups_enum",
        "bm_item.csh_lowpoly_smoothing_groups_angle",
        "bm_item.csh_lowpoly_smoothing_groups_name_contains",
        "bm_item.csh_use_highpoly_reset_normals",
        "bm_item.csh_highpoly_use_smooth",
        "bm_item.csh_highpoly_smoothing_groups_enum",
        "bm_item.csh_highpoly_smoothing_groups_angle",
        "bm_item.csh_highpoly_smoothing_groups_name_contains",

        "bm_item.out_use_denoise",
        "bm_item.out_file_format",
        "bm_item.out_exr_codec",
        "bm_item.out_compression",
        "bm_item.out_res",
        "bm_item.out_res_height",
        "bm_item.out_res_width",
        "bm_item.out_margin",
        "bm_item.out_margin_type",
        "bm_item.out_use_32bit",
        "bm_item.out_use_alpha",
        "bm_item.out_use_transbg",
        "bm_item.out_udim_start_tile",
        "bm_item.out_udim_end_tile",
        "bm_item.out_super_sampling_aa",
        "bm_item.out_samples",
        "bm_item.out_use_adaptive_sampling",
        "bm_item.out_adaptive_threshold",
        "bm_item.out_min_samples",
        "bm_item.out_use_unique_per_map",

        "bm_item.bake_save_internal",
        # "bm_item.bake_output_filepath",
        "bm_item.bake_create_subfolder",
        "bm_item.bake_subfolder_name",
        "bm_item.bake_batchname",
        "bm_item.bake_batchname_use_caps",
        "bm_item.bake_create_material",
        "bm_item.bake_device",
    ]

class BM_OT_OBJECT_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.object_preset_add"
    bl_label = "Object Preset"
    bl_description = "Add or Remove Decal, High to Lowpoly, UVs & Layers, Shading Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_OBJECT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_OBJECT_decal_hl_uv_csh\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_values = [
        "bm_item.decal_is_decal",
        "bm_item.decal_use_custom_camera",
        # "bm_item.decal_custom_camera",
        "bm_item.decal_upper_coordinate",
        "bm_item.decal_boundary_offset",

        # "bm_item.hl_use_unique_per_map"
        # "bm_item.hl_highpoly_table"
        "bm_item.hl_decals_use_separate_texset"
        # "bm_item.hl_use_cage"
        "bm_item.hl_cage_type"
        "bm_item.hl_cage_extrusion"
        "bm_item.hl_max_ray_distance"
        # "bm_item.hl_cage"

        "bm_item.uv_use_unique_per_map",
        "bm_item.uv_bake_data",
        "bm_item.uv_bake_target",
        # "bm_item.uv_active_layer",
        "bm_item.uv_type",
        "bm_item.uv_snap_islands_to_pixels",
        "bm_item.uv_use_auto_unwrap",
        "bm_item.uv_auto_unwrap_angle_limit",
        "bm_item.uv_auto_unwrap_island_margin",
        "bm_item.uv_auto_unwrap_use_scale_to_bounds",
        "bm_map.uv_use_unique_per_map",

        "bm_item.csh_use_triangulate_lowpoly",
        "bm_item.csh_use_lowpoly_reset_normals",
        "bm_item.csh_lowpoly_use_smooth",
        "bm_item.csh_lowpoly_smoothing_groups_enum",
        "bm_item.csh_lowpoly_smoothing_groups_angle",
        "bm_item.csh_lowpoly_smoothing_groups_name_contains",
        "bm_item.csh_use_highpoly_reset_normals",
        "bm_item.csh_highpoly_use_smooth",
        "bm_item.csh_highpoly_smoothing_groups_enum",
        "bm_item.csh_highpoly_smoothing_groups_angle",
        "bm_item.csh_highpoly_smoothing_groups_name_contains",
    ]

class BM_OT_DECAL_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.decal_preset_add"
    bl_label = "Decal Preset"
    bl_description = "Add or Remove Decal Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_DECAL_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_DECAL_decal\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_values = [
        "bm_item.decal_is_decal",
        "bm_item.decal_use_custom_camera",
        # "bm_item.decal_custom_camera",
        "bm_item.decal_upper_coordinate",
        "bm_item.decal_boundary_offset",
    ]

class BM_OT_HL_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.hl_preset_add"
    bl_label = "High to Lowpoly Preset"
    bl_description = "Add or Remove High to Lowpoly Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_HL_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_HL_hl\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_tag = "hl"

    preset_values = [
        # "bm_map.hl_use_unique_per_map"
        # "bm_map.hl_highpoly_table"
        "bm_map.hl_decals_use_separate_texset"
        # "bm_map.hl_use_cage"
        "bm_map.hl_cage_type"
        "bm_map.hl_cage_extrusion"
        "bm_map.hl_max_ray_distance"
        # "bm_map.hl_cage"
    ]

class BM_OT_UV_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.uv_preset_add"
    bl_label = "UVs & Layers Preset"
    bl_description = "Add or Remove UVs & Layers Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_UV_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_UV_uv\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_tag = "uv"

    preset_values = [
        "bm_map.uv_bake_data",
        "bm_map.uv_bake_target",
        # "bm_map.uv_active_layer",
        "bm_map.uv_type",
        "bm_map.uv_snap_islands_to_pixels",
        "bm_item.uv_use_auto_unwrap",
        "bm_item.uv_auto_unwrap_angle_limit",
        "bm_item.uv_auto_unwrap_island_margin",
        "bm_item.uv_auto_unwrap_use_scale_to_bounds",
        "bm_map.uv_use_unique_per_map",
    ]

class BM_OT_CSH_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.csh_preset_add"
    bl_label = "Shading Preset"
    bl_description = "Add or Remove Shading Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_CSH_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_CSH_csh\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_values = [
        "bm_item.csh_use_triangulate_lowpoly",
        "bm_item.csh_use_lowpoly_reset_normals",
        "bm_item.csh_lowpoly_use_smooth",
        "bm_item.csh_lowpoly_smoothing_groups_enum",
        "bm_item.csh_lowpoly_smoothing_groups_angle",
        "bm_item.csh_lowpoly_smoothing_groups_name_contains",
        "bm_item.csh_use_highpoly_reset_normals",
        "bm_item.csh_highpoly_use_smooth",
        "bm_item.csh_highpoly_smoothing_groups_enum",
        "bm_item.csh_highpoly_smoothing_groups_angle",
        "bm_item.csh_highpoly_smoothing_groups_name_contains",
    ]

class BM_OT_OUT_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.out_preset_add"
    bl_label = "Format Preset"
    bl_description = "Add or Remove Format Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_OUT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_OUT_out\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_tag = "out"

    preset_values = [
        "bm_map.out_use_denoise",
        "bm_map.out_file_format",
        "bm_map.out_exr_codec",
        "bm_map.out_compression",
        "bm_map.out_res",
        "bm_map.out_res_height",
        "bm_map.out_res_width",
        "bm_map.out_margin",
        "bm_map.out_margin_type",
        "bm_map.out_use_32bit",
        "bm_map.out_use_alpha",
        "bm_map.out_use_transbg",
        "bm_map.out_udim_start_tile",
        "bm_map.out_udim_end_tile",
        "bm_map.out_super_sampling_aa",
        "bm_map.out_samples",
        "bm_map.out_use_adaptive_sampling",
        "bm_map.out_adaptive_threshold",
        "bm_map.out_min_samples",
        "bm_map.out_use_unique_per_map",
    ]

class BM_OT_FULL_MAP_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.full_map_preset_add"
    bl_label = "Full Maps Preset"
    bl_description = "Add or Remove Full Maps Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_FULL_MAP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_MAP_maps_hl_uv_out\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_tag = "full_map"

    # added in addpresetbase,
    # depends on bm_item maps
    preset_values = []

class BM_OT_MAP_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.map_preset_add"
    bl_label = "Map Preset"
    bl_description = "Add or Remove Map Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_MAP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_MAP_map\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
        "bm_map = bm_item.global_maps[bm_item.global_maps_active_index]",
    ]

    preset_values = [
        "global_use_bake",
        "global_map_type",
        "global_affect_by_hl",

        "map_ALBEDO_prefix",

        "map_METALNESS_prefix",

        "map_ROUGHNESS_prefix",

        "map_DIFFUSE_prefix",

        "map_SPECULAR_prefix",

        "map_GLOSSINESS_prefix",

        "map_OPACITY_prefix",

        "map_EMISSION_prefix",

        "map_PASS_prefix",
        # "map_PASS_use_preview",
        "map_pass_type",

        "map_DECAL_prefix",
        # "map_DECAL_use_preview",
        "map_decal_pass_type",
        "map_decal_height_opacity_invert",
        "map_decal_normal_preset",
        "map_decal_normal_custom_preset",
        "map_decal_normal_r",
        "map_decal_normal_g",
        "map_decal_normal_b",

        "map_VERTEX_COLOR_LAYER_prefix",
        # "map_VERTEX_COLOR_LAYER_use_preview",
        "map_vertexcolor_layer",

        "map_C_COMBINED_prefix",

        "map_C_AO_prefix",

        "map_C_SHADOW_prefix",

        "map_C_NORMAL_prefix",

        "map_C_UV_prefix",

        "map_C_ROUGHNESS_prefix",

        "map_C_EMIT_prefix",

        "map_C_ENVIRONMENT_prefix",

        "map_C_DIFFUSE_prefix",

        "map_C_GLOSSY_prefix",

        "map_C_TRANSMISSION_prefix",

        "map_cycles_use_pass_direct",
        "map_cycles_use_pass_indirect",
        "map_cycles_use_pass_color",
        "map_cycles_use_pass_diffuse",
        "map_cycles_use_pass_glossy",
        "map_cycles_use_pass_transmission",
        "map_cycles_use_pass_ambient_occlusion",
        "map_cycles_use_pass_emit",

        "map_NORMAL_prefix",
        # "map_NORMAL_use_preview",
        "map_normal_data",
        "map_normal_space",
        "map_normal_preset",
        "map_normal_custom_preset",
        "map_normal_r",
        "map_normal_g",
        "map_normal_b",

        "map_DISPLACEMENT_prefix",
        # "map_DISPLACEMENT_use_preview",
        "map_displacement_data",
        "map_displacement_result",
        "map_displacement_subdiv_levels",

        "map_VECTOR_DISPLACEMENT_prefix",
        # "map_VECTOR_DISPLACEMENT_use_preview",
        "map_vector_displacement_use_default",
        "map_vector_displacement_use_negative",
        "map_vector_displacement_result",
        "map_vector_displacement_subdiv_levels",

        "map_POSITION_prefix",
        # "map_POSITION_use_preview",

        "map_AO_prefix",
        # "map_AO_use_preview",
        "map_ao_use_default",
        "map_ao_samples",
        "map_ao_distance",
        "map_ao_black_point",
        "map_ao_white_point",
        "map_ao_brightness",
        "map_ao_contrast",
        "map_ao_opacity",
        "map_ao_use_local",
        "map_ao_use_invert",

        "map_CAVITY_prefix",
        # "map_CAVITY_use_preview",
        "map_cavity_use_default",
        "map_cavity_black_point",
        "map_cavity_white_point",
        "map_cavity_power",
        "map_cavity_use_invert",

        "map_CURVATURE_prefix",
        # "map_CURVATURE_use_preview",
        "map_curv_use_default",
        "map_curv_samples",
        "map_curv_radius",
        "map_curv_black_point",
        "map_curv_mid_point",
        "map_curv_white_point",
        "map_curv_body_gamma",
        "map_curv_use_invert",

        "map_THICKNESS_prefix",
        # "map_THICKNESS_use_preview",
        "map_thick_use_default",
        "map_thick_samples",
        "map_thick_distance",
        "map_thick_black_point",
        "map_thick_white_point",
        "map_thick_brightness",
        "map_thick_contrast",
        "map_thick_use_invert",

        "map_ID_prefix",
        # "map_ID_use_preview",
        "map_matid_data",
        "map_matid_vertex_groups_name_contains",
        "map_matid_algorithm",

        "map_MASK_prefix",
        # "map_MASK_use_preview",
        "map_mask_data",
        "map_mask_vertex_groups_name_contains",
        "map_mask_materials_name_contains",
        "map_mask_color1",
        "map_mask_color2",
        "map_mask_use_invert",

        "map_XYZMASK_prefix",
        # "map_XYZMASK_use_preview",
        "map_xyzmask_use_default",
        "map_xyzmask_use_x",
        "map_xyzmask_use_y",
        "map_xyzmask_use_z",
        "map_xyzmask_coverage",
        "map_xyzmask_saturation",
        "map_xyzmask_opacity",
        "map_xyzmask_use_invert",

        "map_GRADIENT_prefix",
        # "map_GRADIENT_use_preview",
        "map_gmask_use_default",
        "map_gmask_type",
        "map_gmask_location_x",
        "map_gmask_location_y",
        "map_gmask_location_z",
        "map_gmask_rotation_x",
        "map_gmask_rotation_y",
        "map_gmask_rotation_z",
        "map_gmask_scale_x",
        "map_gmask_scale_y",
        "map_gmask_scale_z",
        "map_gmask_coverage",
        "map_gmask_contrast",
        "map_gmask_saturation",
        "map_gmask_opacity",
        "map_gmask_use_invert",

        "map_EDGE_prefix",
        # "map_EDGE_use_preview",
        "map_edgemask_use_default",
        "map_edgemask_samples",
        "map_edgemask_radius",
        "map_edgemask_edge_contrast",
        "map_edgemask_body_contrast",
        "map_edgemask_use_invert",

        "map_WIREFRAME_prefix",
        # "map_WIREFRAME_use_preview",
        "map_wireframemask_line_thickness",
        "map_wireframemask_use_invert",
    ]

class BM_OT_CHNLP_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.chnlp_preset_add"
    bl_label = "Channel Pack Preset"
    bl_description = "Add or Remove Channel Pack Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_CHNLP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_CHNLP_chnlp\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
        "bm_chnlp_item = bm_item.chnlp_channelpacking_table[bm_item.chnlp_channelpacking_table_active_index]",
    ]

    preset_tag = "chnlp"

    preset_values = [
        "bm_chnlp_item.global_channelpack_name",
        "bm_chnlp_item.global_channelpack_type",
        "bm_chnlp_item.R1G1B_use_R",
        "bm_chnlp_item.R1G1B_map_R",
        "bm_chnlp_item.R1G1B_use_G",
        "bm_chnlp_item.R1G1B_map_G",
        "bm_chnlp_item.R1G1B_use_B",
        "bm_chnlp_item.R1G1B_map_B",
        "bm_chnlp_item.RGB1A_use_RGB",
        "bm_chnlp_item.RGB1A_map_RGB",
        "bm_chnlp_item.RGB1A_use_A",
        "bm_chnlp_item.RGB1A_map_A",
        "bm_chnlp_item.R1G1B1A_use_R",
        "bm_chnlp_item.R1G1B1A_map_R",
        "bm_chnlp_item.R1G1B1A_use_G",
        "bm_chnlp_item.R1G1B1A_map_G",
        "bm_chnlp_item.R1G1B1A_use_B",
        "bm_chnlp_item.R1G1B1A_map_B",
        "bm_chnlp_item.R1G1B1A_use_A",
        "bm_chnlp_item.R1G1B1A_map_A",
    ]

class BM_OT_BAKE_Preset_Add(BM_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.bake_preset_add"
    bl_label = "Bake Output Preset"
    bl_description = "Add or Remove Bake Output Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_BAKE_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_BAKE_bake\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]",
    ]

    preset_values = [
        "bm_item.bake_save_internal",
        # "bm_item.bake_output_filepath",
        "bm_item.bake_create_subfolder",
        "bm_item.bake_subfolder_name",
        "bm_item.bake_batchname",
        "bm_item.bake_batchname_use_caps",
        "bm_item.bake_create_material",
        "bm_item.bake_device",
    ]

###########################################################
### UI Presets Panels and Menus ###
###########################################################
class BM_PT_FULL_OBJECT_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Full Object Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh_out_maps_chnlp_bake\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.full_object_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_FULL_OBJECT_Presets'
    }
class BM_MT_FULL_OBJECT_Presets(bpy.types.Menu):
    bl_label = "Full Object Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh_out_maps_chnlp_bake\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_OBJECT_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Object Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.object_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_OBJECT_Presets'
    }
class BM_MT_OBJECT_Presets(bpy.types.Menu):
    bl_label = "Object Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_DECAL_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Decal Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_DECAL_decal\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.decal_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_DECAL_Presets'
    }
class BM_MT_DECAL_Presets(bpy.types.Menu):
    bl_label = "Decal Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_DECAL_decal\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_HL_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "High to Lowpoly Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_HL_hl\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.hl_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_HL_Presets'
    }
class BM_MT_HL_Presets(bpy.types.Menu):
    bl_label = "High to Lowpoly Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_HL_hl\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_UV_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "UVs & Layers Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_UV_uv\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.uv_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_UV_Presets'
    }
class BM_MT_UV_Presets(bpy.types.Menu):
    bl_label = "UVs & Layers Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_UV_uv\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_CSH_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Shading Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_CSH_csh\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.csh_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_CSH_Presets'
    }
class BM_MT_CSH_Presets(bpy.types.Menu):
    bl_label = "Shading Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_CSH_csh\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_OUT_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Format Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_OUT_out\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.out_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_OUT_Presets'
    }
class BM_MT_OUT_Presets(bpy.types.Menu):
    bl_label = "Format Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_OUT_out\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_FULL_MAP_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Full Maps Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_MAP_maps_hl_uv_out\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.full_maps_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_FULL_MAP_Presets'
    }
class BM_MT_FULL_MAP_Presets(bpy.types.Menu):
    bl_label = "Full Maps Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_MAP_maps_hl_uv_out\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset
    
class BM_PT_MAP_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Map Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_MAP_map\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.map_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_MAP_Presets'
    }
class BM_MT_MAP_Presets(bpy.types.Menu):
    bl_label = "Map Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_MAP_map\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_CHNLP_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Channel Pack Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_CHNLP_chnlp\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.chnlp_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_CHNLP_Presets'
    }
class BM_MT_CHNLP_Presets(bpy.types.Menu):
    bl_label = "Channel Pack Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_CHNLP_chnlp\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

class BM_PT_BAKE_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Bake Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_BAKE_bake\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.chnlp_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_BAKE_Presets'
    }
class BM_MT_BAKE_Presets(bpy.types.Menu):
    bl_label = "Bake Preset"
    preset_subdir = 'bakemaster_presets\\PRESETS_BAKE_bake\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

###########################################################
### Execute Preset ###
###########################################################
# original from https://developer.blender.org/diffusion/B/browse/master/release/scripts/startup/bl_operators/presets.py%24213
# for bakemaster presets modified execution
class BM_OT_ExecutePreset(bpy.types.Operator):
    """Execute BakeMaster preset"""
    bl_idname = "script.execute_preset_bakemaster"
    bl_label = "Load BakeMaster Preset"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH',
        options={'SKIP_SAVE'},
    )
    menu_idname: bpy.props.StringProperty(
        name="Menu ID Name",
        description="ID name of the menu this was called from",
        options={'SKIP_SAVE'},
    )
    affect_all_objects: bpy.props.BoolProperty(
        name="Affect all Objects",
        description="Load Preset for every Object/Container in the Table of Objects",
        default=False,
        options={'SKIP_SAVE'}
    )

    def execute(self, context):
        from os.path import basename, splitext
        filepath = self.filepath

        # change the menu title to the most recently chosen option
        preset_class = getattr(bpy.types, self.menu_idname)
        preset_class.bl_label = bpy.path.display_name(basename(filepath), title_case=False)

        ext = splitext(filepath)[1].lower()

        if ext not in {".py", ".xml"}:
            self.report({'ERROR'}, "Unknown file type: %r" % ext)
            return {'CANCELLED'}

        if hasattr(preset_class, "reset_cb"):
            preset_class.reset_cb(context)

        if ext == ".py":
            try:
                # load preset for every object in bm_table_of_objects
                # execute preset, change item index, execute again, ...
                if self.menu_idname == "BM_MT_FULL_OBJECT_Presets" and self.affect_all_objects:
                    for index, bm_item in enumerate(context.scene.bm_table_of_objects):
                        context.scene.bm_props.global_active_index = index
                        bpy.utils.execfile(filepath)
                else:
                    bpy.utils.execfile(filepath)

            # preset load failed
            except Exception as ex:
                self.report({'ERROR'}, "Failed to execute the preset: " + repr(ex))

        elif ext == ".xml":
            import rna_xml
            rna_xml.xml_file_run(context,
                                 filepath,
                                 preset_class.preset_xml_map)

        if hasattr(preset_class, "post_cb"):
            preset_class.post_cb(context)

        return {'FINISHED'}

    def draw(self, context):
        from os.path import basename
        from .operators import BM_OT_ApplyLastEditedProp_SelectAll, BM_OT_ApplyLastEditedProp_InvertSelection
        bm_props = context.scene.bm_props

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Preset: %s" % basename(self.filepath))

        if self.menu_idname == "BM_MT_FULL_OBJECT_Presets":
            items_box = layout.box()
            items_box.use_property_split = True
            items_box.use_property_decorate = False

            rows = len(bm_props.global_alep_maps)

            table = items_box.column().row()
            table.template_list('BM_ALEP_UL_Objects_Item', "", bm_props, 'global_alep_objects', bm_props, 'global_alep_objects_active_index', rows=rows)
            column = table.column(align=True)
            column.operator(BM_OT_ApplyLastEditedProp_SelectAll.bl_idname, text="", icon='WORLD')
            column.operator(BM_OT_ApplyLastEditedProp_InvertSelection.bl_idname, text="", icon='CHECKBOX_HLT')

    def invoke(self, context, event):
        wm = context.window_manager

        # draw what objects to affect by preset if full_object preset called
        if self.menu_idname == "BM_MT_FULL_OBJECT_Presets":
            bm_props = context.scene.bm_props

            # trash all maps and objects items
            bm_props.global_alep_maps_active_index = 0
            to_remove = []
            for index, _ in enumerate(bm_props.global_alep_maps):
                to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                bm_props.global_alep_maps.remove(index)

            bm_props.global_alep_objects_active_index = 0
            to_remove = []
            for index, _ in enumerate(bm_props.global_alep_objects):
                to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                bm_props.global_alep_objects.remove(index)

            # construct objects items
            global_uni_c_master_index = -1
            for object1 in context.scene.bm_table_of_objects:
                add_object = False
                if context.scene.bm_props.global_use_name_matching:
                    if object1.nm_is_universal_container and object1.nm_uni_container_is_global is False:
                        global_uni_c_master_index = -1
                    if object1.nm_is_detached:
                        add_object = True
                    elif object1.nm_is_universal_container and object1.nm_uni_container_is_global:
                        add_object = True
                        global_uni_c_master_index = object1.nm_master_index
                    elif not any([object1.hl_is_highpoly, object1.hl_is_cage, object1.nm_item_uni_container_master_index == global_uni_c_master_index, object1.nm_is_local_container]) and object1.nm_item_uni_container_master_index != -1:
                        add_object = True
                elif not any([object1.hl_is_highpoly, object1.hl_is_cage]):
                    add_object = True
                
                if add_object:
                    new_object = bm_props.global_alep_objects.add()
                    if object1.nm_is_universal_container:
                        new_object_name = object1.nm_container_name + " Container"
                    else:
                        new_object_name = object1.global_object_name
                    new_object.object_name = new_object_name

            return wm.invoke_props_dialog(self, width=300)
        
        # execute preset
        else:
            return self.execute(context)
