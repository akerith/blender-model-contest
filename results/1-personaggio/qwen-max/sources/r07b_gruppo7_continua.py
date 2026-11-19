import math, random
from mathutils import Vector, Matrix

O = bpy.data.objects
def setmat(o, nm):
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[nm])

can = O.get("Contenitore")
if can is None:
    can = O["Valvola.R.001"]
    can.name = "Contenitore"
    log("Canister recuperato da Valvola.R.001")
mn = Vector([min(c[i] for c in can.bound_box) for i in range(3)])
mx = Vector([max(c[i] for c in can.bound_box) for i in range(3)])
cc = (mn + mx) / 2
R = Matrix.Rotation(math.radians(80), 4, 'X')
for v in can.data.vertices:
    p = (Vector(v.co) - cc) * Vector((1.09, 1.09, 1.25))
    v.co = R @ p + Vector((-0.24, -0.03, 0.90))
can.data.update()
setmat(can, "Cuoio")
axis = R @ Vector((0, 0, 1))
for t in (-0.10, 0.10):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=0.02, vertices=12, location=Vector((-0.24, -0.03, 0.90)) + axis * t)
    o = bpy.context.active_object
    o.name = "CanisterTappo.%d" % (t * 100)
    o.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    setmat(o, "Ottone"); bpy.ops.object.shade_smooth()
for t in (-0.05, 0.05):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.036, minor_radius=0.004, major_segments=12, minor_segments=5, location=Vector((-0.24, -0.03, 0.90)) + axis * t)
    o = bpy.context.active_object
    o.name = "CanisterFascia.%d" % (t * 100)
    o.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    setmat(o, "Ottone"); bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=12, ring_count=8, location=(-0.20, -0.02, 0.99))
p = bpy.context.active_object
p.name = "TascaRotonda"; p.scale = (1.0, 0.67, 0.89)
setmat(p, "Cuoio"); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.20, -0.045, 1.015))
fl = bpy.context.active_object
fl.name = "TascaPatta"; fl.scale = (0.05, 0.012, 0.035)
setmat(fl, "CuoioScuro")

bpy.ops.mesh.primitive_cylinder_add(radius=0.0375, depth=0.45, vertices=14, location=(0.22, -0.02, 0.755))
mt = bpy.context.active_object
mt.name = "TuboMappe"; setmat(mt, "Cuoio"); bpy.ops.object.shade_smooth()
for z in (0.96, 0.55):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.039, depth=0.04, vertices=14, location=(0.22, -0.02, z))
    o = bpy.context.active_object
    o.name = "TuboMappeTappo.%.2f" % z
    setmat(o, "Ottone"); bpy.ops.object.shade_smooth()
for z in (0.85, 0.65):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.039, minor_radius=0.005, major_segments=12, minor_segments=5, location=(0.22, -0.02, z))
    o = bpy.context.active_object
    o.name = "TuboMappeCinghia.%.2f" % z
    setmat(o, "CuoioScuro"); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.35, vertices=12, location=(0.285, -0.02, 0.80))
t2 = bpy.context.active_object
t2.name = "TuboSottile"; setmat(t2, "CuoioScuro"); bpy.ops.object.shade_smooth()
for z in (0.965, 0.635):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.025, vertices=12, location=(0.285, -0.02, z))
    o = bpy.context.active_object
    o.name = "TuboSottileTappo.%.2f" % z
    setmat(o, "Ottone"); bpy.ops.object.shade_smooth()

random.seed(9)
cols, rows = 5, 7
verts, faces = [], []
hems = [0.62 + random.uniform(-0.04, 0.03) for _ in range(cols)]
for i in range(rows):
    t = i / (rows - 1)
    for j in range(cols):
        u = 0.135 + 0.07 * j / (cols - 1)
        z = 0.98 - t * (0.98 - hems[j])
        verts.append((u, -0.075 - 0.01 * math.sin(j * 2), z))
for i in range(rows - 1):
    for j in range(cols - 1):
        a = i * cols + j
        faces.append((a, a + 1, a + 1 + cols, a + cols))
me = bpy.data.meshes.new("TelaStrappata")
me.from_pydata(verts, [], faces); me.update()
ob = bpy.data.objects.new("TelaStrappata", me)
bpy.context.scene.collection.objects.link(ob)
setmat(ob, "Manica")
sol = ob.modifiers.new("Sol", 'SOLIDIFY'); sol.thickness = 0.003
bpy.context.view_layer.objects.active = ob
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.object.shade_smooth()

for nm, loc in (("Tasca.1", (0.10, 0.105, 1.05)), ("Tasca.2", (-0.10, 0.105, 1.05)), ("Tasca.3", (0.165, 0.03, 1.04))):
    o = O[nm]
    mn = Vector([min(c[i] for c in o.bound_box) for i in range(3)])
    mx = Vector([max(c[i] for c in o.bound_box) for i in range(3)])
    cc = (mn + mx) / 2
    for v in o.data.vertices:
        v.co = (Vector(v.co) - cc) * Vector((0.86, 1.0, 0.33)) + Vector(loc)
    o.data.update()
bpy.ops.wm.save_mainfile()
render_viste("rev_7", viste=["fronte", "destra", "sinistra", "tre_quarti"])
