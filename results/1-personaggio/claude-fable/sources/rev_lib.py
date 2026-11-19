exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
TEXD = LAV + "\\texture"
scn = bpy.context.scene


def lin(c):
    """spec colours are read as screen (sRGB) values -> linear for Blender"""
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def interp(tab, v):
    """piecewise linear table [(x, y1, y2..)]; returns float or tuple"""
    if v <= tab[0][0]:
        r = tab[0][1:]
    elif v >= tab[-1][0]:
        r = tab[-1][1:]
    else:
        for a, b in zip(tab, tab[1:]):
            if a[0] <= v <= b[0]:
                t = (v - a[0]) / (b[0] - a[0])
                r = tuple(a[i] + (b[i] - a[i]) * t for i in range(1, len(a)))
                break
    return r[0] if len(r) == 1 else r


def islands(o):
    me = o.data
    n = len(me.vertices)
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b:
            par[a] = b
    comp = {}
    for i in range(n):
        comp.setdefault(find(i), []).append(i)
    vm = [None] * n
    for p in me.polygons:
        for vi in p.vertices:
            vm[vi] = p.material_index
    out = []
    for vs in comp.values():
        mi = next((vm[i] for i in vs if vm[i] is not None), None)
        if mi is None:
            continue
        cs = [me.vertices[i].co for i in vs]
        lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
        hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
        out.append(dict(v=vs, mat=me.materials[mi].name, lo=lo, hi=hi, c=(lo + hi) / 2))
    return out


def pick(o, mats, lo=(-9, -9, -9), hi=(9, 9, 9)):
    """vertex indices of the islands of o with a material in mats and centre inside the box"""
    if isinstance(o, str):
        o = bpy.data.objects[o]
    if isinstance(mats, str):
        mats = (mats,)
    out = []
    for i in islands(o):
        c = i["c"]
        if i["mat"] in mats and all(lo[k] <= c[k] <= hi[k] for k in range(3)):
            out += i["v"]
    return out


def move(o, idx, f):
    if isinstance(o, str):
        o = bpy.data.objects[o]
    vv = o.data.vertices
    for i in idx:
        vv[i].co = f(vv[i].co.copy())
    o.data.update()
    return len(idx)


def bbox(o, idx=None):
    if isinstance(o, str):
        o = bpy.data.objects[o]
    cs = [o.data.vertices[i].co for i in idx] if idx is not None else [v.co for v in o.data.vertices]
    lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    return lo, hi


def affine(o, idx, lo2, hi2):
    """fit the selected vertices into a new box"""
    lo, hi = bbox(o, idx)
    lo2, hi2 = Vector(lo2), Vector(hi2)
    def f(c):
        return Vector([lo2[k] + (c[k] - lo[k]) / max(hi[k] - lo[k], 1e-9) * (hi2[k] - lo2[k]) for k in range(3)])
    return move(o, idx, f)


def box_uv(me, SC=2.2):
    if me.uv_layers:
        return
    uvl = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda k: abs(n[k]))
        for li in p.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            uv = (c.y, c.z) if ax == 0 else ((c.x, c.z) if ax == 1 else (c.x, c.y))
            uvl.data[li].uv = (uv[0] * SC, uv[1] * SC)


def new(name, geom, material, bind, smooth=True, sharp=30, uvs=None):
    """a NEW piece of the revision. bind: 0 auto weights, 1 Chest, 2 Hips, 3 LowerArm.L, 4 Head, 5 cape"""
    if isinstance(material, str):
        material = bpy.data.materials[material]
    if isinstance(geom, list):
        geom = merge(*geom)
    o = obj(name, geom, material, "", smooth=smooth, sharp=sharp, uvs=uvs)
    box_uv(o.data)
    o["bind"] = bind
    return o


def tri_report():
    tot = 0
    for o in scn.objects:
        if o.type == "MESH":
            t = sum(len(p.vertices) - 2 for p in o.data.polygons)
            tot += t
    log("triangles in total:", tot)
    return tot


def salva():
    bpy.ops.wm.save_mainfile()
    tri_report()


# ---------- the NEW body (round-1 shapes after the group-1 remap), as vertical specs ----------
ZMAP = [(-0.004, 0.0), (0.09, 0.08), (0.43, 0.42), (0.52, 0.49), (0.80, 0.86), (1.03, 1.08), (1.22, 1.27), (1.30, 1.40),
        (1.365, 1.455), (1.424, 1.475), (1.4855, 1.505), (1.506, 1.53), (1.554, 1.585), (1.668, 1.66), (1.73, 1.70)]
SXY = [(0.80, 1.076, 0.957), (0.90, 1.076, 0.957), (1.03, 1.055, 0.918), (1.22, 1.0, 0.854), (1.28, 1.08, 0.90),
       (1.33, 1.10, 1.0), (1.38, 1.15, 1.0)]
CXO = [(0.06, 0.166), (0.16, 0.160), (0.30, 0.148), (0.40, 0.140), (0.44, 0.135), (0.52, 0.125), (0.62, 0.112), (0.74, 0.097), (0.86, 0.086)]
LRS = [(0.0, 0.90), (0.09, 0.83), (0.43, 0.80), (0.52, 0.82), (0.62, 0.76), (0.86, 0.85)]
NB = [(interp(ZMAP, s[0]), s[1], s[2] * interp(SXY, s[0])[1], s[3] * interp(SXY, s[0])[0], s[4] * interp(SXY, s[0])[1],
       s[5] * interp(SXY, s[0])[1]) for s in TORSO]


def _nleg(spec):
    out = []
    for s in spec:
        z2 = interp(ZMAP, s[0])
        r = interp(LRS, s[0])
        out.append((z2, 0.085 + 0.045 * (1 - min(z2, 0.90) / 0.90), 0.0, s[3] * r, s[4] * r, s[5] * r))
    return out


NLEG, NBOOT = _nleg(LEG), _nleg(BOOT)       # left side; mspec() gives the right side
SHN = Vector((0.19, 0, 1.40))
A1, A2 = 52.0, 46.0
U1 = Vector((math.cos(rad(A1)), 0, -math.sin(rad(A1))))
U2 = Vector((math.cos(rad(A2)), 0, -math.sin(rad(A2))))
N1 = Vector((math.sin(rad(A1)), 0, math.cos(rad(A1))))
N2 = Vector((math.sin(rad(A2)), 0, math.cos(rad(A2))))
ELN = SHN + U1 * 0.29
WRN = ELN + U2 * 0.25
TIPN = WRN + U2 * 0.18


def apn(s, y=0.0, n=0.0):
    """point on the NEW left arm: s metres from the shoulder joint, y towards the back, n towards the upper/outer side"""
    if s <= 0.29:
        return SHN + U1 * s + N1 * n + Vector((0, y, 0))
    return ELN + U2 * (s - 0.29) + N2 * n + Vector((0, y, 0))


def dbl(g, off=None):
    """both faces for thin cloth (the materials cull back faces)"""
    if isinstance(g, list):
        g = merge(*g)
    v, f = g
    v2 = [Vector(p) + (off if off else Vector((0, 0, 0))) for p in v]
    n = len(v)
    return list(v) + v2, list(f) + [tuple(i + n for i in reversed(q)) for q in f]


def both_new(name, g, material, bind, **kw):
    if isinstance(g, list):
        g = merge(*g)
    return new(name, merge(g, mirror(g)), material, bind, **kw)
