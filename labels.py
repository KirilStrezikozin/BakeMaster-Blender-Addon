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

class BM_Labels:
    #INFO Messages:
    INFO_MAP_PREVIEWNOTCYCLES = INFO_BAKE_NOTINCYLES = "Swith to Cycles Render Engine"
    INFO_BAKE_MAPQUEUEEMPTY = "No maps to bake"
    INFO_BAKE_ITEMQUEUEEMPTY = "No items to bake"

    #Operators Descriptions:
    OPERATOR_ITEM_BAKE_DESCRIPTION = "Bake image textures.\nBake This: bake maps only for current item.\nBake All: bake maps for all items in the list"
    OPERATOR_ITEM_BAKE_FULL_DESCRIPTION = "Press `BACKSPACE` to cancel baking all next maps.\nPress `ESC` key to cancel baking current map.\nPress `BACKSPACE + ESC` to cancel baking.\nIf you want to undo the bake, press `Ctrl + Z` just after it finished or canceled.\n\nOpen Blender Console to, if you face unexpected Blender freeze, press `Ctrl + C` to abort the bake.\nNote that there are expectable Blender freezes when baking Displacement, Denoising baked result, baking item with no UV Map or UV Packing items that have no UV Maps"
    OPERATOR_HELP_DESCRIPTION = "BakeMaster online documentation for help. Press to open in your default browser"
    
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
    PROP_ITEM_RES_DESCRIPTION = "Texture resolution or set custom"
    PROP_ITEM_MARGIN_DESCRIPTION = "Extends the bake result as a post process filter"
    PROP_ITEM_USE32BIT_DESCRIPTION = "Create images with 32 bit floating point bit depth"
    PROP_ITEM_USEALPHA_DESCRIPTION = "Create images with an alpha channel"


    PROP_ITEM_MAP_USESTT_NAME = "Affect this map by source-target settings configured in the item settings above.\nThis option won't be shown unless source-target settings are configured, or when baking smooth normals"
    PROP_ITEM_MAP_USEPREVIEW_DESCRIPTION = "Preview texture map in the viewport (Cycles only).\nIf current item's mesh has got no materials, a new one will be added.\nFor each item's mesh materials, custom nodes will be added to preview the map in the Rendered View.\nAfter disabling the preview, all those nodes will be removed without affecting original material(s)"

    PROP_ITEM_bake_batchname_custom_Description = "Write keywords starting with $, any additional text can be added. Some keywords support adding $$ to specify what to write or $$$ to skip the value\n\n$objectindex - Object index\n$objectname - Object name\n$containername - Container name if Object is in it\n$packname - Channel Pack name if map is in Channel Pack\n$texsetname - Texture Set chosen name type if Object is in it\n$mapindex - Map index\n$mapname - Map prefix\n$mapres - Map Resolution\n$mapbit - _32bit_ if map uses 32bit Float, else _8bit_, default - $$32bit$$8bit\n$maptrans - Write _trans_ if map uses transparent bg, default - $$trans$$$\n$mapssaa - SSAA value used for the map\n$mapsamples - Number of map bake samples, max samples if Adaptive is used\n$mapdenoise - _denoised_ if map was denoised, default - $$denoised$$$\n$mapnormal - For Normal map, write preset type\n$mapuv - Write UV Layer name used for baking map\n$engine - Write Bake Engine used for baking\n$autouv - Write _autouv_ if object was auto uv unwrapped, default - $$autouv$$$, you can specify\ntestbake1$objectname_$mapname_$mapdenoise$$D$$NotD -> testbake1monsterhead_NORMAL_NotD"

    #URls
    URL_HELP_BASE = "https://bakemaster-blender-addon.readthedocs.io/en/latest/"