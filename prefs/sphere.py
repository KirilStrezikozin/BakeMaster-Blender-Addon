import bpy
import math
import bmesh


def verts():
    res = []

    n = 1200
    r = 1

    a0 = 0  # pcloud rotation angle, can be seeded
    phi = (1 + 5 ** 0.5) / 2

    n += 1
    for i in range(1, n):
        incl_i = math.acos(1 - 2 * i / n)
        phi_i = 2 * math.pi * i / phi + a0

        x = r * math.cos(phi_i) * math.sin(incl_i)
        y = r * math.sin(phi_i) * math.sin(incl_i)
        z = r * math.cos(incl_i)

        res.append((x, y, z))

    return res


D = bpy.data

old_mesh = D.meshes.get("shape")
if old_mesh:
    D.meshes.remove(old_mesh)

old_obj = D.objects.get("shape")
if old_obj:
    D.objects.remove(old_obj)

mesh = D.meshes.new("shape")
obj = D.objects.new("shape", mesh)

ctx = bpy.context
sc = ctx.scene

sc.collection.objects.link(obj)

bm = bmesh.new()

for v in verts():
    bm.verts.new(v)

bm.to_mesh(mesh)
bm.free()
