import os
from mathutils import Vector

O = bpy.data.objects
for o in O:
    if o.type != 'MESH': continue
    if o.name.startswith(("Ciuffo", "Capelli")):
        for v in o.data.vertices:
            if v.co.z > 1.68: v.co.z = 1.68 + (v.co.z - 1.68) * 0.6
        o.data.update()
meshes = [o for o in O if o.type == 'MESH']
zs = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
log("ALTEZZA FINALE: %.4f" % max(zs))
arm = O["Scheletro"]
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.glb"
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True, export_skins=True,
                          export_animations=False)
log("GLB riscritto:", os.path.getsize(glb), "byte")
bpy.ops.wm.save_mainfile()
render_viste("finale_revisione_personaggio")
