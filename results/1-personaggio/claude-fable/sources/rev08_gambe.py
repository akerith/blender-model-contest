exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 8 - legs and boots
C = bpy.data.objects["Corpo"]
me = C.data
mat("lacci", lin((0.55, 0.42, 0.28)), 0.0, 0.8)
RL, RB = mspec(NLEG), mspec(NBOOT)
ISL = islands(C)
# 8.2 knee pad: the round-1 pad (right knee) re-shaped to 0.11 across, 0.025 thick, centre Z 0.50; left one added
pad = [i for isl in ISL if isl["mat"] == "cuoio_scuro" and isl["c"].x < -0.04 and 0.42 < isl["c"].z < 0.58
       and isl["hi"].z - isl["lo"].z > 0.05 and isl["hi"].x - isl["lo"].x < 0.125 and isl["c"].y < -0.02 for i in isl["v"]]
kx = vparams(NLEG, 0.50)[1]
ky = -vparams(NLEG, 0.50)[5]
log("knee pad verts:", len(pad), "leg centre x %.3f front y %.3f" % (kx, ky))
if pad:
    affine(C, pad, (-kx - 0.055, ky - 0.030, 0.445), (-kx + 0.055, ky + 0.012, 0.555))
    s = set(pad)
    remap = {i: k for k, i in enumerate(pad)}
    vs = [Vector((-me.vertices[i].co.x, me.vertices[i].co.y, me.vertices[i].co.z)) for i in pad]
    fs = [tuple(reversed([remap[v] for v in p.vertices])) for p in me.polygons if all(v in s for v in p.vertices)]
    new("ginocchiera_L", (vs, fs), "cuoio_scuro", 0)
new("ginocchiera_cinghie_L", [g_belt(NLEG, 0.452, 0.020, off=0.004, thick=0.005, n=12), g_belt(NLEG, 0.548, 0.020, off=0.004, thick=0.005, n=12)],
    "cuoio", 0)
# 8.1 creases at the back of the knee
cr = []
for sp in (NLEG, RL):
    for z, w in ((0.468, 26), (0.49, 32), (0.512, 24)):
        cr.append(g_bar(vpt(sp, z, 90 - w, 0.0015), vpt(sp, z + 0.004, 90, 0.003), 0.005, 0.003, up=(0, 1, 0)))
        cr.append(g_bar(vpt(sp, z + 0.004, 90, 0.003), vpt(sp, z, 90 + w, 0.0015), 0.005, 0.003, up=(0, 1, 0)))
new("pieghe_ginocchio", cr, "scuro", 0, smooth=False)
# 8.3 shin wraps: 3 overlapping cream rings between 0.40 and 0.46 on each leg
for isl in ISL:
    if isl["mat"] == "lino" and isl["c"].z < 0.6 and abs(isl["c"].x) < 0.2 and isl["hi"].z - isl["lo"].z < 0.06:
        dz = -0.012 if isl["c"].x > 0 else -0.033
        move(C, isl["v"], lambda p, dz=dz: p + Vector((0, 0, dz)))
wr = [g_belt(NLEG, lambda a: 0.412 + 0.006 * math.sin(rad(a)), 0.026, off=0.007, thick=0.005, n=12),
      g_belt(RL, lambda a: 0.433 + 0.006 * math.sin(rad(a + 40)), 0.026, off=0.008, thick=0.005, n=12),
      g_belt(RL, lambda a: 0.453 - 0.005 * math.sin(rad(a)), 0.024, off=0.006, thick=0.005, n=12)]
new("fasce_nuove", wr, "lino", 0)
# 8.4 boots: straps at the ankle (0.09) and under the cuff, 8 crossed tan laces + eyelets
n_st = 0
for isl in ISL:
    c = isl["c"]
    if isl["mat"] in ("cuoio_scuro", "ottone") and 0.31 < c.z < 0.365 and abs(c.x) < 0.25 and isl["hi"].z - isl["lo"].z < 0.05:
        move(C, isl["v"], lambda p: p + Vector((0, 0, 0.022)))
        n_st += 1
lace = set()
for isl in ISL:
    if isl["mat"] == "scuro" and len(isl["v"]) == 8 and isl["c"].z < 0.42:
        lace.update(isl["v"])
        move(C, isl["v"], lambda p: Vector((p.x, p.y - 0.001, 0.10 + (p.z - 0.11) * (0.1875 / 0.21))))
me.materials.append(bpy.data.materials["lacci"])
li = len(me.materials) - 1
for p in me.polygons:
    if all(v in lace for v in p.vertices):
        p.material_index = li
log("boot straps moved:", n_st, "old lace vertices:", len(lace))
nl, ey = [], []
for sp in (NBOOT, RB):
    for za, zb in ((0.2875, 0.325), (0.325, 0.3625), (0.3625, 0.40)):
        nl.append(g_bar(vpt(sp, za, -110, 0.004), vpt(sp, zb, -70, 0.004), 0.006, 0.004, up=(0, -1, 0)))
        nl.append(g_bar(vpt(sp, za, -70, 0.004), vpt(sp, zb, -110, 0.004), 0.006, 0.004, up=(0, -1, 0)))
    for k in range(9):
        for a in (-110, -70):
            ey.append(g_sphere(vpt(sp, 0.10 + 0.0375 * k, a, 0.003), 0.0045, seg=4, rings=2))
new("lacci_nuovi", nl, "lacci", 0, smooth=False)
new("occhielli", ey, "ottone", 0)
for nm in ("cuoio", "pantaloni"):
    idx = [i for isl in ISL if isl["mat"] == nm and isl["c"].z < 0.9 and abs(isl["c"].x) > 0.03 and abs(isl["c"].x) < 0.2 and isl["c"].z < 0.5 for i in isl["v"]]
    if idx:
        lo, hi = bbox(C, idx)
        log(nm, "below the knee:", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
salva()
render_viste("rev_8", viste=["fronte", "retro", "destra"])
shot("rev_8_gambe", (0, 0, 0.32), 0.72)
shot("rev_8_gambe_3q", (0, 0, 0.32), 0.75, d=(0.8, -1, 0.25))
