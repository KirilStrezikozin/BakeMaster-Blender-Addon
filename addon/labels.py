# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 3.0.0)
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

class BM_LABELS_Props():
    labels = {
        'MatGroups_Item': {
            "group_index": {
                "description": "Divide materials into separate groups by assigning an according group index.\nBy default, BakeMaster will merge all materials, meaning if you, let's say, had Diffuse Color data output in every material and chose to bake Diffuse map, a single Diffuse image texture will be baked. Baked map sets for materials with different group indexes will be separated",  # noqa: E501
            }
        },
        'Map': {
            "map_use_preview": {
                "name": "Preview",
                "description": "Preview texture map in the viewport (Cycles only).\nIf current item's mesh has got no materials, a new one will be added.\nFor each item's mesh materials, custom nodes will be added to preview the map in the Rendered View.\nAfter disabling the preview, all those nodes will be removed without affecting original material(s)",  # noqa: E501
            }
        },
        'Object': {
            "bake_batchname": {
                "description": "Write keywords starting with $, any additional text can be added:\n\n$objectindex - Object index\n$objectname - Object name\n$containername - Container name if Object is in it\n$packname - Channel Pack name if map is in Channel Pack\n$texsetname - Texture Set chosen name type if Object is in it\n$mapindex - Map index\n$mapname - Map prefix\n$mapres - Map Resolution\n$mapbit - _32bit_ if map uses 32bit Float, else _8bit_\n$maptrans - _trans_ if map uses transparent bg\n$mapssaa - SSAA value used for the map\n$mapsamples - Number of map bake samples, max samples if Adaptive is used\n$mapdenoise - _denoised_ if map was denoised\n$mapnormal - For Normal map, write preset type\n$mapuv - Write UV Layer name used for baking map\n$matgroup - Write Material Group naming convention\n$engine - Write Bake Engine used for baking\n$autouv - _autouv_ if object was auto uv unwrapped\n\ntestbake1$objectname_$mapname_$mapdenoise_Final -> testbake1monsterhead_NM_denoised_Final",  # noqa: E501
            }
        },
        'Global': {
            "bake_instruction": {
                "description": "Press `BACKSPACE` to cancel baking all next maps.\nPress `ESC` key to cancel baking current map.\nPress `BACKSPACE`, then `ESC` to cancel baking.\nIf you want to undo the bake, press `Ctrl + Z` (`Cmd + Z` on Mac) just after it finished or canceled.\n\nOpen Blender Console to see more baking process information and, if you face an unexpected Blender freeze, be able to press `Ctrl + C` (`Cmd + C` on Mac) to abort the bake.\nNote that there are expectable Blender freezes when preparing maps for meshes with huge amount of geometry, baking map result to modifiers, Denoising baked result, or UV unwrapping and packing. Please be patient, BakeMaster will notify if any error occured",  # noqa: E501
            }
        }
    }

    def __init__(self, property_group: str, property_name: str,
                 property_arg: str):
        self.property_group = property_group
        self.property_name = property_name
        self.property_arg = property_arg

    def get(self):
        try:
            label = self.labels[self.property_group][self.property_name][
                    self.property_arg]
        except KeyError:
            label = ""
        return label


class BM_LABELS_Operators():
    labels = {
        'BM_OT_ITEM_Bake': {
            "bl_description": "",
        }
    }

    def __init__(self, operator_name: str, property_name: str):
        self.operator_name = operator_name
        self.property_name = property_name

    def get(self):
        try:
            label = self.labels[self.operator_name][self.property_name]
        except KeyError:
            label = ""
        return label


class BM_URLs:
    """
    Get url to bakemaster's online documentation by giving addon_version
    and page identifier.
    """

    def __init__(self, addon_version: str):
        self.addon_version = addon_version

    def get(self, identifier: str):
        urls = {
            'INDEX': r'%s/',
            'BAKEJOBS': r'%s/',
            'PIPELINE': r'%s/',
            'MANAGER': r'%s/',
            'OBJECTS': r'%s/',
            'MAPS': r'%s/',
            'OUTPUT': r'%s/',
            'TEXSETS': r'%s/',
            'BAKE': r'%s/',
        }
        try:
            url = urls[identifier]
        except KeyError:
            url = "%s"
        return url % (
                "https://bakemaster-blender-addon.readthedocs.io/en/" +
                self.addon_version)
