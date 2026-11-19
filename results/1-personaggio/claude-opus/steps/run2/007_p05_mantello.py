exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
random.seed(21)
clear("M_")
get_mat("mantello_medio", (0.17, 0.21, 0.18), 0.9, 0.0)

SEG = 64
TOP = [(1.545, 0.070, 0.066, 0.076, 0.014, -66, 246), (1.50, 0.078, 0.074, 0.084, 0.012, -64, 244),
       (1.455, 0.115, 0.090, 0.100, 0.006, -58, 238), (1.425, 0.195, 0.105, 0.118, 0.002, -46, 226),
       (1.37, 0.228, 0.118, 0.137, 0.010, -32, 212), (1.29, 0.248, 0.122, 0.155, 0.024, -14, 194)]
NLOW = 11
# bottom height per column: zigzag torn strips
bottom = []
for k in range(SEG + 1):
    u = k / SEG
    ang = math.radians(-14 + 208 * u)
    side = abs(math.cos(ang))  # 0 at back, 1 at the sides
    b = 0.215 + 0.06 * side + 0.04 * math.sin(u * 17.0)
    b += random.uniform(0.0, 0.05) if k % 2 == 0 else random.uniform(0.05, 0.15)
    if random.random() < 0.12:
        b += 0.12  # deeper rip
    bottom.append(b)

verts, faces, rowfrac = [], [], []
nrows = len(TOP) + NLOW
for r in range(nrows):
    for k in range(SEG + 1):
        u = k / SEG
        if r < len(TOP):
            z, rx, rf, rb, yo, a0, a1 = TOP[r]
            s = 0.0
        else:
            s = (r - len(TOP) + 1) / NLOW
            z = 1.29 + (bottom[k] - 1.29) * s
            rx = 0.248 + (0.43 - 0.248) * s ** 0.9
            rf = 0.122
            rb = 0.155 + (0.27 - 0.155) * s
            yo = 0.024 + (0.115 - 0.024) * s
            a0 = -14 + 16 * s
            a1 = 194 - 16 * s
        ang = math.radians(a0 + (a1 - a0) * u)
        amp = 0.10 * s ** 0.8
        f = 1.0 + amp * math.sin(ang * 9 + 0.6) + amp * 0.4 * math.sin(ang * 23 + 1.3)
        sn = math.sin(ang)
        x = -math.cos(ang) * rx * f
        y = yo + sn * (rb if sn > 0 else rf) * f
        verts.append(V((x, y, z)))
    rowfrac.append(0.0)
W = SEG + 1
mi = []
for r in range(nrows - 1):
    for k in range(SEG):
        a = r * W + k
        faces.append((a, a + 1, a + 1 + W, a + W))
        s = max(0.0, (r - len(TOP) + 1.5) / NLOW)
        if s > 0.80:
            mi.append(2)
        elif s > 0.62 and random.random() < 0.85:
            mi.append(1)
        elif s > 0.5 and random.random() < 0.3:
            mi.append(1)
        else:
            mi.append(0)

# a few holes near the bottom
drop = set()
for _ in range(14):
    r = random.randint(nrows - 5, nrows - 3)
    k = random.randint(2, SEG - 3)
    drop.add(r * SEG + k)
faces2 = [f for i, f in enumerate(faces) if i not in drop]
mi2 = [m for i, m in enumerate(mi) if i not in drop]
cape = mesh_obj("M_mantello", verts, faces2, "mantello", True,
                ["Chest", "Spine", "Hips", "Neck", "Shoulder.L", "Shoulder.R"])
cape.data.materials.append(bpy.data.materials["mantello_medio"])
cape.data.materials.append(M("mantello_sporco"))
for p, m in zip(cape.data.polygons, mi2):
    p.material_index = m
solidify(cape, 0.007, 0.0)

# shell ornaments on her left shoulder (front)
for i, (dx, dz) in enumerate([(0.0, 0.0), (0.03, -0.025), (-0.022, -0.035)]):
    c = V((0.13 + dx, -0.115, 1.385 + dz))
    sphere("M_conchiglia%d" % i, c, 0.016, 10, 5, scale=(1.0, 0.45, 0.85), mat="lino", bones=["Chest"],
           rot=Matrix.Rotation(math.radians(20 * i), 3, "Y"))
    for j in range(3):
        box("M_conch_riga%d_%d" % (i, j), c + V(((j - 1) * 0.008, -0.006, 0)), (0.0025, 0.004, 0.022), mat="cuoio",
            bones=["Chest"], rot=Matrix.Rotation(math.radians((j - 1) * 25 + 20 * i), 3, "Y"))
# collar clasp
sphere("M_fermaglio", (0.0, -0.075, 1.44), 0.012, 10, 6, scale=(1, 0.5, 1), mat="ottone", bones=["Chest"])

log("triangoli:", tri_count())
save()
render_viste("p05b", viste=["fronte", "destra", "retro", "tre_quarti"])
