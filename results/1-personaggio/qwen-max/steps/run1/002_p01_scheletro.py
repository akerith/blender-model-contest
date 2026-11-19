import math

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'
scn.unit_settings.scale_length = 1.0

bpy.ops.object.light_add(type='SUN', location=(2, -3, 5))
sun = bpy.context.active_object
sun.name = "Sole"
sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(20))

w = scn.world or bpy.data.worlds.new("World")
scn.world = w
w.use_nodes = True
bg = w.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.35, 0.35, 0.38, 1)
bg.inputs[1].default_value = 1.0

bpy.ops.object.armature_add(location=(0, 0, 0))
arm = bpy.context.active_object
arm.name = "Scheletro"
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
eb.remove(eb[0])

def bone(name, head, tail, parent=None, connect=False):
    b = eb.new(name)
    b.head = head
    b.tail = tail
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    return b

bone("pelvis", (0, 0, 0.95), (0, 0, 1.06))
bone("spine", (0, 0, 1.06), (0, 0, 1.22), "pelvis", True)
bone("chest", (0, 0, 1.22), (0, 0, 1.42), "spine", True)
bone("neck", (0, 0, 1.42), (0, 0, 1.50), "chest", True)
bone("head", (0, 0, 1.50), (0, 0, 1.70), "neck", True)
for s, sx in (("L", 1), ("R", -1)):
    bone("clavicle." + s, (sx * 0.03, 0, 1.40), (sx * 0.18, 0, 1.42), "chest")
    bone("upper_arm." + s, (sx * 0.19, 0, 1.42), (sx * 0.30, 0, 1.16), "clavicle." + s)
    bone("forearm." + s, (sx * 0.30, 0, 1.16), (sx * 0.38, 0, 0.92), "upper_arm." + s, True)
    bone("hand." + s, (sx * 0.38, 0, 0.92), (sx * 0.43, 0, 0.79), "forearm." + s, True)
    bone("thigh." + s, (sx * 0.09, 0, 0.95), (sx * 0.10, 0, 0.50), "pelvis")
    bone("shin." + s, (sx * 0.10, 0, 0.50), (sx * 0.10, 0, 0.10), "thigh." + s, True)
    bone("foot." + s, (sx * 0.10, 0, 0.10), (sx * 0.10, -0.14, 0.02), "shin." + s, True)
bpy.ops.object.mode_set(mode='OBJECT')

log("Ossa:", len(arm.data.bones))
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")