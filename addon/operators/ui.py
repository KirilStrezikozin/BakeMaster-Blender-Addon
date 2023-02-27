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
from ..labels import BM_LABELS_Operators


class BM_OT_BakeJobs(Operator):
    """
    Bake Jobs Operator for adding and removing bake jobs.
    """
    bl_idname = 'bakemaster.bakejobs'
    bl_label = ""
    bl_description = BM_LABELS_Operators('BM_OT_BakeJobs', "description").get()
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        items=[('ADD', "Add", ""),
               ('REMOVE', "Remove", ""),
               ('TRASH', "Trash", ""),
               ('MOVE_UP', "Move up", ""),
               ('MOVE_DOWN', "Move down", "")])

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        bakemaster = context.scene.bakemaster
        len_of_bakejobs = len(bakemaster.bakejobs)

        if self.action == 'ADD':
            new_bakejob = bakemaster.bakejobs.add()
            new_bakejob.index = len_of_bakejobs
            new_bakejob.name = "Bake Job %d" % (new_bakejob.index + 1)
            bakemaster.bakejobs_active_index = new_bakejob.index
            return {'FINISHED'}

        try:
            bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
        except IndexError:
            return {'FINISHED'}

        if self.action == 'REMOVE':
            for index in range(bakejob.index, len_of_bakejobs):
                bakemaster.bakejobs[index].index -= 1
            bakemaster.bakejobs.remove(bakejob.index + 1)
            if bakemaster.bakejobs_active_index >= len_of_bakejobs - 1:
                bakemaster.bakejobs_active_index = len_of_bakejobs - 2
            return {'FINISHED'}
        elif self.action == 'TRASH':
            [bakemaster.bakejobs.remove(index) for index in
             reversed(range(len_of_bakejobs))]
            bakemaster.bakejobs_active_index = -1
            return {'FINISHED'}

        mover_indexes = {
            'MOVE_UP': -1,
            'MOVE_DOWN': 1
        }
        try:
            move_to_index = bakejob.index + mover_indexes[self.action]
            bakejob_next = bakemaster.bakejobs[move_to_index]
            if move_to_index < 0 or move_to_index > len_of_bakejobs:
                raise IndexError
        except IndexError:
            return {'FINISHED'}
        bakemaster.bakejobs.move(bakejob.index, bakejob_next.index)
        bakejob.index, bakejob_next.index = bakejob_next.index, bakejob.index
        bakemaster.bakejobs_active_index = bakejob_next.index
        return {'FINISHED'}
