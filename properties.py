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
from .utils import *
from .labels import BM_Labels

#################################################
### Apply Lastly Edited Prop Props ###
#################################################
class BM_ALEP_Object(bpy.types.PropertyGroup):
    object_name : bpy.props.StringProperty(
        name="Object name",
        default="")
    
    use_affect : bpy.props.BoolProperty(
        name="Apply",
        description="Apply property for this object",
        default=True)

class BM_ALEP_Map(bpy.types.PropertyGroup):
    map_name : bpy.props.StringProperty(
        name="Map name",
        default="")
    
    use_affect : bpy.props.BoolProperty(
        name="Apply",
        description="Apply property for this map",
        default=True)

class BM_CAUC_Object(bpy.types.PropertyGroup):
    object_name : bpy.props.StringProperty(
        name="Object name",
        default="")
    
    use_include : bpy.props.BoolProperty(
        name="Inlcude as Lowpoly",
        description="Include this object as a regular or Lowpoly Object in new Artificial Container",
        default=False,
        update=BM_CAUC_Object_use_include_Update)

    is_highpoly : bpy.props.BoolProperty(
        name="Include as Highpoly",
        description="Include this object as a Highpoly Object in new Artificial Container",
        default=False,
        update=BM_CAUC_Object_is_highpoly_Update)

    is_cage : bpy.props.BoolProperty(
        name="Include as Cage",
        description="Include this object as a Highpoly Object in new Artificial Container",
        default=False,
        update=BM_CAUC_Object_is_cage_Update)

#################################################
### GLOBAL SCENE PROPS ###
#################################################
class BM_SceneProps_TextureSet_Object_SubObject(bpy.types.PropertyGroup):
    global_object_name : bpy.props.StringProperty(
        name="Container's Lowpoly Object")

    global_object_index : bpy.props.IntProperty()
    
    global_object_include_in_texset : bpy.props.BoolProperty(
        name="Include in Texture Set",
        description="Include Container's Lowpoly Object in the current Texture Set",
        default=True)

class BM_SceneProps_TextureSet_Object(bpy.types.PropertyGroup):
    global_object_name : bpy.props.EnumProperty(
        name="Choose Object",
        description="Object from BakeMaster Table of Objects to inlcude in the current Texture Set.\nIf Container's chosen, all it's lowpoly objects will be added to the Texture Set",
        items=BM_TEXSET_OBJECT_PROPS_global_object_name_Items,
        update=BM_TEXSET_OBJECT_PROPS_global_object_name_Update)
    
    global_object_index : bpy.props.IntProperty()

    global_source_object_index : bpy.props.IntProperty(default=-1)

    global_object_name_old : bpy.props.StringProperty(default='-1')

    global_object_name_include : bpy.props.StringProperty()

    global_object_name_subitems_active_index : bpy.props.IntProperty(
        name="Container's Lowpoly Object")

    global_object_name_subitems : bpy.props.CollectionProperty(type=BM_SceneProps_TextureSet_Object_SubObject)

class BM_SceneProps_TextureSet(bpy.types.PropertyGroup):
    global_textureset_name : bpy.props.StringProperty(
        name="Texture Set Name.\nTexture Set is a set of objects that share the same image texture file for each map",
        default="Texture Set")

    global_textureset_index : bpy.props.IntProperty()

    uvp_use_uv_repack : bpy.props.BoolProperty(
        name="UV Repack",
        description="Enable UV Repacking for Texture Set Objects",
        default=False)

    uvp_use_islands_rotate : bpy.props.BoolProperty(
        name="Rotate",
        description="Rotate islands for best fit",
        default=False)

    uvp_pack_margin : bpy.props.FloatProperty(
        name="Margin",
        description="Space between packed islands",
        default=0.01,
        min=0.0,
        max=1.0)
    
    global_textureset_naming : bpy.props.EnumProperty(
        name="Naming",
        description="Choose output Image texture naming format",
        default='TEXSET_NAME',
        items=[('EACH_OBJNAME', "Each Object Name", "Include each texture set object name in the output texture set image"),
               ('TEXSET_INDEX', "Texture Set Index", "Name output texture set image in the format: TextureSet_index"),
               ('TEXSET_NAME', "Texture Set Name", "Output texture name will be as Texture Set name")])
    
    global_textureset_table_of_objects : bpy.props.CollectionProperty(type=BM_SceneProps_TextureSet_Object)

    global_textureset_table_of_objects_active_index : bpy.props.IntProperty(
        name="Object",
        default=0)

class BM_SceneProps(bpy.types.PropertyGroup):
    global_active_index : bpy.props.IntProperty(
        name="Mesh Object to bake maps for",
        default=0,
        update=BM_ActiveIndexUpdate)
    
    global_use_name_matching : bpy.props.BoolProperty(
        name="Toggle Name Matching",
        description="If on, High, Lowpoly, and Cage objects will be grouped by their matched names.\nProperties like Highpoly object and Cage will be set automatically if possible, maps and other settings can be configured by the top-parent container",
        default=False,
        update=BM_SCENE_PROPS_global_use_name_matching_Update)

    global_last_edited_prop : bpy.props.StringProperty(default="")
    global_last_edited_prop_name : bpy.props.StringProperty(default="")
    global_last_edited_prop_value : bpy.props.StringProperty(default="")
    global_last_edited_prop_type : bpy.props.StringProperty(default="")
    global_last_edited_prop_is_map : bpy.props.BoolProperty(default=False)

# Apply Lastly Edited Prop Props
    global_alep_objects : bpy.props.CollectionProperty(type=BM_ALEP_Object)

    global_alep_objects_active_index : bpy.props.IntProperty(
        name="Object",
        default=0)

    global_alep_maps : bpy.props.CollectionProperty(type=BM_ALEP_Map)

    global_alep_maps_active_index : bpy.props.IntProperty(
        name="Map",
        default=0)

    global_alep_affect_objects : bpy.props.BoolProperty(
        name="Affect Objects",
        description="Apply property to all maps of chosen objects",
        default=False)

# Create Artificial Universal Container Props
    global_cauc_objects : bpy.props.CollectionProperty(type=BM_CAUC_Object)

    global_cauc_objects_active_index : bpy.props.IntProperty(
        name="Detached Object",
        default=0)
    
# Global Panels Props
    global_is_decal_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Decal Settings panel",
        default=False)

    global_is_hl_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    global_is_uv_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    global_is_csh_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Shading Settings panel",
        default=False)

    global_is_format_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Format Settings panel",
        default=False)

    global_is_chnlpack_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Channel Packing panel",
        default=False)

    global_is_bakeoutput_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Bake Output Settings panel",
        default=False)

    local_is_hl_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    local_is_uv_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    local_is_batchname_panel_expanded : bpy.props.BoolProperty(
        name="Expand/Collapse Batch Naming panel",
        default=False)

# Global Bake-related Props
    global_bake_use_save_log : bpy.props.BoolProperty(
        name="Save Log",
        description="Save log of time used to bake each map and a short summary of all baked maps for all baked objects into a .txt file",
        default=False)

    global_use_bakemaster_reset : bpy.props.BoolProperty(
        name="Reset BakeMaster",
        description="Reset all objects settings and remove all objects from BakeMaster",
        default=True)

    global_bake_instruction : bpy.props.StringProperty(
        name="Bake Operator Instruction",
        default="Bake Instruction",
        description=BM_Labels.OPERATOR_ITEM_BAKE_FULL_DESCRIPTION)

    global_bake_available : bpy.props.BoolProperty(
        default=True)

# GLobal Texture Sets Props
    global_texturesets_table : bpy.props.CollectionProperty(type=BM_SceneProps_TextureSet)

    global_texturesets_active_index : bpy.props.IntProperty(
        name="Texture Set.\nTexture Set is a set of objects that share the same image texture file for each map",
        default=0)

# Addon Preferences Props
    global_lowpoly_tag : bpy.props.StringProperty(
        name="Lowpoly Tag",
        description="What keyword to search for in Object name to determine if it's a Lowpoly Object",
        default="low")

    global_highpoly_tag : bpy.props.StringProperty(
        name="Highpoly Tag",
        description="What keyword to search for in Object name to determine if it's a Highpoly Object",
        default="high")

    global_cage_tag : bpy.props.StringProperty(
        name="Cage Tag",
        description="What keyword to search for in Object name to determine if it's a Cage Object",
        default="cage")

    global_decal_tag : bpy.props.StringProperty(
        name="Decal Tag",
        description="What keyword to search for in Object name to determine if it's a Decal Object",
        default="decal")

    global_bake_uv_layer_tag : bpy.props.StringProperty(
        name="UVMap Tag",
        description="What UVMap name should include for BakeMaster to see it as UVMap for bake",
        default="bake")

##################################################
### MAP PROPS ###
##################################################

class BM_Map_Highpoly(bpy.types.PropertyGroup):
    global_object_name : bpy.props.EnumProperty(
        name="Highpoly",
        description="Choose Highpoly for the Object from the list\n(Highpoly should be added to BakeMaster Table of Objects)",
        items=BM_ITEM_PROPS_hl_highpoly_Items,
        update=BM_ITEM_PROPS_hl_highpoly_Update)
    
    global_item_index : bpy.props.IntProperty()

    global_highpoly_name_old : bpy.props.StringProperty()

    global_highpoly_object_index : bpy.props.IntProperty(default=-1)

    global_highpoly_object_include : bpy.props.StringProperty(default="")

class BM_Map(bpy.types.PropertyGroup):
    global_use_bake : bpy.props.BoolProperty(
        name="Include/exclude map in the bake",
        default=True,
        update=BM_MAP_PROPS_global_use_bake_Update)

    global_map_type : bpy.props.EnumProperty(
        name="Choose Map Type",
        description="Set map type for the current pass",
        items=BM_MAP_PROPS_map_type_Items,
        update=BM_MAP_PROPS_global_map_type_Update)
    
    global_map_index : bpy.props.IntProperty()

    global_affect_by_hl : bpy.props.BoolProperty(
        name="Affect by High to Lowpoly Settings",
        description="Use High to Lowpoly Settigns for baking this map. If checked, bake will be performed from highpoly to lowpoly, otherwise just bake lowpoly",
        default=True,
        update=BM_MAP_PROPS_global_affect_by_hl_Update)
    
# Map High to Lowpoly props:
    hl_highpoly_table : bpy.props.CollectionProperty(type=BM_Map_Highpoly)

    hl_highpoly_table_active_index : bpy.props.IntProperty(
        name="Highpoly Object",
        default=0)

    hl_use_cage : bpy.props.BoolProperty(
        name="Use Cage Object",
        description="Cast rays to Object from cage",
        default=False,
        update=BM_ITEM_PROPS_hl_use_cage_Update)

    hl_cage_type : bpy.props.EnumProperty(
        name="Cage type",
        description="Type of Cage properties to use",
        items=[('STANDARD', "Standard", "Standard Cage properties of Cycles Bake.\nSet extrusion, ray distance, and choose cage object"),
               ('SMART', "Smart", "Auto cage creation using lowpoly mesh displace. Saves time with simple cage")],
        update=BM_MAP_PROPS_hl_cage_type_Update)

    hl_cage_extrusion : bpy.props.FloatProperty(
        name="Cage Extrusion",
        description="Inflate by the specified distance to create cage",
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=BM_MAP_PROPS_hl_cage_extrusion_Update)
    
    hl_max_ray_distance : bpy.props.FloatProperty(
        name="Max Ray Distance",
        description="The maximum ray distance for matching points between the high and lowpoly. If zero, there is no limit",
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=BM_MAP_PROPS_hl_max_ray_distance_Update)

    hl_cage : bpy.props.EnumProperty(
        name="Cage Object",
        description="Object to use as cage instead of calculating with cage extrusion",
        items=BM_ITEM_PROPS_hl_cage_Items,
        update=BM_ITEM_PROPS_hl_cage_Update)

    hl_cage_name_old : bpy.props.StringProperty()

    hl_cage_object_index : bpy.props.IntProperty(default=-1)

    hl_cage_object_include : bpy.props.StringProperty(default="")

# Map UV Props:
    uv_bake_data : bpy.props.EnumProperty(
        name="Bake Data",
        description="Choose data type to use for baking",
        default='OBJECT_MATERIALS',
        items=[('OBJECT_MATERIALS', "Object/Materials", "Use Object and Materials data for baking regular maps"),
                 ('VERTEX_COLORS', "Vertex Colors", "Bake VertexColor Layers to Image Textures")],
        update=BM_MAP_PROPS_uv_bake_data_Update)

    uv_bake_target : bpy.props.EnumProperty(
        name="Bake Target",
        description="Choose Baked Maps output target",
        items=BM_ITEM_PROPS_uv_bake_target_Items,
        update=BM_MAP_PROPS_uv_bake_target_Update)

    uv_active_layer : bpy.props.EnumProperty(
        name="Active UV Map",
        description="Choose active UVMap layer to use in the bake.\nIf mesh has got no UV layers and at least one map to be baked to image texture, auto UV unwrap will be proceeded",
        items=BM_ITEM_PROPS_uv_active_layer_Items)

    uv_type : bpy.props.EnumProperty(
        name = "UV Map Type",
        description = "UVMap type is set automatically when changing Active UV Map. Change if it's not correct",
        items = BM_ITEM_PROPS_uv_type_Items,
        update=BM_MAP_PROPS_uv_type_Update)

    uv_snap_islands_to_pixels : bpy.props.BoolProperty(
        name="Snap to pixels",
        description="Snap UVMap islands to pixel edges for clearer result",
        update=BM_MAP_PROPS_uv_snap_islands_to_pixels_Update)

    # uv_use_auto_unwrap : bpy.props.BoolProperty(
    #     name="Auto Unwrap",
    #     description="Auto UV Unwrap object using smart project",
    #     update=BM_ITEM_PROPS_UVSettings_Update)

    # uv_auto_unwrap_angle_limit : bpy.props.IntProperty(
    #     name="Angle Limit",
    #     description="The angle at which to place seam on the mesh for unwrapping",
    #     default=66,
    #     min=0,
    #     max=89,
    #     subtype='ANGLE',
    #     update=BM_ITEM_PROPS_UVSettings_Update)

    # uv_auto_unwrap_island_margin : bpy.props.FloatProperty(
    #     name="Island Margin",
    #     description="Set distance between adjacent UV islands",
    #     default=0.01,
    #     min=0,
    #     max=1,
    #     update=BM_ITEM_PROPS_UVSettings_Update)
    
    # uv_auto_unwrap_use_scale_to_bounds : bpy.props.BoolProperty(
    #     name="Scale to Bounds",
    #     description="Scale UV coordinates to bounds to fill the whole UV tile area",
    #     default=True,
    #     update=BM_ITEM_PROPS_UVSettings_Update)

# Map Output Props:
    out_use_denoise : bpy.props.BoolProperty(
        name="Denoise",
        description="Denoise and Discpeckle baked maps as a post-process filter",
        default=False,
        update=BM_MAP_PROPS_out_use_denoise_Update)

    out_file_format : bpy.props.EnumProperty(
        name="File Format",
        description="File format of output image files",
        default='PNG',
        items=[('BMP', "BMP", "Output image in bitmap format"),
               ('PNG', "PNG", "Output image in common PNG format. Best file format for true-color images that need perfect tone balance. Default Blender image format.\n\Pros: can contain Alpha Channel"),
               ('JPEG', "JPEG", "Output image in JPEG format. Uncompressed file format and takes the most amount of data and is the exact representation of the image. \n\nCons: With every edit and resave the image quality will deteriorate.\nPros: lightweight"),
               ('TIFF', "TIFF", "Output image in TIFF format. Photographic file standard in print"),
               ('OPEN_EXR', "EXR", "Output image in EXR format. High-dynamic-range bitmap image file for storing large range of color. Common for Displacement and Normal-like maps"),
               ('PSD', "PSD", "Output image in Photoshop PSD layers. All baked maps with PSD set as file format for current Object will be saved to a single .psd file")],
        update=BM_MAP_PROPS_out_file_format_Update)

    # out_psd_include : bpy.props.EnumProperty(
        # name="PSD includes",
        # description="What maps to put into one PSD file",
        # default='MAP',
        # items=[('MAP', "One map", "Each baked map - separate psd file")],
        # update = BM_ITEM_PROPS_OutputSettings_Update)

    out_exr_codec : bpy.props.EnumProperty(
        name="Codec",
        description="Codec settigns for OpenEXR file format. Choose between lossless and lossy compression",
        default='ZIP',
        items=[('NONE', "None", ""),
               ('PXR24', "Pxr24 (Lossy)", ""),
               ('ZIP', "ZIP (Lossless)", ""),
               ('PIZ', "PIZ (lossless)", ""),
               ('RLE', "RLE (lossless)", ""),
               ('ZIPS', "ZIPS (lossless)", ""),
               ('DWAA', "DWAA (lossy)", ""),
               ('DWAB', "DWAB (lossy)", "")],
        update=BM_MAP_PROPS_out_exr_codec_Update)

    out_compression : bpy.props.IntProperty(
        name="Compression",
        description="0 - no compression performed, raw file size. 100 - full compression, takes more time, but descreases output file size",
        default=15,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=BM_MAP_PROPS_out_compression_Update)

    out_res : bpy.props.EnumProperty(
        name="Map Texture Resolution",
        description="Choose map resolution in pixels from the common ones or set custom",
        default='1024',
        items=[('512', "1/2K (512x512)", ""),
               ('1024', "1K (1024x1024)", ""),
               ('2048', "2K (2048x2048)", ""),
               ('4096', "4K (4096x4096)", ""),
               ('8192', "8K (8192x8192)", ""),
               ('CUSTOM', "Custom", "Enter custom height and width")],
               #('TEXEL', "Texel Density defined", "Define image resolution based on object's texel density")],
        update=BM_MAP_PROPS_out_res_Update)

    out_res_height : bpy.props.IntProperty(
        name="Height",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=BM_MAP_PROPS_out_res_height_Update)

    out_res_width : bpy.props.IntProperty(
        name="Width",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=BM_MAP_PROPS_out_res_width_Update)

    # out_texel_density_value : bpy.props.IntProperty(
        # name="Texel Density",
        # description="How many pixels should be in image per 1 unit (1m) of object's face.\nAutomatically calculated when chosen from Map Resolution List based on object's space relativity to Scene Render Resolution",
        # default=100,
        # min=1,
        # max=65536,
        # subtype='PIXEL',
        # update = BM_ITEM_PROPS_OutputSettings_Update)
    
    # out_texel_density_match : bpy.props.BoolProperty(
        # name="Match to Common",
        # description="Recalculate chosen Texel Density so that the image resolution is set to closest common resolution in Map Resolution List.\n(If checked then, for example, when image res by Texel Density is 1891px, it will be changed to 2048px (common 2K). If unchecked, then wil remain 1891px)",
        # default=True)

    out_margin : bpy.props.IntProperty(
        name="Margin",
        description="Padding. Extend bake result by specified number of pixels as a post-process filter.\nImproves baking quality by reducing hard edges visibility",
        default=16,
        min=0,
        max=64,
        subtype='PIXEL',
        update=BM_MAP_PROPS_out_margin_Update)
    
    out_margin_type : bpy.props.EnumProperty(
        name="Margin Type",
        description="Algorithm for margin",
        default='ADJACENT_FACES',
        items=[('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),
               ('EXTEND', "Extend", "Extend face border pixels outwards")],
        update=BM_MAP_PROPS_out_margin_type_Update)

    out_use_32bit : bpy.props.BoolProperty(
        name="32bit",
        description="Create image texture with 32 bit floating point depth.\nStores more color data in the image this way",
        default=False,
        update=BM_MAP_PROPS_out_use_32bit_Update)

    out_use_alpha : bpy.props.BoolProperty(
        name="Alpha",
        description="Create image texture with Alpha color channel",
        default=False,
        update=BM_MAP_PROPS_out_use_alpha_Update)

    out_use_transbg : bpy.props.BoolProperty(
        name="Transparent BG",
        description="Create image texture with transparent background instead of solid black",
        default=False,
        update=BM_MAP_PROPS_out_use_transbg_Update)
    
    out_udim_start_tile : bpy.props.IntProperty(
        name="UDIM Start Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",
        default=1001,
        min=1001,
        max=2000,
        update=BM_MAP_PROPS_out_udim_start_tile_Update)

    out_udim_end_tile : bpy.props.IntProperty(
        name="UDIM End Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",
        default=1001,
        min=1001,
        max=2000,
        update=BM_MAP_PROPS_out_udim_end_tile_Update)

    out_super_sampling_aa : bpy.props.EnumProperty(
        name="SuperSampling AA",
        description="SSAA. Improve image quality by baking at a higher resolution and then downscaling to a lower resolution. Helps removing stepping, jagging, and dramatic color difference near color area edges",
        default='1X1',
        items=[('1X1', "1x1", "No supersampling. Bake and save with chosen resolution"),
               ('2X2', "2x2", "Bake at 2x the chosen resolution and then downscale"),
               ('4X4', "4x4", "Bake at 4x the chosen resolution and then downscale"),
               ('8X8', "8x8", "Bake at 8x the chosen resolution and then downscale"),
               ('16X16', "16x16", "Bake at 16x the chosen resolution and then downscale")],
        update=BM_MAP_PROPS_out_super_sampling_aa_Update)

    out_samples : bpy.props.IntProperty(
        name="Bake Samples",
        description="Number of samples to render per each pixel",
        default=128,
        min=1,
        max=16777216,
        update=BM_MAP_PROPS_out_samples_Update)
    
    out_use_adaptive_sampling : bpy.props.BoolProperty(
        name="Adaptive Sampling",
        description="Automatically reduce the number of samples per pixel based on estimated noise level",
        default=False,
        update=BM_MAP_PROPS_out_use_adaptive_sampling_Update)

    out_adaptive_threshold : bpy.props.FloatProperty(
        name="Noise Threshold",
        description="Noise level step to stop sampling at, lower values reduce noise at the cost of render time.\nZero for automatic setting based on number of AA sampled",
        default=0.01,
        min=0,
        max=1,
        soft_min=0.001,
        step=3,
        precision=4,
        update=BM_MAP_PROPS_out_adaptive_threshold_Update)

    out_min_samples : bpy.props.IntProperty(
        name="Bake Min Samples",
        description="The minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold",
        default=0,
        min=0,
        max=4096,
        update=BM_MAP_PROPS_out_min_samples_Update)

# Albedo Map Props
    map_ALBEDO_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="ALBEDO",
        update=BM_MAP_PROPS_map_ALBEDO_prefix_Update)

    map_ALBEDO_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_ALBEDO_use_preview_Update)

# Metalness Map Props
    map_METALNESS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="METAL",
        update=BM_MAP_PROPS_map_METALNESS_prefix_Update)

    map_METALNESS_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_METALNESS_use_preview_Update)

# Roughness Map Props
    map_ROUGHNESS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="ROUGH",
        update=BM_MAP_PROPS_map_ROUGHNESS_prefix_Update)

    map_ROUGHNESS_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_ROUGHNESS_use_preview_Update)

# Diffuse Map Props
    map_DIFFUSE_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="DIFFUSE",
        update=BM_MAP_PROPS_map_DIFFUSE_prefix_Update)

    map_DIFFUSE_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_DIFFUSE_use_preview_Update)

# Specular Map Props
    map_SPECULAR_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="SPECULAR",
        update=BM_MAP_PROPS_map_SPECULAR_prefix_Update)

    map_SPECULAR_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_SPECULAR_use_preview_Update)

# Glossiness Map Props
    map_GLOSSINESS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="GLOSS",
        update=BM_MAP_PROPS_map_GLOSSINESS_prefix_Update)

    map_GLOSSINESS_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_GLOSSINESS_use_preview_Update)

# Opacity Map Props
    map_OPACITY_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="OPACITY",
        update=BM_MAP_PROPS_map_OPACITY_prefix_Update)

    map_OPACITY_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_OPACITY_use_preview_Update)

# Emission Map Props
    map_EMISSION_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="EMISSION",
        update=BM_MAP_PROPS_map_EMISSION_prefix_Update)

    map_EMISSION_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_EMISSION_use_preview_Update)

# Pass Map Props
    map_PASS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="BSDFPASS",
        update=BM_MAP_PROPS_map_PASS_prefix_Update)

    map_PASS_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_PASS_use_preview_Update)

    map_pass_type : bpy.props.EnumProperty(
        name="Pass",
        description="Choose BSDF node pass to bake to image texture",
        default='BASE_COLOR',
        items=[('BASE_COLOR', "Base Color", ""),
               ('SS_COLOR', "Subsurface Color", ""),
               ('METALLIC', "Metallic", ""),
               ('SPECULAR', "Specular", ""),
               ('ROUGHNESS', "Roughness", ""),
               ('ANISOTROPIC', "Anisotropic", ""),
               ('SHEEN', "Sheen", ""),
               ('CLEARCOAT', "Clearcoat", ""),
               ('IOR', "IOR", ""),
               ('TRANSMISSION', "Transmission", ""),
               ('EMISSION', "Emission", ""),
               ('ALPHA', "Alpha", ""),
               ('NORMAL', "Normal", "")],
        update=BM_MAP_PROPS_map_pass_type_Update)

# Decal Pass Map Props
    map_DECAL_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="DECAL",
        update=BM_MAP_PROPS_map_DECAL_prefix_Update)

    map_DECAL_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_DECAL_use_preview_Update)
    
    map_decal_pass_type : bpy.props.EnumProperty(
        name="Pass Type",
        description="Decal Map pass type to bake",
        default='NORMAL',
        items=[('NORMAL', "Normal", "Normals Pass using MatCap"),
               ('HEIGHT', "Height", "How high mesh parts are from the world ground level"),
               ('OPACITY', "Opacity", "Decal Object - white, empty space - black")],
        update=BM_MAP_PROPS_map_decal_pass_type_Update)

    map_decal_height_opacity_invert : bpy.props.BoolProperty(
        name="Invert",
        description="Invert colors of the map",
        default=False,
        update=BM_MAP_PROPS_map_decal_height_opacity_invert_Update)

    map_decal_normal_preset : bpy.props.EnumProperty(
        name="Preset",
        description="Decal Map Normal Pass preset for different software for correct result when used in that software",
        default='BLENDER',
        items=[('CUSTOM', "Custom", "Choose custom algorithm"),
               ('BLENDER', "Blender", "Blender uses OpenGL format"),
               ('3DS_MAX', "3DS Max", "3DS Max uses DirectX format"),
               ('CORONA', "Corona", "Corona uses DirectX format"),
               ('CRYENGINE', "CryEngine", "CryEngine uses DirectX format"),
               ('SUBSTANCE_PAINTER', "Substance Painter", "Substance Painter uses DirectX format"),
               ('UNREAL_ENGINE', "Unreal Engine", "Unreal Engine uses DirectX format"),
               ('CINEMA_4D', "Cinema 4D", "Cinema 4D uses OpenGL format"),
               ('ARNOLD', "Arnold", "Arnold uses OpenGL format"),
               ('HOUDINI', "Houdini", "Houdini uses OpenGL format"),
               ('MARMOSET_TOOLBAG', "Marmoset Toolbag", "Marmoset Toolbag uses OpenGL format"),
               ('MAYA', "Maya", "Maya uses OpenGL format"),
               ('OCTANE', "Octane", "Octane uses OpenGL format"),
               ('REDSHIFT', "Redshift", "Redshift uses OpenGL format"),
               ('UNITY', "Unity", "Unity uses OpenGL format"),
               ('VRAY', "VRay", "VRay uses OpenGL format"),
               ('ZBRUSH', "ZBrush", "ZBrush uses OpenGL format")],
        update=BM_MAP_PROPS_map_decal_normal_preset_Update)
    
    map_decal_normal_custom_preset : bpy.props.EnumProperty(
        name="Custom Format",
        description="Decal Map Normal Pass format (Green channel is inverted)",
        default='OPEN_GL',
        items=[('OPEN_GL', "OpenGL", "OpenGL Normal Map format. Green Channel Axis is +Y"),
               ('DIRECTX', "DirectX", "DirectX Normal Map format. Green Channel Axis is -Y"),
               ('CUSTOM', "Custom", "Set custom axes for channels")],
        update=BM_MAP_PROPS_map_decal_normal_custom_preset_Update)

    map_decal_normal_r : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "red",
        default='POS_X',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_decal_normal_r_Update)

    map_decal_normal_g : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "green",
        default='POS_Y',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_decal_normal_g_Update)

    map_decal_normal_b : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "blue",
        default='POS_Z',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_decal_normal_b_Update)

# Vertex Color Layer Map Props
    map_VERTEX_COLOR_LAYER_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="VERTEXCOLOR",
        update=BM_MAP_PROPS_map_VERTEX_COLOR_LAYER_prefix_Update)

    map_VERTEX_COLOR_LAYER_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_VERTEX_COLOR_LAYER_use_preview_Update)

    map_vertexcolor_layer : bpy.props.EnumProperty(
        name="Layer",
        description="Vertex Color Layer to bake",
        items=BM_MAP_PROPS_map_vertexcolor_layer_Items,
        update=BM_MAP_PROPS_map_vertexcolor_layer_Update)
    
# Cycles Map Props 
    map_C_COMBINED_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="COMBINED",
        update=BM_MAP_PROPS_map_C_COMBINED_prefix_Update)

    map_C_AO_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="AO",
        update=BM_MAP_PROPS_map_C_AO_prefix_Update)

    map_C_SHADOW_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="SHADOW",
        update=BM_MAP_PROPS_map_C_SHADOW_prefix_Update)

    map_C_NORMAL_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="NORMAL",
        update=BM_MAP_PROPS_map_C_NORMAL_prefix_Update)

    map_C_UV_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="UV",
        update=BM_MAP_PROPS_map_C_UV_prefix_Update)

    map_C_ROUGHNESS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="ROUGH",
        update=BM_MAP_PROPS_map_C_ROUGHNESS_prefix_Update)

    map_C_EMIT_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="EMIT",
        update=BM_MAP_PROPS_map_C_EMIT_prefix_Update)

    map_C_ENVIRONMENT_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="ENV",
        update=BM_MAP_PROPS_map_C_ENVIRONMENT_prefix_Update)

    map_C_DIFFUSE_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="DIFFUSE",
        update=BM_MAP_PROPS_map_C_DIFFUSE_prefix_Update)

    map_C_GLOSSY_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="GLOSS",
        update=BM_MAP_PROPS_map_C_GLOSSY_prefix_Update)

    map_C_TRANSMISSION_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="TRANS",
        update=BM_MAP_PROPS_map_C_TRANSMISSION_prefix_Update)

    map_cycles_use_pass_direct : bpy.props.BoolProperty(
        name="Direct",
        description="Add direct lighting contribution",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_direct_Update)
    
    map_cycles_use_pass_indirect : bpy.props.BoolProperty(
        name="Indirect",
        description="Add indirect lighting contribution",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_indirect_Update)

    map_cycles_use_pass_color : bpy.props.BoolProperty(
        name="Color",
        description="Color the pass",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_color_Update)
    
    map_cycles_use_pass_diffuse : bpy.props.BoolProperty(
        name="Diffuse",
        description="Add %s contribution" % "Diffuse",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_diffuse_Update)

    map_cycles_use_pass_glossy : bpy.props.BoolProperty(
        name="Glossy",
        description="Add %s contribution" % "Glossy",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_glossy_Update)

    map_cycles_use_pass_transmission : bpy.props.BoolProperty(
        name="Transmission",
        description="Add %s contribution" % "Transmission",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_transmission_Update)

    map_cycles_use_pass_ambient_occlusion : bpy.props.BoolProperty(
        name="Ambient Occlusion",
        description="Add %s contribution" % "Ambient Occlusion",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_ambient_occlusion_Update)

    map_cycles_use_pass_emit : bpy.props.BoolProperty(
        name="Emit",
        description="Add %s contribution" % "Emit",
        default=True,
        update=BM_MAP_PROPS_map_cycles_use_pass_emit_Update)

# Normal Map Props
    map_NORMAL_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="NORMAL",
        update=BM_MAP_PROPS_map_NORMAL_prefix_Update)

    map_NORMAL_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_NORMAL_use_preview_Update)

    map_normal_data : bpy.props.EnumProperty(
        name="Data",
        description="Data for Normal map",
        items=BM_MAP_PROPS_map_normal_data_Items,
        update=BM_MAP_PROPS_map_normal_data_Update)

    map_normal_space : bpy.props.EnumProperty(
        name="Normal Space",
        description="Choose normal space for baking",
        default='TANGENT',
        items=[('TANGENT', "Tangent", "Blue colors. Tangent space normal map"),
               ('OBJECT', "Object", "Rainbow colors. Object space normal map with local coordinates")],
        update=BM_MAP_PROPS_map_normal_space_Update)

    map_normal_preset : bpy.props.EnumProperty(
        name="Preset",
        description="Normal Map preset for different software for correct result when used in that software",
        default='BLENDER',
        items=[('CUSTOM', "Custom", "Choose custom algorithm"),
               ('BLENDER', "Blender", "Blender uses OpenGL format"),
               ('3DS_MAX', "3DS Max", "3DS Max uses DirectX format"),
               ('CORONA', "Corona", "Corona uses DirectX format"),
               ('CRYENGINE', "CryEngine", "CryEngine uses DirectX format"),
               ('SUBSTANCE_PAINTER', "Substance Painter", "Substance Painter uses DirectX format"),
               ('UNREAL_ENGINE', "Unreal Engine", "Unreal Engine uses DirectX format"),
               ('CINEMA_4D', "Cinema 4D", "Cinema 4D uses OpenGL format"),
               ('ARNOLD', "Arnold", "Arnold uses OpenGL format"),
               ('HOUDINI', "Houdini", "Houdini uses OpenGL format"),
               ('MARMOSET_TOOLBAG', "Marmoset Toolbag", "Marmoset Toolbag uses OpenGL format"),
               ('MAYA', "Maya", "Maya uses OpenGL format"),
               ('OCTANE', "Octane", "Octane uses OpenGL format"),
               ('REDSHIFT', "Redshift", "Redshift uses OpenGL format"),
               ('UNITY', "Unity", "Unity uses OpenGL format"),
               ('VRAY', "VRay", "VRay uses OpenGL format"),
               ('ZBRUSH', "ZBrush", "ZBrush uses OpenGL format")],
        update=BM_MAP_PROPS_map_normal_preset_Update)
    
    map_normal_custom_preset : bpy.props.EnumProperty(
        name="Custom Format",
        description="Normal Map format (Green channel is inverted)",
        default='OPEN_GL',
        items=[('OPEN_GL', "OpenGL", "OpenGL Normal Map format. Green Channel Axis is +Y"),
               ('DIRECTX', "DirectX", "DirectX Normal Map format. Green Channel Axis is -Y"),
               ('CUSTOM', "Custom", "Set custom axes for channels")],
        update=BM_MAP_PROPS_map_normal_custom_preset_Update)

    map_normal_r : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "red",
        default='POS_X',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_normal_r_Update)

    map_normal_g : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "green",
        default='POS_Y',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_normal_g_Update)

    map_normal_b : bpy.props.EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "blue",
        default='POS_Z',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=BM_MAP_PROPS_map_normal_b_Update)

# Displacement Map Props
    map_DISPLACEMENT_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="DISP",
        update=BM_MAP_PROPS_map_DISPLACEMENT_prefix_Update)

    map_DISPLACEMENT_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_DISPLACEMENT_use_preview_Update)

    map_displacement_data : bpy.props.EnumProperty(
        name="Data",
        description="Data for Displacement map",
        items=BM_MAP_PROPS_map_displacement_data_Items,
        update=BM_MAP_PROPS_map_displacement_data_Update)
    
    map_displacement_result : bpy.props.EnumProperty(
        name="Result to",
        description="How to apply baked displacement map",
        default="MODIFIER",
        items=[('MODIFIER', "Modifiers", "Add displace modifier to the object with bake displacement displace texture"),
               ('MATERIAL', "Material Displacement", "Add baked displacement to every object material displacement socket")],
        update=BM_MAP_PROPS_map_displacement_result_Update)

    map_displacement_subdiv_levels : bpy.props.IntProperty(
        name="Subdivision Levels",
        description="The subdivision level defines the level of details.\nThe lower - the faster, but less details",
        default=1,
        min=1,
        max=10,
        update=BM_MAP_PROPS_map_displacement_subdiv_levels_Update)
    
# Vector Displacement Map Props
    map_VECTOR_DISPLACEMENT_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="VD",
        update=BM_MAP_PROPS_map_VECTOR_DISPLACEMENT_prefix_Update)

    map_VECTOR_DISPLACEMENT_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_VECTOR_DISPLACEMENT_use_preview_Update)
    
    map_vector_displacement_use_negative : bpy.props.BoolProperty(
        name="Include Negative",
        description="Remap color values to include negative values for displacement",
        default=False,
        update=BM_MAP_PROPS_map_vector_displacement_use_negative_Update)

    map_vector_displacement_result : bpy.props.EnumProperty(
        name="Result to",
        description="How to apply baked displacement map",
        default="MODIFIER",
        items=[('MODIFIER', "Modifiers", "Add displace modifier to the object with bake vector displacement displace texture"),
               ('MATERIAL', "Material Displacement", "Add baked vector displacement to every object material displacement socket")],
        update=BM_MAP_PROPS_map_vector_displacement_result_Update)

    map_vector_displacement_subdiv_levels : bpy.props.IntProperty(
        name="Subdivision Levels",
        description="The subdivision level defines the level of details.\nThe lower - the faster, but less details",
        default=1,
        min=1,
        max=10,
        update=BM_MAP_PROPS_map_vector_displacement_subdiv_levels_Update)

# Position Map Props
    map_POSITION_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="POS",
        update=BM_MAP_PROPS_map_POSITION_prefix_Update)

    map_POSITION_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_POSITION_use_preview_Update)

# AO Map Props
    map_AO_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="AO",
        update=BM_MAP_PROPS_map_AO_prefix_Update)

    map_AO_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_AO_use_preview_Update)

    map_AO_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_AO_use_default_Update)
    
    map_ao_samples: bpy.props.IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",
        default=16,
        min=1,
        max=128,
        update=BM_MAP_PROPS_map_ao_samples_Update)

    map_ao_distance : bpy.props.FloatProperty(
        name="Distance",
        description="Distance up to which other objects are considered to occlude the shading point",
        default=1,
        min=0,
        update=BM_MAP_PROPS_map_ao_distance_Update)

    map_ao_black_point : bpy.props.FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_ao_black_point_Update)

    map_ao_white_point : bpy.props.FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",
        default=0.8,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_ao_white_point_Update)

    map_ao_brightness : bpy.props.FloatProperty(
        name="Brightness",
        default=-0.3,
        min=-100.0,
        max=100.0,
        update=BM_MAP_PROPS_map_ao_brightness_Update)

    map_ao_contrast : bpy.props.FloatProperty(
        name="Contrast", 
        default=0.3,
        min=-100.0,
        max=100.0,
        update=BM_MAP_PROPS_map_ao_contrast_Update)

    map_ao_opacity : bpy.props.FloatProperty(
        name="Opacity", 
        default=0.67,
        min=0.0,
        max=1.0,
        update=BM_MAP_PROPS_map_ao_opacity_Update)

    map_ao_use_local : bpy.props.BoolProperty(
        name="Only Local",
        description="Only detect occlusion from the object itself, and not others",
        default=False,
        update=BM_MAP_PROPS_map_ao_use_local_Update)

    map_ao_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_ao_use_invert_Update)

# Cavity Map Props
    map_CAVITY_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="CAV",
        update=BM_MAP_PROPS_map_CAVITY_prefix_Update)

    map_CAVITY_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_CAVITY_use_preview_Update)

    map_CAVITY_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_CAVITY_use_default_Update)

    map_cavity_black_point : bpy.props.FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0.0,
        max=1.0,
        precision=3,
        update=BM_MAP_PROPS_map_cavity_black_point_Update)
    
    map_cavity_white_point : bpy.props.FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",
        default=1,
        min=0.0,
        max=1.0,
        precision=3,
        update=BM_MAP_PROPS_map_cavity_white_point_Update)
    
    map_cavity_power : bpy.props.FloatProperty(
        name="Power",
        description="Cavity map power value", 
        default=2.5,
        update=BM_MAP_PROPS_map_cavity_power_Update)
        
    map_cavity_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_cavity_use_invert_Update)

# Curvature Map Props
    map_CURVATURE_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="CURV",
        update=BM_MAP_PROPS_map_CURVATURE_prefix_Update)

    map_CURVATURE_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_CURVATURE_use_preview_Update)

    map_CURVATURE_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_CURVATURE_use_default_Update)
    
    map_curv_samples: bpy.props.IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",
        default=16,
        min=2,
        max=128,
        update=BM_MAP_PROPS_map_curv_samples_Update)
    
    map_curv_radius : bpy.props.FloatProperty(
        name="Radius",
        default=2.2,
        min=0,
        precision=3,
        update=BM_MAP_PROPS_map_curv_radius_Update)

    map_curv_black_point : bpy.props.FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0.4,
        min=0.0,
        max=1.0,
        precision=3,
        update=BM_MAP_PROPS_map_curv_black_point_Update)
    
    map_curv_mid_point : bpy.props.FloatProperty(
        name="Greys",
        description="Middle grey point location on the map color gradient spectrum",
        default=0.5,
        min=0.0,
        max=1.0,
        precision=3,
        update=BM_MAP_PROPS_map_curv_mid_point_Update)

    map_curv_white_point : bpy.props.FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",
        default=0.6,
        min=0.0,
        max=1.0,
        precision=3,
        update=BM_MAP_PROPS_map_curv_white_point_Update)

    map_curv_body_gamma : bpy.props.FloatProperty(
        name="Gamma",
        default=2.2,
        min=0.001,
        max=10,
        precision=3,
        update=BM_MAP_PROPS_map_curv_body_gamma_Update)

# Thickness Map Props
    map_THICKNESS_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="THICK",
        update=BM_MAP_PROPS_map_THICKNESS_prefix_Update)

    map_THICKNESS_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_THICKNESS_use_preview_Update)

    map_THICKNESS_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_THICKNESS_use_default_Update)
    
    map_thick_samples : bpy.props.IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",
        default=16,
        min=1,
        max=128,
        update=BM_MAP_PROPS_map_thick_samples_Update)

    map_thick_distance : bpy.props.FloatProperty(
        name="Distance",
        description="Distance up to which other objects are considered to occlude the shading point",
        default=1,
        min=0,
        update=BM_MAP_PROPS_map_thick_distance_Update)

    map_thick_black_point : bpy.props.FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_thick_black_point_Update)

    map_thick_white_point : bpy.props.FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",
        default=1,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_thick_white_point_Update)

    map_thick_brightness : bpy.props.FloatProperty(
        name="Brightness", 
        default=1,
        update=BM_MAP_PROPS_map_thick_brightness_Update)

    map_thick_contrast : bpy.props.FloatProperty(
        name="Contrast", 
        default=0,
        update=BM_MAP_PROPS_map_thick_contrast_Update)

    map_thick_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_thick_use_invert_Update)

# Material ID Map Props
    map_ID_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="ID",
        update=BM_MAP_PROPS_map_ID_prefix_Update)

    map_ID_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_ID_use_preview_Update)

    map_matid_data : bpy.props.EnumProperty(
        name="Data",
        description="Data type for detecting color groups",
        default='MATERIALS',
        items=[('VERTEX_GROUPS', "Vertex Groups", "Color each mesh Vertex Groups differently"),
               ('MATERIALS', "Materials", "Color each mesh part each material assigned to differently"),
               ('MESH_ISLANDS', "Mesh Islands", "Color each mesh part differently")],
        update=BM_MAP_PROPS_map_matid_data_Update)

    map_matid_vertex_groups_name_contains : bpy.props.StringProperty(
        name="Name Contains",
        description="Use only those vertex groups which name contains this. Leave empty to use all vertex groups",
        default="_id",
        update=BM_MAP_PROPS_map_matid_vertex_groups_name_contains_Update)
    
    map_matid_algorithm : bpy.props.EnumProperty(
        name="Algorithm",
        description="Algorithm by which the color groups will be painted",
        default='RANDOM',
        items=[('RANDOM', "Random", "Color each group by unique Random Color"),
               ('HUE', "Hue Shift", "Color each group by unique Hue"),
               ('GRAYSCALE', "Grayscale", "Color each group by unique Grayscale Color")],
        update=BM_MAP_PROPS_map_matid_algorithm_Update)

# Mask Map Props
    map_MASK_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="MASK",
        update=BM_MAP_PROPS_map_MASK_prefix_Update)

    map_MASK_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_MASK_use_preview_Update)

    map_mask_data : bpy.props.EnumProperty(
        name="Data",
        description="Data type for detecting mask black and white parts",
        default='SELECTION',
        items=[('SELECTION', "Selection", "Color selected mesh faces in one color, unselected in another"),
               ('VERTEX_GROUPS', "Vertex Groups", "Color specified vertex groups in one color, other in another"),
               ('MATERIALS', "Materials", "Color specified object materials in one color, other in another")],
        update=BM_MAP_PROPS_map_mask_data_Update)
    
    map_mask_vertex_groups_name_contains : bpy.props.StringProperty(
        name="Name Contains",
        description="Use only those vertex groups which names contain this. Leave empty to use all vertex groups",
        default="_mask",
        update=BM_MAP_PROPS_map_mask_vertex_groups_name_contains_Update)

    map_mask_materials_name_contains : bpy.props.StringProperty(
        name="Name Contains",
        description="Use only those object materials which names contain this. Leave empty to use all vertex groups",
        default="_mask",
        update=BM_MAP_PROPS_map_mask_materials_name_contains_Update)
    
    map_mask_color1 : bpy.props.FloatVectorProperty(
        name="Color1",
        description="What color to use as Color1 for masking",
        default=(0, 0, 0),
        size=3,
        min=0,
        max=1,
        precision=3,
        subtype='COLOR',
        update=BM_MAP_PROPS_map_mask_color1_Update)

    map_mask_color2 : bpy.props.FloatVectorProperty(
        name="Color2",
        description="What color to use as Color2 for masking",
        default=(1, 1, 1),
        size=3,
        min=0,
        max=1,
        precision=3,
        subtype='COLOR',
        update=BM_MAP_PROPS_map_mask_color2_Update)
        
    map_mask_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_mask_use_invert_Update)

# XYZMask Map Props
    map_XYZMASK_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="XYZ",
        update=BM_MAP_PROPS_map_XYZMASK_prefix_Update)

    map_XYZMASK_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_XYZMASK_use_preview_Update)

    map_XYZMASK_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_XYZMASK_use_default_Update)

    map_xyzmask_use_x : bpy.props.BoolProperty(
        name="X",
        description="Enable/disable X coordinate mask filter",
        default=False,
        update=BM_MAP_PROPS_map_xyzmask_use_x_Update)

    map_xyzmask_use_y : bpy.props.BoolProperty(
        name="Y",
        description="Enable/disable Y coordinate mask filter",
        default=False,
        update=BM_MAP_PROPS_map_xyzmask_use_y_Update)

    map_xyzmask_use_z : bpy.props.BoolProperty(
        name="Z",
        description="Enable/disable Z coordinate mask filter",
        default=False,
        update=BM_MAP_PROPS_map_xyzmask_use_z_Update)

    map_xyzmask_coverage : bpy.props.FloatProperty(
        name="Coverage",
        default=0,
        precision=3,
        update=BM_MAP_PROPS_map_xyzmask_coverage_Update)

    map_xyzmask_saturation : bpy.props.FloatProperty(
        name="Saturation",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_xyzmask_saturation_Update)

    map_xyzmask_opacity : bpy.props.FloatProperty(
        name="Opacity",
        default=1,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_xyzmask_opacity_Update)

    map_xyzmask_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=1,
        min=-1,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_xyzmask_use_invert_Update)

# GradientMask Map Props
    map_GRADIENT_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="GRADIENT",
        update=BM_MAP_PROPS_map_GRADIENT_prefix_Update)

    map_GRADIENT_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_GRADIENT_use_preview_Update)

    map_GRADIENT_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_GRADIENT_use_default_Update)

    map_gmask_type : bpy.props.EnumProperty(
        name="Type",
        description="Style of color blending",
        items=[("LINEAR", "Linear", "Create a linear progression"),
                 ("QUADRATIC", "Quadratic", "Create a quadratic progression"),
                 ("EASING", "Easing", "Create progression easing from one step to the next"),
                 ("DIAGONAL", "Diagonal", "Create a diagonal progression"),
                 ("SPHERICAL", "Spherical", "Create a spherical progression"),
                 ("QUADRATIC_SPHERE", "Quadratic Sphere", "Create a quadratic progression in the shape of a sphere"),
                 ("RADIAL", "Radial", "Create a radial progression")],
        update=BM_MAP_PROPS_map_gmask_type_Update)
    
    map_gmask_location_x : bpy.props.FloatProperty(
        name="X Location",
        description="Gradient location by the local axis X",
        default=0,
        precision=3,
        subtype="DISTANCE",
        update=BM_MAP_PROPS_map_gmask_location_x_Update)

    map_gmask_location_y : bpy.props.FloatProperty(
        name="Y Location",
        description="Gradient location by the local axis Y",
        default=0,
        precision=3,
        subtype="DISTANCE",
        update=BM_MAP_PROPS_map_gmask_location_y_Update)

    map_gmask_location_z : bpy.props.FloatProperty(
        name="Z Location",
        description="Gradient location by the local axis Z",
        default=0, 
        precision=3,
        subtype="DISTANCE",
        update=BM_MAP_PROPS_map_gmask_location_z_Update)

    map_gmask_rotation_x : bpy.props.FloatProperty(
        name="X Rotation",
        description="Gradient rotation by the local axis X",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=BM_MAP_PROPS_map_gmask_rotation_x_Update)

    map_gmask_rotation_y : bpy.props.FloatProperty(
        name="Y Rotation",
        description="Gradient rotation by the local axis Y",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=BM_MAP_PROPS_map_gmask_rotation_y_Update)

    map_gmask_rotation_z : bpy.props.FloatProperty(
        name="Z Rotation",
        description="Gradient rotation by the local axis Z",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=BM_MAP_PROPS_map_gmask_rotation_z_Update)

    map_gmask_scale_x : bpy.props.FloatProperty(
        name="X Scale",
        description="Smoothness. Gradient scale by the local axis X",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_scale_x_Update)

    map_gmask_scale_y : bpy.props.FloatProperty(
        name="Y Scale",
        description="Smoothness. Gradient scale by the local axis Y",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_scale_y_Update)

    map_gmask_scale_z : bpy.props.FloatProperty(
        name="Z Scale",
        description="Smoothness. Gradient scale by the local axis Z",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_scale_z_Update)
    
    map_gmask_coverage : bpy.props.FloatProperty(
        name="Range of coverage",
        default=0,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_coverage_Update)

    map_gmask_contrast : bpy.props.FloatProperty(
        name="Contrast",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_contrast_Update)

    map_gmask_saturation : bpy.props.FloatProperty(
        name="Saturation", 
        default=1,
        update=BM_MAP_PROPS_map_gmask_saturation_Update)

    map_gmask_opacity : bpy.props.FloatProperty(
        name="Opacity", 
        default=1,
        min=0,
        max=1,
        update=BM_MAP_PROPS_map_gmask_opacity_Update)

    map_gmask_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_gmask_use_invert_Update)

# Edge Map Props
    map_EDGE_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="EDGE",
        update=BM_MAP_PROPS_map_EDGE_prefix_Update)

    map_EDGE_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_EDGE_use_preview_Update)

    map_EDGE_use_default : bpy.props.BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=BM_MAP_PROPS_map_EDGE_use_default_Update)
    
    map_edgemask_samples: bpy.props.IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",
        default=16,
        min=2,
        max=128,
        update=BM_MAP_PROPS_map_edgemask_samples_Update)

    map_edgemask_radius : bpy.props.FloatProperty(
        name="Radius",
        default=0.02,
        min=0,
        precision=3,
        update=BM_MAP_PROPS_map_edgemask_radius_Update)

    map_edgemask_edge_contrast : bpy.props.FloatProperty(
        name="Edge Contrast",
        default=0,
        precision=3,
        update=BM_MAP_PROPS_map_edgemask_edge_contrast_Update)

    map_edgemask_body_contrast : bpy.props.FloatProperty(
        name="Body Contrast",
        default=1,
        precision=3,
        update=BM_MAP_PROPS_map_edgemask_body_contrast_Update)

    map_edgemask_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=1,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_edgemask_use_invert_Update)

# WireframeMask Map Props
    map_WIREFRAME_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",
        default="WIRE",
        update=BM_MAP_PROPS_map_WIREFRAME_prefix_Update)

    map_WIREFRAME_use_preview : bpy.props.BoolProperty(
        name="Preview",
        description=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default=False,
        update=BM_MAP_PROPS_map_WIREFRAME_use_preview_Update)

    map_wireframemask_line_thickness : bpy.props.FloatProperty(
        name="Thickness",
        description="Thickness of uv edge",
        default=0.2,
        min=0,
        update=BM_MAP_PROPS_map_wireframemask_line_thickness_Update)

    map_wireframemask_use_invert : bpy.props.FloatProperty(
        name="Invert",
        description="Invert colors of the map", 
        default=0,
        min=0,
        max=1,
        precision=3,
        update=BM_MAP_PROPS_map_wireframemask_use_invert_Update)

###################################################################
### OBJECT PROPS ###
###################################################################

class BM_Object_Highpoly(bpy.types.PropertyGroup):
    global_object_name : bpy.props.EnumProperty(
        name="Highpoly",
        description="Choose Highpoly for the Object from the list\n(Highpoly should be added to BakeMaster Table of Objects)",
        items=BM_ITEM_PROPS_hl_highpoly_Items,
        update=BM_ITEM_PROPS_hl_highpoly_Update)
    
    global_item_index : bpy.props.IntProperty()

    global_highpoly_name_old : bpy.props.StringProperty()

    global_highpoly_object_index : bpy.props.IntProperty(default=-1)

    global_highpoly_object_include : bpy.props.StringProperty(default="")

class BM_Object_ChannelPack(bpy.types.PropertyGroup):
    global_channelpack_name : bpy.props.StringProperty(
        name="Pack Name",
        description="Enter a Channel Pack name",
        default="ChannelPack")
    
    global_channelpack_index : bpy.props.IntProperty()

    global_channelpack_type : bpy.props.EnumProperty(
        name="Pack Type",
        description="Type of packing operation describing its packing format",
        default='R1G1B1A',
        items=[('R1G1B', "R+G+B", "Select different maps for R, G, B channels"),
               ('RGB1A', "RGB+A", "Select one map to cover RGB, another for A channel"),
               ('R1G1B1A', "R+G+B+A", "Select different maps for R, G, B, A channels")])

    # R+G+B
    R1G1B_use_R : bpy.props.BoolProperty(
        name="Use Red Channel",
        default=True)
    R1G1B_map_R : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Red channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B_R,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B_R)
    R1G1B_map_R_index : bpy.props.IntProperty(default=-1)
    
    R1G1B_use_G : bpy.props.BoolProperty(
        name="Use Green Channel",
        default=True)
    R1G1B_map_G : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Green channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B_G,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B_G)
    R1G1B_map_G_index : bpy.props.IntProperty(default=-1)
        
    R1G1B_use_B : bpy.props.BoolProperty(
        name="Use Blue Channel",
        default=True)
    R1G1B_map_B : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Blue channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B_B,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B_B)
    R1G1B_map_B_index : bpy.props.IntProperty(default=-1)

    # RGB+A
    RGB1A_use_RGB : bpy.props.BoolProperty(
        name="Use RGB Channels",
        default=True)
    RGB1A_map_RGB : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the RGB channels among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_RGB1A_RGB,
        update=BM_CHANNELPACK_PROPS_map_Update_RGB1A_RGB)
    RGB1A_map_RGB_index : bpy.props.IntProperty(default=-1)

    RGB1A_use_A : bpy.props.BoolProperty(
        name="Use Alpha Channel",
        default=True)
    RGB1A_map_A : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Alpha channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_RGB1A_A,
        update=BM_CHANNELPACK_PROPS_map_Update_RGB1A_A)
    RGB1A_map_A_index : bpy.props.IntProperty(default=-1)

    # R+G+B+A
    R1G1B1A_use_R : bpy.props.BoolProperty(
        name="Use Red Channel",
        default=True)
    R1G1B1A_map_R : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Red channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_R,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_R)
    R1G1B1A_map_R_index : bpy.props.IntProperty(default=-1)
    
    R1G1B1A_use_G : bpy.props.BoolProperty(
        name="Use Green Channel",
        default=True)
    R1G1B1A_map_G : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Green channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_G,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_G)
    R1G1B1A_map_G_index : bpy.props.IntProperty(default=-1)
        
    R1G1B1A_use_B : bpy.props.BoolProperty(
        name="Use Blue Channel",
        default=True)
    R1G1B1A_map_B : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Blue channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_B,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_B)
    R1G1B1A_map_B_index : bpy.props.IntProperty(default=-1)

    R1G1B1A_use_A : bpy.props.BoolProperty(
        name="Use Alpha Channel",
        default=True)
    R1G1B1A_map_A : bpy.props.EnumProperty(
        name="Channel Map",
        description="Choose a map for the Alpha channel among added to the table of maps",
        items=BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_A,
        update=BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_A)
    R1G1B1A_map_A_index : bpy.props.IntProperty(default=-1)

# class BM_Object_BatchNamingKeyword(bpy.types.PropertyGroup):
#     global_keyword : bpy.props.EnumProperty(
#         name="Keyword Type",
#         description="Choose keyword type for this keyword",
#         items=BM_BATCHNAMINGKEY_PROPS_global_keyword_Items,
#         update=BM_BATCHNAMINGKEY_PROPS_global_keyword_Update)

#     global_keyword_index : bpy.props.IntProperty()
    
#     global_keyword_old : bpy.props.StringProperty(default="")
    
#     global_use_caps : bpy.props.BoolProperty(
#         name="Use Caps",
#         description="Use capital letters for this keyword",
#         default=False)

#     mapres_use_k : bpy.props.BoolProperty(
#         name="K Resolution",
#         description="If possible, write resolution in K-format, if not then leave in pixels.\nIf checked, 256 -> 256, 1024 -> 1K, 4096 -> 4K, 7452 -> 7452\nIf unchecked, 256 -> 256, 1024 -> 1024, 4096 -> 4096, 7452 -> 7452",
#         default=False)

#     maptrans_custom : bpy.props.StringProperty(
#         name="Write:",
#         description="What to write if map uses transparent background",
#         default="trans")

#     mapdenoise_custom : bpy.props.StringProperty(
#         name="Write:",
#         description="What to write if map was denoised",
#         default="denoised")
    
#     autouv_custom : bpy.props.StringProperty(
#         name="Write:",
#         description="What to write if object was auto uv unwrapped",
        # default="autouv")
    
class BM_Object(bpy.types.PropertyGroup):
    global_object_name : bpy.props.StringProperty()

    global_use_bake : bpy.props.BoolProperty(
        name="Include/Exclude the object for bake",
        default=True,
        update=BM_ITEM_PROPS_global_use_bake_Update)

    global_is_included_in_texset : bpy.props.BoolProperty()
    
# Name matching props:
    nm_is_detached : bpy.props.BoolProperty(default=False)
    nm_master_index : bpy.props.IntProperty(default=-1)
    nm_container_name : bpy.props.StringProperty(default="", update=BM_ITEM_PROPS_nm_container_name_Update)
    nm_container_name_old : bpy.props.StringProperty(default="")
    nm_this_indent : bpy.props.IntProperty(default=0)
    nm_is_universal_container : bpy.props.BoolProperty(default=False)
    nm_is_local_container : bpy.props.BoolProperty(default=False)
    nm_is_expanded : bpy.props.BoolProperty(default=True)
    nm_item_uni_container_master_index : bpy.props.IntProperty(default=-1)
    nm_item_local_container_master_index : bpy.props.IntProperty(default=-1)
    nm_is_lowpoly_container : bpy.props.BoolProperty(default=False)
    nm_is_highpoly_container : bpy.props.BoolProperty(default=False)
    nm_is_cage_container : bpy.props.BoolProperty(default=False)

    nm_uni_container_is_global : bpy.props.BoolProperty(
        name="Is Global Container",
        description="If checked, all Container's Objects settings will be configured by Container settings",
        default=False,
        update=BM_ITEM_PROPS_nm_uni_container_is_global_Update)

# Item Decal Props:
    decal_is_decal : bpy.props.BoolProperty(
        name="Decal Object",
        description="Set the current Object to be Decal Object",
        default=False,
        update=BM_ITEM_PROPS_decal_is_decal_Update)

    decal_use_custom_camera : bpy.props.BoolProperty(
        name="Use Custom Camera",
        description="Use Custom Camera Object for capturing and baking decal maps",
        default=False,
        update=BM_ITEM_PROPS_decal_use_custom_camera_Update)
    
    decal_custom_camera : bpy.props.PointerProperty(
        name="Camera",
        description="Choose Camera Object",
        type=bpy.types.Camera,
        update=BM_ITEM_PROPS_decal_custom_camera_Update)

    decal_upper_coordinate : bpy.props.EnumProperty(
        name="Upper Coordinate",
        description="Choose coordinate specifying where the decal's top is",
        default='+Z',
        items=[('+X', "+X", ""),
               ('+Y', "+Y", ""),
               ('+Z', "+Z", ""),
               ('-X', "-X", ""),
               ('-Y', "-Y", ""),
               ('-Z', "-Z", "")],
        update=BM_ITEM_PROPS_decal_upper_coordinate_Update)

    decal_boundary_offset : bpy.props.FloatProperty(
        name="Boundary Offset",
        description="Distance to use between decal object's bounds and captured image area bounds",
        default=0.1,
        min=0,
        max=1,
        update=BM_ITEM_PROPS_decal_boundary_offset_Update)

# Item High to Lowpoly props:
    hl_use_unique_per_map : bpy.props.BoolProperty(
        name="Unique per map",
        description="Set unqiue High to Lowpoly Settings for each map",
        default=False,
        update=BM_ITEM_PROPS_hl_use_unique_per_map_Update)
    
    hl_is_highpoly : bpy.props.BoolProperty(default=False)
    hl_is_lowpoly : bpy.props.BoolProperty(default=False)
    hl_is_cage : bpy.props.BoolProperty(default=False)

    hl_is_decal : bpy.props.BoolProperty(
        name="Decal",
        description="Mark the current Highpoly as a Decal Object for the Lowpoly",
        default=False)

    hl_highpoly_table : bpy.props.CollectionProperty(type=BM_Object_Highpoly)

    hl_highpoly_table_active_index : bpy.props.IntProperty(
        name="Highpoly Object",
        default=0)

    hl_decals_use_separate_texset : bpy.props.BoolProperty(
        name="Separate Decals",
        description="If checked, all specified decals will be baked to a separate texture set for the Object,\notherwise, decals map passes will be baked to Object's textures",
        default=False,
        update=BM_ITEM_PROPS_hl_decals_use_separate_texset_Update)

    hl_use_cage : bpy.props.BoolProperty(
        name="Use Cage Object",
        description="Cast rays to Object from cage",
        default=False,
        update=BM_ITEM_PROPS_hl_use_cage_Update)

    hl_cage_type : bpy.props.EnumProperty(
        name="Cage type",
        description="Type of Cage properties to use",
        items=[('STANDARD', "Standard", "Standard Cage properties of Cycles Bake.\nSet extrusion, ray distance, and choose cage object"),
               ('SMART', "Smart", "Auto cage creation using lowpoly mesh displace. Saves time with simple cage")],
        update=BM_ITEM_PROPS_hl_cage_type_Update)

    hl_cage_extrusion : bpy.props.FloatProperty(
        name="Cage Extrusion",
        description="Inflate by the specified distance to create cage",
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=BM_ITEM_PROPS_hl_cage_extrusion_Update)
    
    hl_max_ray_distance : bpy.props.FloatProperty(
        name="Max Ray Distance",
        description="The maximum ray distance for matching points between the high and lowpoly. If zero, there is no limit",
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=BM_ITEM_PROPS_hl_max_ray_distance)

    hl_cage : bpy.props.EnumProperty(
        name="Cage Object",
        description="Object to use as cage instead of calculating with cage extrusion",
        items=BM_ITEM_PROPS_hl_cage_Items,
        update=BM_ITEM_PROPS_hl_cage_Update)
    
    hl_cage_name_old : bpy.props.StringProperty()

    hl_cage_object_index : bpy.props.IntProperty(default=-1)

    hl_cage_object_include : bpy.props.StringProperty(default="")

# Item UV Props:
    uv_use_unique_per_map : bpy.props.BoolProperty(
        name="Unique per map",
        description="Set unqiue UV Settings for each map",
        default=False,
        update=BM_ITEM_PROPS_uv_use_unique_per_map_Update)

    uv_bake_data : bpy.props.EnumProperty(
        name="Bake Data",
        description="Choose data type to use for baking",
        default='OBJECT_MATERIALS',
        items=[('OBJECT_MATERIALS', "Object/Materials", "Use Object and Materials data for baking regular maps"),
               ('VERTEX_COLORS', "Vertex Colors", "Bake VertexColor Layers to Image Textures")],
        update=BM_ITEM_PROPS_uv_bake_data_Update)

    uv_bake_target : bpy.props.EnumProperty(
        name="Bake Target",
        description="Choose Baked Maps output target",
        items=BM_ITEM_PROPS_uv_bake_target_Items,
        update=BM_ITEM_PROPS_uv_bake_target_Update)

    uv_active_layer : bpy.props.EnumProperty(
        name="Active UV Map",
        description="Choose active UVMap layer to use in the bake.\nIf mesh has got no UV layers and at least one map to be baked to image texture, auto UV unwrap will be proceeded",
        items=BM_ITEM_PROPS_uv_active_layer_Items)

    uv_type : bpy.props.EnumProperty(
        name="UV Map Type",
        description="UVMap type is set automatically when changing Active UV Map. Change if it's not correct",
        items=BM_ITEM_PROPS_uv_type_Items,
        update=BM_ITEM_PROPS_uv_type_Update)

    uv_snap_islands_to_pixels : bpy.props.BoolProperty(
        name="Snap to pixels",
        description="Snap UVMap islands to pixel edges for clearer result",
        update=BM_ITEM_PROPS_uv_snap_islands_to_pixels_Update)

    uv_use_auto_unwrap : bpy.props.BoolProperty(
        name="Auto Unwrap",
        description="Auto UV Unwrap object using smart project. If UV Type is UDIMs, enabling Auto Unwrap will ignore it",
        update=BM_ITEM_PROPS_uv_use_auto_unwrap_Update)

    uv_auto_unwrap_angle_limit : bpy.props.IntProperty(
        name="Angle Limit",
        description="The angle at which to place seam on the mesh for unwrapping",
        default=66,
        min=0,
        max=89,
        subtype='ANGLE',
        update=BM_ITEM_PROPS_uv_auto_unwrap_angle_limit_Update)

    uv_auto_unwrap_island_margin : bpy.props.FloatProperty(
        name="Island Margin",
        description="Set distance between adjacent UV islands",
        default=0.01,
        min=0,
        max=1,
        update=BM_ITEM_PROPS_uv_auto_unwrap_island_margin_Update)
    
    uv_auto_unwrap_use_scale_to_bounds : bpy.props.BoolProperty(
        name="Scale to Bounds",
        description="Scale UV coordinates to bounds to fill the whole UV tile area",
        default=True,
        update=BM_ITEM_PROPS_uv_auto_unwrap_use_scale_to_bounds_Update)

# Item Output Props:
    out_use_unique_per_map : bpy.props.BoolProperty(
        name="Unique per map",
        description="Set unqiue Output Settings for each map",
        default=False,
        update=BM_ITEM_PROPS_out_use_unique_per_map_Update)
    
    out_use_denoise : bpy.props.BoolProperty(
        name="Denoise",
        description="Denoise and Discpeckle baked maps as a post-process filter",
        default=False,
        update=BM_ITEM_PROPS_out_use_denoise_Update)

    out_file_format : bpy.props.EnumProperty(
        name="File Format",
        description="File format of output image files",
        default='PNG',
        items=[('BMP', "BMP", "Output image in bitmap format"),
               ('PNG', "PNG", "Output image in common PNG format. Best file format for true-color images that need perfect tone balance. Default Blender image format.\n\Pros: can contain Alpha Channel"),
               ('JPEG', "JPEG", "Output image in JPEG format. Uncompressed file format and takes the most amount of data and is the exact representation of the image. \n\nCons: With every edit and resave the image quality will deteriorate.\nPros: lightweight"),
               ('TIFF', "TIFF", "Output image in TIFF format. Photographic file standard in print"),
               ('OPEN_EXR', "EXR", "Output image in EXR format. High-dynamic-range bitmap image file for storing large range of color. Common for Displacement and Normal-like maps"),
               ('PSD', "PSD", "Output image in Photoshop PSD layers. All baked maps for current Object will be saved to a single .psd file")],
        update=BM_ITEM_PROPS_out_file_format_Update)

    # out_psd_include : bpy.props.EnumProperty(
        # name="PSD includes",
        # description="What maps to put into one PSD file",
        # default='MAP',
        # items=[('MAP', "One map", "Each baked map - separate psd file"),
               # ('ALL_MAPS', "All object's maps", "All object's maps into single PSD file")],
        # update = BM_ITEM_PROPS_OutputSettings_Update)

    out_exr_codec : bpy.props.EnumProperty(
        name="Codec",
        description="Codec settigns for OpenEXR file format. Choose between lossless and lossy compression",
        default='ZIP',
        items=[('NONE', "None", ""),
               ('PXR24', "Pxr24 (Lossy)", ""),
               ('ZIP', "ZIP (Lossless)", ""),
               ('PIZ', "PIZ (lossless)", ""),
               ('RLE', "RLE (lossless)", ""),
               ('ZIPS', "ZIPS (lossless)", ""),
               ('DWAA', "DWAA (lossy)", ""),
               ('DWAB', "DWAB (lossy)", "")],
        update=BM_ITEM_PROPS_out_exr_codec_Update)

    out_compression : bpy.props.IntProperty(
        name="Compression",
        description="0 - no compression performed, raw file size. 100 - full compression, takes more time, but descreases output file size",
        default=15,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=BM_ITEM_PROPS_out_compression_Update)

    out_res : bpy.props.EnumProperty(
        name="Map Texture Resolution",
        description="Choose map resolution in pixels from the common ones or set custom",
        default='1024',
        items=[('512', "1/2K (512x512)", ""),
               ('1024', "1K (1024x1024)", ""),
               ('2048', "2K (2048x2048)", ""),
               ('4096', "4K (4096x4096)", ""),
               ('8192', "8K (8192x8192)", ""),
               ('CUSTOM', "Custom", "Enter custom height and width")],
               # ('TEXEL', "Texel Density defined", "Define image resolution based on object's texel density")],
        update=BM_ITEM_PROPS_out_res_Update)

    out_res_height : bpy.props.IntProperty(
        name="Height",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=BM_ITEM_PROPS_out_res_height_Update)

    out_res_width : bpy.props.IntProperty(
        name="Width",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=BM_ITEM_PROPS_out_res_width_Update)

    # out_texel_density_value : bpy.props.IntProperty(
        # name="Texel Density",
        # description="How many pixels should be in image per 1 unit (1m) of object's face.\nAutomatically calculated when chosen from Map Resolution List based on object's space relativity to Scene Render Resolution",
        # default=100,
        # min=1,
        # max=65536,
        # subtype='PIXEL',
        # update = BM_ITEM_PROPS_OutputSettings_Update)
    
    # out_texel_density_match : bpy.props.BoolProperty(
        # name="Match to Common",
        # description="Recalculate chosen Texel Density so that the image resolution is set to closest common resolution in Map Resolution List.\n(If checked then, for example, when image res by Texel Density is 1891px, it will be changed to 2048px (common 2K). If unchecked, then wil remain 1891px)",
        # default=True)

    out_margin : bpy.props.IntProperty(
        name="Margin",
        description="Padding. Extend bake result by specified number of pixels as a post-process filter.\nImproves baking quality by reducing hard edges visibility",
        default=16,
        min=0,
        max=64,
        subtype='PIXEL',
        update=BM_ITEM_PROPS_out_margin_Update)
    
    out_margin_type : bpy.props.EnumProperty(
        name="Margin Type",
        description="Algorithm for margin",
        default='ADJACENT_FACES',
        items=[('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),
               ('EXTEND', "Extend", "Extend face border pixels outwards")],
        update=BM_ITEM_PROPS_out_margin_type_Update)

    out_use_32bit : bpy.props.BoolProperty(
        name="32bit",
        description="Create image texture with 32 bit floating point depth.\nStores more color data in the image this way",
        default=False,
        update=BM_ITEM_PROPS_out_use_32bit_Update)

    out_use_alpha : bpy.props.BoolProperty(
        name="Alpha",
        description="Create image texture with Alpha color channel",
        default=False,
        update=BM_ITEM_PROPS_out_use_alpha_Update)

    out_use_transbg : bpy.props.BoolProperty(
        name="Transparent BG",
        description="Create image texture with transparent background instead of solid black",
        default=False,
        update=BM_ITEM_PROPS_out_use_transbg_Update)
    
    out_udim_start_tile : bpy.props.IntProperty(
        name="UDIM Start Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",
        default=1001,
        min=1001,
        max=2000,
        update=BM_ITEM_PROPS_out_udim_start_tile_Update)

    out_udim_end_tile : bpy.props.IntProperty(
        name="UDIM End Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",
        default=1001,
        min=1001,
        max=2000,
        update=BM_ITEM_PROPS_out_udim_end_tile_Update)

    out_super_sampling_aa : bpy.props.EnumProperty(
        name="SuperSampling AA",
        description="SSAA. Improve image quality by baking at a higher resolution and then downscaling to a lower resolution. Helps removing stepping, jagging, and dramatic color difference near color area edges",
        default='1X1',
        items=[('1X1', "1x1", "No supersampling. Bake and save with chosen resolution"),
               ('2X2', "2x2", "Bake at 2x the chosen resolution and then downscale"),
               ('4X4', "4x4", "Bake at 4x the chosen resolution and then downscale"),
               ('8X8', "8x8", "Bake at 8x the chosen resolution and then downscale"),
               ('16X16', "16x16", "Bake at 16x the chosen resolution and then downscale")],
        update=BM_ITEM_PROPS_out_super_sampling_aa_Update)

    out_samples : bpy.props.IntProperty(
        name="Bake Samples",
        description="Number of samples to render per each pixel",
        default=128,
        min=1,
        max=16777216,
        update=BM_ITEM_PROPS_out_samples)
    
    out_use_adaptive_sampling : bpy.props.BoolProperty(
        name="Adaptive Sampling",
        description="Automatically reduce the number of samples per pixel based on estimated noise level",
        default=False,
        update=BM_ITEM_PROPS_out_use_adaptive_sampling_Update)

    out_adaptive_threshold : bpy.props.FloatProperty(
        name="Noise Threshold",
        description="Noise level step to stop sampling at, lower values reduce noise at the cost of render time.\nZero for automatic setting based on number of AA sampled",
        default=0.01,
        min=0,
        max=1,
        soft_min=0.001,
        step=3,
        precision=4,
        update=BM_ITEM_PROPS_out_adaptive_threshold_Update)

    out_min_samples : bpy.props.IntProperty(
        name="Bake Min Samples",
        description="The minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold",
        default=0,
        min=0,
        max=4096,
        update=BM_ITEM_PROPS_out_min_samples_Update)

# Item Shading Correction Props
    csh_use_triangulate_lowpoly : bpy.props.BoolProperty(
        name="Triangulate Lowpoly",
        description="Triangulate Lowpoly mesh n-gons. Takes time but improves shading of Lowpoly mesh with redundant uv stretches",
        default=False,
        update=BM_ITEM_PROPS_csh_use_triangulate_lowpoly_Update)
    
    csh_use_lowpoly_reset_normals : bpy.props.BoolProperty(
        name="Reset Lowpoly Normals",
        description="Reset all lowpoly mesh normals direction and recalculate them outside",
        default=False,
        update=BM_ITEM_PROPS_csh_use_lowpoly_reset_normals_Update)

    csh_lowpoly_use_smooth : bpy.props.BoolProperty(
        name="Smooth Lowpoly",
        description="Use smooth-shaded Lowpoly for baking. Can be kept unchecked if you've set shading on your own",
        default=False,
        update=BM_ITEM_PROPS_csh_lowpoly_use_smooth_Update)

    csh_lowpoly_smoothing_groups_enum : bpy.props.EnumProperty(
        name="Lowpoly Smoothing groups",
        description="Choose Lowpoly smooth shading groups type to apply",
        default='STANDARD',
        items=[('STANDARD', "Standard", "Apply default Shade Smooth to whole object"),
               ('AUTO', "Auto Smooth", "Apply Auto Shade Smooth based on angle between faces or mesh split normals data"),
               ('VERTEX_GROUPS', "Vertex Groups", "Apply smooth shading to created mesh vertex groups. Correct smooth shading technique")],
        update=BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_enum_Update)
    
    csh_lowpoly_smoothing_groups_angle : bpy.props.IntProperty(
        name="Angle",
        description="Maximum angle between face normals that will be considered as smooth\n(unused if custom split normals are available",
        default=30,
        min=0,
        max=180,
        subtype='ANGLE',
        update=BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_angle_Update)

    csh_lowpoly_smoothing_groups_name_contains : bpy.props.StringProperty(
        name="Name Contains",
        description="Apply smooth shading only to vertex groups which names contain this value. Leave empty to apply to all vertex groups",
        default="_smooth",
        update=BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_name_contains_Update)

    csh_use_highpoly_reset_normals : bpy.props.BoolProperty(
        name="Reset Highpoly Normals",
        description="Reset all highpoly mesh normals direction and recalculate them outside",
        default=False,
        update=BM_ITEM_PROPS_csh_use_highpoly_reset_normals_Update)

    csh_highpoly_use_smooth : bpy.props.BoolProperty(
        name="Smooth Highpoly",
        description="Use smooth-shaded Highpoly for baking. Can be kept unchecked if you've set shading on your own",
        default=False,
        update=BM_ITEM_PROPS_csh_highpoly_use_smooth_Update)

    csh_highpoly_smoothing_groups_enum : bpy.props.EnumProperty(
        name="Highpoly Smoothing groups",
        description="Choose Highpoly smooth shading groups type to apply",
        default='STANDARD',
        items=[('STANDARD', "Standard", "Apply default Shade Smooth to whole object"),
               ('AUTO', "Auto Smooth", "Apply Auto Shade Smooth based on angle between faces or mesh split normals data"),
               ('VERTEX_GROUPS', "Vertex Groups", "Apply smooth shading to created mesh vertex groups. Correct smooth shading technique")],
        update=BM_ITEM_PROPS_csh_highpoly_smoothing_groups_enum_Update)
    
    csh_highpoly_smoothing_groups_angle : bpy.props.IntProperty(
        name="Angle",
        description="Maximum angle between face normals that will be considered as smooth\n(unused if custom split normals are available",
        default=30,
        min=0,
        max=180,
        subtype='ANGLE',
        update=BM_ITEM_PROPS_csh_highpoly_smoothing_groups_angle_Update)

    csh_highpoly_smoothing_groups_name_contains : bpy.props.StringProperty(
        name="Name Contains",
        description="Apply smooth shading only to vertex groups which names contain this value",
        default="_smooth",
        update=BM_ITEM_PROPS_csh_highpoly_smoothing_groups_name_contains_Update)

# Item Maps Collection Props
    global_maps_active_index : bpy.props.IntProperty(
        name="Configure maps to bake",
        default=-1,
        update=BM_ITEM_RemoveLocalPreviews)
    
    global_maps : bpy.props.CollectionProperty(type=BM_Map)

# Item Channel Packing Props
    chnlp_channelpacking_table : bpy.props.CollectionProperty(type=BM_Object_ChannelPack)

    chnlp_channelpacking_table_active_index : bpy.props.IntProperty(
        name="Channel Pack",
        default=0)

# Item Bake Props
    bake_save_internal : bpy.props.BoolProperty(
        name="Internal",
        description="Saved baked maps into the current Blender file",
        default=True,
        update=BM_ITEM_PROPS_bake_save_internal_Update)

    bake_output_filepath : bpy.props.StringProperty(
        name="Output Path",
        description="Directory path on your disk to save bake maps to. \\\\ means relative to this Blender file",
        default="\\\\",
        subtype='DIR_PATH',
        update=BM_ITEM_PROPS_bake_output_filepath_Update)

    bake_create_subfolder : bpy.props.BoolProperty(
        name="Create Subfolder",
        description="Create subfolder in the Output Path directory and save baked maps there",
        default=False,
        update=BM_ITEM_PROPS_bake_create_subfolder_Update)

    bake_subfolder_name : bpy.props.StringProperty(
        name="Subfolder Name",
        description="How to name the subfolder",
        default="Maps",
        update=BM_ITEM_PROPS_bake_subfolder_name_Update)

    # bake_batch_name_table : bpy.props.CollectionProperty(type=BM_Object_BatchNamingKeyword)

    # bake_batch_name_table_active_index : bpy.props.IntProperty(
    #     name="Batch Naming Keyword",
    #     default=0)
    
    # bake_batch_name_use_custom : bpy.props.BoolProperty(
    #     name="Use Custom Batch Name",
    #     default=False)
        
    bake_batchname : bpy.props.StringProperty(
        name="Batch Name",
        description=BM_Labels.PROP_ITEM_bake_batchname_custom_Description,
        default="$objectindex_$objectname_$mapname",
        update=BM_ITEM_PROPS_bake_batchname_Update)

    bake_batchname_use_caps : bpy.props.BoolProperty(
        name="Use Caps",
        description="Use capital letters for batch name",
        default=False,
        update=BM_ITEM_PROPS_bake_batchname_use_caps_Update)
    
    # bake_batchname_preview : bpy.props.StringProperty(
        # name="Preview",
        # description="Output file batch name preview (might change for each map)")

    bake_create_material : bpy.props.BoolProperty(
        name="Create Material",
        description="Assign a new material to the object after bake with all baked maps inlcuded",
        default=False,
        update=BM_ITEM_PROPS_bake_create_material_Update)

    bake_device : bpy.props.EnumProperty(
        name="Bake Device",
        description="Device to use for baking",
        default='CPU',
        items=[('GPU', "GPU", "Use GPU compute device for baking, configured in the system tab in the user preferences"),
               ('CPU', "CPU", "Use CPU for baking")],
        update=BM_ITEM_PROPS_bake_device_Update)
