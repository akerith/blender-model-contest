# GROUP 1 (continued) - move the skeleton to the new joints (mesh was re-shaped in the previous step)
exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\rev_lib.py", encoding="utf-8").read())
rig = bpy.data.objects["Scheletro"]
for o in bpy.context.selected_objects:
    o.select_set(False)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
NEWB = {"Hips": ((0, 0, 0.95), (0, 0, 1.10)), "Spine": ((0, 0, 1.10), (0, 0, 1.27)),
        "Chest": ((0, 0, 1.27), (0, 0, 1.45)), "Neck": ((0, 0, 1.45), (0, -0.005, 1.50)),
        "Head": ((0, -0.005, 1.50), (0, -0.005, 1.70))}
for s, sx in ((".L", 1), (".R", -1)):
    m = lambda v: tuple(V((v[0] * sx, v[1], v[2])))
    NEWB["Shoulder" + s] = (m((0.02, 0.0, 1.44)), m(SH1))
    NEWB["UpperArm" + s] = (m(SH1), m(ELB1))
    NEWB["LowerArm" + s] = (m(ELB1), m(WRI1))
    NEWB["Hand" + s] = (m(WRI1), m(KNU1))
    NEWB["UpperLeg" + s] = (m(HIP1), m(KNEE1))
    NEWB["LowerLeg" + s] = (m(KNEE1), m(ANK1))
    NEWB["Foot" + s] = (m(ANK1), m(BALL1))
    NEWB["Toes" + s] = (m(BALL1), m(TOE1))
with bpy.context.temp_override(active_object=rig, object=rig, selected_objects=[rig], selected_editable_objects=[rig]):
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones
    for b in eb:
        b.use_connect = False
    for name, (h, t) in NEWB.items():
        eb[name].head = h
        eb[name].tail = t
    for name in NEWB:
        b = eb[name]
        if b.parent and (b.parent.tail - b.head).length < 1e-4:
            b.use_connect = True
    bpy.ops.armature.select_all(action="SELECT")
    bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Y")
    bpy.ops.object.mode_set(mode="OBJECT")
for b in rig.data.bones:
    log("osso %-11s (%.3f, %.3f, %.3f) -> (%.3f, %.3f, %.3f)" % ((b.name,) + tuple(b.head_local) + tuple(b.tail_local)))


def zr(name):
    o = obj(name)
    a, b = bbox(o)
    return "%s x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f]" % (name, a.x, b.x, a.y, b.y, a.z, b.z)


for nm in ("Testa", "Capelli", "Collo", "Busto", "Braccio.L", "Guanto.L", "Mano.L", "Pantaloni", "Stivale.L",
           "Mantello", "Elmo", "Cintura", "Cinturone"):
    if obj(nm):
        log(zr(nm))
# torso widths at the key heights (Busto)
bo = obj("Busto")
for z in (0.90, 1.08, 1.27, 1.40):
    vs = [v.co for v in bo.data.vertices if abs(v.co.z - z) < 0.012]
    if vs:
        log("busto z=%.2f larghezza %.3f profondita %.3f" % (z, max(p.x for p in vs) - min(p.x for p in vs),
                                                           max(p.y for p in vs) - min(p.y for p in vs)))
finish(1)
