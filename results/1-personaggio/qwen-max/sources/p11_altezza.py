import os

body = bpy.data.objects["Personaggio"]
arm = bpy.data.objects["Scheletro"]
f = 1.70 / 1.715
for v in body.data.vertices:
    v.co *= f
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
for b in arm.data.edit_bones:
    b.head *= f
    b.tail *= f
bpy.ops.object.mode_set(mode='OBJECT')
zs = [v.co.z for v in body.data.vertices]
log("Altezza corretta:", round(max(zs), 4))

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.glb"
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True, export_skins=True,
                          export_animations=False)
log("GLB riscritto:", os.path.getsize(glb), "byte")
render_viste("finale_personaggio")
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")