import os
from mathutils import Vector

O = bpy.data.objects
arm = O["Scheletro"]
# il mantello non deve seguire le braccia: tolgo i pesi braccio, resto su Chest/Spine
ARM_GROUPS = {"Shoulder.L", "Shoulder.R", "UpperArm.L", "UpperArm.R", "LowerArm.L", "LowerArm.R", "Hand.L", "Hand.R"}
for nm in ("Mantello", "MantelloSpalle"):
    o = O[nm]
    idxs = [g.index for g in o.vertex_groups if g.name in ARM_GROUPS]
    chest = o.vertex_groups.get("Chest") or o.vertex_groups.new(name="Chest")
    for v in o.data.vertices:
        keep = [(g.group, g.weight) for g in v.groups if g.group not in idxs]
        tot = sum(w for _, w in keep)
        for g in list(v.groups):
            o.vertex_groups[g.group].remove([v.index])
        if tot > 1e-6:
            for gi, w in keep:
                o.vertex_groups[gi].add([v.index], w / tot, 'REPLACE')
        else:
            chest.add([v.index], 1.0, 'REPLACE')
    log("Pesi braccio rimossi da", nm)

meshes = [o for o in O if o.type == 'MESH']
tot = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
zs = [ (o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices ]
log("TRI TOTALI:", tot, "| OSSA:", len(arm.data.bones), "| ALTEZZA: %.3f" % max(zs))
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.glb"
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True, export_skins=True,
                          export_animations=False)
log("GLB scritto:", os.path.getsize(glb), "byte")
bpy.ops.wm.save_mainfile()
render_viste("finale_revisione_personaggio")
