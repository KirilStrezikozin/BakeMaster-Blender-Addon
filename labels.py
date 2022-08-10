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

class BM_Labels:
    #INFO Messages:
    INFO_ITEM_EXISTS = "Mesh exists in the list"
    INFO_ITEM_NONMESH = "Expected mesh object"
    INFO_MAP_PREVIEWNOTCYCLES = INFO_BAKE_NOTINCYLES = "Swith to Cycles Render Engine"
    INFO_BAKE_MAPQUEUEEMPTY = "No maps to bake"
    INFO_BAKE_ITEMQUEUEEMPTY = "No items to bake"

    #Operators Descriptions:
    OPERATOR_AOL_SELF_DESCRIPTION = "Move the bake priority of items in the list up and down"
    OPERATOR_AOL_ADD_DESCRIPTION = "Add selected mesh object(s) in the scene to the list below"
    OPERATOR_AOL_REMOVE_DESCRIPTION = "Remove active item from the list below"
    OPERATOR_AOL_REFRESH_DESCRIPTION = "Some of list items cannot be found in the scene.\nPress the refresh button to remove them from the list"
    OPERATOR_AOL_TRASH_DESCRIPTION = "Remove all items from the list (resets BakeMaster)"
    OPERATOR_ITEM_MAPS_DESCRIPTION = "Add/Remove map passes from the list"
    OPERATOR_ITEM_BAKE_DESCRIPTION = "Bake image textures.\nBake This: bake maps only for current item.\nBake All: bake maps for all items in the list"
    OPERATOR_ITEM_BAKE_FULL_DESCRIPTION = "Press `BACKSPACE` to cancel baking all next maps.\nPress `ESC` key to cancel baking current map.\nPress `BACKSPACE + ESC` to cancel baking.\nIf you want to undo the bake, press `Ctrl + Z` just after it finished or canceled.\n\nOpen Blender Console to, if you face unexpected Blender freeze, press `Ctrl + C` to abort the bake.\nNote that there are expectable Blender freezes when baking Displacement, Denoising baked result, baking item with no UV Map or UV Packing items that have no UV Maps"
    
    #Property Labels:
    PROP_AOL_ACTIVEINDEX_NAME = "Object of type 'MESH' to be included in the bake"
    PROP_ITEM_USEBAKE_NAME = "Include/exclude item in the bake"
    PROP_ITEM_USETARGET_NAME = "Set this item as bake target object"
    PROP_ITEM_SOURCE_NAME = "Choose source object within available in the list"
    PROP_ITEM_USECAGE_NAME = "Cast rays to active item from a cage"
    PROP_ITEM_CAGEEXTRUSION_DESCRIPTION = "Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes"
    PROP_ITEM_MAXCAGEEXTRUSION_DESCRIPTION = "The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit"
    PROP_ITEM_CAGEOBJECT_DESCRIPTION = "Object to use as cage instead of calculating the cage from the active object with cage extrusion"
    PROP_ITEM_ACTIVEUV_DESCRIPTION = "Choose active UVMap layer among created to use in the bake.\nIf mesh has got no UV layers, auto UV unwrap will be proceeded"
    PROP_ITEM_UVTYPE_DESCRIPTION = "UVMap type"
    PROP_ITEM_UVTILEDINDEXES_DESCRIPTION = "UDIM tile index of UDIM tiles baking range.\nUDIMs baking range is used for defining UDIM tiles baking boundaries. Bake result will only affect specified range of tiles (Start Tile Index - End Tile Index)"
    PROP_ITEM_USEUVPACK_DESCRIPTION = "Items UVs with 'Pack' turned on will be packed before the bake.\nThose items will share the same baked image.\nAvailable if UV Type is Single)"
    PROP_ITEM_USEISLANDSROTATE_DESCRIPTION = "Rotate islands for best fit"
    PROP_ITEM_USEOVERWRITE_DESCRIPTION = "Set output settings for all item maps at once"
    PROP_ITEM_FILEFORMAT_DESCRIPTION = "Images file format"
    PROP_ITEM_RES_DESCRIPTION = "Texture resolution or set custom"
    PROP_ITEM_MARGIN_DESCRIPTION = "Extends the bake result as a post process filter"
    PROP_ITEM_USE32BIT_DESCRIPTION = "Create images with 32 bit floating point bit depth"
    PROP_ITEM_USEALPHA_DESCRIPTION = "Create images with an alpha channel"

    PROP_ITEM_CYCLES_USEDIRECT_DESCRIPTION = "Add direct lighting contribution"
    PROP_ITEM_CYCLES_USEINDIRECT_DESCRIPTION = "Add indirect lighting contribution"
    PROP_ITEM_CYCLES_USECOLOR_DESCRIPTION = "Color the pass"
    PROP_ITEM_CYCLES_NORMALSPACE_DESCRIPTION = "Choose normal space for baking"

    PROP_ITEM_ACTIVEMAPINDEX_NAME = "Set up maps to bake"
    PROP_ITEM_MAPTYPE_DESCRIPTION = "Set map type for the current pass"
    PROP_ITEM_MAP_USEBAKE_NAME = "Include/exclude map in the bake"
    PROP_ITEM_MAP_USEDENOISE_DESCRIPTION = "Denoise image after bake (available only for not tiled image and if baking externally)"
    PROP_ITEM_MAP_USESTT_NAME = "Affect this map by source-target settings configured in the item settings above.\nThis option won't be shown unless source-target settings are configured, or when baking smooth normals"
    PROP_ITEM_MAP_USENORMALSMOOTH = "Bake faces smooth normals"
    PROP_ITEM_MAP_EMISSIONMASK_NAME = "Bake black and white emission mask"
    PROP_ITEM_MAP_USEINVERT_NAME = "Invert colors of the map"
    PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION = "Preview texture map in the viewport (Cycles only).\nIf current item's mesh has got no materials, a new one will be added.\nFor each item's mesh materials, custom nodes will be added to preview the map in the Rendered View.\nAfter disabling the preview, all those nodes will be removed without affecting original material(s)"
    PROP_ITEM_MAP_USEDEFAULT_DESCRIPTION = "Bake texture map using default settings"
    PROP_ITEM_MAP_SAMPLES_DESCRIPTION = "Tracing samples count. Affects the quality.\nKeep as low as possible for optimal performance"
    PROP_ITEM_MAP_BPOINT_DESCRIPTION = "Shadow point location on the map color gradient spectrum"
    PROP_ITEM_MAP_WPOINT_DESCRIPTION = "Highlight point location on the map color gradient spectrum"
    PROP_ITEM_AOMAP_DISTANCE_DESCRIPTION = "Distance up to which other objects are considered to occlude the shading point"
    PROP_ITEM_AOMAP_USELOCAL_DESCRIPTION = "Only detect occlusion from the object itself, and not others"
    PROP_ITEM_CAVITYMAP_POWER_DESCRIPTION = "Cavity map power value"
    PROP_ITEM_MATIDMAP_COLORSOURCE_DESCRIPTION = "Type of source for detecting color groups"
    PROP_ITEM_MATIDMAP_COLORALGO_DESCRIPTION = "Algorithm by which the color groups will be painted"
    PROP_ITEM_GMASKMAP_TYPE_DESCRIPTION = "Style of color blending"
    PROP_ITEM_GMASKMAP_LOCATION_DESCRIPTION = "Gradient location by the local axis "
    PROP_ITEM_GMASKMAP_ROTATION_DESCRIPTION = "Gradient rotation by the local axis "
    PROP_ITEM_GMASKMAP_SCALE_DESCRIPTION = "Smoothness. Gradient scale by the local axis "
    PROP_ITEM_DISPMAP_SUBDIVLEVELS_DESCRIPTION = "The subdivision level defines the level of details.\nKeep as low as possible for optimal performance"

    PROP_ITEM_USEINTERNAL_DESCRIPTION = "Save baked images internally"
    PROP_ITEM_OUTPUTFILEPATH_DESCRIPTION = "Directory path to save baked images to externally"
    PROP_ITEM_USESUBFOLDER_DESCRIPTION = "Create subfolder in the output filepath directory.\nIf any image has the same name in the directory as the baked image, it will be overwritten"
    PROP_ITEM_BATCHNAME_DESCRIPTION = "Format using underscore(_) between keywords:\n_index_ - write item index in the list\n_item_ - write name of the item in the list\n_sourcetarget_ - write 'Target' if item is a target\n_uvpacked_ - write 'Packed' if item is included in UV Pack\n_map_ - write baked map name\n_res_ - write baked map resolution\n_float_ - write '32bit' if baked image uses 32bit Float, otherwise write '8bit'\n_alpha_ - write 'Alpha' if baked image uses Alpha Channel\n\nExample item_map_res : Suzanne_ALBEDO_2048; map_float_item : NORMAL_32bit_MyCube\n\nIf Batch Name value has no _item_ key, it will be added automatically.\nMultiple keys are supported: item_item_map - Monster.001_Monster.001_DISPLACEMENT"
    PROP_ITEM_USEMATERIAL_NAME = "Create material after bake including all baked maps for this item"
    PROP_ITEM_BAKESAMPLES_DESCRIPTION = "Number of samples to render per each pixel.\nKeep as low as possible for optimal performance"
    PROP_ITEM_MINBAKESAMPLES_DESCRIPTION = "The minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold"
    PROP_ITEM_BAKEUSEADAPSAMPLING_DESCRIPTION = "Automatically reduce the number of samples per pixel based on estimated noise level"
    PROP_ITEM_BAKEADAPSAMPLTHRESHOLD_DESCRIPTION = "Noise level step to stop sampling at, lower values reduce noise at the cost of render time.\nZero for automatic setting based on number of AA sampled"
    PROP_ITEM_BAKEDEVICE_DESCRIPTION = "Device to use for baking"
    PROP_ITEM_USESAVELOG_DESCRIPTION = "Save item, map, bake time preferences into a separate .txt file"
    PROP_ITEM_USEBGBAKE_DESCRIPTION = "Proceed the bake in the background not freezing Blender"
    PROP_ITEM_USERESETAFTERBAKE_DESCRIPTION = "Remove item(s) from the items list after maps finsihed baking.\nIf item(s) use source object, it will be removed as well"