# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on
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

import bpy
from .labels import BM_Labels


class BM_OT_ITEM_Bake(bpy.types.Operator):
    bl_idname = 'bakemaster.item_bake'
    bl_label = "BakeMaster Bake Operator"
    bl_description = BM_Labels.OPERATOR_ITEM_BAKE_DESCRIPTION
    bl_options = {'UNDO'}

    wait_delay = 0.1  # Time Step interval in seconds between timer events
    report_delay = 2.0  # delay between each status report, seconds
    _version_current = bpy.app.version  # to check compatibility
    _handler = None
    _timer = None

    control: bpy.props.EnumProperty(
        items=[('BAKE_ALL', "Bake All", "Bake maps for all objects added"),
               ('BAKE_THIS', "Bake This", "Bake maps only for the current object or container")])

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def invoke(self, context, event):
        self.report({'INFO'}, "Upgrade to Full Version")
        return {'FINISHED'}
