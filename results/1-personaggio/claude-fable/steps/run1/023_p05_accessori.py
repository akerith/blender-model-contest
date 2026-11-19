exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
M = materials()
random.seed(5)
RLEG, RBOOT = mspec(LEG), mspec(BOOT)

# ---- crossed straps on the chest ----
z1 = lambda a: 1.165 + 0.135 * math.cos(rad(a))
z2 = lambda a: 1.165 - 0.135 * math.cos(rad(a))
obj("cinghia_petto_1", g_belt(TORSO, z1, 0.030, off=0.008, thick=0.006, n=32), M["leather"], "Spine,Chest")
obj("cinghia_petto_2", g_belt(TORSO, z2, 0.030, off=0.011, thick=0.006, n=32), M["leather"], "Spine,Chest")
bk = [g_box(vpt(TORSO, 1.165, -90, 0.022), (0.040, 0.010, 0.046)),
      g_box(vpt(TORSO, 1.245, -90 + 38, 0.020), (0.030, 0.010, 0.034), rot=(0, 30, 30)),
      g_box(vpt(TORSO, 1.245, -90 - 38, 0.020), (0.030, 0.010, 0.034), rot=(0, -30, -30))]
# shirt showing at the neck (lighter, above the leather vest)
M["shirt"] = mat("camicia", "#7f8790", rough=0.9)
sh_ = [(z,) + tuple(vparams(TORSO, z)[1:3]) + tuple(x + 0.004 for x in vparams(TORSO, z)[3:]) for z in (1.262, 1.28, 1.32, 1.35, 1.365)]
sh_[-1] = (1.365, 0, 0.0, 0.058, 0.060, 0.056)
obj("camicia", g_vloft(sh_, n=18, cap0=False, cap1=False), M["shirt"], "Chest,Neck")
# ---- belts ----
obj("cintura", g_belt(TORSO, 1.035, 0.052, off=0.008, thick=0.009, n=28), M["leatherd"], "Spine,Hips")
zh = lambda a: 0.955 - 0.035 * math.cos(rad(a)) + 0.02 * math.sin(rad(a))
obj("cintura_bassa", g_belt(TORSO, zh, 0.030, off=0.006, thick=0.008, n=28), M["leather"], "Hips,Spine")
bk.append(g_box(vpt(TORSO, 1.035, -90, 0.022), (0.066, 0.010, 0.066)))
bk.append(g_box(vpt(TORSO, 0.945, -90 - 25, 0.018), (0.034, 0.010, 0.040), rot=(0, 0, -25)))
obj("fibbie", merge(bk), M["brass"], "Spine", smooth=False)
obj("fibbia_centro", g_box(vpt(TORSO, 1.035, -90, 0.026), (0.040, 0.010, 0.040)), M["leatherd"], "Spine", smooth=False)
# medallion hanging in the middle
mc = vpt(TORSO, 0.965, -90, 0.022)
obj("medaglione", merge(g_cyl(mc + Vector((0, 0.004, 0)), mc - Vector((0, 0.006, 0)), 0.026, n=12),
                        g_torus(mc - Vector((0, 0.006, 0)), (0, 1, 0), 0.017, 0.005, nseg=10, nside=4),
                        g_bar(mc + Vector((0, 0, 0.02)), mc + Vector((0, 0.004, 0.06)), 0.008, 0.004, up=(0, 1, 0))), M["brass"], "Hips")

# ---- right hip (-X): pouch, canister, coil of rope ----
pc = vpt(TORSO, 0.905, 180 + 12, 0.030)
obj("borsa", merge(g_sphere(pc, (0.045, 0.058, 0.062), seg=10, rings=8),
                   g_sphere(pc + Vector((-0.006, 0, 0.012)), (0.046, 0.060, 0.052), seg=10, rings=6)), M["leather"], "Hips")
obj("borsa_bottone", g_sphere(pc + Vector((-0.050, -0.004, -0.012)), 0.010, seg=6, rings=4), M["brass"], "Hips")
c0, c1 = Vector((-0.235, -0.050, 0.845)), Vector((-0.265, -0.062, 0.715))
ax = (c1 - c0).normalized()
can = [g_cyl(c0, c1, 0.036, n=12), g_torus(c0 + ax * 0.012, ax, 0.037, 0.007, nseg=12, nside=4),
       g_torus(c1 - ax * 0.012, ax, 0.037, 0.007, nseg=12, nside=4), g_cyl(c0 - ax * 0.022, c0, 0.022, n=10),
       g_torus(c0 - ax * 0.03, (0, 1, 0), 0.014, 0.004, nseg=8, nside=4)]
obj("barattolo", merge(can), M["brass"], "Hips", sharp=40)
obj("barattolo_vetro", g_cyl(c0 + ax * 0.035, c0 + ax * 0.095, 0.0375, n=12, cap0=False, cap1=False), M["glass"], "Hips")
obj("barattolo_cinghia", g_bar(c0 - ax * 0.03, vpt(TORSO, 0.96, 180 + 25, 0.012), 0.014, 0.005, up=(-1, 0, 0)), M["leather"], "Hips")
coil = []
cc = vpt(TORSO, 0.90, -90 - 42, 0.03)
nr = Vector((cc.x, cc.y - 0.02, 0)).normalized()
for k in range(4):
    c = cc + Vector((random.uniform(-0.012, 0.012), -0.006 * k, -0.105 - 0.012 * k)) + nr * (0.006 * k)
    n_ = (nr + Vector((random.uniform(-0.25, 0.25), random.uniform(-0.15, 0.15), 0))).normalized()
    coil.append(g_torus(c, n_, 0.048 + 0.004 * k, 0.0085, nseg=16, nside=5, Ry=0.125 + 0.012 * k))
coil.append(g_torus(cc + Vector((0, 0, 0.005)), (0, 0, 1), 0.024, 0.008, nseg=8, nside=4))
obj("corda_rotolo", merge(coil), M["rope"], "Hips")
# rope across from the belt, hanging in a curve at the front
rp = [vpt(TORSO, 1.01, -90 - 55, 0.02), vpt(TORSO, 0.95, -90 - 40, 0.035), vpt(TORSO, 0.90, -90 - 15, 0.04),
      vpt(TORSO, 0.93, -90 + 15, 0.035), vpt(TORSO, 1.00, -90 + 40, 0.02)]
obj("corda_davanti", g_rope(rp, 0.008, n=5, sub=3), M["rope"], "Hips")

# ---- left hip (+X): two long tubes and hanging rags ----
tubes, rings = [], []
for (p0, p1, r) in ((Vector((0.205, -0.065, 0.965)), Vector((0.245, -0.080, 0.560)), 0.031),
                    (Vector((0.255, -0.005, 0.940)), Vector((0.290, -0.010, 0.590)), 0.027)):
    a = (p1 - p0).normalized()
    L = (p1 - p0).length
    tubes.append(g_cyl(p0, p1, r, n=10))
    for t in (0.0, 0.06, 0.5, 0.94, 1.0):
        rings.append(g_torus(p0 + a * (L * t), a, r + 0.001, 0.006, nseg=10, nside=4))
    rings.append(g_sphere(p0 - a * 0.006, (r * 0.8, r * 0.8, r * 0.5), seg=8, rings=4))
    rings.append(g_bar(p0 + a * 0.02, vpt(TORSO, 1.02, -10 if r < 0.03 else -40, 0.012), 0.014, 0.005, up=(1, 0, 0)))
obj("tubi_fianco", merge(tubes), M["leather"], "Hips")
obj("tubi_fianco_anelli", merge(rings), M["brass"], "Hips", sharp=40)


def rag(p0, length, w, sway, name, bones, m):
    pts, rr = [], []
    n = 6
    for k in range(n + 1):
        t = k / n
        pts.append(Vector(p0) + Vector((sway[0] * t + 0.01 * math.sin(t * 7), sway[1] * t + 0.012 * math.sin(t * 5 + 1), -length * t)))
        rr.append(w * (1 - 0.35 * t) * random.uniform(0.75, 1.1) * (0.35 if k == n else 1))
    obj(name, g_loft([(p, r, 0.004) for p, r in zip(pts, rr)], n=4, ref=(1, 0, 0), sq=0.5), m, bones, sharp=30)


rag(vpt(TORSO, 1.01, -90 + 52, 0.016), 0.40, 0.034, (0.03, -0.01), "straccio_1", "Hips", M["linen"])
rag(vpt(TORSO, 1.01, -90 + 68, 0.018), 0.30, 0.026, (0.03, 0.0), "straccio_2", "Hips", M["linen"])
rag(vpt(TORSO, 1.01, 180 - 5, 0.014), 0.36, 0.030, (-0.035, 0.01), "straccio_3", "Hips", M["linen"])

# ---- legs: knee pad (right), wraps, straps ----
kp = vpt(RLEG, 0.535, -90, 0.0)
obj("ginocchiera", merge(g_sphere(kp + Vector((0, 0.012, 0)), (0.058, 0.034, 0.066), seg=10, rings=8),
                         g_sphere(kp + Vector((0, -0.012, 0)), (0.034, 0.02, 0.040), seg=8, rings=6)), M["leatherd"],
    "RightLowerLeg,RightUpperLeg")
st = [g_belt(RLEG, 0.495, 0.022, off=0.003, thick=0.006, n=12), g_belt(RLEG, 0.575, 0.022, off=0.003, thick=0.006, n=12),
      g_belt(RLEG, 0.70, 0.026, off=0.003, thick=0.006, n=12)]
obj("cinghie_gamba_R", merge(st), M["leather"], "RightUpperLeg,RightLowerLeg")
obj("cinghie_gamba_L", merge(g_belt(LEG, 0.555, 0.024, off=0.003, thick=0.006, n=12),
                             g_belt(LEG, 0.53, 0.02, off=0.003, thick=0.005, n=12)), M["leather"], "LeftUpperLeg,LeftLowerLeg")
obj("fasce_L", merge(g_belt(LEG, 0.462, 0.034, off=0.003, thick=0.006, n=12), g_belt(LEG, 0.492, 0.03, off=0.005, thick=0.006, n=12)),
    M["linen"], "LeftLowerLeg")
obj("fasce_R", g_belt(RLEG, 0.462, 0.034, off=0.003, thick=0.006, n=12), M["linen"], "RightLowerLeg")

# ---- boots: laces, straps, buckles ----
for side, sp, pre in (("L", BOOT, "Left"), ("R", RBOOT, "Right")):
    lace = []
    zs = [0.12 + 0.042 * k for k in range(6)]
    for za, zb in zip(zs, zs[1:]):
        lace.append(g_bar(vpt(sp, za, -90 - 20, 0.004), vpt(sp, zb, -90 + 20, 0.004), 0.007, 0.005, up=(0, -1, 0)))
        lace.append(g_bar(vpt(sp, za, -90 + 20, 0.004), vpt(sp, zb, -90 - 20, 0.004), 0.007, 0.005, up=(0, -1, 0)))
    obj("lacci_" + side, merge(lace), M["dark"], pre + "LowerLeg", smooth=False)
    obj("stivale_cinghie_" + side, merge(g_belt(sp, 0.105, 0.024, off=0.003, thick=0.006, n=12),
                                         g_belt(sp, 0.352, 0.024, off=0.003, thick=0.006, n=12)), M["leatherd"],
        "%sLowerLeg,%sFoot" % (pre, pre))
    sgn = 1 if side == "L" else -1
    obj("stivale_fibbie_" + side, merge(g_box(vpt(sp, 0.105, -90 + 70 * sgn, 0.011), (0.008, 0.024, 0.030)),
                                        g_box(vpt(sp, 0.352, -90 + 70 * sgn, 0.011), (0.008, 0.024, 0.030))), M["brass"],
        pre + "LowerLeg", smooth=False)

# ---- shells on the cape (left chest) ----
sh = []
for dx, dz, r, ang in ((0, 0, 0.022, 0), (0.026, -0.018, 0.017, 30), (-0.016, -0.026, 0.015, -25)):
    c = Vector((0.105 + dx, -0.112, 1.345 + dz))
    sh.append(g_sphere(c, (r, 0.008, r * 0.9), seg=8, rings=5))
obj("conchiglie", merge(sh), M["white"], "Chest")

save()
render_viste("p05", viste=["fronte", "destra", "sinistra"])
shot("p05_busto", (0, 0, 1.0), 0.8)
