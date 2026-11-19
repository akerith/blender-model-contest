import math

arm = bpy.data.objects["Scheletro"]
body = bpy.data.objects["Corpo"]

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
acc = [o for o in meshes if o != body]
bpy.ops.object.select_all(action='DESELECT')
for o in acc:
    o.select_set(True)
bpy.context.view_layer.objects.active = acc[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
log("Pesi automatici sul corpo:", len(body.vertex_groups))

for o in meshes:
    if o == body:
        continue
    bone = o.get("bone")
    bone2 = o.get("bone2")
    if bone2:
        g1 = o.vertex_groups.new(name=bone)
        g2 = o.vertex_groups.new(name=bone2)
        for v in o.data.vertices:
            if v.co.z < 0.10:
                g2.add([v.index], 1.0, 'REPLACE')
            else:
                g1.add([v.index], 1.0, 'REPLACE')
    elif bone:
        g = o.vertex_groups.new(name=bone)
        g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')

bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
    if o != body:
        o.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = "Personaggio"
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
log("Tri totali:", tris, "| gruppi:", len(body.vertex_groups), "| modificatori:", [m.type for m in body.modifiers])

bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["upper_arm.L"]
pb.rotation_mode = 'XYZ'
pb.rotation_euler = (0, 0, math.radians(25))
bpy.ops.object.mode_set(mode='OBJECT')
render_viste("p07_posa", viste=["fronte"])
bpy.ops.object.mode_set(mode='POSE')
pb.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")