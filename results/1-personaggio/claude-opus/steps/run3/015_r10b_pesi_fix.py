# GROUP 10 fix: in the bone test a hair clump moved with the arm and a gauntlet piece stayed behind.
# Head/hair rigid on Head; gauntlets/hands/sleeves only on arm bones; capes only on body bones. Test again.
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
for nm in ("Testa", "Capelli"):
    weight_all(obj(nm), "Head")
for s in (".L", ".R"):
    bind(obj("Guanto" + s), ["UpperArm" + s, "LowerArm" + s, "Hand" + s])
    bind(obj("Mano" + s), ["LowerArm" + s, "Hand" + s])
    bind(obj("Braccio" + s), ["Shoulder" + s, "UpperArm" + s, "LowerArm" + s, "Chest"])
bind(obj("Mantello"), ["Chest", "Spine", "Hips", "Shoulder.L", "Shoulder.R", "UpperLeg.L", "UpperLeg.R"], power=3.0)
bind(obj("Mantellina"), ["Chest", "Shoulder.L", "Shoulder.R", "Neck"], power=3.0)
bind(obj("Colletto_mantello"), ["Chest", "Neck"])
# objects that still have a vertex with no weight
empty = []
for o in chars():
    n = sum(1 for v in o.data.vertices if not any(g.weight > 0 for g in v.groups))
    if n:
        empty.append("%s(%d)" % (o.name, n))
log("vertici senza peso:", empty)
bpy.ops.wm.save_mainfile()
pb = rig.pose.bones["UpperArm.L"]
pb.rotation_mode = "XYZ"
pb.rotation_euler = (0, 0, math.radians(30))
bpy.context.view_layer.update()
render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])
pb.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
log("osso rimesso a 0")
bpy.ops.wm.save_mainfile()
