exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())

# empty scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.armatures, bpy.data.lights):
    for it in list(coll):
        coll.remove(it)

scn = bpy.context.scene
# lights + world
w = scn.world or bpy.data.worlds.new("World")
scn.world = w
w.use_nodes = True
bg = w.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.42, 0.44, 0.46, 1)
bg.inputs[1].default_value = 0.6
for nm, typ, loc, rot, en in [("_luce_sole", "SUN", (2, -3, 5), (0.75, 0.0, 0.45), 3.5),
                              ("_luce_retro", "SUN", (-2, 3, 4), (-0.9, 0.0, 2.6), 1.5)]:
    ld = bpy.data.lights.new(nm, typ)
    ld.energy = en
    lo = bpy.data.objects.new(nm, ld)
    lo.location = loc
    lo.rotation_euler = rot
    scn.collection.objects.link(lo)

# ---------------- armature ----------------
arm = bpy.data.armatures.new("Scheletro")
rig = bpy.data.objects.new("Scheletro", arm)
scn.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.edit_bones


def bone(name, h, t, parent=None, conn=False):
    b = eb.new(name)
    b.head = h
    b.tail = t
    if parent:
        b.parent = eb[parent]
        b.use_connect = conn
    return b


bone("Hips", (0, 0, 0.90), (0, 0, 1.02))
bone("Spine", (0, 0, 1.02), (0, 0, 1.18), "Hips", True)
bone("Chest", (0, 0, 1.18), (0, 0, 1.40), "Spine", True)
bone("Neck", (0, 0, 1.43), (0, -0.005, 1.53), "Chest")
bone("Head", (0, -0.005, 1.53), (0, -0.005, 1.70), "Neck", True)
for s, sx in ((".L", 1), (".R", -1)):
    def m(p):
        return V((p.x * sx, p.y, p.z))
    bone("Shoulder" + s, (0.03 * sx, -0.01, 1.40), m(SH), "Chest")
    bone("UpperArm" + s, m(SH), m(ELB), "Shoulder" + s, True)
    bone("LowerArm" + s, m(ELB), m(WRI), "UpperArm" + s, True)
    bone("Hand" + s, m(WRI), m(HAND_TIP), "LowerArm" + s, True)
    bone("UpperLeg" + s, m(HIP), m(KNEE), "Hips")
    bone("LowerLeg" + s, m(KNEE), m(ANK), "UpperLeg" + s, True)
    bone("Foot" + s, m(ANK), m(V((0.118, -0.10, 0.03))), "LowerLeg" + s, True)
    bone("Toes" + s, m(V((0.118, -0.10, 0.03))), m(V((0.122, -0.175, 0.025))), "Foot" + s, True)
# roll: keep arm bones' Z axis pointing back for nicer rotation
bpy.ops.armature.select_all(action="SELECT")
bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Y")
bpy.ops.object.mode_set(mode="OBJECT")
rig.show_in_front = True
rig.hide_render = True

# ---------------- body ----------------
clear("C_")
# torso (vest area), rings bottom -> top: (z, rx, rf, rb, yoff)
T = [(0.80, 0.10, 0.07, 0.07, 0.0), (0.85, 0.150, 0.090, 0.105, 0.005), (0.91, 0.168, 0.098, 0.115, 0.01),
     (0.97, 0.150, 0.088, 0.100, 0.005), (1.03, 0.134, 0.084, 0.088, 0.0), (1.10, 0.137, 0.090, 0.088, 0.0),
     (1.16, 0.145, 0.105, 0.090, 0.0), (1.22, 0.155, 0.125, 0.094, 0.0), (1.28, 0.160, 0.112, 0.097, 0.0),
     (1.34, 0.168, 0.095, 0.097, 0.0), (1.39, 0.170, 0.080, 0.090, 0.005), (1.43, 0.13, 0.065, 0.075, 0.01),
     (1.46, 0.07, 0.05, 0.055, 0.01)]
loft("C_busto", [((0, t[4], t[0]), t[1], t[2], t[3]) for t in TORSO], seg=28, mat="gilet",
     bones=["Hips", "Spine", "Chest", "Neck", "Shoulder.L", "Shoulder.R", "UpperLeg.L", "UpperLeg.R"])

# neck
loft("C_collo", [((0, 0.01, 1.42), 0.052, 0.05, 0.05), ((0, 0.005, 1.50), 0.046, 0.045, 0.048),
                 ((0, 0.0, 1.55), 0.048, 0.045, 0.05)], seg=14, mat="pelle", bones=["Neck", "Head", "Chest"])

# legs (trousers): hip -> ankle
for s, sx in ((".L", 1), (".R", -1)):
    def L(t, r, rf, rb, dy=0.0):
        p = HIP.lerp(KNEE, t) if t <= 1 else KNEE.lerp(ANK, t - 1)
        return ((p.x * sx, p.y + dy, p.z), r, rf, rb)
    ob = loft("C_gamba" + s, [L(-0.05, 0.088, 0.09, 0.10), L(0.0, 0.088, 0.088, 0.10), L(0.25, 0.082, 0.080, 0.085),
                              L(0.55, 0.072, 0.068, 0.068), L(0.85, 0.060, 0.058, 0.058), L(1.0, 0.055, 0.058, 0.055),
                              L(1.2, 0.058, 0.058, 0.066), L(1.5, 0.052, 0.050, 0.055), L(1.8, 0.042, 0.042, 0.045),
                              L(2.0, 0.036, 0.038, 0.04)], seg=16, mat="pantaloni",
              bones=["Hips", "UpperLeg" + s, "LowerLeg" + s])

# arms
for s, sx in ((".L", 1), (".R", -1)):
    def A(p, r, rf=None, rb=None):
        return ((p.x * sx, p.y, p.z), r, rf or r, rb or r)
    # upper arm: starts inside shoulder
    loft("C_braccio" + s, [A(SH - ARM_D * 0.03 + V((0, 0, -0.01)), 0.058), A(SH + ARM_D * 0.03, 0.056),
                           A(SH.lerp(ELB, 0.45), 0.048), A(ELB, 0.040), A(ELB.lerp(WRI, 0.5), 0.036),
                           A(WRI, 0.028)], seg=14, mat="lino",
         bones=["Shoulder" + s, "UpperArm" + s, "LowerArm" + s, "Chest"])

    # hand (glove): palm + fingers + thumb
    d = V((ARM_D.x * sx, 0, ARM_D.z))
    pn = V((PALM_N.x * sx, 0, PALM_N.z))
    W = V((WRI.x * sx, WRI.y, WRI.z))
    K = W + d * 0.085
    loft("C_palmo" + s, [(W - d * 0.01, 0.022, 0.028, 0.028), (W + d * 0.03, 0.020, 0.040, 0.038),
                         (K - d * 0.005, 0.016, 0.044, 0.040), (K + d * 0.01, 0.013, 0.040, 0.036)],
         seg=12, mat="cuoio_scuro", bones=["Hand" + s, "LowerArm" + s])
    for i, (off, ln, rr) in enumerate([(-0.030, 0.072, 0.0105), (-0.010, 0.082, 0.011), (0.010, 0.077, 0.0105),
                                       (0.027, 0.062, 0.0095)]):
        base = K + V((0, off, 0)) - d * 0.005
        pts = [base]
        dirv = d + V((0, off * 0.8, 0))
        for j in range(3):
            dirv = (dirv.normalized() + pn * 0.28).normalized()
            pts.append(pts[-1] + dirv * ln / 3)
        loft("C_dito%d%s" % (i, s), [(pts[0], rr, rr, rr), (pts[1], rr, rr, rr), (pts[2], rr * 0.95, rr * 0.95, rr * 0.95),
                                     (pts[3], rr * 0.85, rr * 0.85, rr * 0.85)], seg=8, mat="cuoio_scuro",
             bones=["Hand" + s])
    tb = W + d * 0.025 + V((0, -0.03, 0))
    td = (d * 0.6 + V((0, -0.7, 0)) + pn * 0.35).normalized()
    t2 = (d * 0.9 + V((0, -0.3, 0)) + pn * 0.3).normalized()
    loft("C_pollice" + s, [(tb, 0.014, 0.014, 0.014), (tb + td * 0.035, 0.012, 0.012, 0.012),
                           (tb + td * 0.035 + t2 * 0.03, 0.0105, 0.0105, 0.0105)], seg=8, mat="cuoio_scuro",
         bones=["Hand" + s])

# head
H = [(1.478, 0.018, 0.015, 0.015, -0.062), (1.495, 0.040, 0.034, 0.030, -0.050), (1.52, 0.049, 0.050, 0.050, -0.032),
     (1.55, 0.060, 0.066, 0.065, -0.018), (1.58, 0.070, 0.072, 0.080, -0.008), (1.61, 0.074, 0.074, 0.088, -0.002),
     (1.64, 0.075, 0.074, 0.090, 0.002), (1.665, 0.068, 0.066, 0.083, 0.005), (1.685, 0.050, 0.048, 0.064, 0.008),
     (1.697, 0.025, 0.024, 0.034, 0.01)]
loft("C_testa", [((0, h[4], h[0]), h[1], h[2], h[3]) for h in H], seg=24, mat="pelle", bones=["Head", "Neck"])

# boots (simple foot) so she stands
for s, sx in ((".L", 1), (".R", -1)):
    x = 0.115 * sx
    loft("C_piede" + s, [((x, 0.055, 0.05), 0.035, 0.035, 0.035), ((x, 0.03, 0.06), 0.045, 0.05, 0.05),
                         ((x, -0.05, 0.045), 0.048, 0.04, 0.04), ((x, -0.13, 0.035), 0.045, 0.03, 0.03),
                         ((x, -0.175, 0.03), 0.032, 0.022, 0.022)], seg=14, mat="cuoio_scuro",
         bones=["Foot" + s, "Toes" + s, "LowerLeg" + s], up=V((0, 0, 1)))

log("triangoli:", tri_count())
log("ossa:", len(arm.bones))
save()
render_viste("p01", viste=["fronte", "destra", "tre_quarti"])
