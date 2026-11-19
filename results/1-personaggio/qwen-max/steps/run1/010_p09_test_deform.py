import math
from mathutils import Vector

arm = bpy.data.objects["Scheletro"]
body = bpy.data.objects["Personaggio"]
gi = body.vertex_groups["hand.L"].index

def media_mano():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    pts = [v.co for v in me.vertices if any(g.group == gi and g.weight > 0.5 for g in v.groups)]
    c = sum(pts, Vector()) / len(pts)
    ev.to_mesh_clear()
    return c

rest = media_mano()
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["upper_arm.L"]
pb.rotation_mode = 'XYZ'
pb.rotation_euler = (math.radians(45), 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.update()
posed = media_mano()
log("Mano a riposo:", tuple(round(x, 3) for x in rest), "| in posa:", tuple(round(x, 3) for x in posed), "| delta:", round((posed - rest).length, 3))
render_viste("p09_deform", viste=["tre_quarti"])
bpy.ops.object.mode_set(mode='POSE')
pb.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")