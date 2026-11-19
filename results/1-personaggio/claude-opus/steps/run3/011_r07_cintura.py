# GROUP 7 - waist gear: rope coil (twisted), canister, round pouch, map tube + thin tube, cream cloth, 3 pouches
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
random.seed(707)
set_mat("corda", (0.70, 0.62, 0.47), 0.95)
set_mat("stoffa_crema", (0.80, 0.74, 0.62), 0.9)
set_mat("cuoio_borsa", (0.33, 0.20, 0.11), 0.65)

# ---- 7.1 rope: 4 overlapping oval loops 0.10 x 0.16 hanging from the hip belt at X -0.17, down to Z 0.72 ----
parts = split_loose(obj("Corda"))
tori = sorted([o for o in parts if len(o.data.vertices) == 132], key=lambda o: centroid(o).z)
other = [o for o in parts if o not in tori]
loops = []
NRM = V((-0.45, -1.0, 0.0)).normalized()
for i, o in enumerate(tori[:4]):
    cz = 0.80 + 0.012 * (i - 1.5)
    cen = V((-0.185 + 0.012 * (i - 1.5), -0.085 - 0.006 * i, cz))
    rigid_to(o, cen, NRM, 1.0, which=2)
    # oval: 0.16 high (major axis vertical) x 0.10 wide, rope about 0.015 thick
    c, axes = pca(o)
    maj, mnr = axes[0], axes[1]
    hx = (NRM.cross(V((0, 0, 1)))).normalized()
    em = 2 * max(abs((v.co - c).dot(maj)) for v in o.data.vertices)
    en = 2 * max(abs((v.co - c).dot(mnr)) for v in o.data.vertices)
    for v in o.data.vertices:
        d = v.co - c
        v.co = c + V((0, 0, 1)) * d.dot(maj) * (0.16 / em) + hx * d.dot(mnr) * (0.10 / en) + NRM * d.dot(NRM) * 0.8
    o.data.update()
    loops.append(o)
# twisted cord: a second strand spiralling around each loop (2-strand rope)
strands = []
for o in loops:
    c, axes = pca(o)
    hx = (NRM.cross(V((0, 0, 1)))).normalized()
    pts = []
    N = 56
    for j in range(N + 1):
        t = 2 * math.pi * j / N
        core = c + hx * 0.05 * math.cos(t) + V((0, 0, 1)) * 0.08 * math.sin(t)
        tang = (-hx * 0.05 * math.sin(t) + V((0, 0, 1)) * 0.08 * math.cos(t)).normalized()
        side = tang.cross(NRM).normalized()
        ph = t * 14
        pts.append(core + (side * math.cos(ph) + NRM * math.sin(ph)) * 0.0058)
    strands.append(path_tube("_strand", pts, 0.0042, 5, "corda", cap=(False, False)))
for o in strands:
    o.vertex_groups.clear()
# tie: binding from the belt (Z 0.98) down to the top of the loops; 5th torus becomes the wrap of the tie
for o in other + tori[4:]:
    rigid_to(o, V((-0.175, -0.09, 0.90)), V((0, 0, 1)), 0.9, which=2) if len(o.data.vertices) == 132 else \
        remap_cyl(o, (-0.172, -0.085, 0.975), (-0.18, -0.09, 0.875), 0.011)
rope = join(loops + strands + other + tori[4:], "Corda")
use_mat(rope, "corda")
weight_all(rope, "Hips")

# ---- 7.2 canister on the right hip: 0.20 long, 0.07 across, almost horizontal, centre (-0.24, -0.03, 0.90) ----
parts = split_loose(obj("Barattolo"))
cax = V((-0.30, -1.0, -0.12)).normalized()
cc = V((-0.24, -0.03, 0.90))
A, B = cc - cax * 0.10, cc + cax * 0.10
body = max(parts, key=lambda o: len(o.data.vertices) if matname(o).startswith("ottone") and len(o.data.vertices) == 34 else 0)
bands = [o for o in parts if matname(o).startswith("cuoio")]
caps = [o for o in parts if o is not body and o not in bands]
remap_cyl(body, A + cax * 0.012, B - cax * 0.012, 0.035)
use_mat(body, "cuoio")
for o, t in zip(bands, (0.30, 0.70, 0.5)):
    p = A.lerp(B, t)
    remap_cyl(o, p - cax * 0.008, p + cax * 0.008, 0.038)
    use_mat(o, "ottone")
for o in caps:
    remap_cyl(o, A - cax * 0.004, A + cax * 0.016, 0.037)
    use_mat(o, "ottone")
cap2 = tube("_cap2", B - cax * 0.016, B + cax * 0.004, 0.037, None, 16, "ottone")
can = join(parts + [cap2], "Barattolo")
weight_all(can, "Hips")

# ---- 7.3 round leather pouch with a flap above the canister, centre (-0.20, -, 0.99) ----
pc = V((-0.205, -0.035, 0.995))
pouch = sphere("_pouch", pc, 1.0, 14, 8, scale=(0.03, 0.045, 0.04), mat="cuoio_borsa")
flap = sphere("_flap", pc + V((-0.006, -0.004, 0.018)), 1.0, 12, 6, scale=(0.031, 0.044, 0.022), mat="cuoio")
rp = join([pouch, flap], "Borsa_tonda")
weight_all(rp, "Hips")

# ---- 7.4 map tube on the left hip: 0.45 long, 0.075 across, Z 0.98 -> 0.53, centre X +0.22 Y -0.02 ----
parts = split_loose(obj("Astuccio"))
A, B = V((0.22, -0.02, 0.98)), V((0.22, -0.02, 0.53))
ax = (B - A).normalized()
body = max(parts, key=lambda o: len(o.data.vertices) if matname(o).startswith("cuoio") else -1)
rings = sorted([o for o in parts if o is not body and len(o.data.vertices) == 30], key=lambda o: -centroid(o).z)
rest = [o for o in parts if o is not body and o not in rings]
remap_cyl(body, A + ax * 0.03, B - ax * 0.03, 0.0375)
use_mat(body, "cuoio")
spots = [(0.0, 0.04, 0.0395, "ottone"), (1.0, 0.04, 0.0395, "ottone"), (0.25, 0.015, 0.0392, "cinghia_guanto"),
         (0.75, 0.015, 0.0392, "cinghia_guanto")]
for o, (t, h, r, m) in zip([rings[0], rings[-1]] + rings[1:-1], spots):
    p = A.lerp(B, t) + (ax * h / 2 if t == 0.0 else (-ax * h / 2 if t == 1.0 else V()))
    remap_cyl(o, p - ax * h / 2, p + ax * h / 2, r)
    use_mat(o, m)
for o in rest:   # old lid -> small knob on the top cap
    remap_cyl(o, A - ax * 0.012, A, 0.022)
    use_mat(o, "ottone")
# second, thinner tube beside it on the outside: 0.35 long, 0.05 across
A2, B2 = V((0.287, -0.012, 0.95)), V((0.287, -0.012, 0.60))
t2 = [tube("_t2", A2, B2, 0.025, None, 14, "cuoio"),
      tube("_t2a", A2 - V((0, 0, 0.002)), A2 - V((0, 0, 0.03)), 0.027, None, 14, "ottone"),
      tube("_t2b", B2 + V((0, 0, 0.03)), B2 - V((0, 0, 0.002)), 0.027, None, 14, "ottone")]
for o in t2:
    o.vertex_groups.clear()
mt = join(parts + t2, "Astuccio")
weight_all(mt, "Hips")

# ---- 7.5 torn cream cloth from the hip belt on her left, Z 0.98 -> 0.62, 0.07 wide ----
parts = split_loose(obj("Stracci"))
for o, (x, zb) in zip(parts, ((0.150, 0.62), (0.168, 0.665), (0.185, 0.64))):
    a, b = bbox(o)
    c = centroid(o)
    for v in o.data.vertices:
        t = (v.co.z - a.z) / max(1e-6, b.z - a.z)
        v.co = V((x + (v.co.x - c.x) * 0.8, -0.085 + (v.co.y - c.y), zb + t * (0.98 - zb)))
    o.data.update()
cl = join(parts, "Stracci")
use_mat(cl, "stoffa_crema")
bind(cl, ["Hips", "UpperLeg.L"])

# ---- 7.6 three small leather pouches on the belt, at the back and on the sides ----
parts = split_loose(obj("Borse"))
boxes = sorted(parts, key=lambda o: centroid(o).x)
pairs = []
used = set()
for o in boxes:
    if o.name in used:
        continue
    mate = min((p for p in boxes if p is not o and p.name not in used),
               key=lambda p: (centroid(p) - centroid(o)).length, default=None)
    used.add(o.name)
    if mate:
        used.add(mate.name)
    pairs.append((o, mate))
SL = 0.06 / 0.34
for (o, mate), (x, y) in zip(pairs, ((-0.168, 0.055), (0.168, 0.06), (0.10, 0.112))):
    zc = 0.97 + SL * x - 0.035
    out = V((x, y - 0.01, 0)).normalized()
    pos = V((x, y, zc)) + out * 0.012
    grp = [o] + ([mate] if mate else [])
    c0 = sum((centroid(p) for p in grp), V()) / len(grp)
    ang = math.atan2(out.x, -out.y)
    R = Matrix.Rotation(ang, 3, "Z")
    for p in grp:
        for v in p.data.vertices:
            d = v.co - c0
            d = V((d.x * 0.95, d.y * 0.75, d.z * 0.75))
            v.co = pos + R @ d
        p.data.update()
bs = join(parts, "Borse")
weight_all(bs, "Hips")

for nm in ("Corda", "Barattolo", "Borsa_tonda", "Astuccio", "Stracci", "Borse"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(7)
render_parte("rev_7_cintura", ["Corda", "Barattolo", "Borsa_tonda", "Astuccio", "Stracci", "Borse", "Cinturone",
                               "Tunica", "Pantaloni", "Cintura"], ["fronte", "sinistra", "destra", "tre_quarti"])
