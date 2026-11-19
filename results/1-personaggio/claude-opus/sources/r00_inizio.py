# revision step 0: inventory of every object + start renders (nothing is changed)
for ob in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    tri = sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == "MESH" else 0
    log("%-22s %-9s tri=%6d loc=(%.3f, %.3f, %.3f) dim=(%.3f, %.3f, %.3f)" % (
        ob.name, ob.type, tri, ob.location.x, ob.location.y, ob.location.z,
        ob.dimensions.x, ob.dimensions.y, ob.dimensions.z))
render_viste("rev_inizio")
