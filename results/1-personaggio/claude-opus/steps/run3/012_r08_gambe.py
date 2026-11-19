# GROUP 8 - legs and boots (re-shaped with order-independent moves + new eyelets, shin wraps, creases)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
set_mat("pantaloni", (0.22, 0.19, 0.16), 0.9)
set_mat("stivale", (0.30, 0.18, 0.10), 0.65)
set_mat("suola", (0.12, 0.08, 0.06), 0.7)
set_mat("laccio", (0.55, 0.42, 0.28), 0.8)
set_mat("ginocchiera", (0.28, 0.17, 0.09), 0.65)
set_mat("piega", (0.12, 0.10, 0.09), 0.9)


def place_bar(o, p0, p1, w, t):
    """order-independent: put a small box-like part between p0 and p1 (width w, thickness t)"""
    c, axes = pca(o)
    d = (V(p1) - V(p0))
    L = d.length
    dd = d.normalized()
    nrm = V((0, -1, 0))
    side = dd.cross(nrm).normalized()
    e = [2 * max(abs((v.co - c).dot(a)) for v in o.data.vertices) or 1.0 for a in axes]
    mid = (V(p0) + V(p1)) / 2
    for v in o.data.vertices:
        q = v.co - c
        v.co = mid + dd * q.dot(axes[0]) * (L / e[0]) + side * q.dot(axes[1]) * (w / e[1]) + nrm * q.dot(axes[2]) * (t / e[2])
    o.data.update()


for s, sx in ((".L", 1), (".R", -1)):
    K, A = V((KNEE1.x * sx, KNEE1.y, KNEE1.z)), V((ANK1.x * sx, ANK1.y, ANK1.z))

    def axis_at(z):
        t = (K.z - z) / (K.z - A.z)
        return K.lerp(A, t)
    # ---- boots ----
    parts = split_loose(obj("Stivale" + s))
    info = []
    for o in parts:
        n = len(o.data.vertices)
        m = matname(o)
        a, b = bbox(o)
        if n == 98:    # shaft: ankle 0.09 -> top 0.12 across, up to Z 0.42
            z0, z1 = a.z, b.z
            for v in o.data.vertices:
                z = 0.07 + (v.co.z - z0) / (z1 - z0) * (0.42 - 0.07)
                q = axis_at(z)
                r = pwl([(0.07, 0.046), (0.12, 0.046), (0.20, 0.051), (0.30, 0.056), (0.42, 0.060)], z)
                d = V((v.co.x - q.x, v.co.y - q.y, 0))
                if d.length > 1e-5:
                    d = d.normalized() * r
                v.co = V((q.x + d.x, q.y + d.y, z))
            o.data.update()
            use_mat(o, "stivale")
            info.append("gambale")
        elif n == 50:  # folded-down cuff 0.04 high at the top, slightly wider
            remap_cyl(o, axis_at(0.385), axis_at(0.425), 0.066)
            use_mat(o, "stivale")
        elif n == 34:  # straps: ankle (0.09) and top of the shaft (0.38)
            info.append("cinghia")
        elif n == 86:  # foot 0.27 long (toe Y -0.19, heel Y +0.08), 0.10 wide
            ys = [v.co.y for v in o.data.vertices]
            y0, y1 = min(ys), max(ys)
            xc = (a.x + b.x) / 2
            w = b.x - a.x
            zb = a.z
            for v in o.data.vertices:
                t = (v.co.y - y0) / (y1 - y0)
                v.co = V((0.13 * sx + (v.co.x - xc) * (0.10 / w), -0.19 + t * 0.27, max(0.02, v.co.z - zb + 0.02)))
            o.data.update()
            use_mat(o, "stivale")
        elif n == 8 and m.startswith("cuoio") and b.z < 0.05:
            if b.y - a.y > 0.15:   # sole 0.02 thick
                for v in o.data.vertices:
                    v.co = V((0.13 * sx + math.copysign(0.05, v.co.x - (a.x + b.x) / 2),
                              -0.19 if v.co.y < (a.y + b.y) / 2 else 0.08, 0.0 if v.co.z < (a.z + b.z) / 2 else 0.02))
            else:                  # heel block 0.03 high at the back
                for v in o.data.vertices:
                    v.co = V((0.13 * sx + math.copysign(0.045, v.co.x - (a.x + b.x) / 2),
                              0.0 if v.co.y < (a.y + b.y) / 2 else 0.08, 0.0 if v.co.z < (a.z + b.z) / 2 else 0.03))
            o.data.update()
            use_mat(o, "suola")
    straps = sorted([o for o in parts if len(o.data.vertices) == 34], key=lambda o: centroid(o).z)
    bucks = sorted([o for o in parts if len(o.data.vertices) == 8 and matname(o).startswith("ottone")],
                   key=lambda o: centroid(o).z)
    for o, z, r in zip(straps, (0.09, 0.38), (0.049, 0.062)):
        remap_cyl(o, axis_at(z - 0.009), axis_at(z + 0.009), r)
        use_mat(o, "cuoio")
    for o, z, r in zip(bucks, (0.09, 0.38), (0.049, 0.062)):
        q = axis_at(z)
        rigid_to(o, q + V((sx * (r + 0.004), -0.01, 0)), None, 1.0)
    # laces: 8 crossed laces between two rows of eyelets 0.03 apart, Z 0.10 -> 0.40
    lp = split_loose(obj("Lacci" + s))
    lp.sort(key=lambda o: centroid(o).z)
    eyel = []
    for j in range(8):
        z0 = 0.10 + j * (0.30 / 8)
        z1 = z0 + 0.30 / 8
        r0 = pwl([(0.07, 0.046), (0.12, 0.046), (0.20, 0.051), (0.30, 0.056), (0.42, 0.060)], (z0 + z1) / 2)
        q0, q1 = axis_at(z0), axis_at(z1)
        y = (q0.y + q1.y) / 2 - r0 - 0.003
        xa, xb = q0.x - 0.015, q0.x + 0.015
        if 2 * j + 1 < len(lp):
            place_bar(lp[2 * j], V((xa, y, z0)), V((xb, y, z1)), 0.004, 0.004)
            place_bar(lp[2 * j + 1], V((xb, y, z0)), V((xa, y, z1)), 0.004, 0.004)
    for j in range(9):
        z = 0.10 + j * (0.30 / 8)
        q = axis_at(z)
        r0 = pwl([(0.07, 0.046), (0.12, 0.046), (0.20, 0.051), (0.30, 0.056), (0.42, 0.060)], z)
        for dx in (-0.015, 0.015):
            eyel.append(box("_eye", V((q.x + dx, q.y - r0 - 0.002, z)), (0.006, 0.004, 0.006), mat="ottone"))
    lac = join(lp, "Lacci" + s)
    use_mat(lac, "laccio")
    for o in eyel:
        o.vertex_groups.clear()
    ey = join(eyel, "Occhielli" + s)
    bind(ey, ["LowerLeg" + s], rigid=False)
    boot = join(parts, "Stivale" + s)
    bind(boot, ["LowerLeg" + s, "Foot" + s, "Toes" + s])
    bind(lac, ["LowerLeg" + s])
    # ---- 8.3 shin wraps: 3 overlapping cream rings, Z 0.40 -> 0.46 ----
    wr = []
    for i, z in enumerate((0.413, 0.432, 0.451)):
        q = axis_at(z)
        wr.append(torus("_wrap", q, 0.058 - 0.001 * i, 0.0105, 18, 6, normal=(0, 0.06 * (i - 1), 1), mat="stoffa_crema"))
    for o in wr:
        o.vertex_groups.clear()
    wo = join(wr, "Fasce" + s)
    bind(wo, ["LowerLeg" + s])
    # ---- 8.1 creases at the back of the knee ----
    cr = []
    for i, dz in enumerate((-0.025, 0.0, 0.028)):
        pts = []
        for j in range(5):
            u = (j / 4 - 0.5) * 1.6
            pts.append(V((K.x + math.sin(u) * 0.05, K.y + math.cos(u) * 0.058, K.z + dz + 0.006 * math.cos(u * 2))))
        cr.append(loft("_crease", [(p, 0.0028, 0.0028, 0.0028) for p in pts], seg=4, mat=matobj("piega")))
    for o in cr:
        o.vertex_groups.clear()
    co = join(cr, "Pieghe" + s)
    bind(co, ["UpperLeg" + s, "LowerLeg" + s])

# ---- 8.2 knee pads: 0.11 across, 0.025 thick, centre Z 0.50 on the front of the knee + straps ----
parts = split_loose(obj("Ginocchiere"))
for o in parts:
    n = len(o.data.vertices)
    c = centroid(o)
    sx = 1 if c.x > 0 else -1
    K = V((KNEE1.x * sx, KNEE1.y, 0.50))
    if n == 100:
        rigid_to(o, K + V((0, -0.071, 0)), V((0, -1, 0)), 1.0)
        a, b = bbox(o)
        c2 = centroid(o)
        for v in o.data.vertices:
            d = v.co - c2
            v.co = c2 + V((d.x * 0.11 / (b.x - a.x), d.y * 0.025 / (b.y - a.y), d.z * 0.11 / (b.z - a.z)))
        o.data.update()
        use_mat(o, "ginocchiera")
    else:
        z = 0.553 if c.z > 0.495 else 0.447
        remap_cyl(o, V((KNEE1.x * sx, KNEE1.y, z - 0.007)), V((KNEE1.x * sx, KNEE1.y, z + 0.007)), 0.061)
        use_mat(o, "cuoio")
kp = join(parts, "Ginocchiere")
bind(kp, ["UpperLeg.L", "LowerLeg.L", "UpperLeg.R", "LowerLeg.R"])
for nm in ("Stivale.L", "Ginocchiere", "Fasce.L", "Lacci.L", "Occhielli.L"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(8)
render_parte("rev_8_gambe", ["Stivale", "Ginocchiere", "Fasce", "Lacci", "Occhielli", "Pieghe", "Pantaloni"],
             ["fronte", "destra", "retro", "tre_quarti"])
