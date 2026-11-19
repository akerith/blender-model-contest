import math
from mathutils import Vector, Matrix

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
mat("Manica", (0.82, 0.76, 0.64), 0.9)
mat("Guanti", (0.26, 0.16, 0.09), 0.65)
mat("CuoioScuro", (0.20, 0.12, 0.07), 0.65)
vv = mat("VetroVerde", (0.25, 0.55, 0.35), 0.1)
vv.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.6
if hasattr(vv, "surface_render_method"): vv.surface_render_method = 'BLENDED'

def setmat(o, nm):
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[nm])
def cone_between(name, p1, p2, r1, r2, verts=12, matn="Manica"):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d.length, vertices=verts, location=(p1 + p2) / 2)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    setmat(o, matn)
    bpy.ops.object.shade_smooth()
    return o
def ring(name, center, axis, R, r, matn, ms=14, ns=6):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=ms, minor_segments=ns, location=center)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    setmat(o, matn)
    bpy.ops.object.shade_smooth()
    return o

for s, sd in (("L", 1), ("R", -1)):
    S = Vector((sd * 0.19, 0, 1.40)); E = Vector((sd * 0.38, 0, 1.18)); W = Vector((sd * 0.54, 0, 0.99))
    u = (E - S).normalized(); f = (W - E).normalized()
    cone_between("Manica." + s, S + u * 0.02, E - u * 0.01, 0.050, 0.055, 12, "Manica")
    for k, t in enumerate((0.72, 0.84, 0.96)):
        ring("ManicaRollo.%s.%d" % (s, k), S + u * (0.29 * t), u, 0.052, 0.011, "Manica", 12, 6)
    gtop = E - f * 0.04
    cone_between("Guanto." + s, W, gtop, 0.0375, 0.0475, 12, "Guanti")
    ring("GuantoBordo." + s, gtop, f, 0.048, 0.0075, "Guanti", 14, 6)
    n = Vector((sd * 0.765, 0, 0.644))
    for k, t in enumerate((0.02, 0.10, 0.19)):
        c = W + f * t
        rr = 0.0375 + (0.0475 - 0.0375) * (t / 0.21)
        ring("GuantoCinghia.%s.%d" % (s, k), c, f, rr + 0.002, 0.0075, "CuoioScuro", 12, 5)
        bpy.ops.mesh.primitive_cube_add(size=1, location=c + n * (rr + 0.006))
        b = bpy.context.active_object
        b.name = "GuantoFibbia.%s.%d" % (s, k)
        b.scale = (0.008, 0.015, 0.015)
        b.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        setmat(b, "Ottone")
    if s == "L":
        g = O["Gauge"]
        c = W - f * 0.06 + n * 0.040
        mn = Vector([min(q[i] for q in g.bound_box) for i in range(3)])
        mx = Vector([max(q[i] for q in g.bound_box) for i in range(3)])
        cc = (mn + mx) / 2
        for v in g.data.vertices: v.co = (Vector(v.co) - cc) * 1.25 + cc
        g.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        g.location = c
        bpy.ops.object.select_all(action='DESELECT')
        g.select_set(True); bpy.context.view_layer.objects.active = g
        bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
        ring("GaugeBordo", c + n * 0.008, n, 0.026, 0.003, "Ottone", 14, 5)
        cone_between("GaugeVetro", c + n * 0.006, c + n * 0.010, 0.022, 0.022, 14, "VetroVerde")

# --- mani: unico pezzo eliminato e ricostruito (erano scatole) ---
for s in ("L", "R"):
    bpy.data.objects.remove(O["Mano." + s], do_unlink=True)
log("Eliminate Mano.L/R (scatole): ricostruite con dita")

def build_hand(s, sd):
    W = Vector((sd * 0.54, 0, 0.99))
    f = Vector((sd * 0.644, 0, -0.765))
    np_ = Vector((0, 0.34, -0.94)).normalized()
    side = np_.cross(f).normalized()
    if s == "R": side = -side
    parts = []
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    palm = bpy.context.active_object
    palm.name = "Palmo." + s
    Rf = Matrix((side, np_, f)).transposed().to_4x4()
    palm.matrix_world = Matrix.Translation(W + f * 0.045) @ Rf @ Matrix.Diagonal((0.08, 0.03, 0.085, 1))
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    bev = palm.modifiers.new("Bevel", 'BEVEL'); bev.width = 0.006; bev.segments = 2
    bpy.ops.object.modifier_apply(modifier=bev.name)
    parts.append(palm)
    lengths = (0.075, 0.085, 0.080, 0.065)
    offs = (-0.030, -0.010, 0.010, 0.030)
    spreads = (-12, -4, 4, 12)
    for k in range(4):
        d = f.copy()
        Rspread = Matrix.Rotation(math.radians(spreads[k] * sd), 4, np_)
        d = Rspread @ d
        p = W + f * 0.085 + side * offs[k]
        segl = (0.40, 0.35, 0.25)
        r0 = 0.009
        for j in range(3):
            L = lengths[k] * segl[j]
            p2 = p + d * L
            o = cone_between("Dito.%s.%d.%d" % (s, k, j), p, p2, r0, r0 * 0.8, 10, "Guanti")
            parts.append(o)
            p = p2
            r0 *= 0.8
            d = Matrix.Rotation(math.radians(-10), 4, side) @ d
    tb = W + f * 0.015 + side * 0.038
    td = (f * math.cos(math.radians(40)) + Vector((0, -1, 0)) * math.sin(math.radians(40))).normalized()
    if s == "R": td = (f * math.cos(math.radians(40)) + Vector((0, -1, 0)) * math.sin(math.radians(40))).normalized()
    p = tb
    for j, L in enumerate((0.035, 0.030)):
        p2 = p + td * L
        parts.append(cone_between("Pollice.%s.%d" % (s, j), p, p2, 0.011 - j * 0.002, 0.009 - j * 0.002, 10, "Guanti"))
        p = p2
        td = Matrix.Rotation(math.radians(-12), 4, side) @ td
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, segments=10, ring_count=6, location=tb)
    parts.append(bpy.context.active_object)
    parts[-1].name = "PolliceBase." + s
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    h = bpy.context.view_layer.objects.active
    h.name = "Mano." + s
    setmat(h, "Guanti")
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    return h

for s, sd in (("L", 1), ("R", -1)):
    h = build_hand(s, sd)
    log("Mano.%s tri %d" % (s, sum(len(p.vertices) - 2 for p in h.data.polygons)))
bpy.ops.wm.save_mainfile()
render_viste("rev_5", viste=["fronte", "tre_quarti", "destra"])
