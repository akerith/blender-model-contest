exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 10 (fix after the bone test): the long cape followed the arm too much, and the body mesh (automatic weights
# failed there) gets weights piece by piece from the bones that can really move it
arm = bpy.data.objects["Scheletro"]
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}


def dseg(p, n):
    h, t = segs[n]
    ax = t - h
    s = max(0.0, min(1.0, (p - h).dot(ax) / ax.length_squared))
    return (p - (h + ax * s)).length


def wts(p, allowed):
    ds = sorted((dseg(p, n), n) for n in allowed)[:2]
    w = [(n, 1.0 / (d + 0.004) ** 4) for d, n in ds]
    tot = sum(x for _, x in w)
    return [(n, x / tot) for n, x in w if x / tot > 0.05]


def assign(o, table):
    o.vertex_groups.clear()
    acc = {}
    for i, lst in table.items():
        tot = sum(x for _, x in lst)
        for n, x in lst:
            acc.setdefault(n, []).append((i, x / tot))
    for n, lst in acc.items():
        vg = o.vertex_groups.new(name=n)
        for i, x in lst:
            vg.add([i], x, "REPLACE")


C = bpy.data.objects["Corpo"]
tab, cnt = {}, {"arm": 0, "leg": 0, "torso": 0}
for isl in islands(C):
    c = isl["c"]
    s = ".L" if c.x > 0 else ".R"
    for i in isl["v"]:
        p = C.data.vertices[i].co
        if abs(c.x) > 0.16 and c.z > 0.8:
            al, k = ["Shoulder" + s, "UpperArm" + s, "LowerArm" + s, "Hand" + s], "arm"
        elif c.z < 0.84 and abs(c.x) > 0.04:
            al, k = ["UpperLeg" + s, "LowerLeg" + s, "Foot" + s, "Toes" + s], "leg"
        else:
            al, k = ["Hips", "Spine", "Chest", "Neck"], "torso"
            if isl["mat"] == "pelle":
                al.append("Head")
            if p.z < 0.92 and abs(p.x) > 0.02:
                al.append("UpperLeg" + (".L" if p.x > 0 else ".R"))
        tab[i] = wts(p, al)
        cnt[k] += 1
assign(C, tab)
log("Corpo weights by piece:", cnt, "groups", len(C.vertex_groups))

Mn = bpy.data.objects["Mantello"]
me = Mn.data
coll = set(i for isl in islands(Mn) if len(isl["v"]) <= 200 for i in isl["v"])
uvx = {}
for l in me.loops:
    uvx[l.vertex_index] = me.uv_layers[0].data[l.index].uv.x
gn = {g.index: g.name for g in Mn.vertex_groups}
tab, nl = {}, 0
for v in me.vertices:
    z = v.co.z
    if v.index in coll:
        tab[v.index] = [("Chest", 1.0)]
    elif 0.2499 < uvx.get(v.index, 0) < 0.7501:        # long cape: hangs from the torso
        nl += 1
        if z >= 1.27:
            tab[v.index] = [("Chest", 1.0)]
        elif z >= 1.10:
            t = (1.27 - z) / 0.17
            tab[v.index] = [("Chest", 1 - t + 1e-4), ("Spine", t + 1e-4)]
        elif z >= 0.95:
            t = (1.10 - z) / 0.15
            tab[v.index] = [("Spine", 1 - t + 1e-4), ("Hips", t + 1e-4)]
        else:
            tab[v.index] = [("Hips", 1.0)]
    else:                                               # shoulder cape: keeps the automatic weights (no head)
        w = [(gn[g.group], g.weight) for g in v.groups if g.weight > 0.02 and gn[g.group] not in ("Head", "Neck")]
        tab[v.index] = w or [("Chest", 1.0)]
assign(Mn, tab)
log("Mantello: long-cape vertices on Chest/Spine/Hips:", nl, "- shoulder cape keeps automatic weights; groups", len(Mn.vertex_groups))
for o in (C, Mn):
    log(o.name, "vertices without weight:", sum(1 for v in o.data.vertices if not v.groups))

bpy.context.view_layer.objects.active = arm
pb = arm.pose.bones["UpperArm.L"]
h = arm.data.bones["UpperArm.L"].head_local
base = pb.matrix.copy()
pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(rad(-30), 4, "Y") @ Matrix.Translation(-h) @ base
bpy.context.view_layer.update()
render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])
arm.pose.bones["UpperLeg.R"].rotation_mode = "XYZ"
pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
pl = arm.pose.bones["UpperLeg.R"]
hl = arm.data.bones["UpperLeg.R"].head_local
pl.matrix = Matrix.Translation(hl) @ Matrix.Rotation(rad(35), 4, "X") @ Matrix.Translation(-hl) @ pl.matrix.copy()
arm.pose.bones["Head"].matrix_basis = Matrix.Rotation(rad(25), 4, "Y")
bpy.context.view_layer.update()
render_viste("rev_prova_osso2", viste=["tre_quarti"])
for b in arm.pose.bones:
    b.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
salva()
