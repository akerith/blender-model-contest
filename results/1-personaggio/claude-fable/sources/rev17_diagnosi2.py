exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# diagnosis only: the pieces of the cape object, and where the 76-vertex ones really are
Mn = bpy.data.objects["Mantello"]
me = Mn.data
uvd = me.uv_layers[0].data
uvv = {}
for l in me.loops:
    uvv[l.vertex_index] = uvd[l.index].uv.copy()
for isl in islands(Mn):
    lo, hi = isl["lo"], isl["hi"]
    us = [uvv[i].x for i in isl["v"]]
    vs = [uvv[i].y for i in isl["v"]]
    nf = sum(1 for p in me.polygons if p.vertices[0] in set(isl["v"]))
    log("%-17s %5d verts %5d faces  lo (%.3f %.3f %.3f) hi (%.3f %.3f %.3f)  u %.3f..%.3f v %.3f..%.3f" % (
        isl["mat"], len(isl["v"]), nf, lo.x, lo.y, lo.z, hi.x, hi.y, hi.z, min(us), max(us), min(vs), max(vs)))
    if len(isl["v"]) == 76:
        zs = sorted(me.vertices[i].co.z for i in isl["v"])
        log("   z values:", " ".join("%.2f" % z for z in zs[::5]))
