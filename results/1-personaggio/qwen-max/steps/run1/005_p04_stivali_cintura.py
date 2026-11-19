import math

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

def sphere(name, loc, r, seg=12, ring=6, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return o

def torus(name, loc, R, r, rot=(0, 0, 0), ms=12, ns=6):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=ms, minor_segments=ns, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o

def setmat(o, nm):
    o.data.materials.clear()
    o.data.materials.append(bpy.data.materials[nm])

for s, sx in (("L", 1), ("R", -1)):
    shaft = cyl("StivaleGamba." + s, (sx * 0.10, 0, 0.21), 0.072, 0.30, verts=12)
    foot = box("StivalePiede." + s, (sx * 0.10, -0.06, 0.05), (0.10, 0.26, 0.10))
    bpy.ops.object.select_all(action='DESELECT')
    shaft.select_set(True)
    foot.select_set(True)
    bpy.context.view_layer.objects.active = shaft
    bpy.ops.object.join()
    boot = bpy.context.active_object
    boot.name = "Stivale." + s
    setmat(boot, "Stivali")
    boot["bone"] = "shin." + s
    boot["bone2"] = "foot." + s
    for i, z in enumerate((0.26, 0.30, 0.34)):
        l = torus("Laccio.%s.%d" % (s, i), (sx * 0.10, 0, z), 0.074, 0.006, ms=10, ns=4)
        setmat(l, "CuoioScuro")
        l["bone"] = "shin." + s
    k = sphere("Ginocchiera." + s, (sx * 0.10, -0.065, 0.50), 0.055, scale=(1, 0.6, 1))
    setmat(k, "Cuoio")
    k["bone"] = "shin." + s
    w = torus("Fascia." + s, (sx * 0.10, 0, 0.38), 0.062, 0.012, ms=10, ns=5)
    setmat(w, "Manica")
    w["bone"] = "shin." + s

belt = cyl("Cintura", (0, 0, 0.99), 0.17, 0.07, verts=16)
belt.scale = (1, 0.75, 1)
setmat(belt, "Cuoio")
belt["bone"] = "pelvis"
buck = box("Fibbia", (0, -0.135, 0.99), (0.05, 0.02, 0.05))
setmat(buck, "Ottone")
buck["bone"] = "pelvis"
for i, (loc, dim) in enumerate((((0.15, -0.10, 0.93), (0.07, 0.05, 0.09)),
                                ((-0.15, -0.10, 0.93), (0.07, 0.05, 0.09)),
                                ((-0.17, 0.06, 0.93), (0.06, 0.05, 0.09)))):
    p = box("Tasca.%d" % i, loc, dim)
    setmat(p, "CuoioScuro")
    p["bone"] = "pelvis"
r1 = torus("Corda1", (0.18, 0.02, 0.88), 0.07, 0.022, rot=(0, math.radians(90), 0), ms=12, ns=6)
setmat(r1, "Corda")
r1["bone"] = "pelvis"
r2 = torus("Corda2", (0.20, 0.02, 0.88), 0.06, 0.020, rot=(0, math.radians(90), 0), ms=12, ns=6)
setmat(r2, "Corda")
r2["bone"] = "pelvis"
can = cyl("Contenitore", (-0.18, 0.06, 0.90), 0.032, 0.16, verts=10)
setmat(can, "OttoneScuro")
can["bone"] = "pelvis"
for s, sx in (("L", 1), ("R", -1)):
    st = box("Cinghia." + s, (sx * 0.06, -0.115, 1.24), (0.03, 0.012, 0.34), (0, math.radians(sx * 25), 0))
    setmat(st, "CuoioScuro")
    st["bone"] = "chest"
cl = box("Chiusura", (0, -0.125, 1.40), (0.04, 0.02, 0.04))
setmat(cl, "Ottone")
cl["bone"] = "chest"

render_viste("p04_stivali", viste=["fronte", "retro"])
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")