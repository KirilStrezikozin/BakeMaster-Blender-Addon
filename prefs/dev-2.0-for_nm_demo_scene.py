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
]

for name in names:
    bpy.ops.mesh.primitive_cube_add()
    new_object = bpy.context.active_object
    new_object.name = name

print("%s: demo scene load finished" % __file__)

