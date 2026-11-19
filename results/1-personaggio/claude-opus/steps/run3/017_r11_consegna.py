# DELIVERY - save, export personaggio.glb (armature included, +Y up), check it, final renders
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
for pb in rig.pose.bones:   # rest pose
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.rotation_euler = (0, 0, 0)
    pb.scale = (1, 1, 1)
bpy.context.view_layer.update()
meshes = chars()
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
log("altezza: %.3f m (z da %.3f a %.3f) | larghezza: %.3f" % (max(p.z for p in pts) - min(p.z for p in pts),
    min(p.z for p in pts), max(p.z for p in pts), max(p.x for p in pts) - min(p.x for p in pts)))
log("oggetti mesh:", len(meshes), "| ossa:", len(rig.data.bones),
    "| max ossa per vertice:", max(len(v.groups) for o in meshes for v in o.data.vertices))
tri_report()
bpy.ops.wm.save_mainfile()
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in meshes:
    o.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
glb = os.path.join(LAVORO, "personaggio.glb")
with bpy.context.temp_override(active_object=rig, selected_objects=meshes + [rig]):
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=False, export_skins=True, export_animations=False)
log("glb: %.1f KB" % (os.path.getsize(glb) / 1024))
# check: import the glb in a scratch scene
tmp = bpy.data.scenes.new("_verifica")
win = bpy.context.window_manager.windows[0]
old = win.scene
win.scene = tmp
try:
    bpy.ops.import_scene.gltf(filepath=glb)
    nm, nt, nb = 0, 0, 0
    zs = []
    for o in tmp.objects:
        if o.type == "MESH":
            nm += 1
            nt += sum(len(p.vertices) - 2 for p in o.data.polygons)
            zs += [(o.matrix_world @ v.co).z for v in o.data.vertices]
        if o.type == "ARMATURE":
            nb = len(o.data.bones)
    log("glb reimportato: mesh %d, triangoli %d, ossa %d, altezza %.3f" % (nm, nt, nb, max(zs) - min(zs)))
finally:
    win.scene = old
    for o in list(tmp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(tmp)
render_viste("finale_revisione_personaggio")
