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
from bl_operators.presets import AddPresetBase
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
class BM_OT_FULL_OBJECT_Preset_Add(BM_Configurator_AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.full_object_preset_add"
    bl_label = "Full Object Preset"
    bl_description = "Add or Remove Full Object Preset"
    bl_opetions = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_FULL_OBJECT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_OBJECT_decal_hl_uv_csh_out_maps_chnlp_bake\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_OBJECT_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.object_preset_add"
    bl_label = "Object Preset"
    bl_description = "Add or Remove Decal, High to Lowpoly, UVs & Layers, Shading Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_OBJECT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_OBJECT_decal_hl_uv_csh\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_DECAL_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.decal_preset_add"
    bl_label = "Decal Preset"
    bl_description = "Add or Remove Decal Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_DECAL_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_DECAL_decal\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_HL_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.hl_preset_add"
    bl_label = "High to Lowpoly Preset"
    bl_description = "Add or Remove High to Lowpoly Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_HL_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_HL_hl\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_UV_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.uv_preset_add"
    bl_label = "UVs & Layers Preset"
    bl_description = "Add or Remove UVs & Layers Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_UV_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_UV_uv\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_CSH_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.csh_preset_add"
    bl_label = "Shading Preset"
    bl_description = "Add or Remove Shading Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_CSH_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_CSH_csh\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_OUT_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.out_preset_add"
    bl_label = "Format Preset"
    bl_description = "Add or Remove Format Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_OUT_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_OUT_out\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_FULL_MAP_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.full_map_preset_add"
    bl_label = "Full Maps Preset"
    bl_description = "Add or Remove Full Maps Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_FULL_MAP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_FULL_MAP_maps_hl_uv_out\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_MAP_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.map_preset_add"
    bl_label = "Map Preset"
    bl_description = "Add or Remove Map Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_MAP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_MAP_map\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_CHNLP_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.chnlp_preset_add"
    bl_label = "Channel Pack Preset"
    bl_description = "Add or Remove Channel Pack Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_CHNLP_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_CHNLP_chnlp\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

class BM_OT_BAKE_Preset_Add(AddPresetBase, bpy.types.Operator):
    bl_idname = "bakemaster.bake_preset_add"
    bl_label = "Bake Output Preset"
    bl_description = "Add or Remove Bake Output Preset"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    preset_menu = 'BM_MT_BAKE_Presets'
    preset_subdir = 'bakemaster_presets\\PRESETS_BAKE_bake\\'

    preset_defines = [
        "bm_item = bpy.context.scene.bm_table_of_objects[bpy.context.scene.bm_props.global_active_index]"
    ]

    preset_values = [
        #TODO
    ]

###########################################################
### UI Presets Panels and Menus ###
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
