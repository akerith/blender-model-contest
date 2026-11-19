# helper library for the character (exec'd by each step)
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Quaternion

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro"
V = Vector


def get_mat(name, color, rough=0.6, metal=0.0, emit=None, alpha=None, spec=0.4):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1)
        b.inputs["Emission Strength"].default_value = 2.0
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    m.diffuse_color = (color[0], color[1], color[2], 1)
    return m


MATS = {
    "pelle": ((0.72, 0.50, 0.40), 0.55, 0.0),
    "capelli": ((0.035, 0.028, 0.024), 0.7, 0.0),
    "ciocca": ((0.62, 0.60, 0.57), 0.7, 0.0),
    "gilet": ((0.075, 0.08, 0.09), 0.65, 0.0),
    "camicia": ((0.07, 0.10, 0.16), 0.8, 0.0),
    "lino": ((0.52, 0.44, 0.34), 0.9, 0.0),
    "pantaloni": ((0.10, 0.085, 0.075), 0.85, 0.0),
    "cuoio": ((0.19, 0.10, 0.05), 0.55, 0.0),
    "cuoio_scuro": ((0.09, 0.055, 0.035), 0.5, 0.0),
    "ottone": ((0.62, 0.42, 0.17), 0.35, 1.0),
    "ottone_scuro": ((0.30, 0.22, 0.10), 0.45, 1.0),
    "corda": ((0.50, 0.40, 0.27), 0.95, 0.0),
    "mantello": ((0.045, 0.10, 0.09), 0.85, 0.0),
    "mantello_sporco": ((0.24, 0.21, 0.155), 0.95, 0.0),
    "vetro": ((0.35, 0.55, 0.50), 0.1, 0.0),
    "verde_gemma": ((0.15, 0.45, 0.30), 0.3, 0.0),
    "occhi": ((0.02, 0.015, 0.01), 0.3, 0.0),
    "bianco_occhi": ((0.75, 0.72, 0.68), 0.4, 0.0),
    "labbra": ((0.52, 0.22, 0.20), 0.45, 0.0),
    "metallo": ((0.25, 0.25, 0.26), 0.4, 1.0),
}

MATS.update({
    "lino": ((0.40, 0.34, 0.26), 0.9, 0.0),
    "corda": ((0.36, 0.28, 0.17), 0.95, 0.0),
    "cuoio": ((0.15, 0.08, 0.042), 0.55, 0.0),
    "cuoio_scuro": ((0.075, 0.045, 0.03), 0.5, 0.0),
    "camicia": ((0.045, 0.07, 0.115), 0.8, 0.0),
    "gilet": ((0.05, 0.055, 0.065), 0.65, 0.0),
    "pantaloni": ((0.075, 0.065, 0.058), 0.85, 0.0),
    "pelle": ((0.66, 0.45, 0.36), 0.55, 0.0),
})


def M(name):
    c, r, met = MATS[name]
    return get_mat(name, c, r, met)


def clear(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def frame(t, up=V((0, 1, 0))):
    t = t.normalized()
    if abs(t.dot(up)) > 0.95:
        up = V((0, 0, 1)) if abs(t.z) < 0.95 else V((1, 0, 0))
    u = up.cross(t).normalized()
    v = t.cross(u).normalized()
    return u, v


def mesh_obj(name, verts, faces, mat=None, smooth=True, bones=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat:
        me.materials.append(M(mat) if isinstance(mat, str) else mat)
    for p in me.polygons:
        p.use_smooth = smooth
    if bones:
        ob["bones"] = ",".join(bones)
    return ob


def loft(name, rings, seg=16, cap=(True, True), mat=None, smooth=True, bones=None, up=V((0, 1, 0)),
         arc=None, twist=0.0):
    """rings: list of (center, rx, rf, rb) [+ optional dict with 'noise' fn(k,ang)->scale].
    rx along side axis u, rf (front, -v) / rb (back, +v) along v (~ +Y for vertical tubes).
    arc=(a0,a1) makes an open surface over that angle range (no caps)."""
    verts, faces = [], []
    n = len(rings)
    closed = arc is None
    cnt = seg if closed else seg + 1
    for i, r in enumerate(rings):
        c = V(r[0])
        a = V(rings[max(i - 1, 0)][0])
        b = V(rings[min(i + 1, n - 1)][0])
        u, v = frame(b - a, up)
        rx, rf, rb = r[1], r[2], r[3]
        fn = r[4] if len(r) > 4 else None
        for k in range(cnt):
            if closed:
                ang = 2 * math.pi * k / seg + twist * i
            else:
                ang = arc[0] + (arc[1] - arc[0]) * k / seg
            x = math.cos(ang) * rx
            s = math.sin(ang)
            y = s * (rb if s > 0 else rf)
            p = c + u * x + v * y
            if fn:
                p = fn(i, k, ang, p, c)
            verts.append(p)
    for i in range(n - 1):
        for k in range(seg):
            a = i * cnt + k
            b = i * cnt + (k + 1) % cnt
            faces.append((a, b, b + cnt, a + cnt))
    if closed:
        if cap[0]:
            verts.append(V(rings[0][0]))
            ci = len(verts) - 1
            for k in range(seg):
                faces.append((ci, (k + 1) % seg, k))
        if cap[1]:
            verts.append(V(rings[-1][0]))
            ci = len(verts) - 1
            o = (n - 1) * seg
            for k in range(seg):
                faces.append((ci, o + k, o + (k + 1) % seg))
    return mesh_obj(name, verts, faces, mat, smooth, bones)


def tube(name, a, b, r1, r2=None, seg=12, mat=None, bones=None, rings=2, cap=(True, True)):
    a, b = V(a), V(b)
    r2 = r1 if r2 is None else r2
    rr = []
    for i in range(rings):
        t = i / (rings - 1)
        r = r1 + (r2 - r1) * t
        rr.append((a.lerp(b, t), r, r, r))
    return loft(name, rr, seg, cap, mat, True, bones)


def path_tube(name, pts, r, seg=8, mat=None, bones=None, cap=(True, True), radii=None):
    rr = []
    for i, p in enumerate(pts):
        ri = radii[i] if radii else r
        rr.append((V(p), ri, ri, ri))
    return loft(name, rr, seg, cap, mat, True, bones)


def sphere(name, c, r, seg=16, rings=8, scale=(1, 1, 1), mat=None, bones=None, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = V((v.co.x * r * scale[0], v.co.y * r * scale[1], v.co.z * r * scale[2]))
        if rot:
            v.co = rot @ v.co
        v.co += V(c)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat:
        me.materials.append(M(mat))
    for p in me.polygons:
        p.use_smooth = True
    if bones:
        ob["bones"] = ",".join(bones)
    return ob


def box(name, c, size, mat=None, bones=None, rot=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = V((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        if rot:
            v.co = rot @ v.co
        v.co += V(c)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat:
        me.materials.append(M(mat))
    if bones:
        ob["bones"] = ",".join(bones)
    return ob


def torus(name, c, R, r, seg=24, seg2=8, normal=(0, 0, 1), mat=None, bones=None, scale=(1, 1, 1)):
    n = V(normal).normalized()
    u, v = frame(n, V((0, 0, 1)) if abs(n.z) < 0.9 else V((0, 1, 0)))
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        d = u * math.cos(a) * scale[0] + v * math.sin(a) * scale[1]
        for j in range(seg2):
            b = 2 * math.pi * j / seg2
            verts.append(V(c) + d * (R + r * math.cos(b)) + n * r * math.sin(b))
    for i in range(seg):
        for j in range(seg2):
            a = i * seg2 + j
            b = i * seg2 + (j + 1) % seg2
            c2 = ((i + 1) % seg) * seg2 + (j + 1) % seg2
            d2 = ((i + 1) % seg) * seg2 + j
            faces.append((a, b, c2, d2))
    return mesh_obj(name, verts, faces, mat, True, bones)


def mirror_obj(ob, name=None):
    """duplicate an object mirrored in X; swaps .L/.R in its bone list."""
    me = ob.data.copy()
    for v in me.vertices:
        v.co.x = -v.co.x
    me.flip_normals()
    nob = bpy.data.objects.new(name or ob.name.replace(".L", ".R"), me)
    bpy.context.scene.collection.objects.link(nob)
    if "bones" in ob:
        nob["bones"] = ob["bones"].replace(".L", ".#").replace(".R", ".L").replace(".#", ".R")
    return nob


def tri_count():
    t = 0
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH" and not ob.name.startswith("_"):
            for p in ob.data.polygons:
                t += len(p.vertices) - 2
    return t


def save():
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(LAVORO, "personaggio.blend"))


# --- skeleton numbers (shared) ---
SH = V((0.165, 0.0, 1.395))
ARM_ANG = math.radians(42)
ARM_D = V((math.cos(ARM_ANG), 0.0, -math.sin(ARM_ANG)))
ELB = SH + ARM_D * 0.285
WRI = ELB + ARM_D * 0.255
HAND_TIP = WRI + ARM_D * 0.185
PALM_N = V((-math.sin(ARM_ANG), 0.0, -math.cos(ARM_ANG)))  # palm normal (toward the body), left side
HIP = V((0.088, 0.0, 0.92))
KNEE = V((0.10, -0.012, 0.495))
ANK = V((0.112, 0.01, 0.09))


def render_parte(nome, keep, viste):
    """render only objects whose name starts with one of the prefixes in keep."""
    hidden = []
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH" and not any(ob.name.startswith(k) for k in keep) and ob.visible_get():
            ob.hide_set(True)
            ob.hide_render = True
            hidden.append(ob)
    try:
        render_viste(nome, viste=viste)
    finally:
        for ob in hidden:
            ob.hide_set(False)
            ob.hide_render = False


def solidify(ob, th=0.006, offset=-1.0):
    md = ob.modifiers.new("solid", "SOLIDIFY")
    md.thickness = th
    md.offset = offset
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    return ob


# torso table (z, rx, rf, rb, yoff) - same as p01
TORSO = [(0.80, 0.10, 0.07, 0.07, 0.0), (0.85, 0.150, 0.090, 0.105, 0.005), (0.91, 0.168, 0.098, 0.115, 0.01),
         (0.97, 0.148, 0.088, 0.100, 0.005), (1.03, 0.127, 0.082, 0.086, 0.0), (1.10, 0.129, 0.088, 0.086, 0.0),
         (1.16, 0.139, 0.106, 0.090, 0.0), (1.22, 0.149, 0.128, 0.094, 0.0), (1.28, 0.153, 0.113, 0.097, 0.0),
         (1.34, 0.158, 0.095, 0.097, 0.0), (1.39, 0.160, 0.080, 0.090, 0.005), (1.43, 0.13, 0.065, 0.075, 0.01),
         (1.46, 0.07, 0.05, 0.055, 0.01)]


def torso_ring(z):
    z = min(max(z, TORSO[0][0]), TORSO[-1][0])
    for i in range(len(TORSO) - 1):
        a, b = TORSO[i], TORSO[i + 1]
        if a[0] <= z <= b[0]:
            f = (z - a[0]) / (b[0] - a[0])
            return [a[j] + (b[j] - a[j]) * f for j in range(5)]
    return list(TORSO[-1])


def torso_pt(z, x, front=True, off=0.0):
    zz, rx, rf, rb, yo = torso_ring(z)
    rx2 = rx + off
    q = math.sqrt(max(0.0, 1 - (x / rx2) ** 2))
    y = yo - (rf + off) * q if front else yo + (rb + off) * q
    return V((x, y, z))


def band(name, z1, z2, off, mat, bones, seg=28, slope=0.0, extra=0.0):
    rr = []
    for z in (z1, z2):
        zz, rx, rf, rb, yo = torso_ring(z)
        rr.append(((0, yo, z), rx + off + extra, rf + off + extra, rb + off + extra))
    fn = (lambda i, k, ang, p, c: V((p.x, p.y, p.z + slope * p.x))) if slope else None
    if fn:
        rr = [r + (fn,) for r in rr]
    return loft(name, rr, seg, (True, True), mat, True, bones)
