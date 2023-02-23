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


# Quickly add Cube objects with names for name matching config

import bpy

names = [
    "cube_low",
    "cube_high",
    "cube_cage",
    "monster_body",
    "monster_body_low",
    "monster_body_high",
    "monster_leg_low",
    "monster_leg_high",
    "monster_leg_low_2",
    "monster_leg_high_2",
    "monster_leg_high_2",
    "monster_leg",
    "monster_cage",
    "monster_leg_cage",
    "monster_leg_2_cage",
    "monster_leg_cage_3",
    "monster_body_cage",
    "flowers",
    "flowers_low",
    "flowers1_low",
    "flowers_1_low",
    "flowers1_high",
    "flowers1_decorations",
    "monster_leg_low_decal",
    "monster_leg_decal",
    "monster_leg_decal.001",
    "Plane",
]

for name in names:
    bpy.ops.mesh.primitive_cube_add()
    new_object = bpy.context.active_object
    new_object.name = name

print("%s: demo scene load finished" % __file__)

