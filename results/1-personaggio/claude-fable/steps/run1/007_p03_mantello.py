exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
M = materials()
random.seed(11)


def sheet(keys, NC, NR, folds=0.0, rag=False, holes=0.0, cy=0.02, inner_off=0.005):
    """cloth around the body. keys: (v, z, rx, ry_back, ry_front, theta_max_deg). theta=0 is the back.
    returns outer geom, inner geom, uvs"""
    # ragged hem: each column has its own length
    ln = []
    sm = [random.random() for _ in range(NC + 1)]
    for i in range(NC + 1):
        a = (sm[max(i - 1, 0)] + sm[i] + sm[min(i + 1, NC)]) / 3
        d = 0.02 + 0.10 * a + (0.13 * random.random() if random.random() < 0.3 else 0)
        ln.append(1 - d if rag else 1.0)
    ph1, ph2 = random.uniform(0, 6), random.uniform(0, 6)
    vo, vi, uvs = [], [], []
    for r in range(NR + 1):
        v0 = r / NR
        for i in range(NC + 1):
            u = i / NC
            v = v0
            if rag and v0 > 0.4:
                v = 0.4 + (v0 - 0.4) * ln[i]
            _, z, rx, rb, rf, tm = lerp_keys(keys, v)
            th = rad(-tm + 2 * tm * u)
            amp = folds * max(0.0, (v - 0.22)) / 0.78
            k = 1 + amp * (math.sin(th * 9 + ph1) + 0.5 * math.sin(th * 17 + ph2 + v * 3))
            s, c = math.sin(th), math.cos(th)
            ry = rb if c > 0 else rf
            p = Vector((rx * k * s, cy + ry * k * c, z))
            vo.append(p)
            q = Vector((p.x - inner_off * s, p.y - inner_off * c, p.z))
            vi.append(q)
            uvs.append((u, 1 - v))
    fo = []
    W = NC + 1
    for r in range(NR):
        for i in range(NC):
            if holes and r >= NR * 0.72 and random.random() < holes * (r / NR):
                continue
            a = r * W + i
            fo.append((a, a + W, a + W + 1, a + 1))
    fi = [tuple(reversed(f)) for f in fo]
    return (vo, fo), (vi, fi), uvs


CAPE = [  # v, z, rx, ry_back, ry_front, theta_max
    (0.00, 1.385, 0.075, 0.080, 0.070, 152),
    (0.05, 1.378, 0.140, 0.110, 0.100, 148),
    (0.11, 1.368, 0.215, 0.140, 0.130, 138),
    (0.18, 1.315, 0.310, 0.170, 0.155, 122),
    (0.25, 1.250, 0.392, 0.195, 0.150, 104),
    (0.31, 1.165, 0.418, 0.215, 0.120, 70),
    (0.50, 0.900, 0.405, 0.235, 0.100, 67),
    (0.75, 0.500, 0.385, 0.250, 0.100, 65),
    (1.00, 0.120, 0.370, 0.262, 0.100, 64),
]
go, gi, uv = sheet(CAPE, 46, 30, folds=0.075, rag=True, holes=0.22)
obj("mantello", go, M["cape"], "CAPE", uvs=uv, sharp=80)
obj("mantello_dentro", gi, M["capein"], "CAPE", uvs=uv, sharp=80)

# standing collar
COL = [
    (0.0, 1.355, 0.085, 0.090, 0.080, 150),
    (0.5, 1.400, 0.098, 0.104, 0.090, 146),
    (1.0, 1.445, 0.118, 0.122, 0.100, 140),
]
go, gi, uv = sheet(COL, 18, 3, cy=0.005, inner_off=0.006)
# the collar is seen from inside too: outer faces point out, inner faces in
obj("colletto", go, M["cape"], "Chest,Neck", uvs=uv)
obj("colletto_dentro", gi, M["capein"], "Chest,Neck", uvs=uv)

save()
render_viste("p03", viste=["fronte", "retro", "destra"])
