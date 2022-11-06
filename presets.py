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
    presets_makedir(bm_presets_dir_path, "object_configurator_presets")
    ###########################################################
    # object settings presets and subdirs for stt, uv, output presets
    presets_makedir(bm_presets_dir_path, "object_settings_presets")
    # stt settings presets subdir
    presets_makedir(bm_presets_dir_path, "stt_settings_presets")
    # uv settings presets subdir
    presets_makedir(bm_presets_dir_path, "uv_settings_presets")
    # output settings presets subdir
    presets_makedir(bm_presets_dir_path, "output_settings_presets")
    ###########################################################
    # map configurator presets and subdir for map settings presets
    presets_makedir(bm_presets_dir_path, "maps_configurator_presets")
    # map settings presets subdir
    presets_makedir(bm_presets_dir_path, "map_settings_presets")
    ###########################################################
    # bake settings presets subdir
    presets_makedir(bm_presets_dir_path, "bake_settings_presets")

### PRESET BASES ###

# AddPresetBase script
# original from https://developer.blender.org/diffusion/B/browse/master/release/scripts/startup/bl_operators/presets.py%2424
# modified for bakemaster preset base
class BM_Configurator_AddPresetBase():
    """Configurator base preset class,
       for subclassing"""
    # class has to define:
    # preset_menu
    # preset_subdir
    # preset_defines
    # preset_values

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
            cls = AddPresetBase
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

                    def rna_recursive_attr_expand(value, rna_path_step, level):
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

                            file_preset.write("%s = %r\n" % (rna_path_step, value))

                    file_preset = open(filepath, 'w', encoding="utf-8")
                    file_preset.write("import bpy\n")

                    if hasattr(self, "preset_defines"):
                        for rna_path in self.preset_defines:
                            exec(rna_path)
                            file_preset.write("%s\n" % rna_path)
                        file_preset.write("\n")

                    ### *start of custom code block for bakemaster* ###
                    # writing additional properties to the file_preset

                    # storing data for every map added
                    map_props_names = [
                        "use_bake",
                        "map_type",
                        "bake_target",
                        "use_denoise",
                        "file_format",
                        "res_enum",
                        "res_height",
                        "res_width",
                        "margin",
                        "margin_type",
                        "use_32bit",
                        "use_alpha",
                        "use_source_target",
                        "udim_start_tile",
                        "udim_end_tile",
                        "cycles_use_pass_direct",
                        "cycles_use_pass_indirect",
                        "cycles_use_pass_color",
                        "cycles_use_pass_diffuse",
                        "cycles_use_pass_glossy",
                        "cycles_use_pass_transmission",
                        "cycles_use_pass_ambient_occlusion",
                        "cycles_use_pass_emit",
                        "normal_space",
                        "normal_r",
                        "normal_g",
                        "normal_b",
                        "use_smooth_normals",
                        "normal_cage",
                        "displacement_subdiv_levels",
                        "ao_use_preview",
                        "ao_use_default",
                        "ao_samples",
                        "ao_distance",
                        "ao_black_point",
                        "ao_white_point",
                        "ao_brightness",
                        "ao_contrast",
                        "ao_opacity",
                        "ao_use_local",
                        "ao_use_invert",
                        "cavity_use_preview",
                        "cavity_use_default",
                        "cavity_black_point",
                        "cavity_white_point",
                        "cavity_power",
                        "cavity_use_invert",
                        "curv_use_preview",
                        "curv_use_default",
                        "curv_samples",
                        "curv_radius",
                        "curv_edge_contrast",
                        "curv_body_contrast",
                        "curv_use_invert",
                        "thick_use_preview",
                        "thick_use_default",
                        "thick_samples",
                        "thick_distance",
                        "thick_black_point",
                        "thick_white_point",
                        "thick_brightness",
                        "thick_contrast",
                        "thick_use_invert",
                        "xyzmask_use_preview",
                        "xyzmask_use_default",
                        "xyzmask_use_x",
                        "xyzmask_use_y",
                        "xyzmask_use_z",
                        "xyzmask_coverage",
                        "xyzmask_saturation",
                        "xyzmask_opacity",
                        "xyzmask_use_invert",
                        "gmask_use_preview",
                        "gmask_use_default",
                        "gmask_type",
                        "gmask_location_x",
                        "gmask_location_y",
                        "gmask_location_z",
                        "gmask_rotation_x",
                        "gmask_rotation_y",
                        "gmask_rotation_z",
                        "gmask_scale_x",
                        "gmask_scale_y",
                        "gmask_scale_z",
                        "gmask_coverage",
                        "gmask_contrast",
                        "gmask_saturation",
                        "gmask_opacity",
                        "gmask_use_invert"
                        ]

                    for index, map in enumerate(context.scene.bm_aol[context.scene.bm_props.active_index].maps):
                        for prop in map_props_names:
                            self.preset_values.append("bm_item.maps[%d].%s" % (index, prop))

                    ### *end of custom code block for bakemaster* ###

                    for rna_path in self.preset_values:
                        value = eval(rna_path)
                        rna_recursive_attr_expand(value, rna_path, 1)

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
# object configurator preset base
class BM_OT_ObjectConfigutator_Preset_Add(BM_Configurator_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.objectconfigurator_preset_add"
    bl_label = "Add Object Configuration Preset"
    bl_description = "Add or Remove Object Configuration Preset"
    bl_opetions = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_ObjectConfigurator_Presets'
    preset_subdir = 'bakemaster_presets\\object_configurator_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        # all object settings props
        "bm_item.use_bake",
        "bm_item.use_target",
        "bm_item.use_source",
        "bm_item.source",
        "bm_item.source_name",
        "bm_item.use_cage",
        "bm_item.cage_extrusion",
        "bm_item.max_ray_distance",
        "bm_item.cage_object",
        "bm_item.active_uv",
        "bm_item.uv_type",
        "bm_item.use_islands_pack",
        "bm_item.use_overwrite",
        "bm_item.overwrite_bake_target",
        "bm_item.overwrite_use_denoise",
        "bm_item.overwrite_file_format",
        "bm_item.overwrite_res_enum",
        "bm_item.overwrite_res_height",
        "bm_item.overwrite_res_width",
        "bm_item.overwrite_margin",
        "bm_item.overwrite_margin_type",
        "bm_item.overwrite_use_32bit",
        "bm_item.overwrite_use_alpha",
        "bm_item.overwrite_udim_start_tile",
        "bm_item.overwrite_udim_end_tile",
        #all bake settings props
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

# object settings preset base
class BM_OT_ObjectSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.objectsettings_preset_add"
    bl_label = "Add Object Settings Preset"
    bl_description = "Add or Remove Object Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_ObjectSettings_Presets'
    preset_subdir = 'bakemaster_presets\\object_settings_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        "bm_item.use_target",
        "bm_item.use_source",
        "bm_item.source",
        "bm_item.source_name",
        "bm_item.use_cage",
        "bm_item.cage_extrusion",
        "bm_item.max_ray_distance",
        "bm_item.cage_object",
        "bm_item.active_uv",
        "bm_item.uv_type",
        "bm_item.use_islands_pack",
        "bm_item.use_overwrite",
        "bm_item.overwrite_bake_target",
        "bm_item.overwrite_use_denoise",
        "bm_item.overwrite_file_format",
        "bm_item.overwrite_res_enum",
        "bm_item.overwrite_res_height",
        "bm_item.overwrite_res_width",
        "bm_item.overwrite_margin",
        "bm_item.overwrite_margin_type",
        "bm_item.overwrite_use_32bit",
        "bm_item.overwrite_use_alpha",
        "bm_item.overwrite_udim_start_tile",
        "bm_item.overwrite_udim_end_tile"
    ]

# stt settings preset base
class BM_OT_STTSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.sttsettings_preset_add"
    bl_label = "Add Source to Target Settings Preset"
    bl_description = "Add or Remove Source to Target Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_STTSettings_Presets'
    preset_subdir = 'bakemaster_presets\\stt_settings_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        "bm_item.use_target",
        "bm_item.use_source",
        "bm_item.source",
        "bm_item.source_name",
        "bm_item.use_cage",
        "bm_item.cage_extrusion",
        "bm_item.max_ray_distance",
        "bm_item.cage_object"
    ]

# uv settings preset base
class BM_OT_UVSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.uvsettings_preset_add"
    bl_label = "Add UV Settings Preset"
    bl_description = "Add or Remove UV Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_UVSettings_Presets'
    preset_subdir = 'bakemaster_presets\\uv_settings_presets'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        "bm_item.active_uv",
        "bm_item.uv_type",
        "bm_item.use_islands_pack",
        "bm_item.use_overwrite",
    ]    

# output settings preset base
class BM_OT_OutputSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.outputsettings_preset_add"
    bl_label = "Add Output Settings Preset"
    bl_description = "Add or Remove Output Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_OutputSettings_Presets'
    preset_subdir = 'bakemaster_presets\\output_settings_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = [
        "bm_item.use_overwrite",
        "bm_item.overwrite_bake_target",
        "bm_item.overwrite_use_denoise",
        "bm_item.overwrite_file_format",
        "bm_item.overwrite_res_enum",
        "bm_item.overwrite_res_height",
        "bm_item.overwrite_res_width",
        "bm_item.overwrite_margin",
        "bm_item.overwrite_margin_type",
        "bm_item.overwrite_use_32bit",
        "bm_item.overwrite_use_alpha",
        "bm_item.overwrite_udim_start_tile",
        "bm_item.overwrite_udim_end_tile"
    ]

###########################################################
# map configurator preset base
class BM_OT_MapsConfigutator_Preset_Add(BM_Configurator_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.mapsconfigurator_preset_add"
    bl_label = "Add Maps Configuration Preset"
    bl_description = "Add or Remove Maps Configuration Preset"
    bl_opetions = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_MapsConfigurator_Presets'
    preset_subdir = 'bakemaster_presets\\maps_configurator_presets\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index]"
    ]

    preset_values = []

# map settings preset base
class BM_OT_MapSettings_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.mapsettings_preset_add"
    bl_label = "Add Map Settings Preset"
    bl_description = "Add or Remove Map Settings Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_MapSettings_Presets'
    preset_subdir = 'bakemaster_presets\\map_settings_presets\\'

    preset_defines = [
        "bm_map = bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index].maps[bpy.context.scene.bm_aol[bpy.context.scene.bm_props.active_index].maps_active_index]"
    ]

    preset_values = [
        "bm_map.bake_target",
        "bm_map.use_denoise",
        "bm_map.file_format",
        "bm_map.res_enum",
        "bm_map.res_height",
        "bm_map.res_width",
        "bm_map.margin",
        "bm_map.margin_type",
        "bm_map.use_32bit",
        "bm_map.use_alpha",
        "bm_map.use_source_target",
        "bm_map.udim_start_tile",
        "bm_map.udim_end_tile",
        "bm_map.cycles_use_pass_direct",
        "bm_map.cycles_use_pass_indirect",
        "bm_map.cycles_use_pass_color",
        "bm_map.cycles_use_pass_diffuse",
        "bm_map.cycles_use_pass_glossy",
        "bm_map.cycles_use_pass_transmission",
        "bm_map.cycles_use_pass_ambient_occlusion",
        "bm_map.cycles_use_pass_emit",
        "bm_map.normal_space",
        "bm_map.normal_r",
        "bm_map.normal_g",
        "bm_map.normal_b",
        "bm_map.use_smooth_normals",
        "bm_map.normal_cage",
        "bm_map.displacement_subdiv_levels",
        "bm_map.ao_use_preview",
        "bm_map.ao_use_default",
        "bm_map.ao_sample",
        "bm_map.ao_distance",
        "bm_map.ao_black_point",
        "bm_map.ao_white_point",
        "bm_map.ao_brightness",
        "bm_map.ao_contrast",
        "bm_map.ao_opacity",
        "bm_map.ao_use_local",
        "bm_map.ao_use_invert",
        "bm_map.cavity_use_preview",
        "bm_map.cavity_use_default",
        "bm_map.cavity_black_point",
        "bm_map.cavity_white_point",
        "bm_map.cavity_power",
        "bm_map.cavity_use_invert",
        "bm_map.curv_use_preview",
        "bm_map.curv_use_default",
        "bm_map.curv_sample",
        "bm_map.curv_radius",
        "bm_map.curv_edge_contrast",
        "bm_map.curv_body_contrast",
        "bm_map.curv_use_invert",
        "bm_map.thick_use_preview",
        "bm_map.thick_use_default",
        "bm_map.thick_samples",
        "bm_map.thick_distance",
        "bm_map.thick_black_point",
        "bm_map.thick_white_point",
        "bm_map.thick_brightness",
        "bm_map.thick_contrast",
        "bm_map.thick_use_invert",
        "bm_map.xyzmask_use_preview",
        "bm_map.xyzmask_use_default",
        "bm_map.xyzmask_use_x",
        "bm_map.xyzmask_use_y",
        "bm_map.xyzmask_use_z",
        "bm_map.xyzmask_coverage",
        "bm_map.xyzmask_saturation",
        "bm_map.xyzmask_opacity",
        "bm_map.xyzmask_use_invert",
        "bm_map.gmask_use_preview",
        "bm_map.gmask_use_default",
        "bm_map.gmask_type",
        "bm_map.gmask_location_x",
        "bm_map.gmask_location_y",
        "bm_map.gmask_location_z",
        "bm_map.gmask_rotation_x",
        "bm_map.gmask_rotation_y",
        "bm_map.gmask_rotation_z",
        "bm_map.gmask_scale_x",
        "bm_map.gmask_scale_y",
        "bm_map.gmask_scale_z",
        "bm_map.gmask_coverage",
        "bm_map.gmask_contrast",
        "bm_map.gmask_saturation",
        "bm_map.gmask_opacity",
        "bm_map.gmask_use_invert"
    ]

###########################################################
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

###########################################################
# object configurator preset panel and menu
class BM_PT_ObjectConfigurator_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Object Configuration Preset"
    preset_subdir = 'bakemaster_presets\\object_configurator_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.objectconfigurator_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_ObjectConfigurator_Presets'
    }
class BM_MT_ObjectConfigurator_Presets(bpy.types.Menu):
    bl_label = "Object Configuration Preset"
    preset_subdir = 'bakemaster_presets\\object_configurator_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

# object settings preset panel and menu
class BM_PT_ObjectSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Object Settings Preset"
    preset_subdir = 'bakemaster_presets\\object_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.objectsettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_ObjectSettings_Presets'
    }
class BM_MT_ObjectSettings_Presets(bpy.types.Menu):
    bl_label = "Object Settings Preset"
    preset_subdir = 'bakemaster_presets\\object_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

# stt settings preset panel and menu
class BM_PT_STTSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Source to Target Settings Preset"
    preset_subdir = 'bakemaster_presets\\stt_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.sttsettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_STTSettings_Presets'
    }
class BM_MT_STTSettings_Presets(bpy.types.Menu):
    bl_label = "Source to Target Settings Preset"
    preset_subdir = 'bakemaster_presets\\stt_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

# uv settings preset panel and menu
class BM_PT_UVSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "UV Settings Preset"
    preset_subdir = 'bakemaster_presets\\uv_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.uvsettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_UVSettings_Presets'
    }
class BM_MT_UVSettings_Presets(bpy.types.Menu):
    bl_label = "UV Settings Preset"
    preset_subdir = 'bakemaster_presets\\uv_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

# output settings preset panel and menu
class BM_PT_OutputSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Output Settings Preset"
    preset_subdir = 'bakemaster_presets\\output_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.outputsettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_OutputSettings_Presets'
    }
class BM_MT_OutputSettings_Presets(bpy.types.Menu):
    bl_label = "Output Settings Preset"
    preset_subdir = 'bakemaster_presets\\output_settings_presets\\'
    preset_operator = "script.execute_preset_bakemaster"
    
    draw = bpy.types.Menu.draw_preset

###########################################################
# map configurator preset panel and menu
class BM_PT_MapsConfigurator_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Maps Configuration Presets"
    preset_subdir = "bakemaster_presets\\maps_configurator_presets\\"
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.mapsconfigurator_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_MapsConfigurator_Presets'
    } 
class BM_MT_MapsConfigurator_Presets(bpy.types.Menu):
    bl_label = "Maps Configuration Presets"
    preset_subdir = "bakemaster_presets\\maps_configurator_presets\\"
    preset_operator = "script.execute_preset_bakemaster"
   
    draw = bpy.types.Menu.draw_preset

# map settings preset panel and menu
class BM_PT_MapSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Map Settings Presets"
    preset_subdir = "bakemaster_presets\\map_settings_presets\\"
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.mapsettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_MapSettings_Presets'
    } 
class BM_MT_MapSettings_Presets(bpy.types.Menu):
    bl_label = "Map Settings Presets"
    preset_subdir = "bakemaster_presets\\map_settings_presets\\"
    preset_operator = "script.execute_preset_bakemaster"
   
    draw = bpy.types.Menu.draw_preset

###########################################################
# bake settings preset panel and menu
class BM_PT_BakeSettings_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Bake Settings Presets"
    preset_subdir = "bakemaster_presets\\bake_settings_presets\\"
    preset_operator = "script.execute_preset_bakemaster"
    preset_add_operator = "bakemaster.bakesettings_preset_add"
    preset_operator_defaults = {
        "menu_idname" : 'BM_MT_BakeSettings_Presets'
    } 
class BM_MT_BakeSettings_Presets(bpy.types.Menu):
    bl_label = "Bake Settings Presets"
    preset_subdir = "bakemaster_presets\\bake_settings_presets\\"
    preset_operator = "script.execute_preset_bakemaster"

    draw = bpy.types.Menu.draw_preset

### EXECUTE PRESET ###

def data_insert_smartprops_source_cage(data):
    # get the preset's source and cage_object value
    source_line_index = 0
    source_line = ""
    for index, line in enumerate(data):
        if line.find("bm_item.source") != -1:
            source_line_index = index
            source_line = line.strip()
            break
    source_value = source_line[source_line.find("= ") + 2:]

    cage_line_index = 0
    cage_line = ""
    for index, line in enumerate(data):
        if line.find("bm_item.cage_object") != -1:
            cage_line_index = index
            cage_line = line.strip()
            break
    cage_value = cage_line[cage_line.find("= ") + 2:]

    # checking if use_source and use_cage is true to write data
    write_source = False
    write_cage = False
    for index, line in enumerate(data):
        if line.find("bm_item.use_target") != -1:
            write_source = data[index].strip()[data[index].find("= ") + 2:]
            break
    for index, line in enumerate(data):
        if line.find("bm_item.use_cage") != -1:
            write_cage = data[index].strip()[data[index].find("= ") + 2:]
            break

    # writing data
    if data[source_line_index - 1].strip() != "try:" and write_source == 'True':
        data[source_line_index] = "\nsource_assigned = False\ntry_sources = ['high', 'hpoly', 'high-poly', 'highpoly', 'source']\nfor index, item in enumerate(bpy.context.scene.bm_aol):\n\tif any(name.lower() in item.object_pointer.name.lower() for name in try_sources):\n\t\ttry:\n\t\t\tbm_item.source = str(index)\n\t\texcept (TypeError, KeyError):\n\t\t\tpass\n\t\telse:\n\t\t\tbm_item.source = str(index)\n\t\t\tsource_assigned = True\n\t\t\tbreak\n"#if source_assigned is False:\n\t\ttry:\n\t\t\tbm_item.source = %s\n\t\texcept (TypeError, KeyError):\n\t\t\tpass\n" % source_value

    if data[cage_line_index - 1].strip() != "try:" and write_cage == 'True':
        data[cage_line_index] = "\ncage_assinged = False\ntry_cages = ['cage', 'cageobject']\nfor index, obj in enumerate(bpy.context.scene.objects):\n\tif any(name.lower() in obj.name.lower() for name in try_cages):\n\t\ttry:\n\t\t\tbm_item.cage_object = obj\n\t\texcept (TypeError, KeyError):\n\t\t\tpass\n\t\telse:\n\t\t\tbm_item.cage_object = obj\n\t\t\tcage_assinged = True\n\t\t\tbreak\n"#if cage_assinged is False:\n\ttry:\n\t\tbm_item.cage_object = %s\n\texcept (TypeError, KeyError):\n\t\tpass\n" % cage_value

    return data

def data_insert_smartprops_active_uv(data):
    # get the preset's active_uv value
    active_uv_line_index = 0
    active_uv_line = ""
    for index, line in enumerate(data):
        if line.find("bm_item.active_uv") != -1:
            active_uv_line_index = index
            active_uv_line = line.strip()
            break
    active_uv_value = active_uv_line[active_uv_line.find("= ") + 2:]

    # writing data
    if data[active_uv_line_index - 1].strip() != "try:":
        data[active_uv_line_index] = "\ntry:\n\t%s\nexcept TypeError:\n\tpass\n\n" % active_uv_line

    return data

def data_insert_smartprops_mapsconfig(data):
    # get the max index of map = aka length of maps
    map_index = -1
    for index, line in enumerate(reversed(data)):
        if line.find("bm_item.maps[") != -1:

            map_index_temp = int(line.strip()[line.find("bm_item.maps[") + 13:line.find("].")])
            map_index = map_index_temp if map_index_temp > map_index else map_index
            break
    
    # do not add maps if there are none saved to the preset
    if map_index == -1:
        return data

    insert_line_index = 0
    for index, line in enumerate(data):
        if line.strip() == "":
            insert_line_index = index
            break

    # writing data
    if data[insert_line_index - 1].find("bm_item.maps_active_index = len(bm_item.maps) - 1") == -1:
        data[insert_line_index] = "to_remove = []\nfor index, map in enumerate(bm_item.maps):\n\tto_remove.append(index)\nfor index in to_remove[::-1]:\n\tbm_item.maps.remove(index)\nbm_item.maps_active_index = 0\nfor index in range(%d + 1):\n\tnew_pass = bm_item.maps.add()\n\tnew_pass.map_type = 'ALBEDO'\n\tbm_item.maps_active_index = len(bm_item.maps) - 1\n\n" % map_index

    return data

# not used
def data_insert_configurator_affectall(data):
    # stupid, but only this line 1 is possible
    data[1] = "for bm_item in bpy.context.scene.bm_aol:\n\tif bm_item.use_source is True:\n\t\tcontinue\n\ttry:\n\t\tbpy.context.scene.objects[bm_item.object_pointer.name]\n\texcept (KeyError, UnboundLocalError):\n\t\tcontinue\n\telse:\n"

    data_copy = data

    for index, line in enumerate(data):
        if index >= 2:
            data_copy[index] = "\t\t" + line
    
    return data_copy

# original from https://developer.blender.org/diffusion/B/browse/master/release/scripts/startup/bl_operators/presets.py%24213
# for bakemaster presets modified execution
class BM_OT_ExecutePreset(bpy.types.Operator):
    """Execute a BakeMaster preset"""
    bl_idname = "script.execute_preset_bakemaster"
    bl_label = "Load BakeMaster Preset"
    bl_options = {'REGISTER', 'UNDO'}

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
        description="Load Preset for every object in the List of Objects\n(every object that is not source already and exists in the scene)",
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
            ### SMART PRESETS ###
            # adding custom script to presest file
            # for specific props proper execution
            ###
            menus_ids = ["BM_MT_ObjectConfigurator_Presets",
                         "BM_MT_ObjectSettings_Presets",
                         "BM_MT_STTSettings_Presets",
                         "BM_MT_UVSettings_Presets",
                         "BM_MT_MapsConfigurator_Presets"]
            if self.menu_idname in menus_ids:
                with open(filepath, 'r') as preset_file:
                    data = preset_file.readlines()

                # Object preset uv + stt props
                if self.menu_idname in ["BM_MT_ObjectSettings_Presets", "BM_MT_ObjectConfigurator_Presets"]:
                    data = data_insert_smartprops_source_cage(data)
                    data = data_insert_smartprops_active_uv(data)
                
                # STT preset source and cage_object props
                # try except for TypeError when assigning source
                # smart source and cage_object assignment
                if self.menu_idname == "BM_MT_STTSettings_Presets":
                    data = data_insert_smartprops_source_cage(data)

                # UV preset active_uv prop
                # try except for avoiding TypeError when assigning active_uv
                if self.menu_idname == "BM_MT_UVSettings_Presets":
                    data = data_insert_smartprops_active_uv(data)

                # Maps Configurator prest adding maps and props
                if self.menu_idname in ["BM_MT_MapsConfigurator_Presets", "BM_MT_ObjectConfigurator_Presets"]:
                    data = data_insert_smartprops_mapsconfig(data)

                with open(filepath, 'w') as preset_file:
                    preset_file.writelines(data)
            ###

            try:
                # load preset for every object in the aol
                # execute preset, change item index, execute again, ...
                if self.menu_idname == "BM_MT_ObjectConfigurator_Presets" and self.affect_all_objects is True:
                    for index, bm_item in enumerate(context.scene.bm_aol):
                        if bm_item.use_source:
                            continue
                        try:
                            context.scene.objects[bm_item.object_pointer.name]
                        except (KeyError, UnboundLocalError):
                            continue
                        else:
                            context.scene.bm_props.active_index = index
                            bpy.utils.execfile(filepath)
                
                else:
                    bpy.utils.execfile(filepath)

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

        layout = self.layout
        layout.label(text="Preset: %s" % basename(self.filepath))
        layout.separator(factor=0.35)
        if self.menu_idname == "BM_MT_ObjectConfigurator_Presets":
            layout.prop(self, "affect_all_objects")
    
    def invoke(self, context, event):
        wm = context.window_manager
        if self.menu_idname == "BM_MT_ObjectConfigurator_Presets":
            return wm.invoke_props_dialog(self, width=400)
        else:
            return self.execute(context)
