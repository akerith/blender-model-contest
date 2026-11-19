import bpy
import os

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = LAVORO + r"\personaggio.blend"
glb_path = LAVORO + r"\personaggio.glb"

bpy.ops.wm.open_mainfile(filepath=blend_path)

# Seleziona solo Armatura e Mesh (esclude luci/camere) per l'esportazione GLB
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type in ('MESH', 'ARMATURE'):
        obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects.get("Armatura")

win = bpy.context.window_manager.windows[0]
area = next((a for a in win.screen.areas if a.type == 'VIEW_3D'), win.screen.areas[0])
region = next((r for r in area.regions if r.type == 'WINDOW'), area.regions[0])

with bpy.context.temp_override(window=win, area=area, region=region):
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_skins=True,
        export_all_influences=False,
        export_materials='EXPORT'
    )

size_kb = os.path.getsize(glb_path) / 1024.0
log(f"Esportato {glb_path} ({size_kb:.1f} KB)")

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("finale_personaggio")
