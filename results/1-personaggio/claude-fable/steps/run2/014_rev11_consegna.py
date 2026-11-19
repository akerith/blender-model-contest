exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# DELIVERY: save the .blend, export the .glb with the armature, final renders
import os, shutil
arm = bpy.data.objects["Scheletro"]
for b in arm.pose.bones:
    b.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
MESH = [o for o in scn.objects if o.type == "MESH"]
tot = 0
for o in MESH:
    t = sum(len(p.vertices) - 2 for p in o.data.polygons)
    tot += t
    lo, hi = bbox(o)
    log("%-10s %6d tris | %2d materials | %2d groups | no weight: %d | z %.3f..%.3f" % (
        o.name, t, len(o.data.materials), len(o.vertex_groups), sum(1 for v in o.data.vertices if not v.groups), lo.z, hi.z))
zs = [v.co.z for o in MESH for v in o.data.vertices]
xs = [v.co.x for o in MESH for v in o.data.vertices]
log("TOTAL triangles: %d | bones: %d | height %.3f (z %.3f..%.3f) | width %.3f" % (
    tot, len(arm.data.bones), max(zs) - min(zs), min(zs), max(zs), max(xs) - min(xs)))
bpy.ops.wm.save_mainfile()
bpy.ops.object.select_all(action="DESELECT")
for o in MESH + [arm]:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=LAV + "\\personaggio.glb", export_format="GLB", use_selection=True,
                          export_yup=True, export_skins=True, export_animations=False, export_apply=False)
log("glb size: %.2f MB" % (os.path.getsize(LAV + "\\personaggio.glb") / 1e6))
render_viste("finale_revisione_personaggio")
for v in ("fronte", "destra", "retro", "sinistra", "tre_quarti", "alto"):
    shutil.copyfile(OUTBOX + "\\finale_revisione_personaggio_%s.png" % v, LAV + "\\finale_revisione_personaggio_%s.png" % v)
