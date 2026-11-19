import math
from mathutils import Vector

scn = bpy.context.scene
log("OGGETTI DELLA SCENA (giro 1):")
for o in scn.objects:
    if o.type == 'MESH':
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector([min(p[i] for p in bb) for i in range(3)])
        mx = Vector([max(p[i] for p in bb) for i in range(3)])
        log("%s | MESH | tri %d | loc (%.3f, %.3f, %.3f) | dim (%.3f, %.3f, %.3f) | zmin %.3f zmax %.3f"
            % (o.name, tris, o.location.x, o.location.y, o.location.z,
               mx.x - mn.x, mx.y - mn.y, mx.z - mn.z, mn.z, mx.z))
    else:
        log("%s | %s | loc (%.3f, %.3f, %.3f)" % (o.name, o.type, o.location.x, o.location.y, o.location.z))
arm = bpy.data.objects.get("Scheletro")
if arm:
    log("OSSA:", ", ".join(b.name for b in arm.data.bones))
tot = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in scn.objects if o.type == 'MESH')
log("TRI TOTALI:", tot)
render_viste("rev_inizio")
