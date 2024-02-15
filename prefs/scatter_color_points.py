import bpy
import math
import bmesh
import typing

D = bpy.data
ctx = bpy.context
sc = ctx.scene


def root(n, power=3):
    if n <= 1 or 0 == power:
        return ()

    d = math.ceil(n ** (1 / power))
    n /= d
    power -= 1
    return (d, *root(n, power))


def make_plot() -> list[typing.Tuple[int]]:
    res = []
    return res


def make_circle() -> list[typing.Tuple[int]]:
    res = []

    n = 10
    s_max = 1.0
    v_max = 1.0
    r = s_max

    a0 = 0  # pcloud rotation angle, can be seeded
    phi0 = (1 + 5 ** 0.5) / 2

    # p is radial distance (saturation)
    # phi is azimuth (hue)
    # z is height (value)

    phi1 = 1 * math.pi / math.e * phi0 + a0
    p1 = math.sqrt(1 / n)
    x1 = p1 * math.cos(phi1)
    y1 = p1 * math.sin(phi1)
    z1 = 0
    phi2 = 2 * math.pi / math.e * phi0 + a0
    p2 = math.sqrt(2 / n)
    x2 = p2 * math.cos(phi2)
    y2 = p2 * math.sin(phi2)
    z2 = 0
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    z_step = 1 / d

    n += 1
    for z in range(2):
        for i in range(1, n):
            step_phi = 2 * math.pi * i / n * phi0
            p = math.sqrt(i / n)

            phi = i * math.pi / math.e * phi0 + a0

            x = p * math.cos(phi)
            y = p * math.sin(phi)
            z2 = z * v_max / z_step

            if i > 1:
                x1, y1, z1 = res[i - 2]
                d = math.sqrt((x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2)
                # print(d)
            res.append((x, y, z2))

    return res

    n = n * 4 + 1
    for z in range(1, 2):
        for i in range(1, n):
            incl_i = math.acos(1 - 2 * i / n)
            phi_i = 2 * math.pi * i / phi + a0

            x = r * math.cos(phi_i) * math.sin(incl_i)
            y = r * math.sin(phi_i) * math.sin(incl_i)
            z0 = r * math.cos(incl_i)

            if z0 < 0.5:
                break

            res.append((x, y, z / 10))

    return res


def make_cube() -> list[typing.Tuple[int]]:
    res = []

    n = 180
    s_max = 1.0
    v_max = 1.0
    # r = s_max

    # v_cylinder = math.pi * r ** 2 * v_max
    # v_v = v_cylinder / n

    dimensions = root(n) or n
    print(math.prod(dimensions))

    for z in range(dimensions[2]):
        for y in range(dimensions[1]):
            for x in range(dimensions[0]):
                z1 = z * v_max / (dimensions[2] - 1)
                y1 = y * s_max * 2 / (dimensions[1] - 1)
                x1 = x * s_max * 2 / (dimensions[0] - 1)
                res.append((x1, y1, z1))
    return res


# def make_cylinder_surface() -> list[typing.Tuple[int]]:
#     res = []
#
#     n = 180
#     s_max = 1.0
#     v_max = 1.0
#     r = s_max
#
#     a0 = 0  # pcloud rotation angle, can be seeded
#     phi = (1 + 5 ** 0.5) / 2
#     radius = 0.2
#     magnitude = 0.5
#
#     radius_fact = 1 - radius
#     if radius == 0:
#         a_bevel = 0
#     elif radius == 1:
#         a_bevel = 0.5 * math.pi
#     else:
#         a_bevel = math.atan(v_max / (2 * s_max * (1 - radius)))
#
#     max_r = math.sqrt(r ** 2 - (v_max / 4) ** 2)
#
#     n += 1
#     for i in range(1, n):
#         incl_i = math.acos(1 - 2 * i / n)
#         phi_i = 2 * math.pi * i / phi + a0
#
#         z0 = 1
#         # if abs(r * math.cos(incl_i) / 2) > v_max / 4:
#         # z0 = 0
#         # incl_i **= magnitude
#
#         # if math.sin(incl_i) > math.sin(a_bevel):
#         #    incl_i_m = 1.0
#         # else:
#         incl_i_m = math.sin(incl_i)
#
#         x = r * math.cos(phi_i) * incl_i_m
#         y = r * math.sin(phi_i) * incl_i_m
#         z = r * math.cos(incl_i) * z0  # / 2
#
#         if z > v_max / 4:
#             z = v_max / 2 + 0.5
#             d = math.sqrt(x ** 2 + y ** 2)
#
#             x *= (1 + r - max_r) / r
#             y *= (1 + r - max_r) / r
#
#             res.append((x, y, z))
#             continue
#
#         # z += v_max / 4
#             # x *= 1 - (d / r)
#             # y *= 1 - (d / r)
#             # x *= (1 + (d / r) * magnitude)
#             # y /= (1 + (d / r) * magnitude)
#
#         elif z > 0:
#             x /= incl_i_m
#             y /= incl_i_m
#         # elif radius_fact != 0:
#         #    print(2 - math.sqrt(x ** 2 + y ** 2),
#         #          abs(z - 0.5) / (v_max / 2), v_max * radius_fact / 2)
#         #    x *= 1.5 - math.sqrt(x ** 2 + y ** 2)
#         #    y *= 1.5 - math.sqrt(x ** 2 + y ** 2)
#
#         # x *= x / s_max
#         # x *= y / s_max
#
#         # z /= 4
#         res.append((x, y, z))
#         # print(math.sin(incl_i), phi_i, x, y)
#
#     print("----------")
#     return res


def mesh_clean() -> None:
    old_mesh = D.meshes.get("shape")
    old_obj = D.objects.get("shape")

    try:
        if old_mesh:
            D.meshes.remove(old_mesh)
        if old_obj:
            D.objects.remove(old_obj)
    except ReferenceError:
        pass

    return None


def mesh_create() -> typing.Tuple[bpy.types.Object, bpy.types.Mesh]:
    mesh = D.meshes.new("shape")
    obj = D.objects.new("shape", mesh)

    sc.collection.objects.link(obj)

    return obj, mesh


def main() -> None:
    _ = mesh_clean()
    _, mesh = mesh_create()

    bm = bmesh.new()

    for v in make_plot():
        bm.verts.new(v)

    bm.to_mesh(mesh)
    bm.free()

    return None


if __name__ == "__main__":
    _ = main()
