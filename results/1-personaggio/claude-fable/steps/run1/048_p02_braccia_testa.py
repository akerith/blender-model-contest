exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
M = materials()
random.seed(7)
Y = (0, 1, 0)


def both(name, g, material, bones, **kw):
    """g is for the left side; bones may contain %s for Left/Right."""
    obj(name + "_L", g, material, bones.replace("%s", "Left"), **kw)
    obj(name + "_R", mirror(g), material, bones.replace("%s", "Right"), **kw)


def ap(s, y=0.0, n=0.0):
    """point along the left arm: s metres from the shoulder, y sideways, n along the back-of-hand normal"""
    return SH + AD * s + Vector((0, y, 0)) + AN * n


# ---- sleeves (linen, rolled at the elbow) ----
sl = [(ap(-0.035), 0.040, 0.040), (ap(0.0), 0.060, 0.060), (ap(0.06), 0.060, 0.057), (ap(0.14), 0.054, 0.052),
      (ap(0.185), 0.052, 0.050), (ap(0.19), 0.060, 0.058), (ap(0.235), 0.060, 0.058), (ap(0.245), 0.048, 0.046)]
both("manica", g_loft(sl, n=12, ref=Y), M["linen"], "%sUpperArm,%sShoulder,%sLowerArm")
# ---- forearm: long leather glove ----
fa = [(ap(0.235), 0.045, 0.043), (ap(0.25), 0.054, 0.052), (ap(0.27), 0.052, 0.050), (ap(0.34), 0.046, 0.043),
      (ap(0.41), 0.038, 0.034), (ap(0.445), 0.034, 0.029)]
both("guanto", g_loft(fa, n=12, ref=Y, cap1=False), M["leatherd"], "%sLowerArm,%sUpperArm,%sHand")
# straps on the forearm
st = merge(g_torus(ap(0.30), AD, 0.050, 0.006, nseg=12, nside=4), g_torus(ap(0.375), AD, 0.043, 0.006, nseg=12, nside=4))
both("guanto_cinghie", st, M["leather"], "%sLowerArm")
# ---- hand ----
w0 = L_UP + L_FORE
palm = [(ap(w0 - 0.01), 0.030, 0.024), (ap(w0 + 0.03), 0.042, 0.022), (ap(w0 + 0.065), 0.046, 0.019), (ap(w0 + 0.085), 0.044, 0.015)]
g = [g_loft(palm, n=10, ref=Y)]
HR_M = Matrix.Translation(WRI) @ Matrix.Rotation(rad(55), 4, AD) @ Matrix.Translation(-WRI)
fbones = {}
for fname, fy, fl in (("Index", -0.033, 0.062), ("Middle", -0.011, 0.072), ("Ring", 0.011, 0.068), ("Pinky", 0.032, 0.054)):
    b = ap(w0 + 0.078, fy)
    pts = [b, b + AD * (fl * 0.45) - AN * 0.002, b + AD * (fl * 0.8) - AN * 0.008, b + AD * fl - AN * 0.017]
    fg = g_loft([(pts[0], 0.011, 0.010), (pts[1], 0.0105, 0.0095), (pts[2], 0.0095, 0.0085), (pts[3], 0.007, 0.006)], n=6, ref=Y)
    both("dito_" + fname, xf(fg, HR_M), M["leatherd"], "%sHand" + fname + "1,%sHand")
    fbones[fname] = (HR_M @ pts[0], HR_M @ pts[3])
b = ap(w0 + 0.025, -0.036, -0.004)
td = (AD * 0.55 + Vector((0, -0.75, 0)) - AN * 0.25).normalized()
fg = g_loft([(b - td * 0.015, 0.015, 0.015), (b + td * 0.025, 0.0145, 0.0145), (b + td * 0.05, 0.012, 0.012), (b + td * 0.068, 0.008, 0.008)], n=6, ref=(0, 0, 1))
both("dito_Thumb", xf(fg, HR_M), M["leatherd"], "%sHandThumb1,%sHand")
fbones["Thumb"] = (HR_M @ b, HR_M @ (b + td * 0.068))
both("mano", rot_about(merge(g), WRI, AD, 55), M["leatherd"], "%sHand")
# finger bones (one per finger)
arm = bpy.data.objects["Scheletro"]
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
for fname, (h, t) in fbones.items():
    for pre, sx in (("Left", 1), ("Right", -1)):
        nm = pre + "Hand" + fname + "1"
        bn = eb.get(nm) or eb.new(nm)
        bn.head = (h.x * sx, h.y, h.z)
        bn.tail = (t.x * sx, t.y, t.z)
        bn.parent = eb[pre + "Hand"]
bpy.ops.object.mode_set(mode="OBJECT")
# ---- wrist device (left wrist): brass ring + green dial ----
dc = ap(0.40, 0, 0.040)
dev = merge(g_torus(ap(0.40), AD, 0.041, 0.010, nseg=14, nside=5),
            g_cyl(ap(0.40, 0, 0.030), ap(0.40, 0, 0.052), 0.030, n=12),
            g_torus(ap(0.40, 0, 0.052), AN, 0.026, 0.006, nseg=12, nside=4))
obj("bracciale", dev, M["brass"], "LeftLowerArm")
obj("bracciale_vetro", g_cyl(ap(0.40, 0, 0.050), ap(0.40, 0, 0.056), 0.023, n=12), M["glass"], "LeftLowerArm")
# right wrist: plain leather band with a small buckle
g = merge(g_torus(mirror(([ap(0.40)], []))[0][0], (-AD.x, 0, AD.z), 0.040, 0.008, nseg=12, nside=4))
obj("polsino_R", g, M["leather"], "RightLowerArm")

# ---- neck and head ----
obj("collo", g_loft([((0, 0.005, 1.30), 0.056, 0.056), ((0, 0.0, 1.38), 0.047, 0.050), ((0, -0.008, 1.45), 0.046, 0.050)], n=10,
                    axes=((1, 0, 0), (0, 1, 0))), M["skin"], "Neck,Head,Chest")
HEAD = [  # z, cx, cy, rx, ry_back, ry_front
    (1.424, 0, -0.054, 0.024, 0.030, 0.024),
    (1.434, 0, -0.045, 0.042, 0.056, 0.038),
    (1.457, 0, -0.030, 0.064, 0.086, 0.057),
    (1.492, 0, -0.020, 0.081, 0.102, 0.070),
    (1.535, 0, -0.014, 0.091, 0.110, 0.078),
    (1.580, 0, -0.012, 0.093, 0.113, 0.080),
    (1.620, 0, -0.010, 0.089, 0.110, 0.074),
    (1.650, 0, -0.008, 0.070, 0.090, 0.056),
    (1.668, 0, -0.006, 0.040, 0.054, 0.032),
]
obj("testa", g_vloft(HEAD, n=16), M["skin"], "Head")


def hp(z, ang, off=0.0):
    return vpt(HEAD, z, ang, off)


# nose
nose = [((0, -0.090, 1.592), 0.008, 0.007), ((0, -0.101, 1.562), 0.010, 0.009), ((0, -0.112, 1.538), 0.015, 0.012),
        ((0, -0.098, 1.524), 0.012, 0.005)]
ears = merge(g_sphere((0.092, 0.012, 1.548), (0.010, 0.017, 0.028), seg=8, rings=6),
             g_sphere((-0.092, 0.012, 1.548), (0.010, 0.017, 0.028), seg=8, rings=6))
obj("naso_orecchie", merge(g_loft(nose, n=8, ref=(1, 0, 0)), ears), M["skin"], "Head")
# eyes
ew, ir, lid, brow = [], [], [], []
for sx in (1, -1):
    ex = 0.035 * sx
    ey = hp(1.572, -90 + 22 * sx).y
    ew.append(g_sphere((ex, ey + 0.004, 1.572), (0.019, 0.007, 0.0105), seg=10, rings=6))
    ir.append(g_sphere((ex - 0.001 * sx, ey - 0.0015, 1.573), (0.0092, 0.004, 0.0095), seg=8, rings=6))
    lid.append(g_bar((ex - 0.018 * sx, ey + 0.001, 1.578), (ex, ey - 0.004, 1.582), 0.006, 0.004))
    lid.append(g_bar((ex, ey - 0.004, 1.582), (ex + 0.019 * sx, ey + 0.003, 1.577), 0.006, 0.004))
    b0 = hp(1.593, -90 + 9 * sx, 0.002)
    b1 = hp(1.602, -90 + 24 * sx, 0.003)
    b2 = hp(1.598, -90 + 38 * sx, 0.002)
    brow.append(g_bar(b0, b1, 0.008, 0.008))
    brow.append(g_bar(b1, b2, 0.007, 0.006))
obj("occhi_bianco", merge(ew), M["white"], "Head")
obj("occhi_iride", merge(ir), M["dark"], "Head")
obj("sopracciglia", merge(lid + brow), M["hair"], "Head", smooth=False)
# mouth
my = hp(1.500, -90).y
obj("labbra", merge(g_sphere((0, my + 0.003, 1.5035), (0.022, 0.006, 0.0045), seg=10, rings=6),
                    g_sphere((0, my + 0.004, 1.496), (0.017, 0.006, 0.0055), seg=10, rings=6)), M["lips"], "Head")

# ---- hair ----
HC = Vector((0, 0.012, 1.588))
HR = Vector((0.106, 0.124, 0.102))
gv, gf = g_sphere(HC, tuple(HR), seg=16, rings=10)
keep = []
for f in gf:
    c = sum((gv[i] for i in f), Vector()) / len(f)
    face = (c.y < -0.035 and c.z < 1.632) or c.z < 1.50
    if not face:
        keep.append(f)
obj("capelli_base", (gv, keep), M["hair"], "Head")


def tuft(az, el, length, droop, swirl, w=0.022, white=False, out=1.0):
    """az: 0=+X, 90=back, -90=front. el: elevation deg. returns loft geometry"""
    a, e = rad(az), rad(el)
    nrm = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    root = HC + Vector((nrm.x * HR.x, nrm.y * HR.y, nrm.z * HR.z)) * 0.93
    tang = Vector((-math.sin(a), math.cos(a), 0))
    pts = []
    for k in range(5):
        s = k / 4
        pts.append(root + nrm * (0.045 * out * s ** 0.7) + Vector((0, 0, -1)) * (droop * length * s * s)
                   + tang * (swirl * length * s) + nrm * (length * 0.35 * (1 - droop) * s))
    rr = [0.9, 1.25, 1.15, 0.85, 0.3]
    return g_loft([(p, w * r, w * 0.6 * r) for p, r in zip(pts, rr)], n=6, ref=tuple(tang))


dark, white = [], []
# crown and sides: rows of locks
for el, cnt, ln, dr in ((72, 6, 0.06, 0.2), (48, 10, 0.08, 0.45), (22, 12, 0.09, 0.8), (-4, 11, 0.085, 1.0), (-26, 8, 0.07, 1.0)):
    for k in range(cnt):
        az = 360 * k / cnt + random.uniform(-10, 10) + el
        azn = (az + 90 + 180) % 360 - 180   # 0 = front
        if abs(azn) < 62 and el < 60:
            continue                    # the fringe is made below
        if el < 10 and abs(azn) < 85:
            continue
        g = tuft(az, el + random.uniform(-6, 6), ln * random.uniform(0.85, 1.2), dr, random.uniform(-0.6, 0.6),
                 w=random.uniform(0.028, 0.036))
        dark.append(g)
# fringe: starts high on the forehead and sweeps sideways, the face stays free
for az, el, sw, wh in ((-128, 40, -1.1, True), (-112, 47, -1.0, True), (-97, 50, -0.9, False), (-82, 50, 0.9, False),
                       (-66, 46, 1.0, False), (-50, 40, 1.1, False), (-142, 32, -0.8, False), (-104, 62, -0.8, True),
                       (-76, 62, 0.7, False), (-36, 30, 0.8, False), (-152, 20, -0.5, False), (-28, 18, 0.5, False)):
    g = tuft(az, el, random.uniform(0.07, 0.115), random.uniform(0.5, 0.95), sw * random.uniform(0.5, 1.0), w=0.034, out=0.75)
    (white if wh else dark).append(g)
obj("capelli_ciocche", merge(dark), M["hair"], "Head")
obj("capelli_ciocca_bianca", merge(white), M["hairw"], "Head")

save()
shot("p02_viso", (0, 0, 1.55), 0.42)
shot("p02_viso_lato", (0, 0, 1.55), 0.42, d=(1, -0.6, 0.1))
