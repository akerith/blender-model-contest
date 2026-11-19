exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())

# ---- empty scene, lights, world ----
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scn = bpy.context.scene
w = scn.world or bpy.data.worlds.new("World")
scn.world = w
try:
    w.use_nodes = True
except Exception:
    pass
bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
if bg:
    bg.inputs[0].default_value = (0.85, 0.85, 0.85, 1)
    bg.inputs[1].default_value = 0.9
try:
    scn.view_settings.view_transform = "Standard"
except Exception as e:
    log("view transform:", e)
for nm, rot, en in (("_gara_sole_fronte", (55, 0, -30), 2.5), ("_gara_sole_retro", (55, 0, 150), 2.0)):
    ld = bpy.data.lights.new(nm, "SUN")
    ld.energy = en
    lo = bpy.data.objects.new(nm, ld)
    scn.collection.objects.link(lo)
    lo.rotation_euler = (rad(rot[0]), rad(rot[1]), rad(rot[2]))

M = materials()

# ---- armature ----
ad = bpy.data.armatures.new("Scheletro")
arm = bpy.data.objects.new("Scheletro", ad)
scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
allb = {}
for nm, (h, t, p) in BONES.items():
    allb[nm] = (h, t, p)
    if nm.startswith("Left"):
        rn = "Right" + nm[4:]
        pp = ("Right" + p[4:]) if p and p.startswith("Left") else p
        allb[rn] = ((-h[0], h[1], h[2]), (-t[0], t[1], t[2]), pp)
for nm, (h, t, p) in allb.items():
    b = ad.edit_bones.new(nm)
    b.head, b.tail = h, t
for nm, (h, t, p) in allb.items():
    if p:
        ad.edit_bones[nm].parent = ad.edit_bones[p]
        if (Vector(allb[p][1]) - Vector(h)).length < 1e-4:
            ad.edit_bones[nm].use_connect = True
bpy.ops.object.mode_set(mode="OBJECT")
arm.show_in_front = True
log("bones:", len(ad.bones))

# ---- torso (tunic) ----
obj("torso", g_vloft(TORSO, n=24, cap0=True, cap1=True), M["tunic"], "Hips,Spine,Chest")
# leather corset/vest over the chest
VEST = [s for s in TORSO if 0.99 < s[0] < 1.30]
vest = [(1.00,) + vparams(TORSO, 1.00)[1:]] + VEST
vest = [(s[0], s[1], s[2], s[3] + 0.006, s[4] + 0.006, s[5] + 0.006) for s in vest]
obj("corpetto", g_vloft(vest, n=24, cap0=False, cap1=False), M["vest"], "Spine,Chest")

# ---- legs, boots ----
for side, sp_leg, sp_boot, sx in (("L", LEG, BOOT, 1), ("R", mspec(LEG), mspec(BOOT), -1)):
    pre = "Left" if sx > 0 else "Right"
    obj("gamba_" + side, g_vloft(sp_leg, n=14, cap0=False, cap1=True), M["pants"],
        "%sUpperLeg,%sLowerLeg,Hips" % (pre, pre))
    obj("stivale_" + side, g_vloft(sp_boot, n=14, cap0=False, cap1=False), M["leather"],
        "%sLowerLeg,%sFoot" % (pre, pre))
    # cuff at the top of the boot
    cuff = [(z, s[1], s[2], s[3] + o, s[4] + o, s[5] + o) for z, o in ((0.385, 0.0), (0.39, 0.009), (0.435, 0.011), (0.44, 0.0))
            for s in [vparams(sp_boot, z)]]
    obj("stivale_bordo_" + side, g_vloft(cuff, n=14, cap0=False, cap1=False), M["leatherd"], pre + "LowerLeg")
    # foot
    x0 = 0.166
    foot = [((x0, 0.072, 0.045), 0.030, 0.030), ((x0, 0.050, 0.052), 0.046, 0.046), ((x0, 0.0, 0.060), 0.051, 0.056),
            ((x0, -0.07, 0.048), 0.053, 0.043), ((x0, -0.14, 0.040), 0.055, 0.035), ((x0, -0.19, 0.036), 0.047, 0.031),
            ((x0, -0.218, 0.032), 0.026, 0.022)]
    g = g_loft(foot, n=14, axes=((1, 0, 0), (0, 0, 1)))
    sole = [((x0, 0.074, 0.008), 0.030, 0.012), ((x0, 0.050, 0.008), 0.046, 0.012), ((x0, 0.0, 0.008), 0.050, 0.012),
            ((x0, -0.07, 0.008), 0.053, 0.012), ((x0, -0.14, 0.008), 0.055, 0.012), ((x0, -0.19, 0.008), 0.047, 0.012),
            ((x0, -0.220, 0.008), 0.026, 0.012)]
    gs = g_loft(sole, n=8, axes=((1, 0, 0), (0, 0, 1)), sq=0.6)
    heel = g_box((x0, 0.040, 0.010), (0.078, 0.066, 0.028))
    gs = merge(gs, heel)
    g = rot_about(g, (x0, 0, 0), (0, 0, 1), -8)
    gs = rot_about(gs, (x0, 0, 0), (0, 0, 1), -8)
    if sx < 0:
        g, gs = mirror(g), mirror(gs)
    obj("piede_" + side, g, M["leather"], "%sFoot,%sToes" % (pre, pre))
    obj("suola_" + side, gs, M["dark"], "%sFoot,%sToes" % (pre, pre), sharp=40)

save()
render_viste("p01", viste=["fronte", "destra"])
