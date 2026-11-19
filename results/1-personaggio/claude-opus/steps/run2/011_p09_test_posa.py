exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
pb = rig.pose.bones
from mathutils import Euler


def rot_world(bn, axis, deg):
    """rotate a pose bone around a world axis (rest pose based)."""
    b = pb[bn]
    R = rig.data.bones[bn].matrix_local.to_3x3()
    q_world = Quaternion(V(axis), math.radians(deg))
    q_local = (R.inverted() @ q_world.to_matrix() @ R).to_quaternion()
    b.rotation_mode = "QUATERNION"
    b.rotation_quaternion = q_local @ b.rotation_quaternion


rot_world("UpperArm.L", (0, 1, 0), -55)      # raise left arm
rot_world("LowerArm.L", (0, 0, 1), 60)       # bend left elbow forward
rot_world("UpperArm.R", (1, 0, 0), -40)      # right arm forward
rot_world("LowerArm.R", (1, 0, 0), -50)
rot_world("UpperLeg.L", (1, 0, 0), -45)      # left thigh forward
rot_world("LowerLeg.L", (1, 0, 0), 70)       # knee bend
rot_world("Head", (0, 0, 1), 30)             # turn head
rot_world("Spine", (0, 1, 0), 8)
bpy.context.view_layer.update()
render_viste("p09_posa", viste=["fronte", "tre_quarti", "destra"])
for b in pb:
    b.rotation_quaternion = (1, 0, 0, 0)
    b.rotation_euler = (0, 0, 0)
    b.location = (0, 0, 0)
bpy.context.view_layer.update()
log("posa di prova resa e azzerata")
