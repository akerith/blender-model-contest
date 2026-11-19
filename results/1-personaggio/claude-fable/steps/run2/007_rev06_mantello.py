exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 6 - the cape. The round-1 cape mesh is kept: its long back part gets extra loops and becomes the wide bell,
# its two short front flaps are cut loose and re-shaped into the shoulder cape. Everything is moved through the UVs.
random.seed(66)
# small fix of group 5: hands a little longer (wrist to fingertip 0.18)
Hn = bpy.data.objects["mani"]
move(Hn, range(len(Hn.data.vertices)), lambda p: Vector((1 if p.x > 0 else -1, 1, 1)) * 1.0 and (
    Vector((math.copysign(1, p.x) * (WRN.x + (abs(p.x) - WRN.x) * 1.08), p.y * 1.08, WRN.z + (p.z - WRN.z) * 1.08))))

Mn = bpy.data.objects["Mantello"]
me = Mn.data
coll = set(i for isl in islands(Mn) if len(isl["v"]) <= 200 for i in isl["v"])
inner_mi = [k for k, m in enumerate(me.materials) if m.name == "mantello_interno"][0]
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
cv = set(bm.verts[i] for i in coll)


def U(v):
    return v.link_loops[0][uvl].uv


# 1. cut the side flaps loose from the long part
cut = []
for f in bm.faces:
    if f.verts[0] in cv:
        continue
    us = [l[uvl].uv.x for l in f.loops]
    if (min(us) < 0.249 < max(us)) or (min(us) < 0.751 < max(us)):
        cut.append(f)
bmesh.ops.delete(bm, geom=cut, context="FACES")
# 2. extra loops in the long part: twice the columns
es = [e for e in bm.edges if e.verts[0] not in cv and e.verts[1] not in cv and e.verts[0].link_loops and e.verts[1].link_loops
      and abs(U(e.verts[0]).x - U(e.verts[1]).x) > 1e-4 and 0.2499 < U(e.verts[0]).x < 0.7501 and 0.2499 < U(e.verts[1]).x < 0.7501]
bmesh.ops.subdivide_edges(bm, edges=es, cuts=1, use_grid_fill=True)
log("cape: faces cut", len(cut), "edges split", len(es))

WT = [(0.0, 0.57), (0.2, 0.55), (0.5, 0.50), (0.86, 0.42), (1.0, 0.37), (1.17, 0.30), (1.30, 0.24), (1.385, 0.205)]
YB = [(0.2, 0.23), (0.5, 0.21), (0.86, 0.185), (0.95, 0.165), (1.10, 0.13), (1.27, 0.115), (1.40, 0.108)]
YC = [(0.2, 0.08), (0.86, 0.09), (1.2, 0.07), (1.40, 0.03)]
DF = [(0.2, 0.13), (0.86, 0.11), (1.2, 0.07), (1.40, 0.05)]
XT = [(0.2, 0.24), (0.86, 0.22), (1.2, 0.20), (1.40, 0.17)]
PHI = 150.0


def Cpt(phi, z):
    a, sg = abs(phi), (1 if phi >= 0 else -1)
    W, yb, yc = interp(WT, z), interp(YB, z), interp(YC, z)
    if a <= 90:
        x, y = W * math.sin(rad(a)), yc + (yb - yc) * math.cos(rad(a))
    else:
        tau = (a - 90) / 60
        x, y = W - (W - interp(XT, z)) * tau ** 1.3, yc - interp(DF, z) * math.sin(rad(tau * 90))
    return Vector((sg * x, y, z))


# torn hem: irregular triangular rags over the 73 columns of the long part
RAG = [0.0] * 73
i, nr = 0, 0
while i < 73:
    w = random.choice((2, 2, 3, 3, 4, 5))
    d = random.uniform(0.05, 0.18)
    for k in range(w + 1):
        if i + k < 73:
            RAG[i + k] = max(RAG[i + k] if k == 0 else 0, d * abs(k - w / 2) / (w / 2))
    i += w
    nr += 1
log("hem rags:", nr)
EXT = {k: random.uniform(-0.03, 0.05) for k in range(-1, 75)}
ED = [(-70, 0.105, -0.105, 1.335), (-45, 0.30, -0.085, 1.235), (-15, 0.395, -0.03, 1.245), (15, 0.395, 0.04, 1.245),
      (45, 0.31, 0.105, 1.22), (70, 0.17, 0.142, 1.205), (90, 0.0, 0.145, 1.20)]


def long_pt(u, t, inner):
    key = int(round((u - 0.25) * 144))
    phi = (4 * u - 2) * PHI
    zend = 0.20 + 0.05 * (abs(phi) / PHI) ** 2 - 0.03 + RAG[max(0, min(72, key))]
    t0 = 0.07
    if t < t0:
        s = t / t0
        s = s * s * (3 - 2 * s)
        nk = Vector((0.088 * math.sin(rad(phi)), 0.008 + 0.088 * math.cos(rad(phi)), 1.415))
        p = nk.lerp(Cpt(phi, 1.385), s)
        amp = 0.0
    else:
        q = (t - t0) / (1 - t0)
        p = Cpt(phi, 1.385 - (1.385 - zend) * q)
        amp = 0.022 * min(1.0, q / 0.45) ** 1.3
    n = Vector((p.x, (p.y - 0.06) * 1.5, 0))
    n.normalize()
    pr = rad(phi)
    p = p + n * (amp * math.sin(12 * pr + 1.2 * math.sin(3.1 * pr + 1.0)) - (0.008 if inner else 0.0))
    return p, key


def sh_pt(w, t, key, inner):
    al = 90 - 160 * w
    ex, ey, ez = interp(ED, al)
    e = Vector((ex, ey, ez))
    nk = Vector((0.095 * math.cos(rad(al)), 0.005 + 0.09 * math.sin(rad(al)), 1.425))
    sp = Vector((0.235 * math.cos(rad(al)), 0.005 + 0.125 * math.sin(rad(al)), 1.455 - 0.03 * abs(math.sin(rad(al)))))
    c = sp * 2 - (nk + e) * 0.5
    p = nk * (1 - t) ** 2 + c * (2 * t * (1 - t)) + e * (t * t)
    if t > 0.6:
        p += (e - sp).normalized() * (EXT[key] * (t - 0.6) / 0.4)
    if inner:
        p += Vector((-p.x * 0.02, -(p.y - 0.01) * 0.03, -0.006))
    return p


# 3. column ends (from the vertices that still exist), then move everything
vend, info = {}, {}
for v in bm.verts:
    if v in cv or not v.link_loops:
        continue
    uv = U(v)
    inner = v.link_faces[0].material_index == inner_mi
    ck = (inner, int(round(uv.x * 144)))
    vend[ck] = max(vend.get(ck, 0.0), 1 - uv.y)
    info[v] = (uv.x, 1 - uv.y, inner, ck)
for v, (u, vv, inner, ck) in info.items():
    t = min(1.0, vv / max(vend[ck], 1e-6))
    if 0.2499 < u < 0.7501:
        p, key = long_pt(u, t, inner)
        newv = 1 - 0.98 * t
        info[v] = (key, t, True)
    else:
        w = (u - 0.75) / 0.25 if u > 0.5 else (0.25 - u) / 0.25
        p = sh_pt(w, t, ck[1] // 2, inner)
        if u < 0.5:
            p.x = -p.x
        newv = 1 - 0.30 * t
        info[v] = (0, t, False)
    v.co = p
    for l in v.link_loops:
        l[uvl].uv.y = newv
# 4. holes just above the edge
holes = []
for f in bm.faces:
    if any(v not in info for v in f.verts):
        continue
    ii = [info[v] for v in f.verts]
    if all(x[2] for x in ii) and all(0.78 < x[1] < 0.93 for x in ii) and min(x[0] for x in ii) in (9, 10, 25, 40, 41, 56, 66):
        holes.append(f)
bmesh.ops.delete(bm, geom=holes, context="FACES")
log("hole faces removed:", len(holes))
bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f.material_index != inner_mi and f.verts[0] not in cv])
bm.to_mesh(me)
bm.free()
me.update()
lo, hi = bbox(Mn)
log("cape box", [round(x, 3) for x in lo], [round(x, 3) for x in hi], "tris", sum(len(p.vertices) - 2 for p in me.polygons))
# 6.7 shells: on the cape at the front of her left collarbone
C = "Corpo"
idx = pick(C, "bianco")
if idx:
    lo, hi = bbox(C, idx)
    c = (lo + hi) / 2
    move(C, idx, lambda p: Vector((0.12, -0.112, 1.372)) + (p - c) * 0.9)
    log("shells moved from", [round(x, 3) for x in c])
salva()
render_viste("rev_6")
