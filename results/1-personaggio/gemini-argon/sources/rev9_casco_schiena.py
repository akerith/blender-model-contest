import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 9 - The diving helmet and back gear (rev_9)
# - 9.1 Position: carried on upper back ON TOP of cape; centre at X 0, Y +0.25,
#   Z 1.30; top at Z 1.47, bottom at Z 1.13; 0.32 wide and 0.30 deep.
# - 9.2 Shape: brass dome, rounder at top, flattening a bit at bottom on a brass
#   collar ring (breastplate rim) 0.03 high (Z 1.13..1.16), 0.30 across.
# - 9.3 Main porthole (+Y back face): round window 0.13 across, frame a thick
#   brass ring 0.02 wide sticking out 0.025; glass RGB (0.55, 0.70, 0.65),
#   slightly transparent and shiny, with a brass cross grille dividing it into
#   4 parts (2 thin bars, 0.008 wide).
# - 9.4 Side portholes (-X and +X): small round window on each side, 0.07 across,
#   with a brass frame and cross grille.
# - 9.5 Rivets: ring of small brass half-spheres (0.008 across) around main
#   porthole (12 of them) and around collar ring (16 of them).
# - 9.6 Brass bands: two vertical raised bands from top of dome down to collar,
#   0.015 wide, on left and right of main porthole.
# - 9.7 Colour: aged brass RGB (0.62, 0.45, 0.20), metallic 1.0, roughness 0.35,
#   with darker edges RGB (0.35, 0.24, 0.10) where pieces meet.
# - 9.8 Hoses: two ribbed hoses (many short rings, corrugated tube), 0.03 across,
#   coming out of lower sides of helmet:
#   - right side (-X): goes down and coils into a flat spiral disc 0.12 across,
#     hanging at X -0.12, Y +0.20, Z 1.00
#   - left side (+X): goes down and forward under her arm towards belt at X +0.17, Z 1.02.
# - 9.9 Bedroll: horizontal roll 0.34 long and 0.11 across, centre X 0, Y +0.22,
#   Z 1.06; cream-tan canvas RGB (0.66, 0.58, 0.45), held by two brown leather
#   straps (0.02 wide) at X -0.10 and X +0.10.
# - 9.10 Two loops of beige rope (0.12 long, twisted cord) hanging from bottom
#   of helmet over the bedroll.
# - 9.11 Harness: chest straps from shoulders reaching collar ring of helmet at
#   top-left and top-right, plus one horizontal strap around waist at back holding bedroll.
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
        bsdf.inputs["Specular IOR Level"].default_value = 0.25 if metal < 0.5 else 0.5
    if alpha < 1.0:
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.45
    rgb_node = nodes.get("Spec_Tone") or nodes.new("ShaderNodeRGB")
    rgb_node.name = "Spec_Tone"
    rgb_node.outputs[0].default_value = (*render_rgb, 1.0)
    links.new(rgb_node.outputs[0], bsdf.inputs["Base Color"])
    return m

mat_ottone = set_spec_mat("Mat_Ottone", (0.62, 0.45, 0.20), (0.58, 0.40, 0.16), rough=0.35, metal=1.0)
mat_ottone_scuro = set_spec_mat("Mat_OttoneScuro", (0.35, 0.24, 0.10), (0.24, 0.15, 0.05), rough=0.40, metal=1.0)
mat_vetro = set_spec_mat("Mat_VetroOblo", (0.55, 0.70, 0.65), (0.42, 0.60, 0.54), rough=0.12, metal=0.1, alpha=0.75)
mat_sacca = set_spec_mat("Mat_SaccaTela", (0.66, 0.58, 0.45), (0.52, 0.44, 0.32), rough=0.88)
mat_cuoio_medio = set_spec_mat("Mat_CuoioMedio", (0.36, 0.22, 0.12), (0.24, 0.13, 0.06), rough=0.65)
mat_cuoio_scuro = set_spec_mat("Mat_CuoioScuro", (0.24, 0.14, 0.08), (0.14, 0.07, 0.035), rough=0.66)
mat_corda = set_spec_mat("Mat_Corda", (0.70, 0.62, 0.47), (0.56, 0.47, 0.33), rough=0.88)

def add_tube_bm(bm_t, pts, radii, segs=12, closed=False, cap_ends=True, mat_idx=0, corr_amp=0.0, corr_cycles=24):
    rings = []
    n = len(pts)
    for i in range(n):
        c = Vector(pts[i])
        r_item = radii[i] if isinstance(radii, list) else radii
        rx, ry = r_item if isinstance(r_item, (tuple, list)) else (r_item, r_item)
        if closed:
            t = (Vector(pts[(i + 1) % n]) - Vector(pts[(i - 1) % n])).normalized()
        elif i == 0:
            t = (Vector(pts[1]) - c).normalized()
        elif i == n - 1:
            t = (c - Vector(pts[-2])).normalized()
        else:
            t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.88 else Vector((1, 0, 0))
        b1 = t.cross(up).normalized()
        b2 = b1.cross(t).normalized()
        u_t = i / float(max(1, n - 1))
        rmod = 1.0 + (corr_amp * math.sin(2.0 * math.pi * u_t * corr_cycles) if corr_amp else 0.0)
        ring = [bm_t.verts.new(c + b1 * (rx * rmod * math.cos(2 * math.pi * j / segs)) + b2 * (ry * rmod * math.sin(2 * math.pi * j / segs))) for j in range(segs)]
        rings.append(ring)
    limit = n if closed else n - 1
    for i in range(limit):
        inext = (i + 1) % n
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm_t.faces.new((rings[i][j], rings[i][jn], rings[inext][jn], rings[inext][j]))
            f.smooth = True
            f.material_index = mat_idx
    if not closed and cap_ends:
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm_t.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = False
                f.material_index = mat_idx

# 1. Reshape Casco_Palombaro (9.1 - 9.7):
#    Centre at X 0, Y +0.25, Z 1.30; top at Z 1.47, bottom at Z 1.13; 0.32 wide (X in [-0.16, +0.16]), 0.30 deep (Y in [+0.10, +0.40]).
helmet_obj = bpy.data.objects.get("Casco_Palombaro")
if helmet_obj:
    helmet_obj.data.materials.clear()
    helmet_obj.data.materials.append(mat_ottone)        # 0: aged brass
    helmet_obj.data.materials.append(mat_ottone_scuro)  # 1: darker brass edges/seams
    helmet_obj.data.materials.append(mat_vetro)         # 2: glass porthole
    bm = bmesh.new()

    h_center = Vector((0.000, 0.245, 1.300))

    # A) Brass dome (Z from 1.16 to 1.47, rounder at top, flattening a bit at bottom onto collar ring)
    ret_d = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=22, radius=1.0)
    for v in ret_d["verts"]:
        ux, uy, uz = v.co.x, v.co.y, v.co.z
        # Map uz in [-1, 1] -> Z from 1.145 to 1.465
        tz = 0.5 * (uz + 1.0)
        z = 1.145 + tz * (1.465 - 1.145)
        rx = 0.148
        ry = 0.135
        # Flatten front side (towards character's back, uy < -0.55) so it sits against cape without intersecting spine
        if uy < -0.55:
            uy = -0.55 + (uy + 0.55) * 0.45
        # Slight waist above collar ring
        if tz < 0.20:
            flare = (0.20 - tz) / 0.20
            rx = rx * (1.0 - 0.05 * (1.0 - flare))
        v.co = Vector((ux * rx, 0.245 + uy * ry, z))
    for f in bm.faces:
        f.smooth = True
        f.material_index = 0

    # B) Brass collar ring (breastplate rim) at bottom: 0.03 high (Z = 1.13 to 1.16), 0.30 across (rx=0.150, ry=0.135)
    n_col = 32
    col_rings = []
    for z_c, r_x, r_y, m_i in (
        (1.130, 0.150, 0.136, 1),
        (1.134, 0.152, 0.138, 0),
        (1.156, 0.148, 0.134, 0),
        (1.160, 0.138, 0.125, 1),
    ):
        ring = []
        for k in range(n_col):
            th = 2.0 * math.pi * k / n_col
            ring.append(bm.verts.new(Vector((r_x * math.cos(th), 0.245 + r_y * math.sin(th), z_c))))
        col_rings.append((ring, m_i))
    for i in range(len(col_rings) - 1):
        r0, m0 = col_rings[i]
        r1, m1 = col_rings[i + 1]
        for k in range(n_col):
            kn = (k + 1) % n_col
            f = bm.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
            f.smooth = True
            f.material_index = m0
    # Close bottom of collar ring at Z=1.130
    c_bot_v = bm.verts.new(Vector((0.0, 0.245, 1.130)))
    for k in range(n_col):
        kn = (k + 1) % n_col
        fb = bm.faces.new((col_rings[0][0][kn], col_rings[0][0][k], c_bot_v))
        fb.material_index = 1

    # C) 16 small brass half-sphere rivets (0.008 across -> radius 0.004) around the collar ring (9.5)
    for k in range(16):
        th = 2.0 * math.pi * k / 16.0
        r_pos = Vector((0.151 * math.cos(th), 0.245 + 0.137 * math.sin(th), 1.145))
        ret_r = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.004)
        for v in ret_r["verts"]:
            v.co += r_pos
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0

    # D) Two vertical raised brass bands from top of dome down to collar, 0.015 wide, on left and right of main porthole (9.6)
    for sx_b in (-1.0, 1.0):
        band_pts = []
        for k in range(15):
            t = k / 14.0  # 0 at top of dome (Z=1.462), 1 at collar (Z=1.158)
            ang_p = math.radians(12.0 + t * 145.0)
            z_b = 1.305 + 0.160 * math.cos(ang_p)
            r_yz = 0.136 * math.sin(ang_p)
            # Positioned at X = +-0.082 (just outside the 0.13 main porthole!)
            x_b = sx_b * (0.025 + 0.062 * math.sin(ang_p * 0.85))
            y_b = 0.245 + math.sqrt(max(0.001, r_yz * r_yz - (x_b * 0.55) ** 2))
            band_pts.append((x_b, y_b, z_b))
        add_tube_bm(bm, band_pts, (0.0075, 0.0045), segs=8, closed=False, cap_ends=True, mat_idx=0)

    # Top valve lug reaching Z = 1.470 so exact top of helmet is at Z = 1.47 (9.1)
    add_tube_bm(bm, [(0.0, 0.245, 1.445), (0.0, 0.245, 1.470)], [0.022, 0.018], segs=12, closed=False, cap_ends=True, mat_idx=0)
    # Angled left-top air valve (visible over her left collarbone in front view)
    add_tube_bm(bm, [(0.065, 0.215, 1.420), (0.098, 0.195, 1.458)], [0.018, 0.020], segs=10, closed=False, cap_ends=True, mat_idx=0)

    # Helper to build porthole (9.3 & 9.4)
    def build_porthole(c_base, norm_dir, up_dir, outer_diam, frame_width, stick_out, n_rivets):
        n_v = Vector(norm_dir).normalized()
        u_v = Vector(up_dir).normalized()
        r_v = u_v.cross(n_v).normalized()
        u_v = n_v.cross(r_v).normalized()
        c_p = Vector(c_base)

        r_outer = outer_diam * 0.5
        r_inner = r_outer - frame_width

        # Thick brass ring frame sticking out `stick_out` from dome, with dark edge seam at base (9.7)
        n_seg = 28
        ring_base_o, ring_front_o, ring_front_i, ring_glass = [], [], [], []
        for k in range(n_seg):
            th = 2.0 * math.pi * k / n_seg
            d2 = r_v * math.cos(th) + u_v * math.sin(th)
            ring_base_o.append(bm.verts.new(c_p - n_v * 0.008 + d2 * (r_outer + 0.002)))
            ring_front_o.append(bm.verts.new(c_p + n_v * stick_out + d2 * r_outer))
            ring_front_i.append(bm.verts.new(c_p + n_v * stick_out + d2 * r_inner))
            ring_glass.append(bm.verts.new(c_p + n_v * (stick_out - 0.006) + d2 * r_inner))

        c_glass = bm.verts.new(c_p + n_v * (stick_out - 0.002))
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            f1 = bm.faces.new((ring_base_o[k], ring_base_o[kn], ring_front_o[kn], ring_front_o[k]))
            f1.material_index = 1 if (k % 2 == 0 and False) else 0
            f1.smooth = True
            f2 = bm.faces.new((ring_front_o[k], ring_front_o[kn], ring_front_i[kn], ring_front_i[k]))
            f2.material_index = 0
            f2.smooth = True
            f3 = bm.faces.new((ring_front_i[k], ring_front_i[kn], ring_glass[kn], ring_glass[k]))
            f3.material_index = 1
            f3.smooth = True
            fg = bm.faces.new((ring_glass[k], ring_glass[kn], c_glass))
            fg.material_index = 2
            fg.smooth = True

        # Cross grille dividing window into 4 parts: 2 thin bars (1 vertical, 1 horizontal), 0.008 wide (r=0.004)
        bar_r = 0.004
        for axis_bar in (u_v, r_v):
            b_pts = []
            for s in range(7):
                st = -1.0 + 2.0 * s / 6.0
                arch = stick_out + 0.002 + 0.006 * (1.0 - st * st)
                b_pts.append(tuple(c_p + axis_bar * (st * (r_inner + 0.003)) + n_v * arch))
            add_tube_bm(bm, b_pts, bar_r, segs=8, closed=False, cap_ends=True, mat_idx=0)

        # Ring of small brass half-spheres (0.008 across -> r=0.004) around porthole frame
        r_rivet_circle = r_outer - frame_width * 0.45
        for k in range(n_rivets):
            th = 2.0 * math.pi * k / n_rivets + (math.pi / n_rivets)
            rv_pos = c_p + (r_v * math.cos(th) + u_v * math.sin(th)) * r_rivet_circle + n_v * (stick_out + 0.001)
            ret_rv = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.004)
            for v in ret_rv["verts"]:
                v.co += rv_pos
                for f in v.link_faces:
                    f.smooth = True
                    f.material_index = 0

    # E) Main porthole on back face (+Y): 0.13 across, frame 0.02 wide, sticking out 0.025, 12 rivets, 2-bar cross grille (9.3, 9.5)
    build_porthole(
        c_base=(0.000, 0.375, 1.300),
        norm_dir=(0.0, 1.0, 0.0),
        up_dir=(0.0, 0.0, 1.0),
        outer_diam=0.130,
        frame_width=0.020,
        stick_out=0.025,
        n_rivets=12,
    )

    # F) Side portholes (-X and +X): 0.07 across, brass frame (9.4)
    for sx_s in (-1.0, 1.0):
        build_porthole(
            c_base=(sx_s * 0.142, 0.245, 1.300),
            norm_dir=(sx_s, 0.0, 0.0),
            up_dir=(0.0, 0.0, 1.0),
            outer_diam=0.070,
            frame_width=0.012,
            stick_out=0.018,
            n_rivets=8,
        )

    bm.normal_update()
    bm.to_mesh(helmet_obj.data)
    bm.free()
    helmet_obj.data.update()

# 2. Reshape Tubi_Casco (9.8 Hoses):
#    Two ribbed hoses (made of many short rings, corrugated tube), 0.03 across (radius 0.015),
#    coming out of the lower sides of the helmet:
#    - Right side (-X): goes down and coils into a flat spiral disc, 0.12 across, hanging at X -0.12, Y +0.20, Z 1.00
#    - Left side (+X): goes down and forward under her arm towards the belt at X +0.17, Z 1.02.
hoses_obj = bpy.data.objects.get("Tubi_Casco")
if hoses_obj:
    hoses_obj.data.materials.clear()
    hoses_obj.data.materials.append(mat_ottone_scuro)
    bm = bmesh.new()

    # Right hose (-X): from lower right side of helmet (-0.135, 0.245, 1.155) down into a flat spiral disc
    # 0.12 across (outer radius 0.060) centered at X = -0.12, Y = +0.20, Z = 1.00 (visible in side views!)
    right_hose_pts = [
        (-0.135, 0.245, 1.155),
        (-0.148, 0.235, 1.115),
        (-0.145, 0.220, 1.070),
    ]
    # Spiral coil in YZ/XZ plane at X = -0.12, Y_c = +0.20, Z_c = 1.00, outer diameter 0.12 (r from 0.055 down to 0.016)
    n_spiral = 38
    for k in range(n_spiral):
        t = k / float(n_spiral - 1)
        ang = t * 2.0 * math.pi * 2.1 + math.pi * 0.55  # ~2.1 turns
        r_sp = 0.052 * (1.0 - 0.72 * t)                 # outer diameter = 2*(0.052 + 0.010) ~ 0.12 m!
        px = -0.125 - 0.015 * math.cos(ang)             # slight X tilt so spiral shows from side AND back
        py = 0.200 - r_sp * math.cos(ang)
        pz = 1.000 + r_sp * math.sin(ang)
        right_hose_pts.append((px, py, pz))
    add_tube_bm(bm, right_hose_pts, 0.0145, segs=12, closed=False, cap_ends=True, mat_idx=0, corr_amp=0.18, corr_cycles=36)

    # Left hose (+X): from lower left side of helmet (+0.135, 0.245, 1.155) going down and forward under her left arm
    # towards the belt at X = +0.17, Z = 1.02
    left_hose_pts = [
        (0.135,  0.245, 1.155),
        (0.165,  0.230, 1.120),
        (0.185,  0.195, 1.080),
        (0.195,  0.145, 1.048),
        (0.192,  0.085, 1.028),
        (0.182,  0.030, 1.020),
        (0.170, -0.010, 1.020),
    ]
    add_tube_bm(bm, left_hose_pts, 0.0150, segs=12, closed=False, cap_ends=True, mat_idx=0, corr_amp=0.18, corr_cycles=22)

    bm.normal_update()
    bm.to_mesh(hoses_obj.data)
    bm.free()
    hoses_obj.data.update()

# 3. Reshape Sacca_Arrotolata (9.9 Bedroll, 9.10 Back rope loops, 9.11 Back waist harness):
#    - Bedroll: horizontal roll 0.34 long (X from -0.17 to +0.17) and 0.11 across (radius 0.055),
#      centre X 0, Y +0.22, Z 1.06; cream-tan canvas RGB (0.66, 0.58, 0.45),
#      held by two brown leather straps around it (each 0.02 wide) at X -0.10 and X +0.10.
#    - 2 loops of beige rope (0.12 long, same twisted rope as 7.1) hanging from bottom of helmet over bedroll.
#    - Back waist strap holding the bedroll + upper harness straps connecting chest straps to helmet collar ring.
sacca_obj = bpy.data.objects.get("Sacca_Arrotolata")
if sacca_obj:
    sacca_obj.data.materials.clear()
    sacca_obj.data.materials.append(mat_sacca)        # 0: cream-tan canvas
    sacca_obj.data.materials.append(mat_cuoio_medio)  # 1: brown leather straps & harness
    sacca_obj.data.materials.append(mat_corda)        # 2: beige rope loops
    sacca_obj.data.materials.append(mat_ottone)       # 3: brass buckles/rings
    bm = bmesh.new()

    # A) Horizontal bedroll cylinder: 0.34 long (X = -0.17 to +0.17), 0.11 across (r = 0.055), centre (0, 0.22, 1.06)
    roll_pts = [
        (-0.170, 0.216, 1.062),
        (-0.085, 0.220, 1.060),
        ( 0.000, 0.222, 1.060),
        ( 0.085, 0.220, 1.060),
        ( 0.170, 0.216, 1.062),
    ]
    add_tube_bm(bm, roll_pts, [0.052, 0.055, 0.055, 0.055, 0.052], segs=20, closed=False, cap_ends=True, mat_idx=0)

    # B) Two brown leather straps around bedroll (each 0.02 wide) at X = -0.10 and X = +0.10, reaching up to helmet collar ring
    for sx_s in (-0.100, 0.100):
        s_ring = []
        for k in range(20):
            th = 2.0 * math.pi * k / 20.0
            s_ring.append((sx_s, 0.220 + 0.057 * math.cos(th), 1.060 + 0.057 * math.sin(th)))
        add_tube_bm(bm, s_ring, (0.010, 0.004), segs=8, closed=True, cap_ends=False, mat_idx=1)

    # C) Two loops of beige twisted rope (0.12 long) hanging from bottom of helmet (Z=1.13) over the bedroll (down to Z=1.01)
    for sx_r, x_c in ((-1.0, -0.045), (1.0, 0.045)):
        n_rp = 28
        r_pts = []
        for k in range(n_rp):
            th = 2.0 * math.pi * k / n_rp
            # Oval loop 0.12 high (Z from 1.01 to 1.13), 0.055 wide, draping over the back of the bedroll (Y ~ 0.275)
            px = x_c + 0.026 * math.sin(th)
            py = 0.268 + 0.016 * math.sin(th * 0.5)
            pz = 1.070 + 0.060 * math.cos(th)
            r_pts.append((px, py, pz))
        add_tube_bm(bm, r_pts, 0.0070, segs=10, closed=True, cap_ends=False, mat_idx=2, corr_amp=0.18, corr_cycles=14)

    # D) Harness (9.11):
    #    - Upper shoulder straps connecting chest straps (at X=+-0.13, Z=1.41) down to top-left and top-right of helmet collar ring (X=+-0.12, Y=0.19, Z=1.16)
    for sx_h in (-1.0, 1.0):
        h_pts = [
            (sx_h * 0.130, 0.030, 1.410),
            (sx_h * 0.135, 0.120, 1.340),
            (sx_h * 0.132, 0.165, 1.240),
            (sx_h * 0.125, 0.185, 1.155),
        ]
        add_tube_bm(bm, h_pts, (0.016, 0.005), segs=8, closed=False, cap_ends=True, mat_idx=1)

    #    - Horizontal strap around waist at the back, holding the bedroll (Z = 1.06)
    back_waist_pts = [
        (-0.145, 0.030, 1.080),
        (-0.140, 0.135, 1.070),
        (-0.105, 0.215, 1.060),
        ( 0.000, 0.230, 1.060),
        ( 0.105, 0.215, 1.060),
        ( 0.140, 0.135, 1.070),
        ( 0.145, 0.030, 1.080),
    ]
    add_tube_bm(bm, back_waist_pts, (0.014, 0.005), segs=8, closed=False, cap_ends=True, mat_idx=1)

    bm.normal_update()
    bm.to_mesh(sacca_obj.data)
    bm.free()
    sacca_obj.data.update()

# Also ensure Mantella_Corpo does not poke through the helmet or bedroll on the upper back
cape_obj = bpy.data.objects.get("Mantella_Corpo")
if cape_obj:
    for v in cape_obj.data.vertices:
        if 1.00 < v.co.z < 1.38 and abs(v.co.x) < 0.17 and v.co.y > 0.125:
            v.co.y = min(v.co.y, 0.125)
    cape_obj.data.update()

h_vs = helmet_obj.data.vertices
s_vs = sacca_obj.data.vertices
log("=== VERIFICA MISURE GROUP 9 ===")
log(f"Casco_Palombaro Z: {min(v.co.z for v in h_vs):.4f} .. {max(v.co.z for v in h_vs):.4f}m (target 1.13..1.47)")
log(f"Casco_Palombaro X width: {max(v.co.x for v in h_vs)-min(v.co.x for v in h_vs):.4f}m (target 0.32), Y depth: {max(v.co.y for v in h_vs)-min(v.co.y for v in h_vs):.4f}m (target 0.30)")
log(f"Sacca_Arrotolata X length: {max(v.co.x for v in s_vs)-min(v.co.x for v in s_vs):.4f}m (target 0.34)")

bpy.ops.wm.save_mainfile()
render_viste("rev_9")
