# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (3.0.0)
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

from bpy.types import (
    Operator,
)
from bpy.props import (
    EnumProperty,
)


class BM_OT_BakeJobs_AddRemove(Operator):
    bl_idname = 'bakemaster.bakejobs_addremove'
    bl_label = "Add/Remove"
    bl_description = "Add or Remove Bake Job from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=[('ADD', "Add", ""),
               ('REMOVE', "Remove", "")])

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if self.action == 'ADD':
            new_bakejob = bakemaster.bakejobs.add()
            new_bakejob.index = bakemaster.bakejobs_len
            new_bakejob.name = "Bake Job %d" % (new_bakejob.index + 1)
            bakemaster.bakejobs_active_index = new_bakejob.index
            bakemaster.bakejobs_len += 1
            return {'FINISHED'}

        try:
            bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
        except IndexError:
            return {'FINISHED'}

        if self.action == 'REMOVE':
            for index in range(bakejob.index + 1, bakemaster.bakejobs_len):
                bakemaster.bakejobs[index].index -= 1
            bakemaster.bakejobs.remove(bakejob.index)
            bakemaster.bakejobs_len -= 1
            if not bakemaster.bakejobs_active_index < bakemaster.bakejobs_len:
                bakemaster.bakejobs_active_index = bakemaster.bakejobs_len - 1
            return {'FINISHED'}


class BM_OT_BakeJobs_Move(Operator):
    bl_idname = 'bakemaster.bakejobs_move'
    bl_label = "Move"
    bl_description = "Move the current selected Bake Job up or down (change its bake order)"  # noqa: E261
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        default='MOVE_UP',
        items=[('MOVE_UP', "Move up", ""),
               ('MOVE_DOWN', "Move down", "")])

    def invoke(self, context, event):
        self.mover_indexes = {
            'MOVE_UP': -1,
            'MOVE_DOWN': 1
        }
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        try:
            bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
        except IndexError:
            return {'CANCELLED'}

        move_to_index = bakejob.index + self.mover_indexes[self.action]
        if move_to_index < 0 or move_to_index >= bakemaster.bakejobs_len:
            return {'CANCELLED'}

        bakejob_next = bakemaster.bakejobs[move_to_index]
        bakemaster.bakejobs.move(bakejob.index, bakejob_next.index)
        bakejob.index, bakejob_next.index = bakejob_next.index, bakejob.index
        bakemaster.bakejobs_active_index = bakejob_next.index
        return {'FINISHED'}


class BM_OT_BakeJobs_Trash(Operator):
    bl_idname = 'bakemaster.bakejobs_trash'
    bl_label = "Trash"
    bl_description = "Remove all Bake Jobs from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        [bakemaster.bakejobs.remove(index) for index in
         reversed(range(bakemaster.bakejobs_len))]
        bakemaster.bakejobs_active_index = -1
        bakemaster.bakejobs_len = 0
        return {'FINISHED'}
