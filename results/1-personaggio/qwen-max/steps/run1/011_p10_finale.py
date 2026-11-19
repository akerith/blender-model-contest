import os

body = bpy.data.objects["Personaggio"]
arm = bpy.data.objects["Scheletro"]
zs = [ (body.matrix_world @ v.co).z for v in body.data.vertices ]
log("Altezza:", round(max(zs), 3), "m | Tri:", sum(len(p.vertices) - 2 for p in body.data.polygons), "| Ossa:", len(arm.data.bones))

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.glb"
try:
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_skins=True,
                              export_animations=False)
except Exception as e:
    log("Export fallito, provo ad abilitare l'addon glTF:", repr(e))
    bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_skins=True,
                              export_animations=False)
log("GLB scritto:", os.path.exists(glb), os.path.getsize(glb) if os.path.exists(glb) else 0, "byte")

render_viste("finale_personaggio")
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")