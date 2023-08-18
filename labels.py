# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 2.5.2)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This License permits you to use this software for any purpose including
# personal, educational, and commercial; You are allowed to modify it to suit
# your needs, and to redistribute the software or any modifications you make
# to it, as long as you follow the terms of this License and the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This License grants permission to redistribute this software to
# UNLIMITED END USER SEATS (OPEN SOURCE VARIANT) defined by the
# acquired License type. A redistributed copy of this software
# must follow and share similar rights of free software and usage
# specifications determined by the GNU General Public License.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License in
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# ##### END LICENSE BLOCK #####

class BM_Labels:
    # INFO Messages:
    INFO_MAP_PREVIEWNOTCYCLES = ERROR_BAKE_NOTINCYLES = "Swith to Cycles Render Engine"
    ERROR_BAKE_MAPQUEUEEMPTY = "No maps to bake"
    ERROR_BAKE_ITEMQUEUEEMPTY = "No items to bake"

    # Operators Descriptions:
    OPERATOR_ITEM_BAKE_DESCRIPTION = "Bake image textures.\nBake This: bake maps only for the current object.\nBake All: bake maps for all objects added"
    OPERATOR_ITEM_BAKE_FULL_DESCRIPTION = "Press `BACKSPACE` to cancel baking all next maps.\nPress `ESC` key to cancel baking current map.\nPress `BACKSPACE`, then `ESC` to cancel baking.\nIf you want to undo the bake, press `Ctrl + Z` (`Cmd + Z` on Mac) just after it finished or canceled.\n\nOpen Blender Console to see more baking process information and, if you face an unexpected Blender freeze, be able to press `Ctrl + C` (`Cmd + C` on Mac) to abort the bake.\nNote that there are expectable Blender freezes when preparing maps for meshes with huge amount of geometry, baking map result to modifiers, Denoising baked result, or UV unwrapping and packing. Please be patient, BakeMaster will notify if any error occured"
    OPERATOR_HELP_DESCRIPTION = "BakeMaster online documentation for help. Press to open in your default browser"
    
    # Property Labels:
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

    PROP_ITEM_bake_batchname_custom_Description = "Write keywords starting with $, any additional text can be added:\n\n$objectindex - Object index\n$objectname - Object name\n$containername - Container name if Object is in it\n$packname - Channel Pack name if map is in Channel Pack\n$texsetname - Texture Set chosen name type if Object is in it\n$mapindex - Map index\n$mapname - Map prefix\n$mapres - Map Resolution\n$mapbit - _32bit_ if map uses 32bit Float, else _8bit_\n$maptrans - _trans_ if map uses transparent bg\n$mapssaa - SSAA value used for the map\n$mapsamples - Number of map bake samples, max samples if Adaptive is used\n$mapdenoise - _denoised_ if map was denoised\n$mapnormal - For Normal map, write preset type\n$mapuv - Write UV Layer name used for baking map\n$engine - Write Bake Engine used for baking\n$autouv - _autouv_ if object was auto uv unwrapped\n\ntestbake1$objectname_$mapname_$mapdenoise_Final -> testbake1monsterhead_NM_denoised_Final"

    # URLs
    # different documentation versions may have different pages setup
    __addon_version__ = "2.5.2"
    URL_HELP_MAIN = "https://bakemaster-blender-addon.readthedocs.io/en/%s/" % __addon_version__
    URL_HELP_OBJS = "https://bakemaster-blender-addon.readthedocs.io/en/%s/pages/start/objects.html" % __addon_version__
    URL_HELP_MAPS = "https://bakemaster-blender-addon.readthedocs.io/en/%s/pages/start/maps.html" % __addon_version__
    URL_HELP_BAKE = "https://bakemaster-blender-addon.readthedocs.io/en/%s/pages/start/bake.html" % __addon_version__
    URL_HELP_SUPPORT = "https://bakemaster-blender-addon.readthedocs.io/en/%s/pages/more/connect.html" % __addon_version__
