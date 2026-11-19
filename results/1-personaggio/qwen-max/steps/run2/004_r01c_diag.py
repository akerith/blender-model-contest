from mathutils import Vector
for o in bpy.data.objects:
    if o.type == 'MESH':
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        cs = [Vector(c) for c in o.bound_box]
        mn = Vector([min(c[i] for c in cs) for i in range(3)])
        mx = Vector([max(c[i] for c in cs) for i in range(3)])
        mats = ",".join(sorted(set(m.name for m in o.data.materials if m)))
        log("%s | tri %d | z %.3f..%.3f | x %.3f..%.3f | mats %s | sel %s" %
            (o.name, t, mn.z, mx.z, mn.x, mx.x, mats, o.select_get()))
    else:
        log("%s | %s" % (o.name, o.type))
