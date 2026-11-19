# revision helpers (exec'd by each revision step). Uses the round-1 lib.py for loft/tube/sphere/torus.
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
import bmesh, math, random
from mathutils import Vector, Matrix, Quaternion
V = Vector
RIG = bpy.data.objects.get("Scheletro")

# ---------------- target skeleton (revision numbers, metres) ----------------
A_UP, A_LOW, A_HAND = math.radians(45), math.radians(55), math.radians(53)
SH1 = V((0.19, 0.0, 1.40))
ELB1 = SH1 + V((math.cos(A_UP), 0, -math.sin(A_UP))) * 0.29
WRI1 = ELB1 + V((math.cos(A_LOW), 0, -math.sin(A_LOW))) * 0.25
HD1 = V((math.cos(A_HAND), 0, -math.sin(A_HAND)))
KNU1 = WRI1 + HD1 * 0.085
TIP1 = WRI1 + HD1 * 0.18
HIP1 = V((0.09, 0.0, 0.90))
KNEE1 = V((0.11, -0.01, 0.49))
ANK1 = V((0.13, 0.0, 0.08))
BALL1 = V((0.13, -0.12, 0.025))
TOE1 = V((0.13, -0.19, 0.025))

# new torso table (z, rx, rf, rb, yoff): hips 0.34x0.22 @0.90, waist 0.27x0.18 @1.08, chest 0.32x0.21 @1.27, shoulders 0.40
NEWT = [(0.79, 0.10, 0.07, 0.07, 0.0), (0.84, 0.152, 0.092, 0.108, 0.005), (0.90, 0.170, 0.100, 0.120, 0.01),
        (0.97, 0.153, 0.092, 0.100, 0.005), (1.03, 0.138, 0.088, 0.090, 0.0), (1.08, 0.135, 0.090, 0.090, 0.0),
        (1.14, 0.142, 0.098, 0.090, 0.0), (1.21, 0.155, 0.112, 0.094, 0.0), (1.27, 0.160, 0.115, 0.095, 0.0),
        (1.33, 0.170, 0.100, 0.096, 0.0), (1.38, 0.192, 0.082, 0.090, 0.005), (1.40, 0.200, 0.076, 0.086, 0.005),
        (1.425, 0.150, 0.065, 0.075, 0.01), (1.445, 0.080, 0.056, 0.062, 0.01), (1.46, 0.056, 0.050, 0.055, 0.01)]


def tab(t, z):
    if z <= t[0][0]:
        return list(t[0])
    if z >= t[-1][0]:
        return list(t[-1])
    for a, b in zip(t, t[1:]):
        if a[0] <= z <= b[0]:
            f = (z - a[0]) / (b[0] - a[0])
            return [a[j] + (b[j] - a[j]) * f for j in range(len(a))]


def new_pt(z, x, front=True, off=0.0):
    """point on the NEW torso surface (+off outward) at height z and side coordinate x"""
    zz, rx, rf, rb, yo = tab(NEWT, z)
    rx2 = rx + off
    q = math.sqrt(max(0.0, 1 - (x / rx2) ** 2))
    return V((x, yo - (rf + off) * q if front else yo + (rb + off) * q, z))


def pwl(pts, x):
    """piecewise linear through (x, y) pairs, linear extrapolation at the ends"""
    if x <= pts[0][0]:
        (x0, y0), (x1, y1) = pts[0], pts[1]
    elif x >= pts[-1][0]:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
    else:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                break
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def bind(ob, bones, rigid=False, power=4.0):
    """weights for a NEW piece: distance to the allowed bones (like round 1), armature modifier, parent"""
    rig = bpy.data.objects["Scheletro"]
    B = {b.name: (rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local) for b in rig.data.bones}
    bones = [b for b in bones if b in B]
    ob.vertex_groups.clear()
    gr = {b: ob.vertex_groups.new(name=b) for b in bones}

    def segd(p, a, b):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        return (p - (a + ab * t)).length

    def ws(p):
        l = sorted(((1.0 / (segd(p, *B[b]) + 0.01) ** power, b) for b in bones), reverse=True)[:3]
        tot = sum(w for w, _ in l)
        return [(w / tot, b) for w, b in l if w / tot > 0.02]
    if rigid or len(bones) == 1:
        c = sum((v.co for v in ob.data.vertices), V()) / max(1, len(ob.data.vertices))
        idx = [v.index for v in ob.data.vertices]
        for w, b in (ws(c) if len(bones) > 1 else [(1.0, bones[0])]):
            gr[b].add(idx, w, "REPLACE")
    else:
        for v in ob.data.vertices:
            for w, b in ws(v.co):
                gr[b].add([v.index], w, "REPLACE")
    if not ob.modifiers.get("Armature"):
        md = ob.modifiers.new("Armature", "ARMATURE")
        md.object = rig
    ob.parent = rig
    return ob


def obj(name):
    return bpy.data.objects.get(name)


def kill(name_or_ob):
    ob = obj(name_or_ob) if isinstance(name_or_ob, str) else name_or_ob
    if ob:
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def join(objs, name):
    objs = [o for o in objs if o]
    if not objs:
        return None
    tgt = objs[0]
    if len(objs) > 1:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = tgt
        with bpy.context.temp_override(active_object=tgt, object=tgt, selected_objects=objs,
                                       selected_editable_objects=objs):
            bpy.ops.object.join()
        tgt = bpy.context.view_layer.objects.active
    tgt.name = name
    tgt.data.name = name
    return tgt


def split_loose(ob):
    """separate an object into its loose parts; returns the list of parts (ob included)"""
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    before = set(bpy.data.objects)
    with bpy.context.temp_override(active_object=ob, object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")
    return [ob] + [o for o in bpy.data.objects if o not in before]


def centroid(ob):
    n = len(ob.data.vertices)
    return sum((v.co for v in ob.data.vertices), V()) / max(1, n)


def bbox(ob):
    xs = [v.co for v in ob.data.vertices]
    return (V((min(p.x for p in xs), min(p.y for p in xs), min(p.z for p in xs))),
            V((max(p.x for p in xs), max(p.y for p in xs), max(p.z for p in xs))))


def matname(ob):
    if not ob.data.polygons:
        return ""
    i = ob.data.polygons[0].material_index
    m = ob.data.materials[i] if i < len(ob.data.materials) else None
    return m.name if m else ""


def set_mat(name, rgb, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1)
    return m


def use_mat(ob, mat):
    """put material (object or name) on all faces of ob"""
    m = bpy.data.materials[mat] if isinstance(mat, str) else mat
    ob.data.materials.clear()
    ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = 0


def chars():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("_")]


def tri_report():
    tot = 0
    rows = []
    for o in sorted(chars(), key=lambda o: o.name):
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        tot += t
        rows.append("%s:%d" % (o.name, t))
    log("triangoli totali:", tot)
    log("per oggetto:", ", ".join(rows))
    return tot


def finish(group):
    bpy.context.view_layer.update()
    tri_report()
    bpy.ops.wm.save_mainfile()
    render_viste("rev_%s" % group)


def reloft(o, rings, seg, up=V((0, 1, 0)), cap=(True, True)):
    """re-shape an existing loft-made part in place (same vertices, new ring centres/radii)"""
    vs = o.data.vertices
    n = len(rings)
    need = n * seg + (1 if cap[0] else 0) + (1 if cap[1] else 0)
    if len(vs) != need:
        return False
    i = 0
    for r_i, r in enumerate(rings):
        c = V(r[0])
        a = V(rings[max(r_i - 1, 0)][0])
        b = V(rings[min(r_i + 1, n - 1)][0])
        u, v = frame(b - a, up)
        for k in range(seg):
            ang = 2 * math.pi * k / seg
            s = math.sin(ang)
            vs[i].co = c + u * math.cos(ang) * r[1] + v * s * (r[3] if s > 0 else r[2])
            i += 1
    if cap[0]:
        vs[i].co = V(rings[0][0])
        i += 1
    if cap[1]:
        vs[i].co = V(rings[-1][0])
    o.data.update()
    return True


def new_band(name, z1, z2, off, mat, seg=32, slope=0.0, extra_y=0.0):
    rr = []
    for z in (z1, z2):
        zz, rx, rf, rb, yo = tab(NEWT, z)
        rr.append(((0, yo, z), rx + off, rf + off + extra_y, rb + off))
    if slope:
        fn = lambda i, k, ang, p, c: V((p.x, p.y, p.z + slope * p.x))
        rr = [r + (fn,) for r in rr]
    return loft(name, rr, seg, (True, True), mat, True)


def matobj(name):
    return bpy.data.materials[name]


_M_orig = M


def M(name):
    """use the material as it is now in the file (revision colours), create it only if missing"""
    m = bpy.data.materials.get(name)
    return m if m else _M_orig(name)


def lin(c):
    """the brief's RGB values are display (sRGB) colours: convert to Blender's linear values"""
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


_set_mat_raw = set_mat


def set_mat(name, rgb, rough, metal=0.0):
    return _set_mat_raw(name, lin(rgb), rough, metal)


def retorus(o, c, R, r, normal, seg, seg2, scale=(1, 1)):
    vs = o.data.vertices
    if len(vs) != seg * seg2:
        return False
    n = V(normal).normalized()
    u, v = frame(n, V((0, 0, 1)) if abs(n.z) < 0.9 else V((0, 1, 0)))
    for i in range(seg):
        a = 2 * math.pi * i / seg
        d = u * math.cos(a) * scale[0] + v * math.sin(a) * scale[1]
        for j in range(seg2):
            b = 2 * math.pi * j / seg2
            vs[i * seg2 + j].co = V(c) + d * (R + r * math.cos(b)) + n * r * math.sin(b)
    o.data.update()
    return True


def subdivide(o, levels=1):
    md = o.modifiers.new("sub", "SUBSURF")
    md.levels = levels
    md.render_levels = levels
    # the subdivision must come before the armature
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_move_to_index(modifier="sub", index=0)
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_apply(modifier="sub")


def reset_colours():
    set_mat("pelle", (0.85, 0.68, 0.58), 0.5)
    set_mat("capelli", (0.10, 0.08, 0.07), 0.75)
    set_mat("ciocca", (0.80, 0.80, 0.78), 0.7)
    set_mat("occhi", (0.20, 0.11, 0.06), 0.3)
    set_mat("labbra", (0.70, 0.45, 0.40), 0.5)
    set_mat("bianco_occhi", (0.86, 0.84, 0.80), 0.4)
    set_mat("camicia_collo", (0.30, 0.33, 0.38), 0.85)
    set_mat("mantello_rev", (0.22, 0.34, 0.31), 0.9)
    set_mat("gilet", (0.13, 0.16, 0.22), 0.85)
    set_mat("cuoio", (0.36, 0.22, 0.12), 0.65)
    set_mat("cuoio_cintura", (0.30, 0.18, 0.09), 0.65)
    set_mat("cucitura", (0.05, 0.06, 0.08), 0.9)
    set_mat("ottone", (0.62, 0.45, 0.20), 0.35, 1.0)


def pca(o):
    import numpy as np
    P = np.array([tuple(v.co) for v in o.data.vertices])
    c = P.mean(axis=0)
    w, vec = np.linalg.eigh(np.cov((P - c).T))
    order = w.argsort()[::-1]
    axes = [V(tuple(vec[:, i])) for i in order]
    return V(tuple(c)), axes


def remap_cyl(o, a, b, r_new):
    """order-independent: map a cylinder-like part from its own main axis onto segment a->b, radius r_new"""
    c, axes = pca(o)
    ax = axes[0]
    if ax.dot(V(b) - V(a)) < 0:
        ax = -ax
    ss = [(v.co - c).dot(ax) for v in o.data.vertices]
    s0, s1 = min(ss), max(ss)
    rad = [((v.co - c) - ax * s).length for v, s in zip(o.data.vertices, ss)]
    r_old = max(rad) if rad else 1.0
    a, b = V(a), V(b)
    nax = (b - a).normalized()
    q = ax.rotation_difference(nax).to_matrix()
    for v, s in zip(o.data.vertices, ss):
        t = (s - s0) / max(1e-6, (s1 - s0))
        radial = q @ ((v.co - c) - ax * s)
        v.co = a.lerp(b, t) + radial * (r_new / r_old)
    o.data.update()


def rigid_to(o, new_c, new_n=None, scale=1.0, which=2):
    """order-independent rigid move (+uniform scale); new_n aligns the part's thinnest axis"""
    c, axes = pca(o)
    R = Matrix.Identity(3)
    if new_n is not None:
        n0 = axes[which]
        if n0.dot(V(new_n)) < 0:
            n0 = -n0
        R = n0.rotation_difference(V(new_n).normalized()).to_matrix()
    for v in o.data.vertices:
        v.co = V(new_c) + R @ ((v.co - c) * scale)
    o.data.update()


def weight_all(o, bone):
    o.vertex_groups.clear()
    g = o.vertex_groups.new(name=bone)
    g.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
    if not o.modifiers.get("Armature"):
        md = o.modifiers.new("Armature", "ARMATURE")
        md.object = bpy.data.objects["Scheletro"]
    o.parent = bpy.data.objects["Scheletro"]


def set_part_mat(o, matname_):
    use_mat(o, matname_)
