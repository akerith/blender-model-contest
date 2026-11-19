# GROUP 10 - materials pass, normals/smoothing, triangle budget, skeleton check, new binding (automatic weights)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
# ---- 10.1 materials still with round-1 values ----
set_mat("cuoio_scuro", (0.24, 0.15, 0.08), 0.65)
set_mat("corda", (0.70, 0.62, 0.47), 0.95)
set_mat("pantaloni", (0.22, 0.19, 0.16), 0.9)
for nm in ("lino", "camicia", "mantello", "mantello_medio", "mantello_sporco", "metallo"):
    m = bpy.data.materials.get(nm)
    if m and m.users == 0:
        bpy.data.materials.remove(m)
# every object keeps only the material slots it really uses
for o in chars():
    used = sorted({p.material_index for p in o.data.polygons})
    mats = [o.data.materials[i] for i in used if i < len(o.data.materials)]
    remap = {old: new for new, old in enumerate(used)}
    idx = [remap.get(p.material_index, 0) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:
        # appended duplicates (name.001) -> the original material
        base = m.name.split(".")[0] if m and "." in m.name else (m.name if m else None)
        o.data.materials.append(bpy.data.materials.get(base) or m)
    for p, i in zip(o.data.polygons, idx):
        p.material_index = i
bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
bad = []
for m in bpy.data.materials:
    if m.users and m.node_tree and m.node_tree.nodes.get("Principled BSDF"):
        c = m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
        if max(c[:3]) < 0.004 or min(c[:3]) > 0.98:
            bad.append(m.name)
log("materiali:", len([m for m in bpy.data.materials if m.users]), "| nero/bianco puro:", bad)

# ---- 10.4 triangles: fewer segments on hair locks, rope, wraps, small loops (never hands or face) ----
for nm, ratio in (("Capelli", 0.45), ("Corda", 0.5), ("Fasce.L", 0.5), ("Fasce.R", 0.5), ("Mantellina", 0.6),
                  ("Elmo_corda", 0.5), ("Elmo", 0.85)):
    o = obj(nm)
    md = o.modifiers.new("dec", "DECIMATE")
    md.ratio = ratio
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
        bpy.ops.object.modifier_apply(modifier="dec")

# ---- 10.2 normals out, smooth shading; metal/leather keep real edges (30 degrees) ----
ORGANIC = ("Testa", "Capelli", "Collo", "Mano", "Mantello", "Mantellina", "Colletto_mantello", "Corda", "Busto",
           "Pantaloni", "Braccio", "Tunica", "Stracci", "Fasce", "Elmo_corda", "Tubi", "Rotolo")
for o in chars():
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = True
    if not o.name.startswith(ORGANIC):
        try:
            o.data.set_sharp_from_angle(angle=math.radians(30))
        except Exception as e:
            log("sharp:", o.name, e)
    o.data.update()

# ---- 10.6 binding: automatic weights for the body/clothes, fixed weights for rigid gear ----
RIGID = {"Elmo": "Chest", "Tubi": "Chest", "Rotolo": "Chest", "Imbracatura": "Chest", "Elmo_corda": "Chest",
         "Borse": "Hips", "Corda": "Hips", "Astuccio": "Hips", "Barattolo": "Hips", "Borsa_tonda": "Hips",
         "Quadrante": "LowerArm.L"}
auto = [o for o in chars() if o.name not in RIGID]
for o in chars():
    for md in list(o.modifiers):
        if md.type == "ARMATURE":
            o.modifiers.remove(md)
    o.parent = None
for o in auto:
    o.vertex_groups.clear()
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in auto:
    o.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
sel = auto + [rig]
with bpy.context.temp_override(active_object=rig, object=rig, selected_objects=sel, selected_editable_objects=sel):
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
fallback = []
for o in auto:
    empty = sum(1 for v in o.data.vertices if not any(g.weight > 0 for g in v.groups))
    if empty > 0:
        # heat weighting failed on some loose parts: give those vertices distance weights
        rigb = {b.name: (b.head_local, b.tail_local) for b in rig.data.bones}
        names = [b for b in rigb]

        def segd(p, a, b):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            return (p - (a + ab * t)).length
        for v in o.data.vertices:
            if any(g.weight > 0 for g in v.groups):
                continue
            ws = sorted(((1.0 / (segd(v.co, *rigb[b]) + 0.01) ** 4, b) for b in names), reverse=True)[:3]
            tot = sum(w for w, _ in ws)
            for w, b in ws:
                gg = o.vertex_groups.get(b) or o.vertex_groups.new(name=b)
                gg.add([v.index], w / tot, "REPLACE")
        fallback.append("%s(%d)" % (o.name, empty))
log("pesi automatici:", len(auto), "oggetti | completati a distanza:", fallback)
for nm, bone in RIGID.items():
    o = obj(nm)
    if o:
        weight_all(o, bone)
for o in chars():
    if not any(md.type == "ARMATURE" for md in o.modifiers):
        md = o.modifiers.new("Armature", "ARMATURE")
        md.object = rig
    o.parent = rig
# at most 4 bones per vertex (Unity)
for o in chars():
    for v in o.data.vertices:
        gs = sorted(v.groups, key=lambda g: -g.weight)
        for g in gs[4:]:
            o.vertex_groups[g.group].remove([v.index])

# ---- 10.5 skeleton check ----
need = ["Hips", "Spine", "Chest", "Neck", "Head"] + [b + s for s in (".L", ".R") for b in
        ("Shoulder", "UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot", "Toes")]
log("ossa:", len(rig.data.bones), "| mancanti:", [b for b in need if b not in rig.data.bones])
tri_report()
bpy.ops.wm.save_mainfile()
render_viste("rev_10")

# ---- bone test: UpperArm.L +30 degrees ----
pb = rig.pose.bones["UpperArm.L"]
pb.rotation_mode = "XYZ"
pb.rotation_euler = (0, 0, math.radians(30))
bpy.context.view_layer.update()
render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])
pb.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
log("osso rimesso a 0")
bpy.ops.wm.save_mainfile()
