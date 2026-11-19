import math
from mathutils import Vector

def box(name, loc, dim, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = dim
    return o

def cyl(name, loc, r, depth, rot=(0, 0, 0), verts=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o

def sphere(name, loc, r, seg=20, ring=10, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return o

def torus(name, loc, R, r, rot=(0, 0, 0), ms=16, ns=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=ms, minor_segments=ns, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o

def setmat(o, nm):
    o.data.materials.clear()
    o.data.materials.append(bpy.data.materials[nm])

cols, rows = 25, 5
verts, faces = [], []
for i in range(rows):
    t = i / (rows - 1)
    for j in range(cols):
        th = math.radians(-150 + 300 * j / (cols - 1))
        r = 0.10 + 0.13 * t
        z = 1.47 - 0.15 * t
        verts.append((r * math.sin(th), r * math.cos(th) * 0.85, z))
for i in range(rows - 1):
    for j in range(cols - 1):
        a = i * cols + j
        faces.append((a, a + 1, a + 1 + cols, a + cols))
mesh = bpy.data.meshes.new("MantelloSpalle")
mesh.from_pydata(verts, [], faces)
mesh.update()
yoke = bpy.data.objects.new("MantelloSpalle", mesh)
bpy.context.scene.collection.objects.link(yoke)
yoke.data.materials.append(bpy.data.materials["Mantello"])
sol = yoke.modifiers.new("Sol", 'SOLIDIFY')
sol.thickness = 0.012
bpy.context.view_layer.objects.active = yoke
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.object.shade_smooth()
yoke["bone"] = "chest"

helm = sphere("Casco", (0, 0.26, 1.27), 0.115, scale=(1, 0.9, 1.1))
setmat(helm, "Ottone")
helm["bone"] = "chest"
ring = torus("CascoCollare", (0, 0.24, 1.15), 0.09, 0.02)
setmat(ring, "OttoneScuro")
ring["bone"] = "chest"
port = torus("Oblo", (0, 0.365, 1.28), 0.055, 0.012, rot=(math.radians(90), 0, 0))
setmat(port, "Ottone")
port["bone"] = "chest"
glass = cyl("ObloVetro", (0, 0.36, 1.28), 0.05, 0.01, rot=(math.radians(90), 0, 0), verts=16)
setmat(glass, "Vetro")
glass["bone"] = "chest"
g1 = box("GrigliaV", (0, 0.368, 1.28), (0.006, 0.006, 0.10))
setmat(g1, "Ottone")
g1["bone"] = "chest"
g2 = box("GrigliaO", (0, 0.368, 1.28), (0.10, 0.006, 0.006))
setmat(g2, "Ottone")
g2["bone"] = "chest"
tv = cyl("ValvolaAlta", (0, 0.26, 1.40), 0.02, 0.03, verts=10)
setmat(tv, "OttoneScuro")
tv["bone"] = "chest"
for s, sx in (("L", 1), ("R", -1)):
    sv = cyl("Valvola." + s, (sx * 0.115, 0.26, 1.28), 0.018, 0.025, rot=(0, math.radians(90), 0), verts=10)
    setmat(sv, "OttoneScuro")
    sv["bone"] = "chest"

    cu = bpy.data.curves.new("Tubo." + s, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 6
    cu.bevel_depth = 0.014
    cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(2)
    pts = [(sx * 0.10, 0.26, 1.35), (sx * 0.16, 0.05, 1.44), (sx * 0.12, -0.11, 1.30)]
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    tob = bpy.data.objects.new("Tubo." + s, cu)
    bpy.context.scene.collection.objects.link(tob)
    bpy.ops.object.select_all(action='DESELECT')
    tob.select_set(True)
    bpy.context.view_layer.objects.active = tob
    bpy.ops.object.convert(target='MESH')
    tob = bpy.context.active_object
    setmat(tob, "Gomma")
    tob["bone"] = "chest"

render_viste("p06_zaino", viste=["retro", "destra", "fronte"])
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")