import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

LAV = r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro"
rad = math.radians


def V(*a):
    return Vector(a)


def hexc(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def mat(name, col, metal=0.0, rough=0.75, emit=0.0):
    if isinstance(col, str):
        col = hexc(col)
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        nt.nodes.clear()
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        o = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(b.outputs[0], o.inputs[0])
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (col[0], col[1], col[2], 1)
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (col[0], col[1], col[2], 1)
    m.use_backface_culling = True
    return m


def remove(name):
    o = bpy.data.objects.get(name)
    if o:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0 and isinstance(me, bpy.types.Mesh):
            bpy.data.meshes.remove(me)


def remove_prefix(pre):
    for o in list(bpy.data.objects):
        if o.name.startswith(pre):
            remove(o.name)


def obj(name, geom, material, bones, smooth=True, sharp=50, uvs=None):
    """geom = (verts, faces). bones = 'Bone' or 'A,B,C' (skin by distance among them)."""
    remove(name)
    verts, faces = geom
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.materials.append(material)
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        try:
            me.set_sharp_from_angle(angle=rad(sharp))
        except Exception:
            pass
    if uvs:
        uvl = me.uv_layers.new(name="UVMap")
        for l in me.loops:
            uvl.data[l.index].uv = uvs[l.vertex_index]
        me.uv_layers.active = uvl
        uvl.active_render = True
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o["bones"] = bones
    return o


# ---------- geometry (verts, faces) ----------
def merge(*geoms):
    verts, faces = [], []
    for g in geoms:
        if isinstance(g, list):
            g = merge(*g)
        k = len(verts)
        verts += list(g[0])
        faces += [tuple(i + k for i in f) for f in g[1]]
    return verts, faces


def mirror(g):
    return [Vector((-v[0], v[1], v[2])) for v in g[0]], [tuple(reversed(f)) for f in g[1]]


def xf(g, M):
    return [M @ Vector(v) for v in g[0]], g[1]


def rot_about(g, pivot, axis, deg):
    p = Vector(pivot)
    M = Matrix.Translation(p) @ Matrix.Rotation(rad(deg), 4, Vector(axis)) @ Matrix.Translation(-p)
    return xf(g, M)


def g_loft(rings, n=12, cap0=True, cap1=True, ref=(1, 0, 0), axes=None, sq=1.0):
    """rings: (center, rx, ry) or (center, rx, ry_plus, ry_minus). axes=(U,V) fixes the frame."""
    pts = [Vector(r[0]) for r in rings]
    verts, faces = [], []
    Up = None
    m = len(rings)
    for i, r in enumerate(rings):
        if axes:
            U, W = Vector(axes[0]), Vector(axes[1])
        else:
            if i == 0:
                t = pts[1] - pts[0]
            elif i == m - 1:
                t = pts[-1] - pts[-2]
            else:
                t = pts[i + 1] - pts[i - 1]
            t.normalize()
            rv = Up if Up is not None else Vector(ref)
            U = rv - t * rv.dot(t)
            if U.length < 1e-5:
                U = Vector((0, 1, 0)) - t * t.y
            U.normalize()
            W = t.cross(U)
            Up = U
        rx, ryp = r[1], r[2]
        rym = r[3] if len(r) > 3 else r[2]
        for j in range(n):
            a = 2 * math.pi * j / n
            c, s = math.cos(a), math.sin(a)
            if sq != 1.0:
                c = math.copysign(abs(c) ** sq, c)
                s = math.copysign(abs(s) ** sq, s)
            verts.append(pts[i] + U * (rx * c) + W * ((ryp if s > 0 else rym) * s))
    for i in range(m - 1):
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((i * n + j, i * n + j2, (i + 1) * n + j2, (i + 1) * n + j))
    if cap0:
        verts.append(pts[0].copy())
        k = len(verts) - 1
        for j in range(n):
            faces.append((k, (j + 1) % n, j))
    if cap1:
        verts.append(pts[-1].copy())
        k = len(verts) - 1
        b = (m - 1) * n
        for j in range(n):
            faces.append((k, b + j, b + (j + 1) % n))
    return verts, faces


def g_cyl(p0, p1, r, n=10, r1=None, cap0=True, cap1=True):
    return g_loft([(p0, r, r), (p1, r1 if r1 is not None else r, r1 if r1 is not None else r)], n=n, cap0=cap0, cap1=cap1)


def g_sphere(c, radii, seg=12, rings=8, M=None):
    if not isinstance(radii, (tuple, list)):
        radii = (radii, radii, radii)
    verts, faces = [], []
    verts.append(Vector((0, 0, radii[2])))
    for i in range(1, rings):
        ph = math.pi * i / rings
        for j in range(seg):
            a = 2 * math.pi * j / seg
            verts.append(Vector((radii[0] * math.sin(ph) * math.cos(a), radii[1] * math.sin(ph) * math.sin(a), radii[2] * math.cos(ph))))
    verts.append(Vector((0, 0, -radii[2])))
    for j in range(seg):
        faces.append((0, 1 + j, 1 + (j + 1) % seg))
    for i in range(rings - 2):
        for j in range(seg):
            a = 1 + i * seg + j
            b = 1 + i * seg + (j + 1) % seg
            faces.append((a, a + seg, b + seg, b))
    last = len(verts) - 1
    base = 1 + (rings - 2) * seg
    for j in range(seg):
        faces.append((last, base + (j + 1) % seg, base + j))
    c = Vector(c)
    if M is not None:
        verts = [M @ v for v in verts]
    return [v + c for v in verts], faces


def frame(axis):
    t = Vector(axis).normalized()
    rv = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
    U = (rv - t * rv.dot(t)).normalized()
    return U, t.cross(U), t


def g_torus(c, axis, R, r, nseg=16, nside=6, a0=0, a1=360, Ry=None):
    U, W, t = frame(axis)
    c = Vector(c)
    full = abs(a1 - a0) >= 360
    cnt = nseg if full else nseg + 1
    verts, faces = [], []
    for i in range(cnt):
        a = rad(a0 + (a1 - a0) * i / nseg)
        d = U * math.cos(a) + W * math.sin(a)
        cc = c + U * (R * math.cos(a)) + W * ((Ry or R) * math.sin(a))
        for j in range(nside):
            b = 2 * math.pi * j / nside
            verts.append(cc + d * (r * math.cos(b)) + t * (r * math.sin(b)))
    for i in range(cnt - 1 if not full else cnt):
        i2 = (i + 1) % cnt
        for j in range(nside):
            j2 = (j + 1) % nside
            faces.append((i * nside + j, i2 * nside + j, i2 * nside + j2, i * nside + j2))
    return verts, faces


def g_box(c, size, rot=None, M=None):
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    vs = [Vector((x, y, z)) for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]
    fs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    if rot:
        R = Euler((rad(rot[0]), rad(rot[1]), rad(rot[2]))).to_matrix()
        vs = [R @ v for v in vs]
    if M is not None:
        vs = [M @ v for v in vs]
    c = Vector(c)
    return [v + c for v in vs], fs


def g_bar(p0, p1, w, h, up=(0, 0, 1)):
    """box from p0 to p1 with width w (side) and height h (along up-ish)."""
    p0, p1 = Vector(p0), Vector(p1)
    t = (p1 - p0).normalized()
    u = Vector(up)
    u = u - t * u.dot(t)
    if u.length < 1e-5:
        u = Vector((1, 0, 0))
    u.normalize()
    s = t.cross(u)
    vs = []
    for p in (p0, p1):
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(p + s * (a * w / 2) + u * (b * h / 2))
    fs = [(0, 1, 2, 3), (7, 6, 5, 4), (4, 5, 1, 0), (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3)]
    return vs, fs


def catmull(pts, sub=4):
    pts = [Vector(p) for p in pts]
    if len(pts) < 3:
        return pts
    P = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(sub):
            t = k / sub
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def g_rope(pts, r, n=6, sub=4, cap=True, r_end=None):
    P = catmull(pts, sub) if sub > 1 else [Vector(p) for p in pts]
    m = len(P)
    rings = []
    for i, p in enumerate(P):
        rr = r if r_end is None else r + (r_end - r) * i / (m - 1)
        rings.append((p, rr, rr))
    return g_loft(rings, n=n, cap0=cap, cap1=cap)


# ---------- vertical shapes described by (z, cx, cy, rx, ry_back, ry_front) ----------
def vparams(spec, z):
    if z <= spec[0][0]:
        return spec[0]
    if z >= spec[-1][0]:
        return spec[-1]
    for a, b in zip(spec, spec[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in range(6))


def vpt(spec, z, ang, off=0.0):
    """point on the surface. ang in degrees: 0=+X, 90=+Y (back), -90 = front."""
    _, cx, cy, rx, rb, rf = vparams(spec, z)
    c, s = math.cos(rad(ang)), math.sin(rad(ang))
    return Vector((cx + (rx + off) * c, cy + ((rb if s > 0 else rf) + off) * s, z))


def g_vloft(spec, n=14, cap0=True, cap1=True):
    rings = [((s[1], s[2], s[0]), s[3], s[4], s[5]) for s in spec]
    return g_loft(rings, n=n, cap0=cap0, cap1=cap1, axes=((1, 0, 0), (0, 1, 0)))


def g_belt(spec, zfun, width, off=0.004, thick=0.006, n=24, a0=0, a1=360):
    """strap lying on a vertical shape. zfun(angle_deg)->z of the strap centre."""
    if not callable(zfun):
        z0 = zfun
        zfun = lambda a: z0
    full = abs(a1 - a0) >= 360
    cnt = n if full else n + 1
    verts, faces = [], []
    for i in range(cnt):
        a = a0 + (a1 - a0) * i / n
        z = zfun(a)
        for dz, o in ((-width / 2, off), (-width / 2, off + thick), (width / 2, off + thick), (width / 2, off)):
            verts.append(vpt(spec, z + dz, a, o))
    for i in range(cnt if full else cnt - 1):
        i2 = (i + 1) % cnt
        for j in range(4):
            j2 = (j + 1) % 4
            faces.append((i * 4 + j, i2 * 4 + j, i2 * 4 + j2, i * 4 + j2))
    if not full:
        faces.append((3, 2, 1, 0))
        b = (cnt - 1) * 4
        faces.append((b, b + 1, b + 2, b + 3))
    return verts, faces


def tris():
    n = 0
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            n += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return n


def save(name="personaggio"):
    bpy.ops.wm.save_as_mainfile(filepath=LAV + "\\" + name + ".blend")
    log("saved", name + ".blend", "- triangles:", tris())


# ---------- colours ----------
def materials():
    M = {}
    M["skin"] = mat("pelle", "#c99a7c", rough=0.6)
    M["hair"] = mat("capelli", "#2a2422", rough=0.55)
    M["hairw"] = mat("capelli_bianchi", "#d8d4cc", rough=0.55)
    M["cape"] = mat("mantello", "#4f7566", rough=0.9)
    M["capein"] = mat("mantello_interno", "#3b5a50", rough=0.95)
    M["tunic"] = mat("tunica", "#2f3a48", rough=0.85)
    M["vest"] = mat("corpetto", "#272c33", rough=0.7)
    M["linen"] = mat("lino", "#b9a587", rough=0.95)
    M["pants"] = mat("pantaloni", "#4a3f38", rough=0.9)
    M["leather"] = mat("cuoio", "#5a3d2a", rough=0.6)
    M["leatherd"] = mat("cuoio_scuro", "#3a2a20", rough=0.6)
    M["brass"] = mat("ottone", "#b08a3e", metal=0.9, rough=0.38)
    M["brassd"] = mat("ottone_scuro", "#7a5a2c", metal=0.9, rough=0.5)
    M["glass"] = mat("vetro", "#5d8f7c", metal=0.3, rough=0.15)
    M["rope"] = mat("corda", "#a8946c", rough=0.95)
    M["dark"] = mat("scuro", "#1c1815", rough=0.8)
    M["white"] = mat("bianco", "#e8e4dc", rough=0.5)
    M["lips"] = mat("labbra", "#9a5a52", rough=0.5)
    M["iron"] = mat("ferro", "#55524e", metal=0.9, rough=0.5)
    return M


# ---------- body measures ----------
SH = Vector((0.17, 0, 1.30))            # left shoulder joint
AD = Vector((0.788, 0, -0.616))         # left arm direction (38 deg down)
L_UP, L_FORE, L_HAND = 0.23, 0.21, 0.15
ELB = SH + AD * L_UP
WRI = ELB + AD * L_FORE
HEND = WRI + AD * L_HAND
AN = Vector((0.616, 0, 0.788))          # normal of the back of the left hand

TORSO = [  # z, cx, cy, rx, ry_back, ry_front
    (0.80, 0, 0.005, 0.168, 0.125, 0.115),
    (0.90, 0, 0.005, 0.158, 0.120, 0.110),
    (1.03, 0, 0.005, 0.128, 0.098, 0.098),
    (1.13, 0, 0.005, 0.146, 0.112, 0.118),
    (1.22, 0, 0.005, 0.160, 0.118, 0.128),
    (1.28, 0, 0.005, 0.166, 0.112, 0.112),
    (1.32, 0, 0.005, 0.130, 0.090, 0.088),
    (1.35, 0, 0.000, 0.062, 0.058, 0.055),
]
LEG = [  # left leg (trousers)
    (0.38, 0.140, 0.0, 0.058, 0.066, 0.062),
    (0.44, 0.135, 0.0, 0.064, 0.072, 0.064),
    (0.52, 0.125, 0.0, 0.064, 0.066, 0.068),
    (0.62, 0.112, 0.0, 0.076, 0.082, 0.080),
    (0.74, 0.097, 0.0, 0.088, 0.094, 0.092),
    (0.86, 0.086, 0.0, 0.088, 0.098, 0.094),
]
BOOT = [  # left boot shaft
    (0.06, 0.166, 0.0, 0.054, 0.062, 0.058),
    (0.16, 0.160, 0.0, 0.055, 0.062, 0.056),
    (0.30, 0.148, 0.0, 0.068, 0.078, 0.066),
    (0.40, 0.140, 0.0, 0.073, 0.080, 0.072),
    (0.43, 0.138, 0.0, 0.075, 0.081, 0.074),
]


def refine(spec, k=2):
    """smooth a vertical shape: k times more rings (Catmull-Rom on every column)"""
    P = [spec[0]] + list(spec) + [spec[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k
            out.append(tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(spec[-1])
    return out


TORSO, LEG, BOOT = refine(TORSO), refine(LEG), refine(BOOT)


def mspec(spec):
    return [(s[0], -s[1], s[2], s[3], s[4], s[5]) for s in spec]


BONES = {  # name: (head, tail, parent)
    "Hips": ((0, 0, 0.82), (0, 0, 0.95), None),
    "Spine": ((0, 0, 0.95), (0, 0, 1.10), "Hips"),
    "Chest": ((0, 0, 1.10), (0, 0, 1.33), "Spine"),
    "Neck": ((0, 0, 1.33), (0, -0.01, 1.42), "Chest"),
    "Head": ((0, -0.01, 1.42), (0, -0.01, 1.66), "Neck"),
    "LeftShoulder": ((0.03, 0, 1.30), tuple(SH), "Chest"),
    "LeftUpperArm": (tuple(SH), tuple(ELB), "LeftShoulder"),
    "LeftLowerArm": (tuple(ELB), tuple(WRI), "LeftUpperArm"),
    "LeftHand": (tuple(WRI), tuple(WRI + AD * 0.08), "LeftLowerArm"),
    "LeftUpperLeg": ((0.088, 0, 0.83), (0.125, 0, 0.52), "Hips"),
    "LeftLowerLeg": ((0.125, 0, 0.52), (0.165, 0.01, 0.09), "LeftUpperLeg"),
    "LeftFoot": ((0.165, 0.01, 0.09), (0.175, -0.12, 0.02), "LeftLowerLeg"),
    "LeftToes": ((0.175, -0.12, 0.02), (0.185, -0.21, 0.02), "LeftFoot"),
    "Cape1": ((0, 0.14, 1.05), (0, 0.17, 0.75), "Chest"),
    "Cape2": ((0, 0.17, 0.75), (0, 0.19, 0.45), "Cape1"),
    "Cape3": ((0, 0.19, 0.45), (0, 0.20, 0.15), "Cape2"),
}


def shot(name, center, size, d=(0, -1, 0), res=800):
    """extra close-up render (same idea as render_viste, but framed where I want)"""
    scn = bpy.context.scene
    cd = bpy.data.cameras.new("_gara_cam2")
    cd.type = "ORTHO"
    cd.ortho_scale = size
    cd.clip_end = 100
    cam = bpy.data.objects.new("_gara_cam2", cd)
    scn.collection.objects.link(cam)
    r = scn.render
    old = (scn.camera, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath)
    try:
        scn.camera = cam
        r.resolution_x = r.resolution_y = res
        r.resolution_percentage = 100
        c = Vector(center)
        cam.location = c + Vector(d).normalized() * 5
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        r.filepath = OUTBOX + "\\" + name + ".png"
        bpy.ops.render.render(write_still=True)
    finally:
        scn.camera, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath = old
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cd)


def lerp_keys(keys, v):
    if v <= keys[0][0]:
        return keys[0]
    if v >= keys[-1][0]:
        return keys[-1]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= v <= b[0]:
            t = (v - a[0]) / (b[0] - a[0])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5
            return tuple(a[k] + (b[k] - a[k]) * t for k in range(len(a)))
