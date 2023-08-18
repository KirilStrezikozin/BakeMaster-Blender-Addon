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


import bpy
from .labels import BM_Labels


class BM_OT_ITEM_Bake(bpy.types.Operator):
    bl_idname = 'bakemaster.item_bake'
    bl_label = "BakeMaster Bake Operator"
    bl_description = BM_Labels.OPERATOR_ITEM_BAKE_DESCRIPTION
    bl_options = {'UNDO'}

    wait_delay = 0.1  # Time Step interval in seconds between timer events
    report_delay = 1.0  # delay between each status report, seconds
    _version_current = bpy.app.version  # for compatibility checks
    _handler = None
    _timer = None

    control: bpy.props.EnumProperty(
        items=[('BAKE_ALL', "Bake All", "Bake maps for all objects added"),
               ('BAKE_THIS', "Bake This",
                "Bake maps only for the current object or container")])

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def invoke(self, context, _):
        self.report({'ERROR'}, "Bake isn't available. Upgrade to Full Version")
        return {'FINISHED'}
