import math
from mathutils import Vector

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
mat("Ottone", (0.62, 0.45, 0.20), 0.35, 1.0)
mat("OttoneScuro", (0.35, 0.24, 0.10), 0.45, 1.0)
mat("Telo", (0.66, 0.58, 0.45), 0.95)
def setmat(o, nm):
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[nm])
def center(o):
    cs = [Vector(c) for c in o.bound_box]
    return (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2

# casco: scala e posizione da specifica
h = O["Casco"]
c = center(h)
for v in h.data.vertices:
    v.co = (Vector(v.co) - c) * Vector((1.391, 1.449, 1.344)) + Vector((0, 0.25, 1.30))
h.data.update()
bpy.ops.object.select_all(action='DESELECT')
h.select_set(True); bpy.context.view_layer.objects.active = h
bpy.ops.object.shade_smooth()
# collare del casco
r = O["CascoCollare"]
c = center(r)
for v in r.data.vertices:
    p = Vector(v.co) - c
    v.co = Vector((p.x * 1.667, p.y * 1.667, p.z * 0.75)) + Vector((0, 0.25, 1.145))
r.data.update()
# oblo principale + vetro + griglia
ob = O["Oblo"]
c = center(ob)
for v in ob.data.vertices:
    p = Vector(v.co) - c
    rad = Vector((p.x, 0, p.z)); rl = rad.length
    if rl > 1e-6:
        ring = rad * (0.055 / rl)
        off = p - ring
        v.co = ring * (0.075 / 0.055) + off * 0.833 + Vector((0, 0.395, 1.30))
    else:
        v.co = p + Vector((0, 0.395, 1.30))
ob.data.update()
g = O["ObloVetro"]
c = center(g)
for v in g.data.vertices:
    p = Vector(v.co) - c
    v.co = Vector((p.x * 1.3, p.y, p.z * 1.3)) + Vector((0, 0.392, 1.30))
g.data.update()
for nm, ax in (("GrigliaV", 2), ("GrigliaO", 0)):
    o = O[nm]
    c = center(o)
    for v in o.data.vertices:
        p = Vector(v.co) - c
        p[ax] *= 1.3
        v.co = p + Vector((0, 0.402, 1.30))
    o.data.update()
# oblo laterali
for s, sd in (("L", 1), ("R", -1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.035, minor_radius=0.008, major_segments=12, minor_segments=6, location=(sd * 0.158, 0.25, 1.30), rotation=(0, math.radians(90), 0))
    t = bpy.context.active_object
    t.name = "ObloLat." + s
    setmat(t, "Ottone"); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=0.008, vertices=12, location=(sd * 0.160, 0.25, 1.30), rotation=(0, math.radians(90), 0))
    t = bpy.context.active_object
    t.name = "ObloLatVetro." + s
    setmat(t, "Vetro"); bpy.ops.object.shade_smooth()
# rivetti
for i in range(12):
    a = 2 * math.pi * i / 12
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004, segments=6, ring_count=4, location=(0.088 * math.cos(a), 0.398, 1.30 + 0.088 * math.sin(a)))
    t = bpy.context.active_object
    t.name = "RivettoOblo.%d" % i
    setmat(t, "OttoneScuro")
for i in range(16):
    a = 2 * math.pi * i / 16
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004, segments=6, ring_count=4, location=(0.150 * math.cos(a), 0.25 + 0.150 * math.sin(a), 1.145))
    t = bpy.context.active_object
    t.name = "RivettoCollare.%d" % i
    setmat(t, "OttoneScuro")
# bande verticali rilevate ai lati dell'oblo
for sd in (-1, 1):
    verts, faces = [], []
    rows = 9
    for i in range(rows):
        z = 1.16 + i * (0.30 / (rows - 1))
        q = 1 - (0.09 / 0.16) ** 2 - ((z - 1.30) / 0.17) ** 2
        y = 0.25 + 0.15 * math.sqrt(max(0.02, q)) + 0.004
        verts.append((sd * 0.09 - 0.0075, y, z)); verts.append((sd * 0.09 + 0.0075, y, z))
    for i in range(rows - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("BandaCasco.%d" % sd)
    me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new("BandaCasco.%d" % sd, me)
    bpy.context.scene.collection.objects.link(o)
    setmat(o, "Ottone")
    sol = o.modifiers.new("Sol", 'SOLIDIFY'); sol.thickness = 0.004
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=sol.name)

# tubi: rimappo il percorso esistente + coste + spirale a destra
OLD = {1: [(0.10, 0.26, 1.35), (0.16, 0.05, 1.44), (0.12, -0.11, 1.30)],
       -1: [(-0.10, 0.26, 1.35), (-0.16, 0.05, 1.44), (-0.12, -0.11, 1.30)]}
NEW = {1: [(0.13, 0.25, 1.20), (0.16, 0.16, 1.10), (0.17, 0.02, 1.02)],
       -1: [(-0.13, 0.25, 1.20), (-0.12, 0.22, 1.10), (-0.12, 0.20, 1.04)]}
def path_pt(pts, t):
    seg = t * (len(pts) - 1)
    i = min(int(seg), len(pts) - 2)
    f = seg - i
    return Vector(pts[i]).lerp(Vector(pts[i + 1]), f)
for sd in (1, -1):
    o = O["Tubo.%s" % ("L" if sd == 1 else "R")]
    op = [Vector(p) for p in OLD[sd]]
    for v in o.data.vertices:
        p = Vector(v.co)
        best, bt = 1e9, 0
        for i in range(len(op) - 1):
            a, b = op[i], op[i + 1]
            ab = b - a
            t = clamp((p - a).dot(ab) / ab.length_squared, 0, 1)
            d = (p - (a + ab * t)).length
            if d < best: best, bt = d, (i + t) / (len(op) - 1)
        oldc = path_pt(OLD[sd], bt)
        off = p - oldc
        v.co = path_pt(NEW[sd], bt) + off
    o.data.update()
    for i in range(12):
        t = i / 11.0
        c = path_pt(NEW[sd], t)
        tang = (path_pt(NEW[sd], min(1, t + 0.05)) - path_pt(NEW[sd], max(0, t - 0.05))).normalized()
        bpy.ops.mesh.primitive_torus_add(major_radius=0.016, minor_radius=0.004, major_segments=8, minor_segments=4, location=c)
        tr = bpy.context.active_object
        tr.name = "TuboCosta.%d.%d" % (sd, i)
        tr.rotation_euler = tang.to_track_quat('Z', 'Y').to_euler()
        setmat(tr, "Gomma")
# spirale piatta a destra
cu = bpy.data.curves.new("SpiraleTubo", 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 0.013; cu.bevel_resolution = 1; cu.resolution_u = 2
sp = cu.splines.new('POLY'); sp.points.add(71)
for i in range(72):
    t = i / 71.0
    a = t * 2 * math.pi * 2.2
    rr = 0.018 + 0.042 * t
    sp.points[i].co = (-0.12, 0.20 + rr * math.cos(a), 1.00 + rr * math.sin(a), 1)
so = bpy.data.objects.new("SpiraleTubo", cu)
bpy.context.scene.collection.objects.link(so)
bpy.ops.object.select_all(action='DESELECT')
so.select_set(True); bpy.context.view_layer.objects.active = so
bpy.ops.object.convert(target='MESH')
so = bpy.context.view_layer.objects.active
setmat(so, "Gomma"); bpy.ops.object.shade_smooth()

# bedroll + cinghie + loops di corda + harness
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.34, vertices=14, location=(0, 0.22, 1.06), rotation=(0, math.radians(90), 0))
br = bpy.context.active_object
br.name = "Bedroll"; setmat(br, "Telo"); bpy.ops.object.shade_smooth()
for x in (-0.10, 0.10):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.057, minor_radius=0.010, major_segments=12, minor_segments=5, location=(x, 0.22, 1.06), rotation=(0, math.radians(90), 0))
    t = bpy.context.active_object
    t.name = "BedrollCinghia.%.2f" % x
    setmat(t, "Cuoio"); bpy.ops.object.shade_smooth()
for k, x in enumerate((-0.06, 0.06)):
    cu = bpy.data.curves.new("LoopCasco.%d" % k, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 0.006; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(31); sp.use_cyclic_u = True
    for i in range(32):
        a = 2 * math.pi * i / 32
        sp.points[i].co = (x + 0.03 * math.cos(a), 0.245, 1.08 + 0.06 * math.sin(a), 1)
    lo = bpy.data.objects.new("LoopCasco.%d" % k, cu)
    bpy.context.scene.collection.objects.link(lo)
    bpy.ops.object.select_all(action='DESELECT')
    lo.select_set(True); bpy.context.view_layer.objects.active = lo
    bpy.ops.object.convert(target='MESH')
    lo = bpy.context.view_layer.objects.active
    setmat(lo, "Corda"); bpy.ops.object.shade_smooth()
for sd in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sd * 0.09, 0.205, 1.16))
    t = bpy.context.active_object
    t.name = "HarnessAttacco.%d" % sd
    t.scale = (0.035, 0.05, 0.02)
    t.rotation_euler = (math.radians(20), 0, 0)
    setmat(t, "Cuoio")
bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.03, vertices=16, location=(0, 0.06, 1.06))
ws = bpy.context.active_object
ws.name = "CinturaSchiena"; ws.scale = (1, 0.80, 1)
setmat(ws, "Cuoio"); bpy.ops.object.shade_smooth()
bpy.ops.wm.save_mainfile()
render_viste("rev_9", viste=["retro", "destra", "sinistra", "tre_quarti"])
