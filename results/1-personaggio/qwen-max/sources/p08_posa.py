import math

arm = bpy.data.objects["Scheletro"]
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["upper_arm.L"]
pb.rotation_mode = 'XYZ'
pb.rotation_euler = (0, 0, math.radians(25))
bpy.ops.object.mode_set(mode='OBJECT')
render_viste("p08_posa", viste=["fronte"])
bpy.ops.object.mode_set(mode='POSE')
pb.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')
log("Posa di prova ok, riportata a riposo")
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")