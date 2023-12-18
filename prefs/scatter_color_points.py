import bpy
import math
import bmesh


def root(n, power=3):
    if n <= 1 or 0 == power:
        return ()
    
    d = math.ceil(n ** (1 / power))
    n /= d
    power -= 1
    return (d, *root(n, power))


def verts():
    res = []

    n = 180
    s_max = 1.0
    v_max = 1.0
    r = s_max
    
    v_cylinder = math.pi * r ** 2 * v_max
    v_v = v_cylinder / n
    
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

    a0 = 0  # pcloud rotation angle, can be seeded
    phi = (1 + 5 ** 0.5) / 2
    radius = 0.2
    magnitude = 0.5
    
    radius_fact = 1 - radius
    if radius == 0:
        a_bevel = 0
    elif radius == 1:
        a_bevel = 0.5 * math.pi
    else:
        a_bevel = math.atan(v_max / (2 * s_max * (1 - radius)))
        
    max_r = math.sqrt(r ** 2 - (v_max / 4) ** 2)

    n += 1
    for i in range(1, n):
        incl_i = math.acos(1 - 2 * i / n)
        phi_i = 2 * math.pi * i / phi + a0
        
        z0 = 1
        #if abs(r * math.cos(incl_i) / 2) > v_max / 4:
            # z0 = 0
            #incl_i **= magnitude
        
        #if math.sin(incl_i) > math.sin(a_bevel):
        #    incl_i_m = 1.0
        #else:
        incl_i_m = math.sin(incl_i)
            
        x = r * math.cos(phi_i) * incl_i_m
        y = r * math.sin(phi_i) * incl_i_m
        z = r * math.cos(incl_i) * z0 #/ 2
        
        
        if z > v_max / 4:
            z = v_max / 2 + 0.5
            d = math.sqrt(x ** 2 + y ** 2)
            
            x *= (1 + r - max_r) / r
            y *= (1 + r - max_r) / r
            
            res.append((x, y, z))
            continue
            
        #z += v_max / 4
            #x *= 1 - (d / r)
            #y *= 1 - (d / r)
            #x *= (1 + (d / r) * magnitude)
            #y /= (1 + (d / r) * magnitude)
        
        elif z > 0:
            x /= incl_i_m
            y /= incl_i_m
        #elif radius_fact != 0:
        #    print(2 - math.sqrt(x ** 2 + y ** 2), abs(z - 0.5) / (v_max / 2), v_max * radius_fact / 2)
        #    x *= 1.5 - math.sqrt(x ** 2 + y ** 2)
        #    y *= 1.5 - math.sqrt(x ** 2 + y ** 2)
        
        #x *= x / s_max
        #x *= y / s_max
        
        #z /= 4
        res.append((x, y, z))
        #print(math.sin(incl_i), phi_i, x, y)
        
    
    print("----------")
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
