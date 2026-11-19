exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
BONES = {b.name: (rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local) for b in rig.data.bones}
RIGID = ("E_", "V_borsa", "V_patta", "V_barattolo", "V_astuccio", "V_fibbia", "V_medaglione", "V_bottone",
         "V_borchia", "V_anello", "V_quadrante", "M_conch", "M_fermaglio", "V_stiv_fibbia", "V_laccio", "V_corda",
         "F_", "V_ginocchiera")


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


def weights(p, allowed, power=4.0, keep=3):
    ws = []
    for bn in allowed:
        a, b = BONES[bn]
        d = seg_dist(p, a, b) + 0.01
        ws.append((1.0 / d ** power, bn))
    ws.sort(reverse=True)
    ws = ws[:keep]
    tot = sum(w for w, _ in ws)
    return [(w / tot, bn) for w, bn in ws if w / tot > 0.02]


meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("_")]
missing = []
for ob in meshes:
    allowed = ob.get("bones", "")
    allowed = [b for b in allowed.split(",") if b in BONES] if allowed else []
    if not allowed:
        missing.append(ob.name)
        allowed = list(BONES.keys())
    ob.vertex_groups.clear()
    groups = {bn: ob.vertex_groups.new(name=bn) for bn in allowed}
    rigid = ob.name.startswith(RIGID)
    if rigid:
        c = sum((v.co for v in ob.data.vertices), V((0, 0, 0))) / max(1, len(ob.data.vertices))
        wc = weights(c, allowed)
        idx = [v.index for v in ob.data.vertices]
        for w, bn in wc:
            groups[bn].add(idx, w, "REPLACE")
    else:
        pw = 6.0 if ob.name.startswith("M_mantello") else 4.0
        for v in ob.data.vertices:
            for w, bn in weights(v.co, allowed, pw):
                groups[bn].add([v.index], w, "REPLACE")
log("senza lista ossa:", missing)

# join everything into one mesh
body = bpy.data.objects["C_busto"]
for o in bpy.context.selected_objects:
    o.select_set(False)
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = body
with bpy.context.temp_override(active_object=body, object=body, selected_objects=meshes,
                               selected_editable_objects=meshes):
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Esploratrice"
body.data.name = "Esploratrice"
# clean: merge exact duplicates only inside the joined mesh is not wanted (separate shells) -> skip
body.parent = rig
md = body.modifiers.new("Armature", "ARMATURE")
md.object = rig
# limit to 4 influences (Unity)
for v in body.data.vertices:
    gs = sorted(v.groups, key=lambda g: -g.weight)
    if len(gs) > 4:
        for g in gs[4:]:
            body.vertex_groups[g.group].remove([v.index])
log("oggetti uniti:", len(meshes), "vertici:", len(body.data.vertices), "triangoli:", tri_count())
log("gruppi:", len(body.vertex_groups), "materiali:", len(body.data.materials))
save()
