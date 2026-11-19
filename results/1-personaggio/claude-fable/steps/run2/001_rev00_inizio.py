for o in bpy.context.scene.objects:
    t = sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == "MESH" else 0
    log("%s | %s | tris %d | loc (%.3f, %.3f, %.3f) | dim (%.3f, %.3f, %.3f)" % (
        o.name, o.type, t, o.location.x, o.location.y, o.location.z, o.dimensions.x, o.dimensions.y, o.dimensions.z))
render_viste("rev_inizio")
