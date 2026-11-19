exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
random.seed(7)

# --- fix legs: slimmer at the top, inside the torso ---
clear("C_gamba")
for s, sx in ((".L", 1), (".R", -1)):
    def L(t, r, rf, rb, dy=0.0):
        p = HIP.lerp(KNEE, t) if t <= 1 else KNEE.lerp(ANK, t - 1)
        return ((p.x * sx * (0.85 if t < 0.1 else 1.0), p.y + dy, p.z), r, rf, rb)
    loft("C_gamba" + s, [L(-0.05, 0.07, 0.075, 0.085), L(0.05, 0.078, 0.085, 0.095), L(0.25, 0.076, 0.078, 0.082),
                         L(0.55, 0.068, 0.066, 0.066), L(0.85, 0.058, 0.057, 0.057), L(1.0, 0.054, 0.057, 0.054),
                         L(1.2, 0.057, 0.056, 0.064), L(1.5, 0.050, 0.049, 0.053), L(1.8, 0.041, 0.041, 0.044),
                         L(2.0, 0.036, 0.038, 0.04)], seg=16, mat="pantaloni",
         bones=["Hips", "UpperLeg" + s, "LowerLeg" + s])

# --- fingers: less curl ---
clear("C_dito")
for s, sx in ((".L", 1), (".R", -1)):
    d = V((ARM_D.x * sx, 0, ARM_D.z))
    pn = V((PALM_N.x * sx, 0, PALM_N.z))
    W = V((WRI.x * sx, WRI.y, WRI.z))
    K = W + d * 0.085
    for i, (off, ln, rr) in enumerate([(-0.029, 0.074, 0.0105), (-0.010, 0.084, 0.011), (0.009, 0.079, 0.0105),
                                       (0.026, 0.064, 0.0095)]):
        base = K + V((0, off, 0)) - d * 0.005
        pts = [base]
        dirv = d + V((0, off * 0.6, 0))
        for j in range(3):
            dirv = (dirv.normalized() + pn * 0.13).normalized()
            pts.append(pts[-1] + dirv * ln / 3)
        loft("C_dito%d%s" % (i, s), [(pts[0], rr, rr, rr), (pts[1], rr, rr, rr), (pts[2], rr * 0.95, rr * 0.95, rr * 0.95),
                                     (pts[3], rr * 0.8, rr * 0.8, rr * 0.8)], seg=8, mat="cuoio_scuro",
             bones=["Hand" + s])

# --- face ---
clear("F_")
HB = ["Head"]
for sx in (1, -1):
    sphere("F_occhio_b%d" % sx, (0.030 * sx, -0.062, 1.603), 0.0125, 10, 6, mat="bianco_occhi", bones=HB)
    sphere("F_iride%d" % sx, (0.030 * sx, -0.0725, 1.603), 0.0068, 8, 5, scale=(1, 0.5, 1), mat="occhi", bones=HB)
    # brows: slightly frowning
    rot = Matrix.Rotation(math.radians(-14 * sx), 3, "Y")
    box("F_ciglio%d" % sx, (0.031 * sx, -0.0755, 1.626), (0.034, 0.008, 0.0065), mat="capelli", bones=HB, rot=rot)
    # upper eyelid line
    box("F_palpebra%d" % sx, (0.030 * sx, -0.0735, 1.6125), (0.026, 0.006, 0.003), mat="cuoio_scuro", bones=HB)
    # ears
    sphere("F_orecchio%d" % sx, (0.072 * sx, 0.006, 1.588), 0.024, 10, 6, scale=(0.35, 0.62, 1.0), mat="pelle", bones=HB)
    # cheekbones
    sphere("F_zigomo%d" % sx, (0.045 * sx, -0.055, 1.578), 0.022, 10, 6, scale=(1.0, 0.7, 0.8), mat="pelle", bones=HB)
# nose
loft("F_naso", [((0, -0.070, 1.607), 0.008, 0.006, 0.006), ((0, -0.081, 1.585), 0.010, 0.008, 0.008),
                ((0, -0.091, 1.565), 0.013, 0.010, 0.008), ((0, -0.083, 1.552), 0.012, 0.008, 0.008)],
     seg=10, mat="pelle", bones=HB, up=V((0, 0, 1)))
sphere("F_narici", (0, -0.083, 1.557), 0.011, 10, 6, scale=(1.5, 0.8, 0.7), mat="pelle", bones=HB)
# lips
sphere("F_labbro_s", (0, -0.0755, 1.531), 0.016, 12, 6, scale=(1.45, 0.45, 0.35), mat="labbra", bones=HB)
sphere("F_labbro_i", (0, -0.0735, 1.522), 0.014, 12, 6, scale=(1.35, 0.5, 0.42), mat="labbra", bones=HB)
# chin
sphere("F_mento", (0, -0.062, 1.497), 0.022, 10, 6, scale=(1.2, 0.8, 0.8), mat="pelle", bones=HB)

# --- hair shell ---
clear("K_")
HR = [(1.545, 0.060, 0.025, 0.074, 0.026), (1.57, 0.079, 0.035, 0.093, 0.016), (1.60, 0.083, 0.045, 0.101, 0.008),
      (1.63, 0.084, 0.060, 0.103, 0.004), (1.655, 0.080, 0.077, 0.098, 0.004), (1.68, 0.068, 0.073, 0.083, 0.006),
      (1.70, 0.047, 0.052, 0.058, 0.008), (1.714, 0.018, 0.02, 0.022, 0.01)]
loft("K_calotta", [((0, h[4], h[0]), h[1], h[2], h[3]) for h in HR], seg=20, mat="capelli", bones=HB,
     cap=(False, True))

# --- hair tufts ---
C = V((0, 0.006, 1.612))


def surf(a, e):
    ry = 0.083 if math.cos(a) > 0 else 0.102
    return C + V((math.sin(a) * 0.086 * math.cos(e), -math.cos(a) * ry * math.cos(e), 0.102 * math.sin(e)))


tufts_main, tufts_white = [], []
n = 0
while n < 150:
    a = random.uniform(-math.pi, math.pi)
    e = random.uniform(-0.75, 1.45)
    front = math.cos(a)
    if front > 0.35 and e < 0.42:
        continue
    if front > -0.1 and e < -0.15:
        continue
    p = surf(a, e)
    nrm = (p - C).normalized()
    down = V((0, 0, -1)) - nrm * nrm.dot(V((0, 0, -1)))
    if down.length < 0.2:
        down = V((random.uniform(-1, 1), random.uniform(-1, 1), 0))
        down -= nrm * nrm.dot(down)
    down.normalize()
    rnd = V((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * 0.45
    bang = front > 0.35
    if bang:
        # bangs fall over the forehead, swept to her left (+X)
        dirv = (down * 1.0 + V((0.45, -0.25, 0)) + nrm * 0.25 + rnd * 0.6).normalized()
        L = random.uniform(0.045, 0.075)
    else:
        dirv = (nrm * 0.45 + down * 0.9 + rnd).normalized()
        L = random.uniform(0.045, 0.085) * (1.15 if e < 0.2 else 1.0)
    r0 = random.uniform(0.016, 0.024)
    p0 = p - nrm * 0.008
    p1 = p0 + dirv * L * 0.45
    d2 = (dirv + down * 0.6 + rnd * 0.5).normalized()
    p2 = p1 + d2 * L * 0.35
    d3 = (d2 + down * 0.5 + nrm * 0.25).normalized()
    p3 = p2 + d3 * L * 0.3
    white = (bang or e > 0.3) and -1.25 < a < -0.25 and e < 1.15
    ob = loft("K_ciuffo%03d" % n, [(p0, r0, r0 * 0.7, r0 * 0.7), (p1, r0 * 0.75, r0 * 0.55, r0 * 0.55),
                                   (p2, r0 * 0.45, r0 * 0.35, r0 * 0.35), (p3, 0.002, 0.002, 0.002)],
              seg=6, mat=("ciocca" if white else "capelli"), bones=HB, cap=(False, False))
    n += 1

log("triangoli:", tri_count())
save()
render_viste("p02", viste=["fronte", "tre_quarti"])
render_parte("p02_testa", ["C_testa", "C_collo", "F_", "K_"], ["fronte", "destra", "tre_quarti", "retro"])
