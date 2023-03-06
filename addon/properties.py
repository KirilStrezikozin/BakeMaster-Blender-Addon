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

from bpy.types import (
    PropertyGroup,
    Camera as bpy_types_Camera,
)
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
)
from .labels import BM_LABELS_Props
from .utils import properties as bm_props_utils


# class F():


class Map_Highpoly(PropertyGroup):
    name: EnumProperty(
        name="Highpoly Object",
        description="Choose a highpoly among available (highpoly should be added to Bake Job's Objects",  # noqa: E501
        items=bm_props_utils.Highpoly_Items,
        update=bm_props_utils.Highpoly_Update)

    name_old: StringProperty(default="")
    index: IntProperty(default=-1)
    map_index: IntProperty(default=-1)
    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)
    object_include: StringProperty(default="")
    self_object_index: IntProperty(default=-1)


class Map(PropertyGroup):
    use_bake: BoolProperty(
        name="Include/exclude map from being baked",
        default=True,
        update=bm_props_utils.Map_use_bake_Update)

    map_type: EnumProperty(
        name="Choose Map Type",
        description="Type of the current map pass",
        items=bm_props_utils.Map_map_type_Items,
        update=bm_props_utils.Map_map_type_Update)

    index: IntProperty(default=-1)
    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    # Map hl Props
    hl_highpolies: CollectionProperty(type=Map_Highpoly)

    hl_highpolies_active_index: IntProperty(
        name="Highpoly Object",
        default=0)

    hl_highpolies_len: IntProperty(default=0)

    hl_use_cage: BoolProperty(
        name="Use Cage Object",
        description="Cast rays to Object from cage",
        default=False,
        update=bm_props_utils.Object_hl_use_cage_Update)

    hl_cage_type: EnumProperty(
        name="Cage type",
        description="Type of Cage properties to use",
        items=[('STANDARD', "Standard", "Standard Cage properties.\nSet extrusion, ray distance, and choose a cage object"),  # noqa: E501
               ('SMART', "Smart", "Auto cage creation using lowpoly mesh displace. Saves time with simple cage")],  # noqa: E501
        update=bm_props_utils.Map_hl_cage_type_Update)

    hl_cage_extrusion: FloatProperty(
        name="Cage Extrusion",
        description="Inflate the lowpoly by the specified distance to create cage",  # noqa: E501
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=bm_props_utils.Map_hl_cage_extrusion_Update)

    hl_max_ray_distance: FloatProperty(
        name="Max Ray Distance",
        description="The maximum ray distance for matching points between the high and lowpoly. If zero, there is no limit",  # noqa: E501
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=bm_props_utils.Map_hl_max_ray_distance_Update)

    hl_cage: EnumProperty(
        name="Cage Object",
        description="Object to use as cage instead of calculating with cage extrusion",  # noqa: E501
        items=bm_props_utils.Object_hl_cage_Items,
        update=bm_props_utils.Object_hl_cage_Update)

    hl_cage_name_old: StringProperty()

    hl_cage_object_index: IntProperty(default=-1)

    hl_cage_object_include: StringProperty(default="")

    # Map uv Props
    uv_bake_data: EnumProperty(
        name="Bake Data",
        description="Choose data type to bake from for the current object",
        default='OBJECT_MATERIALS',
        items=[('OBJECT_MATERIALS', "Object/Materials", "Use Object and Materials data for baking regular maps"),  # noqa: E501
               ('VERTEX_COLORS', "Vertex Colors", "Bake VertexColor Layers to Image Textures")],  # noqa: E501
        update=bm_props_utils.Map_uv_bake_data_Update)

    uv_bake_target: EnumProperty(
        name="Bake Target",
        description="Choose Baked Maps output target",
        items=bm_props_utils.Object_uv_bake_target_Items,
        update=bm_props_utils.Map_uv_bake_target_Update)

    uv_active_layer: EnumProperty(
        name="Active UV Map",
        description="Choose active UVMap layer to use in the bake.\nIf mesh has got no UV layers and at least one map to be baked to image texture, auto UV unwrap will be proceeded",  # noqa: E501
        items=bm_props_utils.Object_uv_active_layer_Items)

    uv_type: EnumProperty(
        name="UV Map Type",
        description="Choose UV Map type for the chosen Active UV Map",
        items=bm_props_utils.Object_uv_type_Items,
        update=bm_props_utils.Map_uv_type_Update)

    uv_snap_islands_to_pixels: BoolProperty(
        name="Snap UV to pixels",
        description="Make chosen UV Layer pixel perfect by aligning UV Coordinates to pixels' corners/edges (will depend on chosen map resolution)",  # noqa: E501
        update=bm_props_utils.Map_uv_snap_islands_to_pixels_Update)

    # uv_use_auto_unwrap: BoolProperty(
    #     name="Auto Unwrap",
    #     description="Auto UV Unwrap object using smart project",
    #     update=bm_props_utils.Object_UVSettings_Update)

    # uv_auto_unwrap_angle_limit: IntProperty(
    #     name="Angle Limit",
    #     description="The angle at which to place seam on the mesh for unwrapping",  # noqa: E501
    #     default=66,
    #     min=0,
    #     max=89,
    #     subtype='ANGLE',
    #     update=bm_props_utils.Object_UVSettings_Update)

    # uv_auto_unwrap_island_margin: FloatProperty(
    #     name="Island Margin",
    #     description="Set distance between adjacent UV islands",
    #     default=0.01,
    #     min=0,
    #     max=1,
    #     update=bm_props_utils.Object_UVSettings_Update)

    # uv_auto_unwrap_use_scale_to_bounds: BoolProperty(
    #     name="Scale to Bounds",
    #     description="Scale UV coordinates to bounds to fill the whole UV tile area",  # noqa: E501
    #     default=True,
    #     update=bm_props_utils.Object_UVSettings_Update)

    # Map out Props
    out_use_denoise: BoolProperty(
        name="Denoise",
        description="Denoise and Discpeckle baked maps as a post-process filter. For external bake only",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_out_use_denoise_Update)

    out_use_scene_color_management: BoolProperty(
        name="Scene Color Management",
        description="Affect baked map by scene color management settings and compositor nodes. For external bake only",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_out_use_scene_color_management_Update)

    out_file_format: EnumProperty(
        name="File Format",
        description="File format of output image files",
        default='PNG',
        items=[('BMP', "BMP", "Output image in bitmap format"),
               ('PNG', "PNG", "Output image in common PNG format. Best file format for true-color images that need perfect tone balance. Default Blender image format.\n\nPros: can contain Alpha Channel"),  # noqa: E501
               ('JPEG', "JPEG", "Output image in JPEG format. Uncompressed file format and takes the most amount of data and is the exact representation of the image. \n\nCons: With every edit and resave the image quality will deteriorate.\nPros: lightweight"),  # noqa: E501
               ('TIFF', "TIFF", "Output image in TIFF format. Photographic file standard in print"),  # noqa: E501
               ('OPEN_EXR', "EXR", "Output image in EXR format. High-dynamic-range bitmap image file for storing large range of color. Common for Displacement and Normal-like maps")],  # noqa: E501
               # ('PSD', "PSD", "Output image in Photoshop PSD layers. All baked maps with PSD set as file format for current Object will be saved to a single .psd file")],  # noqa: E501
        update=bm_props_utils.Map_out_file_format_Update)

    # out_psd_include: EnumProperty(
    #     name="PSD includes",
    #     description="What maps to put into one PSD file",
    #     default='MAP',
    #     items=[('MAP', "One map", "Each baked map - separate psd file")],
    #     update=bm_props_utils.Object_OutputSettings_Update)

    out_exr_codec: EnumProperty(
        name="Codec",
        description="Codec settigns for OpenEXR file format. Choose between lossless and lossy compression",  # noqa: E501
        default='ZIP',
        items=[('NONE', "None", ""),
               ('PXR24', "Pxr24 (Lossy)", ""),
               ('ZIP', "ZIP (Lossless)", ""),
               ('PIZ', "PIZ (lossless)", ""),
               ('RLE', "RLE (lossless)", ""),
               ('ZIPS', "ZIPS (lossless)", ""),
               ('DWAA', "DWAA (lossy)", ""),
               ('DWAB', "DWAB (lossy)", "")],
        update=bm_props_utils.Map_out_exr_codec_Update)

    out_compression: IntProperty(
        name="Compression",
        description="0 - no compression performed, raw file size. 100 - full compression, takes more time, but descreases output file size",  # noqa: E501
        default=15,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=bm_props_utils.Map_out_compression_Update)

    out_res: EnumProperty(
        name="Map Texture Resolution",
        description="Choose map resolution in pixels from the common ones or set custom",  # noqa: E501
        default='1024',
        items=[('512', "1/2K (512x512)", ""),
               ('1024', "1K (1024x1024)", ""),
               ('2048', "2K (2048x2048)", ""),
               ('4096', "4K (4096x4096)", ""),
               ('8192', "8K (8192x8192)", ""),
               ('CUSTOM', "Custom", "Enter custom height and width")],
               #  ('TEXEL', "Texel Density defined", "Define image resolution based on object's texel density")],  # noqa: E501
        update=bm_props_utils.Map_out_res_Update)

    out_res_height: IntProperty(
        name="Height",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=bm_props_utils.Map_out_res_height_Update)

    out_res_width: IntProperty(
        name="Width",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=bm_props_utils.Map_out_res_width_Update)

    # out_texel_density_value: IntProperty(
    #     name="Texel Density",
    #     description="How many pixels should be in image per 1 unit (1m) of object's face.\nAutomatically calculated when chosen from Map Resolution List based on object's space relativity to Scene Render Resolution",  # noqa: E501
    #     default=100,
    #     min=1,
    #     max=65536,
    #     subtype='PIXEL',
    #     update=bm_props_utils.Object_OutputSettings_Update)

    # out_texel_density_match: BoolProperty(
    #     name="Match to Common",
    #     description="Recalculate chosen Texel Density so that the image resolution is set to closest common resolution in Map Resolution List.\n(If checked then, for example, when image res by Texel Density is 1891px, it will be changed to 2048px (common 2K). If unchecked, then wil remain 1891px)",  # noqa: E501
    #     default=True)

    out_margin: IntProperty(
        name="Margin",
        description="Padding. Extend bake result by specified number of pixels as a post-process filter.\nImproves baking quality by reducing hard edges visibility",  # noqa: E501
        default=16,
        min=0,
        max=64,
        subtype='PIXEL',
        update=bm_props_utils.Map_out_margin_Update)

    out_margin_type: EnumProperty(
        name="Margin Type",
        description="Algorithm for margin",
        default='ADJACENT_FACES',
        items=[('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),  # noqa: E501
               ('EXTEND', "Extend", "Extend face border pixels outwards")],
        update=bm_props_utils.Map_out_margin_type_Update)

    out_use_32bit: BoolProperty(
        name="32bit",
        description="Create image texture with 32 bit floating point depth.\nStores more color data in the image this way",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_out_use_32bit_Update)

    out_use_alpha: BoolProperty(
        name="Alpha",
        description="Create image texture with Alpha color channel",
        default=False,
        update=bm_props_utils.Map_out_use_alpha_Update)

    out_use_transbg: BoolProperty(
        name="Transparent BG",
        description="Create image texture with transparent background instead of solid black",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_out_use_transbg_Update)

    out_udim_start_tile: IntProperty(
        name="UDIM Start Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",  # noqa: E501
        default=1001,
        min=1001,
        max=2000,
        update=bm_props_utils.Map_out_udim_start_tile_Update)

    out_udim_end_tile: IntProperty(
        name="UDIM End Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",  # noqa: E501
        default=1001,
        min=1001,
        max=2000,
        update=bm_props_utils.Map_out_udim_end_tile_Update)

    out_super_sampling_aa: EnumProperty(
        name="SuperSampling AA",
        description="SSAA. Improve image quality by baking at a higher resolution and then downscaling to a lower resolution. Helps removing stepping, jagging, and dramatic color difference near color area edges",  # noqa: E501
        default='1',
        items=[('1', "1x1", "No supersampling. Bake and save with chosen resolution"),  # noqa: E501
               ('2', "2x2", "Bake at 2x the chosen resolution and then downscale"),  # noqa: E501
               ('4', "4x4", "Bake at 4x the chosen resolution and then downscale"),  # noqa: E501
               ('8', "8x8", "Bake at 8x the chosen resolution and then downscale"),  # noqa: E501
               ('16', "16x16", "Bake at 16x the chosen resolution and then downscale")],  # noqa: E501
        update=bm_props_utils.Map_out_super_sampling_aa_Update)

    out_samples: IntProperty(
        name="Bake Samples",
        description="Number of samples to render per each pixel",
        default=128,
        min=1,
        max=16777216,
        update=bm_props_utils.Map_out_samples_Update)

    out_use_adaptive_sampling: BoolProperty(
        name="Adaptive Sampling",
        description="Automatically reduce the number of samples per pixel based on estimated noise level",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_out_use_adaptive_sampling_Update)

    out_adaptive_threshold: FloatProperty(
        name="Noise Threshold",
        description="Noise level step to stop sampling at, lower values reduce noise at the cost of render time.\nZero for automatic setting based on number of AA sampled",  # noqa: E501
        default=0.01,
        min=0,
        max=1,
        soft_min=0.001,
        step=3,
        precision=4,
        update=bm_props_utils.Map_out_adaptive_threshold_Update)

    out_min_samples: IntProperty(
        name="Bake Min Samples",
        description="The minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold",  # noqa: E501
        default=0,
        min=0,
        max=4096,
        update=bm_props_utils.Map_out_min_samples_Update)

# Albedo Map Props
    map_ALBEDO_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="ALBEDO",
        update=bm_props_utils.Map_map_ALBEDO_prefix_Update)

    map_ALBEDO_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_ALBEDO_use_preview_Update)

# Metalness Map Props
    map_METALNESS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="METAL",
        update=bm_props_utils.Map_map_METALNESS_prefix_Update)

    map_METALNESS_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_METALNESS_use_preview_Update)

# Roughness Map Props
    map_ROUGHNESS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="ROUGH",
        update=bm_props_utils.Map_map_ROUGHNESS_prefix_Update)

    map_ROUGHNESS_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_ROUGHNESS_use_preview_Update)

# Diffuse Map Props
    map_DIFFUSE_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="DIFFUSE",
        update=bm_props_utils.Map_map_DIFFUSE_prefix_Update)

    map_DIFFUSE_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_DIFFUSE_use_preview_Update)

# Specular Map Props
    map_SPECULAR_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="SPECULAR",
        update=bm_props_utils.Map_map_SPECULAR_prefix_Update)

    map_SPECULAR_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_SPECULAR_use_preview_Update)

# Glossiness Map Props
    map_GLOSSINESS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="GLOSS",
        update=bm_props_utils.Map_map_GLOSSINESS_prefix_Update)

    map_GLOSSINESS_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_GLOSSINESS_use_preview_Update)

# Opacity Map Props
    map_OPACITY_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="OPACITY",
        update=bm_props_utils.Map_map_OPACITY_prefix_Update)

    map_OPACITY_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_OPACITY_use_preview_Update)

# Emission Map Props
    map_EMISSION_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="EMISSION",
        update=bm_props_utils.Map_map_EMISSION_prefix_Update)

    map_EMISSION_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_EMISSION_use_preview_Update)

# Pass Map Props
    map_PASS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="BSDFPASS",
        update=bm_props_utils.Map_map_PASS_prefix_Update)

    map_PASS_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_PASS_use_preview_Update)

    map_pass_type: EnumProperty(
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
        update=bm_props_utils.Map_map_pass_type_Update)

# Decal Pass Map Props
    map_DECAL_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="DECAL",
        update=bm_props_utils.Map_map_DECAL_prefix_Update)

    map_DECAL_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_DECAL_use_preview_Update)

    map_decal_pass_type: EnumProperty(
        name="Pass Type",
        description="Decal Map pass type to bake",
        default='NORMAL',
        items=[('NORMAL', "Normal", "Normals Pass"),
               ('HEIGHT', "Height", "How high mesh parts are from the world ground level"),  # noqa: E501
               ('OPACITY', "Opacity", "Decal Object - white, empty space - black")],  # noqa: E501
        update=bm_props_utils.Map_map_decal_pass_type_Update)

    map_decal_height_opacity_invert: BoolProperty(
        name="Invert",
        description="Invert colors of the map",
        default=False,
        update=bm_props_utils.Map_map_decal_height_opacity_invert_Update)

    map_decal_normal_preset: EnumProperty(
        name="Preset",
        description="Decal Map Normal Pass preset for different software for correct result when used in that software",  # noqa: E501
        default='BLENDER_OPENGL',
        items=[('CUSTOM', "Custom", "Choose custom algorithm"),
               ('BLENDER_OPENGL', "Blender", "Blender uses OpenGL format"),
               ('3DS_MAX_DIRECTX', "3DS Max", "3DS Max uses DirectX format"),
               ('CORONA_DIRECTX', "Corona", "Corona uses DirectX format"),
               ('CRYENGINE_DIRECTX', "CryEngine", "CryEngine uses DirectX format"),  # noqa: E501
               ('SUBSTANCE_PAINTER_DIRECTX', "Substance Painter", "Substance Painter uses DirectX format"),  # noqa: E501
               ('UNREAL_ENGINE_DIRECTX', "Unreal Engine", "Unreal Engine uses DirectX format"),  # noqa: E501
               ('CINEMA_4D_OPENGL', "Cinema 4D", "Cinema 4D uses OpenGL format"),  # noqa: E501
               ('ARNOLD_OPENGL', "Arnold", "Arnold uses OpenGL format"),
               ('HOUDINI_OPENGL', "Houdini", "Houdini uses OpenGL format"),
               ('MARMOSET_TOOLBAG_OPENGL', "Marmoset Toolbag", "Marmoset Toolbag uses OpenGL format"),  # noqa: E501
               ('MAYA_OPENGL', "Maya", "Maya uses OpenGL format"),
               ('OCTANE_OPENGL', "Octane", "Octane uses OpenGL format"),
               ('REDSHIFT_OPENGL', "Redshift", "Redshift uses OpenGL format"),
               ('UNITY_OPENGL', "Unity", "Unity uses OpenGL format"),
               ('VRAY_OPENGL', "VRay", "VRay uses OpenGL format"),
               ('ZBRUSH_OPENGL', "ZBrush", "ZBrush uses OpenGL format")],
        update=bm_props_utils.Map_map_decal_normal_preset_Update)

    map_decal_normal_custom_preset: EnumProperty(
        name="Custom Format",
        description="Decal Map Normal Pass format (Green channel is inverted)",
        default='OPEN_GL',
        items=[('OPEN_GL', "OpenGL", "OpenGL Normal Map format. Green Channel Axis is +Y"),  # noqa: E501
               ('DIRECTX', "DirectX", "DirectX Normal Map format. Green Channel Axis is -Y")],  # noqa: E501
               # ('CUSTOM', "Custom", "Set custom axes for channels")],
        update=bm_props_utils.Map_map_decal_normal_custom_preset_Update)

    map_decal_normal_r: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "red",
        default='POS_X',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_decal_normal_r_Update)

    map_decal_normal_g: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "green",
        default='POS_Y',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_decal_normal_g_Update)

    map_decal_normal_b: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "blue",
        default='POS_Z',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_decal_normal_b_Update)

# Vertex Color Layer Map Props
    map_VERTEX_COLOR_LAYER_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="VERTEXCOLOR",
        update=bm_props_utils.Map_map_VERTEX_COLOR_LAYER_prefix_Update)

    map_VERTEX_COLOR_LAYER_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_VERTEX_COLOR_LAYER_use_preview_Update)

    map_vertexcolor_layer: EnumProperty(
        name="Layer",
        description="Vertex Color Layer to bake",
        items=bm_props_utils.Map_map_vertexcolor_layer_Items,
        update=bm_props_utils.Map_map_vertexcolor_layer_Update)

# Cycles Map Props
    map_C_COMBINED_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="COMBINED",
        update=bm_props_utils.Map_map_C_COMBINED_prefix_Update)

    map_C_AO_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="AO",
        update=bm_props_utils.Map_map_C_AO_prefix_Update)

    map_C_SHADOW_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="SHADOW",
        update=bm_props_utils.Map_map_C_SHADOW_prefix_Update)

    map_C_POSITION_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="POS",
        update=bm_props_utils.Map_map_C_POSITION_prefix_Update)

    map_C_NORMAL_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="NORMAL",
        update=bm_props_utils.Map_map_C_NORMAL_prefix_Update)

    map_C_UV_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="UV",
        update=bm_props_utils.Map_map_C_UV_prefix_Update)

    map_C_ROUGHNESS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="ROUGH",
        update=bm_props_utils.Map_map_C_ROUGHNESS_prefix_Update)

    map_C_EMIT_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="EMIT",
        update=bm_props_utils.Map_map_C_EMIT_prefix_Update)

    map_C_ENVIRONMENT_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="ENV",
        update=bm_props_utils.Map_map_C_ENVIRONMENT_prefix_Update)

    map_C_DIFFUSE_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="DIFFUSE",
        update=bm_props_utils.Map_map_C_DIFFUSE_prefix_Update)

    map_C_GLOSSY_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="GLOSS",
        update=bm_props_utils.Map_map_C_GLOSSY_prefix_Update)

    map_C_TRANSMISSION_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="TRANS",
        update=bm_props_utils.Map_map_C_TRANSMISSION_prefix_Update)

    map_cycles_use_pass_direct: BoolProperty(
        name="Direct",
        description="Add direct lighting contribution",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_direct_Update)

    map_cycles_use_pass_indirect: BoolProperty(
        name="Indirect",
        description="Add indirect lighting contribution",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_indirect_Update)

    map_cycles_use_pass_color: BoolProperty(
        name="Color",
        description="Color the pass",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_color_Update)

    map_cycles_use_pass_diffuse: BoolProperty(
        name="Diffuse",
        description="Add %s contribution" % "Diffuse",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_diffuse_Update)

    map_cycles_use_pass_glossy: BoolProperty(
        name="Glossy",
        description="Add %s contribution" % "Glossy",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_glossy_Update)

    map_cycles_use_pass_transmission: BoolProperty(
        name="Transmission",
        description="Add %s contribution" % "Transmission",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_transmission_Update)

    map_cycles_use_pass_ambient_occlusion: BoolProperty(
        name="Ambient Occlusion",
        description="Add %s contribution" % "Ambient Occlusion",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_ambient_occlusion_Update)

    map_cycles_use_pass_emit: BoolProperty(
        name="Emit",
        description="Add %s contribution" % "Emit",
        default=True,
        update=bm_props_utils.Map_map_cycles_use_pass_emit_Update)

# Normal Map Props
    map_NORMAL_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="NORMAL",
        update=bm_props_utils.Map_map_NORMAL_prefix_Update)

    map_NORMAL_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_NORMAL_use_preview_Update)

    map_normal_data: EnumProperty(
        name="Data",
        description="Data for Normal map",
        items=bm_props_utils.Map_map_normal_data_Items,
        update=bm_props_utils.Map_map_normal_data_Update)

    map_normal_space: EnumProperty(
        name="Normal Space",
        description="Choose normal space for baking",
        default='TANGENT',
        items=[('TANGENT', "Tangent", "Blue colors. Tangent space normal map"),
               ('OBJECT', "Object", "Rainbow colors. Object space normal map with local coordinates")],  # noqa: E501
        update=bm_props_utils.Map_map_normal_space_Update)

    map_normal_preset: EnumProperty(
        name="Preset",
        description="Normal Map preset for different software for correct result when used in that software",  # noqa: E501
        default='BLENDER_OPENGL',
        items=[('CUSTOM', "Custom", "Choose custom algorithm"),
               ('BLENDER_OPENGL', "Blender", "Blender uses OpenGL format"),
               ('3DS_MAX_DIRECTX', "3DS Max", "3DS Max uses DirectX format"),
               ('CORONA_DIRECTX', "Corona", "Corona uses DirectX format"),
               ('CRYENGINE_DIRECTX', "CryEngine", "CryEngine uses DirectX format"),  # noqa: E501
               ('SUBSTANCE_PAINTER_DIRECTX', "Substance Painter", "Substance Painter uses DirectX format"),  # noqa: E501
               ('UNREAL_ENGINE_DIRECTX', "Unreal Engine", "Unreal Engine uses DirectX format"),  # noqa: E501
               ('CINEMA_4D_OPENGL', "Cinema 4D", "Cinema 4D uses OpenGL format"),  # noqa: E501
               ('ARNOLD_OPENGL', "Arnold", "Arnold uses OpenGL format"),
               ('HOUDINI_OPENGL', "Houdini", "Houdini uses OpenGL format"),
               ('MARMOSET_TOOLBAG_OPENGL', "Marmoset Toolbag", "Marmoset Toolbag uses OpenGL format"),  # noqa: E501
               ('MAYA_OPENGL', "Maya", "Maya uses OpenGL format"),
               ('OCTANE_OPENGL', "Octane", "Octane uses OpenGL format"),
               ('REDSHIFT_OPENGL', "Redshift", "Redshift uses OpenGL format"),
               ('UNITY_OPENGL', "Unity", "Unity uses OpenGL format"),
               ('VRAY_OPENGL', "VRay", "VRay uses OpenGL format"),
               ('ZBRUSH_OPENGL', "ZBrush", "ZBrush uses OpenGL format")],
        update=bm_props_utils.Map_map_normal_preset_Update)

    map_normal_custom_preset: EnumProperty(
        name="Custom Format",
        description="Normal Map format (Green channel is inverted)",
        default='OPEN_GL',
        items=[('OPEN_GL', "OpenGL", "OpenGL Normal Map format. Green Channel Axis is +Y"),  # noqa: E501
               ('DIRECTX', "DirectX", "DirectX Normal Map format. Green Channel Axis is -Y"),  # noqa: E501
               ('CUSTOM', "Custom", "Set custom axes for channels")],
        update=bm_props_utils.Map_map_normal_custom_preset_Update)

    map_normal_r: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "red",
        default='POS_X',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_normal_r_Update)

    map_normal_g: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "green",
        default='POS_Y',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_normal_g_Update)

    map_normal_b: EnumProperty(
        name="Normal Space",
        description="Axis to bake in %s channel" % "blue",
        default='POS_Z',
        items=[('POS_X', "+X", ""),
               ('POS_Y', "+Y", ""),
               ('POS_Z', "+Z", ""),
               ('NEG_X', "-X", ""),
               ('NEG_Y', "-Y", ""),
               ('NEG_Z', "-Z", "")],
        update=bm_props_utils.Map_map_normal_b_Update)

# Displacement Map Props
    map_DISPLACEMENT_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="DISP",
        update=bm_props_utils.Map_map_DISPLACEMENT_prefix_Update)

    map_DISPLACEMENT_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_DISPLACEMENT_use_preview_Update)

    map_displacement_data: EnumProperty(
        name="Data",
        description="Data for Displacement map",
        items=bm_props_utils.Map_map_displacement_data_Items,
        update=bm_props_utils.Map_map_displacement_data_Update)

    map_displacement_result: EnumProperty(
        name="Result to",
        description="How to apply baked displacement map",
        default="MODIFIER",
        items=[('IMAGE_ONLY', "Only Image Texture", "Bake displacement and just save output image"),  # noqa: E501
               ('MODIFIER', "Modifiers", "Add displace modifier to the object with bake displacement displace texture"),  # noqa: E501
               ('MATERIAL', "Material Displacement", "Add baked displacement to every object material displacement socket")],  # noqa: E501
        update=bm_props_utils.Map_map_displacement_result_Update)

    map_displacement_subdiv_levels: IntProperty(
        name="Subdivision Levels",
        description="The subdivision level defines the level of details.\nThe lower - the faster, but less details",  # noqa: E501
        default=1,
        min=1,
        max=10,
        update=bm_props_utils.Map_map_displacement_subdiv_levels_Update)

    map_displacement_lowresmesh: BoolProperty(
        name="Heights against lowpoly",
        description="Calculate heights against unsubdivided low resolution mesh",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_displacement_lowresmesh_Update)

# Vector Displacement Map Props
    map_VECTOR_DISPLACEMENT_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="VD",
        update=bm_props_utils.Map_map_VECTOR_DISPLACEMENT_prefix_Update)

    map_VECTOR_DISPLACEMENT_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_VECTOR_DISPLACEMENT_use_preview_Update)

    map_vector_displacement_use_negative: BoolProperty(
        name="Include Negative",
        description="Remap color values to include negative values for displacement",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_vector_displacement_use_negative_Update)

    map_vector_displacement_result: EnumProperty(
        name="Result to",
        description="How to apply baked displacement map",
        default="MODIFIER",
        items=[('IMAGE_ONLY', "Only Image Texture", "Bake vector displacement and just save output image"),  # noqa: E501
               ('MODIFIER', "Modifiers", "Add displace modifier to the object with bake vector displacement displace texture"),  # noqa: E501
               ('MATERIAL', "Material Displacement", "Add baked vector displacement to every object material displacement socket")],  # noqa: E501
        update=bm_props_utils.Map_map_vector_displacement_result_Update)

    map_vector_displacement_subdiv_levels: IntProperty(
        name="Subdivision Levels",
        description="The subdivision level defines the level of details.\nThe lower - the faster, but less details",  # noqa: E501
        default=1,
        min=1,
        max=10,
        update=bm_props_utils.Map_map_vector_displacement_subdiv_levels_Update)

# Position Map Props
    map_POSITION_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="POS",
        update=bm_props_utils.Map_map_POSITION_prefix_Update)

    map_POSITION_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_POSITION_use_preview_Update)

# AO Map Props
    map_AO_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="AO",
        update=bm_props_utils.Map_map_AO_prefix_Update)

    map_AO_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_AO_use_preview_Update)

    map_AO_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_AO_use_default_Update)

    map_ao_samples: IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",  # noqa: E501
        default=16,
        min=1,
        max=128,
        update=bm_props_utils.Map_map_ao_samples_Update)

    map_ao_distance: FloatProperty(
        name="Distance",
        description="Distance up to which other objects are considered to occlude the shading point",  # noqa: E501
        default=1,
        min=0,
        update=bm_props_utils.Map_map_ao_distance_Update)

    map_ao_black_point: FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_ao_black_point_Update)

    map_ao_white_point: FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",  # noqa: E501
        default=0.8,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_ao_white_point_Update)

    map_ao_brightness: FloatProperty(
        name="Brightness",
        default=-0.3,
        min=-100.0,
        max=100.0,
        update=bm_props_utils.Map_map_ao_brightness_Update)

    map_ao_contrast: FloatProperty(
        name="Contrast",
        default=0.3,
        min=-100.0,
        max=100.0,
        update=bm_props_utils.Map_map_ao_contrast_Update)

    map_ao_opacity: FloatProperty(
        name="Opacity",
        default=0.67,
        min=0.0,
        max=1.0,
        update=bm_props_utils.Map_map_ao_opacity_Update)

    map_ao_use_local: BoolProperty(
        name="Only Local",
        description="Only detect occlusion from the object itself, and not others",  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_ao_use_local_Update)

    map_ao_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_ao_use_invert_Update)

# Cavity Map Props
    map_CAVITY_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="CAV",
        update=bm_props_utils.Map_map_CAVITY_prefix_Update)

    map_CAVITY_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_CAVITY_use_preview_Update)

    map_CAVITY_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_CAVITY_use_default_Update)

    map_cavity_black_point: FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0.0,
        max=1.0,
        precision=3,
        update=bm_props_utils.Map_map_cavity_black_point_Update)

    map_cavity_white_point: FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",  # noqa: E501
        default=1,
        min=0.0,
        max=1.0,
        precision=3,
        update=bm_props_utils.Map_map_cavity_white_point_Update)

    map_cavity_power: FloatProperty(
        name="Power",
        description="Cavity map power value",
        default=2.5,
        update=bm_props_utils.Map_map_cavity_power_Update)

    map_cavity_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_cavity_use_invert_Update)

# Curvature Map Props
    map_CURVATURE_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="CURV",
        update=bm_props_utils.Map_map_CURVATURE_prefix_Update)

    map_CURVATURE_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_CURVATURE_use_preview_Update)

    map_CURVATURE_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_CURVATURE_use_default_Update)

    map_curv_samples: IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",  # noqa: E501
        default=16,
        min=2,
        max=128,
        update=bm_props_utils.Map_map_curv_samples_Update)

    map_curv_radius: FloatProperty(
        name="Radius",
        default=2.2,
        min=0,
        precision=3,
        update=bm_props_utils.Map_map_curv_radius_Update)

    map_curv_black_point: FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0.4,
        min=0.0,
        max=1.0,
        precision=3,
        update=bm_props_utils.Map_map_curv_black_point_Update)

    map_curv_mid_point: FloatProperty(
        name="Greys",
        description="Middle grey point location on the map color gradient spectrum",  # noqa: E501
        default=0.5,
        min=0.0,
        max=1.0,
        precision=3,
        update=bm_props_utils.Map_map_curv_mid_point_Update)

    map_curv_white_point: FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",  # noqa: E501
        default=0.6,
        min=0.0,
        max=1.0,
        precision=3,
        update=bm_props_utils.Map_map_curv_white_point_Update)

    map_curv_body_gamma: FloatProperty(
        name="Gamma",
        default=2.2,
        min=0.001,
        max=10,
        precision=3,
        update=bm_props_utils.Map_map_curv_body_gamma_Update)

# Thickness Map Props
    map_THICKNESS_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="THICK",
        update=bm_props_utils.Map_map_THICKNESS_prefix_Update)

    map_THICKNESS_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_THICKNESS_use_preview_Update)

    map_THICKNESS_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_THICKNESS_use_default_Update)

    map_thick_samples: IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",  # noqa: E501
        default=16,
        min=1,
        max=128,
        update=bm_props_utils.Map_map_thick_samples_Update)

    map_thick_distance: FloatProperty(
        name="Distance",
        description="Distance up to which other objects are considered to occlude the shading point",  # noqa: E501
        default=1,
        min=0,
        update=bm_props_utils.Map_map_thick_distance_Update)

    map_thick_black_point: FloatProperty(
        name="Blacks",
        description="Shadow point location on the map color gradient spectrum",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_thick_black_point_Update)

    map_thick_white_point: FloatProperty(
        name="Whites",
        description="Highlight point location on the map color gradient spectrum",  # noqa: E501
        default=1,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_thick_white_point_Update)

    map_thick_brightness: FloatProperty(
        name="Brightness",
        default=1,
        update=bm_props_utils.Map_map_thick_brightness_Update)

    map_thick_contrast: FloatProperty(
        name="Contrast",
        default=0,
        update=bm_props_utils.Map_map_thick_contrast_Update)

    map_thick_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_thick_use_invert_Update)

# Material ID Map Props
    map_ID_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="ID",
        update=bm_props_utils.Map_map_ID_prefix_Update)

    map_ID_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_ID_use_preview_Update)

    map_matid_data: EnumProperty(
        name="Data",
        description="Data type for detecting color groups",
        default='MATERIALS',
        items=[('VERTEX_GROUPS', "Vertex Groups", "Color each mesh Vertex Group differently"),  # noqa: E501
               ('MATERIALS', "Materials", "Color each mesh part each material assigned to differently"),  # noqa: E501
               ('MESH_ISLANDS', "Mesh Islands", "Color each mesh part differently"),  # noqa: E501
               ('OBJECTS', "Objects", "Color each highpoly baked onto the Object differently or the whole Object will be in one color if no highpolies")],  # noqa: E501
        update=bm_props_utils.Map_map_matid_data_Update)

    map_matid_vertex_groups_name_contains: StringProperty(
        name="Name Contains",
        description="Use only those vertex groups which name contains this. Leave empty to use all vertex groups",  # noqa: E501
        default="_id",
        update=bm_props_utils.Map_map_matid_vertex_groups_name_contains_Update)

    map_matid_algorithm: EnumProperty(
        name="Algorithm",
        description="Algorithm by which the color groups will be painted",
        default='RANDOM',
        items=[('RANDOM', "Random", "Color each group by unique Random Color"),
               ('HUE', "Hue Shift", "Color each group by unique Hue"),
               ('GRAYSCALE', "Grayscale", "Color each group by unique Grayscale Color")],  # noqa: E501
        update=bm_props_utils.Map_map_matid_algorithm_Update)

    map_matid_jilter: IntProperty(
        name="Jilter",
        description="Shuffle the order of colors. Leave 0 for no shuffle",
        default=0,
        update=bm_props_utils.Map_map_matid_jilter_Update)

# Mask Map Props
    map_MASK_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="MASK",
        update=bm_props_utils.Map_map_MASK_prefix_Update)

    map_MASK_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_MASK_use_preview_Update)

    map_mask_data: EnumProperty(
        name="Data",
        description="Data type for detecting mask black and white parts",
        default='SELECTION',
        items=[('SELECTION', "Selection", "Color selected mesh faces in one color, unselected in another"),  # noqa: E501
               ('VERTEX_GROUPS', "Vertex Groups", "Color specified vertex groups in one color, other in another"),  # noqa: E501
               ('MATERIALS', "Materials", "Color specified object materials in one color, other in another")],  # noqa: E501
        update=bm_props_utils.Map_map_mask_data_Update)

    map_mask_vertex_groups_name_contains: StringProperty(
        name="Name Contains",
        description="Use only those vertex groups which names contain this. Leave empty to use all vertex groups",  # noqa: E501
        default="_mask",
        update=bm_props_utils.Map_map_mask_vertex_groups_name_contains_Update)

    map_mask_materials_name_contains: StringProperty(
        name="Name Contains",
        description="Use only those object materials which names contain this. Leave empty to use all materials",  # noqa: E501
        default="_mask",
        update=bm_props_utils.Map_map_mask_materials_name_contains_Update)

    map_mask_color1: FloatVectorProperty(
        name="Color1",
        description="What color to use as Color1 for masking",
        default=(0, 0, 0, 1),
        size=4,
        min=0,
        max=1,
        precision=3,
        subtype='COLOR',
        update=bm_props_utils.Map_map_mask_color1_Update)

    map_mask_color2: FloatVectorProperty(
        name="Color2",
        description="What color to use as Color2 for masking",
        default=(1, 1, 1, 1),
        size=4,
        min=0,
        max=1,
        precision=3,
        subtype='COLOR',
        update=bm_props_utils.Map_map_mask_color2_Update)

    map_mask_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_mask_use_invert_Update)

# XYZMask Map Props
    map_XYZMASK_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="XYZ",
        update=bm_props_utils.Map_map_XYZMASK_prefix_Update)

    map_XYZMASK_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_XYZMASK_use_preview_Update)

    map_XYZMASK_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_XYZMASK_use_default_Update)

    map_xyzmask_use_x: BoolProperty(
        name="X",
        description="Enable/disable X coordinate mask filter",
        default=False,
        update=bm_props_utils.Map_map_xyzmask_use_x_Update)

    map_xyzmask_use_y: BoolProperty(
        name="Y",
        description="Enable/disable Y coordinate mask filter",
        default=False,
        update=bm_props_utils.Map_map_xyzmask_use_y_Update)

    map_xyzmask_use_z: BoolProperty(
        name="Z",
        description="Enable/disable Z coordinate mask filter",
        default=False,
        update=bm_props_utils.Map_map_xyzmask_use_z_Update)

    map_xyzmask_coverage: FloatProperty(
        name="Coverage",
        default=0,
        precision=3,
        update=bm_props_utils.Map_map_xyzmask_coverage_Update)

    map_xyzmask_saturation: FloatProperty(
        name="Saturation",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_xyzmask_saturation_Update)

    map_xyzmask_opacity: FloatProperty(
        name="Opacity",
        default=1,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_xyzmask_opacity_Update)

    map_xyzmask_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=1,
        min=-1,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_xyzmask_use_invert_Update)

# GradientMask Map Props
    map_GRADIENT_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="GRADIENT",
        update=bm_props_utils.Map_map_GRADIENT_prefix_Update)

    map_GRADIENT_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_GRADIENT_use_preview_Update)

    map_GRADIENT_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_GRADIENT_use_default_Update)

    map_gmask_type: EnumProperty(
        name="Type",
        description="Style of color blending",
        items=[("LINEAR", "Linear", "Create a linear progression"),
                 ("QUADRATIC", "Quadratic", "Create a quadratic progression"),
                 ("EASING", "Easing", "Create progression easing from one step to the next"),  # noqa: E501
                 ("DIAGONAL", "Diagonal", "Create a diagonal progression"),
                 ("SPHERICAL", "Spherical", "Create a spherical progression"),
                 ("QUADRATIC_SPHERE", "Quadratic Sphere", "Create a quadratic progression in the shape of a sphere"),  # noqa: E501
                 ("RADIAL", "Radial", "Create a radial progression")],
        update=bm_props_utils.Map_map_gmask_type_Update)

    map_gmask_location_x: FloatProperty(
        name="X Location",
        description="Gradient location by the local axis X",
        default=0,
        precision=3,
        subtype="DISTANCE",
        update=bm_props_utils.Map_map_gmask_location_x_Update)

    map_gmask_location_y: FloatProperty(
        name="Y Location",
        description="Gradient location by the local axis Y",
        default=0,
        precision=3,
        subtype="DISTANCE",
        update=bm_props_utils.Map_map_gmask_location_y_Update)

    map_gmask_location_z: FloatProperty(
        name="Z Location",
        description="Gradient location by the local axis Z",
        default=0,
        precision=3,
        subtype="DISTANCE",
        update=bm_props_utils.Map_map_gmask_location_z_Update)

    map_gmask_rotation_x: FloatProperty(
        name="X Rotation",
        description="Gradient rotation by the local axis X",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=bm_props_utils.Map_map_gmask_rotation_x_Update)

    map_gmask_rotation_y: FloatProperty(
        name="Y Rotation",
        description="Gradient rotation by the local axis Y",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=bm_props_utils.Map_map_gmask_rotation_y_Update)

    map_gmask_rotation_z: FloatProperty(
        name="Z Rotation",
        description="Gradient rotation by the local axis Z",
        default=0,
        precision=2,
        subtype="ANGLE",
        update=bm_props_utils.Map_map_gmask_rotation_z_Update)

    map_gmask_scale_x: FloatProperty(
        name="X Scale",
        description="Smoothness. Gradient scale by the local axis X",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_gmask_scale_x_Update)

    map_gmask_scale_y: FloatProperty(
        name="Y Scale",
        description="Smoothness. Gradient scale by the local axis Y",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_gmask_scale_y_Update)

    map_gmask_scale_z: FloatProperty(
        name="Z Scale",
        description="Smoothness. Gradient scale by the local axis Z",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_gmask_scale_z_Update)

    map_gmask_coverage: FloatProperty(
        name="Range of coverage",
        default=0,
        precision=3,
        update=bm_props_utils.Map_map_gmask_coverage_Update)

    map_gmask_contrast: FloatProperty(
        name="Contrast",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_gmask_contrast_Update)

    map_gmask_saturation: FloatProperty(
        name="Saturation",
        default=1,
        update=bm_props_utils.Map_map_gmask_saturation_Update)

    map_gmask_opacity: FloatProperty(
        name="Opacity",
        default=1,
        min=0,
        max=1,
        update=bm_props_utils.Map_map_gmask_opacity_Update)

    map_gmask_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_gmask_use_invert_Update)

# Edge Map Props
    map_EDGE_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="EDGE",
        update=bm_props_utils.Map_map_EDGE_prefix_Update)

    map_EDGE_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_EDGE_use_preview_Update)

    map_EDGE_use_default: BoolProperty(
        name="Default",
        description="Bake texture map using default settings",
        default=True,
        update=bm_props_utils.Map_map_EDGE_use_default_Update)

    map_edgemask_samples: IntProperty(
        name="Samples",
        description="Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance",  # noqa: E501
        default=16,
        min=2,
        max=128,
        update=bm_props_utils.Map_map_edgemask_samples_Update)

    map_edgemask_radius: FloatProperty(
        name="Radius",
        default=0.02,
        min=0,
        precision=3,
        update=bm_props_utils.Map_map_edgemask_radius_Update)

    map_edgemask_edge_contrast: FloatProperty(
        name="Edge Contrast",
        default=0,
        precision=3,
        update=bm_props_utils.Map_map_edgemask_edge_contrast_Update)

    map_edgemask_body_contrast: FloatProperty(
        name="Body Contrast",
        default=1,
        precision=3,
        update=bm_props_utils.Map_map_edgemask_body_contrast_Update)

    map_edgemask_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=1,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_edgemask_use_invert_Update)

# WireframeMask Map Props
    map_WIREFRAME_prefix: StringProperty(
        name="Prefix",
        description="Map Prefix to write in output file or layer name (if $mapname keyword is added to the Batch Name)",  # noqa: E501
        default="WIRE",
        update=bm_props_utils.Map_map_WIREFRAME_prefix_Update)

    map_WIREFRAME_use_preview: BoolProperty(
        name="Preview",
        description=BM_LABELS_Props('Map', "map_use_preview", "description").get(),  # noqa: E501
        default=False,
        update=bm_props_utils.Map_map_WIREFRAME_use_preview_Update)

    map_wireframemask_line_thickness: FloatProperty(
        name="Thickness",
        description="Thickness of uv edge",
        default=0.2,
        min=0,
        update=bm_props_utils.Map_map_wireframemask_line_thickness_Update)

    map_wireframemask_use_invert: FloatProperty(
        name="Invert",
        description="Invert colors of the map",
        default=0,
        min=0,
        max=1,
        precision=3,
        update=bm_props_utils.Map_map_wireframemask_use_invert_Update)


class Object_Highpoly(PropertyGroup):
    object_name: EnumProperty(
        name="Highpoly",
        description="Choose Highpoly for the Object from the list\n(Highpoly should be added to BakeMaster Table of Objects)",  # noqa: E501
        items=bm_props_utils.Highpoly_Items,
        update=bm_props_utils.Highpoly_Update)

    holder_index: IntProperty(default=-1)

    item_index: IntProperty()

    highpoly_name_old: StringProperty()

    highpoly_object_index: IntProperty(default=-1)

    highpoly_object_include: StringProperty(default="")


class Object_ChannelPack(PropertyGroup):
    name: StringProperty(
        name="Pack Name",
        description="Enter a Channel Pack name",
        default="ChannelPack")

    index: IntProperty(default=-1)
    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    type: EnumProperty(
        name="Pack Type",
        description="Type of packing operation describing its packing format",
        default='R1G1B1A',
        items=[('R1G1B', "R+G+B", "Select different maps for R, G, B channels"),  # noqa: E501
               ('RGB1A', "RGB+A", "Select one map to cover RGB, another for A channel"),  # noqa: E501
               ('R1G1B1A', "R+G+B+A", "Select different maps for R, G, B, A channels")])  # noqa: E501

    # R+G+B
    R1G1B_use_R: BoolProperty(
        name="Use Red Channel",
        default=True)
    R1G1B_map_R: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Red channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B_R,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B_R)
    R1G1B_map_R_index: IntProperty(default=-1)

    R1G1B_use_G: BoolProperty(
        name="Use Green Channel",
        default=True)
    R1G1B_map_G: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Green channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B_G,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B_G)
    R1G1B_map_G_index: IntProperty(default=-1)

    R1G1B_use_B: BoolProperty(
        name="Use Blue Channel",
        default=True)
    R1G1B_map_B: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Blue channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B_B,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B_B)
    R1G1B_map_B_index: IntProperty(default=-1)

    # RGB+A
    RGB1A_use_RGB: BoolProperty(
        name="Use RGB Channels",
        default=True)
    RGB1A_map_RGB: EnumProperty(
        name="Channel Map",
        description="Choose a map for the RGB channels among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_RGB1A_RGB,
        update=bm_props_utils.ChannelPack_map_Update_RGB1A_RGB)
    RGB1A_map_RGB_index: IntProperty(default=-1)

    RGB1A_use_A: BoolProperty(
        name="Use Alpha Channel",
        default=True)
    RGB1A_map_A: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Alpha channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_RGB1A_A,
        update=bm_props_utils.ChannelPack_map_Update_RGB1A_A)
    RGB1A_map_A_index: IntProperty(default=-1)

    # R+G+B+A
    R1G1B1A_use_R: BoolProperty(
        name="Use Red Channel",
        default=True)
    R1G1B1A_map_R: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Red channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B1A_R,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B1A_R)
    R1G1B1A_map_R_index: IntProperty(default=-1)

    R1G1B1A_use_G: BoolProperty(
        name="Use Green Channel",
        default=True)
    R1G1B1A_map_G: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Green channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B1A_G,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B1A_G)
    R1G1B1A_map_G_index: IntProperty(default=-1)

    R1G1B1A_use_B: BoolProperty(
        name="Use Blue Channel",
        default=True)
    R1G1B1A_map_B: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Blue channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B1A_B,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B1A_B)
    R1G1B1A_map_B_index: IntProperty(default=-1)

    R1G1B1A_use_A: BoolProperty(
        name="Use Alpha Channel",
        default=True)
    R1G1B1A_map_A: EnumProperty(
        name="Channel Map",
        description="Choose a map for the Alpha channel among added to the table of maps",  # noqa: E501
        items=bm_props_utils.ChannelPack_map_Items_R1G1B1A_A,
        update=bm_props_utils.ChannelPack_map_Update_R1G1B1A_A)
    R1G1B1A_map_A_index: IntProperty(default=-1)


class MatGroups_Item(PropertyGroup):
    material_name: StringProperty(
        name="Object's material" + BM_LABELS_Props('MatGroups_Item', "group_index", "description").get(),  # noqa: E501
        default="")

    group_index: IntProperty(
        name="Material Group Index",
        description=BM_LABELS_Props('MatGroups_Item', "group_index", "description").get(),  # noqa: E501
        default=1,
        min=1,
        step=1)


class Object(PropertyGroup):
    name: StringProperty()

    index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    use_bake: BoolProperty(
        name="Include/Exclude the object for bake",
        default=True,
        update=bm_props_utils.Object_use_bake_Update)

    is_included_in_texset: BoolProperty()

# Name matching props:
    nm_is_detached: BoolProperty(default=False)
    nm_mindex: IntProperty(default=-1)
    nm_container_name: StringProperty(default="", update=bm_props_utils.Object_nm_container_name_Update)  # noqa: E501
    nm_container_name_old: StringProperty(default="")
    nm_this_indent: IntProperty(default=0)
    nm_is_uc: BoolProperty(default=False)
    nm_is_lc: BoolProperty(default=False)
    nm_is_expanded: BoolProperty(default=True)
    nm_uc_mindex: IntProperty(default=-1)
    nm_lc_mindex: IntProperty(default=-1)
    nm_uc_index: IntProperty(default=-1)
    nm_lc_index: IntProperty(default=-1)
    nm_is_lowc: BoolProperty(default=False)
    nm_is_highc: BoolProperty(default=False)
    nm_is_cagec: BoolProperty(default=False)

    nm_uc_is_global: BoolProperty(
        name="Is Global Container",
        description="If checked, all Container's Objects settings will be configured by Container settings",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_nm_uni_container_is_Update)

# Item Decal Props:
    decal_is_decal: BoolProperty(
        name="Decal Object",
        description="Set the current Object to be Decal Object",
        default=False,
        update=bm_props_utils.Object_decal_is_decal_Update)

    decal_use_custom_camera: BoolProperty(
        name="Use Custom Camera",
        description="Use Custom Camera Object for capturing and baking decal maps",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_decal_use_custom_camera_Update)

    decal_custom_camera: PointerProperty(
        name="Camera",
        description="Choose Camera Object",
        type=bpy_types_Camera,
        update=bm_props_utils.Object_decal_custom_camera_Update)

    decal_upper_coordinate: EnumProperty(
        name="Upper Coordinate",
        description="Choose coordinate specifying where the decal's top is",
        default='+Z',
        items=[('+X', "+X", ""),
               ('+Y', "+Y", ""),
               ('+Z', "+Z", ""),
               ('-X', "-X", ""),
               ('-Y', "-Y", ""),
               ('-Z', "-Z", "")],
        update=bm_props_utils.Object_decal_upper_coordinate_Update)

    decal_boundary_offset: FloatProperty(
        name="Boundary Offset",
        description="Distance to use between decal object's bounds and captured image area bounds",  # noqa: E501
        default=0.01,
        min=-0.999,
        update=bm_props_utils.Object_decal_boundary_offset_Update)

# Item High to Lowpoly props:
    hl_use_unique_per_map: BoolProperty(
        name="Unique per map",
        description="Set unqiue High to Lowpoly Settings for each map",
        default=False,
        update=bm_props_utils.Object_hl_use_unique_per_map_Update)

    hl_is_highpoly: BoolProperty(default=False)
    hl_is_lowpoly: BoolProperty(default=False)
    hl_is_cage: BoolProperty(default=False)

    hl_is_decal: BoolProperty(
        name="Decal",
        description="Mark the current Highpoly as a Decal Object for the Lowpoly",  # noqa: E501
        default=False)

    hl_highpoly_table: CollectionProperty(type=Object_Highpoly)

    hl_highpoly_table_active_index: IntProperty(
        name="Highpoly Object",
        default=0)

    hl_decals_use_separate_texset: BoolProperty(
        name="Separate Decals",
        description="If checked, all specified decals will be baked to a separate texture set for the Object,\notherwise, decals map passes will be baked to Object's textures",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_hl_decals_use_separate_texset_Update)

    hl_decals_separate_texset_prefix: StringProperty(
        name="Decals TexSet prefix",
        description="What prefix to add in the end of image name for decals texture set",  # noqa: E501
        default="_decals",
        update=bm_props_utils.Object_hl_decals_separate_texset_prefix_Update)

    hl_use_cage: BoolProperty(
        name="Use Cage Object",
        description="Cast rays to Object from cage",
        default=False,
        update=bm_props_utils.Object_hl_use_cage_Update)

    hl_cage_type: EnumProperty(
        name="Cage type",
        description="Type of Cage properties to use",
        items=[('STANDARD', "Standard", "Standard Cage properties of Cycles Bake.\nSet extrusion, ray distance, and choose cage object"),  # noqa: E501
               ('SMART', "Smart", "Auto cage creation using lowpoly mesh displace. Saves time with simple cage")],  # noqa: E501
        update=bm_props_utils.Object_hl_cage_type_Update)

    hl_cage_extrusion: FloatProperty(
        name="Cage Extrusion",
        description="Inflate by the specified distance to create cage",
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=bm_props_utils.Object_hl_cage_extrusion_Update)

    hl_max_ray_distance: FloatProperty(
        name="Max Ray Distance",
        description="The maximum ray distance for matching points between the high and lowpoly. If zero, there is no limit",  # noqa: E501
        default=0,
        min=0,
        max=1,
        precision=2,
        subtype='DISTANCE',
        update=bm_props_utils.Object_hl_max_ray_distance)

    hl_cage: EnumProperty(
        name="Cage Object",
        description="Object to use as cage instead of calculating with cage extrusion",  # noqa: E501
        items=bm_props_utils.Object_hl_cage_Items,
        update=bm_props_utils.Object_hl_cage_Update)

    hl_cage_name_old: StringProperty()

    hl_cage_object_index: IntProperty(default=-1)

    hl_cage_object_include: StringProperty(default="")

# Item UV Props:
    uv_use_unique_per_map: BoolProperty(
        name="Unique per map",
        description="Set unqiue UV Settings for each map",
        default=False,
        update=bm_props_utils.Object_uv_use_unique_per_map_Update)

    uv_bake_data: EnumProperty(
        name="Bake Data",
        description="Choose data type to use for baking",
        default='OBJECT_MATERIALS',
        items=[('OBJECT_MATERIALS', "Object/Materials", "Use Object and Materials data for baking regular maps"),  # noqa: E501
               ('VERTEX_COLORS', "Vertex Colors", "Bake VertexColor Layers to Image Textures")],  # noqa: E501
        update=bm_props_utils.Object_uv_bake_data_Update)

    uv_bake_target: EnumProperty(
        name="Bake Target",
        description="Choose Baked Maps output target",
        items=bm_props_utils.Object_uv_bake_target_Items,
        update=bm_props_utils.Object_uv_bake_target_Update)

    uv_active_layer: EnumProperty(
        name="Active UV Map",
        description="Choose active UVMap layer to use in the bake.\nIf mesh has got no UV layers and at least one map to be baked to image texture, auto UV unwrap will be proceeded",  # noqa: E501
        items=bm_props_utils.Object_uv_active_layer_Items)

    uv_type: EnumProperty(
        name="UV Map Type",
        description="Set the chosen Active UV Map type",
        items=bm_props_utils.Object_uv_type_Items,
        update=bm_props_utils.Object_uv_type_Update)

    uv_snap_islands_to_pixels: BoolProperty(
        name="Snap UV to pixels",
        description="Make chosen UV Layer pixel perfect by aligning UV Coordinates to pixels' corners/edges",  # noqa: E501
        update=bm_props_utils.Object_uv_snap_islands_to_pixels_Update)

    uv_use_auto_unwrap: BoolProperty(
        name="Auto Unwrap",
        description="Auto UV Unwrap object using smart project. If UV Type is UDIMs, enabling Auto Unwrap will ignore it.\nWarning: if Object has materials that depend on UV Layout, enabling this option might change the result of these materials",  # noqa: E501
        update=bm_props_utils.Object_uv_use_auto_unwrap_Update)

    uv_auto_unwrap_angle_limit: IntProperty(
        name="Angle Limit",
        description="The angle at which to place seam on the mesh for unwrapping",  # noqa: E501
        default=66,
        min=0,
        max=89,
        subtype='ANGLE',
        update=bm_props_utils.Object_uv_auto_unwrap_angle_limit_Update)

    uv_auto_unwrap_island_margin: FloatProperty(
        name="Island Margin",
        description="Set distance between adjacent UV islands",
        default=0.01,
        min=0,
        max=1,
        update=bm_props_utils.Object_uv_auto_unwrap_island_margin_Update)

    uv_auto_unwrap_use_scale_to_bounds: BoolProperty(
        name="Scale to Bounds",
        description="Scale UV coordinates to bounds to fill the whole UV tile area",  # noqa: E501
        default=True,
        update=bm_props_utils.Object_uv_auto_unwrap_use_scale_to_bounds_Update)

# Item Material Groups Props:
    matgroups: CollectionProperty(type=MatGroups_Item)

    matgroups_active_index: IntProperty(
        name="Object's material",
        default=-1)

    matgroups_len: IntProperty(default=0)

    matgroups_batch_naming_type: EnumProperty(
        name="Mat Groups naming",
        description="How to name material groups in the output image batch name if it contains $matgroup tag",  # noqa: E501
        default='GROUP_INDEX',
        items=[('GROUP_INDEX', 'Index', "Put material group index into the batch name"),  # noqa: E501
               ('GROUP_NAMES', 'Materials names', "Put material names with the same group index into the batch name")],  # noqa: E501
        update=bm_props_utils.Object_matgroups_batch_naming_type_Update)

# Item Output Props:
    out_use_unique_per_map: BoolProperty(
        name="Unique per map",
        description="Set unqiue Output Settings for each map",
        default=False,
        update=bm_props_utils.Object_out_use_unique_per_map_Update)

    out_use_denoise: BoolProperty(
        name="Denoise",
        description="Denoise and Discpeckle baked maps as a post-process filter. For external bake only",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_out_use_denoise_Update)

    out_use_scene_color_management: BoolProperty(
        name="Scene Color Management",
        description="Affect baked map by scene color management settings and compositor nodes. For external bake only",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_out_use_scene_color_management_Update)

    out_file_format: EnumProperty(
        name="File Format",
        description="File format of output image files",
        default='PNG',
        items=[('BMP', "BMP", "Output image in bitmap format"),
               ('PNG', "PNG", "Output image in common PNG format. Best file format for true-color images that need perfect tone balance. Default Blender image format.\n\nPros: can contain Alpha Channel"),  # noqa: E501
               ('JPEG', "JPEG", "Output image in JPEG format. Uncompressed file format and takes the most amount of data and is the exact representation of the image. \n\nCons: With every edit and resave the image quality will deteriorate.\nPros: lightweight"),  # noqa: E501
               ('TIFF', "TIFF", "Output image in TIFF format. Photographic file standard in print"),  # noqa: E501
               ('OPEN_EXR', "EXR", "Output image in EXR format. High-dynamic-range bitmap image file for storing large range of color. Common for Displacement and Normal-like maps")],  # noqa: E501
               # ('PSD', "PSD", "Output image in Photoshop PSD layers. All baked maps for current Object will be saved to a single .psd file")],  # noqa: E501
        update=bm_props_utils.Object_out_file_format_Update)

    # out_psd_include: EnumProperty(
    #     name="PSD includes",
    #     description="What maps to put into one PSD file",
    #     default='MAP',
    #     items=[('MAP', "One map", "Each baked map - separate psd file"),
    #          # ('ALL_MAPS', "All object's maps", "All object's maps into single PSD file")],  # noqa: E501
    #     update=bm_props_utils.Object_OutputSettings_Update)

    out_exr_codec: EnumProperty(
        name="Codec",
        description="Codec settigns for OpenEXR file format. Choose between lossless and lossy compression",  # noqa: E501
        default='ZIP',
        items=[('NONE', "None", ""),
               ('PXR24', "Pxr24 (Lossy)", ""),
               ('ZIP', "ZIP (Lossless)", ""),
               ('PIZ', "PIZ (lossless)", ""),
               ('RLE', "RLE (lossless)", ""),
               ('ZIPS', "ZIPS (lossless)", ""),
               ('DWAA', "DWAA (lossy)", ""),
               ('DWAB', "DWAB (lossy)", "")],
        update=bm_props_utils.Object_out_exr_codec_Update)

    out_compression: IntProperty(
        name="Compression",
        description="0 - no compression performed, raw file size. 100 - full compression, takes more time, but descreases output file size",  # noqa: E501
        default=15,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        update=bm_props_utils.Object_out_compression_Update)

    out_res: EnumProperty(
        name="Map Texture Resolution",
        description="Choose map resolution in pixels from the common ones or set custom",  # noqa: E501
        default='1024',
        items=[('512', "1/2K (512x512)", ""),
               ('1024', "1K (1024x1024)", ""),
               ('2048', "2K (2048x2048)", ""),
               ('4096', "4K (4096x4096)", ""),
               ('8192', "8K (8192x8192)", ""),
               ('CUSTOM', "Custom", "Enter custom height and width")],
               # ('TEXEL', "Texel Density defined", "Define image resolution based on object's texel density")],  # noqa: E501
        update=bm_props_utils.Object_out_res_Update)

    out_res_height: IntProperty(
        name="Height",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=bm_props_utils.Object_out_res_height_Update)

    out_res_width: IntProperty(
        name="Width",
        description="Custom height resolution",
        default=1000,
        min=1,
        max=65536,
        subtype='PIXEL',
        update=bm_props_utils.Object_out_res_width_Update)

    # out_texel_density_value: IntProperty(
    #     name="Texel Density",
    #     description="How many pixels should be in image per 1 unit (1m) of object's face.\nAutomatically calculated when chosen from Map Resolution List based on object's space relativity to Scene Render Resolution",  # noqa: E501
    #     default=100,
    #     min=1,
    #     max=65536,
    #     subtype='PIXEL',
    #     update=bm_props_utils.Object_OutputSettings_Update)

    # out_texel_density_match: BoolProperty(
    #     name="Match to Common",
    #     description="Recalculate chosen Texel Density so that the image resolution is set to closest common resolution in Map Resolution List.\n(If checked then, for example, when image res by Texel Density is 1891px, it will be changed to 2048px (common 2K). If unchecked, then wil remain 1891px)",  # noqa: E501
    #     default=True)

    out_margin: IntProperty(
        name="Margin",
        description="Padding. Extend bake result by specified number of pixels as a post-process filter.\nImproves baking quality by reducing hard edges visibility",  # noqa: E501
        default=16,
        min=0,
        max=64,
        subtype='PIXEL',
        update=bm_props_utils.Object_out_margin_Update)

    out_margin_type: EnumProperty(
        name="Margin Type",
        description="Algorithm for margin",
        default='ADJACENT_FACES',
        items=[('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),  # noqa: E501
               ('EXTEND', "Extend", "Extend face border pixels outwards")],
        update=bm_props_utils.Object_out_margin_type_Update)

    out_use_32bit: BoolProperty(
        name="32bit",
        description="Create image texture with 32 bit floating point depth.\nStores more color data in the image this way",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_out_use_32bit_Update)

    out_use_alpha: BoolProperty(
        name="Alpha",
        description="Create image texture with Alpha color channel",
        default=False,
        update=bm_props_utils.Object_out_use_alpha_Update)

    out_use_transbg: BoolProperty(
        name="Transparent BG",
        description="Create image texture with transparent background instead of solid black",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_out_use_transbg_Update)

    out_udim_start_tile: IntProperty(
        name="UDIM Start Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",  # noqa: E501
        default=1001,
        min=1001,
        max=2000,
        update=bm_props_utils.Object_out_udim_start_tile_Update)

    out_udim_end_tile: IntProperty(
        name="UDIM End Tile Index",
        description="UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)",  # noqa: E501
        default=1001,
        min=1001,
        max=2000,
        update=bm_props_utils.Object_out_udim_end_tile_Update)

    out_super_sampling_aa: EnumProperty(
        name="SuperSampling AA",
        description="SSAA. Improve image quality by baking at a higher resolution and then downscaling to a lower resolution. Helps removing stepping, jagging, and dramatic color difference near color area edges",  # noqa: E501
        default='1',
        items=[('1', "1x1", "No supersampling. Bake and save with chosen resolution"),  # noqa: E501
               ('2', "2x2", "Bake at 2x the chosen resolution and then downscale"),  # noqa: E501
               ('4', "4x4", "Bake at 4x the chosen resolution and then downscale"),  # noqa: E501
               ('8', "8x8", "Bake at 8x the chosen resolution and then downscale"),  # noqa: E501
               ('16', "16x16", "Bake at 16x the chosen resolution and then downscale")],  # noqa: E501
        update=bm_props_utils.Object_out_super_sampling_aa_Update)

    out_samples: IntProperty(
        name="Bake Samples",
        description="Number of samples to render per each pixel",
        default=128,
        min=1,
        max=16777216,
        update=bm_props_utils.Object_out_samples)

    out_use_adaptive_sampling: BoolProperty(
        name="Adaptive Sampling",
        description="Automatically reduce the number of samples per pixel based on estimated noise level",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_out_use_adaptive_sampling_Update)

    out_adaptive_threshold: FloatProperty(
        name="Noise Threshold",
        description="Noise level step to stop sampling at, lower values reduce noise at the cost of render time.\nZero for automatic setting based on number of AA sampled",  # noqa: E501
        default=0.01,
        min=0,
        max=1,
        soft_min=0.001,
        step=3,
        precision=4,
        update=bm_props_utils.Object_out_adaptive_threshold_Update)

    out_min_samples: IntProperty(
        name="Bake Min Samples",
        description="The minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold",  # noqa: E501
        default=0,
        min=0,
        max=4096,
        update=bm_props_utils.Object_out_min_samples_Update)

# Item Shading Correction Props
    csh_use_triangulate_lowpoly: BoolProperty(
        name="Triangulate Lowpoly",
        description="Triangulate Lowpoly mesh n-gons. Takes time but improves shading of Lowpoly mesh with redundant uv stretches",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_csh_use_triangulate_lowpoly_Update)

    csh_use_lowpoly_recalc_normals: BoolProperty(
        name="Recalculate Lowpoly Normals Outside",
        description="Recalculate Lowpoly Vertex and Face Normals Outside",
        default=False,
        update=bm_props_utils.Object_csh_use_lowpoly_recalc_normals_Update)

    csh_lowpoly_use_smooth: BoolProperty(
        name="Smooth Lowpoly",
        description="Use smooth-shaded Lowpoly for baking. Can be kept unchecked if you've set shading on your own",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_csh_lowpoly_use_smooth_Update)

    csh_lowpoly_smoothing_groups_enum: EnumProperty(
        name="Lowpoly Smoothing groups",
        description="Choose Lowpoly smooth shading groups type to apply",
        default='STANDARD',
        items=[('STANDARD', "Standard", "Apply default Shade Smooth to whole object"),  # noqa: E501
               ('AUTO', "Auto Smooth", "Apply Auto Shade Smooth based on angle between faces or mesh split normals data"),  # noqa: E501
               ('VERTEX_GROUPS', "Vertex Groups", "Apply smooth shading to created mesh vertex groups. Vertex group boundary will be marked sharped")],  # noqa: E501
        update=bm_props_utils.Object_csh_lowpoly_smoothing_groups_enum_Update)

    csh_lowpoly_smoothing_groups_angle: IntProperty(
        name="Angle",
        description="Maximum angle between face normals that will be considered as smooth\n(unused if custom split normals are available",  # noqa: E501
        default=30,
        min=0,
        max=180,
        subtype='ANGLE',
        update=bm_props_utils.Object_csh_lowpoly_smoothing_groups_angle_Update)

    csh_lowpoly_smoothing_groups_name_contains: StringProperty(
        name="Name Contains",
        description="Apply smooth shading only to vertex groups which names contain this value. Leave empty to apply to all vertex groups",  # noqa: E501
        default="_smooth",
        update=bm_props_utils.Object_csh_lowpoly_smoothing_groups_name_contains_Update)  # noqa: E501

    csh_use_highpoly_recalc_normals: BoolProperty(
        name="Recalculate Highpoly Normals Outside",
        description="Recalculate Highpoly Vertex and Face Normals Outside",
        default=False,
        update=bm_props_utils.Object_csh_use_highpoly_recalc_normals_Update)

    csh_highpoly_use_smooth: BoolProperty(
        name="Smooth Highpoly",
        description="Use smooth-shaded Highpoly for baking. Can be kept unchecked if you've set shading on your own",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_csh_highpoly_use_smooth_Update)

    csh_highpoly_smoothing_groups_enum: EnumProperty(
        name="Highpoly Smoothing groups",
        description="Choose Highpoly smooth shading groups type to apply",
        default='STANDARD',
        items=[('STANDARD', "Standard", "Apply default Shade Smooth to whole object"),  # noqa: E501
               ('AUTO', "Auto Smooth", "Apply Auto Shade Smooth based on angle between faces or mesh split normals data"),  # noqa: E501
               ('VERTEX_GROUPS', "Vertex Groups", "Apply smooth shading to created mesh vertex groups. Vertex group boundary will be marked sharped")],  # noqa: E501
        update=bm_props_utils.Object_csh_highpoly_smoothing_groups_enum_Update)

    csh_highpoly_smoothing_groups_angle: IntProperty(
        name="Angle",
        description="Maximum angle between face normals that will be considered as smooth\n(unused if custom split normals are available",  # noqa: E501
        default=30,
        min=0,
        max=180,
        subtype='ANGLE',
        update=bm_props_utils.Object_csh_highpoly_smoothing_groups_angle_Update)  # noqa: E501

    csh_highpoly_smoothing_groups_name_contains: StringProperty(
        name="Name Contains",
        description="Apply smooth shading only to vertex groups which names contain this value",  # noqa: E501
        default="_smooth",
        update=bm_props_utils.Object_csh_highpoly_smoothing_groups_name_contains_Update)  # noqa: E501

# Item Maps Collection Props
    maps_active_index: IntProperty(
        name="Configure maps to bake",
        default=-1)

    maps: CollectionProperty(type=Map)

    maps_len: IntProperty(default=0)

# Item Channel Packing Props
    chnlps: CollectionProperty(type=Object_ChannelPack)

    chnlps_active_index: IntProperty(
        name="Channel Pack",
        default=0)

    chnlps_len: IntProperty(default=0)

# Item Bake Props
    bake_save_internal: BoolProperty(
        name="Internal",
        description="Pack baked maps into the current Blender file",
        default=True,
        update=bm_props_utils.Object_bake_save_internal_Update)

    bake_output_filepath: StringProperty(
        name="Output Path",
        description="Directory path on your disk to save baked maps to",
        default="",
        subtype='DIR_PATH',
        update=bm_props_utils.Object_bake_output_filepath_Update)

    bake_create_subfolder: BoolProperty(
        name="Create Subfolder",
        description="Create subfolder in the Output Path directory and save baked maps there",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_bake_create_subfolder_Update)

    bake_subfolder_name: StringProperty(
        name="Subfolder Name",
        description="How to name the subfolder",
        default="Maps",
        update=bm_props_utils.Object_bake_subfolder_name_Update)

    bake_batchname: StringProperty(
        name="Batch Name",
        description=BM_LABELS_Props('Object', "bake_batchname", "description").get(),  # noqa: E501
        default="$objectindex_$objectname_$mapname",
        update=bm_props_utils.Object_bake_batchname_Update)

    bake_batchname_use_caps: BoolProperty(
        name="Use Caps",
        description="Use capital letters for batch name",
        default=False,
        update=bm_props_utils.Object_bake_batchname_use_caps_Update)

    # bake_batchname_preview: StringProperty(
    #     name="Preview",
    #     description="Output file batch name preview (might change for each map)")  # noqa: E501

    bake_create_material: BoolProperty(
        name="Create Material",
        description="Assign a new material to the object after bake with all baked maps included",  # noqa: E501
        default=False,
        update=bm_props_utils.Object_bake_create_material_Update)

    bake_assign_modifiers: BoolProperty(
        name="Assign Modifiers",
        description="If Object maps like Displacement or Vector Displacement have Result to Modifiers, modifiers will be assigned if this is checked. If unchecked, baked maps will be just saved to image textures",  # noqa: E501
        default=True,
        update=bm_props_utils.Object_bake_assign_modifiers_Update)

    bake_device: EnumProperty(
        name="Bake Device",
        description="Device to use for baking",
        default='CPU',
        items=[('GPU', "GPU", "Use GPU compute device for baking, configured in the system tab in the user preferences"),  # noqa: E501
               ('CPU', "CPU", "Use CPU for baking")],
        update=bm_props_utils.Object_bake_device_Update)

    bake_view_from: EnumProperty(
        name="Bake View from",
        description="Source of reflection ray directions",
        default='ABOVE_SURFACE',
        items=[('ABOVE_SURFACE', "Above Surface", "Cast rays from above the surface. Default"),  # noqa: E501
               ('ACTIVE_CAMERA', "Active Camera", "Use the active scene camera's position to cast rays")],  # noqa: E501
        update=bm_props_utils.Object_bake_view_from_Update)

    bake_hide_when_inactive: BoolProperty(
        name="Hide when Inactive",
        description="If checked, Object's Mesh will not affect any other Objects while baking",  # noqa: E501
        default=True,
        update=bm_props_utils.Object_bake_hide_when_inactive_Update)

    bake_vg_index: IntProperty(
        name="VG Index",
        description="Object's Mesh will affect other Objects Meshes if their Visibility Group Indexes are equal to the same value.\nThe effect is noticeable in areas where Meshes intersect",  # noqa: E501
        default=0,
        min=0,
        step=1,
        update=bm_props_utils.Object_bake_vg_index_Update)


class RedoLastAction_Object(PropertyGroup):
    name: StringProperty(
        name="Object name",
        default="")

    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    use_affect: BoolProperty(
        name="Apply",
        description="Apply property for this object",
        default=True)


class RedoLastAction_Map(PropertyGroup):
    name: StringProperty(
        name="Map name",
        default="")

    bm_object_index: IntProperty(default=-1)

    bm_map_index: IntProperty(default=-1)

    use_affect: BoolProperty(
        name="Apply",
        description="Apply property for this map",
        default=True)


class BakeGroup(PropertyGroup):
    name: StringProperty(
        name="Object name",
        default="")

    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    is_lowpoly: BoolProperty(
        name="Inlcude as Lowpoly",
        description="Include this object as a regular or Lowpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=bm_props_utils.BakeGroup_use_include_Update)

    is_highpoly: BoolProperty(
        name="Include as Highpoly",
        description="Include this object as a Highpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=bm_props_utils.BakeGroup_is_highpoly_Update)

    is_cage: BoolProperty(
        name="Include as Cage",
        description="Include this object as a Highpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=bm_props_utils.BakeGroup_is_cage_Update)


class MatchRes(PropertyGroup):
    image_name: StringProperty(
        name="Image Texture name",
        default="Image")

    socket_and_node_name: StringProperty(
        name="Plugged into",
        default="*Not plugged*")

    image_res: StringProperty(
        name="Resolution",
        default="")

    image_height: IntProperty(default=1)
    image_width: IntProperty(default=1)


class TexSet_Object_Subitem(PropertyGroup):
    name: StringProperty(
        name="Container's Lowpoly Object")

    index: IntProperty(default=-1)
    texset_object_index: IntProperty(default=-1)
    texset_index: IntProperty(default=-1)
    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    use: BoolProperty(
        name="Include/Exclude from Texture Set",
        description="Include/Exclude Container's Lowpoly Object from the current Texture Set",  # noqa: E501
        default=True)


class TexSet_Object(PropertyGroup):
    name: EnumProperty(
        name="Choose Object",
        description="Object from the current Bake Job Objects to inlcude in the current Texture Set.\nIf Container's chosen, all its lowpoly objects will be added to the Texture Set",  # noqa: E501
        items=bm_props_utils.TexSet_Object_name_Items,
        update=bm_props_utils.TexSet_Object_name_Update)

    index: IntProperty(default=-1)
    texset_index: IntProperty(default=-1)
    object_index: IntProperty(default=-1)
    bakejob_index: IntProperty(default=-1)

    name_old: StringProperty(default='-1')

    name_include: StringProperty(default="")

    subitems: CollectionProperty(type=TexSet_Object_Subitem)

    subitems_active_index: IntProperty(name="Container's Lowpoly Object")

    subitems_len: IntProperty(default=0)


class TexSet(PropertyGroup):
    name: StringProperty(
            name="Texture Set Name.\nTexture Set is a set of objects that share the same image texture file for each map",  # noqa: E501
        default="Texture Set")

    index: IntProperty(default=-1)

    syncer_use: BoolProperty(
        name="",
        description="Enable one object to dictate maps, channel packs, and bake settings for all others in the current texture set",  # noqa: E501
        default=False)

    syncer_object_name: EnumProperty(
        name="Sync with",
        description="Choose an object from the ones in the current texture set",  # noqa: E501
        items=bm_props_utils.TexSet_Object_syncer_Items)

    syncer_use_dictate_bake_output: BoolProperty(
        name="Sync Bake Output Settings",
        description="Channel packs and maps settings are synced with enabling 'Sync with', check this option to sync bake settings as well",  # noqa: E501
        default=True)

    uvp_use_uv_repack: BoolProperty(
        name="UV Repack",
        description="Enable UV Repacking for Texture Set Objects.\nWarning: if Objects have materials that depend on UV Layout, enabling this option might change the result of these materials",  # noqa: E501
        default=False)

    uvp_use_islands_rotate: BoolProperty(
        name="Rotate",
        description="Rotate islands for best fit",
        default=False)

    uvp_pack_margin: FloatProperty(
        name="Margin",
        description="Space between packed islands",
        default=0.01,
        min=0.0,
        max=1.0)

    uvp_use_average_islands_scale: BoolProperty(
        name="Average Islands Scale",
        description="Average the size of separate UV islands, based on their area in 3D space",  # noqa: E501
        default=True)

    naming: EnumProperty(
        name="Naming",
        description="Choose output Image texture naming format",
        default='TEXSET_NAME',
        items=[('EACH_OBJNAME', "Each Object Name", "Include each texture set object name in the output texture set image"),  # noqa: E501
               ('TEXSET_INDEX', "Texture Set Index", "Name output texture set image in the format: TextureSet_index"),  # noqa: E501
               ('TEXSET_NAME', "Texture Set Name", "Output texture name will be as Texture Set name")])  # noqa: E501

    texset_objects: CollectionProperty(type=TexSet_Object)

    texset_objects_active_index: IntProperty(
        name="Object in the Texture Set",
        default=0)

    texset_objects_len: IntProperty(default=0)


class BakeJob(PropertyGroup):
    # Bake Job Props

    name: StringProperty(
        name="Bake Job",
        description="Double click to rename",
        default="Bake Job")

    index: IntProperty(default=-1)

    # TODO: Redo Last Action update
    use_bake: BoolProperty(
        name="Include/Exclude Bake Job from baking",
        default=True)

    objects: CollectionProperty(type=Object)

    objects_active_index: IntProperty(
        name="Mesh Object to bake maps for",
        default=0,
        update=bm_props_utils.BakeJob_objects_active_index_Update)

    objects_len: IntProperty(default=0)

    use_name_matching: BoolProperty(
        name="Toggle Name Matching",
        description="If on, High, Lowpoly, and Cage objects will be grouped by their matched names.\nProperties like Highpoly object and Cage will be set automatically if possible, maps and other settings can be configured by the top-parent container",  # noqa: E501
        default=False,
        update=bm_props_utils.BakeJob_use_name_matching_Update)

    use_save_log: BoolProperty(
        name="Save Log",
        description="Save log of time used to bake each map and a short summary of all baked maps for all baked objects into a .txt file",  # noqa: E501
        default=False)

    use_bake_overwrite: BoolProperty(
        name="Overwrite",
        description="If checked, previous bake result will be erased and overwritten by the new one",  # noqa: E501
        default=False)

    texsets: CollectionProperty(type=TexSet)

    texsets_active_index: IntProperty(
        name="Texture Set.\nTexture Set is a set of objects that share the same image texture file for each map",  # noqa: E501
        default=-1)

    texsets_len: IntProperty(default=0)


class Global(PropertyGroup):
    # Bake Jobs Props

    bakejobs: CollectionProperty(type=BakeJob)

    bakejobs_active_index: IntProperty(
        name="Bake Job",
        description="Active Bake Job",
        default=-1)

    bakejobs_len: IntProperty(default=0)

    # Addon Preferences Props

    prefs_use_show_help: BoolProperty(
        name="Show Help buttons",
        description="Allow help buttons in panels' headers",
        default=True)

    prefs_use_pipeline: BoolProperty(
        name="Bake Pipeline",
        description="Enable/disable Bake Pipeline settings (Bake Configs save/load, Atlas Management, Asset Matching)",  # noqa: E501
        default=False)

    prefs_use_hide_notbaked: BoolProperty(
        name="Hide not baked",
        description="Hide all Objects in the scene that won't be baked, as such they won't affect it",  # noqa: E501
        default=True)

    prefs_texsets_matchmaps_type: EnumProperty(
        name="Maps Match type",
        description="Determine map matching for Texture Sets aka how to source maps that should be baked onto the same image texture",  # noqa: E501
        default='MAP_PREFIX',
        items=[('MAP_PREFIX', "Maps Prefixes", "Maps with identical prefixes will be baked onto the same image file"),  # noqa: E501
               ('MAP_TYPE', "Maps Types", "Maps of identical types will be baked onto the same image file"),  # noqa: E501
               ('MAP_PREFIX_AND_TYPE', "Both Type and Prefix", "Maps with identical prefixes will be baked onto the same image file.\nIf no identical prefixes found, BakeMaster will try to match maps of the same type")])  # noqa: E501

    prefs_texsets_use_matching: BoolProperty(
        name="Match TexSets",
        description="When enabling Name Matching, if this option is checked, Objects with TexSet Tag in their names will be auto matched and put into Texture Sets",  # noqa: E501
        default=True)

    prefs_lowpoly_tag: StringProperty(
        name="Lowpoly Tag",
        description="What keyword to search for in Object name to determine it's a Lowpoly Object",  # noqa: E501
        default="low")

    prefs_highpoly_tag: StringProperty(
        name="Highpoly Tag",
        description="What keyword to search for in Object name to determine it's a Highpoly Object",  # noqa: E501
        default="high")

    prefs_cage_tag: StringProperty(
        name="Cage Tag",
        description="What keyword to search for in Object name to determine it's a Cage Object",  # noqa: E501
        default="cage")

    prefs_decal_tag: StringProperty(
        name="Decal Tag",
        description="What keyword to search for in Object name to determine it's a Decal Object",  # noqa: E501
        default="decal")

    prefs_texset_tag: StringProperty(
        name="TexSet Tag",
        description="What keyword to search for in Object name to determine it should be put into Texture Set (If Match TexSets enabled)",  # noqa: E501
        default="texset")

    prefs_bake_uv_layer_tag: StringProperty(
        name="UVMap Tag",
        description="What UVMap name should contain for BakeMaster to higher up its priority in Active UV Layer items",  # noqa: E501
        default="bake")

    # Redo Last Action Props

    redolastaction_prop: StringProperty(default="")
    redolastaction_prop_name: StringProperty(default="")
    redolastaction_prop_value: StringProperty(default="")
    redolastaction_prop_type: StringProperty(default="")
    redolastaction_prop_is_map: BoolProperty(default=False)

    redolastaction_objects: CollectionProperty(type=RedoLastAction_Object)  # noqa: E501

    redolastaction_objects_active_index: IntProperty(
        name="Object",
        default=-1)

    redolastaction_maps: CollectionProperty(type=RedoLastAction_Map)  # noqa: E501

    redolastaction_maps_active_index: IntProperty(
        name="Map",
        default=-1)

    redolastaction_affect_objects: BoolProperty(
        name="Affect Objects",
        description="Apply property to all maps of chosen objects",
        default=False)

    redolastaction_objects_len: IntProperty(default=0)

    # Bake Group Props
    bakegroup_objects: CollectionProperty(type=BakeGroup)

    bakegroup_objects_active_index: IntProperty(
        name="Detached Object",
        default=-1)

    bakegroup_objects_len: IntProperty(default=0)

    # Math Res Props
    matchres_items: CollectionProperty(type=MatchRes)

    matchres_items_active_index: IntProperty(
        name="Resolution, Image name, Plugged into",
        default=0)

    mathres_items_len: IntProperty(default=0)

    # Panels UI Props

    is_decal_panel_expanded: BoolProperty(
        name="Expand/Collapse Decal Settings panel",
        default=False)

    is_hl_panel_expanded: BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    is_uv_panel_expanded: BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    is_matgroups_panel_expanded: BoolProperty(
        name="Expand/Collapse Material Groups panel",
        default=False)

    is_csh_panel_expanded: BoolProperty(
        name="Expand/Collapse Shading Settings panel",
        default=False)

    is_format_panel_expanded: BoolProperty(
        name="Expand/Collapse Format Settings panel",
        default=False)

    is_chnlpack_panel_expanded: BoolProperty(
        name="Expand/Collapse Channel Packing panel",
        default=False)

    is_bakeoutput_panel_expanded: BoolProperty(
        name="Expand/Collapse Bake Output Settings panel",
        default=False)

    is_map_hl_panel_expanded: BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    is_map_uv_panel_expanded: BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    # Idle Bake Props

    use_bakemaster_reset: BoolProperty(
        name="Reset BakeMaster",
        description="Remove baked objects from BakeMaster Table of Objects after the bake",  # noqa: E501
        default=False)

    bake_instruction: StringProperty(
        name="Bake Operator Instruction",
        default="Short Bake Instruction",
        description=BM_LABELS_Props('Global', "bake_instruction", "description").get())  # noqa: E501

    is_bake_available: BoolProperty(
        default=True)
