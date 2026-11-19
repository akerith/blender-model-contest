import bpy
import math

# Group 10.6 Bone Test: rotate UpperArm.L by 30 degrees, render "rev_prova_osso" (fronte, tre_quarti),
# check sleeve, glove, bracer and hand follow without tearing, then reset bone to 0 and save.

arm = bpy.data.objects.get("Armatura")
if not arm:
    raise RuntimeError("Armatura missing!")

bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=[arm]):
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm.pose.bones["UpperArm.L"]
    old_mode = pb.rotation_mode
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (math.radians(30.0), 0.0, 0.0)
    bpy.context.view_layer.update()

    render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])

    # Put bone back to 0
    pb.rotation_euler = (0.0, 0.0, 0.0)
    pb.rotation_mode = old_mode
    pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_mainfile()
log("Bone test rev_prova_osso complete and UpperArm.L reset to 0.")
