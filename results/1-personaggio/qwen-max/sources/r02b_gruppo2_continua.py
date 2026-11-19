import math, random
from mathutils import Vector, Matrix, Euler

def clamp(v, a, b): return max(a, min(b, v))
random.seed(7)

def place(o, loc, scale=None, rot=None):
    mn = Vector([min(c[i] for c in o.bound_box) for i in range(3)])
    mx = Vector([max(c[i] for c in o.bound_box) for i in range(3)])
    c = (mn + mx) / 2
    if scale:
        for v in o.data.vertices:
            v.co = Vector(((v.co.x - c.x) * scale[0] + c.x, (v.co.y - c.y) * scale[1] + c.y, (v.co.z - c.z) * scale[2] + c.z))
    if rot:
        R = Matrix.Rotation(rot[1], 4, 'Y') if len(rot) == 2 else Euler(rot, 'XYZ').to_matrix().to_4x4()
        for v in o.data.vertices: v.co = R @ (Vector(v.co) - c) + c
    d = Vector(loc) - c
    for v in o.data.vertices: v.co = Vector(v.co) + d
    o.data.update()

O = bpy.data.objects
place(O["Naso"], (0, -0.100, 1.555), (1.0, 0.8, 2.0), (math.radians(12), 0, 0))
place(O["Bocca"], (0, -0.068, 1.505), (2.25, 1.0, 1.2))

def sphere(name, loc, r, scale=(1, 1, 1), seg=10, ring=6, mat="Pelle"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    o = bpy.context.active_object
    o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[mat])
    bpy.ops.object.shade_smooth()
    return o

for s, sx in (("L", 1), ("R", -1)):
    sphere("Orecchio." + s, (sx * 0.072, 0.005, 1.57), 0.016, (0.5, 0.8, 1.0))

hair = O["Capelli"]
for v in hair.data.vertices:
    v.co.x *= 1.06
    if v.co.z < 1.63: v.co.z -= 0.10 * clamp((1.63 - v.co.z) / 0.05, 0, 1)
hair.data.update()

def clump(name, base, direction, length, thick, mat="Capelli", bend=0.3):
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(radius1=thick, radius2=thick * 0.15, depth=length, vertices=8, location=(0, 0, 0))
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(rotation=True)
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-4: side = Vector((1, 0, 0))
    side.normalize()
    for v in o.data.vertices:
        t = clamp((v.co.z + length / 2) / length, 0, 1)
        v.co += side * (bend * length * t * t)
    o.location = Vector(base) + d * (length / 2)
    bpy.ops.object.transform_apply(location=True)
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[mat])
    bpy.ops.object.shade_smooth()
    return o

HC = Vector((0, 0.005, 1.60))
n = 0
for k in range(9):
    a = math.radians(k * 40 + 10)
    base = HC + Vector((0.070 * math.cos(a), 0.080 * math.sin(a), 0.040))
    d = Vector((0.5 * math.cos(a), 0.5 * math.sin(a), 1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.05, 0.075), random.uniform(0.011, 0.018)); n += 1
for k in range(10):
    a = math.radians(20 + k * 32)
    if 60 < a < 120: a += 40
    sx = 1 if k % 2 == 0 else -1
    base = HC + Vector((sx * 0.082, 0.05 * math.cos(a), 0.020))
    d = Vector((sx * 0.55, 0.25 * math.cos(a), -1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.10, 0.14), random.uniform(0.012, 0.019)); n += 1
for k in range(8):
    a = math.radians(-70 + k * 20)
    base = HC + Vector((0.07 * math.sin(a), 0.085, 0.0))
    d = Vector((0.3 * math.sin(a), 0.5, -1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.10, 0.14), random.uniform(0.012, 0.018)); n += 1
for k in range(5):
    x = -0.05 + k * 0.025
    base = Vector((x, -0.075, 1.645))
    d = Vector((0.15 * (k - 2), -0.35, -1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.04, 0.06), random.uniform(0.010, 0.015)); n += 1
place(O["Ciuffo"], (-0.045, -0.03, 1.665), (1.5, 1.8, 0.7), (0, math.radians(15)))
for k in range(4):
    t = k / 3.0
    base = Vector((-0.03 - 0.03 * t, -0.06 + 0.10 * t, 1.665 + 0.02 * math.sin(t * 3)))
    d = Vector((-0.4, 0.5, 0.8))
    clump("CiuffoB.%d" % k, base, d, 0.05, 0.011, mat="Bianco"); n += 1
log("Ciuffi capelli:", n)
bpy.ops.wm.save_mainfile()
render_viste("rev_2", viste=["fronte", "retro", "destra", "tre_quarti"])
