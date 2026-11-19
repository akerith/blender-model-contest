exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
random.seed(11)
HB = ["Head"]
# face tweaks: smaller cheekbones and chin, smaller iris
clear("F_zigomo")
clear("F_mento")
clear("F_iride")
for sx in (1, -1):
    sphere("F_zigomo%d" % sx, (0.044 * sx, -0.050, 1.577), 0.02, 10, 6, scale=(1.0, 0.6, 0.7), mat="pelle", bones=HB)
    sphere("F_iride%d" % sx, (0.030 * sx, -0.0722, 1.6025), 0.0058, 8, 5, scale=(1, 0.5, 1), mat="occhi", bones=HB)
sphere("F_mento", (0, -0.058, 1.497), 0.02, 10, 6, scale=(1.15, 0.7, 0.7), mat="pelle", bones=HB)

# hair: flat wavy locks lying on the head
clear("K_ciuffo")
C = V((0, 0.006, 1.612))


def surf(a, e):
    ry = 0.083 if math.cos(a) > 0 else 0.102
    return C + V((math.sin(a) * 0.086 * math.cos(e), -math.cos(a) * ry * math.cos(e), 0.102 * math.sin(e)))


n = 0
tries = 0
while n < 170 and tries < 5000:
    tries += 1
    a = random.uniform(-math.pi, math.pi)
    e = random.uniform(-0.7, 1.35)
    front = math.cos(a)
    if front > 0.35 and e < 0.45:
        continue
    if front > -0.1 and e < -0.2:
        continue
    p = surf(a, e)
    nrm = (p - C).normalized()
    down = V((0, 0, -1)) - nrm * nrm.dot(V((0, 0, -1)))
    if down.length < 0.35:  # crown: flow backwards/sideways
        down = V((math.sin(a) * 0.5, 1.0, 0)) - nrm * nrm.dot(V((math.sin(a) * 0.5, 1.0, 0)))
    down.normalize()
    side = nrm.cross(down).normalized()
    bang = front > 0.35
    if bang:
        flow = (down + side * random.uniform(-0.2, 0.6) + V((0.35, 0, 0))).normalized()
        L = random.uniform(0.05, 0.08)
    else:
        flow = (down + side * random.uniform(-0.35, 0.35)).normalized()
        L = random.uniform(0.06, 0.10) * (1.1 if e < 0.1 else 1.0)
    w = random.uniform(0.020, 0.030)
    th = random.uniform(0.007, 0.011)
    lift = random.uniform(0.006, 0.02)
    pts = []
    rings = []
    for j in range(5):
        t = j / 4
        wave = math.sin(t * math.pi * 1.5 + random.uniform(0, 0.5)) * 0.012
        q = p + flow * L * t + nrm * (lift * math.sin(t * math.pi) - 0.006 + 0.004 * t) + side * wave
        if j == 4:
            q += nrm * -0.008  # tip curls in
        ww = w * (1.0 - 0.85 * t ** 1.5)
        rings.append((q, ww, th * (1 - 0.6 * t), th * (1 - 0.6 * t)))
    white = (bang or e > 0.25) and -1.2 < a < -0.35 and e < 1.1
    # up=nrm -> thickness along the normal, width along the head
    loft("K_ciuffo%03d" % n, rings, seg=6, mat=("ciocca" if white else "capelli"), bones=HB, cap=(False, True), up=nrm)
    n += 1

log("ciuffi:", n, "triangoli:", tri_count())
save()
render_parte("p03_testa", ["C_testa", "C_collo", "F_", "K_"], ["fronte", "destra", "tre_quarti", "retro"])
