# GROUP 1 - body proportions and pose. The round-1 mesh is re-shaped (not rebuilt):
# every vertex is moved with its own bone weights: rigid moves for arms/legs/head, a torso field for the body.
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
body = bpy.data.objects["Esploratrice"]
OB = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
k = OB["Head"][1].z / 1.70  # round-1 global scale
log("scala giro 1: %.4f" % k)

# ---- old torso table (round 1 lib TORSO scaled by k) and its height landmarks ----
OLDT = [(t[0] * k, t[1] * k, t[2] * k, t[3] * k, t[4] * k) for t in TORSO]
ZMAP = [(0.80 * k, 0.79), (0.92 * k, 0.90), (1.03 * k, 1.075), (1.22 * k, 1.27), (1.395 * k, 1.40),
        (1.46 * k, 1.45), (1.62, 1.64)]


def F(p):  # torso field old -> new
    z1 = pwl(ZMAP, p.z)
    _, rx0, rf0, rb0, yo0 = tab(OLDT, p.z)
    _, rx1, rf1, rb1, yo1 = tab(NEWT, z1)
    dy = p.y - yo0
    return V((p.x * rx1 / rx0, yo1 + dy * ((rb1 / rb0) if dy > 0 else (rf1 / rf0)), z1))


HZ = [(1.30, 1.325), (1.478 * k, 1.475), (1.603 * k, 1.585), (1.697 * k, 1.66), (1.80, 1.773)]


def Hh(p):  # head: chin 1.475, eyes 1.585, skull top 1.66, depth 0.19
    return V((p.x * 1.02, -0.03 + (p.y + 0.03) * 1.18, pwl(HZ, p.z)))


def Nk(p):  # neck: 0.11 wide, up to the new head
    return V((p.x * 1.12, 0.005 + (p.y - 0.005) * 1.12, p.z + 0.024))


def rigid(h0, t0, h1, t1, roll=0.0):
    q = (t0 - h0).rotation_difference(t1 - h1)
    R = q.to_matrix()
    if roll:
        R = Matrix.Rotation(roll, 3, (t1 - h1).normalized()) @ R
    return lambda p: h1 + R @ (p - h0)


T = {}
for b in ("Hips", "Spine", "Chest", "Shoulder.L", "Shoulder.R"):
    T[b] = F
T["Neck"] = Nk
T["Head"] = Hh
for s, sx in ((".L", 1), (".R", -1)):
    m = lambda v: V((v.x * sx, v.y, v.z))
    T["UpperArm" + s] = rigid(OB["UpperArm" + s][0], OB["UpperArm" + s][1], m(SH1), m(ELB1))
    T["LowerArm" + s] = rigid(OB["LowerArm" + s][0], OB["LowerArm" + s][1], m(ELB1), m(WRI1))
    T["Hand" + s] = rigid(OB["Hand" + s][0], OB["Hand" + s][1], m(WRI1), m(TIP1), roll=math.radians(-22 * sx))
    T["UpperLeg" + s] = rigid(OB["UpperLeg" + s][0], OB["UpperLeg" + s][1], m(HIP1), m(KNEE1))
    T["LowerLeg" + s] = rigid(OB["LowerLeg" + s][0], OB["LowerLeg" + s][1], m(KNEE1), m(ANK1))
    dA = m(ANK1) - OB["Foot" + s][0]
    T["Foot" + s] = (lambda d: (lambda p: p + d))(dA)
    T["Toes" + s] = T["Foot" + s]

# ---- 1) split the joined round-1 mesh into its loose parts and label them (old coordinates) ----
parts = split_loose(body)
log("parti:", len(parts))


def armline(ax):
    return 1.395 * k - (ax - 0.165 * k) * math.tan(math.radians(42))


def classify(o):
    m = matname(o)
    n = len(o.data.vertices)
    c = centroid(o) / k
    ax = abs(c.x)
    sd = ".L" if c.x > 0 else ".R"
    if m.startswith("mantello"):
        return "Mantello"
    if c.y > 0.17 and c.z > 0.85:
        if m == "lino" or (m == "cuoio" and abs(c.z - 1.0) < 0.08 and ax < 0.2):
            return "Rotolo"
        if m == "cuoio_scuro":
            return "Tubi"
        if m == "corda":
            return "Elmo_corda"
        return "Elmo"
    if c.z > 1.47 and ax < 0.13:
        if m == "pelle" and n == 44:
            return "Collo"
        if m in ("capelli", "ciocca") and n > 8:
            return "Capelli"
        return "Testa"
    if m == "lino" and c.z > 1.30 and c.x > 0.05 and c.y < -0.05:
        return "Conchiglie"
    if m == "cuoio" and n == 8 and c.z > 1.30 and 0.08 < c.x < 0.2 and c.y < -0.09:
        return "Conchiglie"
    if m == "ottone" and ax < 0.02 and c.z > 1.40 and c.y < -0.05:
        return "Fermaglio"
    if ax > 0.17 and abs(c.z * k - armline(ax * k)) / k < 0.13:
        if m == "lino":
            return "Braccio" + sd
        if m == "cuoio_scuro" and ax > 0.40:
            return "Mano" + sd
        if m in ("ottone", "verde_gemma", "ottone_scuro") and c.x > 0:
            return "Quadrante"
        return "Guanto" + sd
    if m == "pantaloni":
        return "Pantaloni"
    if c.z < 0.58:
        if m == "cuoio_scuro" and 0.42 < c.z < 0.58 and n > 8:
            return "Ginocchiere"
        if m == "cuoio" and 0.42 < c.z < 0.58:
            return "Ginocchiere"
        if m == "corda" and n == 8:
            return "Lacci" + sd
        if m == "lino":
            return "Stracci"
        if ax < 0.25:
            return "Stivale" + sd
    if m == "camicia":
        return "Tunica"
    if m == "gilet":
        return "Busto"
    if m == "corda":
        return "Corda"
    if m == "lino":
        return "Stracci"
    if c.x < -0.17 and c.y < -0.02 and 0.80 < c.z < 1.05:
        return "Barattolo"
    if c.x > 0.18 and c.z < 1.06:
        return "Astuccio"
    if n == 8 and m in ("cuoio", "cuoio_scuro") and c.y < -0.05 and 0.9 < c.z < 1.03:
        return "Borse"
    if m == "ottone" and n == 62 and ax < 0.02:
        return "Medaglione"
    if m == "ottone" and n == 26:
        return "Bottoni"
    if n == 58 and m == "cuoio_scuro":
        return "Cinturone"
    if m == "ottone" and n == 8 and 0.88 < c.z < 0.97:
        return "Cinturone"
    if n == 58 and m == "cuoio":
        return "Cintura"
    if n == 8 and ax < 0.03 and 0.97 < c.z < 1.05:
        return "Cintura"
    if m == "cuoio_scuro" and n == 32:
        return "Bavero"
    if m in ("cuoio", "ottone"):
        return "Cinghie"
    return "Varie"


labels = {}
for o in parts:
    labels[o.name] = classify(o)

# ---- 2) move every vertex with its weights ----
for o in parts:
    me = o.data
    gname = {g.index: g.name for g in o.vertex_groups}
    wl = [[(gname[g.group], g.weight) for g in v.groups if g.weight > 0 and gname[g.group] in T] for v in me.vertices]
    uniform = all(sorted(w) == sorted(wl[0]) for w in wl) if wl else True
    c = centroid(o)
    new = []
    for v, ws in zip(me.vertices, wl):
        tot = sum(w for _, w in ws)
        if tot <= 0:
            new.append(F(v.co))
            continue
        acc = V()
        for b, w in ws:
            if uniform and T[b] is F:
                acc += (v.co + (F(c) - c)) * w
            else:
                acc += T[b](v.co) * w
        new.append(acc / tot)
    for v, p in zip(me.vertices, new):
        v.co = p
    me.update()

# ---- 3) join the parts by label ----
groups = {}
for o in parts:
    groups.setdefault(labels[o.name], []).append(o)
made = []
for lab, objs in sorted(groups.items()):
    j = join(objs, lab)
    made.append("%s(%d)" % (lab, len(objs)))
log("oggetti:", ", ".join(made))

# ---- 4) skeleton to the new joints ----
bpy.context.view_layer.objects.active = rig
for o in bpy.context.selected_objects:
    o.select_set(False)
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = rig.data.edit_bones
NEWB = {"Hips": ((0, 0, 0.95), (0, 0, 1.10)), "Spine": ((0, 0, 1.10), (0, 0, 1.27)),
        "Chest": ((0, 0, 1.27), (0, 0, 1.45)), "Neck": ((0, 0, 1.45), (0, -0.005, 1.50)),
        "Head": ((0, -0.005, 1.50), (0, -0.005, 1.70))}
for s, sx in ((".L", 1), (".R", -1)):
    m = lambda v: tuple(V((v[0] * sx, v[1], v[2])))
    NEWB["Shoulder" + s] = (m((0.02, 0.0, 1.44)), m(SH1))
    NEWB["UpperArm" + s] = (m(SH1), m(ELB1))
    NEWB["LowerArm" + s] = (m(ELB1), m(WRI1))
    NEWB["Hand" + s] = (m(WRI1), m(KNU1))
    NEWB["UpperLeg" + s] = (m(HIP1), m(KNEE1))
    NEWB["LowerLeg" + s] = (m(KNEE1), m(ANK1))
    NEWB["Foot" + s] = (m(ANK1), m(BALL1))
    NEWB["Toes" + s] = (m(BALL1), m(TOE1))
for b in eb:
    b.use_connect = False
for name, (h, t) in NEWB.items():
    eb[name].head = h
    eb[name].tail = t
for name in NEWB:
    b = eb[name]
    if b.parent and (b.parent.tail - b.head).length < 1e-4:
        b.use_connect = True
bpy.ops.armature.select_all(action="SELECT")
bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Y")
bpy.ops.object.mode_set(mode="OBJECT")
for b in rig.data.bones:
    log("osso %-11s testa (%.3f, %.3f, %.3f) coda (%.3f, %.3f, %.3f)" % ((b.name,) + tuple(b.head_local) + tuple(b.tail_local)))

# ---- 5) measurements ----
def zr(name):
    o = obj(name)
    a, b = bbox(o)
    return "%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (name, a.x, b.x, a.y, b.y, a.z, b.z)


for nm in ("Testa", "Capelli", "Collo", "Busto", "Braccio.L", "Mano.L", "Pantaloni", "Stivale.L", "Mantello", "Elmo"):
    if obj(nm):
        log(zr(nm))
finish(1)
