exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
body = bpy.data.objects["Esploratrice"]
rig = bpy.data.objects["Scheletro"]
zmax = max(v.co.z for v in body.data.vertices)
k = 1.70 / zmax
for v in body.data.vertices:
    v.co = v.co * k
body.data.update()
bpy.context.view_layer.objects.active = rig
for o in bpy.context.selected_objects:
    o.select_set(False)
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for b in rig.data.edit_bones:
    b.head = b.head * k
    b.tail = b.tail * k
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()
pts = [v.co for v in body.data.vertices]
log("scala %.4f -> altezza %.3f m" % (k, max(p.z for p in pts) - min(p.z for p in pts)))
save()
for o in bpy.context.selected_objects:
    o.select_set(False)
body.select_set(True)
rig.select_set(True)
glb = os.path.join(LAVORO, "personaggio.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_yup=True,
                          export_apply=False, export_skins=True, export_animations=False)
log("glb:", "%.1f KB" % (os.path.getsize(glb) / 1024))

# check the glb by importing it into a scratch scene
tmp = bpy.data.scenes.new("_verifica")
win = bpy.context.window_manager.windows[0]
old = win.scene
win.scene = tmp
try:
    bpy.ops.import_scene.gltf(filepath=glb)
    for o in tmp.objects:
        if o.type == "MESH":
            ws = [o.matrix_world @ v.co for v in o.data.vertices]
            log("glb reimportato: mesh", o.name, "tri", sum(len(p.vertices) - 2 for p in o.data.polygons),
                "altezza %.3f" % (max(p.z for p in ws) - min(p.z for p in ws)), "gruppi", len(o.vertex_groups))
        if o.type == "ARMATURE":
            log("glb reimportato: armatura", o.name, "ossa", len(o.data.bones))
finally:
    win.scene = old
    for o in list(tmp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(tmp)
save()
render_viste("finale_personaggio")
