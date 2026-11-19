import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 1: Body proportions and pose (and matching skeleton bone names/positions)

# 1. Update Armature in place (rename bones to exact 10.5 names and set Group 1 positions)
arm = bpy.data.objects.get("Armatura")
if not arm:
    raise RuntimeError("Armatura non trovata!")

# Clear parent/modifiers temporarily while adjusting rest pose
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.parent == arm:
        obj.parent = None
        for mod in list(obj.modifiers):
            if mod.type == 'ARMATURE':
                obj.modifiers.remove(mod)

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='OBJECT')
arm.location = (0, 0, 0)
arm.rotation_euler = (0, 0, 0)
arm.scale = (1, 1, 1)

# Reset any pose transforms
bpy.ops.object.mode_set(mode='POSE')
for pb in arm.pose.bones:
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.rotation_euler = (0, 0, 0)
    pb.scale = (1, 1, 1)

bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

rename_map = {
    "Pelvis": "Hips",
    "Shoulder_L": "Shoulder.L",
    "Shoulder_R": "Shoulder.R",
    "UpperArm_L": "UpperArm.L",
    "UpperArm_R": "UpperArm.R",
    "Forearm_L": "LowerArm.L",
    "Forearm_R": "LowerArm.R",
    "Hand_L": "Hand.L",
    "Hand_R": "Hand.R",
    "Thigh_L": "UpperLeg.L",
    "Thigh_R": "UpperLeg.R",
    "Shin_L": "LowerLeg.L",
    "Shin_R": "LowerLeg.R",
    "Foot_L": "Foot.L",
    "Foot_R": "Foot.R",
    "Toe_L": "Toes.L",
    "Toe_R": "Toes.R",
}
for old_name, new_name in rename_map.items():
    if old_name in eb and new_name not in eb:
        eb[old_name].name = new_name

# Exact Group 1 & 10.5 coordinates
# L = +X, R = -X; facing -Y
def set_bone(name, head, tail, parent=None, connect=False):
    b = eb.get(name) or eb.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    b.roll = 0.0
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    else:
        b.parent = None
        b.use_connect = False
    return b

set_bone("Hips",  (0.0, 0.0, 0.90),  (0.0, 0.0, 1.01))
set_bone("Spine", (0.0, 0.0, 1.01),  (0.0, 0.0, 1.19), "Hips", True)
set_bone("Chest", (0.0, -0.005, 1.19), (0.0, 0.0, 1.45), "Spine", True)
set_bone("Neck",  (0.0, 0.0, 1.45),  (0.0, 0.0, 1.50), "Chest", True)
set_bone("Head",  (0.0, 0.0, 1.50),  (0.0, 0.0, 1.70), "Neck", True)

for side, s in (("L", 1.0), ("R", -1.0)):
    # Shoulder: neck base -> shoulder joint (Z 1.40)
    set_bone(f"Shoulder.{side}", (0.045 * s, 0.0, 1.425), (0.185 * s, 0.0, 1.40), "Chest", False)
    # UpperArm: shoulder (0.185, 0, 1.40) -> elbow (0.382, 0.01, 1.185) [len ~0.292, ~47 deg]
    set_bone(f"UpperArm.{side}", (0.185 * s, 0.0, 1.40), (0.382 * s, 0.010, 1.185), f"Shoulder.{side}", True)
    # LowerArm: elbow -> wrist (0.540, 0.0, 0.990) [len ~0.251, ~51 deg, subtle ~5 deg bend]
    set_bone(f"LowerArm.{side}", (0.382 * s, 0.010, 1.185), (0.540 * s, 0.0, 0.990), f"UpperArm.{side}", True)
    # Hand: wrist -> middle knuckle/fingertip guide (knuckles ~0.60, fingertips ~0.66, Z 0.86)
    set_bone(f"Hand.{side}", (0.540 * s, 0.0, 0.990), (0.605 * s, -0.005, 0.920), f"LowerArm.{side}", True)

    # Legs: hip (0.095, 0, 0.90) -> knee (0.112, -0.004, 0.49) -> ankle (0.130, 0.0, 0.08)
    set_bone(f"UpperLeg.{side}", (0.095 * s, 0.0, 0.90), (0.112 * s, -0.004, 0.49), "Hips", False)
    set_bone(f"LowerLeg.{side}", (0.112 * s, -0.004, 0.49), (0.130 * s, 0.0, 0.08), f"UpperLeg.{side}", True)
    set_bone(f"Foot.{side}",     (0.130 * s, 0.0, 0.08), (0.130 * s, -0.11, 0.025), f"LowerLeg.{side}", True)
    set_bone(f"Toes.{side}",     (0.130 * s, -0.11, 0.025), (0.130 * s, -0.19, 0.015), f"Foot.{side}", True)

bpy.ops.object.mode_set(mode='OBJECT')

# 2. Rebuild CorpoBase mesh in-place with exact Group 1 proportions
#    (head 0.15x0.19, chin 1.475 -> skull 1.66; neck 0.11 at 1.45..1.49;
#     shoulders 0.40 outside-outside at 1.40; chest 0.32x0.21 at 1.27;
#     waist 0.27x0.18 at 1.08; hips 0.34x0.22 at 0.90; crotch 0.86;
#     arms at Y~0, shoulder 0.185->elbow 0.382->wrist 0.540; legs to ankle 0.13, 0.08)

def add_loft(bm, rings, cap_start=True, cap_end=True):
    n = len(rings[0])
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(len(vr) - 1):
        r0, r1 = vr[i], vr[i + 1]
        for j in range(n):
            jn = (j + 1) % n
            bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
    if cap_start:
        bm.faces.new(vr[0][::-1])
    if cap_end:
        bm.faces.new(vr[-1])
    return vr

def make_oval(center, rx, ry, n=24):
    cx, cy, cz = center
    return [Vector((cx + rx * math.cos(2 * math.pi * i / n),
                    cy + ry * math.sin(2 * math.pi * i / n),
                    cz)) for i in range(n)]

def make_limb_rings(p0, p1, r_list, n=14):
    axis = (Vector(p1) - Vector(p0)).normalized()
    ref = Vector((0, -1, 0)) if abs(axis.y) < 0.9 else Vector((1, 0, 0))
    right = axis.cross(ref).normalized()
    fwd = right.cross(axis).normalized()
    rings = []
    for t, rx, ry in r_list:
        c = Vector(p0).lerp(Vector(p1), t)
        rings.append([c + right * (rx * math.cos(2 * math.pi * i / n))
                        + fwd * (ry * math.sin(2 * math.pi * i / n)) for i in range(n)])
    return rings

bm = bmesh.new()

# Torso + Neck (slightly slimmed inside clothes to avoid poke-through while keeping exact silhouette proportions)
# Crotch 0.86, hips 0.90 (0.34x0.22 -> jacket/pants outer is 0.34x0.22, body core 0.160x0.105),
# waist 1.08 (0.27x0.18 -> body core 0.128x0.084), chest 1.27 (0.32x0.21 -> body core 0.152x0.098),
# shoulders 1.40, neck 0.11 wide (rx=0.055, ry=0.052) at Z 1.45..1.49
torso_specs = [
    ((0.0, 0.010, 0.855), 0.145, 0.095),  # pelvis/crotch 0.86
    ((0.0, 0.015, 0.900), 0.162, 0.105),  # hip peak (bottom slightly back)
    ((0.0, 0.008, 0.980), 0.146, 0.094),  # lower waist
    ((0.0, 0.002, 1.080), 0.128, 0.084),  # waist narrowest (Z 1.08)
    ((0.0, -0.006, 1.180), 0.140, 0.092), # ribcage
    ((0.0, -0.012, 1.270), 0.152, 0.100), # chest fullest (Z 1.27, chest slightly forward)
    ((0.0, -0.005, 1.350), 0.155, 0.092), # upper chest
    ((0.0, 0.000, 1.405), 0.148, 0.082),  # shoulder line (Z 1.40)
    ((0.0, 0.000, 1.445), 0.056, 0.054),  # neck base (Z 1.45, width 0.11)
    ((0.0, 0.000, 1.495), 0.052, 0.052),  # neck top (Z 1.49)
]
add_loft(bm, [make_oval(c, rx, ry, 24) for c, rx, ry in torso_specs])

# Head egg base (chin 1.475 -> skull top 1.66, 0.15 wide rx=0.075, 0.19 deep ry=0.095)
head_specs = [
    ((0.0, -0.015, 1.475), 0.030, 0.042),  # chin 1.475
    ((0.0, -0.018, 1.500), 0.052, 0.068),  # jaw / mouth 1.505
    ((0.0, -0.012, 1.545), 0.068, 0.085),  # cheekbones / nose
    ((0.0, -0.005, 1.585), 0.075, 0.095),  # eyes level 1.585 (0.15 x 0.19)
    ((0.0,  0.002, 1.625), 0.071, 0.090),  # forehead
    ((0.0,  0.008, 1.652), 0.048, 0.064),  # upper skull
    ((0.0,  0.010, 1.660), 0.018, 0.024),  # top of skull 1.66
]
add_loft(bm, [make_oval(c, rx, ry, 24) for c, rx, ry in head_specs])

# Arms (upper arm + forearm, inside sleeves/gauntlets)
for s in (1.0, -1.0):
    p_sh = Vector((0.185 * s, 0.0, 1.40))
    p_el = Vector((0.382 * s, 0.010, 1.185))
    p_wr = Vector((0.540 * s, 0.0, 0.990))
    # Deltoid cap (outer edge hits ~0.200 -> 0.40 shoulder width)
    bmesh.ops.create_uvsphere(
        bm, u_segments=14, v_segments=10, radius=0.046,
        matrix=Matrix.Translation((0.158 * s, 0.0, 1.392)) @ Matrix.Diagonal((1.0, 0.92, 0.95, 1.0))
    )
    add_loft(bm, make_limb_rings(p_sh, p_el, [
        (0.0, 0.044, 0.042), (0.35, 0.040, 0.038), (0.75, 0.036, 0.034), (1.0, 0.033, 0.032)
    ], n=14))
    add_loft(bm, make_limb_rings(p_el, p_wr, [
        (0.0, 0.033, 0.032), (0.4, 0.031, 0.030), (0.8, 0.026, 0.024), (1.0, 0.023, 0.020)
    ], n=14))

# Legs (hip -> knee -> ankle, inside trousers/boots)
for s in (1.0, -1.0):
    p_hp = Vector((0.095 * s, 0.0, 0.90))
    p_kn = Vector((0.112 * s, -0.004, 0.49))
    p_an = Vector((0.130 * s, 0.0, 0.08))
    add_loft(bm, make_limb_rings(p_hp, p_kn, [
        (0.0, 0.070, 0.072), (0.4, 0.058, 0.060), (0.85, 0.048, 0.050), (1.0, 0.046, 0.048)
    ], n=14))
    add_loft(bm, make_limb_rings(p_kn, p_an, [
        (0.0, 0.046, 0.048), (0.35, 0.048, 0.050), (0.75, 0.038, 0.040), (1.0, 0.034, 0.036)
    ], n=14))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
obj_body = bpy.data.objects.get("CorpoBase")
bm.to_mesh(obj_body.data)
bm.free()
obj_body.data.update()

# 3. Temporarily re-fit existing outfit/accessory meshes to Group 1 landmarks
#    so rev_1 shows the full proportioned pose cleanly before Groups 2-9 detail them!

def map_z_torso(z):
    # Map old torso Z (0.84, 1.03, 1.18, 1.32, 1.44) -> new (0.86, 1.08, 1.27, 1.40, 1.46)
    old_pts = [0.70, 0.84, 1.03, 1.18, 1.32, 1.44]
    new_pts = [0.76, 0.86, 1.08, 1.27, 1.40, 1.46]
    if z <= old_pts[0]:
        return z - old_pts[0] + new_pts[0]
    if z >= old_pts[-1]:
        return z - old_pts[-1] + new_pts[-1]
    for i in range(len(old_pts) - 1):
        if old_pts[i] <= z <= old_pts[i + 1]:
            t = (z - old_pts[i]) / (old_pts[i + 1] - old_pts[i])
            return new_pts[i] + t * (new_pts[i + 1] - new_pts[i])
    return z

def map_arm_point(p):
    # Map old arm line (0.155*s, 0.015, 1.335) -> (0.52*s, -0.02, 0.97)
    # onto new arm line (0.185*s, 0.0, 1.40) -> (0.540*s, 0.0, 0.990)
    s = 1.0 if p.x >= 0 else -1.0
    a0 = Vector((0.155 * s, 0.015, 1.335))
    a1 = Vector((0.520 * s, -0.020, 0.970))
    b0 = Vector((0.185 * s, 0.0, 1.400))
    b1 = Vector((0.540 * s, 0.0, 0.990))
    va = a1 - a0
    t = (p - a0).dot(va) / va.length_squared
    perp = p - (a0 + va * t)
    # Remove old Y drift
    vb = b1 - b0
    # Rotate perp around Y slightly to match new arm pitch
    ang_old = math.atan2(va.z, va.x)
    ang_new = math.atan2(vb.z, vb.x)
    rot = Matrix.Rotation(-(ang_new - ang_old), 3, 'Y')
    return b0 + vb * t + (rot @ perp)

# Fit DettagliVolto & Capelli into skull 1.475..1.66 / hair 1.70 (temporary alignment for rev_1)
for name in ("DettagliVolto", "Capelli"):
    ob = bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            # Old head 1.465..1.695 -> new 1.475..1.66 (shift eyes 1.568 -> 1.585)
            tz = (v.co.z - 1.465) / (1.702 - 1.465)
            v.co.z = 1.475 + tz * (1.700 - 1.475)
            v.co.y += 0.008
        ob.data.update()

# Fit TunicaManiche
ob_tm = bpy.data.objects.get("TunicaManiche")
if ob_tm:
    for v in ob_tm.data.vertices:
        if abs(v.co.x) > 0.165 and v.co.z < 1.38:
            v.co = map_arm_point(v.co)
        else:
            v.co.z = map_z_torso(v.co.z)
            v.co.x *= 1.09
    ob_tm.data.update()

# Fit Guanti & BussolaPolso_L
for name in ("Guanti", "BussolaPolso_L"):
    ob = bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            v.co = map_arm_point(v.co)
        ob.data.update()

# Fit Pantaloni & StivaliGinocchiera (align X to leg line +-0.095 -> +-0.130 and Y=0 at ankle)
for name in ("Pantaloni", "StivaliGinocchiera"):
    ob = bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            s = 1.0 if v.co.x >= 0 else -1.0
            t_leg = max(0.0, min(1.0, (0.90 - v.co.z) / (0.90 - 0.08)))
            old_cx = (0.095 + 0.020 * t_leg) * s
            new_cx = (0.095 + 0.035 * t_leg) * s
            v.co.x += (new_cx - old_cx)
            if v.co.z > 0.05:
                v.co.y -= 0.015 * t_leg
        ob.data.update()

# Fit CinturaCinghie, AccessoriDestra, TuboMappe_L, CascoPalombaro, ZainoTubi
for name in ("CinturaCinghie",):
    ob = bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            v.co.z = map_z_torso(v.co.z)
            v.co.x *= 1.08
        ob.data.update()

for name, dx, dz in (("AccessoriDestra", -0.02, 0.05), ("TuboMappe_L", 0.02, 0.05),
                     ("CascoPalombaro", 0.0, 0.035), ("ZainoTubi", 0.0, 0.035)):
    ob = bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            v.co.x += dx
            v.co.z += dz
        ob.data.update()

ob_cape = bpy.data.objects.get("MantelloVerde")
if ob_cape:
    for v in ob_cape.data.vertices:
        v.co.z = map_z_torso(v.co.z) if v.co.z > 0.70 else v.co.z
        v.co.x *= 1.15
    ob_cape.data.update()

ob_md = bpy.data.objects.get("MantelloDettagli")
if ob_md:
    for v in ob_md.data.vertices:
        v.co.z = map_z_torso(v.co.z)
        v.co.x *= 1.08
    ob_md.data.update()

# Shade smooth CorpoBase
bpy.ops.object.select_all(action='DESELECT')
obj_body.select_set(True)
bpy.context.view_layer.objects.active = obj_body
bpy.ops.object.shade_smooth()

# Save and render rev_1
bpy.ops.wm.save_mainfile()

# Log heights & proportions check
pts = [obj_body.matrix_world @ v.co for v in obj_body.data.vertices]
log(f"CorpoBase Z range: {min(p.z for p in pts):.4f} .. {max(p.z for p in pts):.4f}")
log(f"Armatura bones ({len(arm.data.bones)}): {[b.name for b in arm.data.bones]}")
render_viste("rev_1")
