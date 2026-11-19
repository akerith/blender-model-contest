import math
from mathutils import Vector, Matrix

O = bpy.data.objects
def clamp(v, a, b): return max(a, min(b, v))
def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m
mat("Corda", (0.70, 0.62, 0.47), 0.95)
def setmat(o, nm):
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[nm])

# --- fix mantello: striature piu' rare, dorso fuori dalla giacca ---
nt = bpy.data.materials["Mantello"].node_tree
for n in nt.nodes:
    if n.type == 'VALTORGB':
        n.color_ramp.elements[0].position = 0.55
        n.color_ramp.elements[1].position = 0.72
    if n.type == 'MIX_RGB' and n.blend_type == 'MIX':
        n.inputs["Color2"].default_value = (0.32, 0.44, 0.40, 1)
    if n.type == 'MIX_RGB' and n.blend_type == 'MULTIPLY':
        for lk in list(nt.links):
            if lk.to_node == n and lk.to_socket.name == "Fac":
                nt.links.remove(lk)
        nz2 = next(q for q in nt.nodes if q.type == 'TEX_NOISE' and abs(q.inputs["Scale"].default_value - 9) < 0.1)
        mh = nt.nodes.new("ShaderNodeMath"); mh.operation = 'MULTIPLY'
        mh.inputs[1].default_value = 0.35
        nt.links.new(nz2.outputs["Fac"], mh.inputs[0])
        nt.links.new(mh.outputs["Value"], n.inputs["Fac"])
for nm in ("Mantello", "MantelloSpalle"):
    o = O[nm]
    for v in o.data.vertices:
        x, y, z = v.co
        if y > 0.02:
            t = clamp((1.45 - z) / 1.25, 0, 1)
            v.co.y = y + (0.03 if nm == "Mantello" else 0.025) * clamp((0.35 - t) / 0.35, 0, 1)
    o.data.update()

# --- corda: 4 loops ovali sul fianco DESTRO, anima + trecciolo ---
def oval_loop(name, center, ry, rz, minor, matn="Corda"):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.resolution_u = 2; cu.bevel_depth = minor; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(47); sp.use_cyclic_u = True
    for i in range(48):
        a = 2 * math.pi * i / 48
        sp.points[i].co = (center[0], center[1] + ry * math.cos(a), center[2] + rz * math.sin(a), 1)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    setmat(ob, matn); bpy.ops.object.shade_smooth()
    return ob

def twist_strand(name, center, ry, rz, phase):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.resolution_u = 1; cu.bevel_depth = 0.0035; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(95); sp.use_cyclic_u = True
    for i in range(96):
        a = 2 * math.pi * i / 96
        p = Vector((center[0], center[1] + ry * math.cos(a), center[2] + rz * math.sin(a)))
        N1 = Vector((0, math.cos(a), math.sin(a)))
        N2 = Vector((1, 0, 0))
        w = 14 * a + phase
        p += N1 * (0.006 * math.cos(w)) + N2 * (0.006 * math.sin(w))
        sp.points[i].co = (p.x, p.y, p.z, 1)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    setmat(ob, "Corda"); bpy.ops.object.shade_smooth()
    return ob

# riduco le due torce esistenti a anime sottili e le sposto a destra
for nm, R, r, cen in (("Corda1", 0.07, 0.022, (-0.170, 0.020, 0.80)),
                      ("Corda2", 0.06, 0.020, (-0.185, 0.045, 0.79))):
    o = O[nm]
    for v in o.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        ring = Vector((R * math.cos(th), R * math.sin(th), 0))
        off = Vector((x, y, z)) - ring
        v.co = ring * (0.05 / R) + off * (0.006 / r)
    o.data.update()
    mn = Vector([min(c[i] for c in o.bound_box) for i in range(3)])
    mx = Vector([max(c[i] for c in o.bound_box) for i in range(3)])
    cc = (mn + mx) / 2
    for v in o.data.vertices: v.co = Vector(v.co) - cc + Vector(cen)
    o.data.update()
loops = [(-0.170, 0.020, 0.80), (-0.185, 0.045, 0.79), (-0.160, 0.060, 0.81), (-0.195, 0.010, 0.80)]
for k, c in enumerate(loops[2:]):
    oval_loop("CordaLoop.%d" % k, c, 0.05, 0.08, 0.006)
for k, c in enumerate(loops):
    twist_strand("CordaTreccia.%d" % k, c, 0.05, 0.08, k * 1.3)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.17, 0.02, 0.93))
st = bpy.context.active_object
st.name = "CordaAttacco"; st.scale = (0.02, 0.012, 0.10)
setmat(st, "CuoioScuro")

# --- canister ottone+cuoio quasi orizzontale ---
can = O["Contenitore"]
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

# tasca rotonda con patta
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=12, ring_count=8, location=(-0.20, -0.02, 0.99))
p = bpy.context.active_object
p.name = "TascaRotonda"; p.scale = (1.0, 0.67, 0.89)
setmat(p, "Cuoio"); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.20, -0.045, 1.015))
fl = bpy.context.active_object
fl.name = "TascaPatta"; fl.scale = (0.05, 0.012, 0.035)
setmat(fl, "CuoioScuro")

# --- tubo mappe a sinistra + secondo tubo sottile ---
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

# striscia di tela strappata tra tubo e gamba
import random
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

# tasche piccole lungo la cintura (dietro e lati)
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
