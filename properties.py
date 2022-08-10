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
from .utils import *
from .labels import BM_Labels

class BM_SceneProps(bpy.types.PropertyGroup):
    active_index : bpy.props.IntProperty(
        name = BM_Labels.PROP_AOL_ACTIVEINDEX_NAME,
        default = 0,
        update = BM_ActiveIndexUpdate)
    
    use_background_bake : bpy.props.BoolProperty(
        name = "Bake in the background",
        description = BM_Labels.PROP_ITEM_USEBGBAKE_DESCRIPTION,
        default = False)

    use_islands_rotate : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USEISLANDSROTATE_DESCRIPTION,
        default = False)

    uv_pack_margin : bpy.props.FloatProperty(
        name = "Margin",
        description = "Space between packed islands",
        default = 0.01,
        min = 0.0,
        max = 1.0)

    use_bakemaster_reset : bpy.props.BoolProperty(
        name = "Clear bake items list based on bake option",
        description = BM_Labels.PROP_ITEM_USERESETAFTERBAKE_DESCRIPTION,
        default = True)

    bake_instruction : bpy.props.StringProperty(
        name = "Bake Operator Instruction",
        default = "Bake Instruction",
        description=BM_Labels.OPERATOR_ITEM_BAKE_FULL_DESCRIPTION)

    bake_available : bpy.props.BoolProperty(default = True)

class BM_Item_Map(bpy.types.PropertyGroup):
    use_bake : bpy.props.BoolProperty(
        name = BM_Labels.PROP_ITEM_MAP_USEBAKE_NAME,
        default = True)

    map_type : bpy.props.EnumProperty(
        name = "Choose Map Type",
        description = BM_Labels.PROP_ITEM_MAPTYPE_DESCRIPTION,
        items = BM_ITEM_Maps_Items,
        update = BM_ITEM_RemoveLocalPreviews)

#Map Settings
    bake_target : bpy.props.EnumProperty(
        name = "Target",
        description = "Where to output the baked map",
        items = BM_ITEM_Map_BakeTarget_Items)

    use_denoise : bpy.props.BoolProperty(
        name = "Denoise baked images",
        description = BM_Labels.PROP_ITEM_MAP_USEDENOISE_DESCRIPTION,
        default = False)

    file_format : bpy.props.EnumProperty(
        name = "File Format",
        description = BM_Labels.PROP_ITEM_FILEFORMAT_DESCRIPTION,
        default = 'PNG',
        items = [('BMP', "BMP", ""),
                 ('PNG', "PNG", ""),
                 ('JPEG', "JPEG", ""),
                 ('TIFF', "TIFF", ""),
                 ('OPEN_EXR', "EXR", "")])

    res_enum : bpy.props.EnumProperty(
        name = "Resolution",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = '1024',
        items = [('512', "1/2K (512x512)", ""),
                 ('1024', "1K (1024x1024)", ""),
                 ('2048', "2K (2048x2048)", ""),
                 ('4096', "4K (4096x4096)", ""),
                 ('8192', "8K (8192x8192)", ""),
                 ('CUSTOM', "Custom", "")])

    res_height : bpy.props.IntProperty(
        name = "Height",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = 1000,
        min = 1,
        max = 32768,
        subtype = 'PIXEL')

    res_width : bpy.props.IntProperty(
        name = "Width",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = 1000,
        min = 1,
        max = 32768,
        subtype = 'PIXEL')

    margin : bpy.props.IntProperty(
        name = "Margin",
        description = BM_Labels.PROP_ITEM_MARGIN_DESCRIPTION,
        default = 16,
        min = 0,
        max = 64,
        subtype = 'PIXEL')
    
    margin_type : bpy.props.EnumProperty(
        name = "Margin Type",
        description = "Algorithm to extend the baked result",
        default = 'ADJACENT_FACES',
        items = [('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),
                 ('EXTEND', "Extend", "Extend border pixels outwards")])

    use_32bit : bpy.props.BoolProperty(
        name = "32 bit Float",
        description = BM_Labels.PROP_ITEM_USE32BIT_DESCRIPTION,
        default = False)

    use_alpha : bpy.props.BoolProperty(
        name = "Alpha",
        description = BM_Labels.PROP_ITEM_USEALPHA_DESCRIPTION,
        default = False)

    use_source_target : bpy.props.BoolProperty(
        name = "Source-Target effect",
        description = BM_Labels.PROP_ITEM_MAP_USESTT_NAME,
        default = False,
        update = BM_MAP_AffectBySouce_Update)

    udim_start_tile : bpy.props.IntProperty(
        name = "UDIM Start Tile Index",
        description = BM_Labels.PROP_ITEM_UVTILEDINDEXES_DESCRIPTION,
        default = 1001,
        min = 1001,
        max = 2000)
    
    udim_end_tile : bpy.props.IntProperty(
        name = "UDIM Start Tile Index",
        description = BM_Labels.PROP_ITEM_UVTILEDINDEXES_DESCRIPTION,
        default = 1001,
        min = 1001,
        max = 2000)

#Cycles Map Settings 
    cycles_use_pass_direct : bpy.props.BoolProperty(
        name = "Direct",
        description = BM_Labels.PROP_ITEM_CYCLES_USEDIRECT_DESCRIPTION,
        default = True)
    
    cycles_use_pass_indirect : bpy.props.BoolProperty(
        name = "Indirect",
        description = BM_Labels.PROP_ITEM_CYCLES_USEINDIRECT_DESCRIPTION,
        default = True)

    cycles_use_pass_color : bpy.props.BoolProperty(
        name = "Color",
        description = BM_Labels.PROP_ITEM_CYCLES_USECOLOR_DESCRIPTION,
        default = True)
    
    cycles_use_pass_diffuse : bpy.props.BoolProperty(
        name = "Diffuse",
        description = "Add %s contribution" % "Diffuse",
        default = True)

    cycles_use_pass_glossy : bpy.props.BoolProperty(
        name = "Glossy",
        description = "Add %s contribution" % "Glossy",
        default = True)

    cycles_use_pass_transmission : bpy.props.BoolProperty(
        name = "Transmission",
        description = "Add %s contribution" % "Transmission",
        default = True)

    cycles_use_pass_ambient_occlusion : bpy.props.BoolProperty(
        name = "Ambient Occlusion",
        description = "Add %s contribution" % "Ambient Occlusion",
        default = True)

    cycles_use_pass_emit : bpy.props.BoolProperty(
        name = "Emit",
        description = "Add %s contribution" % "Emit",
        default = True)

#Normal Map Settings
    normal_space : bpy.props.EnumProperty(
        name = "Normal Space",
        description = BM_Labels.PROP_ITEM_CYCLES_NORMALSPACE_DESCRIPTION,
        default = 'TANGENT',
        items = [('TANGENT', "Tangent", ""),
                 ('OBJECT', "Object", "")])

    normal_r : bpy.props.EnumProperty(
        name = "Normal Space",
        description = "Axis to bake in %s channel" % "red",
        default = 'POS_X',
        items = [('POS_X', "+X", ""),
                 ('POS_Y', "+Y", ""),
                 ('POS_Z', "+Z", ""),
                 ('NEG_X', "-X", ""),
                 ('NEG_Y', "-Y", ""),
                 ('NEG_Z', "-Z", "")])

    normal_g : bpy.props.EnumProperty(
        name = "Normal Space",
        description = "Axis to bake in %s channel" % "green",
        default = 'POS_Y',
        items = [('POS_X', "+X", ""),
                 ('POS_Y', "+Y", ""),
                 ('POS_Z', "+Z", ""),
                 ('NEG_X', "-X", ""),
                 ('NEG_Y', "-Y", ""),
                 ('NEG_Z', "-Z", "")])

    normal_b : bpy.props.EnumProperty(
        name = "Normal Space",
        description = "Axis to bake in %s channel" % "blue",
        default = 'POS_Z',
        items = [('POS_X', "+X", ""),
                 ('POS_Y', "+Y", ""),
                 ('POS_Z', "+Z", ""),
                 ('NEG_X', "-X", ""),
                 ('NEG_Y', "-Y", ""),
                 ('NEG_Z', "-Z", "")])

    use_smooth_normals : bpy.props.BoolProperty(
        name = "Smooth Normals",
        description = BM_Labels.PROP_ITEM_MAP_USENORMALSMOOTH,
        default = False)

    normal_cage : bpy.props.FloatProperty(
        name = "Cage Extrusion",
        description = BM_Labels.PROP_ITEM_CAGEEXTRUSION_DESCRIPTION,
        default = 0,
        min = 0,
        max = 1,
        precision = 2,
        subtype = 'DISTANCE')

#Displacement Map Settings
    displacement_subdiv_levels : bpy.props.IntProperty(
        name = "Subdivision Levels",
        description = BM_Labels.PROP_ITEM_DISPMAP_SUBDIVLEVELS_DESCRIPTION,
        default = 1,
        min = 1,
        max = 10)

#Emission Map Settings
    #emission_use_mask : bpy.props.BoolProperty(
        #name = "Mask Only",
        #description = BM_Labels.PROP_ITEM_MAP_EMISSIONMASK_NAME,
        #default = False)

#AO Map Settings
    ao_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_AO)

    ao_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_AO_MaterialUpdate)    
    
    ao_samples: bpy.props.IntProperty(
        name = "Samples",
        description = BM_Labels.PROP_ITEM_MAP_SAMPLES_DESCRIPTION,
        default = 16,
        min = 1,
        max = 128,
        update = BM_MAP_AO_MaterialUpdate)

    ao_distance : bpy.props.FloatProperty(
        name = "Distance",
        description = BM_Labels.PROP_ITEM_AOMAP_DISTANCE_DESCRIPTION,
        default = 1,
        min = 0,
        update = BM_MAP_AO_MaterialUpdate)

    ao_black_point : bpy.props.FloatProperty(
        name = "Blacks",
        description = BM_Labels.PROP_ITEM_MAP_BPOINT_DESCRIPTION,
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_AO_MaterialUpdate)

    ao_white_point : bpy.props.FloatProperty(
        name = "Whites",
        description = BM_Labels.PROP_ITEM_MAP_WPOINT_DESCRIPTION,
        default = 0.8,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_AO_MaterialUpdate)

    ao_brightness : bpy.props.FloatProperty(
        name = "Brightness",
        default = -0.3,
        min = -100.0,
        max = 100.0,
        update = BM_MAP_AO_MaterialUpdate)

    ao_contrast : bpy.props.FloatProperty(
        name = "Contrast", 
        default = 0.3,
        min = -100.0,
        max = 100.0,
        update = BM_MAP_AO_MaterialUpdate)

    ao_opacity : bpy.props.FloatProperty(
        name = "Opacity", 
        default = 0.67,
        min = 0.0,
        max = 1.0,
        update = BM_MAP_AO_MaterialUpdate)

    ao_use_local : bpy.props.BoolProperty(
        name = "Local",
        description = BM_Labels.PROP_ITEM_AOMAP_USELOCAL_DESCRIPTION,
        default = False,
        update = BM_MAP_AO_MaterialUpdate)

    ao_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_AO_MaterialUpdate)

#Cavity Map Settings
    cavity_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_Cavity)

    cavity_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_Cavity_MaterialUpdate)   

    cavity_black_point : bpy.props.FloatProperty(
        name = "Blacks",
        description = BM_Labels.PROP_ITEM_MAP_BPOINT_DESCRIPTION,
        default = 0,
        min = 0.0,
        max = 1.0,
        precision = 3,
        update = BM_MAP_Cavity_MaterialUpdate)
    
    cavity_white_point : bpy.props.FloatProperty(
        name = "Whites",
        description = BM_Labels.PROP_ITEM_MAP_WPOINT_DESCRIPTION,
        default = 1,
        min = 0.0,
        max = 1.0,
        precision = 3,
        update = BM_MAP_Cavity_MaterialUpdate)
    
    cavity_power : bpy.props.FloatProperty(
        name = "Power",
        description = BM_Labels.PROP_ITEM_CAVITYMAP_POWER_DESCRIPTION, 
        default = 2.5,
        update = BM_MAP_Cavity_MaterialUpdate)
        
    cavity_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_Cavity_MaterialUpdate)

#Curvature Map Settings
    curv_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_Curvature)

    curv_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_Curvature_MaterialUpdate)    
    
    curv_samples: bpy.props.IntProperty(
        name = "Samples",
        description = BM_Labels.PROP_ITEM_MAP_SAMPLES_DESCRIPTION,
        default = 4,
        min = 2,
        max = 16,
        update = BM_MAP_Curvature_MaterialUpdate)
    
    curv_radius : bpy.props.FloatProperty(
        name = "Radius",
        default = 0.02,
        min = 0,
        precision = 3,
        update = BM_MAP_Curvature_MaterialUpdate)

    curv_edge_contrast : bpy.props.FloatProperty(
        name = "Edge Contrast value",
        default = 0,
        precision = 3,
        update = BM_MAP_Curvature_MaterialUpdate)

    curv_body_contrast : bpy.props.FloatProperty(
        name = "Body Contrast value",
        default = 1,
        precision = 3,
        update = BM_MAP_Curvature_MaterialUpdate)

    curv_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 1,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_Curvature_MaterialUpdate)

#Thickness Map Settings
    thick_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_Thickness)

    thick_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_Thickness_MaterialUpdate)    
    
    thick_samples : bpy.props.IntProperty(
        name = "Samples",
        description = BM_Labels.PROP_ITEM_MAP_SAMPLES_DESCRIPTION,
        default = 16,
        min = 1,
        max = 128,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_distance : bpy.props.FloatProperty(
        name = "Distance",
        description = BM_Labels.PROP_ITEM_AOMAP_DISTANCE_DESCRIPTION,
        default = 1,
        min = 0,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_black_point : bpy.props.FloatProperty(
        name = "Blacks",
        description = BM_Labels.PROP_ITEM_MAP_BPOINT_DESCRIPTION,
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_white_point : bpy.props.FloatProperty(
        name = "Whites",
        description = BM_Labels.PROP_ITEM_MAP_WPOINT_DESCRIPTION,
        default = 1,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_brightness : bpy.props.FloatProperty(
        name = "Brightness", 
        default = 1,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_contrast : bpy.props.FloatProperty(
        name = "Contrast", 
        default = 0,
        update = BM_MAP_Thickness_MaterialUpdate)

    thick_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_Thickness_MaterialUpdate)

#MaterialID Map Settings
    #matid_source : bpy.props.EnumProperty(
        #name = "Color Source",
        #description = BM_Labels.PROP_ITEM_MATIDMAP_COLORSOURCE_DESCRIPTION,
        #default = 'VERTEX',
        #items = [('VERTEX', "Mesh Vertex Groups", "Define color groups by mesh Vertex Groups"),
                 #('MATERIAL', "Existing Materials", "Define color groups by assigned Materials")])
    
    #matid_algorithm : bpy.props.EnumProperty(
        #name = "Algorithm",
        #description = BM_Labels.PROP_ITEM_MATIDMAP_COLORALGO_DESCRIPTION,
        #default = 'HUE',
        #items = [('RANDOM', "Random", "Color each group by unique Random Color"),
                 #('HUE', "Hue Shift", "Color each group by unique Hue"),
                 #('GRAYSCALE', "Grayscale", "Color each group by unique Grayscale Color")])

#NormalMask Map Settings
    xyzmask_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_NormalMask)

    xyzmask_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_NormalMask_MaterialUpdate) 

    xyzmask_use_x : bpy.props.BoolProperty(
        name = " X",
        description = "Enable/disable X coordinate mask filter",
        default = False,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_use_y : bpy.props.BoolProperty(
        name = " Y",
        description = "Enable/disable Y coordinate mask filter",
        default = False,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_use_z : bpy.props.BoolProperty(
        name = " Z",
        description = "Enable/disable Z coordinate mask filter",
        default = False,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_coverage : bpy.props.FloatProperty(
        name = "Range of coverage",
        default = 0,
        precision = 3,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_saturation : bpy.props.FloatProperty(
        name = "Saturation",
        default = 1,
        precision = 3,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_opacity : bpy.props.FloatProperty(
        name = "Opacity",
        default = 1,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_NormalMask_MaterialUpdate)

    xyzmask_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 1,
        min = -1,
        max = 1,
        precision = 3,
        update = BM_MAP_NormalMask_MaterialUpdate)

#GradientMask Map Settings
    gmask_use_preview : bpy.props.BoolProperty(
        name = "Preview",
        description = BM_Labels.PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION,
        default = False,
        update = BM_MAP_Preview_GradientMask)

    gmask_use_default : bpy.props.BoolProperty(
        name = "Default",
        description = BM_Labels.PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION,
        default = True,
        update = BM_MAP_GradientMask_MaterialUpdate) 

    gmask_type : bpy.props.EnumProperty(
        name = "Type",
        description = BM_Labels.PROP_ITEM_GMASKMAP_TYPE_DESCRIPTION,
        items = [("LINEAR", "Linear", "Create a linear progression"),
                 ("QUADRATIC", "Quadratic", "Create a quadratic progression"),
                 ("EASING", "Easing", "Create progression easing from one step to the next"),
                 ("DIAGONAL", "Diagonal", "Create a diagonal progression"),
                 ("SPHERICAL", "Spherical", "Create a spherical progression"),
                 ("QUADRATIC_SPHERE", "Quadratic Sphere", "Create a quadratic progression in the shape of a sphere"),
                 ("RADIAL", "Radial", "Create a radial progression")],
        update = BM_MAP_GradientMask_MaterialUpdate)
    
    gmask_location_x : bpy.props.FloatProperty(
        name = "X Location",
        description = BM_Labels.PROP_ITEM_GMASKMAP_LOCATION_DESCRIPTION + "X",
        default = 0,
        precision = 3,
        subtype = "DISTANCE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_location_y : bpy.props.FloatProperty(
        name = "Y Location",
        description = BM_Labels.PROP_ITEM_GMASKMAP_LOCATION_DESCRIPTION + "Y",
        default = 0,
        precision = 3,
        subtype = "DISTANCE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_location_z : bpy.props.FloatProperty(
        name = "Z Location",
        description = BM_Labels.PROP_ITEM_GMASKMAP_LOCATION_DESCRIPTION + "Z",
        default = 0, 
        precision = 3,
        subtype = "DISTANCE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_rotation_x : bpy.props.FloatProperty(
        name = "X Rotation",
        description = BM_Labels.PROP_ITEM_GMASKMAP_ROTATION_DESCRIPTION + "X",
        default = 0,
        precision = 2,
        subtype = "ANGLE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_rotation_y : bpy.props.FloatProperty(
        name = "Y Rotation",
        description = BM_Labels.PROP_ITEM_GMASKMAP_ROTATION_DESCRIPTION + "Y",
        default = 0,
        precision = 2,
        subtype = "ANGLE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_rotation_z : bpy.props.FloatProperty(
        name = "Z Rotation",
        description = BM_Labels.PROP_ITEM_GMASKMAP_ROTATION_DESCRIPTION + "Z",
        default = 0,
        precision = 2,
        subtype = "ANGLE",
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_scale_x : bpy.props.FloatProperty(
        name = "X Scale",
        description = BM_Labels.PROP_ITEM_GMASKMAP_SCALE_DESCRIPTION + "X",
        default = 1,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_scale_y : bpy.props.FloatProperty(
        name = "Y Scale",
        description = BM_Labels.PROP_ITEM_GMASKMAP_SCALE_DESCRIPTION + "Y",
        default = 1,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_scale_z : bpy.props.FloatProperty(
        name = "Z Scale",
        description = BM_Labels.PROP_ITEM_GMASKMAP_SCALE_DESCRIPTION + "Z",
        default = 1,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)
    
    gmask_coverage : bpy.props.FloatProperty(
        name = "Range of coverage",
        default = 0,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_contrast : bpy.props.FloatProperty(
        name = "Contrast",
        default = 1,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_saturation : bpy.props.FloatProperty(
        name = "Saturation", 
        default = 1,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_opacity : bpy.props.FloatProperty(
        name = "Opacity", 
        default = 1,
        min = 0,
        max = 1,
        update = BM_MAP_GradientMask_MaterialUpdate)

    gmask_use_invert : bpy.props.FloatProperty(
        name = "Invert",
        description = BM_Labels.PROP_ITEM_MAP_USEINVERT_NAME, 
        default = 0,
        min = 0,
        max = 1,
        precision = 3,
        update = BM_MAP_GradientMask_MaterialUpdate)

class BM_Item(bpy.types.PropertyGroup):
    object_pointer : bpy.props.PointerProperty(
        type = bpy.types.Object)

    use_bake : bpy.props.BoolProperty(
        name = BM_Labels.PROP_ITEM_USEBAKE_NAME,
        default = True)

#Item Source-Target Props:
    use_target : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USETARGET_NAME,
        default = False,
        update = BM_ITEM_UseTargetUpdate)
    
    use_source : bpy.props.BoolProperty(
        name = "",
        default = False)

    source : bpy.props.EnumProperty(
        name = "Source Item",
        description = BM_Labels.PROP_ITEM_SOURCE_NAME,
        items = BM_ITEM_Source,
        update = BM_ITEM_SourceUpdate)

    source_name : bpy.props.StringProperty()

    use_cage : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USECAGE_NAME,
        default = False)

    cage_extrusion : bpy.props.FloatProperty(
        name = "Cage Extrusion",
        description = BM_Labels.PROP_ITEM_CAGEEXTRUSION_DESCRIPTION,
        default = 0,
        min = 0,
        max = 1,
        precision = 2,
        subtype = 'DISTANCE')
    
    max_ray_distance : bpy.props.FloatProperty(
        name = "Max Ray Distance",
        description = BM_Labels.PROP_ITEM_MAXCAGEEXTRUSION_DESCRIPTION,
        default = 0,
        min = 0,
        max = 1,
        precision = 2,
        subtype = 'DISTANCE')

    cage_object : bpy.props.PointerProperty(
        name = "Cage Object",
        description = BM_Labels.PROP_ITEM_CAGEOBJECT_DESCRIPTION,
        type = bpy.types.Object)

#Item UVMap Props:
    active_uv : bpy.props.EnumProperty(
        name = "Active UV Map",
        description = BM_Labels.PROP_ITEM_ACTIVEUV_DESCRIPTION,
        items = BM_ITEM_UVLayers)

    uv_type : bpy.props.EnumProperty(
        name = "UVMap Type",
        description = BM_Labels.PROP_ITEM_UVTYPE_DESCRIPTION,
        items = BM_ITEM_UVType_Items)

    use_islands_pack : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USEUVPACK_DESCRIPTION,
        default = False)

#Item Output Props:
    use_overwrite : bpy.props.BoolProperty(
        name = "Overwrite Maps Settings",
        description = BM_Labels.PROP_ITEM_USEOVERWRITE_DESCRIPTION,
        default = False,
        update = BM_ITEM_OverwriteUpdate)
    
    overwrite_bake_target : bpy.props.EnumProperty(
        name = "Overwrite Target",
        description = "Where to output the baked map",
        items = BM_ITEM_Map_BakeTarget_Items,
        update = BM_ITEM_OverwriteUpdate)
    
    overwrite_use_denoise : bpy.props.BoolProperty(
        name = "Overwrite all with Image Denoising",
        description = BM_Labels.PROP_ITEM_MAP_USEDENOISE_DESCRIPTION,
        default = False,
        update = BM_ITEM_OverwriteUpdate)

    overwrite_file_format : bpy.props.EnumProperty(
        name = "Overwrite File Format",
        description = BM_Labels.PROP_ITEM_FILEFORMAT_DESCRIPTION,
        default = 'PNG',
        items = [('BMP', "BMP", ""),
                 ('PNG', "PNG", ""),
                 ('JPEG', "JPEG", ""),
                 ('TIFF', "TIFF", ""),
                 ('OPEN_EXR', "EXR", "")],
        update = BM_ITEM_OverwriteUpdate)

    overwrite_res_enum : bpy.props.EnumProperty(
        name = "Overwrite Resolution",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = '1024',
        items = [('512', "1/2K (512x512)", ""),
                 ('1024', "1K (1024x1024)", ""),
                 ('2048', "2K (2048x2048)", ""),
                 ('4096', "4K (4096x4096)", ""),
                 ('8192', "8K (8192x8192)", ""),
                 ('CUSTOM', "Custom", "")],
        update = BM_ITEM_OverwriteUpdate)

    overwrite_res_height : bpy.props.IntProperty(
        name = "Overwrite Height",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = 1000,
        min = 1,
        max = 32768,
        subtype = 'PIXEL',
        update = BM_ITEM_OverwriteUpdate)

    overwrite_res_width : bpy.props.IntProperty(
        name = "Overwrite Width",
        description = BM_Labels.PROP_ITEM_RES_DESCRIPTION,
        default = 1000,
        min = 1,
        max = 32768,
        subtype = 'PIXEL',
        update = BM_ITEM_OverwriteUpdate)

    overwrite_margin : bpy.props.IntProperty(
        name = "Overwrite Margin",
        description = BM_Labels.PROP_ITEM_MARGIN_DESCRIPTION,
        default = 16,
        min = 0,
        max = 64,
        subtype = 'PIXEL',
        update = BM_ITEM_OverwriteUpdate)
    
    overwrite_margin_type : bpy.props.EnumProperty(
        name = "Overwrite Margin Type",
        description = "Algorithm to extend the baked result",
        default = 'ADJACENT_FACES',
        items = [('ADJACENT_FACES', "Adjacent Faces", "Use pixels from adjacent faces across UV seams"),
                 ('EXTEND', "Extend", "Extend border pixels outwards")],
        update = BM_ITEM_OverwriteUpdate)

    overwrite_use_32bit : bpy.props.BoolProperty(
        name = "Overwrite all with 32 bit Float",
        description = BM_Labels.PROP_ITEM_USE32BIT_DESCRIPTION,
        default = False,
        update = BM_ITEM_OverwriteUpdate)

    overwrite_use_alpha : bpy.props.BoolProperty(
        name = "Overwrite all with Alpha",
        description = BM_Labels.PROP_ITEM_USEALPHA_DESCRIPTION,
        default = False,
        update = BM_ITEM_OverwriteUpdate)
    
    overwrite_udim_start_tile : bpy.props.IntProperty(
        name = "Overwrite UDIM Start Tile Index",
        description = BM_Labels.PROP_ITEM_UVTILEDINDEXES_DESCRIPTION,
        default = 1001,
        min = 1001,
        max = 2000)
    
    overwrite_udim_end_tile : bpy.props.IntProperty(
        name = "Overwrite UDIM Start Tile Index",
        description = BM_Labels.PROP_ITEM_UVTILEDINDEXES_DESCRIPTION,
        default = 1001,
        min = 1001,
        max = 2000)

#Item Maps Collection Settings
    maps_active_index : bpy.props.IntProperty(
        name = BM_Labels.PROP_ITEM_ACTIVEMAPINDEX_NAME,
        default = -1,
        update = BM_ITEM_RemoveLocalPreviews)
    
    maps : bpy.props.CollectionProperty(type = BM_Item_Map)

#Item Bake Settings
    use_internal : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USEINTERNAL_DESCRIPTION,
        default = True)

    output_filepath : bpy.props.StringProperty(
        name = "Output Path",
        description = BM_Labels.PROP_ITEM_OUTPUTFILEPATH_DESCRIPTION,
        default = "\\\\",
        subtype = 'DIR_PATH')

    use_subfolder : bpy.props.BoolProperty(
        name = "Create Subfolder",
        description = BM_Labels.PROP_ITEM_USESUBFOLDER_DESCRIPTION,
        default = False)

    subfolder_name : bpy.props.StringProperty(
        name = "Subfolder Name",
        default = "Maps")

    batch_name : bpy.props.StringProperty(
        name = "Output files Batch Naming",
        description = BM_Labels.PROP_ITEM_BATCHNAME_DESCRIPTION,
        default = "item_map_res",
        update = BM_ITEM_BatchNameUpdate)

    use_material : bpy.props.BoolProperty(
        description = BM_Labels.PROP_ITEM_USEMATERIAL_NAME,
        default = False)

    bake_samples : bpy.props.IntProperty(
        name = "Bake Samples",
        description = BM_Labels.PROP_ITEM_BAKESAMPLES_DESCRIPTION,
        default = 128,
        min = 1,
        max = 16777216)
    
    bake_use_adaptive_sampling : bpy.props.BoolProperty(
        name = "Use Adaptive Sampling for Bake",
        description = BM_Labels.PROP_ITEM_BAKEUSEADAPSAMPLING_DESCRIPTION,
        default = False)

    bake_adaptive_threshold : bpy.props.FloatProperty(
        name = "Adaptive Sampling Threshold for Bake",
        description = BM_Labels.PROP_ITEM_BAKEADAPSAMPLTHRESHOLD_DESCRIPTION,
        default = 0.01,
        min = 0,
        max = 1,
        soft_min = 0.001,
        step = 3,
        precision = 4)

    bake_min_samples : bpy.props.IntProperty(
        name = "Bake Min Samples",
        description = BM_Labels.PROP_ITEM_MINBAKESAMPLES_DESCRIPTION,
        default = 0,
        min = 0,
        max = 4096)

    bake_device : bpy.props.EnumProperty(
        name = "Choose Bake Device",
        description = BM_Labels.PROP_ITEM_BAKEDEVICE_DESCRIPTION,
        default = 'CPU',
        items = [('GPU', "GPU Compute", "Use GPU compute device for baking, configured in the system tab in the user preferences"),
                 ('CPU', "CPU", "Use CPU for baking")])

    #use_save_log : bpy.props.BoolProperty(
        #name = "Save Log File",
        #description = BM_Labels.PROP_ITEM_USESAVELOG_DESCRIPTION,
        #default = False)