exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
M = materials()
random.seed(11)


def sheet(keys, NC, NR, folds=0.0, vend=None, cy=0.02, inner_off=0.005):
    """cloth around the body. keys: (v, z, rx, ry_back, ry_front, theta_max_deg). theta=0 is the back.
    vend(theta_deg, i) -> where the column ends (0..1): gives the torn hem.
    returns outer geom, inner geom, uvs"""
    tm_last = keys[-1][5]
    ve = [1.0] * (NC + 1)
    if vend:
        for i in range(NC + 1):
            ve[i] = vend(-tm_last + 2 * tm_last * i / NC, i)
    ph1, ph2 = random.uniform(0, 6), random.uniform(0, 6)
    vo, vi, uvs = [], [], []
    for r in range(NR + 1):
        v0 = r / NR
        for i in range(NC + 1):
            u = i / NC
            v = min(v0, ve[i])
            _, z, rx, rb, rf, tm = lerp_keys(keys, v)
            th = rad(-tm + 2 * tm * u)
            amp = folds * max(0.0, (v - 0.2)) / 0.8
            k = 1 + amp * (math.sin(th * 7 + ph1) + 0.45 * math.sin(th * 15 + ph2 + v * 3))
            s, c = math.sin(th), math.cos(th)
            ry = rb if c > 0 else rf
            p = Vector((rx * k * s, cy + ry * k * c, z))
            vo.append(p)
            vi.append(Vector((p.x - inner_off * s, p.y - inner_off * c, p.z)))
            uvs.append((u, 1 - v))
    fo = []
    W = NC + 1
    for r in range(NR):
        for i in range(NC):
            if r / NR >= min(ve[i], ve[i + 1]) - 1e-6:
                continue
            a = r * W + i
            fo.append((a, a + W, a + W + 1, a + 1))
    fi = [tuple(reversed(f)) for f in fo]
    return (vo, fo), (vi, fi), uvs


CAPE = [  # v, z, rx, ry_back, ry_front, theta_max
    (0.00, 1.385, 0.075, 0.080, 0.070, 154),
    (0.05, 1.378, 0.140, 0.105, 0.100, 150),
    (0.11, 1.368, 0.215, 0.125, 0.130, 150),
    (0.18, 1.315, 0.310, 0.135, 0.160, 148),
    (0.25, 1.250, 0.392, 0.140, 0.175, 146),
    (0.31, 1.165, 0.418, 0.150, 0.170, 146),
    (0.38, 1.060, 0.415, 0.172, 0.165, 146),
    (0.50, 0.900, 0.405, 0.205, 0.160, 146),
    (0.75, 0.500, 0.385, 0.240, 0.120, 146),
    (1.00, 0.120, 0.370, 0.258, 0.120, 146),
]
NC = 72
_n = [random.random() for _ in range(NC + 1)]
_slit = set(random.sample(range(18, NC - 18), 5))


def cape_end(th, i):
    a = abs(th)
    sm = (_n[max(i - 1, 0)] + _n[i] + _n[min(i + 1, NC)]) / 3
    if a > 100:        # front flaps over the upper arm and chest side
        return 0.30 + 0.16 * ((a - 100) / 46) ** 1.2 + 0.035 * _n[i]
    if a > 71:         # resting on top of the arm
        return 0.285 + 0.015 * _n[i]
    d = 0.015 + 0.10 * sm + (0.12 * _n[(i * 7) % NC] if _n[(i * 3) % NC] < 0.3 else 0)
    if i in _slit:
        d = random.uniform(0.25, 0.42)
    return 1 - d


go, gi, uv = sheet(CAPE, NC, 32, folds=0.11, vend=cape_end)
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
