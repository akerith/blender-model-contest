# DELIVERY fix: re-export the glb exactly as in round 1 (no context override) and check bones + skin
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
meshes = chars()
log("rig nascosto:", rig.hide_get(), rig.hide_viewport, "| visibile:", rig.visible_get(), "| in scena:", rig.name in bpy.context.scene.objects)
rig.hide_set(False)
rig.hide_viewport = False
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in meshes:
    o.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
log("selezionati:", len(bpy.context.selected_objects), "| rig selezionato:", rig.select_get())
glb = os.path.join(LAVORO, "personaggio.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_yup=True,
                          export_apply=False, export_skins=True, export_animations=False)
log("glb: %.1f KB" % (os.path.getsize(glb) / 1024))
tmp = bpy.data.scenes.new("_verifica")
win = bpy.context.window_manager.windows[0]
old = win.scene
win.scene = tmp
try:
    bpy.ops.import_scene.gltf(filepath=glb)
    nm, nt, nb, sk = 0, 0, 0, 0
    for o in tmp.objects:
        if o.type == "MESH":
            nm += 1
            nt += sum(len(p.vertices) - 2 for p in o.data.polygons)
            if any(md.type == "ARMATURE" for md in o.modifiers) and len(o.vertex_groups):
                sk += 1
        if o.type == "ARMATURE":
            nb = len(o.data.bones)
    log("glb reimportato: mesh %d (con pelle sulle ossa %d), triangoli %d, ossa %d" % (nm, sk, nt, nb))
finally:
    win.scene = old
    for o in list(tmp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(tmp)
bpy.ops.wm.save_mainfile()
