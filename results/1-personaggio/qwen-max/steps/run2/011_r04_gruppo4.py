import math
from mathutils import Vector

def clamp(v, a, b): return max(a, min(b, v))
def prof(z, pts):
    if z <= pts[0][0]: return pts[0][1]
    for (z0, f0), (z1, f1) in zip(pts, pts[1:]):
        if z <= z1: return f0 + (f1 - f0) * (z - z0) / (z1 - z0)
    return pts[-1][1]
O = bpy.data.objects

def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

mat("Cuoio", (0.36, 0.22, 0.12), 0.65)
mat("TunicaScuro", (0.08, 0.10, 0.14), 0.9)
mat("Ottone", (0.62, 0.45, 0.20), 0.35, 1.0)

def place(o, loc, scale=None, rot=None):
    mn = Vector([min(c[i] for c in o.bound_box) for i in range(3)])
    mx = Vector([max(c[i] for c in o.bound_box) for i in range(3)])
    c = (mn + mx) / 2
    if scale:
        for v in o.data.vertices:
            v.co = Vector(((v.co.x - c.x) * scale[0] + c.x, (v.co.y - c.y) * scale[1] + c.y, (v.co.z - c.z) * scale[2] + c.z))
    if rot:
        R = Matrix.Rotation(rot, 4, 'Y')
        for v in o.data.vertices: v.co = R @ (Vector(v.co) - c) + c
    d = Vector(loc) - c
    for v in o.data.vertices: v.co = Vector(v.co) + d
    o.data.update()
from mathutils import Matrix

XH = [(1.06, 0.140), (1.27, 0.160), (1.42, 0.185)]
YH = [(1.06, 0.092), (1.27, 0.112), (1.42, 0.100)]
def surf_y(x, z):
    xh, yh = prof(z, XH), prof(z, YH)
    return -yh * math.sqrt(max(0.0, 1 - (x / xh) ** 2))

# cuciture verticali sul davanti della giacca
for k in range(5):
    x0 = -0.08 + k * 0.04
    verts, faces = [], []
    rows = 9
    for i in range(rows):
        z = 1.10 + i * (0.30 / (rows - 1))
        y = surf_y(x0, z) - 0.003
        verts.append((x0 - 0.002, y, z)); verts.append((x0 + 0.002, y, z))
    for i in range(rows - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("Cucitura.%d" % k)
    me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new("Cucitura.%d" % k, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(bpy.data.materials["TunicaScuro"])

# gonna della tunica: pannelli davanti e dietro, lati aperti, orlo irregolare
import random
random.seed(3)
for tag, sy in (("Davanti", -1), ("Dietro", 1)):
    cols, rows = 13, 6
    verts, faces = [], []
    hems = [0.80 + random.uniform(-0.03, 0.04) for _ in range(cols)]
    for i in range(rows):
        t = i / (rows - 1)
        for j in range(cols):
            u = -0.19 + 0.38 * j / (cols - 1)
            z = 1.06 - t * (1.06 - hems[j])
            y = sy * (0.10 + 0.045 * t) * math.sqrt(max(0.05, 1 - (u / 0.20) ** 2))
            verts.append((u, y, z))
    for i in range(rows - 1):
        for j in range(cols - 1):
            a = i * cols + j
            faces.append((a, a + 1, a + 1 + cols, a + cols))
    me = bpy.data.meshes.new("Gonna." + tag)
    me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new("Gonna." + tag, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(bpy.data.materials["Tunica"])
    sol = ob.modifiers.new("Sol", 'SOLIDIFY'); sol.thickness = 0.005
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=sol.name)
    bpy.ops.object.shade_smooth()

# bandoliere incrociate: nastro su petto, spalle e schiena fino al casco
def ribbon(name, pts, width, thick, matn):
    verts, faces = [], []
    P = [Vector(p) for p in pts]
    for i, p in enumerate(P):
        tang = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        sidev = tang.cross(Vector((0, 0, 1)))
        if sidev.length < 1e-4: sidev = Vector((1, 0, 0))
        sidev.normalize()
        verts.append(tuple(p - sidev * width / 2)); verts.append(tuple(p + sidev * width / 2))
    for i in range(len(P) - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(bpy.data.materials[matn])
    sol = ob.modifiers.new("Sol", 'SOLIDIFY'); sol.thickness = thick
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=sol.name)
    bpy.ops.object.shade_smooth()
    return ob

for s, sd in (("L", 1), ("R", -1)):
    pts = [(-sd * 0.15, -0.085, 1.04), (-sd * 0.07, -0.105, 1.15), (0, -0.112, 1.25),
           (sd * 0.07, -0.100, 1.33), (sd * 0.13, -0.055, 1.41), (sd * 0.13, 0.02, 1.435),
           (sd * 0.10, 0.10, 1.36), (sd * 0.08, 0.16, 1.24), (sd * 0.07, 0.19, 1.16)]
    ribbon("Bandoliera." + s, pts, 0.035, 0.008, "Cuoio")
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sd * 0.045, -0.108, 1.30))
    b = bpy.context.active_object
    b.name = "FibbiaPetto." + s
    b.scale = (0.03, 0.010, 0.03)
    b.rotation_euler = (0, sd * math.radians(37), 0)
    b.data.materials.append(bpy.data.materials["Ottone"])

# fascia orizzontale sotto il petto
bpy.ops.mesh.primitive_cylinder_add(radius=0.163, depth=0.03, vertices=16, location=(0, 0, 1.20))
f = bpy.context.active_object
f.name = "FasciaPetto"; f.scale = (1, 0.70, 1)
f.data.materials.append(bpy.data.materials["Cuoio"])
bpy.ops.object.shade_smooth()

# cintura principale in vita + fibbia con perno
place(O["Cintura"], (0, 0, 1.09), (0.86, 0.86, 0.86))
place(O["Fibbia"], (0, -0.108, 1.09), (1.4, 1.0, 1.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.118, 1.09))
pin = bpy.context.active_object
pin.name = "FibbiaPerno"; pin.scale = (0.006, 0.012, 0.04)
pin.data.materials.append(bpy.data.materials["Ottone"])

# cintura bassa obliqua sul bacino
bpy.ops.mesh.primitive_cylinder_add(radius=0.175, depth=0.04, vertices=16, location=(0, 0, 0.97), rotation=(0, math.radians(-10), 0))
hb = bpy.context.active_object
hb.name = "CinturaBacino"; hb.scale = (1, 0.72, 1)
hb.data.materials.append(bpy.data.materials["Cuoio"])
bpy.ops.object.shade_smooth()

# medaglione appeso sotto la fibbia
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.006, vertices=14, location=(0, -0.115, 0.99), rotation=(math.radians(90), 0, 0))
med = bpy.context.active_object
med.name = "Medaglione"
med.data.materials.append(bpy.data.materials["Ottone"])
bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=0.06, vertices=6, location=(0, -0.113, 1.03), rotation=(math.radians(8), 0, 0))
cord = bpy.context.active_object
cord.name = "CordinoMedaglione"
cord.data.materials.append(bpy.data.materials["CuoioScuro"])
place(O["Chiusura"], (0, -0.066, 1.44))
bpy.ops.wm.save_mainfile()
render_viste("rev_4", viste=["fronte", "retro", "tre_quarti"])
