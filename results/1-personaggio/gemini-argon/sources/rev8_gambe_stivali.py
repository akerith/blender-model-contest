import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 8 - Legs and boots (rev_8) + 45-degree oval orientation on right-hip rope
# - 8.1 Trousers: grey-brown RGB (0.22, 0.19, 0.16), slightly loose, from waist
#   to boots. Thigh 0.15 across at top, 0.11 above knee. 3 creases at back of knee.
# - 8.2 Knee pads: round leather pads on BOTH knees, 0.11 across and 0.025 thick,
#   centre at Z 0.50, on front of knee, held by a strap around leg above and below.
# - 8.3 Shin wraps: band of cream cloth wrapped around leg from Z 0.40 to Z 0.46,
#   made of 3 overlapping rings.
# - 8.4 Boots: tall brown leather boots RGB (0.30, 0.18, 0.10):
#   - shaft from ankle (Z 0.08) up to Z 0.42, 0.12 across at top, 0.09 at ankle
#   - folded-down cuff at top of shaft, 0.04 high (Z 0.38 to 0.42), slightly wider
#   - lacing at front of shaft: two rows of eyelets 0.03 apart, from Z 0.10 to Z 0.40,
#     and 8 crossed laces (X shapes) between them, light tan RGB (0.55, 0.42, 0.28),
#     thickness 0.004
#   - one strap with a brass buckle around ankle (Z 0.09) and one around top of shaft (Z 0.38)
#   - foot: 0.27 long from heel to toe, 0.10 wide, toe slightly rounded, pointing
#     straight forward (-Y); toe at Y -0.19, heel at Y +0.08, centre at X = +-0.13
#   - sole 0.02 thick, darker RGB (0.12, 0.08, 0.06); heel block 0.03 high at back of sole.
# ==============================================================================

scn = bpy.context.scene

def set_spec_mat(mat_name, spec_rgb, render_rgb, rough=0.65, metal=0.0):
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
    rgb_node = nodes.get("Spec_Tone") or nodes.new("ShaderNodeRGB")
    rgb_node.name = "Spec_Tone"
    rgb_node.outputs[0].default_value = (*render_rgb, 1.0)
    links.new(rgb_node.outputs[0], bsdf.inputs["Base Color"])
    return m

mat_pantaloni = set_spec_mat("Mat_Pantaloni", (0.22, 0.19, 0.16), (0.13, 0.11, 0.09), rough=0.88)
mat_stivale = set_spec_mat("Mat_StivaleCuoio", (0.30, 0.18, 0.10), (0.18, 0.10, 0.05), rough=0.64)
mat_suola = set_spec_mat("Mat_SuolaScuro", (0.12, 0.08, 0.06), (0.05, 0.03, 0.02), rough=0.70)
mat_lacci = set_spec_mat("Mat_LacciTan", (0.55, 0.42, 0.28), (0.42, 0.30, 0.18), rough=0.82)
mat_cuoio_scuro = set_spec_mat("Mat_CuoioScuro", (0.22, 0.13, 0.07), (0.12, 0.06, 0.03), rough=0.65)
mat_cuoio_medio = set_spec_mat("Mat_CuoioMedio", (0.36, 0.22, 0.12), (0.24, 0.13, 0.06), rough=0.65)
mat_fasce = set_spec_mat("Mat_ManicaLino", (0.82, 0.76, 0.64), (0.68, 0.60, 0.46), rough=0.88)
mat_ottone = set_spec_mat("Mat_Ottone", (0.62, 0.45, 0.20), (0.58, 0.40, 0.16), rough=0.35, metal=1.0)

# Quick Group 7 rope polish: rotate the 4 oval loops on her right hip (-X) so their 0.10 width shows clearly in front AND side views
corda_obj = bpy.data.objects.get("Corda_Fianco_DX")
if corda_obj:
    bm = bmesh.new()
    loop_configs = [
        (0.980, 0.780, -0.165, -0.055, 0.050,  0.000),
        (0.970, 0.755, -0.174, -0.050, 0.050,  0.400),
        (0.960, 0.735, -0.183, -0.045, 0.050,  0.800),
        (0.950, 0.720, -0.192, -0.040, 0.050,  1.200),
    ]
    n_path, n_sect, r_base = 44, 12, 0.0075
    # Oval width vector angled at 42 deg between X and Y so oval loop openings show in front view and side view
    w_vec = Vector((-0.62, -0.78, 0.0)).normalized()
    n_vec = Vector((-0.78,  0.62, 0.0)).normalized()
    for zt, zb, cx, cy, rw, phase in loop_configs:
        z_mid = 0.5 * (zt + zb)
        rz_h = 0.5 * (zt - zb)
        pts = []
        for k in range(n_path):
            th = 2.0 * math.pi * k / n_path
            ct, st = math.cos(th), math.sin(th)
            p = Vector((cx, cy, z_mid)) + w_vec * (rw * st) + n_vec * (0.008 * math.sin(2 * th + phase)) + Vector((0, 0, rz_h * ct))
            pts.append(p)
        rings = []
        for k in range(n_path):
            c = pts[k]
            t_v = (pts[(k + 1) % n_path] - pts[(k - 1) % n_path]).normalized()
            b1 = t_v.cross(n_vec).normalized()
            b2 = b1.cross(t_v).normalized()
            u_len = k / float(n_path)
            ring = []
            for j in range(n_sect):
                ang = 2.0 * math.pi * j / n_sect
                r_c = r_base * (1.0 + 0.22 * math.cos(3.0 * ang - 2.0 * math.pi * u_len * 14.0))
                ring.append(bm.verts.new(c + b1 * (r_c * math.cos(ang)) + b2 * (r_c * math.sin(ang))))
            rings.append(ring)
        for k in range(n_path):
            kn = (k + 1) % n_path
            for j in range(n_sect):
                jn = (j + 1) % n_sect
                f = bm.faces.new((rings[k][j], rings[k][jn], rings[kn][jn], rings[kn][j]))
                f.smooth = True
    bm.normal_update()
    bm.to_mesh(corda_obj.data)
    bm.free()
    corda_obj.data.update()

# Leg centerline X(z) from hip joint (X=+-0.100 at Z=0.90) through knee (X=+-0.115 at Z=0.49) to ankle (X=+-0.130 at Z=0.08)
def leg_center_x(z, sx):
    if z <= 0.08:
        return sx * 0.130
    elif z <= 0.49:
        t = (z - 0.08) / (0.49 - 0.08)
        return sx * (0.130 * (1.0 - t) + 0.115 * t)
    else:
        t = min(1.0, (z - 0.49) / (0.90 - 0.49))
        return sx * (0.115 * (1.0 - t) + 0.100 * t)

# 1. Reshape Pantalone_SX and Pantalone_DX (8.1):
#    Grey-brown RGB (0.22, 0.19, 0.16), slightly loose, from waist/hips down to boots (Z=0.41).
#    Thigh 0.15 across at top (radius 0.075), 0.11 above knee (radius 0.055).
#    Add 3 creases at the back of the knee (Z = 0.47, 0.50, 0.53 on +Y side).
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    pant_obj = bpy.data.objects.get(f"Pantalone_{side}")
    if not pant_obj:
        continue
    pant_obj.data.materials.clear()
    pant_obj.data.materials.append(mat_pantaloni)
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    n_rings = 24
    segs = 22
    rings = []
    for i in range(n_rings):
        t = i / float(n_rings - 1)  # 0 at bottom (Z=0.41), 1 at top (Z=0.90)
        z = 0.410 + t * (0.900 - 0.410)
        cx = leg_center_x(z, sx)
        # Radius: 0.055 (0.11 across) above knee (Z<=0.53), widening to 0.075 (0.15 across) at top of thigh (Z=0.90)
        if z <= 0.53:
            r_base = 0.054 + 0.001 * ((z - 0.41) / 0.12)
        else:
            u_th = (z - 0.53) / (0.90 - 0.53)
            r_base = 0.055 + 0.020 * (u_th ** 0.9)

        ring = []
        for j in range(segs):
            th = 2.0 * math.pi * j / segs  # +pi/2 is back (+Y), -pi/2 is front (-Y)
            ct, st = math.cos(th), math.sin(th)
            # Slight loose fabric folds along the trouser leg
            fold = 0.002 * math.sin(th * 5.0 + t * 4.0)
            # 3 sharp horizontal creases at the back of the knee (Z in 0.45..0.54, st > 0.25)
            crease = 0.0
            if 0.445 <= z <= 0.545 and st > 0.20:
                back_w = ((st - 0.20) / 0.80) ** 1.2
                u_k = (z - 0.445) / 0.100  # 0..1 -> 3 crease waves
                crease = -0.0065 * (math.sin(u_k * 3.0 * math.pi) ** 2) * back_w
            rx = r_base + fold + crease * 0.4
            ry = r_base * 1.03 + fold + crease
            ring.append(bm.verts.new(Vector((cx + rx * ct, ry * st, z))))
        rings.append(ring)

    for i in range(n_rings - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
            f.smooth = True
            for l in f.loops:
                l[uv_lay].uv = (j / float(segs), i / float(n_rings - 1))
    for idx, inv in ((0, True), (-1, False)):
        c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
        cv = bm.verts.new(c_pt)
        for j in range(segs):
            jn = (j + 1) % segs
            bm.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))

    bm.normal_update()
    bm.to_mesh(pant_obj.data)
    bm.free()
    pant_obj.data.update()

# 2. Reshape Ginocchiera_DX into Ginocchiere (8.2: round leather pads on BOTH knees,
#    0.11 across and 0.025 thick, centre at Z 0.50, on the front of the knee,
#    held by a strap around the leg above and below)
kp_obj = bpy.data.objects.get("Ginocchiera_DX") or bpy.data.objects.get("Ginocchiere")
if kp_obj:
    kp_obj.name = "Ginocchiere"
    kp_obj.data.name = "Ginocchiere"
    kp_obj.data.materials.clear()
    kp_obj.data.materials.append(mat_cuoio_medio)
    kp_obj.data.materials.append(mat_cuoio_scuro)
    bm = bmesh.new()

    for sx in (-1.0, 1.0):
        cx = leg_center_x(0.50, sx)
        # Round leather pad: 0.11 across (radius X/Z = 0.055), 0.025 thick, centre at (cx, -0.056, 0.50)
        ret = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
        for v in ret["verts"]:
            # Cup slightly around the front of the knee
            px = v.co.x * 0.055
            pz = v.co.z * 0.055
            cup_y = 0.014 * ((v.co.x ** 2) + 0.5 * (v.co.z ** 2))
            py = v.co.y * 0.0125 + cup_y
            v.co = Vector((cx + px, -0.058 + py, 0.500 + pz))
        for v in ret["verts"]:
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0

        # Straps around the leg ABOVE (Z = 0.545) and BELOW (Z = 0.455) holding each knee pad
        for z_st, r_st in ((0.545, 0.057), (0.455, 0.055)):
            cx_s = leg_center_x(z_st, sx)
            n_s = 20
            hw, ht = 0.008, 0.003
            s_rings = []
            for k in range(n_s):
                th = 2.0 * math.pi * k / n_s
                n_dir = Vector((math.cos(th), math.sin(th), 0.0))
                p_k = Vector((cx_s, 0.0, z_st)) + n_dir * r_st
                s_rings.append([
                    bm.verts.new(p_k + Vector((0, 0, -hw)) - n_dir * ht),
                    bm.verts.new(p_k + Vector((0, 0,  hw)) - n_dir * ht),
                    bm.verts.new(p_k + Vector((0, 0,  hw)) + n_dir * ht),
                    bm.verts.new(p_k + Vector((0, 0, -hw)) + n_dir * ht),
                ])
            for k in range(n_s):
                kn = (k + 1) % n_s
                for j in range(4):
                    jn = (j + 1) % 4
                    fs = bm.faces.new((s_rings[k][j], s_rings[k][jn], s_rings[kn][jn], s_rings[kn][j]))
                    fs.material_index = 1
                    fs.smooth = True

    bm.normal_update()
    bm.to_mesh(kp_obj.data)
    bm.free()
    kp_obj.data.update()

# 3. Reshape Fascia_Gamba_SX and Fascia_Gamba_DX (8.3 Shin wraps):
#    Just under the knee pad, a band of cream cloth wrapped around the leg,
#    from Z 0.40 to Z 0.46, made of 3 overlapping rings.
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    wrap_obj = bpy.data.objects.get(f"Fascia_Gamba_{side}")
    if not wrap_obj:
        continue
    wrap_obj.data.materials.clear()
    wrap_obj.data.materials.append(mat_fasce)
    bm = bmesh.new()

    # 3 overlapping cloth rings spanning Z = 0.40 to Z = 0.46
    ring_specs = [
        (0.400, 0.424,  0.002),
        (0.418, 0.442, -0.002),
        (0.436, 0.460,  0.002),
    ]
    segs = 20
    for z0, z1, tilt in ring_specs:
        n_r = 5
        rings = []
        for i in range(n_r):
            t = i / float(n_r - 1)
            z_base = z0 + t * (z1 - z0)
            cx = leg_center_x(z_base, sx)
            # Bulging ring profile (overlapping band look)
            r_w = 0.056 + 0.0035 * math.sin(t * math.pi)
            ring = []
            for j in range(segs):
                th = 2.0 * math.pi * j / segs
                z_th = z_base + tilt * math.sin(th)
                ring.append(bm.verts.new(Vector((cx + r_w * math.cos(th), r_w * 1.02 * math.sin(th), z_th))))
            rings.append(ring)
        for i in range(n_r - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True

    bm.normal_update()
    bm.to_mesh(wrap_obj.data)
    bm.free()
    wrap_obj.data.update()

# 4. Reshape Stivale_SX/DX and Lacci_Stivale_SX/DX (8.4 Boots):
#    - Tall brown leather boots RGB (0.30, 0.18, 0.10)
#    - Shaft from ankle (Z 0.08) up to Z 0.42, 0.12 across at top (r=0.060), 0.09 at ankle (r=0.045)
#    - Top of shaft has folded-down cuff 0.04 high (Z 0.38 to 0.42), slightly wider (0.128 across -> r=0.064)
#    - One strap with a brass buckle around ankle (Z 0.09) and one around top of shaft (Z 0.38)
#    - Foot: 0.27 long from heel to toe, 0.10 wide (rx=0.050), toe slightly rounded, pointing straight forward (-Y).
#      Toe at Y -0.19, heel at Y +0.08, centre at X = +-0.13.
#    - Sole 0.02 thick (Z 0.00 to 0.02), darker RGB (0.12, 0.08, 0.06); heel block 0.03 high (Z 0.00 to 0.03) at back of sole.
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    boot_obj = bpy.data.objects.get(f"Stivale_{side}")
    if not boot_obj:
        continue
    boot_obj.data.materials.clear()
    boot_obj.data.materials.append(mat_stivale)      # 0: boot leather
    boot_obj.data.materials.append(mat_suola)        # 1: dark sole & heel block
    boot_obj.data.materials.append(mat_cuoio_scuro)  # 2: straps
    boot_obj.data.materials.append(mat_ottone)       # 3: brass buckles & eyelets
    bm = bmesh.new()

    cx_boot = sx * 0.130  # centre of each boot at X = -0.13 (right) and X = +0.13 (left)

    # A) Boot shaft from Z=0.08 to Z=0.42 (0.09 across at ankle -> r=0.045; 0.12 across at top -> r=0.060)
    shaft_z = [0.065, 0.080, 0.140, 0.220, 0.300, 0.375, 0.420]
    shaft_r = [0.046, 0.045, 0.048, 0.053, 0.058, 0.059, 0.060]
    segs = 22
    s_rings = []
    for z, r in zip(shaft_z, shaft_r):
        cx = leg_center_x(z, sx)
        ring = []
        for j in range(segs):
            th = 2.0 * math.pi * j / segs
            # Subtle tongue recess at front center (-Y, th ~ -pi/2) between Z=0.10 and Z=0.38
            recess = 0.0
            if 0.09 <= z <= 0.39 and math.sin(th) < -0.85:
                recess = -0.003
            ring.append(bm.verts.new(Vector((cx + (r + recess) * math.cos(th), (r * 1.04 + recess) * math.sin(th), z))))
        s_rings.append(ring)
    for i in range(len(s_rings) - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm.faces.new((s_rings[i][j], s_rings[i][jn], s_rings[i + 1][jn], s_rings[i + 1][j]))
            f.smooth = True
            f.material_index = 0

    # B) Folded-down cuff at top of shaft: 0.04 high (Z 0.38 to 0.42), slightly wider (r=0.064)
    cuff_z = [0.380, 0.384, 0.416, 0.420]
    cuff_r = [0.061, 0.064, 0.064, 0.060]
    c_rings = []
    for z, r in zip(cuff_z, cuff_r):
        cx = leg_center_x(z, sx)
        c_rings.append([bm.verts.new(Vector((cx + r * math.cos(2 * math.pi * j / segs), r * 1.04 * math.sin(2 * math.pi * j / segs), z))) for j in range(segs)])
    for i in range(len(c_rings) - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm.faces.new((c_rings[i][j], c_rings[i][jn], c_rings[i + 1][jn], c_rings[i + 1][j]))
            f.smooth = True
            f.material_index = 0

    # C) Foot upper leather (from heel Y=+0.08 to toe Y=-0.19 -> 0.27 m long, 0.10 m wide -> rx=0.050, Z from 0.020 above sole up to ankle Z=0.085)
    foot_slices = [
        # (y, rx_half_width, z_top)
        ( 0.080, 0.036, 0.072),  # heel back (Y = +0.08)
        ( 0.050, 0.045, 0.082),  # heel middle
        ( 0.000, 0.046, 0.088),  # ankle / instep
        (-0.060, 0.049, 0.070),  # mid-foot
        (-0.120, 0.050, 0.056),  # ball of foot (0.10 wide!)
        (-0.165, 0.044, 0.048),  # toe box
        (-0.190, 0.026, 0.036),  # rounded toe tip (Y = -0.19)
    ]
    n_arch = 14
    f_rings = []
    for y_pos, rx_w, z_top in foot_slices:
        z_bot = 0.028 if y_pos > 0.010 else 0.020  # sits right on top of 0.03 heel block / 0.02 sole
        ring = []
        for j in range(n_arch):
            t_a = j / float(n_arch - 1)  # 0 (-X side) .. 1 (+X side) over the top arch
            ang = math.pi * (1.0 - t_a)  # pi .. 0
            px = cx_boot + rx_w * math.cos(ang)
            pz = z_bot + (z_top - z_bot) * (math.sin(ang) ** 0.75)
            ring.append(bm.verts.new(Vector((px, y_pos, pz))))
        f_rings.append(ring)
    for i in range(len(f_rings) - 1):
        for j in range(n_arch - 1):
            f = bm.faces.new((f_rings[i][j], f_rings[i][j + 1], f_rings[i + 1][j + 1], f_rings[i + 1][j]))
            f.smooth = True
            f.material_index = 0
        # Bottom closure quad
        fb = bm.faces.new((f_rings[i][0], f_rings[i + 1][0], f_rings[i + 1][-1], f_rings[i][-1]))
        fb.material_index = 0
    # Cap heel back and toe tip
    for idx, inv in ((0, False), (-1, True)):
        c_pt = sum((v.co for v in f_rings[idx]), Vector((0, 0, 0))) / n_arch
        cv = bm.verts.new(c_pt)
        for j in range(n_arch - 1):
            f = bm.faces.new((f_rings[idx][j + 1], f_rings[idx][j], cv) if inv else (f_rings[idx][j], f_rings[idx][j + 1], cv))
            f.smooth = True
            f.material_index = 0

    # D) Sole (0.02 thick, Z=0.00 to 0.02, from heel Y=+0.08 to toe Y=-0.19, 0.10 wide)
    #    + Heel block 0.03 high (Z=0.00 to 0.03) at the back of the sole (Y=+0.015 to +0.080)
    sole_slices = [
        ( 0.080, 0.037, 0.030),  # heel back: 0.03 high!
        ( 0.050, 0.046, 0.030),  # heel mid:  0.03 high!
        ( 0.018, 0.045, 0.030),  # heel front edge: 0.03 high!
        ( 0.012, 0.043, 0.020),  # step down from 0.03 heel block to 0.02 sole
        (-0.060, 0.049, 0.020),
        (-0.120, 0.050, 0.020),  # 0.10 wide
        (-0.165, 0.045, 0.020),
        (-0.190, 0.027, 0.020),  # toe at Y = -0.19
    ]
    sl_rings = []
    for y_pos, rx_w, z_h in sole_slices:
        # 4-vertex cross-section (bottom left, bottom right, top right, top left)
        sl_rings.append([
            bm.verts.new(Vector((cx_boot - rx_w, y_pos, 0.000))),
            bm.verts.new(Vector((cx_boot + rx_w, y_pos, 0.000))),
            bm.verts.new(Vector((cx_boot + rx_w, y_pos, z_h))),
            bm.verts.new(Vector((cx_boot - rx_w, y_pos, z_h))),
        ])
    for i in range(len(sl_rings) - 1):
        for j in range(4):
            jn = (j + 1) % 4
            fs = bm.faces.new((sl_rings[i][j], sl_rings[i][jn], sl_rings[i + 1][jn], sl_rings[i + 1][j]))
            fs.material_index = 1
    bm.faces.new((sl_rings[0][3], sl_rings[0][2], sl_rings[0][1], sl_rings[0][0])).material_index = 1
    bm.faces.new((sl_rings[-1][0], sl_rings[-1][1], sl_rings[-1][2], sl_rings[-1][3])).material_index = 1

    # E) Two straps with brass buckles: one around ankle (Z 0.09) and one around top of shaft (Z 0.38)
    for z_st, r_st in ((0.090, 0.048), (0.380, 0.065)):
        cx_s = leg_center_x(z_st, sx)
        n_s = 20
        hw, ht = 0.009, 0.003
        st_rings = []
        for k in range(n_s):
            th = 2.0 * math.pi * k / n_s
            n_dir = Vector((math.cos(th), 1.04 * math.sin(th), 0.0))
            p_k = Vector((cx_s, 0.0, z_st)) + n_dir * r_st
            st_rings.append([
                bm.verts.new(p_k + Vector((0, 0, -hw)) - n_dir.normalized() * ht),
                bm.verts.new(p_k + Vector((0, 0,  hw)) - n_dir.normalized() * ht),
                bm.verts.new(p_k + Vector((0, 0,  hw)) + n_dir.normalized() * ht),
                bm.verts.new(p_k + Vector((0, 0, -hw)) + n_dir.normalized() * ht),
            ])
        for k in range(n_s):
            kn = (k + 1) % n_s
            for j in range(4):
                jn = (j + 1) % 4
                fst = bm.faces.new((st_rings[k][j], st_rings[k][jn], st_rings[kn][jn], st_rings[kn][j]))
                fst.material_index = 2
                fst.smooth = True
        # Brass buckle on the outside (+-X) of each boot strap
        b_c = Vector((cx_s + sx * (r_st + 0.004), -0.010, z_st))
        bhw, bhh, bht = 0.003, 0.012, 0.011
        ret_b = bmesh.ops.create_cube(bm, size=1.0)
        for v in ret_b["verts"]:
            v.co = b_c + Vector((v.co.x * bhw * 2, v.co.y * bht * 2, v.co.z * bhh * 2))
            for f in v.link_faces:
                f.material_index = 3

    bm.normal_update()
    bm.to_mesh(boot_obj.data)
    bm.free()
    boot_obj.data.update()

    # F) Lacing at the front of the shaft (Lacci_Stivale_SX / DX):
    #    Two rows of eyelets 0.03 apart (cx +- 0.015), from Z 0.10 to Z 0.40,
    #    and 8 crossed laces (X shapes) between them, light tan RGB (0.55, 0.42, 0.28), lace thickness 0.004 (r=0.002).
    lace_obj = bpy.data.objects.get(f"Lacci_Stivale_{side}")
    if lace_obj:
        lace_obj.data.materials.clear()
        lace_obj.data.materials.append(mat_lacci)
        lace_obj.data.materials.append(mat_ottone)
        bm_l = bmesh.new()

        # 9 pairs of eyelets from Z=0.10 to Z=0.40 -> 8 crossed X intervals between them!
        z_eyelets = [0.100 + (0.400 - 0.100) * (k / 8.0) for k in range(9)]

        def front_boot_y(z_val):
            t_s = max(0.0, min(1.0, (z_val - 0.08) / (0.42 - 0.08)))
            r_s = 0.045 * (1.0 - t_s) + 0.060 * t_s
            return -(r_s * 1.04 + 0.002)

        def add_lace_tube(p0, p1, p2, r_l=0.002, segs_l=6):
            pts_l = [Vector(p0), Vector(p1), Vector(p2)]
            rings_l = []
            for idx_p, c_p in enumerate(pts_l):
                t_v = (pts_l[min(2, idx_p + 1)] - pts_l[max(0, idx_p - 1)]).normalized()
                b1 = t_v.cross(Vector((0, 1, 0))).normalized()
                b2 = b1.cross(t_v).normalized()
                rings_l.append([bm_l.verts.new(c_p + b1 * (r_l * math.cos(2 * math.pi * j / segs_l)) + b2 * (r_l * math.sin(2 * math.pi * j / segs_l))) for j in range(segs_l)])
            for i_l in range(2):
                for j in range(segs_l):
                    jn = (j + 1) % segs_l
                    fl = bm_l.faces.new((rings_l[i_l][j], rings_l[i_l][jn], rings_l[i_l + 1][jn], rings_l[i_l + 1][j]))
                    fl.material_index = 0
                    fl.smooth = True

        # Add 9 pairs of tiny brass eyelets (0.03 apart -> dx = +-0.015) and 8 crossed X laces
        for k in range(9):
            zk = z_eyelets[k]
            cx_k = leg_center_x(zk, sx)
            yk = front_boot_y(zk)
            for dx_e in (-0.015, 0.015):
                ret_e = bmesh.ops.create_uvsphere(bm_l, u_segments=6, v_segments=4, radius=0.0032)
                for v in ret_e["verts"]:
                    v.co.y *= 0.5
                    v.co += Vector((cx_k + dx_e, yk, zk))
                for v in ret_e["verts"]:
                    for f in v.link_faces:
                        f.material_index = 1
                        f.smooth = True

            if k < 8:
                zn = z_eyelets[k + 1]
                cx_n = leg_center_x(zn, sx)
                yn = front_boot_y(zn)
                zm = 0.5 * (zk + zn)
                cx_m = 0.5 * (cx_k + cx_n)
                ym = 0.5 * (yk + yn) - 0.0035
                # Cross 1: bottom-left (-0.015, zk) to top-right (+0.015, zn)
                add_lace_tube((cx_k - 0.015, yk, zk), (cx_m, ym - 0.001, zm), (cx_n + 0.015, yn, zn), r_l=0.0022)
                # Cross 2: bottom-right (+0.015, zk) to top-left (-0.015, zn)
                add_lace_tube((cx_k + 0.015, yk, zk), (cx_m, ym + 0.001, zm), (cx_n - 0.015, yn, zn), r_l=0.0022)

        bm_l.normal_update()
        bm_l.to_mesh(lace_obj.data)
        bm_l.free()
        lace_obj.data.update()

log("=== VERIFICA MISURE GROUP 8 ===")
st_vs = bpy.data.objects["Stivale_SX"].data.vertices
kp_vs = bpy.data.objects["Ginocchiere"].data.vertices
log(f"Stivale_SX Y (punta..tallone): {min(v.co.y for v in st_vs):.4f} .. {max(v.co.y for v in st_vs):.4f}m (target -0.19..+0.08, lunghezza 0.27m)")
log(f"Stivale_SX Z: {min(v.co.z for v in st_vs):.4f} .. {max(v.co.z for v in st_vs):.4f}m (target 0.00..0.42)")
log(f"Ginocchiere X range: {min(v.co.x for v in kp_vs):.4f} .. {max(v.co.x for v in kp_vs):.4f}m (both knees +-0.115)")

bpy.ops.wm.save_mainfile()
render_viste("rev_8")
