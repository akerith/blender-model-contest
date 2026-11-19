exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 9 - diving helmet and back gear (existing pieces re-shaped, bands / harness / rivets added)
E = bpy.data.objects["Elmo"]
me = E.data
HCN = Vector((0, 0.25, 1.30))
mat("tela", lin((0.66, 0.58, 0.45)), 0.0, 0.9)
# fix of group 8: the heel blocks are sole, not laces
Cb = bpy.data.objects["Corpo"]
heel = set(i for isl in islands(Cb) if isl["mat"] == "lacci" and isl["hi"].z < 0.06 for i in isl["v"])
si = [k for k, m in enumerate(Cb.data.materials) if m.name == "scuro"][0]
for p in Cb.data.polygons:
    if all(v in heel for v in p.vertices):
        p.material_index = si
log("heel vertices fixed:", len(heel))

ISL = islands(E)
# 9.1 size: 0.32 wide, 0.30 deep, top 1.47, bottom 1.13
hel = [i for isl in ISL if isl["mat"] in ("ottone", "ottone_scuro", "vetro") and isl["c"].z > 1.10 for i in isl["v"]]
move(E, hel, lambda p: Vector((p.x, HCN.y + (p.y - HCN.y) * 1.087, HCN.z + (p.z - HCN.z) * 1.0625)))
# 9.2 dome flattened a bit at the bottom, on the collar ring
dome = max((isl for isl in ISL if isl["mat"] == "ottone"), key=lambda i: len(i["v"]))
move(E, dome["v"], lambda p: Vector((p.x, p.y, 1.20 + (p.z - 1.20) * 0.6)) if p.z < 1.20 else p)
ISL = islands(E)
lo, hi = bbox(E, hel)
log("helmet box", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
# 9.3 grille of the main porthole: the four round-1 bars pushed together into one cross
for isl in ISL:
    c = isl["c"]
    if len(isl["v"]) == 8 and abs(c.x) < 0.07 and c.y > 0.40 and abs(c.z - 1.315) < 0.07:
        if isl["hi"].z - isl["lo"].z > isl["hi"].x - isl["lo"].x:
            move(E, isl["v"], lambda p, d=-math.copysign(0.019, c.x): p + Vector((d, 0, 0)))
        else:
            move(E, isl["v"], lambda p, d=-math.copysign(0.020, c.z - 1.3149): p + Vector((0, 0, d)))
    # 9.4 side portholes 0.07 across
    elif abs(c.x) > 0.135 and 1.25 < c.z < 1.40 and isl["mat"] in ("ottone_scuro", "vetro") and abs(c.y - 0.256) < 0.06:
        move(E, isl["v"], lambda p: Vector((p.x, 0.256 + (p.y - 0.256) * 0.72, 1.3236 + (p.z - 1.3236) * 0.72)))
# 9.5 rivets on the collar ring: the 12 old ones re-spaced, 4 added -> 16
riv = [isl for isl in ISL if isl["mat"] == "ottone_scuro" and max(isl["hi"] - isl["lo"]) < 0.025 and 1.10 < isl["c"].z < 1.155
       and 0.10 < Vector((isl["c"].x, isl["c"].y - 0.2457)).length < 0.17]
riv.sort(key=lambda i: math.atan2(i["c"].y - 0.2457, i["c"].x))
zr = sum(i["c"].z for i in riv) / max(len(riv), 1)
rp = lambda k: Vector((0.150 * math.cos(rad(22.5 * k)), 0.2457 + 0.128 * math.sin(rad(22.5 * k)), zr))
for k, isl in enumerate(riv):
    move(E, isl["v"], lambda p, d=rp(k) - isl["c"]: p + d)
new("elmo_rivetti_nuovi", [g_sphere(rp(k), 0.0085, seg=6, rings=4) for k in range(len(riv), 16)], "ottone_scuro", 1)
log("collar rivets: old", len(riv), "new", 16 - len(riv))
# 9.6 two vertical raised bands, left and right of the main porthole
RD = Vector((0.16, 0.150, 0.170))
bands = []
for az in (45, 135):
    pts = []
    for el in range(86, -44, -13):
        a, e = rad(az), rad(el)
        pts.append(HCN + Vector((RD.x * math.cos(e) * math.cos(a), RD.y * math.cos(e) * math.sin(a), RD.z * math.sin(e))) * 1.012)
    for p, q in zip(pts, pts[1:]):
        bands.append(g_bar(p, q, 0.015, 0.006, up=tuple((p + q) / 2 - HCN)))
new("elmo_fasce", bands, "ottone_scuro", 1, sharp=50)
# 9.8 hoses: ribbed (ring by ring), right one down to the flat spiral, left one forward under the arm to the belt
hs = [isl for isl in ISL if isl["mat"] == "tubo"]
spiral = max(hs, key=lambda i: len(i["v"]))
c = spiral["c"]
move(E, spiral["v"], lambda p: Vector((-0.12 + (p.x - c.x), 0.20 + (p.y - c.y) * 0.94, 1.00 + (p.z - c.z) * 0.94)))
PATH = {-1: [(-0.123, 0.292, 1.20), (-0.165, 0.30, 1.14), (-0.172, 0.285, 1.08), (-0.14, 0.265, 1.035), (-0.12, 0.258, 1.005)],
        1: [(0.123, 0.292, 1.20), (0.175, 0.29, 1.14), (0.225, 0.22, 1.08), (0.232, 0.12, 1.05), (0.20, 0.03, 1.035), (0.172, -0.02, 1.022)]}
for isl in hs:
    if isl is spiral:
        continue
    idx = sorted(isl["v"])
    nr = (len(idx) - 2) // 6
    P = catmull(PATH[1 if isl["c"].x > 0 else -1], 8)
    L = [0.0]
    for a_, b_ in zip(P, P[1:]):
        L.append(L[-1] + (b_ - a_).length)
    rings = []
    for j in range(nr):
        s = L[-1] * j / (nr - 1)
        k = max(i for i in range(len(L)) if L[i] <= s + 1e-9)
        k = min(k, len(P) - 2)
        pt = P[k].lerp(P[k + 1], (s - L[k]) / max(L[k + 1] - L[k], 1e-9))
        r = 0.015 * (1.14 if j % 2 else 0.86)
        rings.append((pt, r, r))
    vs, _ = g_loft(rings, n=6)
    for i, p in zip(idx, vs):
        me.vertices[i].co = p
    log("hose side %+d: %d rings, length %.2f" % (1 if isl["c"].x > 0 else -1, nr, L[-1]))
r2 = [g_torus(spiral["c"] * 0 + Vector((-0.12, 0.20, 1.00)), (1, 0, 0), 0.0, 0.001, nseg=3, nside=3)]
# 9.9 bedroll: 0.34 long, 0.11 across, centre (0, 0.22, 1.06), canvas colour, straps at x = +-0.10
me.materials.append(bpy.data.materials["tela"])
ti = len(me.materials) - 1
for isl in ISL:
    c = isl["c"]
    if isl["mat"] == "lino" and abs(c.x) < 0.05:
        affine(E, isl["v"], (-0.17, 0.165, 1.005), (0.17, 0.275, 1.115))
        s = set(isl["v"])
        for p in me.polygons:
            if p.vertices[0] in s:
                p.material_index = ti
    elif isl["mat"] == "cuoio" and 0.03 < abs(c.x) < 0.12 and 0.95 < c.z < 1.15:
        sg = 1 if c.x > 0 else -1
        affine(E, isl["v"], (sg * 0.10 - 0.008, 0.160, 1.000), (sg * 0.10 + 0.008, 0.280, 1.120))
    elif isl["mat"] == "corda" and c.z < 1.16:      # 9.10 rope loops under the helmet, over the bedroll
        move(E, isl["v"], lambda p: p + Vector((0, -0.024, 0.0)))
# 9.11 harness: straps from the shoulders to the collar ring of the helmet, and a strap at the back holding the bedroll
har = []
for sg in (1, -1):
    pts = [(sg * 0.13, 0.03, 1.452), (sg * 0.142, 0.115, 1.432), (sg * 0.14, 0.168, 1.34), (sg * 0.125, 0.19, 1.25), (sg * 0.112, 0.205, 1.19)]
    P = catmull(pts, 3)
    har.append(g_loft([(p, 0.0175, 0.004) for p in P], n=4, ref=(1, 0, 0), sq=0.5))
pts = [(-0.15, 0.05, 1.062), (-0.19, 0.14, 1.06), (-0.185, 0.24, 1.06), (-0.10, 0.283, 1.06), (0.10, 0.283, 1.06), (0.185, 0.24, 1.06),
       (0.19, 0.14, 1.06), (0.15, 0.05, 1.062)]
har.append(g_loft([(p, 0.004, 0.011) for p in catmull(pts, 3)], n=4, ref=(0, -1, 0), sq=0.5))
new("imbracatura", har, "cuoio", 1, sharp=50)
me.update()
salva()
render_viste("rev_9", viste=["retro", "destra", "sinistra", "alto"])
shot("rev_9_elmo", (0, 0.2, 1.22), 0.7, d=(0.45, 1, 0.3))
shot("rev_9_elmo_dx", (0, 0.2, 1.2), 0.7, d=(-1, 0.5, 0.2))
