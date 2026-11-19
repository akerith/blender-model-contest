# GROUP 3 - neck, shirt collar, stand-up cape collar
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
set_mat("camicia_collo", (0.30, 0.33, 0.38), 0.85)
set_mat("mantello_rev", (0.22, 0.34, 0.31), 0.9)

# neck: 0.11 wide
nk = obj("Collo")
for v in nk.data.vertices:
    v.co.x *= 0.93
    v.co.y = 0.005 + (v.co.y - 0.005) * 0.93
nk.data.update()

# shirt collar: high, wrapped around the neck, 1.41 -> 1.46, small V opening at the front
rings = []
for z, rx, rf, rb in ((1.41, 0.072, 0.066, 0.070), (1.435, 0.064, 0.060, 0.066), (1.46, 0.062, 0.059, 0.066)):
    rings.append(((0, 0.006, z), rx, rf, rb))
sc = loft("Colletto_camicia", rings, seg=24, cap=(False, False), mat=bpy.data.materials["camicia_collo"],
          arc=(math.radians(-82), math.radians(262)), up=V((0, 1, 0)))
solidify(sc, 0.004, 1.0)
bind(sc, ["Chest", "Neck"])

# stand-up cape collar: back and sides of the neck, open at the front, leaning out a little
NS = 26
verts, faces = [], []
rows = [(0.0,), (0.5,), (1.0,)]
for r, (t,) in enumerate(rows):
    for k in range(NS + 1):
        u = k / NS
        th = math.radians(-145 + 290 * u)       # 0 = back (+Y)
        ztop = 1.52 - 0.04 * (abs(th) / math.radians(145)) ** 1.5
        z = 1.415 + (ztop - 1.415) * t
        rx = 0.100 + 0.022 * t
        ry = 0.092 + 0.040 * t
        x = math.sin(th) * rx
        y = 0.008 + math.cos(th) * ry
        verts.append(V((x, y, z)))
W = NS + 1
for r in range(len(rows) - 1):
    for k in range(NS):
        a = r * W + k
        faces.append((a, a + 1, a + 1 + W, a + W))
cc = mesh_obj("Colletto_mantello", verts, faces, bpy.data.materials["mantello_rev"], True)
solidify(cc, 0.008, 1.0)
bind(cc, ["Chest", "Neck"])

for nm in ("Collo", "Colletto_camicia", "Colletto_mantello"):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
finish(3)
render_parte("rev_3_collo", ["Testa", "Capelli", "Collo", "Colletto", "Busto"], ["fronte", "retro", "tre_quarti"])
