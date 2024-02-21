# BEGIN LICENSE & COPYRIGHT BLOCK.
#
# Copyright (C) 2022-2024 Kiril Strezikozin
# BakeMaster Blender Add-on (version 2.6.1)
#
# This file is a part of BakeMaster Blender Add-on, a plugin for texture
# baking in open-source Blender 3d modelling software.
# The author can be contacted at <kirilstrezikozin@gmail.com>.
#
# Redistribution and use for any purpose including personal, educational, and
# commercial, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. The current acquired License allows copies/redistributions of this
#    software be made to UNLIMITED END USER SEATS (OPEN SOURCE LICENSE).
# 2. Redistributions of this source code or partial usage of this source code
#    must follow the terms of this license and retain the above copyright
#    notice, and the following disclaimer.
# 3. The name of the author may be used to endorse or promote products derived
#    from this software. In such a case, a prior written permission from the
#    author is required.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# You should have received a copy of the GNU General Public License in the
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# END LICENSE & COPYRIGHT BLOCK.


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
