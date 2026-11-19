import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 8: Legs and boots
# - 8.1 Loose grey-brown trousers (0.15 thigh, 0.11 above knee, 3 back-of-knee creases)
# - 8.2 Round leather knee pads on BOTH knees (0.11 across, 0.025 thick, centre Z=0.50) + upper/lower straps
# - 8.3 Shin wraps: 3 overlapping cream cloth rings (Z 0.40..0.46)
# - 8.4 Tall brown leather boots (ankle Z=0.08 -> shaft Z=0.42, 0.12 top / 0.09 ankle, 0.04 folded cuff,
#       eyelet rows + 8 crossed laces Z 0.10..0.40, ankle strap Z=0.09 & top strap Z=0.38 with brass buckles,
#       sculpted foot 0.27 long x 0.10 wide from Y +0.08 to -0.19, 0.02 dark sole, 0.03 heel block at Z=0)

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.65, metallic=0.0, spec=0.35):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        for lnk in list(mat.node_tree.links):
            if lnk.to_socket == bsdf.inputs["Base Color"]:
                mat.node_tree.links.remove(lnk)
        lin = tuple(srgb_to_lin(x) for x in col_srgb)
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat

mat_pants        = set_mat_srgb("PantaloniScuri", (0.22, 0.19, 0.16), roughness=0.88, spec=0.18)
mat_wrap         = set_mat_srgb("FasceCrema", (0.82, 0.76, 0.64), roughness=0.90, spec=0.18)
mat_boot         = set_mat_srgb("PelleStivali", (0.30, 0.18, 0.10), roughness=0.64, spec=0.35)
mat_boot_dark    = set_mat_srgb("PelleScura", (0.20, 0.12, 0.07), roughness=0.66, spec=0.32)
mat_sole         = set_mat_srgb("SuolaStivali", (0.12, 0.08, 0.06), roughness=0.70, spec=0.25)
mat_lace         = set_mat_srgb("LacciStivali", (0.55, 0.42, 0.28), roughness=0.82, spec=0.22)
mat_brass        = set_mat_srgb("Ottone", (0.62, 0.45, 0.20), roughness=0.35, metallic=1.0, spec=0.50)

# Quick Group 7/4 polish:
# 1) Pull upper chest brass buckles back slightly (+0.008 in Y) so they sit 100% flush on cross straps (not floating)
ob_belt = bpy.data.objects.get("CinturaCinghie")
if ob_belt:
    for poly in ob_belt.data.polygons:
        if poly.material_index == 2 and 1.275 <= poly.center.z <= 1.325 and poly.center.y < -0.07:
            for vi in poly.vertices:
                ob_belt.data.vertices[vi].co.y += 0.008
    ob_belt.data.update()

# 2) Rotate right-hip canister slightly (~28 deg outward in Z, ~16 deg forward down) so length & brass bands read in front view
ob_r = bpy.data.objects.get("AccessoriDestra")
if ob_r:
    can_c = Vector((-0.24, -0.03, 0.90))
    rot_fix = Matrix.Translation(can_c) @ Matrix.Rotation(math.radians(-28), 4, 'Z') @ Matrix.Translation(-can_c)
    for v in ob_r.data.vertices:
        # Canister lies around X=-0.28..-0.20, Z=0.82..0.96, Y=-0.13..+0.07
        if v.co.x < -0.195 and 0.81 <= v.co.z <= 0.965 and v.co.y < 0.08:
            v.co = rot_fix @ v.co
    ob_r.data.update()

def add_loft(bm, rings, cap_start=True, cap_end=True, mat_idx=0):
    n = len(rings[0])
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(len(vr) - 1):
        r0, r1 = vr[i], vr[i + 1]
        for j in range(n):
            jn = (j + 1) % n
            f = bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
            f.material_index = mat_idx
    if cap_start:
        f = bm.faces.new(vr[0][::-1])
        f.material_index = mat_idx
    if cap_end:
        f = bm.faces.new(vr[-1])
        f.material_index = mat_idx
    return vr

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

def add_tube(bm, pts, r, n=6, mat_idx=0, closed=False):
    rings = []
    m = len(pts)
    for i, p in enumerate(pts):
        if closed:
            t = (pts[(i + 1) % m] - pts[(i - 1) % m]).normalized()
        elif i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == m - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = u.cross(t).normalized()
        rings.append([p + u * (r * math.cos(2 * math.pi * k / n)) + v * (r * math.sin(2 * math.pi * k / n)) for k in range(n)])
    if closed:
        rings.append(rings[0])
    add_loft(bm, rings, cap_start=not closed, cap_end=not closed, mat_idx=mat_idx)

def leg_center(s, z):
    # Linear leg centerline from hip (0.095*s, 0.0, 0.90) -> knee (0.112*s, -0.004, 0.49) -> ankle (0.130*s, 0.0, 0.08)
    if z >= 0.49:
        t = max(0.0, min(1.0, (0.90 - z) / (0.90 - 0.49)))
        return Vector(((0.095 + 0.017 * t) * s, -0.004 * t, z))
    else:
        t = max(0.0, min(1.0, (0.49 - z) / (0.49 - 0.08)))
        return Vector(((0.112 + 0.018 * t) * s, -0.004 * (1.0 - t), z))

# 1. Rebuild Pantaloni (8.1): loose grey-brown trousers from waist (1.06) to boots (0.38)
#    Thigh 0.15 across at top (r=0.075), 0.11 above knee (r=0.055), 3 creases at back of knee!
bm_p = bmesh.new()

# Pelvis / waist block (0.86..1.06)
pelvis_z = [
    (0.855, 0.008, 0.165, 0.105),
    (0.900, 0.010, 0.162, 0.105),
    (0.980, 0.006, 0.148, 0.096),
    (1.060, 0.000, 0.128, 0.084),
]
pelvis_rings = []
for z, cy, rx, ry in pelvis_z:
    pelvis_rings.append([
        Vector((rx * math.sin(2*math.pi*i/20), cy - ry * math.cos(2*math.pi*i/20), z))
        for i in range(20)
    ])
add_loft(bm_p, pelvis_rings, cap_start=True, cap_end=True, mat_idx=0)

# Loose trouser legs with 3 back-of-knee creases
leg_z_specs = [
    # (z, rx, ry, back_crease_bump)
    (0.900, 0.076, 0.078, 0.000), # thigh top: 0.152 across!
    (0.800, 0.071, 0.073, 0.000),
    (0.680, 0.064, 0.066, 0.000),
    (0.560, 0.056, 0.058, 0.000), # above knee: 0.112 across!
    # 3 back-of-knee creases around Z=0.47..0.53
    (0.530, 0.054, 0.055, 0.006),
    (0.515, 0.053, 0.054, -0.005),
    (0.500, 0.054, 0.055, 0.007), # knee center
    (0.485, 0.053, 0.054, -0.005),
    (0.470, 0.054, 0.055, 0.006),
    (0.450, 0.053, 0.054, 0.000),
    (0.415, 0.051, 0.052, 0.000),
    (0.375, 0.048, 0.049, 0.000), # tucks cleanly inside shin wraps & boot cuff
]

for s in (1.0, -1.0):
    rings = []
    for z, rx, ry, crease in leg_z_specs:
        c = leg_center(s, z)
        ring = []
        for i in range(18):
            ang = 2.0 * math.pi * i / 18  # 0 = -Y front, pi = +Y back
            back_fac = max(0.0, -math.cos(ang)) ** 1.5
            x = c.x + rx * math.sin(ang)
            y = c.y - (ry + crease * back_fac) * math.cos(ang)
            ring.append(Vector((x, y, z)))
        rings.append(ring)
    add_loft(bm_p, rings, cap_start=True, cap_end=True, mat_idx=0)

# Ensure CorpoBase legs stay slim inside trousers & boots (no poke-through at knees/thighs)
ob_body = bpy.data.objects.get("CorpoBase")
if ob_body:
    for v in ob_body.data.vertices:
        if v.co.z < 0.85:
            s = 1.0 if v.co.x >= 0 else -1.0
            c = leg_center(s, v.co.z)
            dx, dy = v.co.x - c.x, v.co.y - c.y
            v.co.x = c.x + dx * 0.78
            v.co.y = c.y + dy * 0.78
    ob_body.data.update()

bmesh.ops.recalc_face_normals(bm_p, faces=bm_p.faces[:])
ob_p = bpy.data.objects.get("Pantaloni")
ob_p.data.materials.clear()
ob_p.data.materials.append(mat_pants)
bm_p.to_mesh(ob_p.data)
bm_p.free()
for p in ob_p.data.polygons:
    p.use_smooth = True
ob_p.data.update()

# 2. Rebuild StivaliGinocchiera:
#    - 8.2 Both knee pads (0.11 across, 0.025 thick, centre Z=0.50, straps above & below)
#    - 8.3 Shin wraps (3 overlapping cream cloth rings Z 0.40..0.46)
#    - 8.4 Tall boots (Z 0.08..0.42, 0.12 top / 0.09 ankle, 0.04 folded cuff,
#          eyelet rows & 8 crossed laces Z 0.10..0.40, ankle strap Z=0.09 & top strap Z=0.38 w/ brass buckles,
#          foot 0.27 long Y +0.08..-0.19 x 0.10 wide, 0.02 dark sole, 0.03 heel block at Z=0)

bm_s = bmesh.new()
# Materials:
# 0: mat_boot, 1: mat_boot_dark, 2: mat_sole, 3: mat_wrap, 4: mat_lace, 5: mat_brass

for s in (1.0, -1.0):
    c_knee = leg_center(s, 0.500)
    c_ank  = leg_center(s, 0.080)
    c_top  = leg_center(s, 0.420)

    # A. 8.2 Round leather knee pad (0.11 across -> radius 0.055, 0.025 thick, centre Z=0.50)
    kp_c = Vector((c_knee.x, c_knee.y - 0.054, 0.500))
    # Sculpted curved leather knee dome (flat back against knee, domed 0.025 front)
    res_kp = bmesh.ops.create_uvsphere(
        bm_s, u_segments=16, v_segments=10, radius=1.0,
        matrix=Matrix.Translation(kp_c) @ Matrix.Diagonal((0.055, 0.015, 0.055, 1.0))
    )
    tag_res(res_kp["verts"], 0)
    # Outer stitched border rim on knee pad
    res_kpr = bmesh.ops.create_cone(
        bm_s, cap_ends=False, cap_tris=False, segments=18,
        radius1=0.055, radius2=0.052, depth=0.012,
        matrix=Matrix.Translation(kp_c + Vector((0, 0.004, 0))) @ Matrix.Rotation(math.radians(90), 4, 'X')
    )
    tag_res(res_kpr["verts"], 1)

    # Upper & lower knee-pad straps around the leg (Z=0.535 & Z=0.465) + small brass buckle outside
    for zs in (0.465, 0.535):
        cz_leg = leg_center(s, zs)
        r_leg = 0.058 if zs > 0.50 else 0.056
        s_rings = []
        for dz in (-0.008, 0.008):
            s_rings.append([
                Vector((cz_leg.x + r_leg * math.cos(2*math.pi*k/16),
                        cz_leg.y + r_leg * math.sin(2*math.pi*k/16), zs + dz))
                for k in range(16)
            ])
        vr_st = add_loft(bm_s, s_rings, cap_start=False, cap_end=False, mat_idx=1)
        bmesh.ops.solidify(bm_s, geom=list({f for v in vr_st[0] for f in v.link_faces}), thickness=0.004)
        # Brass buckle on outside of knee strap
        res_kb = bmesh.ops.create_cube(
            bm_s, size=1.0,
            matrix=Matrix.Translation((cz_leg.x + (r_leg + 0.004) * s, cz_leg.y, zs)) @ Matrix.Diagonal((0.008, 0.018, 0.020, 1.0))
        )
        tag_res(res_kb["verts"], 5)

    # B. 8.3 Shin wraps: 3 overlapping cream cloth rings from Z=0.40 to Z=0.46
    wrap_bands = [
        (0.440, 0.462, 0.058, 0.056),
        (0.420, 0.444, 0.060, 0.057),
        (0.400, 0.424, 0.059, 0.058),
    ]
    for z0, z1, r0, r1 in wrap_bands:
        c0 = leg_center(s, z0)
        c1 = leg_center(s, z1)
        w_rings = []
        for z_cur, c_cur, r_cur, tilt in ((z0, c0, r0, 0.004 * s), (z1, c1, r1, -0.004 * s)):
            w_rings.append([
                Vector((c_cur.x + r_cur * math.cos(2*math.pi*k/16),
                        c_cur.y + r_cur * math.sin(2*math.pi*k/16),
                        z_cur + tilt * math.cos(2*math.pi*k/16)))
                for k in range(16)
            ])
        vr_w = add_loft(bm_s, w_rings, cap_start=False, cap_end=False, mat_idx=3)
        bmesh.ops.solidify(bm_s, geom=list({f for v in vr_w[0] for f in v.link_faces}), thickness=0.005)

    # C. 8.4 Tall brown leather boot shaft (Z=0.08..0.42, 0.12 across top r=0.060, 0.09 ankle r=0.045)
    shaft_specs = [
        (0.065, 0.046, 0.050), # ankle base inside foot collar
        (0.080, 0.045, 0.048), # ankle (0.09 across)
        (0.160, 0.048, 0.050),
        (0.260, 0.054, 0.055), # calf curve
        (0.350, 0.057, 0.058),
        (0.390, 0.059, 0.060),
        (0.420, 0.060, 0.061), # top of shaft (0.12 across)
    ]
    shaft_rings = []
    for z, rx, ry in shaft_specs:
        c = leg_center(s, z)
        shaft_rings.append([
            Vector((c.x + rx * math.cos(2*math.pi*k/18),
                    c.y + ry * math.sin(2*math.pi*k/18), z))
            for k in range(18)
        ])
    add_loft(bm_s, shaft_rings, cap_start=True, cap_end=True, mat_idx=0)

    # Folded-down cuff at top of shaft: 0.04 high (Z 0.38..0.42), slightly wider (r ~ 0.066), open front V-split for laces
    c_cuff_top = leg_center(s, 0.422)
    c_cuff_bot = leg_center(s, 0.380)
    cuff_grid = []
    for z, c_cur, r_out in ((0.380, c_cuff_bot, 0.065), (0.402, c_cuff_bot.lerp(c_cuff_top, 0.5), 0.067), (0.422, c_cuff_top, 0.065)):
        cuff_grid.append([
            Vector((c_cur.x + r_out * math.cos(2*math.pi*k/18),
                    c_cur.y + r_out * math.sin(2*math.pi*k/18), z))
            for k in range(18)
        ])
    vr_cf = add_loft(bm_s, cuff_grid, cap_start=False, cap_end=False, mat_idx=1)
    bmesh.ops.solidify(bm_s, geom=list({f for r in vr_cf for v in r for f in v.link_faces}), thickness=0.006)

    # D. Ankle strap (Z=0.09) & Top shaft strap (Z=0.38) with brass buckles on outside!
    for z_str, r_str in ((0.095, 0.051), (0.378, 0.066)):
        cs = leg_center(s, z_str)
        st_rings = [
            [Vector((cs.x + r_str * math.cos(2*math.pi*k/16), cs.y + r_str * math.sin(2*math.pi*k/16), z_str - 0.009)) for k in range(16)],
            [Vector((cs.x + r_str * math.cos(2*math.pi*k/16), cs.y + r_str * math.sin(2*math.pi*k/16), z_str + 0.009)) for k in range(16)],
        ]
        vr_bs = add_loft(bm_s, st_rings, cap_start=False, cap_end=False, mat_idx=1)
        bmesh.ops.solidify(bm_s, geom=list({f for v in vr_bs[0] for f in v.link_faces}), thickness=0.004)
        # Brass buckle outside (+X for L, -X for R)
        res_bb = bmesh.ops.create_cube(
            bm_s, size=1.0,
            matrix=Matrix.Translation((cs.x + (r_str + 0.004) * s, cs.y, z_str)) @ Matrix.Diagonal((0.008, 0.020, 0.024, 1.0))
        )
        tag_res(res_bb["verts"], 5)

    # E. Lacing at front of shaft: 2 rows of eyelets 0.03 apart (X=+-0.015) from Z=0.10 to Z=0.40,
    #    and 8 crossed laces (X shapes) between them, thickness 0.004 (r=0.002), light tan!
    eye_zs = [0.105 + i * (0.290 / 8.0) for i in range(9)]  # 9 rows -> 8 X-cross intervals from 0.105 to 0.395
    eye_pts_L = []
    eye_pts_R = []
    for ze in eye_zs:
        ce = leg_center(s, ze)
        # Shaft radius at ze
        t_sh = (ze - 0.08) / (0.42 - 0.08)
        r_sh = 0.047 + t_sh * 0.015
        if ze > 0.375:
            r_sh += 0.007 # over cuff
        # Compute front surface Y at X_off = +-0.015
        for side_e, store in ((-0.015, eye_pts_L), (0.015, eye_pts_R)):
            px = ce.x + side_e
            py = ce.y - math.sqrt(max(0.0001, r_sh * r_sh - side_e * side_e)) - 0.002
            p_eye = Vector((px, py, ze))
            store.append(p_eye)
            # Tiny brass eyelet ring/disc (6 sides)
            res_ey = bmesh.ops.create_cone(
                bm_s, cap_ends=True, cap_tris=False, segments=6,
                radius1=0.0038, radius2=0.0038, depth=0.003,
                matrix=Matrix.Translation(p_eye) @ Matrix.Rotation(math.radians(90), 4, 'X')
            )
            tag_res(res_ey["verts"], 5)

    # 8 crossed laces (X shapes): each interval i -> i+1 has 2 crossing diagonal cords
    for i in range(8):
        pL0, pR0 = eye_pts_L[i], eye_pts_R[i]
        pL1, pR1 = eye_pts_L[i + 1], eye_pts_R[i + 1]
        p_mid1 = pL0.lerp(pR1, 0.5) + Vector((0, -0.0022, 0))
        p_mid2 = pR0.lerp(pL1, 0.5) + Vector((0, -0.0005, 0))
        add_tube(bm_s, [pL0, p_mid1, pR1], r=0.0020, n=5, mat_idx=4)
        add_tube(bm_s, [pR0, p_mid2, pL1], r=0.0020, n=5, mat_idx=4)

    # F. Boot Foot (0.27 long from Y=+0.08 heel to Y=-0.19 toe, 0.10 wide, rounded toe, straight forward -Y)
    #    Anatomical loft along Y from +0.08 to -0.19
    cx_f = c_ank.x
    foot_slices = [
        # (y, z_bot, z_top, half_w)
        ( 0.080, 0.030, 0.052, 0.022), # heel back tip
        ( 0.068, 0.028, 0.085, 0.042), # heel counter
        ( 0.020, 0.024, 0.095, 0.047), # ankle instep
        (-0.040, 0.020, 0.074, 0.049), # mid-foot vamp
        (-0.100, 0.020, 0.056, 0.050), # ball of foot (0.10 wide!)
        (-0.145, 0.020, 0.048, 0.046), # toe box
        (-0.178, 0.021, 0.040, 0.034), # rounded toe taper
        (-0.190, 0.024, 0.033, 0.016), # toe tip (Y=-0.19!)
    ]
    foot_rings = []
    for y_f, zb, zt, hw in foot_slices:
        zc = 0.5 * (zb + zt)
        hz = 0.5 * (zt - zb)
        ring = []
        for k in range(14):
            ang = 2.0 * math.pi * k / 14
            ca, sa = math.cos(ang), math.sin(ang)
            # Flatter sole bottom, rounded upper vamp
            dx = math.copysign(abs(ca) ** 0.78, ca) * hw
            dz = (sa * hz) if sa >= 0 else (-abs(sa) ** 0.55) * hz
            ring.append(Vector((cx_f + dx, y_f, zc + dz)))
        foot_rings.append(ring)
    add_loft(bm_s, foot_rings, cap_start=True, cap_end=True, mat_idx=0)

    # G. Boot Sole (0.02 thick, dark (0.12, 0.08, 0.06)) + Heel block (0.03 high at back, bottom at Z=0.000!)
    sole_slices = [
        ( 0.080, 0.000, 0.030, 0.024), # heel block 0.03 high at Z=0..0.03
        ( 0.068, 0.000, 0.030, 0.043),
        ( 0.010, 0.000, 0.030, 0.046), # front edge of heel block
        (-0.010, 0.004, 0.024, 0.044), # subtle waist arch
        (-0.065, 0.000, 0.020, 0.049), # forefoot sole 0.02 thick (Z 0..0.02)
        (-0.120, 0.000, 0.020, 0.050),
        (-0.165, 0.001, 0.021, 0.043),
        (-0.188, 0.003, 0.022, 0.022), # rounded sole toe tip
    ]
    sole_rings = []
    for y_s, zb, zt, hw in sole_slices:
        zc = 0.5 * (zb + zt)
        hz = 0.5 * (zt - zb)
        ring = []
        for k in range(12):
            ang = 2.0 * math.pi * k / 12
            ca, sa = math.cos(ang), math.sin(ang)
            dx = math.copysign(abs(ca) ** 0.60, ca) * hw
            dz = math.copysign(abs(sa) ** 0.50, sa) * hz
            ring.append(Vector((cx_f + dx, y_s, zc + dz)))
        sole_rings.append(ring)
    add_loft(bm_s, sole_rings, cap_start=True, cap_end=True, mat_idx=2)

bmesh.ops.recalc_face_normals(bm_s, faces=bm_s.faces[:])
ob_s = bpy.data.objects.get("StivaliGinocchiera")
ob_s.data.materials.clear()
for m in (mat_boot, mat_boot_dark, mat_sole, mat_wrap, mat_lace, mat_brass):
    ob_s.data.materials.append(m)
bm_s.to_mesh(ob_s.data)
bm_s.free()
for p in ob_s.data.polygons:
    p.use_smooth = True
ob_s.data.update()

# Log Group 8 stats
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ("Pantaloni", "StivaliGinocchiera"):
    ob = bpy.data.objects.get(name)
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    log(f"{name}: tris={len(me.loop_triangles)}, Y=({min(p.y for p in pts):.3f}..{max(p.y for p in pts):.3f}), Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
    ev.to_mesh_clear()

bpy.ops.wm.save_mainfile()
render_viste("rev_8")
