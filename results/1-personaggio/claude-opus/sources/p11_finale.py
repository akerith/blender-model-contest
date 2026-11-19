exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
scn = bpy.context.scene
body = bpy.data.objects["Esploratrice"]
rig = bpy.data.objects["Scheletro"]

# softer light, a bit more contrast so the colours read like the drawing
bpy.data.objects["_luce_sole"].data.energy = 2.6
bpy.data.objects["_luce_retro"].data.energy = 1.2
scn.world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
try:
    scn.view_settings.look = "AgX - Medium High Contrast"
except Exception as e:
    log("look non disponibile:", e)

# measurements
pts = [body.matrix_world @ v.co for v in body.data.vertices]
zmin = min(p.z for p in pts)
zmax = max(p.z for p in pts)
xs = max(p.x for p in pts) - min(p.x for p in pts)
log("altezza: %.3f m (da %.3f a %.3f), larghezza braccia: %.3f m" % (zmax - zmin, zmin, zmax, xs))
log("triangoli:", tri_count(), "| ossa:", len(rig.data.bones), "| materiali:", len(body.data.materials))
# max influences check
mx = max(len(v.groups) for v in body.data.vertices)
nog = sum(1 for v in body.data.vertices if len(v.groups) == 0)
log("max ossa per vertice:", mx, "| vertici senza peso:", nog)

save()
# export glb (Y up, metres)
for o in bpy.context.selected_objects:
    o.select_set(False)
body.select_set(True)
rig.select_set(True)
glb = os.path.join(LAVORO, "personaggio.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_yup=True,
                          export_apply=False, export_skins=True, export_animations=False)
log("glb:", glb, "%.1f KB" % (os.path.getsize(glb) / 1024))
render_viste("finale_personaggio")
