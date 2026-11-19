exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 4 - torso: jacket seams, tunic skirt, straps, belts, medallion
random.seed(4)
C = "Corpo"
# 4.3 crossed straps (existing loops): ends at 1.41 / 1.04, crossing at 1.25
idx = [i for isl in islands(bpy.data.objects[C]) if isl["mat"] == "cuoio" and isl["hi"].z - isl["lo"].z > 0.25
       and abs(isl["c"].x) < 0.05 and 1.1 < isl["c"].z < 1.35 for i in isl["v"]]
ZS = [(1.00, 0.97), (1.08, 1.04), (1.215, 1.25), (1.40, 1.41), (1.45, 1.46)]
log("cross straps verts:", move(C, idx, lambda p: Vector((p.x, p.y, interp(ZS, p.z)))))
idx = pick(C, "ottone", lo=(-0.2, -0.2, 1.25), hi=(0.2, 0, 1.36))       # their buckles: 0.03 x 0.03 at 1.30
log("strap buckles verts:", move(C, idx, lambda p: Vector((p.x, p.y - 0.004, p.z - 0.008))))
# 4.4 horizontal strap under the breasts (new)
new("cinghia_orizzontale", g_belt(NB, 1.20, 0.030, off=0.007, thick=0.006, n=28), "cuoio", 0)
# 4.5 main belt buckle: 0.07 x 0.05, frame + pin
idx = pick(C, "ottone", lo=(-0.03, -0.25, 1.04), hi=(0.03, -0.06, 1.13))
if idx:
    lo, hi = bbox(C, idx)
    affine(C, idx, (-0.035, lo.y, 1.065), (0.035, hi.y, 1.115))
idx = pick(C, "cuoio_scuro", lo=(-0.03, -0.25, 1.04), hi=(0.03, -0.085, 1.13))
if idx:
    lo, hi = bbox(C, idx)
    affine(C, idx, (-0.025, lo.y, 1.075), (0.025, hi.y, 1.105))
    new("fibbia_perno", g_bar((-0.03, lo.y - 0.003, 1.09), (0.012, lo.y - 0.003, 1.09), 0.006, 0.005, up=(0, 1, 0)), "ottone", 0, smooth=False)
# 4.6 lower hip belt: higher on her left (1.00 at x +0.17), lower on her right (0.94 at x -0.17), 0.04 high
idx = pick(C, "cuoio", lo=(-0.05, -0.05, 0.93), hi=(0.05, 0.05, 1.07))
lo, hi = bbox(C, idx)
log("low belt before", round(lo.z, 3), round(hi.z, 3), "verts", len(idx))
f_low = lambda p: Vector((p.x, p.y, p.z - 0.0375 + 0.3676 * p.x))
move(C, idx, f_low)
vv = bpy.data.objects[C].data.vertices
for k in range(0, len(idx) - 3, 4):          # the belt is built in columns of 4 vertices: make it 0.04 high
    zc = sum(vv[i].co.z for i in idx[k:k + 4]) / 4
    for i in idx[k:k + 4]:
        vv[i].co.z = zc + (vv[i].co.z - zc) * 1.33
move(C, pick(C, "ottone", lo=(-0.25, -0.25, 0.94), hi=(0.0, 0.0, 1.04)), f_low)
# 4.7 medallion: 0.04 across, centre at Z 0.99, on a short cord under the buckle
F = "Fianchi"
idx = pick(F, "ottone", lo=(-0.04, -0.25, 0.97), hi=(0.04, -0.07, 1.10))
if idx:
    lo, hi = bbox(F, idx)
    cx = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z + 0.026))
    move(F, idx, lambda p: Vector((p.x * 0.78, cx.y + (p.y - cx.y) * 0.8, 0.99 + (p.z - cx.z) * 0.78)))
    log("medallion box", [round(x, 3) for x in bbox(F, idx)[0]], [round(x, 3) for x in bbox(F, idx)[1]])
# 4.1 vertical seam lines on the front of the jacket (thin dark grooves)
seams = []
for a in (-90 - 52, -90 - 26, -90 - 9, -90 + 9, -90 + 26, -90 + 52):
    zz = [1.125 + 0.05 * k for k in range(6)]
    for za, zb in zip(zz, zz[1:]):
        seams.append(g_bar(vpt(NB, za, a, 0.0068), vpt(NB, zb, a, 0.0068), 0.004, 0.003, up=(0, -1, 0)))
new("giacca_cuciture", seams, "scuro", 0, smooth=False)
# 4.2 tunic skirt: front and back panels from 1.06 to 0.80, open on the sides, 0.38 wide, uneven edge
panels = []
for a0 in (-90, 90):
    NCc, NRr = 12, 5
    vs, fs = [], []
    for i in range(NCc + 1):
        a = a0 - 66 + 132 * i / NCc
        zb = 0.80 + random.uniform(-0.028, 0.03) + (0.02 if i in (0, NCc) else 0)
        for r in range(NRr + 1):
            t = r / NRr
            z = 1.06 - t * (1.06 - zb)
            p = vpt(NB, max(z, 0.90), a, 0.010 + 0.022 * t + 0.006 * math.sin(i * 2.1) * t)
            vs.append(Vector((p.x * (1 + 0.10 * t), p.y, z)))
    for i in range(NCc):
        for r in range(NRr):
            q = (i * (NRr + 1) + r, (i + 1) * (NRr + 1) + r, (i + 1) * (NRr + 1) + r + 1, i * (NRr + 1) + r + 1)
            fs.append(q if a0 < 0 else q)
    panels.append((vs, fs))
g = merge(*panels)
o = new("tunica_gonna", dbl(g), "tunica", 0, sharp=60)
lo, hi = bbox(o)
log("skirt box", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
salva()
render_viste("rev_4", viste=["fronte", "retro", "sinistra"])
shot("rev_4_busto", (0, 0, 1.15), 0.75)
shot("rev_4_busto_3q", (0, 0, 1.15), 0.8, d=(0.7, -1, 0.2))
