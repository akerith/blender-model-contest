# GROUP 9 - diving helmet and back gear (re-shaped/moved round-1 parts + ribbed hoses, rivets, harness)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
set_mat("ottone", (0.62, 0.45, 0.20), 0.35, 1.0)
set_mat("ottone_scuro", (0.35, 0.24, 0.10), 0.4, 1.0)
set_mat("tela", (0.66, 0.58, 0.45), 0.9)
set_mat("tubo", (0.20, 0.14, 0.10), 0.6)
g = bpy.data.materials.get("vetro")
set_mat("vetro", (0.55, 0.70, 0.65), 0.05)
b = g.node_tree.nodes.get("Principled BSDF")
b.inputs["Alpha"].default_value = 0.45
try:
    g.surface_render_method = "BLENDED"
except Exception:
    pass
CY = 0.275   # helmet centre Y: 0.25 asked, 0.275 so its front stays behind the cape on her back (no cut)

parts = split_loose(obj("Elmo"))
dome = max(parts, key=lambda o: len(o.data.vertices) if len(o.data.vertices) == 314 else 0)
collar = [o for o in parts if len(o.data.vertices) == 98]
a, bb = bbox(dome)
ca, cb = bbox(collar[0]) if collar else (a, bb)
cx, cy = (a.x + bb.x) / 2, (a.y + bb.y) / 2
sx_, sy_ = 0.32 / (bb.x - a.x), 0.30 / (bb.y - a.y)
zb, zt = ca.z, bb.z
sz = (1.47 - 1.13) / (zt - zb)
hose_rings = [o for o in parts if len(o.data.vertices) == 40]


def H(p):
    return V(((p.x - cx) * sx_, CY + (p.y - cy) * sy_, 1.13 + (p.z - zb) * sz))


for o in parts:
    if o in hose_rings:
        continue
    for v in o.data.vertices:
        v.co = H(v.co)
    o.data.update()
C = V((0, CY, (1.13 + 1.47) / 2))
# porthole parts and rivets
ob_base = [o for o in parts if len(o.data.vertices) == 50]
pc = centroid(ob_base[0]) if ob_base else V((0, CY + 0.15, 1.30))
small = [o for o in parts if len(o.data.vertices) == 26]
near = sorted(small, key=lambda o: (centroid(o) - pc).length)
port_r, coll_r = near[:8], near[8:]
newr = []
for i in range(12):   # 12 rivets around the main porthole (8 moved + 4 new)
    ang = 2 * math.pi * i / 12
    p = pc + V((math.cos(ang) * 0.094, 0.004, math.sin(ang) * 0.094))
    if i < len(port_r):
        rigid_to(port_r[i], p, None, 0.5)
    else:
        newr.append(sphere("_riv", p, 0.004, 8, 4, mat="ottone"))
zc = 1.145
for i in range(16):   # 16 rivets around the collar ring (12 moved + 4 new)
    ang = 2 * math.pi * i / 16
    p = V((math.cos(ang) * 0.152, CY + math.sin(ang) * 0.142, zc))
    if i < len(coll_r):
        rigid_to(coll_r[i], p, None, 0.5)
    else:
        newr.append(sphere("_riv", p, 0.004, 8, 4, mat="ottone"))
# two vertical raised bands left and right of the porthole (the 2 old bands turned into meridians)
bands = [o for o in parts if len(o.data.vertices) == 192 and matname(o).startswith("ottone_scuro")]
for o, ang in zip(bands, (35, -35)):
    n = V((math.cos(math.radians(ang)), -math.sin(math.radians(ang)), 0))
    rigid_to(o, C + V((0, 0, 0.01)), n, 1.0, which=2)
    c2, ax2 = pca(o)
    for v in o.data.vertices:   # 0.015 wide, on the dome surface
        d = v.co - c2
        v.co = c2 + V((d.x * 1.0, d.y * 1.0, d.z * 1.06))
    o.data.update()
# side portholes smaller (0.07 across)
for o in parts:
    n = len(o.data.vertices)
    c = centroid(o)
    if n in (120, 62) and abs(c.x) > 0.1:
        rigid_to(o, c, None, 0.74)
# colours: dome/frames brass, collar/bands/porthole base dark brass
for o in parts:
    m = matname(o)
    if m.startswith("vetro"):
        use_mat(o, "vetro")
    elif m.startswith("ottone_scuro"):
        use_mat(o, "ottone_scuro")
    elif m.startswith("ottone"):
        use_mat(o, "ottone")
for o in newr:
    o.vertex_groups.clear()

# ---- 9.8 ribbed hoses (new) + old smooth hoses re-used as brass connectors + old rings as clamps ----
def catmull(pts, n):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        for j in range(n):
            t = j / n
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


SPC = V((-0.195, 0.20, 1.00))   # spiral disc (x -0.12 asked: moved out to -0.195 so it does not cut the bedroll)
paths = {
    "R": [V((-0.125, CY - 0.01, 1.175)), V((-0.17, CY - 0.03, 1.12)), V((-0.20, 0.24, 1.07)), SPC + V((0, 0.0, 0.06))],
    "L": [V((0.125, CY - 0.01, 1.175)), V((0.18, 0.22, 1.12)), V((0.205, 0.12, 1.07)), V((0.20, 0.02, 1.03)),
          V((0.17, -0.06, 1.02))],
}
hoses = []
clamp_spots = []
for k, pts in paths.items():
    cp = catmull(pts, 10)
    rings = []
    acc = 0.0
    for i, p in enumerate(cp):
        if i:
            acc += (p - cp[i - 1]).length
        r = 0.015 if int(acc / 0.008) % 2 == 0 else 0.0175
        rings.append((p, r, r, r))
    hoses.append(loft("_hose", rings, seg=6, mat="tubo", cap=(True, True)))
    clamp_spots += [(cp[3], (cp[4] - cp[2])), (cp[len(cp) // 2], (cp[len(cp) // 2 + 1] - cp[len(cp) // 2 - 1])),
                    (cp[-4], (cp[-3] - cp[-5]))]
for o, (p, t) in zip(hose_rings, clamp_spots):
    rigid_to(o, p, t, 1.2, which=2)
    use_mat(o, "ottone_scuro")
tubi = split_loose(obj("Tubi"))
old_h = [o for o in tubi if len(o.data.vertices) == 52]
spir = sorted([o for o in tubi if len(o.data.vertices) == 108], key=lambda o: -max((v.co - centroid(o)).length for v in o.data.vertices))
for o, sxx in zip(old_h, (1, -1)):
    remap_cyl(o, V((0.105 * sxx, CY - 0.005, 1.19)), V((0.13 * sxx, CY - 0.01, 1.165)), 0.019)
    use_mat(o, "ottone")
for i, o in enumerate(spir):   # flat spiral disc 0.12 across, facing sideways
    rigid_to(o, SPC + V((-0.004 * i, 0, 0)), V((1, 0, 0)), 1.0, which=2)
    a2, b2 = bbox(o)
    s_ = (0.12 - 0.034 * i) / max(1e-4, (b2.z - a2.z))
    c2 = centroid(o)
    for v in o.data.vertices:
        d = v.co - c2
        v.co = c2 + V((d.x * 1.0, d.y * s_, d.z * s_))
    o.data.update()
    use_mat(o, "tubo")
for o in hoses:
    o.vertex_groups.clear()
tubi_o = join(tubi + hoses, "Tubi")
weight_all(tubi_o, "Chest")
helmet = join(parts + newr, "Elmo")
weight_all(helmet, "Chest")

# ---- 9.9 bedroll 0.34 long, 0.11 across, centre (0, 0.22, 1.06), two straps at X -0.10 / +0.10 ----
rp = split_loose(obj("Rotolo"))
rp.sort(key=lambda o: -(bbox(o)[1].x - bbox(o)[0].x))
RC = V((0, 0.22, 1.06))
for i, o in enumerate(rp):
    a3, b3 = bbox(o)
    c3 = centroid(o)
    m = matname(o)
    if i == 0:
        remap_cyl(o, RC - V((0.165, 0, 0)), RC + V((0.165, 0, 0)), 0.055)
        use_mat(o, "tela")
    elif m.startswith("lino"):
        sx3 = 1 if c3.x > 0 else -1
        remap_cyl(o, RC + V((0.165 * sx3, 0, 0)), RC + V((0.172 * sx3, 0, 0)), 0.047)
        use_mat(o, "tela")
    else:
        sx3 = 1 if c3.x > 0 else -1
        remap_cyl(o, RC + V((0.10 * sx3 - 0.01, 0, 0)), RC + V((0.10 * sx3 + 0.01, 0, 0)), 0.058)
        use_mat(o, "cuoio")
roll = join(rp, "Rotolo")
weight_all(roll, "Chest")

# ---- 9.10 two rope loops hanging from the bottom of the helmet over the bedroll ----
rl = split_loose(obj("Elmo_corda"))
for o, x in zip(rl, (-0.05, 0.06)):
    rigid_to(o, V((x, CY + 0.06, 1.085)), V((0.15 * x / abs(x), 1, 0.2)), 1.0, which=2)
    a4, b4 = bbox(o)
    s4 = 0.12 / max(1e-4, (b4.z - a4.z))
    c4 = centroid(o)
    for v in o.data.vertices:
        v.co = c4 + (v.co - c4) * s4
    o.data.update()
    use_mat(o, "corda")
ec = join(rl, "Elmo_corda")
weight_all(ec, "Chest")

# ---- 9.11 harness: shoulder straps to the helmet top corners + horizontal back strap over the bedroll ----
hs = []
for sxx in (1, -1):
    pts = [V((0.13 * sxx, 0.035, 1.437)), V((0.135 * sxx, 0.10, 1.43)), V((0.135 * sxx, CY - 0.10, 1.41)),
           V((0.13 * sxx, CY - 0.055, 1.38))]
    hs.append(loft("_harn", [(p, 0.0175, 0.004, 0.004) for p in pts], seg=6, mat="cuoio", up=V((0, 0, 1))))
pts = []
for j in range(13):
    t = -1 + 2 * j / 12
    x = 0.175 * t
    y = 0.165 + 0.05 * math.cos(t * math.pi / 2) if abs(t) < 0.75 else 0.06 + 0.11 * (1 - abs(t)) / 0.25
    pts.append(V((x, max(0.03, min(y, 0.285)), 1.06)))
for i, p in enumerate(pts):
    if abs(p.x) < 0.13:
        pts[i] = V((p.x, 0.22 + math.sqrt(max(0.0, 0.058 ** 2 - 0.0 ** 2)), 1.06))
hs.append(loft("_harn", [(p, 0.004, 0.012, 0.012) for p in pts], seg=6, mat="cuoio", up=V((0, 0, 1))))
for o in hs:
    o.vertex_groups.clear()
har = join(hs, "Imbracatura")
weight_all(har, "Chest")

for nm in ("Elmo", "Tubi", "Rotolo", "Elmo_corda", "Imbracatura"):
    a5, b5 = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a5.x, b5.x, a5.y, b5.y, a5.z, b5.z))
finish(9)
render_parte("rev_9_elmo", ["Elmo", "Tubi", "Rotolo", "Imbracatura", "Mantello", "Busto", "Cinghie"],
             ["retro", "destra", "sinistra", "tre_quarti"])
