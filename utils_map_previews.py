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
from .utils_bm_gets import *
from .labels import BM_Labels

# Map Preview Configurators
def BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, map_tag):
    pass

def BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, map_tag):
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, map_tag)
    pass

def BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, map_tag):
    pass

def BM_IterableData_GetNewUniqueName_Simple(data, name_starter):
    index = 0
    for d in data:
        if d.name.find(name_starter) != -1:
            index += 1
    return "%s.%d" % (name_starter, index)

def BM_MAP_PROPS_MapPreview_ReassignMaterials_Prepare(self, context, map_tag):
    pass

def BM_MAP_PROPS_MapPreview_ReassignMaterials_Restore(self, context):
    pass

def BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context):
    pass
