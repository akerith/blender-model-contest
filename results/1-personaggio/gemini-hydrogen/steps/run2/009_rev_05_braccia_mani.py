import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 5: Arms (puffy rolled linen sleeves, leather gauntlets with flared cuffs & 3 buckled straps,
# left wrist brass bracer-gauge with green glass, articulated 5-fingered gloved hands ~2000 tris each).
# Note: Rebuilds Guanti (previously blocky mitten hands) per rule A3.

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.65, metallic=0.0, spec=0.35, transmission=0.0, alpha=1.0):
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
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    return mat

mat_sleeve       = set_mat_srgb("CamiciaBeige", (0.82, 0.76, 0.64), roughness=0.90, spec=0.18)
mat_glove        = set_mat_srgb("PelleGuanti", (0.26, 0.16, 0.09), roughness=0.65, spec=0.32)
mat_strap_dark   = set_mat_srgb("PelleGuantiCinghie", (0.20, 0.12, 0.07), roughness=0.66, spec=0.30)
mat_brass        = set_mat_srgb("Ottone", (0.62, 0.45, 0.20), roughness=0.35, metallic=1.0, spec=0.50)
mat_dial_glass   = set_mat_srgb("QuadranteVerde", (0.25, 0.55, 0.35), roughness=0.10, metallic=0.05, spec=0.65, transmission=0.55, alpha=0.85)

# Small Group 4 polish: push chest buckles slightly outward (+Y negative) so both are crisp,
# and slim CorpoBase deltoid inside the puffy sleeves so zero skin pokes out of shoulder!
ob_body = bpy.data.objects.get("CorpoBase")
if ob_body:
    for v in ob_body.data.vertices:
        if 1.32 <= v.co.z <= 1.44 and abs(v.co.x) > 0.125:
            # Pull deltoid sphere slightly inward inside jacket/sleeve
            v.co.x *= 0.90
            v.co.y *= 0.85
            v.co.z -= 0.008
    ob_body.data.update()

ob_belt = bpy.data.objects.get("CinturaCinghie")
if ob_belt:
    for v in ob_belt.data.vertices:
        # Push upper chest buckles (1.28..1.32, front) slightly forward so Strap 1 buckle stands clear
        if 1.275 <= v.co.z <= 1.325 and v.co.y < -0.07 and 0.02 < abs(v.co.x) < 0.085:
            v.co.y -= 0.006
    ob_belt.data.update()

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

def make_limb_rings(p0, p1, r_list, n=16):
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

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

# 1. Update TunicaManiche sleeves (5.1): puffy cream linen sleeves (0.10 at shoulder, 0.11 at roll above elbow)
#    with 4 distinct bulging rolled fabric rings between Z 1.25 and elbow (Z 1.185)
ob_tm = bpy.data.objects.get("TunicaManiche")
bm_t = bmesh.new()
bm_t.from_mesh(ob_tm.data)

# Remove old sleeve vertices (|x| > 0.162 and z < 1.405) while keeping jacket, skirt, and collar
old_sleeve_v = [v for v in bm_t.verts if abs(v.co.x) > 0.162 and v.co.z < 1.405]
if old_sleeve_v:
    bmesh.ops.delete(bm_t, geom=old_sleeve_v, context='VERTS')

# Find mat_sleeve slot in TunicaManiche
mats_tm = list(ob_tm.data.materials)
if mat_sleeve.name in [m.name for m in mats_tm if m]:
    sleeve_mat_idx = [m.name for m in mats_tm].index(mat_sleeve.name)
else:
    mats_tm.append(mat_sleeve)
    sleeve_mat_idx = len(mats_tm) - 1

for s in (1.0, -1.0):
    p_sh = Vector((0.155 * s, 0.0, 1.395))   # tucks cleanly into jacket shoulder
    p_el = Vector((0.382 * s, 0.010, 1.185)) # elbow
    p_wr = Vector((0.540 * s, 0.0, 0.990))   # wrist (for axis projection)
    # Upper sleeve from shoulder (t=0) to elbow (t=1.0), plus cuff tuck to t=1.18 inside gauntlet
    # Width: 0.10 across at shoulder (r=0.050), 0.11 at roll above elbow (r=0.055)
    # 4 bulging rolled fabric rings between Z=1.25 (t~0.68) and elbow (t=1.02)
    r_specs = [
        (-0.04, 0.044, 0.042),
        ( 0.04, 0.051, 0.049), # 0.102 across at shoulder
        ( 0.25, 0.052, 0.050), # puffy upper arm
        ( 0.50, 0.051, 0.049),
        # Bulge ring 1 (Z~1.25)
        ( 0.65, 0.048, 0.046),
        ( 0.70, 0.056, 0.054),
        ( 0.74, 0.047, 0.045),
        # Bulge ring 2
        ( 0.78, 0.056, 0.055),
        ( 0.82, 0.047, 0.045),
        # Bulge ring 3
        ( 0.87, 0.057, 0.056), # 0.114 across at roll above elbow!
        ( 0.91, 0.048, 0.046),
        # Bulge ring 4 (right at elbow)
        ( 0.96, 0.055, 0.054),
        ( 1.02, 0.045, 0.044),
        ( 1.16, 0.036, 0.035), # tucks inside gauntlet cuff cleanly!
    ]
    rings = make_limb_rings(p_sh, p_el, r_specs, n=18)
    add_loft(bm_t, rings, cap_start=True, cap_end=True, mat_idx=sleeve_mat_idx)

bmesh.ops.recalc_face_normals(bm_t, faces=bm_t.faces[:])
ob_tm.data.materials.clear()
for m in mats_tm:
    ob_tm.data.materials.append(m)
bm_t.to_mesh(ob_tm.data)
bm_t.free()
for p in ob_tm.data.polygons:
    p.use_smooth = True
ob_tm.data.update()

# 2. Rebuild Guanti (5.2, 5.3, 5.5):
#    - Forearm gauntlets from 0.04 below elbow down to wrist (0.095 top cuff -> 0.075 wrist) with 0.015 flared cuff
#    - 3 dark leather straps per gauntlet (top cuff, mid forearm, wrist), 0.015 wide + tiny 0.015 brass buckle outside
#    - Gloved hands: rounded palm (0.085 x 0.08 x 0.03), 4 fingers (3 segments each, 12 sides, ~8 deg spread, ~10 deg curl),
#      thumb (2 segments + base, 0.065 long, ~40 deg from index), palm facing down & slightly back, touching wrist cleanly!

bm_g = bmesh.new()

def add_finger(bm_t, p_base, dir_fwd, palm_nrm, seg_lens, r_base, n_sides=12, curl_deg=10.0, mat_idx=0):
    # Builds a 3-segment (or 2-segment) finger with knuckle bulges and rounded tip
    cur_p = p_base.copy()
    cur_d = dir_fwd.normalized()
    side_axis = cur_d.cross(palm_nrm).normalized()
    rings = []
    # Base ring inside palm
    def make_f_ring(pos, d_ax, r):
        s_ax = d_ax.cross(palm_nrm).normalized()
        p_ax = s_ax.cross(d_ax).normalized()
        return [pos + s_ax * (r * math.cos(2 * math.pi * k / n_sides))
                    + p_ax * (r * 0.92 * math.sin(2 * math.pi * k / n_sides)) for k in range(n_sides)]

    rings.append(make_f_ring(cur_p - cur_d * 0.005, cur_d, r_base * 1.05))
    rings.append(make_f_ring(cur_p, cur_d, r_base))

    num_seg = len(seg_lens)
    for si, slen in enumerate(seg_lens):
        # Rotate cur_d towards palm_nrm by curl_deg around side_axis
        rot_q = Matrix.Rotation(math.radians(curl_deg * (si + 0.5)), 3, side_axis)
        seg_d = (rot_q @ cur_d).normalized()
        t_start = si / num_seg
        t_end = (si + 1) / num_seg
        r0 = r_base * (1.0 - 0.28 * t_start)
        r1 = r_base * (1.0 - 0.28 * t_end)
        # Mid-segment & joint rings
        rings.append(make_f_ring(cur_p + seg_d * (slen * 0.45), seg_d, (r0 + r1) * 0.49))
        cur_p = cur_p + seg_d * slen
        if si < num_seg - 1:
            # Slight knuckle bulge
            rings.append(make_f_ring(cur_p, seg_d, r1 * 1.05))
        else:
            # Fingertip taper
            rings.append(make_f_ring(cur_p - seg_d * 0.004, seg_d, r1 * 0.85))
            rings.append(make_f_ring(cur_p - seg_d * 0.001, seg_d, r1 * 0.45))
        cur_d = seg_d

    vr = add_loft(bm_t, rings, cap_start=True, cap_end=False, mat_idx=mat_idx)
    v_tip = bm_t.verts.new(cur_p + cur_d * 0.002)
    last_r = vr[-1]
    for k in range(n_sides):
        kn = (k + 1) % n_sides
        f = bm_t.faces.new((last_r[k], last_r[kn], v_tip))
        f.material_index = mat_idx

for s in (1.0, -1.0):
    p_el = Vector((0.382 * s, 0.010, 1.185))
    p_wr = Vector((0.540 * s, 0.000, 0.990))
    arm_axis = (p_wr - p_el).normalized()
    arm_len = (p_wr - p_el).length

    # Gauntlet starts 0.04 below elbow (t = 0.04 / 0.251 = 0.16) down to wrist (t = 1.02)
    t_top = 0.04 / arm_len
    g_specs = [
        (t_top,        0.0475, 0.0465), # 0.095 across at top cuff
        (t_top + 0.12, 0.0460, 0.0450),
        (0.55,         0.0425, 0.0415),
        (0.85,         0.0390, 0.0380),
        (1.02,         0.0375, 0.0365), # 0.075 across at wrist
    ]
    g_rings = make_limb_rings(p_el, p_wr, g_specs, n=18)
    add_loft(bm_g, g_rings, cap_start=True, cap_end=True, mat_idx=0)

    # Flared cuff ring at top of gauntlet (0.015 thick lip -> outer radius ~0.056)
    cuff_specs = [
        (t_top - 0.01, 0.054, 0.053),
        (t_top + 0.02, 0.053, 0.052),
        (t_top + 0.05, 0.051, 0.050),
        (t_top + 0.06, 0.045, 0.044),
    ]
    cuff_rings = make_limb_rings(p_el, p_wr, cuff_specs, n=18)
    # Extrude cuff edge inside to give real 0.015 lip feel
    cuff_rings.insert(0, make_limb_rings(p_el, p_wr, [(t_top - 0.01, 0.041, 0.040)], n=18)[0])
    add_loft(bm_g, cuff_rings, cap_start=True, cap_end=True, mat_idx=0)

    # Local forearm basis for straps & buckles
    ref_up = Vector((0, 0, 1))
    # Outer normal pointing outward (+X/+Z for left, -X/+Z for right)
    forearm_out = Vector((0.7 * s, 0.0, 0.7)).normalized()
    forearm_out = (forearm_out - arm_axis * forearm_out.dot(arm_axis)).normalized()

    # 3 straps around gauntlet (5.3): top cuff, mid forearm, wrist; 0.015 wide, darker leather + tiny brass buckle 0.015 wide
    strap_ts = [
        (t_top + 0.08, 0.0485),
        (0.58,         0.0440),
        (0.93,         0.0395),
    ]
    hw_t = (0.015 * 0.5) / arm_len
    for ts, rs in strap_ts:
        s_rings = make_limb_rings(p_el, p_wr, [
            (ts - hw_t, rs, rs * 0.98),
            (ts - hw_t, rs + 0.004, (rs + 0.004) * 0.98),
            (ts + hw_t, rs + 0.004, (rs + 0.004) * 0.98),
            (ts + hw_t, rs, rs * 0.98),
        ], n=18)
        add_loft(bm_g, s_rings, cap_start=False, cap_end=False, mat_idx=1)

        # Tiny brass buckle (0.015 wide) on outside of forearm
        b_center = p_el.lerp(p_wr, ts) + forearm_out * (rs + 0.005)
        b_side = arm_axis.cross(forearm_out).normalized()
        basis_b = Matrix((b_side, forearm_out, arm_axis)).transposed().to_4x4()
        res_bk = bmesh.ops.create_cube(
            bm_g, size=1.0,
            matrix=Matrix.Translation(b_center) @ basis_b @ Matrix.Diagonal((0.015, 0.006, 0.018, 1.0))
        )
        tag_res(res_bk["verts"], 2)

    # Hand frame (5.5): continues forearm, palm facing down and slightly back
    # Wrist = (0.540*s, 0, 0.990) -> Middle fingertip target = (0.660*s, 0, 0.860)
    p_tip_target = Vector((0.660 * s, 0.0, 0.860))
    hand_fwd = (p_tip_target - p_wr).normalized()
    # Palm faces down (-Z) and slightly back (+Y)
    palm_pref = Vector((0.0, 0.28, -0.96)).normalized()
    palm_nrm = (palm_pref - hand_fwd * palm_pref.dot(hand_fwd)).normalized()
    # Side vector pointing toward THUMB (-Y front)
    side_vec = hand_fwd.cross(palm_nrm).normalized()
    if side_vec.y > 0:
        side_vec = -side_vec

    # Palm: rounded flat block 0.085 long, 0.080 wide (hw=0.040), 0.030 thick (ht=0.015)
    # Touches wrist cleanly (starts slightly inside wrist at -0.008)
    palm_len = 0.085
    palm_rings_spec = [
        (-0.008, 0.035, 0.017), # inside wrist cuff
        ( 0.005, 0.036, 0.016), # wrist heel
        ( 0.028, 0.038, 0.016), # mid lower palm
        ( 0.055, 0.040, 0.0155),# upper palm (0.080 wide, 0.031 thick)
        ( 0.075, 0.040, 0.015), # knuckle base
        ( 0.085, 0.037, 0.013), # knuckle line
        ( 0.090, 0.030, 0.008), # web close
    ]
    n_palm = 16
    palm_rings = []
    for d_u, hw, ht in palm_rings_spec:
        c = p_wr + hand_fwd * d_u
        ring = []
        for k in range(n_palm):
            ang = 2.0 * math.pi * k / n_palm
            ca, sa = math.cos(ang), math.sin(ang)
            # Super-ellipse (rounded rectangular cross-section)
            sx = math.copysign(abs(ca) ** 0.72, ca) * hw
            sy = math.copysign(abs(sa) ** 0.75, sa) * ht
            ring.append(c + side_vec * sx + palm_nrm * sy)
        palm_rings.append(ring)
    add_loft(bm_g, palm_rings, cap_start=True, cap_end=True, mat_idx=0)

    # 4 Fingers (3 segments each, 12 sides, ~8 deg spread, ~10 deg curl towards palm):
    # Index 0.075, Middle 0.085, Ring 0.080, Little 0.065; thickness ~0.018 (r=0.009)
    finger_specs = [
        ("Index",  0.027, 0.082,  10.0, [0.031, 0.024, 0.020], 0.0092),
        ("Middle", 0.009, 0.084,   2.0, [0.035, 0.027, 0.023], 0.0095),
        ("Ring",  -0.010, 0.082,  -6.0, [0.033, 0.025, 0.022], 0.0090),
        ("Little",-0.028, 0.077, -14.0, [0.027, 0.020, 0.018], 0.0082),
    ]
    for fname, side_off, fwd_off, spread_deg, seg_lens, r_f in finger_specs:
        f_base = p_wr + hand_fwd * fwd_off + side_vec * side_off + palm_nrm * 0.001
        f_dir = (Matrix.Rotation(math.radians(spread_deg), 3, palm_nrm) @ hand_fwd).normalized()
        add_finger(bm_g, f_base, f_dir, palm_nrm, seg_lens, r_f, n_sides=12, curl_deg=10.0, mat_idx=0)

    # Thumb: 2 segments + base, 0.065 long, starts at side of palm near wrist, points forward & down ~40 deg from index
    th_base_p = p_wr + hand_fwd * 0.024 + side_vec * 0.032 + palm_nrm * 0.005
    th_dir = (hand_fwd * 0.72 + side_vec * 0.62 + palm_nrm * 0.30).normalized()
    add_finger(bm_g, th_base_p, th_dir, palm_nrm, [0.024, 0.022, 0.019], 0.0095, n_sides=12, curl_deg=12.0, mat_idx=0)

bmesh.ops.recalc_face_normals(bm_g, faces=bm_g.faces[:])
ob_g = bpy.data.objects.get("Guanti")
ob_g.data.materials.clear()
for m in (mat_glove, mat_strap_dark, mat_brass):
    ob_g.data.materials.append(m)
bm_g.to_mesh(ob_g.data)
bm_g.free()
for p in ob_g.data.polygons:
    p.use_smooth = True
ob_g.data.update()

# 3. Rebuild BussolaPolso_L (5.4): on LEFT forearm (+X), outside, just above wrist,
#    round brass disc 0.055 across, 0.015 thick, green glass face (0.25, 0.55, 0.35), thin brass rim
bm_b = bmesh.new()
p_el_L = Vector((0.382, 0.010, 1.185))
p_wr_L = Vector((0.540, 0.000, 0.990))
ax_L = (p_wr_L - p_el_L).normalized()
out_L = Vector((0.70, 0.0, 0.71)).normalized()
out_L = (out_L - ax_L * out_L.dot(ax_L)).normalized()
side_L = ax_L.cross(out_L).normalized()

# Position just above wrist strap (t=0.82) sitting cleanly on forearm surface (r ~ 0.040)
bracer_c = p_el_L.lerp(p_wr_L, 0.82) + out_L * 0.041
# Rotation matrix aligning local Z to out_L
rot_br = Matrix((side_L, ax_L, out_L)).transposed().to_4x4()
br_mat = Matrix.Translation(bracer_c) @ rot_br

# Dark leather pad/strap mount under gauge
res_pad = bmesh.ops.create_cone(
    bm_b, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.029, radius2=0.029, depth=0.006,
    matrix=br_mat @ Matrix.Translation((0, 0, -0.004))
)
tag_res(res_pad["verts"], 2)

# Brass casing (0.055 across -> radius 0.0275, 0.015 thick)
res_case = bmesh.ops.create_cone(
    bm_b, cap_ends=True, cap_tris=False, segments=24,
    radius1=0.0275, radius2=0.0265, depth=0.013,
    matrix=br_mat @ Matrix.Translation((0, 0, 0.003))
)
tag_res(res_case["verts"], 0)

# Thin raised brass bezel rim around glass face
n_rim = 24
rim_verts = []
for i in range(n_rim):
    a = 2.0 * math.pi * i / n_rim
    ca, sa = math.cos(a), math.sin(a)
    ring_pts = [
        Vector((0.023 * ca, 0.023 * sa, 0.009)),
        Vector((0.0275 * ca, 0.0275 * sa, 0.009)),
        Vector((0.0275 * ca, 0.0275 * sa, 0.0135)),
        Vector((0.0235 * ca, 0.0235 * sa, 0.0135)),
    ]
    rim_verts.append([bm_b.verts.new(br_mat @ p) for p in ring_pts])
for i in range(n_rim):
    inext = (i + 1) % n_rim
    for k in range(4):
        kn = (k + 1) % 4
        f = bm_b.faces.new((rim_verts[i][k], rim_verts[inext][k], rim_verts[inext][kn], rim_verts[i][kn]))
        f.material_index = 0

# Green glass dial face (mat_idx=1)
res_gl = bmesh.ops.create_cone(
    bm_b, cap_ends=True, cap_tris=False, segments=24,
    radius1=0.0235, radius2=0.0235, depth=0.003,
    matrix=br_mat @ Matrix.Translation((0, 0, 0.0105))
)
tag_res(res_gl["verts"], 1)

# Tiny brass pointer needle & center pin on top of dial
res_nd = bmesh.ops.create_cube(
    bm_b, size=1.0,
    matrix=br_mat @ Matrix.Translation((0.005, 0.004, 0.012)) @ Matrix.Rotation(math.radians(35), 4, 'Z') @ Matrix.Diagonal((0.018, 0.0025, 0.0015, 1.0))
)
tag_res(res_nd["verts"], 0)

bmesh.ops.recalc_face_normals(bm_b, faces=bm_b.faces[:])
ob_b = bpy.data.objects.get("BussolaPolso_L")
ob_b.data.materials.clear()
for m in (mat_brass, mat_dial_glass, mat_strap_dark):
    ob_b.data.materials.append(m)
bm_b.to_mesh(ob_b.data)
bm_b.free()
for p in ob_b.data.polygons:
    p.use_smooth = True
ob_b.data.update()

# Log Group 5 stats
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ("TunicaManiche", "Guanti", "BussolaPolso_L"):
    ob = bpy.data.objects.get(name)
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    log(f"{name}: tris={len(me.loop_triangles)}, X=({min(p.x for p in pts):.3f}..{max(p.x for p in pts):.3f}), Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
    ev.to_mesh_clear()

bpy.ops.wm.save_mainfile()
render_viste("rev_5")
