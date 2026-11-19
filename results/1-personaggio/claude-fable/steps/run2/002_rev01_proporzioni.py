exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 1 - body proportions and pose: the existing mesh is re-shaped, nothing is deleted
P = bpy.data.objects["Personaggio"]
arm = bpy.data.objects["Scheletro"]
me = P.data
for m in list(P.modifiers):
    P.modifiers.remove(m)
P.parent = None
# back to the construction coordinates of round 1 (undo the final scale)
b = arm.data.bones["LeftUpperArm"].head_local
k = b.x / 0.17
zoff = b.z / k - 1.30
for v in me.vertices:
    v.co = Vector((v.co.x / k, v.co.y / k, v.co.z / k - zoff))
log("round-1 scale k=%.4f zoff=%.4f" % (k, zoff))

gname = {g.index: g.name for g in P.vertex_groups}
W = [{gname[g.group]: g.weight for g in v.groups} for v in me.vertices]


def wsum(w, keys):
    return sum(x for n, x in w.items() if any(kk in n for kk in keys))


ZMAP = [(-0.004, 0.0), (0.09, 0.08), (0.43, 0.42), (0.52, 0.49), (0.80, 0.86), (1.03, 1.08), (1.22, 1.27), (1.30, 1.40),
        (1.365, 1.455), (1.424, 1.475), (1.4855, 1.505), (1.506, 1.53), (1.554, 1.585), (1.668, 1.66), (1.73, 1.70)]
SXY = [(0.80, 1.076, 0.957), (0.90, 1.076, 0.957), (1.03, 1.055, 0.918), (1.22, 1.0, 0.854), (1.28, 1.08, 0.90),
       (1.33, 1.10, 1.0), (1.38, 1.15, 1.0)]
# new arm line (left): shoulder joint, 52 deg upper arm, 46 deg forearm (small bend at the elbow)
SHN = Vector((0.19, 0, 1.40))
A1, A2 = 52.0, 46.0
SMAP = [(-0.1, -0.1), (0.0, 0.0), (0.23, 0.29), (0.44, 0.54), (0.59, 0.72), (0.70, 0.85)]
RS = [(0.0, 0.85), (0.24, 0.92), (0.29, 0.92), (0.31, 0.88), (0.54, 1.10)]


def arm_pt(s2):
    """point and direction angle on the new left arm line at s2 metres from the shoulder"""
    u1 = Vector((math.cos(rad(A1)), 0, -math.sin(rad(A1))))
    u2 = Vector((math.cos(rad(A2)), 0, -math.sin(rad(A2))))
    base = SHN + u1 * s2 if s2 <= 0.29 else SHN + u1 * 0.29 + u2 * (s2 - 0.29)
    ang = interp([(0.25, A1), (0.33, A2)], s2)
    return base, ang


def f_body(c):
    sx, sy = interp(SXY, c.z)
    return Vector((c.x * sx, c.y * sy, interp(ZMAP, c.z)))


def f_arm(c, sgn):
    p = Vector((c.x * sgn, c.y, c.z))
    d = p - SH
    s, n = d.dot(AD), d.dot(AN)
    s2 = interp(SMAP, s)
    base, ang = arm_pt(s2)
    N = Vector((math.sin(rad(ang)), 0, math.cos(rad(ang))))
    rs = interp(RS, s2)
    q = base + N * (n * rs) + Vector((0, p.y * rs, 0))
    return Vector((q.x * sgn, q.y, q.z))


CXO = [(0.06, 0.166), (0.16, 0.160), (0.30, 0.148), (0.40, 0.140), (0.44, 0.135), (0.52, 0.125), (0.62, 0.112), (0.74, 0.097), (0.86, 0.086)]
LRS = [(0.0, 0.90), (0.09, 0.83), (0.43, 0.80), (0.52, 0.82), (0.62, 0.76), (0.86, 0.85)]


def f_leg(c, sgn, foot):
    x, y = c.x * sgn, c.y
    if foot:   # undo the 8 deg toe-out, fit heel/toe to +0.08 / -0.19
        a = rad(8)
        dx, dy = x - 0.166, y
        x, y = 0.166 + dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
        y = -0.19 + (y + 0.22) * (0.27 / 0.294)
    z2 = interp(ZMAP, c.z)
    cxn = 0.085 + 0.045 * (1 - min(z2, 0.90) / 0.90)
    r = interp(LRS, c.z)
    return Vector(((cxn + (x - interp(CXO, c.z)) * r) * sgn, y * (1.0 if foot else r), z2))


tags = [0] * len(me.vertices)
cnt = {}
for isl in islands(P):
    vs, mt = isl["v"], isl["mat"]
    ws = [W[i] for i in vs]
    n = len(vs)
    aL = sum(wsum(w, ("LeftUpperArm", "LeftLowerArm", "LeftHand")) for w in ws) / n
    aR = sum(wsum(w, ("RightUpperArm", "RightLowerArm", "RightHand")) for w in ws) / n
    lL = sum(wsum(w, ("LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "LeftToes")) for w in ws) / n
    lR = sum(wsum(w, ("RightUpperLeg", "RightLowerLeg", "RightFoot", "RightToes")) for w in ws) / n
    ring = isl["lo"].x < -0.08 and isl["hi"].x > 0.08 and isl["lo"].y < -0.04 and isl["hi"].y > 0.04
    foot = all(wsum(w, ("UpperLeg", "LowerLeg")) < 0.001 for w in ws)
    tag = 0
    if mt in ("mantello", "mantello_interno"):
        kind, tag = "cape", 5
        f = lambda c: Vector((c.x, c.y, interp(ZMAP, c.z)))
    elif all(w.get("Head", 0) > 0.999 for w in ws):
        kind, tag = "head", 4
        f = lambda c: Vector((c.x * 0.806, -0.012 + (c.y + 0.012) * 0.985, interp(ZMAP, c.z)))
    elif aL > 0.5 or aR > 0.5:
        kind = "arm"
        sg = 1 if aL > 0.5 else -1
        tag = 3 if mt in ("ottone", "vetro") else 0
        f = lambda c, sg=sg: f_arm(c, sg)
    elif lL > 0.5 or lR > 0.5:
        kind = "leg"
        sg = 1 if lL > 0.5 else -1
        f = lambda c, sg=sg, foot=foot: f_leg(c, sg, foot)
    elif all(w.get("Chest", 0) > 0.999 for w in ws) and isl["c"].y > 0.12:
        kind, tag = "elmo", 1
        f = lambda c: c + Vector((0, 0.018, -0.025))
    elif all(w.get("Hips", 0) > 0.999 for w in ws) and mt != "tunica" and not ring:
        kind, tag = "fianchi", 2
        f = lambda c: c + Vector((0, 0, 0.053))
    else:
        kind = "body"
        f = f_body
    for i in vs:
        me.vertices[i].co = f(me.vertices[i].co.copy())
        tags[i] = tag
    cnt[kind] = cnt.get(kind, 0) + 1
log("islands by kind:", cnt)
me.update()

# split the single mesh into working parts (same geometry, only regrouped)
NAMES = {0: "Corpo", 1: "Elmo", 2: "Fianchi", 3: "Bracciale", 4: "Testa", 5: "Mantello"}
for t, nm in NAMES.items():
    o = P.copy()
    o.data = P.data.copy()
    o.name = o.data.name = nm
    scn.collection.objects.link(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    dele = [v for v in bm.verts if tags[v.index] != t or not v.link_faces]
    bmesh.ops.delete(bm, geom=dele, context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    o["bind"] = t
    lo, hi = bbox(o)
    log("%s: %d verts, %d tris, z %.3f..%.3f, x %.3f..%.3f, y %.3f..%.3f" % (
        nm, len(o.data.vertices), sum(len(p.vertices) - 2 for p in o.data.polygons), lo.z, hi.z, lo.x, hi.x, lo.y, hi.y))
bpy.data.objects.remove(P, do_unlink=True)
salva()
render_viste("rev_1")
