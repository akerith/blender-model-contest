exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
M = materials()
M["hose"] = mat("tubo", "#4a3526", rough=0.55)
random.seed(3)
B = "Chest"
HC = Vector((0, 0.275, 1.315))
R = Vector((0.150, 0.132, 0.152))


def on(az, el, k=1.0):
    """point on the helmet. az: 0=+X, 90=+Y (looking away from the body). el elevation"""
    a, e = rad(az), rad(el)
    return HC + Vector((R.x * math.cos(e) * math.cos(a), R.y * math.cos(e) * math.sin(a), R.z * math.sin(e))) * k


def nrm(az, el):
    a, e = rad(az), rad(el)
    return Vector((math.cos(e) * math.cos(a) / R.x, math.cos(e) * math.sin(a) / R.y, math.sin(e) / R.z)).normalized()


def rivets(pts, r=0.008):
    return merge([g_sphere(p, r, seg=6, rings=4) for p in pts])


obj("elmo", g_sphere(HC, tuple(R), seg=20, rings=12), M["brass"], B)
dark, brass, glass = [], [], []
# big front porthole (looks backwards), with a grille
pc = on(90, 5, 1.0)
brass.append(g_cyl(pc - Vector((0, 0.02, 0)), pc + Vector((0, 0.022, 0)), 0.082, n=20))
brass.append(g_torus(pc + Vector((0, 0.024, 0)), (0, 1, 0), 0.074, 0.013, nseg=20, nside=6))
glass.append(g_cyl(pc + Vector((0, 0.018, 0)), pc + Vector((0, 0.027, 0)), 0.064, n=20))
for o in (-0.022, 0.022):
    dark.append(g_bar(pc + Vector((o, 0.031, -0.062)), pc + Vector((o, 0.031, 0.062)), 0.007, 0.007, up=(0, 1, 0)))
    dark.append(g_bar(pc + Vector((-0.062, 0.031, o)), pc + Vector((0.062, 0.031, o)), 0.007, 0.007, up=(0, 1, 0)))
brass.append(rivets([pc + Vector((0.074 * math.cos(rad(a)), 0.038, 0.074 * math.sin(rad(a)))) for a in range(15, 360, 30)], 0.007))
# side portholes
for sx in (1, -1):
    c = on(90 - 88 * sx, 8)
    ax = Vector((sx, 0.05, 0.1)).normalized()
    brass.append(g_cyl(c - ax * 0.02, c + ax * 0.014, 0.050, n=14))
    brass.append(g_torus(c + ax * 0.015, ax, 0.044, 0.009, nseg=14, nside=5))
    glass.append(g_cyl(c + ax * 0.012, c + ax * 0.02, 0.038, n=14))
    dark.append(g_bar(c + ax * 0.023 + Vector((0, 0, -0.036)), c + ax * 0.023 + Vector((0, 0, 0.036)), 0.006, 0.006, up=ax))
    dark.append(g_bar(c + ax * 0.023 + Vector((0, -0.036, 0)), c + ax * 0.023 + Vector((0, 0.036, 0)), 0.006, 0.006, up=ax))
# top: small porthole / valve
tc = on(90, 62)
tn = nrm(90, 62)
brass.append(g_cyl(tc - tn * 0.015, tc + tn * 0.016, 0.040, n=12))
glass.append(g_cyl(tc + tn * 0.014, tc + tn * 0.021, 0.029, n=12))
brass.append(g_torus(tc + tn * 0.017, tn, 0.034, 0.008, nseg=12, nside=5))
# crest band over the top (from front to back) and band around
band = []
for el in range(-40, 221, 20):
    band.append(on(0, 0) * 0 + HC + Vector((0, R.y * math.cos(rad(el)), R.z * math.sin(rad(el)))) * 1.012)
brass.append(g_loft([(p, 0.022, 0.006) for p in band if (p - pc).length > 0.09 and (p - tc).length > 0.045], n=6, ref=(1, 0, 0)) if False else ([], []))
# neck ring (bottom) + breastplate flange
zb = HC.z - 0.118
brass.append(g_torus((HC.x, HC.y, zb), (0, 0, 1), 0.105, 0.019, nseg=20, nside=6, Ry=0.094))
fl = [((HC.x, HC.y, zb - 0.012), 0.112, 0.100), ((HC.x, HC.y - 0.004, zb - 0.045), 0.150, 0.118), ((HC.x, HC.y - 0.006, zb - 0.062), 0.158, 0.122)]
obj("elmo_colletto", g_loft(fl, n=20, cap0=False, cap1=True, axes=((1, 0, 0), (0, -1, 0))), M["brassd"], B)
brass.append(rivets([Vector((HC.x + 0.150 * math.cos(rad(a)), HC.y - 0.004 + 0.118 * math.sin(rad(a)), zb - 0.046)) for a in range(0, 360, 30)], 0.008))
# valve knobs on the sides (back of the helmet, near the porthole)
for sx in (1, -1):
    c = on(90 - 42 * sx, -28)
    n_ = nrm(90 - 42 * sx, -28)
    brass.append(g_cyl(c - n_ * 0.01, c + n_ * 0.030, 0.020, n=10))
    brass.append(g_cyl(c + n_ * 0.030, c + n_ * 0.040, 0.027, n=10))
# rivets around the equator band
brass.append(g_torus(HC + Vector((0, 0, -0.065)), (0, 0, 1), R.x * 0.915, 0.008, nseg=20, nside=4, Ry=R.y * 0.915))
obj("elmo_ottone", merge(brass), M["brassd"], B, sharp=40)
obj("elmo_vetro", merge(glass), M["glass"], B, sharp=40)
obj("elmo_griglie", merge(dark), M["brassd"], B, smooth=False)

# ---- hoses: from the helmet sides down, looping under the bedroll ----
hoses = []
for sx in (1, -1):
    s0 = on(90 - 70 * sx, -35)
    pts = [s0, s0 + Vector((0.06 * sx, 0.02, -0.07)), Vector((0.155 * sx, 0.30, 1.08)), Vector((0.150 * sx, 0.31, 0.98)),
           Vector((0.10 * sx, 0.32, 0.92)), Vector((0.03 * sx, 0.31, 0.93)), Vector((0.02 * sx, 0.29, 1.00)), Vector((0.03 * sx, 0.27, 1.07))]
    hoses.append(g_rope(pts, 0.015, n=6, sub=3))
    # hose ends: brass couplings
    brass2 = g_cyl(s0 - (pts[1] - s0).normalized() * 0.01, s0 + (pts[1] - s0).normalized() * 0.03, 0.021, n=8)
    hoses_c = brass2
    obj("tubo_raccordo_%s" % ("L" if sx > 0 else "R"), hoses_c, M["brassd"], B)
obj("tubi", merge(hoses), M["hose"], B)
# coiled hose hanging at the left side (as in the side view)
coil = []
cc = Vector((0.175, 0.255, 1.03))
pts = []
for k in range(0, 29):
    a = rad(k * 30)
    rr = 0.062 - 0.0014 * k
    pts.append(cc + Vector((0.004 * k * 0.25, rr * math.cos(a), rr * math.sin(a))))
obj("tubo_spirale", g_rope(pts, 0.012, n=6, sub=1), M["hose"], B)

# ---- bedroll under the helmet ----
by, bz = 0.262, 1.075
roll = [((-0.135, by, bz), 0.040, 0.040), ((-0.125, by, bz), 0.058, 0.058), ((0.125, by, bz), 0.058, 0.058), ((0.135, by, bz), 0.040, 0.040)]
obj("rotolo", g_loft(roll, n=12, ref=(0, 1, 0)), M["linen"], B)
obj("rotolo_cinghie", merge(g_torus((-0.07, by, bz), (1, 0, 0), 0.060, 0.007, nseg=12, nside=4),
                            g_torus((0.07, by, bz), (1, 0, 0), 0.060, 0.007, nseg=12, nside=4)), M["leather"], B)
# rope tied round the bedroll, hanging
rp = [Vector((-0.02, by + 0.06, bz + 0.02)), Vector((-0.03, by + 0.075, bz - 0.05)), Vector((-0.06, by + 0.07, bz - 0.13)),
      Vector((-0.02, by + 0.065, bz - 0.20)), Vector((0.03, by + 0.07, bz - 0.14)), Vector((0.04, by + 0.075, bz - 0.05)), Vector((0.02, by + 0.06, bz + 0.02))]
obj("rotolo_corda", g_rope(rp, 0.008, n=5, sub=3), M["rope"], B)

save()
render_viste("p04", viste=["retro", "destra", "tre_quarti"])
shot("p04_elmo", (0, 0.2, 1.2), 0.7, d=(0.5, 1, 0.3))
