exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 2 - head, face, hair: existing pieces moved / scaled, new hair clumps added
random.seed(21)
T = bpy.data.objects["Testa"]
n_eye = 0
for isl in islands(T):
    c, mt = isl["c"], isl["mat"]
    if mt in ("bianco", "iride") or (mt == "capelli" and len(isl["v"]) <= 8 and c.y < -0.05):
        sg = 1 if c.x > 0 else -1     # eyes 0.065 apart, set a little into the face
        move(T, isl["v"], lambda p, sg=sg: p + Vector((0.0045 * sg, 0.0025 if mt != "capelli" else 0.0, 0)))
        n_eye += 1
    elif mt == "labbra":              # mouth 0.045 wide, flatter (closed straight line)
        move(T, isl["v"], lambda p: Vector((p.x * 1.28, p.y, 1.505 + (p.z - 1.505) * 0.8)))
log("face pieces moved:", n_eye)
lo, hi = bbox(T)
log("head box", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
for mt in ("pelle", "bianco", "labbra"):
    idx = pick(T, mt)
    if idx:
        l2, h2 = bbox(T, idx)
        log(mt, [round(x, 3) for x in l2], [round(x, 3) for x in h2])


def clump(p0, p1, bend=(0, 0, 0), w=0.015, n=6):
    p0, p1, bend = Vector(p0), Vector(p1), Vector(bend)
    pts = [p0.lerp(p1, k / 4) + bend * (4 * (k / 4) * (1 - k / 4)) for k in range(5)]
    rr = [0.75, 1.15, 1.0, 0.65, 0.12]
    return g_loft([(p, w * r, w * 0.65 * r) for p, r in zip(pts, rr)], n=n, ref=(0.3, 0.5, 0.8))


HCN, HRN = Vector((0, 0.012, 1.60)), Vector((0.090, 0.122, 0.093))


def E(az, el, k=1.0):
    a, e = rad(az), rad(el)
    return HCN + Vector((HRN.x * math.cos(e) * math.cos(a), HRN.y * math.cos(e) * math.sin(a), HRN.z * math.sin(e))) * k


dark, white = [], []
# white streak: from the parting (x -0.03) back and to the right over the top of the head
white.append(clump((-0.028, -0.092, 1.668), (-0.040, -0.020, 1.700), (0, 0, 0.012), 0.015))
white.append(clump((-0.036, -0.035, 1.694), (-0.058, 0.055, 1.688), (0, 0, 0.010), 0.015))
white.append(clump((-0.050, 0.035, 1.690), (-0.066, 0.105, 1.650), (0, 0.01, 0.008), 0.013))
white.append(clump((-0.030, -0.094, 1.672), (-0.060, -0.104, 1.618), (-0.006, -0.012, 0), 0.013))
# locks falling on the forehead, down to just above the eyebrows
for x, zb, sw in ((0.004, 1.612, 0.012), (0.034, 1.608, 0.016), (0.060, 1.604, 0.012), (-0.012, 1.616, -0.012), (0.078, 1.59, 0.006)):
    p0 = E(-90 + x * 420, 52)
    dark.append(clump(p0, (x + sw, hi.y * 0 - 0.100 + abs(x) * 0.25, zb), (0, -0.016, 0.004), random.uniform(0.012, 0.016)))
# sides: cover the ears, end at jaw height 1.50
for sg in (1, -1):
    for az, zb, ln in ((-25, 1.500, 0.012), (8, 1.505, 0.016), (35, 1.495, 0.012)):
        p0 = E(90 - sg * (90 - az), 18)
        p1 = E(90 - sg * (90 - az), -60, 1.04)
        p1.z = zb
        dark.append(clump(p0, p1, (sg * 0.012, 0, 0), random.uniform(0.013, 0.017)))
# nape: uneven points ending around 1.48
for az, zb in ((58, 1.492), (74, 1.478), (90, 1.486), (106, 1.474), (122, 1.490)):
    p0 = E(az, 5)
    p1 = E(az, -62, 1.02)
    p1.z = zb
    dark.append(clump(p0, p1, (0, 0.014, 0), random.uniform(0.013, 0.017)))
# top: thick messy clumps standing up to 1.70
for az, el, d in ((20, 62, 0.05), (95, 58, 0.06), (160, 60, 0.05), (-60, 66, 0.045), (60, 40, 0.06), (130, 38, 0.06)):
    p0 = E(az, el, 0.92)
    a = rad(az + random.uniform(-40, 40))
    p1 = E(az, el - 22, 1.08) + Vector((math.cos(a), math.sin(a), 0)) * 0.02
    dark.append(clump(p0, p1, (0, 0, 0.022), random.uniform(0.014, 0.018)))
new("capelli_ciocche_nuove", dark, "capelli", 4, sharp=80)
new("ciocca_bianca_nuova", white, "capelli_bianchi", 4, sharp=80)
log("new clumps: dark", len(dark), "white", len(white))
salva()
render_viste("rev_2", viste=["fronte", "retro", "destra"])
shot("rev_2_viso", (0, 0, 1.585), 0.34)
shot("rev_2_viso_lato", (0, 0, 1.585), 0.34, d=(-1, -0.7, 0.15))
shot("rev_2_nuca", (0, 0, 1.585), 0.34, d=(0.3, 1, 0.5))
