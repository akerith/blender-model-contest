import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ==============================================================================
# GROUP 5 - Arms: sleeves, gloves, bracer, hands (rev_5)
# - 5.1 Upper arms (shoulder to elbow): wide, puffy, cream linen sleeves,
#   RGB (0.82, 0.76, 0.64), rolled up and bunched just above elbow. 0.10 across
#   at shoulder, 0.11 at roll above elbow, 3-4 bulging rings between Z 1.25 and elbow.
# - 5.2 Forearms: long brown leather gauntlets from hands up to 0.04 below elbow;
#   0.075 across at wrist, 0.095 at top cuff; flared cuff ring 0.015 thick.
# - 5.3 Three straps around each gauntlet (top cuff, mid forearm, wrist), each
#   0.015 wide, darker leather RGB (0.20, 0.12, 0.07), with tiny brass buckle 0.015 wide on outside.
# - 5.4 Left forearm (+X), on outside, just above wrist: round brass bracer-gauge,
#   disc 0.055 across and 0.015 thick, green glass face RGB (0.25, 0.55, 0.35), thin brass rim.
# - 5.5 Hands (gloved, brown leather RGB (0.26, 0.16, 0.09)):
#   - palm: flat block with rounded edges, 0.085 long, 0.08 wide, 0.03 thick
#   - 4 fingers, 3 segments each, lengths: index 0.075, middle 0.085, ring 0.08, little 0.065,
#     thickness ~0.018, spread ~8 deg between them, curled ~10 deg per joint towards palm, >=8 sides
#   - thumb: 2 segments + base, 0.065 long, starting at side of palm near wrist,
#     pointing forward and down at ~40 deg from index
#   - palm facing down and slightly back, touching wrist (no gap), middle fingertip at (+-0.66, 0.0, 0.86).
# ==============================================================================

scn = bpy.context.scene

def set_spec_mat(mat_name, spec_rgb, render_rgb, rough=0.65, metal=0.0, alpha=1.0):
    m = bpy.data.materials.get(mat_name)
    if not m:
        m = bpy.data.materials.new(mat_name)
        m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    for link in list(links):
        if link.to_socket == bsdf.inputs["Base Color"]:
            links.remove(link)
    bsdf.inputs["Base Color"].default_value = (*spec_rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.25
    if alpha < 1.0 and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    rgb_node = nodes.get("Spec_Tone") or nodes.new("ShaderNodeRGB")
    rgb_node.name = "Spec_Tone"
    rgb_node.outputs[0].default_value = (*render_rgb, 1.0)
    links.new(rgb_node.outputs[0], bsdf.inputs["Base Color"])
    return m

mat_manica = set_spec_mat("Mat_ManicaLino", (0.82, 0.76, 0.64), (0.68, 0.60, 0.46), rough=0.88)
mat_guanto = set_spec_mat("Mat_GuantoCuoio", (0.26, 0.16, 0.09), (0.15, 0.08, 0.04), rough=0.64)
mat_cinturino_g = set_spec_mat("Mat_CinturinoGuanto", (0.20, 0.12, 0.07), (0.10, 0.05, 0.025), rough=0.66)
mat_ottone = set_spec_mat("Mat_Ottone", (0.62, 0.45, 0.20), (0.58, 0.40, 0.16), rough=0.35, metal=1.0)
mat_quadrante = set_spec_mat("Mat_QuadranteVerde", (0.25, 0.55, 0.35), (0.20, 0.52, 0.32), rough=0.18, alpha=0.85)

# Helper: build a profiled tube along 3D points into a bmesh
def add_tube_to_bm(bm_t, pts, radii_xy, segs=16, cap_ends=True, mat_idx=0):
    uv_lay = bm_t.loops.layers.uv.active or bm_t.loops.layers.uv.new("UVMap")
    rings = []
    n = len(pts)
    for i in range(n):
        c = Vector(pts[i])
        r_item = radii_xy[i] if isinstance(radii_xy, list) else radii_xy
        rx, ry = r_item if isinstance(r_item, (tuple, list)) else (r_item, r_item)
        if i == 0:
            t = (Vector(pts[1]) - c).normalized()
        elif i == n - 1:
            t = (c - Vector(pts[-2])).normalized()
        else:
            t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        # Orthonormal frame: b1 in Y direction (-Y is front), b2 perpendicular in XZ plane
        b1 = Vector((0.0, 1.0, 0.0))
        b1 = (b1 - t * b1.dot(t)).normalized()
        b2 = t.cross(b1).normalized()
        ring = []
        for j in range(segs):
            th = 2.0 * math.pi * j / segs
            v = bm_t.verts.new(c + b1 * (rx * math.cos(th)) + b2 * (ry * math.sin(th)))
            ring.append(v)
        rings.append(ring)
    for i in range(n - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm_t.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
            f.smooth = True
            f.material_index = mat_idx
            for l in f.loops:
                l[uv_lay].uv = (j / float(segs), i / float(n - 1))
    if cap_ends:
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm_t.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True
                f.material_index = mat_idx

# 1. Reshape Manica_SX and Manica_DX (5.1):
#    - Shoulder (+-0.19, 0.0, 1.40) to elbow (+-0.38, 0.0, 1.18) plus inner extension to 0.04 below elbow (+-0.41, 0.0, 1.14)
#    - 0.10 across at shoulder (radius 0.050), 0.11 at roll above elbow (radius 0.055)
#    - 4 bulging rings (rolled fabric) between Z 1.25 and the elbow (Z 1.18)
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    manica_obj = bpy.data.objects.get(f"Manica_{side}")
    if not manica_obj:
        continue
    manica_obj.data.materials.clear()
    manica_obj.data.materials.append(mat_manica)
    bm = bmesh.new()

    p_sh = Vector((sx * 0.175, 0.000, 1.405))
    p_el = Vector((sx * 0.380, 0.000, 1.180))
    p_in = Vector((sx * 0.415, 0.000, 1.138))

    n_rings = 24
    pts = []
    rads = []
    for i in range(n_rings):
        t = i / float(n_rings - 1)
        if t <= 0.84:
            u = t / 0.84  # 0 at shoulder (Z=1.405), 1 at elbow (Z=1.180)
            p = p_sh.lerp(p_el, u)
            # Base radius: 0.050 (0.10 across) at shoulder, widening to 0.052 towards elbow
            r_base = 0.050 * (1.0 - u) + 0.051 * u
            # Between Z=1.255 (u~0.66) and Z=1.180 (u=1.0): 4 bulging rings reaching 0.11 across (radius 0.055)
            if u >= 0.62:
                u_roll = (u - 0.62) / (1.0 - 0.62)  # [0, 1] -> 4 peaks
                bulge = math.sin(u_roll * 4.0 * math.pi) ** 2
                r_base = 0.048 + 0.0075 * bulge  # peaks at 0.0555 (0.111 across!), valleys at 0.048
            # Taper slightly under shoulder cape near u < 0.25 so it never pokes through shoulder cape
            if u < 0.28:
                r_base *= (0.82 + 0.18 * (u / 0.28))
            pts.append(tuple(p))
            rads.append((r_base, r_base))
        else:
            # Short inner sleeve going into top of gauntlet (from elbow to 0.045 below elbow)
            u_in = (t - 0.84) / 0.16
            p = p_el.lerp(p_in, u_in)
            r_in = 0.041 * (1.0 - u_in) + 0.036 * u_in
            pts.append(tuple(p))
            rads.append((r_in, r_in))

    add_tube_to_bm(bm, pts, rads, segs=18, cap_ends=True)
    bm.normal_update()
    bm.to_mesh(manica_obj.data)
    bm.free()
    manica_obj.data.update()

# 2. Reshape Guanto_SX and Guanto_DX (5.2):
#    - From wrist (+-0.54, 0.0, 0.99) up to 0.04 below elbow:
#      elbow is (+-0.38, 0.0, 1.18), wrist is (+-0.54, 0.0, 0.99), distance = 0.2484 m.
#      0.04 m below elbow is at t = 0.04 / 0.2484 = 0.161 from elbow -> (+-0.406, 0.0, 1.149).
#    - 0.075 across at wrist (radius 0.0375) and 0.095 at top cuff (radius 0.0475);
#      the cuff is a flared ring 0.015 thick.
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    guanto_obj = bpy.data.objects.get(f"Guanto_{side}")
    if not guanto_obj:
        continue
    guanto_obj.data.materials.clear()
    guanto_obj.data.materials.append(mat_guanto)
    bm = bmesh.new()

    p_el = Vector((sx * 0.380, 0.000, 1.180))
    p_wr = Vector((sx * 0.540, 0.000, 0.990))
    p_cuff_top = p_el.lerp(p_wr, 0.161)   # exactly 0.04 m below elbow
    p_cuff_bot = p_el.lerp(p_wr, 0.240)   # bottom of flared cuff ring

    # Profile from cuff top (0.095 across -> r=0.0475, wall thickness 0.015) down to wrist (0.075 across -> r=0.0375)
    g_pts = [
        tuple(p_cuff_top + (p_wr - p_el).normalized() * 0.004),  # inner lip of 0.015-thick cuff
        tuple(p_cuff_top),                                       # top outer rim of flared cuff (0.095 across)
        tuple(p_cuff_top.lerp(p_cuff_bot, 0.5)),                 # middle of flared cuff ring
        tuple(p_cuff_bot),                                       # base of cuff ring
        tuple(p_el.lerp(p_wr, 0.45)),
        tuple(p_el.lerp(p_wr, 0.72)),
        tuple(p_wr),                                             # wrist (0.075 across)
    ]
    g_rads = [
        (0.0325, 0.0325),  # inner wall of cuff (0.0475 - 0.015 = 0.0325 -> cuff ring is 0.015 thick!)
        (0.0475, 0.0475),  # 0.095 across at top cuff
        (0.0475, 0.0475),
        (0.0435, 0.0435),
        (0.0415, 0.0415),
        (0.0390, 0.0390),
        (0.0375, 0.0375),  # 0.075 across at wrist
    ]
    add_tube_to_bm(bm, g_pts, g_rads, segs=18, cap_ends=True)
    bm.normal_update()
    bm.to_mesh(guanto_obj.data)
    bm.free()
    guanto_obj.data.update()

# 3. Reshape Cinturini_Guanto_SX and Cinturini_Guanto_DX (5.3):
#    - Three straps around each gauntlet: one at top cuff, one in middle of forearm, one at wrist
#    - Each 0.015 wide, darker leather RGB (0.20, 0.12, 0.07), with a tiny brass buckle 0.015 wide on the outside
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    cint_obj = bpy.data.objects.get(f"Cinturini_Guanto_{side}")
    if not cint_obj:
        continue
    cint_obj.data.materials.clear()
    cint_obj.data.materials.append(mat_cinturino_g)
    cint_obj.data.materials.append(mat_ottone)
    bm = bmesh.new()

    p_el = Vector((sx * 0.380, 0.000, 1.180))
    p_wr = Vector((sx * 0.540, 0.000, 0.990))
    axis = (p_wr - p_el).normalized()
    # Outside normal of forearm (pointing away from body and up: perpendicular to axis in XZ plane)
    out_dir = Vector((sx * 0.766, 0.0, 0.643)).normalized()
    front_dir = Vector((0.0, -1.0, 0.0))

    # Three positions along forearm: top cuff (t=0.22), middle of forearm (t=0.58), wrist (t=0.96)
    strap_specs = [
        (0.22, 0.0455),
        (0.58, 0.0405),
        (0.96, 0.0380),
    ]
    n_seg = 18
    hw = 0.0075  # 0.015 wide
    ht = 0.0025
    for t_pos, r_s in strap_specs:
        c_s = p_el.lerp(p_wr, t_pos)
        rings = []
        for k in range(n_seg):
            th = 2.0 * math.pi * k / n_seg
            rad_dir = front_dir * math.cos(th) + out_dir * math.sin(th)
            p_k = c_s + rad_dir * (r_s + ht)
            rings.append([
                bm.verts.new(p_k - axis * hw - rad_dir * ht),
                bm.verts.new(p_k + axis * hw - rad_dir * ht),
                bm.verts.new(p_k + axis * hw + rad_dir * ht),
                bm.verts.new(p_k - axis * hw + rad_dir * ht),
            ])
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            for j in range(4):
                jn = (j + 1) % 4
                f = bm.faces.new((rings[k][j], rings[k][jn], rings[kn][jn], rings[kn][j]))
                f.material_index = 0
                f.smooth = True

        # Tiny brass buckle 0.015 wide on the outside (out_dir)
        b_center = c_s + out_dir * (r_s + 0.0035)
        bhw, bhh, bht = 0.0075, 0.0085, 0.0025
        biw, bih = bhw * 0.62, bhh * 0.62
        outer = [bm.verts.new(b_center + axis * (sx_b * bhw) + out_dir * (sy_b * bht) + front_dir * (sz_b * bhh))
                 for sy_b in (-1, 1) for sx_b, sz_b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        inner = [bm.verts.new(b_center + axis * (sx_b * biw) + out_dir * (sy_b * bht) + front_dir * (sz_b * bih))
                 for sy_b in (-1, 1) for sx_b, sz_b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for i in range(4):
            inext = (i + 1) % 4
            for quad in (
                (outer[i], outer[inext], inner[inext], inner[i]),
                (outer[4 + inext], outer[4 + i], inner[4 + i], inner[4 + inext]),
                (outer[i], outer[4 + i], outer[4 + inext], outer[inext]),
                (inner[inext], inner[4 + inext], inner[4 + i], inner[i]),
            ):
                fb = bm.faces.new(quad)
                fb.material_index = 1

    bm.normal_update()
    bm.to_mesh(cint_obj.data)
    bm.free()
    cint_obj.data.update()

# 4. Reshape Strumento_Polso_SX (5.4):
#    - On her LEFT forearm (+X), on the outside, just above the wrist:
#      round brass bracer-gauge, a disc 0.055 across (radius 0.0275) and 0.015 thick,
#      with a green glass face RGB (0.25, 0.55, 0.35) and a thin brass rim.
#      Visible in front drawing (right of picture) and back drawing (left of picture).
bracer_obj = bpy.data.objects.get("Strumento_Polso_SX")
if bracer_obj:
    bracer_obj.data.materials.clear()
    bracer_obj.data.materials.append(mat_ottone)
    bracer_obj.data.materials.append(mat_quadrante)
    bm = bmesh.new()

    p_el = Vector((0.380, 0.000, 1.180))
    p_wr = Vector((0.540, 0.000, 0.990))
    axis = (p_wr - p_el).normalized()
    # Outside of left forearm (+X, +Z perpendicular to forearm, tilted slightly forward so green face & rim show in front, side, and back views!)
    out_n = Vector((0.72, -0.25, 0.64)).normalized()
    out_n = (out_n - axis * out_n.dot(axis)).normalized()
    tangent_v = axis.cross(out_n).normalized()

    # Centre just above the left wrist (t = 0.78 along forearm -> X ~ 0.505, Z ~ 1.032) + forearm radius 0.039
    c_disc = p_el.lerp(p_wr, 0.78) + out_n * (0.038 + 0.0075)
    r_disc = 0.0275  # 0.055 across
    r_inner = 0.0235 # thin brass rim (0.004 wide)
    h_half = 0.0075  # 0.015 thick

    n_seg = 24
    bot_out, top_out, top_in, glass_ring = [], [], [], []
    for k in range(n_seg):
        th = 2.0 * math.pi * k / n_seg
        dir_2d = axis * math.cos(th) + tangent_v * math.sin(th)
        bot_out.append(bm.verts.new(c_disc - out_n * h_half + dir_2d * r_disc))
        top_out.append(bm.verts.new(c_disc + out_n * h_half + dir_2d * r_disc))
        top_in.append(bm.verts.new(c_disc + out_n * h_half + dir_2d * r_inner))
        glass_ring.append(bm.verts.new(c_disc + out_n * (h_half - 0.0015) + dir_2d * r_inner))

    c_bot = bm.verts.new(c_disc - out_n * h_half)
    c_glass = bm.verts.new(c_disc + out_n * (h_half + 0.001))

    for k in range(n_seg):
        kn = (k + 1) % n_seg
        # Brass cylinder wall, bottom cap, top rim, inner rim bevel
        for quad in (
            (bot_out[k], bot_out[kn], top_out[kn], top_out[k]),
            (top_out[k], top_out[kn], top_in[kn], top_in[k]),
            (top_in[k], top_in[kn], glass_ring[kn], glass_ring[k]),
        ):
            f = bm.faces.new(quad)
            f.material_index = 0
            f.smooth = True
        fb = bm.faces.new((bot_out[kn], bot_out[k], c_bot))
        fb.material_index = 0
        # Green glass face
        fg = bm.faces.new((glass_ring[k], glass_ring[kn], c_glass))
        fg.material_index = 1
        fg.smooth = True

    bm.normal_update()
    bm.to_mesh(bracer_obj.data)
    bm.free()
    bracer_obj.data.update()

# 5. Reshape Mano_SX and Mano_DX (5.5):
#    - Gloved in same brown leather as gauntlets RGB (0.26, 0.16, 0.09)
#    - Continues line of forearm from wrist (+-0.54, 0.0, 0.99) to middle fingertip (+-0.66, 0.0, 0.86)
#    - Palm facing down and slightly back; touches wrist (no gap)
#    - Palm: flat block with rounded edges, 0.085 long, 0.08 wide, 0.03 thick
#    - Four fingers, each made of 3 segments (thick at base, thinner at tip), >= 8 sides (10 sides):
#      lengths: index 0.075, middle 0.085, ring 0.080, little 0.065, thickness ~0.018
#      slightly spread (~8 deg between them) and slightly curled (~10 deg per joint towards palm)
#    - Thumb: 2 segments plus a base, 0.065 long, starting at side of palm near wrist,
#      pointing forward and down at ~40 deg from index
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    mano_obj = bpy.data.objects.get(f"Mano_{side}")
    if not mano_obj:
        continue
    mano_obj.data.materials.clear()
    mano_obj.data.materials.append(mat_guanto)
    bm = bmesh.new()

    p_wr = Vector((sx * 0.540, 0.000, 0.990))
    p_tip_target = Vector((sx * 0.660, 0.000, 0.860))
    # Main hand axis continuing line of forearm: length 0.1769 m from wrist to middle fingertip
    hand_dir = (p_tip_target - p_wr).normalized()  # (sx*0.678, 0.0, -0.735)
    # Width axis across knuckles (0.08 wide): almost along -Y (index at -Y front, little at +Y back),
    # tilted slightly so palm normal faces down (-Z / inward -X) and slightly back (+Y)
    palm_norm = Vector((-sx * 0.68, 0.24, -0.69)).normalized()
    palm_norm = (palm_norm - hand_dir * palm_norm.dot(hand_dir)).normalized()
    width_dir = hand_dir.cross(palm_norm).normalized()
    # Ensure width_dir points towards front (-Y) for index finger
    if width_dir.y > 0:
        width_dir = -width_dir
        palm_norm = hand_dir.cross(width_dir).normalized()

    # A) Palm: flat block with rounded edges, 0.085 long, 0.08 wide (rx=0.040), 0.03 thick (ry=0.015)
    #    Starts slightly inside wrist (-0.006) to 0.085 along hand_dir so there is zero gap at wrist
    n_palm = 8
    palm_rings = []
    segs_p = 16
    for i in range(n_palm):
        t = i / float(n_palm - 1)
        d_along = -0.005 + t * 0.090  # total 0.085 exposed palm length
        c_p = p_wr + hand_dir * d_along
        # Rounded profile: matches wrist (0.036 x 0.034) at t=0, widens to 0.080 wide x 0.030 thick across palm, rounds at knuckles
        if t < 0.20:
            u = t / 0.20
            hw = 0.035 * (1.0 - u) + 0.038 * u
            ht = 0.032 * (1.0 - u) + 0.015 * u
        elif t > 0.88:
            u = (t - 0.88) / 0.12
            hw = 0.040 * (1.0 - 0.12 * u)
            ht = 0.015 * (1.0 - 0.20 * u)
        else:
            hw = 0.038 + 0.002 * math.sin(((t - 0.20) / 0.68) * math.pi)  # 0.080 wide
            ht = 0.015                                                     # 0.030 thick
        ring = []
        for j in range(segs_p):
            th = 2.0 * math.pi * j / segs_p
            # Superellipse (rounded rectangle cross-section) for flat block with rounded edges
            ct, st = math.cos(th), math.sin(th)
            x_loc = math.copysign(abs(ct) ** 0.65, ct) * hw
            y_loc = math.copysign(abs(st) ** 0.75, st) * ht
            ring.append(bm.verts.new(c_p + width_dir * x_loc + palm_norm * y_loc))
        palm_rings.append(ring)

    for i in range(n_palm - 1):
        for j in range(segs_p):
            jn = (j + 1) % segs_p
            f = bm.faces.new((palm_rings[i][j], palm_rings[i][jn], palm_rings[i + 1][jn], palm_rings[i + 1][j]))
            f.smooth = True
    for idx, inv in ((0, True), (-1, False)):
        c_pt = sum((v.co for v in palm_rings[idx]), Vector((0, 0, 0))) / segs_p
        cv = bm.verts.new(c_pt)
        for j in range(segs_p):
            jn = (j + 1) % segs_p
            f = bm.faces.new((palm_rings[idx][jn], palm_rings[idx][j], cv) if inv else (palm_rings[idx][j], palm_rings[idx][jn], cv))
            f.smooth = True

    # B) Four fingers, each made of 3 segments, >= 8 sides (10 sides around)
    #    Lengths: index 0.075, middle 0.085, ring 0.080, little 0.065; thickness ~0.018 (r_base = 0.0095)
    #    Spread: ~8 degrees between adjacent fingers (+12, +4, -4, -12 deg)
    #    Curled: each joint bent ~10 degrees towards palm_norm
    knuckle_line = p_wr + hand_dir * 0.082
    finger_specs = [
        ("Indice",   0.028, 0.075,  12.0, 0.0094),
        ("Medio",    0.009, 0.085,   4.0, 0.0098),
        ("Anulare", -0.010, 0.080,  -4.0, 0.0093),
        ("Mignolo", -0.028, 0.065, -12.0, 0.0084),
    ]
    for fname, w_off, flen, spread_deg, r_b in finger_specs:
        p0 = knuckle_line + width_dir * w_off
        sp_rad = math.radians(spread_deg)
        # Base direction spread in the plane of the palm
        base_d = (hand_dir * math.cos(sp_rad) + width_dir * math.sin(sp_rad)).normalized()
        # 3 segments with 10 degrees curl towards palm_norm at each joint (10, 20, 30 deg)
        seg_lens = [flen * 0.42, flen * 0.33, flen * 0.25]
        f_pts = [tuple(p0)]
        curr_p = p0.copy()
        for s_idx, s_len in enumerate(seg_lens):
            curl_rad = math.radians(10.0 * (s_idx + 1))
            seg_dir = (base_d * math.cos(curl_rad) + palm_norm * math.sin(curl_rad)).normalized()
            curr_p = curr_p + seg_dir * s_len
            f_pts.append(tuple(curr_p))
        f_rads = [r_b, r_b * 0.90, r_b * 0.78, r_b * 0.58]
        add_tube_to_bm(bm, f_pts, f_rads, segs=10, cap_ends=True)

    # C) Thumb: 2 segments plus a base, 0.065 long, starting at side of palm near wrist,
    #    pointing forward and down at ~40 degrees from the index finger
    thumb_start = p_wr + hand_dir * 0.022 + width_dir * 0.034 + palm_norm * 0.004
    ang_40 = math.radians(40.0)
    t_dir0 = (hand_dir * math.cos(ang_40) + width_dir * (math.sin(ang_40) * 0.82) + palm_norm * (math.sin(ang_40) * 0.55)).normalized()
    t_dir1 = (t_dir0 * math.cos(math.radians(10.0)) + palm_norm * math.sin(math.radians(10.0))).normalized()
    t_dir2 = (t_dir1 * math.cos(math.radians(12.0)) - width_dir * math.sin(math.radians(12.0))).normalized()
    tp0 = thumb_start
    tp1 = tp0 + t_dir0 * (0.065 * 0.36)  # base metacarpal segment
    tp2 = tp1 + t_dir1 * (0.065 * 0.35)  # proximal phalanx
    tp3 = tp2 + t_dir2 * (0.065 * 0.29)  # distal phalanx (total 0.065 long)
    add_tube_to_bm(bm, [tuple(tp0), tuple(tp1), tuple(tp2), tuple(tp3)], [0.0125, 0.0105, 0.0092, 0.0072], segs=10, cap_ends=True)

    bm.normal_update()
    bm.to_mesh(mano_obj.data)
    bm.free()
    mano_obj.data.update()

# Verify Group 5 measurements
m_sx = bpy.data.objects["Mano_SX"].data.vertices
tip_sx = max(m_sx, key=lambda v: v.co.x)
br_vs = bpy.data.objects["Strumento_Polso_SX"].data.vertices
log("=== VERIFICA MISURE GROUP 5 ===")
log(f"Mano_SX punta dito medio: X={tip_sx.co.x:.4f}, Y={tip_sx.co.y:.4f}, Z={tip_sx.co.z:.4f} (target X=0.66, Y=0.00, Z=0.86)")
log(f"Bracer-gauge SX: centro X={(min(v.co.x for v in br_vs)+max(v.co.x for v in br_vs))/2:.4f}, Z={(min(v.co.z for v in br_vs)+max(v.co.z for v in br_vs))/2:.4f}")

bpy.ops.wm.save_mainfile()
render_viste("rev_5")
