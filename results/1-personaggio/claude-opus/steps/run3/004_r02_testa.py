# GROUP 2 - head, face and hair: re-shape the existing face parts and hair locks, add thick clumps
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
random.seed(202)

# ---- colours ----
set_mat("pelle", (0.85, 0.68, 0.58), 0.5)
set_mat("capelli", (0.10, 0.08, 0.07), 0.75)
set_mat("ciocca", (0.80, 0.80, 0.78), 0.7)
set_mat("occhi", (0.16, 0.09, 0.05), 0.3)
set_mat("labbra", (0.66, 0.42, 0.38), 0.5)
set_mat("bianco_occhi", (0.80, 0.77, 0.73), 0.4)

# ---- face parts ----
parts = split_loose(obj("Testa"))
info = []
for o in parts:
    info.append((o, matname(o), len(o.data.vertices), centroid(o)))
brows = sorted([t for t in info if t[1] == "capelli" and t[2] == 8], key=lambda t: -t[3].z)
nb = len(brows) // 2
brow_set, lid_set = brows[:nb], brows[nb:]


def move(o, d, s=1.0, c=None):
    c = centroid(o) if c is None else c
    for v in o.data.vertices:
        v.co = c + (v.co - c) * s + d


for o, m, n, c in info:
    sx = 1 if c.x > 0 else -1
    if m in ("bianco_occhi", "occhi"):          # eyes 0.065 apart, 0.03 wide, set into the face
        tgt = V((0.0325 * sx, c.y + 0.004, 1.585))
        move(o, tgt - c, 1.2 if m == "bianco_occhi" else 1.15)
    elif (o, m, n, c) in lid_set:
        move(o, V((0.0325 * sx - c.x, 0.004, (1.585 + 0.0085) - c.z)), 1.1)
    elif (o, m, n, c) in brow_set:            # 0.012 above the eyes, inner end lower
        move(o, V((0.034 * sx - c.x, 0.002, (1.585 + 0.013) - c.z)), 1.0)
        for v in o.data.vertices:
            v.co.z += (abs(v.co.x) - 0.034) * 0.30
            v.co.y -= 0.0
    elif m == "labbra":                        # closed straight mouth at 1.505
        upper = c.z > 1.515
        tz = 1.5085 if upper else 1.5015
        for v in o.data.vertices:
            v.co.z = c.z + (v.co.z - c.z) * 0.7
        move(o, V((0, 0.002, tz - c.z)), 1.0)
    elif m == "pelle" and n == 42:             # nose 1.58 -> 1.53
        a, b = bbox(o)
        for v in o.data.vertices:
            v.co.z = 1.53 + (v.co.z - a.z) * (0.05 / max(1e-4, b.z - a.z))
            v.co.y -= 0.002
    elif m == "pelle" and n == 52 and abs(c.x) < 0.02 and 1.53 < c.z < 1.56:  # nostrils
        move(o, V((0, -0.002, 1.538 - c.z)), 1.0)
    elif m == "pelle" and n == 52 and abs(c.x) > 0.05:  # ears 1.55-1.59
        move(o, V((0, 0, 1.57 - c.z)), 1.0)
head = join(parts, "Testa")
a, b = bbox(head)
log("testa dopo: x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (a.x, b.x, a.y, b.y, a.z, b.z))

# ---- hair: thicker locks, fewer hidden ones, fuller top ----
locks = split_loose(obj("Capelli"))
kept, removed = [], 0
for o in locks:
    m = matname(o)
    n = len(o.data.vertices)
    c = centroid(o)
    if m == "capelli" and (c.z > 1.60 or c.y > 0.03) and random.random() < 0.45:
        kill(o)
        removed += 1
        continue
    if n == 31:
        vs = o.data.vertices
        for j in range(5):
            idx = range(j * 6, j * 6 + 6)
            rc = sum((vs[i].co for i in idx), V()) / 6
            for i in idx:
                vs[i].co = rc + (vs[i].co - rc) * 1.55
    kept.append(o)
log("ciocche tolte:", removed, "tenute:", len(kept))
hair = join(kept, "Capelli")
HC = V((0.0, 0.008, 1.565))
for v in hair.data.vertices:
    p = v.co
    # lift the top so the hair stands 0.04 above the skull
    t = max(0.0, min(1.0, (p.z - 1.59) / 0.08))
    p.z += 0.016 * t * t * (3 - 2 * t)
    # keep the width close to 0.19-0.20
    if abs(p.x) > 0.092:
        p.x = math.copysign(0.092 + (abs(p.x) - 0.092) * 0.45, p.x)
    # back of the hair ends at the nape (1.48), sides at the jaw (1.50)
    if p.z < 1.50 and p.y < 0.03:
        p.z = 1.50 + (p.z - 1.50) * 0.3
    if p.z < 1.48:
        p.z = 1.48 + (p.z - 1.48) * 0.3


# new clumps on the head surface (ellipsoid around the skull)
def surf(a, e, off=0.0):
    ry = 0.090 if math.cos(a) > 0 else 0.103
    return HC + V((math.sin(a) * (0.079 + off) * math.cos(e), -math.cos(a) * (ry + off) * math.cos(e),
                   (0.097 + off) * math.sin(e)))


def clump(name, p, nrm, flow, L, w, th, mat, lift=0.012):
    side = nrm.cross(flow).normalized()
    rings = []
    for j in range(5):
        t = j / 4
        wave = math.sin(t * math.pi * 1.4 + random.uniform(0, 0.6)) * 0.008
        q = p + flow * L * t + nrm * (lift * math.sin(t * math.pi * 0.9)) + side * wave
        ww = w * (1.0 - 0.88 * t ** 1.3)
        tt = th * (1.0 - 0.65 * t)
        rings.append((q, ww, tt, tt))
    return loft(name, rings, seg=6, mat=mat, bones=["Head"], cap=(True, True), up=nrm)


new = []
specs = []
for i in range(14):    # crown and top: full, standing up, flowing back and out
    a = random.uniform(-math.pi, math.pi)
    e = random.uniform(0.75, 1.35)
    specs.append((a, e, "top"))
for i in range(10):    # sides over the ears, down to the jaw
    a = random.choice([-1, 1]) * random.uniform(1.15, 2.1)
    e = random.uniform(-0.05, 0.55)
    specs.append((a, e, "side"))
for i in range(8):     # back, down to the nape
    a = math.pi + random.uniform(-0.9, 0.9)
    e = random.uniform(-0.1, 0.5)
    specs.append((a, e, "back"))
for i in range(7):     # front locks falling on the forehead
    a = random.uniform(-0.75, 0.85)
    e = random.uniform(0.55, 0.85)
    specs.append((a, e, "front"))
for i, (a, e, kind) in enumerate(specs):
    p = surf(a, e, 0.006)
    nrm = (p - HC).normalized()
    down = V((0, 0, -1)) - nrm * nrm.dot(V((0, 0, -1)))
    if down.length < 0.3:
        down = V((math.sin(a) * 0.6, 1.0, 0)) - nrm * nrm.dot(V((math.sin(a) * 0.6, 1.0, 0)))
    down.normalize()
    if kind == "top":
        flow = (down * 0.8 + nrm * 0.35 + V((random.uniform(-0.3, 0.3), 0, 0))).normalized()
        L, lift = random.uniform(0.07, 0.11), 0.02
    elif kind == "front":
        flow = (down + V((0.25, -0.2, 0)) + nrm * 0.15).normalized()
        L, lift = random.uniform(0.06, 0.08), 0.008
    else:
        flow = (down + nrm * 0.25).normalized()
        L, lift = random.uniform(0.08, 0.12), 0.01
    w = random.uniform(0.035, 0.05)
    th = random.uniform(0.010, 0.017)
    new.append(clump("_c%02d" % i, p, nrm, flow, L, w, th, "capelli", lift))
# white streak: from the parting at X -0.03 back and to her right over the top
for i, (x0, y0) in enumerate([(-0.03, -0.075), (-0.034, -0.045), (-0.038, -0.01), (-0.045, 0.03), (-0.05, 0.065)]):
    p = V((x0, y0, 0.0))
    # put it on the hair surface
    a = math.atan2(x0, -y0)
    e = math.acos(min(1.0, math.hypot(x0 / 0.085, y0 / 0.1)))
    p = surf(a, e, 0.016)
    nrm = (p - HC).normalized()
    flow = V((-0.35, 1.0, -0.25)).normalized()
    flow = (flow - nrm * nrm.dot(flow)).normalized()
    new.append(clump("_w%02d" % i, p, nrm, flow, 0.075, 0.03, 0.009, "ciocca", 0.006))
for o in new:
    o.vertex_groups.clear()
hair = join([hair] + new, "Capelli")
bind(hair, ["Head"], rigid=True) if False else None
# new clumps need the Head weight + armature like the rest of the hair
g = hair.vertex_groups.get("Head") or hair.vertex_groups.new(name="Head")
g.add([v.index for v in hair.data.vertices], 1.0, "REPLACE")
if not hair.modifiers.get("Armature"):
    md = hair.modifiers.new("Armature", "ARMATURE")
    md.object = bpy.data.objects["Scheletro"]
hair.parent = bpy.data.objects["Scheletro"]
a, b = bbox(hair)
log("capelli: x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f], ciuffi nuovi %d" % (a.x, b.x, a.y, b.y, a.z, b.z, len(new)))
finish(2)
render_parte("rev_2_testa", ["Testa", "Capelli", "Collo"], ["fronte", "retro", "tre_quarti", "destra"])
