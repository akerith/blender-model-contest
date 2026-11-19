exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
scn = bpy.context.scene
arm = bpy.data.objects["Scheletro"]
remove("Personaggio")

segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}


def dist_eff(p, h, t):
    ax = t - h
    L = ax.length
    ax = ax / L
    s = (p - h).dot(ax)
    radial = ((p - h) - ax * s).length
    exc = -s if s < 0 else (s - L if s > L else 0.0)
    return math.sqrt(exc * exc + (0.35 * radial) ** 2) + 0.004


def weights_for(p, names):
    if len(names) == 1:
        return {names[0]: 1.0}
    w = {n: 1.0 / dist_eff(p, *segs[n]) ** 4 for n in names}
    tot = sum(w.values())
    w = {n: v / tot for n, v in w.items() if v / tot > 0.06}
    tot = sum(w.values())
    return {n: v / tot for n, v in w.items()}


def cape_weights(p):
    side = "Left" if p.x > 0 else "Right"
    ax = abs(p.x)
    if p.z > 1.20 or (p.y < 0.03 and p.z > 0.95):
        t = min(max((ax - 0.17) / 0.20, 0.0), 1.0) * 0.85
        w = {"Chest": 1 - t, side + "UpperArm": t}
    else:
        keys = [(1.18, "Chest"), (0.92, "Cape1"), (0.62, "Cape2"), (0.32, "Cape3")]
        if p.z >= keys[0][0]:
            w = {"Chest": 1.0}
        elif p.z <= keys[-1][0]:
            w = {"Cape3": 1.0}
        else:
            for (za, na), (zb, nb) in zip(keys, keys[1:]):
                if zb <= p.z <= za:
                    t = (za - p.z) / (za - zb)
                    w = {na: 1 - t, nb: t}
    return {n: v for n, v in w.items() if v > 0.001}


parts = [o for o in scn.objects if o.type == "MESH" and "bones" in o.keys()]
log("parts:", len(parts))
for o in parts:
    names = [n.strip() for n in o["bones"].split(",")]
    o.vertex_groups.clear()
    acc = {}
    for v in o.data.vertices:
        w = cape_weights(v.co) if names == ["CAPE"] else weights_for(v.co, names)
        for n, x in w.items():
            acc.setdefault(n, []).append((v.index, x))
    for n, lst in acc.items():
        if n not in segs:
            raise Exception("unknown bone " + n + " in " + o.name)
        vg = o.vertex_groups.new(name=n)
        for i, x in lst:
            vg.add([i], x, "REPLACE")

# ---- join everything into one mesh ----
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
main = bpy.data.objects["torso"]
bpy.context.view_layer.objects.active = main
bpy.ops.object.join()
main.name = "Personaggio"
main.data.name = "Personaggio"
main.parent = arm
md = main.modifiers.new("Armature", "ARMATURE")
md.object = arm
main.data.uv_layers.active_index = 0
main.data.uv_layers[0].active_render = True
log("uv layers:", [u.name for u in main.data.uv_layers])
# exact height 1.70 m: scale skeleton and mesh together
zs0 = [v.co.z for v in main.data.vertices]
k = 1.70 / (max(zs0) - min(zs0))
M4 = Matrix.Translation((0, 0, -min(zs0) * k)) @ Matrix.Scale(k, 4)
main.data.transform(M4)
arm.data.transform(M4)
main.data.update()
log("scaled by %.4f" % k)
unw = sum(1 for v in main.data.vertices if not v.groups)
log("vertices without weights:", unw)
log("materials:", len(main.data.materials), "vertices:", len(main.data.vertices))

# ---- size check ----
zs = [v.co.z for v in main.data.vertices]
log("height: %.3f m (min z %.3f)" % (max(zs) - min(zs), min(zs)))

# ---- test pose: does the skeleton move the mesh? ----
bpy.context.view_layer.objects.active = arm
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"
test = {"LeftUpperArm": (0, 0, -35), "RightUpperArm": (0, 0, 60), "RightLowerArm": (0, 0, 50), "LeftLowerArm": (60, 0, 0),
        "LeftHandIndex1": (0, 0, 60), "RightHandMiddle1": (0, 0, -60), "LeftUpperLeg": (-50, 0, 0), "LeftLowerLeg": (70, 0, 0), "Head": (0, 30, 0), "Spine": (10, 0, 8), "Cape2": (-20, 0, 0)}
for n, r in test.items():
    pb[n].rotation_euler = (rad(r[0]), rad(r[1]), rad(r[2]))
bpy.context.view_layer.update()
arm.hide_render = True
render_viste("p07_posa", viste=["fronte", "tre_quarti"])
for b in pb:
    b.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

save("personaggio")

# ---- export glb ----
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
main.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=LAV + "\\personaggio.glb", export_format="GLB", use_selection=True,
                          export_yup=True, export_skins=True, export_animations=False, export_apply=False)
import os
log("glb size: %.2f MB" % (os.path.getsize(LAV + "\\personaggio.glb") / 1e6))
log("FINAL triangles:", sum(len(p.vertices) - 2 for p in main.data.polygons), "bones:", len(arm.data.bones))
render_viste("finale_personaggio")
import shutil
for v in ("fronte", "destra", "retro", "sinistra", "tre_quarti", "alto"):
    shutil.copyfile(OUTBOX + "\\finale_personaggio_%s.png" % v, LAV + "\\finale_personaggio_%s.png" % v)

shot("p07_viso", (0, 0, 1.52), 0.42, d=(0.25, -1, 0.05))
shot("p07_alto_corpo", (0, 0, 1.25), 0.95, d=(0.6, -1, 0.25))
shot("p07_gambe", (0, 0, 0.42), 0.95, d=(-0.5, -1, 0.2))
shot("p07_dietro", (0, 0.1, 1.1), 0.95, d=(-0.5, 1, 0.3))
shot("p07_sotto", (0, 0, 0.8), 1.5, d=(0.3, -1, -0.8))
