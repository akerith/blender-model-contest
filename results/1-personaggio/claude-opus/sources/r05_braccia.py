# GROUP 5 - arms: puffy rolled sleeves, gauntlets with cuff and 3 straps, bracer-gauge, hands (re-shaped)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
reset_colours()   # colours of groups 2-4 now as display (sRGB) values
set_mat("manica", (0.82, 0.76, 0.64), 0.9)
set_mat("guanto", (0.26, 0.16, 0.09), 0.65)
set_mat("cinghia_guanto", (0.20, 0.12, 0.07), 0.65)
set_mat("verde_gemma", (0.25, 0.55, 0.35), 0.1)
d1 = (ELB1 - SH1).normalized()
d2 = (WRI1 - ELB1).normalized()
TOPG = ELB1 + d2 * 0.04          # top of the gauntlet, 0.04 below the elbow
info = []

for s, sx in ((".L", 1), (".R", -1)):
    M3 = lambda v: V((v.x * sx, v.y, v.z))
    S, E, W, T = M3(SH1), M3(ELB1), M3(WRI1), M3(TOPG)
    a1, a2, dh = M3(d1), M3(d2), M3(HD1)
    out = M3(V((math.sin(A_LOW), 0, math.cos(A_LOW))))   # outside/top of the forearm
    # ---- 5.1 sleeve: puffy, 0.10 at the shoulder, rolled and bunched above the elbow ----
    arm = obj("Braccio" + s)
    use_mat(arm, "manica")
    parts = split_loose(arm)
    for o in parts:
        n = len(o.data.vertices)
        if n == 86:
            rings = [(S - a1 * 0.03 + V((0, 0, -0.01)), 0.054, 0.054, 0.054), (S + a1 * 0.03, 0.050, 0.050, 0.050),
                     (S + a1 * 0.15, 0.053, 0.053, 0.053), (E - a1 * 0.01, 0.046, 0.046, 0.046),
                     (E + a2 * 0.12, 0.034, 0.034, 0.034), (W, 0.03, 0.03, 0.03)]
            info.append(("manica", reloft(o, rings, 14, up=V((0, 1, 0)))))
        elif n == 96:   # the old elbow roll -> the big roll just above the elbow (0.11 across)
            info.append(("rotolo", retorus(o, S + a1 * 0.272, 0.043, 0.012, a1, 16, 6)))
    rolls = []
    for dist, R in ((0.212, 0.047), (0.232, 0.049), (0.252, 0.048)):   # bulging rings between Z 1.25 and the elbow
        rolls.append(torus("_roll", S + a1 * dist, R, 0.0105, 16, 6, normal=a1, mat="manica"))
    for o in rolls:
        o.vertex_groups.clear()
    arm = join(parts + rolls, "Braccio" + s)
    bind(arm, ["Shoulder" + s, "UpperArm" + s, "LowerArm" + s, "Chest"])

    # ---- 5.2 gauntlet: 0.075 at the wrist, 0.095 at the top, flared cuff ring ----
    g = obj("Guanto" + s)
    use_mat(g, "guanto")
    rings = [(W + a2 * 0.012, 0.036, 0.036, 0.036), (W - a2 * 0.02, 0.0375, 0.0375, 0.0375),
             (W.lerp(T, 0.45), 0.041, 0.041, 0.041), (W.lerp(T, 0.85), 0.0455, 0.0455, 0.0455),
             (T, 0.0475, 0.0475, 0.0475)]
    info.append(("guanto", reloft(g, rings, 14, up=V((0, 1, 0)))))
    cuff = loft("_cuff", [(T - a2 * 0.006, 0.047, 0.047, 0.047), (T + a2 * 0.002, 0.052, 0.052, 0.052),
                          (T + a2 * 0.009, 0.056, 0.056, 0.056)], seg=16, mat="guanto", cap=(False, False))
    solidify(cuff, 0.006, 0.0)
    cuff.vertex_groups.clear()
    g = join([g, cuff], "Guanto" + s)

    # ---- 5.5 hand frame ----
    pdown = M3(V((-math.sin(A_HAND), 0, -math.cos(A_HAND))))
    pn = (pdown * math.cos(math.radians(25)) + V((0, 1, 0)) * math.sin(math.radians(25))).normalized()
    sa = pn.cross(dh).normalized()
    if sa.y > 0:
        sa = -sa     # side axis from little finger to index points forward (-Y)
    hand = obj("Mano" + s)
    use_mat(hand, "guanto")
    parts = split_loose(hand)
    fingers, straps = [], []
    for o in parts:
        n = len(o.data.vertices)
        if n == 50:      # palm 0.085 x 0.08 x 0.03
            rings = [(W - dh * 0.006, 0.030, 0.013, 0.013), (W + dh * 0.03, 0.040, 0.0155, 0.0155),
                     (W + dh * 0.068, 0.041, 0.015, 0.015), (W + dh * 0.087, 0.037, 0.012, 0.012)]
            info.append(("palmo", reloft(o, rings, 12, up=pn)))
        elif n == 34:
            fingers.append(o)
        elif n == 26:    # thumb: from the side of the palm near the wrist, forward-down 40 deg from the index
            tb = W + dh * 0.028 + sa * 0.034 + pn * 0.006
            td = (dh * math.cos(math.radians(40)) + sa * math.sin(math.radians(40)) + pn * 0.25).normalized()
            t2 = (td + pn * 0.25).normalized()
            rings = [(tb, 0.0115, 0.0115, 0.0115), (tb + td * 0.035, 0.0105, 0.0105, 0.0105),
                     (tb + td * 0.035 + t2 * 0.03, 0.0088, 0.0088, 0.0088)]
            info.append(("pollice", reloft(o, rings, 8)))
        elif n == 30:
            straps.append(o)
    fingers.sort(key=lambda o: -centroid(o).dot(sa))   # index first
    for o, (ln, off, spread) in zip(fingers, ((0.075, 0.029, 12), (0.085, 0.0095, 4), (0.08, -0.0095, -4),
                                             (0.065, -0.028, -12))):
        base = W + dh * 0.086 + sa * off
        dv = (dh * math.cos(math.radians(spread)) + sa * math.sin(math.radians(spread))).normalized()
        pts = [base]
        for j, frac in enumerate((0.42, 0.32, 0.26)):
            ax = dv.cross(pn).normalized()
            dv = (Matrix.Rotation(math.radians(10), 3, ax) @ dv).normalized()
            pts.append(pts[-1] + dv * ln * frac)
        r = 0.0098
        info.append(("dito", reloft(o, [(pts[0], r, r, r), (pts[1], r * 0.97, r * 0.97, r * 0.97),
                                        (pts[2], r * 0.9, r * 0.9, r * 0.9), (pts[3], r * 0.8, r * 0.8, r * 0.8)], 8)))
    # thumb base (thenar) - new small piece
    base = sphere("_tbase", W + dh * 0.03 + sa * 0.026 + pn * 0.008, 0.02, 10, 6, scale=(1.0, 1.0, 0.6),
                  mat="guanto")
    base.vertex_groups.clear()
    # ---- 5.3 three straps per gauntlet: top cuff (new), middle and wrist (re-shaped) with tiny buckles ----
    spots = [W.lerp(T, 0.12), W.lerp(T, 0.55)]
    for o, p in zip(straps, spots):
        rr = 0.0395 + 0.007 * (p - W).length / (T - W).length
        reloft(o, [(p - a2 * 0.0075, rr, rr, rr), (p + a2 * 0.0075, rr, rr, rr)], 14)
        use_mat(o, "cinghia_guanto")
    top = tube("_strap_top", T - a2 * 0.022, T - a2 * 0.007, 0.0495, None, 14, "cinghia_guanto")
    top.vertex_groups.clear()
    bks = []
    for p, rr in ((spots[0], 0.041), (spots[1], 0.044), (T - a2 * 0.0145, 0.0495)):
        bks.append(box("_bk", p + out * (rr + 0.002), (0.015, 0.006, 0.015), mat="ottone"))
    for o in bks:
        o.vertex_groups.clear()
    hand = join([o for o in parts if o not in straps] + [base], "Mano" + s)
    subdivide(hand, 1)
    bind(hand, ["Hand" + s, "LowerArm" + s])
    gs = join([g, top] + straps + bks, "Guanto" + s)
    bind(gs, ["LowerArm" + s, "Hand" + s, "UpperArm" + s])

# ---- 5.4 bracer-gauge on her LEFT forearm, outside, above the wrist ----
q = obj("Quadrante")
parts = split_loose(q)
W, T = WRI1, TOPG
n_out = V((math.sin(A_LOW), -0.35, math.cos(A_LOW))).normalized()
P = W.lerp(T, 0.26)
for o in parts:
    n = len(o.data.vertices)
    m = matname(o)
    if n == 108:
        retorus(o, P + n_out * 0.0545, 0.0255, 0.0028, n_out, 18, 6)
    elif n == 38 and m == "verde_gemma":
        reloft(o, [(P + n_out * 0.050, 0.023, 0.023, 0.023), (P + n_out * 0.0535, 0.023, 0.023, 0.023)], 18)
    elif n == 38:
        reloft(o, [(P + n_out * 0.038, 0.0275, 0.0275, 0.0275), (P + n_out * 0.053, 0.0275, 0.0275, 0.0275)], 18)
q = join(parts, "Quadrante")
for o in [q]:
    o.vertex_groups.clear()
    g = o.vertex_groups.new(name="LowerArm.L")
    g.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
log("rimodellati:", info)
for nm in ("Braccio.L", "Guanto.L", "Mano.L", "Quadrante"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(5)
render_parte("rev_5_braccio", ["Braccio.L", "Guanto.L", "Mano.L", "Quadrante"], ["fronte", "retro", "tre_quarti", "alto"])
