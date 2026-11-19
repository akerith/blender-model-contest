# GROUP 4 - torso: jacket, tunic skirt, cross straps, chest strap, belts, medallion (re-shaped + new pieces)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
random.seed(404)
set_mat("gilet", (0.13, 0.16, 0.22), 0.85)
set_mat("cuoio", (0.36, 0.22, 0.12), 0.65)
set_mat("cuoio_cintura", (0.30, 0.18, 0.09), 0.65)
set_mat("cucitura", (0.05, 0.06, 0.08), 0.9)
set_mat("ottone", (0.62, 0.45, 0.20), 0.35, 1.0)
TOR = ["Hips", "Spine", "Chest"]

# ---- 4.2 tunic skirt: navy, 1.06 -> 0.80, 0.38 wide at the hem, open on the sides ----
tu = obj("Tunica")
use_mat(tu, "gilet")
vs = tu.data.vertices
zs = [v.co.z for v in vs]
z0, z1 = min(zs), max(zs)


def ring_r(sel):
    return max(abs(p.x) for p in sel), max(-p.y for p in sel), max(p.y for p in sel)


cb = ring_r([v.co for v in vs if v.co.z < z0 + 0.15 * (z1 - z0)])
ct = ring_r([v.co for v in vs if v.co.z > z1 - 0.1 * (z1 - z0)])
for v in vs:
    t = (v.co.z - z0) / (z1 - z0)
    zn = 0.795 + t * (1.065 - 0.795)
    tb = (0.19, 0.125, 0.135)
    tt = (0.147, 0.103, 0.103)
    fx = (tb[0] / cb[0]) * (1 - t) + (tt[0] / ct[0]) * t
    ff = (tb[1] / cb[1]) * (1 - t) + (tt[1] / ct[1]) * t
    fb = (tb[2] / cb[2]) * (1 - t) + (tt[2] / ct[2]) * t
    v.co = V((v.co.x * fx, v.co.y * (fb if v.co.y > 0 else ff), zn))
bm = bmesh.new()
bm.from_mesh(tu.data)
dead = []
for f in bm.faces:
    c = f.calc_center_median()
    rx = 0.19 + (0.147 - 0.19) * (c.z - 0.795) / 0.27
    if c.z < 0.985 and abs(c.x) / rx > 0.9:
        dead.append(f)
bmesh.ops.delete(bm, geom=dead, context="FACES")
bm.to_mesh(tu.data)
bm.free()
log("tunica: facce tolte sui fianchi", len(dead))

# ---- 4.1 jacket: 6 vertical seams (4 new grooves + the 2 old lapel edges) ----
seams = []
for x in (-0.10, -0.045, 0.045, 0.10):
    pts = [new_pt(z, x, True, 0.0012) for z in (1.13, 1.18, 1.23, 1.28, 1.33, 1.38)]
    seams.append(loft("_seam", [(p, 0.0022, 0.0016, 0.0016) for p in pts], seg=4, mat=matobj("cucitura"),
                      up=V((0, -1, 0))))
sm = join(seams, "Cuciture")
bind(sm, TOR)

# ---- 4.3 cross straps ----
parts = split_loose(obj("Cinghie"))
used = []
for o in parts:
    n = len(o.data.vertices)
    c = centroid(o)
    vs = o.data.vertices
    if n == 62:
        sx = 1 if (sum((vs[i].co for i in range(6)), V()) / 6).x > 0 else -1
        front = c.y < 0
        rings = []
        if front:
            rings.append((V((0.13 * sx, -0.03, 1.437)), 0.0175, 0.004, 0.004))
            for j in range(9):
                t = j / 8
                x, z = (0.13 - 0.28 * t) * sx, 1.41 - 0.37 * t
                rings.append((new_pt(z, x, True, 0.007 + 0.004 * math.sin(t * math.pi)), 0.0175, 0.004, 0.004))
            ok = reloft(o, rings, 6, up=V((0, -1, 0)))
        else:
            rings.append((V((0.13 * sx, 0.035, 1.437)), 0.0175, 0.004, 0.004))
            for j in range(9):
                t = j / 8
                x, z = (0.13 - 0.03 * t) * sx, 1.41 - 0.31 * t
                rings.append((new_pt(z, x, False, 0.024), 0.0175, 0.004, 0.004))
            ok = reloft(o, rings, 6, up=V((0, 1, 0)))
        used.append(("cinghia", front, sx, ok))
    elif n == 32:
        sx = 1 if c.x > 0 else -1
        rings = [(V((0.13 * sx, y, z)), 0.0175, 0.004, 0.004)
                 for y, z in ((-0.062, 1.414), (-0.034, 1.438), (0.0, 1.447), (0.036, 1.438), (0.066, 1.414))]
        used.append(("spalla", sx, reloft(o, rings, 6, up=V((0, 0, 1)))))
    elif n == 84:
        front = c.y < 0
        tgt = new_pt(1.238, 0.0, True, 0.016) if front else new_pt(1.24, 0.0, False, 0.03)
        for v in vs:
            v.co += tgt - c
        used.append(("anello", front))
    else:
        used.append(("altro", n, tuple(round(q, 3) for q in c)))
    o.data.update()
log("cinghie:", used)
straps = join(parts, "Cinghie")

# brass buckles (0.03 x 0.03) on each front strap at Z 1.30
bk = []
for sx in (1, -1):
    t = (1.41 - 1.30) / 0.37
    x = (0.13 - 0.28 * t) * sx
    p = new_pt(1.30, x, True, 0.007 + 0.004 * math.sin(t * math.pi) + 0.005)
    ang = math.atan2(-0.28 * sx, -0.37)
    R = Matrix.Rotation(-ang + math.pi, 3, "Y")
    for dx, dz, sxz in ((0.0, 0.0125, (0.03, 0.005, 0.005)), (0.0, -0.0125, (0.03, 0.005, 0.005)),
                        (0.0125, 0.0, (0.005, 0.005, 0.03)), (-0.0125, 0.0, (0.005, 0.005, 0.03)),
                        (0.0, 0.0, (0.0025, 0.004, 0.028))):
        bk.append(box("_bk", p + R @ V((dx, 0, dz)), sxz, mat="ottone", rot=R))
fb = join(bk, "Fibbie_cinghie")
bind(fb, TOR, rigid=True)

# ---- 4.4 chest strap under the breasts (Z 1.20, 0.03 wide) ----
cp = new_band("Cinghia_petto", 1.185, 1.215, 0.004, matobj("cuoio"), seg=32)
bind(cp, TOR)

# ---- 4.5 main belt 1.06 -> 1.12 with a framed brass buckle and pin ----
parts = split_loose(obj("Cintura"))
for o in parts:
    n = len(o.data.vertices)
    if n == 58:
        rr = []
        for z in (1.06, 1.12):
            zz, rx, rf, rb, yo = tab(NEWT, z)
            rr.append(((0, yo, z), rx + 0.008, rf + 0.008, rb + 0.008))
        reloft(o, rr, 28)
        use_mat(o, "cuoio_cintura")
yf = new_pt(1.09, 0.0, True, 0.008).y
for o in parts:
    if len(o.data.vertices) == 8:
        m = matname(o)
        c = centroid(o)
        if m == "ottone":   # back plate of the buckle
            sz, yy = (0.07, 0.003, 0.05), yf - 0.003
        else:               # leather tongue under the frame
            sz, yy = (0.045, 0.004, 0.03), yf - 0.006
        a, b = bbox(o)
        for v in o.data.vertices:
            q = (v.co - c)
            v.co = V((math.copysign(sz[0] / 2, q.x), yy + math.copysign(sz[1] / 2, q.y), 1.09 + math.copysign(sz[2] / 2, q.z)))
        o.data.update()
belt = join(parts, "Cintura")
fr = []
for dx, dz, s3 in ((0, 0.022, (0.07, 0.006, 0.006)), (0, -0.022, (0.07, 0.006, 0.006)),
                   (0.032, 0, (0.006, 0.006, 0.05)), (-0.032, 0, (0.006, 0.006, 0.05))):
    fr.append(box("_fr", (dx, yf - 0.009, 1.09 + dz), s3, mat="ottone"))
fr.append(box("_pin", (0.0, yf - 0.011, 1.09), (0.004, 0.004, 0.046), mat="ottone"))
frame_o = join(fr, "Fibbia_cintura")
bind(frame_o, TOR, rigid=True)

# ---- 4.6 lower hip belt, slanting: Z 1.00 at X +0.17, Z 0.94 at X -0.17 ----
parts = split_loose(obj("Cinturone"))
SL = 0.06 / 0.34
for o in parts:
    n = len(o.data.vertices)
    c = centroid(o)
    if n == 58:
        rr = [((0, 0.01, 0.95), 0.168, 0.118, 0.125), ((0, 0.01, 0.99), 0.168, 0.118, 0.125)]
        reloft(o, rr, 28)
        for v in o.data.vertices:
            v.co.z += SL * v.co.x
        o.data.update()
for o in parts:
    if len(o.data.vertices) == 8:
        c = centroid(o)
        x = 0.07 if c.x > 0 else -0.07
        y = 0.01 - 0.122 * math.sqrt(1 - (x / 0.168) ** 2)
        d = V((x, y, 0.97 + SL * x)) - c
        for v in o.data.vertices:
            v.co += d
        o.data.update()
hb = join(parts, "Cinturone")

# ---- 4.7 medallion: brass disc 0.04 on a short cord, centre Z 0.99 ----
md = obj("Medaglione")
c = centroid(md)
a, b = bbox(md)
s = 0.04 / max(1e-4, (b.x - a.x))
tgt = V((0.0, -0.132, 0.99))
for v in md.data.vertices:
    v.co = tgt + (v.co - c) * s
md.data.update()
cord = tube("Medaglione_cordino", (0, -0.13, 1.066), (0, -0.131, 1.01), 0.0022, None, 6, "corda")
bind(cord, ["Hips", "Spine"], rigid=True)

for nm in ("Tunica", "Cinghie", "Cintura", "Cinturone", "Medaglione", "Cinghia_petto"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(4)
render_parte("rev_4_busto", ["Busto", "Tunica", "Cinghie", "Cintura", "Cinturone", "Medaglione", "Cinghia_petto",
                             "Fibbie", "Fibbia", "Cuciture", "Bottoni", "Bavero", "Colletto", "Collo", "Testa",
                             "Capelli", "Pantaloni"], ["fronte", "retro", "tre_quarti"])
