exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# what are the small pale flakes inside the rope coil? list every island around that spot (nothing is changed)
for o in scn.objects:
    if o.type != "MESH":
        continue
    for isl in islands(o):
        lo, hi = isl["lo"], isl["hi"]
        if lo.x < -0.13 and hi.x > -0.23 and lo.z < 0.90 and hi.z > 0.80 and lo.y < -0.02 and hi.y > -0.12:
            log("%-9s %-14s %4d verts  lo (%.3f %.3f %.3f) hi (%.3f %.3f %.3f)" % (
                o.name, isl["mat"], len(isl["v"]), lo.x, lo.y, lo.z, hi.x, hi.y, hi.z))
