exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 7 - waist gear: rope coil (twisted), canister, pouch, map tubes, cloth, small pouches
random.seed(7)
F = bpy.data.objects["Fianchi"]
Z = Vector((0, 0, 1))


def axis_map(idx, p0, a_old, q0, a_new, sa, sr):
    a_old, a_new = Vector(a_old).normalized(), Vector(a_new).normalized()
    R = a_old.rotation_difference(a_new).to_matrix()
    p0, q0 = Vector(p0), Vector(q0)

    def f(p):
        s = (p - p0).dot(a_old)
        return q0 + a_new * (s * sa) + (R @ ((p - p0) - a_old * s)) * sr
    return move(F, idx, f)


# ---- 7.1 rope coil on her right hip: 4 oval loops 0.16 x 0.10, from Z 0.98 down to 0.72, twisted cord ----
loops = sorted([i for i in islands(F) if i["mat"] == "corda" and i["c"].x < -0.06 and i["hi"].z - i["lo"].z > 0.15],
               key=lambda i: -i["c"].z)
small = [i for i in islands(F) if i["mat"] == "corda" and i["c"].x < -0.06 and i["hi"].z - i["lo"].z <= 0.15]
strands = []
vv = F.data.vertices
for k, isl in enumerate(loops[:4]):
    c = isl["c"]
    cs = [vv[i].co - c for i in isl["v"]]
    sxx = sum(p.x * p.x for p in cs)
    syy = sum(p.y * p.y for p in cs)
    sxy = sum(p.x * p.y for p in cs)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    Uh = Vector((math.cos(ang), math.sin(ang), 0))
    Nn = Uh.cross(Z)
    hu = max(abs(p.dot(Uh)) for p in cs)
    hz = max(abs(p.z) for p in cs)
    Ck = Vector((-0.185 + random.uniform(-0.01, 0.01), -0.062 - 0.007 * k, 0.90 - 0.035 * k))
    R_, Ry_ = 0.050 - 0.008, 0.080 - 0.008

    def f(p, c=c, Uh=Uh, Nn=Nn, hu=hu, hz=hz, Ck=Ck):
        d = p - c
        q = Vector((d.dot(Uh) * 0.050 / hu, d.dot(Nn), d.z * 0.080 / hz))      # in the loop frame
        tau = math.atan2(q.z / Ry_, q.x / R_)
        cen = Vector((R_ * math.cos(tau), 0, Ry_ * math.sin(tau)))
        q = cen + (q - cen) * 0.42                                              # the old tube becomes the thin core
        return Ck + Uh * q.x + Nn * q.y + Z * q.z
    move(F, isl["v"], f)
    N = 36
    for h in range(2):                 # two strands twisted around the core
        pts = []
        for j in range(N):
            tau = 2 * math.pi * j / N
            er = (Uh * (math.cos(tau) * Ry_) + Z * (math.sin(tau) * R_)).normalized()
            psi = 9 * tau + h * math.pi
            pts.append(Ck + Uh * (R_ * math.cos(tau)) + Z * (Ry_ * math.sin(tau)) + er * (0.0038 * math.cos(psi)) + Nn * (0.0038 * math.sin(psi)))
        vs, fs = [], []
        for j in range(N):
            t = (pts[(j + 1) % N] - pts[j - 1]).normalized()
            a_ = Nn.cross(t).normalized()
            b_ = t.cross(a_)
            for m in range(3):
                be = 2 * math.pi * m / 3
                vs.append(pts[j] + (a_ * math.cos(be) + b_ * math.sin(be)) * 0.0046)
        for j in range(N):
            j2 = (j + 1) % N
            for m in range(3):
                m2 = (m + 1) % 3
                fs.append((j * 3 + m, j2 * 3 + m, j2 * 3 + m2, j * 3 + m2))
        strands.append((vs, fs))
log("rope loops re-shaped:", len(loops[:4]), "small ring:", len(small))
for isl in small:
    c = isl["c"]
    move(F, isl["v"], lambda p, c=c: Vector((-0.178, -0.05, 0.972)) + (p - c))
o = new("corda_trefoli", strands, "corda", 2, sharp=80)
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")

# ---- 7.2 canister: lying almost horizontal, 0.20 long, 0.07 across ----
idx = pick(F, ("ottone", "vetro", "cuoio"), lo=(-0.33, -0.12, 0.72), hi=(-0.2, 0.0, 0.935))
c0, c1 = Vector((-0.235, -0.050, 0.898)), Vector((-0.265, -0.062, 0.768))
A, Bq = Vector((-0.145, -0.092, 0.915)), Vector((-0.335, -0.048, 0.885))
ao = (c1 - c0).normalized()
an = (Bq - A).normalized()
log("canister verts:", axis_map(idx, c0 + ao * 0.0515, ao, (A + Bq) / 2, an, 1.23, 0.93))
# ---- 7.3 round pouch above the canister: 0.09 x 0.06 x 0.08 at X -0.20, Z 0.99 ----
idx = pick(F, "cuoio", lo=(-0.24, -0.08, 0.9), hi=(-0.12, 0.04, 1.02))
if idx:
    affine(F, idx, (-0.235, -0.065, 0.95), (-0.175, 0.025, 1.03))
idx = pick(F, "ottone", lo=(-0.26, -0.06, 0.92), hi=(-0.2, 0.0, 0.97))
if idx:
    lo, hi = bbox(F, idx)
    move(F, idx, lambda p: p - (lo + hi) / 2 + Vector((-0.238, -0.02, 0.985)))
# ---- 7.4 map tube (0.45 x 0.075, Z 0.98 .. 0.53, X +0.22, Y -0.02) and the thinner tube beside it ----
T1 = (Vector((0.205, -0.065, 1.018)), Vector((0.245, -0.080, 0.613)))
T2 = (Vector((0.255, -0.005, 0.993)), Vector((0.290, -0.010, 0.643)))
g1, g2 = [], []
for isl in islands(F):
    if isl["mat"] not in ("cuoio", "ottone") or isl["c"].x < 0.15:
        continue
    ds = []
    for p0, p1 in (T1, T2):
        a_ = (p1 - p0).normalized()
        d = isl["c"] - p0
        ds.append((d - a_ * d.dot(a_)).length)
    if min(ds) < 0.07:
        (g1 if ds[0] <= ds[1] else g2).extend(isl["v"])
axis_map(g1, T1[0], T1[1] - T1[0], (0.22, -0.02, 0.98), (0, 0, -1), 0.45 / 0.407, 0.0375 / 0.031)
axis_map(g2, T2[0], T2[1] - T2[0], (0.287, 0.0, 0.955), (0, 0, -1), 0.35 / 0.352, 0.025 / 0.027)
log("tube verts:", len(g1), len(g2))
caps = [g_cyl((0.22, -0.02, 0.985), (0.22, -0.02, 0.94), 0.0395, n=12), g_cyl((0.22, -0.02, 0.57), (0.22, -0.02, 0.527), 0.0395, n=12),
        g_cyl((0.287, 0.0, 0.96), (0.287, 0.0, 0.93), 0.0268, n=10), g_cyl((0.287, 0.0, 0.635), (0.287, 0.0, 0.603), 0.0268, n=10),
        g_sphere((0.22, -0.02, 0.988), (0.03, 0.03, 0.012), seg=10, rings=4)]
new("tubi_tappi", caps, "ottone", 2, sharp=40)
new("tubi_cinghie", [g_torus((0.22, -0.02, z), (0, 0, 1), 0.0385, 0.005, nseg=12, nside=4) for z in (0.86, 0.66)], "cuoio_cinghie", 2)
# ---- 7.5 torn cream cloth between the map tube and the leg: 0.07 wide, Z 0.98 .. 0.62 ----
rags = sorted([i for i in islands(F) if i["mat"] == "lino"], key=lambda i: -(i["hi"].z - i["lo"].z))
for isl in rags:
    if isl["c"].x > 0 and isl is rags[0]:
        affine(F, isl["v"], (0.115, -0.105, 0.62), (0.185, -0.085, 0.985))
    else:
        move(F, isl["v"], lambda p: p + Vector((0, 0, -0.07)))
# ---- 7.6 three small leather pouches on the main belt (sides and back) ----
pch = []
for a in (0, 150, 32):
    p = vpt(NB, 1.082, a, 0.020)
    Rz = Matrix.Rotation(rad(a), 3, "Z")
    pch.append(g_sphere(p, (0.017, 0.031, 0.027), seg=8, rings=6, M=Rz))
    pch.append(g_box(p + Rz @ Vector((0.012, 0, 0.012)), (0.012, 0.062, 0.026), M=Rz))
new("borsette", pch, "cuoio", 2, sharp=40)
salva()
render_viste("rev_7", viste=["fronte", "destra", "sinistra"])
shot("rev_7_fianchi", (0, 0, 0.85), 0.8)
shot("rev_7_fianco_dx", (-0.1, 0, 0.85), 0.6, d=(-1, -0.8, 0.2))
