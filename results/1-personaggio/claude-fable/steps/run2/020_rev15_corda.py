exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# small fix seen in the close-up: the thin core of the rope coil (the round-1 loops) stuck out of the twisted strands
F = bpy.data.objects["Fianchi"]
vv = F.data.vertices
Z = Vector((0, 0, 1))
n = 0
for isl in islands(F):
    c = isl["c"]
    if isl["mat"] != "corda" or len(isl["v"]) != 80 or not (-0.26 < c.x < -0.11 and 0.74 < c.z < 0.95 and c.y < -0.03):
        continue
    cs = [vv[i].co - c for i in isl["v"]]
    sxx, syy, sxy = sum(p.x * p.x for p in cs), sum(p.y * p.y for p in cs), sum(p.x * p.y for p in cs)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    Uh = Vector((math.cos(ang), math.sin(ang), 0))
    Nn = Uh.cross(Z)
    R_, Ry_ = 0.042, 0.072

    def f(p, c=c, Uh=Uh, Nn=Nn):
        d = p - c
        tau = math.atan2(d.z / Ry_, d.dot(Uh) / R_)
        cen = c + Uh * (R_ * math.cos(tau)) + Z * (Ry_ * math.sin(tau))
        return cen + (p - cen) * 0.25
    move(F, isl["v"], f)
    n += 1
log("rope cores tucked inside the strands:", n)
salva()
shot("rev_15_corda", (-0.18, 0, 0.88), 0.5, d=(-0.6, -1, 0.15))
