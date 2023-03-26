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
        'Global': {
            "short_bake_instruction": {
                "description": "Press `ESC` key to cancel baking current map iteration.\n\nOpen Blender Console to see more information about the baking process and, if you face an unexpected Blender freeze, be able to press `Ctrl + C` (Windows), `Cmd + C` (Mac), `Super + C` (Linux) to abort the bake. Enable Prompt before freeze for more control",  # noqa: E501
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
            print("asdfsadf")
            label = ""
        return label


class BM_LABELS_Operators():
    labels = {
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
        base = "https://bakemaster-blender-addon.readthedocs.io/en/"
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
            'BAKEHISTORY': r'%s/',
        }
        try:
            url = urls[identifier]
        except KeyError:
            url = "%s"
        return url % (base + self.addon_version)
