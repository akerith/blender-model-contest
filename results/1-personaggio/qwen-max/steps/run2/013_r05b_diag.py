from mathutils import Vector
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector([min(c[i] for c in cs) for i in range(3)])
    mx = Vector([max(c[i] for c in cs) for i in range(3)])
    if mx.x > 0.70 or mn.x < -0.70 or mx.z > 1.71 or mn.z < -0.001:
        log("FUORI: %s | x %.3f..%.3f z %.3f..%.3f | loc (%.3f,%.3f,%.3f) rot (%.2f,%.2f,%.2f)" %
            (o.name, mn.x, mx.x, mn.z, mx.z, o.location.x, o.location.y, o.location.z,
             o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z))
h = bpy.data.objects["Mano.L"]
cs = [h.matrix_world @ Vector(c) for c in h.bound_box]
log("Mano.L bbox:", tuple(round(v, 3) for v in cs[0]), tuple(round(v, 3) for v in cs[6]))
log("Mano.L vert:", len(h.data.vertices), "loc", tuple(h.location), "rot", tuple(round(a, 2) for a in h.rotation_euler))
