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

from bpy.types import Operator
from bpy.props import IntProperty


class BM_OT_Subcontainer_Trash(Operator):
    bl_idname = 'bakemaster.subcontainer_trash'
    bl_label = "Trash"
    bl_description = "Remove all Items from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    container_index: IntProperty(default=-1)

    def invoke(self, context, _):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        container = bakemaster.get_container(bakejob, self.container_index)
        bakemaster.wh_trash(container, "subcontainers")
        return {'FINISHED'}


class BM_OT_Subcontainer_Toggle_Expand(Operator):
    bl_idname = "bakemaster.subcontainer_toggle_expand"
    bl_label = "Expand/Collapse"
    bl_options = {'INTERNAL'}

    bakejob_index: IntProperty(default=-1)
    container_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        container = bakemaster.get_container(bakejob, self.container_index)
        subcontainer = bakemaster.get_subcontainer(container, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}
        elif not subcontainer.is_group:
            bakemaster.log("o3x0002")
            return {'CANCELLED'}

        subcontainer.is_expanded = not subcontainer.is_expanded
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)
