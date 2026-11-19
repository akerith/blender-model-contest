# GROUP 5 fix: the sleeve/gauntlet/gauge came out scrambled (vertex order changes when parts are separated).
# Take those pieces back from the saved group-4 file and re-shape them with an order-independent method:
# every vertex is moved radially around the arm axis (same faces, new radius profile).
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
SRC = r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\personaggio_rev_g4.blend"
rig = bpy.data.objects["Scheletro"]
for nm in ("Braccio.L", "Braccio.R", "Guanto.L", "Guanto.R", "Quadrante"):
    kill(nm)
want = ["Braccio.L", "Braccio.R", "Guanto.L", "Guanto.R", "Quadrante", "Mano.L", "Mano.R"]
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    req = [n for n in src.objects if n in want]
    dst.objects = list(req)
L = {}
for o, nm in zip(dst.objects, req):
    bpy.context.scene.collection.objects.link(o)
    o.parent = rig
    for md in o.modifiers:
        if md.type == "ARMATURE":
            md.object = rig
    L[nm] = o
log("caricati:", sorted((k, o.name) for k, o in L.items()))
for o in list(bpy.data.objects):
    if o.name.startswith("Scheletro.") and o.type == "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)


def closest_on_poly(p, pts):
    best, acc = None, 0.0
    for a, b in zip(pts, pts[1:]):
        ab = b - a
        ln = ab.length
        t = max(0.0, min(1.0, (p - a).dot(ab) / (ln * ln)))
        q = a + ab * t
        d = (p - q).length
        if best is None or d < best[0]:
            best = (d, q, acc + t * ln)
        acc += ln
    return best[1], best[2]


def radial(o, pts, prof, s0=0.0):
    for v in o.data.vertices:
        q, s = closest_on_poly(v.co, pts)
        r = v.co - q
        if r.length > 1e-5:
            v.co = q + r.normalized() * pwl(prof, s - s0)
    o.data.update()


d1 = (ELB1 - SH1).normalized()
d2 = (WRI1 - ELB1).normalized()
TOPG = ELB1 + d2 * 0.04
for s, sx in ((".L", 1), (".R", -1)):
    M3 = lambda v: V((v.x * sx, v.y, v.z))
    S, E, W, T = M3(SH1), M3(ELB1), M3(WRI1), M3(TOPG)
    a1, a2 = M3(d1), M3(d2)
    out = M3(V((math.sin(A_LOW), 0, math.cos(A_LOW))))
    # ---- sleeve ----
    parts = split_loose(L["Braccio" + s])
    for o in parts:
        n = len(o.data.vertices)
        if n == 86:
            radial(o, [S - a1 * 0.08, E, W], [(-0.06, 0.054), (0.03, 0.050), (0.15, 0.054), (0.27, 0.047),
                                              (0.29, 0.045), (0.41, 0.034), (0.54, 0.030)], s0=0.08)
        elif n == 96:   # the old roll (it was below the elbow) -> the big roll just above the elbow
            c = centroid(o)
            q = a2.rotation_difference(a1).to_matrix()
            tgt = S + a1 * 0.272
            for v in o.data.vertices:
                v.co = tgt + q @ ((v.co - c) * 0.96)
            o.data.update()
    rolls = [torus("_roll", S + a1 * dist, R, 0.0105, 16, 6, normal=a1, mat="manica")
             for dist, R in ((0.212, 0.047), (0.232, 0.049), (0.252, 0.048))]
    for o in rolls:
        o.vertex_groups.clear()
    arm = join(parts + rolls, "Braccio" + s)
    use_mat(arm, "manica")
    bind(arm, ["Shoulder" + s, "UpperArm" + s, "LowerArm" + s, "Chest"])
    # ---- gauntlet 0.075 at the wrist -> 0.095 at the top (0.04 below the elbow) ----
    g = L["Guanto" + s]
    radial(g, [E - a2 * 0.02, W + a2 * 0.05], [(0.0, 0.048), (0.04, 0.0475), (0.075, 0.0455), (0.14, 0.041),
                                               (0.25, 0.0375), (0.27, 0.036)], s0=-0.02)
    use_mat(g, "guanto")
    cuff = loft("_cuff", [(T - a2 * 0.006, 0.047, 0.047, 0.047), (T + a2 * 0.002, 0.052, 0.052, 0.052),
                          (T + a2 * 0.009, 0.056, 0.056, 0.056)], seg=16, mat="guanto", cap=(False, False))
    solidify(cuff, 0.006, 0.0)
    cuff.vertex_groups.clear()
    # ---- 3 straps: wrist + middle (old ones, moved along the arm), top cuff (new) ----
    old = split_loose(L["Mano" + s])
    straps = [o for o in old if len(o.data.vertices) == 30]
    for o in old:
        if o not in straps:
            kill(o)
    spots = [W.lerp(T, 0.12), W.lerp(T, 0.55)]
    straps.sort(key=lambda o: (centroid(o) - W).length)
    for o, p in zip(straps, spots):
        c = centroid(o)
        q0, s_c = closest_on_poly(c, [E, W])
        shift = p - q0
        for v in o.data.vertices:
            v.co += shift
        rr = 0.0395 + 0.0075 * (p - W).length / (T - W).length
        radial(o, [E - a2 * 0.1, W + a2 * 0.1], [(0.0, rr), (1.0, rr)])
        use_mat(o, "cinghia_guanto")
    top = tube("_strap_top", T - a2 * 0.022, T - a2 * 0.007, 0.0495, None, 14, "cinghia_guanto")
    top.vertex_groups.clear()
    bks = [box("_bk", p + out * (rr + 0.002), (0.015, 0.006, 0.015), mat="ottone")
           for p, rr in ((spots[0], 0.041), (spots[1], 0.044), (T - a2 * 0.0145, 0.0495))]
    for o in bks:
        o.vertex_groups.clear()
    gs = join([g, cuff, top] + straps + bks, "Guanto" + s)
    bind(gs, ["LowerArm" + s, "Hand" + s, "UpperArm" + s])

# ---- bracer-gauge: rigid move of the old gauge (rotate + scale) to the outside of the left forearm ----
qd = L["Quadrante"]
c = centroid(qd)
q0, _ = closest_on_poly(c, [ELB1, WRI1])
n0 = (c - q0).normalized()
n_out = V((math.sin(A_LOW), -0.35, math.cos(A_LOW))).normalized()
P = WRI1.lerp(TOPG, 0.26)
R = n0.rotation_difference(n_out).to_matrix()
tgt = P + n_out * 0.047
for v in qd.data.vertices:
    v.co = tgt + R @ ((v.co - c) * 0.92)
qd.data.update()
qd.name = "Quadrante"
qd.vertex_groups.clear()
gq = qd.vertex_groups.new(name="LowerArm.L")
gq.add([v.index for v in qd.data.vertices], 1.0, "REPLACE")
# materials of the gauge: brass + green glass
for i, m in enumerate(qd.data.materials):
    if m and m.name.startswith("ottone"):
        qd.data.materials[i] = bpy.data.materials["ottone"]
    elif m and m.name.startswith("verde_gemma"):
        qd.data.materials[i] = bpy.data.materials["verde_gemma"]
for nm in ("Braccio.L", "Guanto.L", "Mano.L", "Quadrante", "Braccio.R", "Guanto.R"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(5)
render_parte("rev_5_braccio", ["Braccio.L", "Guanto.L", "Mano.L", "Quadrante"], ["fronte", "retro", "tre_quarti", "alto"])
