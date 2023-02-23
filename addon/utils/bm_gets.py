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

###############################################################
### BM Gets Funcs ###
###############################################################
def BM_Object_Get(self, context):
    if self is None:
        object = [context.scene.bm_table_of_objects[context.scene.bm_props.global_active_index], True] 
    else:
        if hasattr(self, "global_map_object_index"):
            object1 = context.scene.bm_table_of_objects[self.global_map_object_index]
        else:
            object1 = self
        object = [object1, True]
    try:
        context.scene.objects[object[0].global_object_name]
    except (KeyError, AttributeError, UnboundLocalError):
        object[1] = False
    return object

def BM_Map_Get(self, object):
    if self is not None and hasattr(self, "global_map_object_index"):
        return self
    map = object.global_maps[object.global_maps_active_index]
    return map
