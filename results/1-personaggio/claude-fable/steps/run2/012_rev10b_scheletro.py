exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 10 (second half) - normals, skeleton with the exact names, binding, bone test
arm = bpy.data.objects["Scheletro"]
MESH = [o for o in scn.objects if o.type == "MESH"]
for o in MESH:
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.material_slot_remove_unused()
    if o.name in ("Testa", "Elmo", "Fianchi", "Bracciale"):      # closed shells: outside facing out
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
    log("%s: %d material slots" % (o.name, len(o.data.materials)))

# ---- 10.5 skeleton: the round-1 bones renamed and moved to the new joints; finger and cape bones removed ----
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.parent = None
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
SIDE = ("Shoulder", "UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot", "Toes")
for b in list(eb):
    for pre, suf in (("Left", ".L"), ("Right", ".R")):
        if b.name.startswith(pre) and b.name[len(pre):] in SIDE:
            b.name = b.name[len(pre):] + suf
for b in list(eb):
    if b.name not in ("Hips", "Spine", "Chest", "Neck", "Head") and b.name[:-2] not in SIDE:
        eb.remove(b)
KNEE, ANK = Vector((0.1055, 0, 0.49)), Vector((0.126, 0.005, 0.08))
POS = {"Hips": ((0, 0, 0.95), (0, 0, 1.10), None), "Spine": ((0, 0, 1.10), (0, 0, 1.27), "Hips"),
       "Chest": ((0, 0, 1.27), (0, 0, 1.45), "Spine"), "Neck": ((0, 0, 1.45), (0, 0, 1.50), "Chest"),
       "Head": ((0, 0, 1.50), (0, 0, 1.70), "Neck"),
       "Shoulder.L": ((0.025, 0, 1.43), tuple(SHN), "Chest"), "UpperArm.L": (tuple(SHN), tuple(ELN), "Shoulder.L"),
       "LowerArm.L": (tuple(ELN), tuple(WRN), "UpperArm.L"), "Hand.L": (tuple(WRN), tuple(WRN + U2 * 0.09), "LowerArm.L"),
       "UpperLeg.L": ((0.085, 0, 0.90), tuple(KNEE), "Hips"), "LowerLeg.L": (tuple(KNEE), tuple(ANK), "UpperLeg.L"),
       "Foot.L": (tuple(ANK), (0.13, -0.12, 0.02), "LowerLeg.L"), "Toes.L": ((0.13, -0.12, 0.02), (0.13, -0.19, 0.02), "Foot.L")}
for nm, (h, t, par) in list(POS.items()):
    if nm.endswith(".L"):
        POS[nm[:-2] + ".R"] = ((-h[0], h[1], h[2]), (-t[0], t[1], t[2]), (par[:-2] + ".R") if par.endswith(".L") else par)
for nm in POS:
    if nm not in eb:
        eb.new(nm)
    eb[nm].use_connect = False
for nm, (h, t, par) in POS.items():
    eb[nm].head, eb[nm].tail, eb[nm].roll = h, t, 0.0
for nm, (h, t, par) in POS.items():
    if par:
        eb[nm].parent = eb[par]
        eb[nm].use_connect = (Vector(POS[par][1]) - Vector(h)).length < 1e-5
bpy.ops.object.mode_set(mode="OBJECT")
log("bones:", len(arm.data.bones), sorted(b.name for b in arm.data.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}


def near_w(p):
    ds = []
    for n, (h, t) in segs.items():
        ax = t - h
        s = max(0.0, min(1.0, (p - h).dot(ax) / ax.length_squared))
        ds.append(((p - (h + ax * s)).length, n))
    ds.sort()
    w = [(n, 1.0 / (d + 0.004) ** 4) for d, n in ds[:2]]
    tot = sum(x for _, x in w)
    return [(n, x / tot) for n, x in w if x / tot > 0.05]


# ---- 10.6 binding ----
RIGID = {"Elmo": "Chest", "Fianchi": "Hips", "Bracciale": "LowerArm.L", "Testa": "Head"}
for o in MESH:
    for m in list(o.modifiers):
        o.modifiers.remove(m)
    o.vertex_groups.clear()
    if o.name in RIGID:
        vg = o.vertex_groups.new(name=RIGID[o.name])
        vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
        o.parent = arm
        md = o.modifiers.new("Armature", "ARMATURE")
        md.object = arm
        log("%s -> %s (weight 1.0, %d vertices)" % (o.name, RIGID[o.name], len(o.data.vertices)))
    else:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        try:
            bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        except Exception as e:
            log("automatic weights error on", o.name, e)
        if not any(m.type == "ARMATURE" for m in o.modifiers):
            o.parent = arm
            md = o.modifiers.new("Armature", "ARMATURE")
            md.object = arm
        unw = [v.index for v in o.data.vertices if not any(g.weight > 1e-4 for g in v.groups)]
        for i in unw:
            for n, x in near_w(o.data.vertices[i].co):
                (o.vertex_groups.get(n) or o.vertex_groups.new(name=n)).add([i], x, "REPLACE")
        log("%s: automatic weights, %d groups, %d vertices filled by nearest bone" % (o.name, len(o.vertex_groups), len(unw)))
arm.hide_render = True
# ---- test: UpperArm.L raised by 30 degrees ----
bpy.context.view_layer.objects.active = arm
pb = arm.pose.bones["UpperArm.L"]
h = arm.data.bones["UpperArm.L"].head_local
base = pb.matrix.copy()
pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(rad(-30), 4, "Y") @ Matrix.Translation(-h) @ base
bpy.context.view_layer.update()
render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])
for b in arm.pose.bones:
    b.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
salva()
render_viste("rev_10", viste=["fronte", "retro"])
