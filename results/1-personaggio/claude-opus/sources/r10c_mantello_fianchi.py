# GROUP 10 fix (10.3): the long cape (the rebuilt piece) regenerated with its front panels opened at hip height,
# so the rope, canister and map tube hang in front of it as in the reference; nothing cuts through.
# GROUP 6 - the cape. The ONE piece rebuilt: the round-1 cape was a closed bell with a regular zig-zag hem,
# no front panels and solidify already applied, so it could not be re-shaped into the requested form.
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
random.seed(606)
TEAL, STREAK, SAND, STAIN = (0.22, 0.34, 0.31), (0.40, 0.52, 0.48), (0.62, 0.55, 0.43), (0.36, 0.26, 0.15)

# ---- material: colour from the vertex colours (exported to the glb too) ----
mat = bpy.data.materials.get("mantello_rev") or bpy.data.materials.new("mantello_rev")
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes.get("Principled BSDF")
ca = nt.nodes.get("_col") or nt.nodes.new("ShaderNodeVertexColor")
ca.name = "_col"
ca.layer_name = "Col"
nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.92
mat.diffuse_color = lin(TEAL) + (1,)


def mixc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def cape_colour(p, th, zhem):
    streak = 0.5 + 0.5 * math.sin(th * 21.0 + 2.5 * math.sin(th * 6.0 + p.z * 3.0) + p.z * 1.5)
    streak = max(0.0, (streak - 0.72) / 0.28)
    c = mixc(TEAL, STREAK, 0.85 * streak)
    fade = min(1.0, max(0.0, (zhem + 0.25 - p.z) / 0.25))
    c = mixc(c, SAND, fade ** 0.8)
    st = 0.0
    for (sx, sz, sr) in STAINS:
        d = math.hypot((th - sx) * 0.45, p.z - sz)
        st = max(st, 1.0 - d / sr)
    c = mixc(c, STAIN, 0.75 * max(0.0, st) * min(1.0, fade + 0.3))
    return lin(c)


STAINS = [(random.uniform(-2.8, 2.8), random.uniform(0.22, 0.55), random.uniform(0.04, 0.09)) for _ in range(16)]


def paint(o, colfn):
    me = o.data
    at = me.color_attributes.get("Col") or me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
    for v in me.vertices:
        c = colfn(v)
        at.data[v.index].color = (c[0], c[1], c[2], 1.0)


# ---- collision helpers (push the cloth out of body, legs and arms) ----
def push_body(p, m):
    if 0.76 < p.z < 1.47:
        zz, rx, rf, rb, yo = tab(NEWT, p.z)
        if p.z < 1.07:   # tunic skirt + belts
            t = (p.z - 0.795) / 0.27
            rx, rf, rb = 0.19 + (0.147 - 0.19) * t, 0.125 + (0.103 - 0.125) * t, 0.135 + (0.103 - 0.135) * t
        ry = rb if p.y > yo else rf
        e = (p.x / (rx + m)) ** 2 + ((p.y - yo) / (ry + m)) ** 2
        if e < 1.0:
            k = 1.0 / math.sqrt(max(e, 1e-6))
            p.x *= k
            p.y = yo + (p.y - yo) * k
    for sx in (1, -1):
        for a, b, r in ((V((0.09 * sx, 0, 0.92)), V((0.11 * sx, -0.01, 0.49)), 0.085),
                        (V((0.11 * sx, -0.01, 0.49)), V((0.13 * sx, 0, 0.06)), 0.075)):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            q = a + ab * t
            dxy = V((p.x - q.x, p.y - q.y, 0))
            if dxy.length < r + m:
                if dxy.length < 1e-5:
                    dxy = V((sx, 0.3, 0))
                dxy = dxy.normalized() * (r + m)
                p.x, p.y = q.x + dxy.x, q.y + dxy.y
    return p


def push_arms(p, m, back=True):
    for sx in (1, -1):
        S, E, W = V((SH1.x * sx, 0, SH1.z)), V((ELB1.x * sx, 0, ELB1.z)), V((WRI1.x * sx, 0, WRI1.z))
        for a, b, r in ((S, E, 0.058), (E, W, 0.052)):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            q = a + ab * t
            d = p - q
            if d.length < r + m:
                if back:   # cloth hangs behind (or in front) of the arm: move along Y
                    perp = d - V((0, d.y, 0))
                    need = math.sqrt(max(0.0, (r + m) ** 2 - perp.length_squared))
                    p.y = q.y + (need if p.y >= q.y - 0.015 else -need)
                else:      # cloth lies over the arm: move away from the axis
                    if d.length < 1e-5:
                        d = V((0, 0, 1))
                    p = q + d.normalized() * (r + m)
    return p


# ---- 6.3 long cape ----
NC, NR = 72, 20
hem = []
k = 0
drops = [0.0] * (NC + 1)
while k <= NC:            # irregular triangular rags: widths 2-6 columns, lengths 0.05-0.18
    w = random.randint(2, 6)
    L = random.uniform(0.05, 0.18)
    for j in range(w + 1):
        if k + j <= NC:
            f = 1.0 - abs(2.0 * j / w - 1.0)
            drops[k + j] = max(drops[k + j], L * f ** 1.3)
    k += w
verts, cols = [], []
for r in range(NR):
    s = r / (NR - 1)
    for c in range(NC + 1):
        u = c / NC
        zz = 1.42 - (1.42 - 0.2) * s
        bump = max(0.0, 1.0 - abs(zz - 0.84) / 0.26) ** 0.8   # open the panels at hip height (gear in front)
        the = math.radians(150 + 12 * s - 34 * bump)
        th = -the + 2 * the * u                  # 0 = back (+Y)
        zhem = 0.20 + 0.05 * (abs(th) / the) ** 2
        z = 1.42 - (1.42 - zhem) * s
        if r == NR - 1:
            z -= drops[c]
        rx = 0.13 + 0.11 * min(1.0, s / 0.06) + 0.31 * max(0.0, (s - 0.06) / 0.94) ** 1.1
        ryb = 0.10 + 0.10 * s
        ryf = 0.08 + 0.09 * s
        fold = (0.008 + 0.035 * s) * math.sin(th * 5.2 + 0.7) + 0.01 * s * math.sin(th * 11 + 2.0)
        cy = math.cos(th)
        x = math.sin(th) * (rx + fold)
        y = 0.0 + cy * ((ryb if cy > 0 else ryf) + fold)
        p = V((x, y, z))
        p = push_body(p, 0.016)
        p = push_arms(p, 0.02, True)
        verts.append(p)
        cols.append((th, zhem))
faces = []
W_ = NC + 1
holes = set()
for _ in range(9):
    rr = random.randint(NR - 4, NR - 3)
    cc = random.randint(2, NC - 4)
    holes.add((rr, cc))
    if random.random() < 0.5:
        holes.add((rr, cc + 1))
for r in range(NR - 1):
    for c in range(NC):
        if (r, c) in holes:
            continue
        a = r * W_ + c
        faces.append((a, a + 1, a + 1 + W_, a + W_))
kill("Mantello")
cape = mesh_obj("Mantello", verts, faces, mat, True)
me = cape.data
at = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
for i, v in enumerate(me.vertices):
    th, zh = cols[i] if i < len(cols) else (0.0, 0.2)
    cc = cape_colour(v.co, th, zh)
    at.data[i].color = (cc[0], cc[1], cc[2], 1.0)
solidify(cape, 0.007, 1.0)
bind(cape, ["Chest", "Spine", "Hips", "Shoulder.L", "Shoulder.R", "UpperLeg.L", "UpperLeg.R"], power=3.0)
reset_colours()


for nm in ("Mantello",):
    a, b = bbox(obj(nm))
    log("%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (nm, a.x, b.x, a.y, b.y, a.z, b.z))
hip = [v.co for v in obj("Mantello").data.vertices if 0.80 < v.co.z < 0.88 and v.co.y < 0.0]
log("bordo davanti ai fianchi: x da %.3f a %.3f" % (min(abs(p.x) for p in hip), max(abs(p.x) for p in hip)) if hip else "")
bot = [v.co for v in obj("Mantello").data.vertices if v.co.z < 0.45]
log("larghezza in basso: %.3f" % (max(p.x for p in bot) - min(p.x for p in bot)))
tri_report()
bpy.ops.wm.save_mainfile()
render_viste("rev_10_mantello", viste=["fronte", "tre_quarti", "retro"])
