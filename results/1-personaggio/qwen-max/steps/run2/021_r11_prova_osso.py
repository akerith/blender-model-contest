import math
from mathutils import Vector

O = bpy.data.objects
for n in ("Mano.L.001", "Mano.R.001", "Stivale.L.001", "Stivale.R.001"):
    o = O.get(n)
    if o:
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector([min(c[i] for c in cs) for i in range(3)])
        mx = Vector([max(c[i] for c in cs) for i in range(3)])
        log("%s bbox (%.3f,%.3f,%.3f)-(%.3f,%.3f,%.3f)" % (n, mn.x, mn.y, mn.z, mx.x, mx.y, mx.z))

arm = O["Scheletro"]
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["UpperArm.L"]
pb.rotation_mode = 'XYZ'
pb.rotation_euler = (0, 0, math.radians(30))
bpy.ops.object.mode_set(mode='OBJECT')
render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])
bpy.ops.object.mode_set(mode='POSE')
pb.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')
log("Prova osso UpperArm.L 30 gradi: render fatte, osso riportato a 0")
bpy.ops.wm.save_mainfile()
