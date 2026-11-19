exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 5 - arms: sleeve rolls, gauntlet cuffs and straps, bracer, NEW hands
C = bpy.data.objects["Corpo"]
mat("cuoio_cinghie", lin((0.20, 0.12, 0.07)), 0.0, 0.65)
mat("vetro_verde", lin((0.25, 0.55, 0.35)), 0.0, 0.12)


def rot(v, axis, deg):
    return Matrix.Rotation(rad(deg), 3, Vector(axis).normalized()) @ Vector(v)


# --- the ONE piece deleted and rebuilt: the hands (round-1 hands were 6-sided one-piece fingers) ---
dele = []
for isl in islands(C):
    if isl["mat"] != "cuoio_scuro":
        continue
    c = isl["c"]
    p = Vector((abs(c.x), c.y, c.z))
    s = (p - ELN).dot(U2) + 0.29
    radial = ((p - ELN) - U2 * (p - ELN).dot(U2)).length
    if s > 0.565 and radial < 0.09:
        dele += isl["v"]
bm = bmesh.new()
bm.from_mesh(C.data)
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.verts[i] for i in dele], context="VERTS")
bm.to_mesh(C.data)
bm.free()
log("old hand vertices deleted:", len(dele))

a = U2.copy()
B = (N2 * math.cos(rad(20)) - Vector((0, 1, 0)) * math.sin(rad(20))).normalized()   # back of the hand: up, a little forward
T = a.cross(B).normalized()                                                          # thumb side (forward)


def hp(s, t=0.0, b=0.0):
    return WRN + a * s + T * t + B * b


def finger(base, d, L, r0, n=10):
    ax = B.cross(d).normalized()
    pts, dirs, dd = [base], [], d
    for sl in (0.42 * L, 0.32 * L, 0.26 * L):
        dd = rot(dd, ax, 10)            # every joint bent 10 deg towards the palm
        dirs.append(dd)
        pts.append(pts[-1] + dd * sl)
    rr = [(pts[0] - dirs[0] * 0.008, 1.0), (pts[0].lerp(pts[1], 0.5), 0.94), (pts[1], 0.99), (pts[1].lerp(pts[2], 0.5), 0.86),
          (pts[2], 0.91), (pts[2].lerp(pts[3], 0.55), 0.79), (pts[3] - dirs[2] * 0.005, 0.70), (pts[3], 0.36)]
    return g_loft([(p, r0 * k, r0 * k) for p, k in rr], n=n, ref=tuple(B)), pts[3]


hand = []
palm = [(hp(-0.008), 0.031, 0.015), (hp(0.012), 0.037, 0.0155), (hp(0.045), 0.040, 0.015), (hp(0.075), 0.040, 0.0135),
        (hp(0.086), 0.037, 0.011), (hp(0.090), 0.030, 0.007)]
hand.append(g_loft(palm, n=16, axes=(tuple(T), tuple(B)), sq=0.7))
tips = {}
for nm, t, ang, L, r0 in (("index", 0.0285, -12, 0.075, 0.0095), ("middle", 0.0095, -4, 0.085, 0.0098),
                          ("ring", -0.0095, 4, 0.080, 0.0093), ("little", -0.0280, 12, 0.065, 0.0085)):
    g, tip = finger(hp(0.083, t, -0.001), rot(a, B, ang), L, r0)
    hand.append(g)
    tips[nm] = tip
# thumb: base + 2 segments, 0.065 long, from the side of the palm near the wrist, 40 deg from the index
td = rot(a, B, -52)
td = rot(td, B.cross(td), 22)
tb = hp(0.020, 0.030, -0.004)
td2 = rot(td, B.cross(td), 12)
p1, p2 = tb + td * 0.014, tb + td * 0.036
p3 = p2 + td2 * 0.029
th = [(tb - td * 0.014, 0.0135, 0.0135), (p1, 0.0130, 0.0130), (p1.lerp(p2, 0.6), 0.0112, 0.0112), (p2, 0.0114, 0.0114),
      (p2.lerp(p3, 0.5), 0.0098, 0.0098), (p3 - td2 * 0.005, 0.0088, 0.0088), (p3, 0.0045, 0.0045)]
hand.append(g_loft(th, n=10, ref=tuple(B)))
o = both_new("mani", hand, "cuoio_scuro", 0, sharp=60)
log("hands: %d tris; left middle fingertip at (%.3f, %.3f, %.3f); wrist (%.3f, %.3f); elbow (%.3f, %.3f)" % (
    sum(len(p.vertices) - 2 for p in o.data.polygons), tips["middle"].x, tips["middle"].y, tips["middle"].z, WRN.x, WRN.z, ELN.x, ELN.z))

# --- 5.1 sleeves: 4 bulging rings of rolled linen between Z 1.25 and the elbow ---
rings = [g_torus(apn(s), U1, R, r, nseg=12, nside=5) for s, R, r in ((0.185, 0.046, 0.013), (0.212, 0.048, 0.014),
                                                                     (0.240, 0.049, 0.0145), (0.266, 0.047, 0.013))]
both_new("manica_rotoli", rings, "lino", 0, sharp=80)
# --- 5.2 gauntlet: flared top cuff 0.04 below the elbow, 0.095 across ---
cuff = g_loft([(apn(0.322), 0.043, 0.043), (apn(0.328), 0.0475, 0.0475), (apn(0.343), 0.0475, 0.0475), (apn(0.350), 0.043, 0.043)],
              n=14, ref=(0, 1, 0), cap0=False, cap1=False)
both_new("guanto_risvolto", cuff, "cuoio_scuro", 0, sharp=40)
# --- 5.3 three straps on each gauntlet (cuff, middle, wrist) with tiny brass buckles on the outside ---
# the two round-1 straps stay (moved to the cuff and the middle), the right wrist band of round 1 goes to the wrist
st_old = [i for isl in islands(C) if isl["mat"] == "cuoio" and isl["c"].z < 1.2 and abs(isl["c"].x) > 0.36 and isl["c"].z > 0.95
          for i in [isl]]
for isl in st_old:
    c = isl["c"]
    sg = 1 if c.x > 0 else -1
    s = (Vector((abs(c.x), c.y, c.z)) - ELN).dot(U2) + 0.29
    tgt = 0.336 if s < 0.41 else (0.43 if s < 0.47 else 0.522)
    d = U2 * (tgt - s)
    move(C, isl["v"], lambda p, d=d, sg=sg: p + Vector((d.x * sg, 0, d.z)))
    log("old arm strap at s=%.3f moved to %.3f (side %d)" % (s, tgt, sg))
for i in pick(C, "cuoio", lo=(-0.7, -0.1, 0.95), hi=(0.7, 0.1, 1.2)):
    pass
wr = g_torus(apn(0.522), U2, 0.0375, 0.0065, nseg=12, nside=4)
new("guanto_cinghia_polso_L", wr, "cuoio_cinghie", 0)
bk = [g_box(apn(s, 0, n), (0.015, 0.012, 0.006), M=Matrix(((U2.x, 0, N2.x), (0, 1, 0), (U2.z, 0, N2.z))))
      for s, n in ((0.336, 0.056), (0.43, 0.050), (0.522, 0.045))]
both_new("guanto_fibbie", bk, "ottone", 0, smooth=False)
for isl in islands(C):       # darker leather on the old gauntlet straps
    pass
# --- 5.4 bracer gauge on the LEFT forearm, outside, just above the wrist: 0.055 across, 0.015 thick ---
Bo = bpy.data.objects["Bracciale"]
lo, hi = bbox(Bo)
log("bracer box before", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
c0 = apn(0.492)
move(Bo, range(len(Bo.data.vertices)), lambda p: apn(0.497) + (p - c0) * 0.92)
for k, m in enumerate(Bo.data.materials):
    if m.name == "vetro":
        Bo.data.materials[k] = bpy.data.materials["vetro_verde"]
salva()
render_viste("rev_5", viste=["fronte", "retro", "alto"])
shot("rev_5_mano_L", tuple(WRN + U2 * 0.06), 0.42, d=(0.3, -1, 0.5))
shot("rev_5_braccio_L", tuple(ELN + U2 * 0.1), 0.62, d=(0.2, -1, 0.6))
shot("rev_5_mano_sotto", tuple(WRN + U2 * 0.06), 0.42, d=(0.4, -0.3, -1))
