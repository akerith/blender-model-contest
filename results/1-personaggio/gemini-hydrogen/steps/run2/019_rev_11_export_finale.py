import bpy
import os

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = os.path.join(LAVORO, "personaggio.blend")
glb_path = os.path.join(LAVORO, "personaggio.glb")

arm = bpy.data.objects.get("Armatura")
if not arm:
    raise RuntimeError("Armatura missing!")

# Ensure rest pose (all pose bones at 0)
arm.hide_viewport = False
arm.hide_set(False)
with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=[arm]):
    bpy.ops.object.mode_set(mode='POSE')
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.update()

# Ensure CapeAlbedo image is packed cleanly for both .blend and GLB
cape_img = bpy.data.images.get("CapeAlbedo")
if cape_img and not cape_img.packed_file:
    cape_img.pack()

# Final stats verification
depsgraph = bpy.context.evaluated_depsgraph_get()
total_tris = 0
min_z, max_z = 999.0, -999.0
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type == 'MESH':
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        t = len(me.loop_triangles)
        total_tris += t
        for v in me.vertices:
            wz = (obj.matrix_world @ v.co).z
            min_z = min(min_z, wz)
            max_z = max(max_z, wz)
        ev.to_mesh_clear()
        log(f"  {obj.name}: {t} tris")

log(f"FINAL_TOTAL_TRIS={total_tris}")
log(f"FINAL_HEIGHT={max_z - min_z:.4f} m (Z={min_z:.4f}..{max_z:.4f})")
log(f"FINAL_BONES={len(arm.data.bones)}")

# Save personaggio.blend (D1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log(f"Saved {blend_path}")

# Export personaggio.glb (D2)
bpy.ops.object.select_all(action='DESELECT')
export_objs = [o for o in bpy.data.objects if o.type in ('MESH', 'ARMATURE')]
for o in export_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm

with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=export_objs):
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_skins=True,
        export_all_influences=False,
        export_materials='EXPORT',
    )

size_kb = os.path.getsize(glb_path) / 1024.0
log(f"Exported {glb_path} ({size_kb:.1f} KB)")

# Render finale_revisione_personaggio (D3)
render_viste("finale_revisione_personaggio")
