# GROUP 2 fix: hair volume to 0.20 wide / top 1.70, iris visible, egg-shaped jaw
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
hair = obj("Capelli")
for v in hair.data.vertices:
    p = v.co
    if abs(p.x) > 0.082:
        p.x = math.copysign(0.082 + (abs(p.x) - 0.082) * 0.28, p.x)
    if p.y > 0.115:
        p.y = 0.115 + (p.y - 0.115) * 0.3
    if p.y < -0.095:
        p.y = -0.095 + (p.y + 0.095) * 0.4
    if p.z > 1.66:
        p.z = 1.66 + (p.z - 1.66) * 0.74
hair.data.update()
parts = split_loose(obj("Testa"))
for o in parts:
    m = matname(o)
    if m == "occhi":
        c = centroid(o)
        for v in o.data.vertices:
            v.co = c + (v.co - c) * 1.3 + V((0, -0.0045, 0))
    else:
        for v in o.data.vertices:
            z = v.co.z
            if z < 1.565:  # narrower towards the chin (egg)
                f = 1.0 - 0.22 * min(1.0, (1.565 - z) / 0.09)
                v.co.x *= f
head = join(parts, "Testa")
a, b = bbox(hair)
log("capelli: x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (a.x, b.x, a.y, b.y, a.z, b.z))
a, b = bbox(head)
log("testa: x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (a.x, b.x, a.y, b.y, a.z, b.z))
finish(2)
render_parte("rev_2_testa", ["Testa", "Capelli", "Collo"], ["fronte", "retro", "tre_quarti", "destra"])
