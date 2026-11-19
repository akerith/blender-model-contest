exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
random.seed(3)
clear("F_zigomo")
clear("V_")
clear("C_piede")
HIPB = ["Hips", "Spine", "UpperLeg.L", "UpperLeg.R"]
TOR = ["Hips", "Spine", "Chest"]

# ---- tunic hem (blue shirt below the vest) ----
sk = loft("V_tunica", [((0, 0.0, 1.00), 0.140, 0.090, 0.093), ((0, 0.01, 0.93), 0.172, 0.104, 0.118),
                       ((0, 0.01, 0.85), 0.178, 0.112, 0.124), ((0, 0.01, 0.76), 0.186, 0.118, 0.13)],
          seg=28, mat="camicia", bones=HIPB, cap=(False, False))
# ragged bottom edge
for v in sk.data.vertices:
    if v.co.z < 0.77:
        v.co.z += random.uniform(-0.025, 0.02)
solidify(sk, 0.006)

# ---- vest buttons + lapel edges ----
for i, z in enumerate([1.05, 1.11, 1.17, 1.30, 1.35]):
    p = torso_pt(z, 0.0, True, 0.003)
    sphere("V_bottone%d" % i, p, 0.007, 8, 4, scale=(1, 0.6, 1), mat="ottone", bones=TOR)
for sx in (1, -1):
    pts = [torso_pt(z, sx * (0.012 + (z - 1.0) * 0.18), True, 0.002) for z in (1.0, 1.1, 1.2, 1.3, 1.38)]
    loft("V_bavero%d" % sx, [(p, 0.009, 0.003, 0.003) for p in pts], seg=6, mat="cuoio_scuro", bones=TOR,
         up=V((0, -1, 0)))

# ---- cross straps (front + back) ----
for side, front in (("A", True), ("B", False)):
    for sx in (1, -1):
        pts = []
        for j in range(9):
            t = j / 8
            x = (0.115 - 0.24 * t) * sx
            z = 1.41 - 0.40 * t
            pts.append(torso_pt(z, x, front, 0.008 + 0.004 * math.sin(t * math.pi)))
        pts.insert(0, pts[0] + V((0.012 * sx, 0.0, 0.035)))
        loft("V_cinghia%s%d" % (side, sx), [(p, 0.020, 0.004, 0.004) for p in pts], seg=6, mat="cuoio",
             bones=TOR, up=V((0, -1 if front else 1, 0)))
    # metal ring where they cross
    c = torso_pt(1.205, 0.0, front, 0.014)
    torus("V_anello" + side, c, 0.016, 0.004, 14, 6, normal=(0, -1 if front else 1, 0), mat="ottone", bones=TOR)
# over the shoulders
for sx in (1, -1):
    loft("V_spallaccio%d" % sx, [((0.112 * sx, -0.085, 1.40), 0.02, 0.004, 0.004), ((0.112 * sx, -0.06, 1.435), 0.02, 0.004, 0.004),
                                 ((0.112 * sx, 0.0, 1.455), 0.02, 0.004, 0.004), ((0.112 * sx, 0.06, 1.44), 0.02, 0.004, 0.004),
                                 ((0.112 * sx, 0.09, 1.40), 0.02, 0.004, 0.004)],
         seg=6, mat="cuoio", bones=["Chest", "Shoulder.L" if sx > 0 else "Shoulder.R"], up=V((0, 0, 1)))

# ---- belts ----
band("V_cintura", 0.985, 1.03, 0.009, "cuoio", TOR)
box("V_fibbia", torso_pt(1.008, 0.0, True, 0.016), (0.05, 0.008, 0.042), mat="ottone", bones=TOR)
box("V_fibbia_in", torso_pt(1.008, 0.0, True, 0.021), (0.03, 0.006, 0.024), mat="cuoio_scuro", bones=TOR)
band("V_cinturone", 0.895, 0.94, 0.012, "cuoio_scuro", HIPB, slope=0.18)
sphere("V_medaglione", torso_pt(0.905, 0.0, True, 0.022), 0.019, 12, 6, scale=(1, 0.35, 1), mat="ottone", bones=HIPB)
for i, x in enumerate((-0.07, 0.07)):
    p = torso_pt(0.92 + 0.18 * x, x, True, 0.022)
    box("V_borchia%d" % i, p, (0.016, 0.006, 0.03), mat="ottone", bones=HIPB)

# ---- pouches ----
for i, (x, z, w, h) in enumerate([(0.10, 0.955, 0.06, 0.07), (-0.115, 0.95, 0.05, 0.065), (0.155, 0.99, 0.045, 0.06)]):
    p = torso_pt(z, x, True, 0.03)
    ob = box("V_borsa%d" % i, p, (w, 0.04, h), mat="cuoio", bones=HIPB,
             rot=Matrix.Rotation(math.atan2(-x, 0.25) * -0.8, 3, "Z"))
    box("V_patta%d" % i, p + V((0, -0.022, h * 0.25)), (w * 1.04, 0.008, h * 0.55), mat="cuoio_scuro", bones=HIPB,
        rot=Matrix.Rotation(math.atan2(-x, 0.25) * -0.8, 3, "Z"))

# ---- long case on her left hip (+X) ----
a, b = V((0.21, -0.02, 0.985)), V((0.225, 0.0, 0.66))
tube("V_astuccio", a, b, 0.033, 0.033, 14, "cuoio", ["Hips", "UpperLeg.L"], rings=2)
for t in (0.0, 0.08, 0.92, 1.0):
    p = a.lerp(b, t)
    d = (b - a).normalized() * 0.012
    tube("V_astuccio_anello%d" % int(t * 100), p - d, p + d, 0.037, 0.037, 14, "ottone", ["Hips", "UpperLeg.L"])
tube("V_astuccio_tappo", a - (b - a).normalized() * 0.03, a, 0.02, 0.03, 10, "ottone", ["Hips", "UpperLeg.L"])

# ---- brass canister on her right hip (-X) ----
a, b = V((-0.205, -0.055, 1.00)), V((-0.215, -0.07, 0.855))
tube("V_barattolo", a, b, 0.043, 0.043, 16, "ottone", ["Hips", "UpperLeg.R"])
for t in (0.2, 0.5, 0.8):
    p = a.lerp(b, t)
    d = (b - a).normalized() * 0.008
    tube("V_barattolo_f%d" % int(t * 10), p - d, p + d, 0.047, 0.047, 16, "cuoio_scuro", ["Hips", "UpperLeg.R"])
tube("V_barattolo_tappo", a - (b - a).normalized() * 0.025, a, 0.025, 0.04, 12, "ottone_scuro", ["Hips", "UpperLeg.R"])

# ---- rope coils hanging at her right hip ----
for i in range(5):
    c = V((-0.155 + 0.006 * i, -0.105 - 0.004 * i, 0.82 + 0.006 * i))
    n = V((-0.35 + 0.05 * i, -1.0, 0.05 * (i - 2)))
    torus("V_corda%d" % i, c + V((0, 0, -0.04)), 0.07 + 0.005 * (i % 2), 0.009, 22, 6, normal=n, mat="corda",
          bones=["Hips", "UpperLeg.R"], scale=(0.9, 1.6))
# rope binding at the top of the coil
tube("V_corda_legame", (-0.15, -0.115, 0.925), (-0.15, -0.115, 0.895), 0.02, 0.02, 10, "corda", ["Hips"])

# ---- cloth rags at her left hip ----
for i, (x, ln) in enumerate([(0.12, 0.26), (0.145, 0.33), (0.175, 0.22)]):
    top = torso_pt(0.91, x, True, 0.03)
    pts = [top + V((random.uniform(-0.01, 0.01) * j, -0.004 * j, -ln * j / 4)) for j in range(5)]
    rr = [(p, 0.022 * (1 - 0.15 * j) + 0.006, 0.0025, 0.0025) for j, p in enumerate(pts)]
    loft("V_straccio%d" % i, rr, seg=6, mat="lino", bones=["Hips", "UpperLeg.L"], up=V((0, -1, 0)))

# ---- knee pads ----
for s, sx in ((".L", 1), (".R", -1)):
    k = V((KNEE.x * sx, KNEE.y - 0.052, KNEE.z + 0.005))
    sphere("V_ginocchiera" + s, k, 0.052, 14, 8, scale=(0.95, 0.42, 1.1), mat="cuoio_scuro", bones=["UpperLeg" + s, "LowerLeg" + s])
    for dz in (0.035, -0.035):
        p = V((KNEE.x * sx, KNEE.y, KNEE.z + dz))
        loft("V_ginocch_cinghia%d%s" % (int(dz * 100), s), [(p + V((0, 0, -0.006)), 0.059, 0.059, 0.059),
                                                            (p + V((0, 0, 0.006)), 0.059, 0.059, 0.059)],
             seg=14, mat="cuoio", bones=["UpperLeg" + s, "LowerLeg" + s])

# ---- boots ----
for s, sx in ((".L", 1), (".R", -1)):
    def lp(z):
        t = (KNEE.z - z) / (KNEE.z - ANK.z)
        p = KNEE.lerp(ANK, t)
        return V((p.x * sx, p.y, z))
    rr = [(lp(0.07), 0.046, 0.05, 0.05), (lp(0.12), 0.047, 0.05, 0.052), (lp(0.2), 0.054, 0.054, 0.06),
          (lp(0.30), 0.062, 0.06, 0.068), (lp(0.38), 0.066, 0.064, 0.07), (lp(0.405), 0.07, 0.068, 0.074)]
    loft("V_stivale" + s, rr, seg=16, mat="cuoio_scuro", bones=["LowerLeg" + s, "Foot" + s])
    # folded cuff
    loft("V_risvolto" + s, [(lp(0.37), 0.071, 0.07, 0.075), (lp(0.40), 0.077, 0.075, 0.081), (lp(0.435), 0.075, 0.073, 0.079)],
         seg=16, mat="cuoio", bones=["LowerLeg" + s], cap=(True, True))
    # straps
    for z in (0.17, 0.29):
        loft("V_stiv_cinghia%d%s" % (int(z * 100), s), [(lp(z - 0.009), 0.0, 0, 0)][:0] +
             [(lp(z - 0.009), 0.061 if z > 0.2 else 0.055, 0.062 if z > 0.2 else 0.056, 0.068 if z > 0.2 else 0.062),
              (lp(z + 0.009), 0.063 if z > 0.2 else 0.057, 0.063 if z > 0.2 else 0.057, 0.069 if z > 0.2 else 0.063)],
             seg=16, mat="cuoio", bones=["LowerLeg" + s])
        box("V_stiv_fibbia%d%s" % (int(z * 100), s), lp(z) + V((0.058 * sx, -0.012, 0)), (0.006, 0.02, 0.022),
            mat="ottone", bones=["LowerLeg" + s])
    # laces on the front
    for j in range(8):
        z = 0.10 + j * 0.034
        p = lp(z)
        zz, rr_ = z, 0.05 + (z - 0.1) * 0.06
        q = V((p.x, p.y - rr_ - 0.002, z))
        for ang in (35, -35):
            box("V_laccio%d_%d%s" % (j, ang, s), q, (0.03, 0.004, 0.0045), mat="corda", bones=["LowerLeg" + s],
                rot=Matrix.Rotation(math.radians(ang), 3, "Y"))
    # foot (up = Z: rb = top, rf = bottom)
    x = 0.118 * sx
    loft("V_piede" + s, [((x, 0.065, 0.05), 0.034, 0.045, 0.03), ((x, 0.035, 0.06), 0.047, 0.06, 0.05),
                         ((x, -0.04, 0.047), 0.052, 0.047, 0.037), ((x, -0.11, 0.037), 0.050, 0.037, 0.027),
                         ((x, -0.16, 0.031), 0.040, 0.031, 0.021), ((x, -0.182, 0.03), 0.022, 0.025, 0.015)],
         seg=14, mat="cuoio_scuro", bones=["Foot" + s, "Toes" + s, "LowerLeg" + s], up=V((0, 0, 1)))
    box("V_suola" + s, (x, -0.06, 0.008), (0.10, 0.25, 0.016), mat="cuoio_scuro", bones=["Foot" + s, "Toes" + s])
    box("V_tacco" + s, (x, 0.045, 0.018), (0.075, 0.07, 0.036), mat="cuoio_scuro", bones=["Foot" + s])

# ---- bracers (glove cuffs) + rolled sleeves ----
for s, sx in ((".L", 1), (".R", -1)):
    d = V((ARM_D.x * sx, 0, ARM_D.z))
    W = V((WRI.x * sx, WRI.y, WRI.z))
    E = V((ELB.x * sx, ELB.y, ELB.z))
    B = ["LowerArm" + s, "Hand" + s]
    loft("V_bracciale" + s, [(W + d * 0.01, 0.034, 0.034, 0.034), (W - d * 0.03, 0.039, 0.039, 0.039),
                             (W.lerp(E, 0.45), 0.044, 0.044, 0.044), (W.lerp(E, 0.78), 0.05, 0.05, 0.05),
                             (W.lerp(E, 0.84), 0.053, 0.053, 0.053)], seg=14, mat="cuoio", bones=B)
    for t in (0.2, 0.55):
        p = W.lerp(E, t)
        tube("V_bracc_cinghia%d%s" % (int(t * 100), s), p - d * 0.007, p + d * 0.007, 0.042 + 0.006 * t, None, 14,
             "cuoio_scuro", B)
    torus("V_manica_rotolo" + s, E + d * 0.035, 0.044, 0.013, 16, 6, normal=d, mat="lino", bones=["LowerArm" + s, "UpperArm" + s])
# wrist gauge on her left forearm
d = ARM_D
up = V((math.sin(ARM_ANG), -0.55, math.cos(ARM_ANG))).normalized()
c = WRI.lerp(ELB, 0.42) + up * 0.043
tube("V_quadrante", c - up * 0.01, c + up * 0.008, 0.03, 0.03, 18, "ottone", ["LowerArm.L"])
tube("V_quadrante_vetro", c + up * 0.006, c + up * 0.011, 0.022, 0.022, 18, "verde_gemma", ["LowerArm.L"])
torus("V_quadrante_ghiera", c + up * 0.009, 0.026, 0.004, 18, 6, normal=up, mat="ottone", bones=["LowerArm.L"])

log("triangoli:", tri_count())
save()
render_viste("p04", viste=["fronte", "destra", "tre_quarti", "retro"])
