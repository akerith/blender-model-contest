import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 4 - Torso: jacket, straps, belts (rev_4)
# - 4.1 Jacket: dark navy blue RGB (0.13, 0.16, 0.22), Z 1.06 to 1.42, following
#   Group 1 chest (0.32x0.21 at Z 1.27) and waist (0.27x0.18 at Z 1.08), with
#   5 vertical seam lines (thin dark grooves) on the front.
# - 4.2 Tunic skirt: Z 1.06 down to Z 0.80 at front and back, open on the sides,
#   0.38 wide, uneven lower edge.
# - 4.3 Cross straps (bandoliers): two brown leather straps 0.035 wide, 0.008 thick,
#   RGB (0.36, 0.22, 0.12), from (+-0.13, Z 1.41) to (-+0.15, Z 1.04), crossing at
#   Z 1.25 on breastbone, continuing over shoulders and down the back, with square
#   brass buckles (0.03 x 0.03) on each strap at Z 1.30.
# - 4.4 Horizontal brown strap around chest at Z 1.20, 0.03 wide.
# - 4.5 Main belt: brown leather, 0.06 high (Z 1.06 to 1.12), 0.006 thick, standing
#   0.006 out of jacket; centre front rectangular brass buckle 0.07 wide, 0.05 high,
#   with a frame and a pin.
# - 4.6 Lower hip belt: 0.04 high, slanting: higher on left (Z 1.00 at X +0.17)
#   and lower on right (Z 0.94 at X -0.17).
# - 4.7 Medallion: round brass disc 0.04 across, hanging on a short cord 0.04 below
#   main buckle, centre at Z 0.99, X 0.
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

mat_giacca = set_spec_mat("Mat_GiaccaBlu", (0.13, 0.16, 0.22), (0.07, 0.10, 0.16), rough=0.88)
mat_cucitura = set_spec_mat("Mat_CucituraGiacca", (0.07, 0.09, 0.13), (0.03, 0.04, 0.07), rough=0.92)
mat_cuoio_cintura = set_spec_mat("Mat_CuoioMedio", (0.36, 0.22, 0.12), (0.24, 0.13, 0.06), rough=0.65)
mat_cuoio_scuro = set_spec_mat("Mat_CuoioScuro", (0.26, 0.16, 0.09), (0.15, 0.08, 0.04), rough=0.65)
mat_ottone = set_spec_mat("Mat_Ottone", (0.62, 0.45, 0.20), (0.58, 0.40, 0.16), rough=0.35, metal=1.0)

# Helper: analytical torso surface (rx, ry, y_off) at height Z
def torso_profile(z):
    # Returns (rx, ry, y_off)
    table = [
        (0.80, 0.190, 0.115,  0.008),  # Tunic skirt bottom (0.38 wide)
        (0.90, 0.170, 0.110,  0.008),  # Hips (0.34 wide, 0.22 deep)
        (1.00, 0.150, 0.098,  0.003),  # Upper hips
        (1.08, 0.135, 0.090,  0.000),  # Waist narrowest (0.27 wide, 0.18 deep)
        (1.20, 0.150, 0.100, -0.005),  # Under-bust ribcage
        (1.27, 0.160, 0.105, -0.008),  # Chest fullest (0.32 wide, 0.21 deep)
        (1.36, 0.175, 0.096, -0.003),  # Upper chest / clavicles
        (1.40, 0.160, 0.085,  0.000),  # Shoulder slope
        (1.42, 0.085, 0.072,  0.000),  # Jacket collar base
    ]
    if z <= table[0][0]:
        return table[0][1], table[0][2], table[0][3]
    if z >= table[-1][0]:
        return table[-1][1], table[-1][2], table[-1][3]
    for i in range(len(table) - 1):
        z0, rx0, ry0, yo0 = table[i]
        z1, rx1, ry1, yo1 = table[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return rx0 + t * (rx1 - rx0), ry0 + t * (ry1 - ry0), yo0 + t * (yo1 - yo0)
    return table[-1][1], table[-1][2], table[-1][3]

# 1. Reshape Giacca_Torso in-place:
#    - Upper jacket from Z=1.06 to Z=1.42 with 5 vertical seam grooves on the front
#    - Tunic skirt from Z=1.06 down to Z=0.80, open on the sides (+-X), 0.38 wide, uneven lower edge
giacca_obj = bpy.data.objects.get("Giacca_Torso")
if giacca_obj:
    bm = bmesh.new()
    bm.from_mesh(giacca_obj.data)
    bm.faces.ensure_lookup_table()
    if len(giacca_obj.data.materials) < 2:
        giacca_obj.data.materials.append(mat_cucitura)

    # Identify connected components (main torso vs the 3 old chest bands)
    visited = set()
    comps = []
    for f in bm.faces:
        if f.index in visited:
            continue
        comp = []
        q = [f]
        visited.add(f.index)
        while q:
            c = q.pop()
            comp.append(c)
            for v in c.verts:
                for lf in v.link_faces:
                    if lf.index not in visited:
                        visited.add(lf.index)
                        q.append(lf)
        comps.append(comp)
    comps.sort(key=lambda c: len(c), reverse=True)
    main_comp = comps[0]
    old_bands = comps[1:]

    # Remove old horizontal chest bands and replace with 5 vertical front seam lines (thin dark grooves)
    for b_comp in old_bands:
        bmesh.ops.delete(bm, geom=b_comp, context='FACES')

    main_verts = list({v for f in main_comp for v in f.verts})
    zmin_g = min(v.co.z for v in main_verts)
    zmax_g = max(v.co.z for v in main_verts)

    # Subdivide main jacket mesh once so we have plenty of resolution for side slits, uneven hem, and vertical seams
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)

    # Delete side-slit faces on the tunic skirt below Z = 1.05 (4.2: "open on the sides")
    faces_to_del = []
    for f in bm.faces:
        fc = f.calc_center_median()
        if fc.z < 1.04:
            # Side slits at +-X: gap opens wider towards Z=0.80
            t_down = (1.04 - fc.z) / 0.24
            slit_y_half = 0.014 + 0.032 * t_down
            if abs(fc.y - 0.006) < slit_y_half and abs(fc.x) > 0.08:
                faces_to_del.append(f)
    if faces_to_del:
        bmesh.ops.delete(bm, geom=faces_to_del, context='FACES')

    for v in bm.verts:
        tz = max(0.0, min(1.0, (v.co.z - zmin_g) / max(1e-5, zmax_g - zmin_g)))
        z = 0.800 + tz * (1.420 - 0.800)
        r_xy = math.hypot(v.co.x, v.co.y)
        if r_xy < 0.015:
            v.co.z = z
            continue
        ang = math.atan2(v.co.y, v.co.x)  # -pi/2 is front (-Y), +pi/2 is back (+Y)
        cx = math.cos(ang)
        sy = math.sin(ang)
        rx, ry, y_off = torso_profile(z)

        # Female bust contour around Z=1.27 on front (-Y)
        if 1.15 <= z <= 1.35 and sy < -0.15:
            bust = math.exp(-((abs(cx) - 0.42) ** 2 / 0.12 + (z - 1.27) ** 2 / 0.004))
            ry += 0.012 * bust * (-sy)

        # 5 vertical seam grooves carved into the front jacket (X_norm = -0.56, -0.28, 0.0, +0.28, +0.56)
        groove = 0.0
        if 1.07 <= z <= 1.39 and sy < -0.25:
            for s_cx in (-0.56, -0.28, 0.0, 0.28, 0.56):
                d_seam = abs(cx - s_cx)
                if d_seam < 0.055:
                    groove = -0.0045 * math.cos((d_seam / 0.055) * math.pi * 0.5) ** 2

        # Uneven lower edge on tunic skirt below Z=0.88 (4.2)
        z_hem = z
        if z < 0.90:
            t_hem = (0.90 - z) / 0.10
            uneven = (0.014 * math.sin(ang * 7.0 + 0.5) + 0.010 * math.cos(ang * 13.0 - 0.8)) * t_hem
            z_hem = max(0.800, z + uneven)

        v.co.x = (rx + groove) * cx
        v.co.y = y_off + (ry + groove) * sy
        v.co.z = z_hem

    # Add 5 explicit vertical dark seam strips in the front grooves so they read clearly in renders
    for s_x in (-0.088, -0.044, 0.000, 0.044, 0.088):
        n_s = 10
        hw = 0.0028
        prev_pair = None
        for i in range(n_s):
            zs = 1.075 + (1.385 - 1.075) * (i / float(n_s - 1))
            rx, ry, y_off = torso_profile(zs)
            u_x = max(-0.95, min(0.95, s_x / rx))
            sy = -math.sqrt(1.0 - u_x * u_x)
            bust = math.exp(-((abs(u_x) - 0.42) ** 2 / 0.12 + (zs - 1.27) ** 2 / 0.004)) if 1.15 <= zs <= 1.35 else 0.0
            ys = y_off + (ry + 0.012 * bust * (-sy) - 0.0015) * sy
            v_l = bm.verts.new(Vector((s_x - hw, ys, zs)))
            v_r = bm.verts.new(Vector((s_x + hw, ys, zs)))
            if prev_pair:
                f = bm.faces.new((prev_pair[0], prev_pair[1], v_r, v_l))
                f.material_index = 1
                f.smooth = True
            prev_pair = (v_l, v_r)

    bm.normal_update()
    bm.to_mesh(giacca_obj.data)
    bm.free()
    giacca_obj.data.update()

# Helper to build rectangular leather straps in a bmesh
def add_strap_to_bm(bm_t, pts, width, thick, closed=False):
    rings = []
    n = len(pts)
    for i in range(n):
        p = Vector(pts[i])
        if closed:
            t = (Vector(pts[(i + 1) % n]) - Vector(pts[(i - 1) % n])).normalized()
        elif i == 0:
            t = (Vector(pts[1]) - p).normalized()
        elif i == n - 1:
            t = (p - Vector(pts[-2])).normalized()
        else:
            t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        out_n = Vector((p.x, p.y, 0.0))
        if out_n.length < 1e-4:
            out_n = Vector((0.0, -1.0, 0.0))
        else:
            out_n.normalize()
        b1 = t.cross(out_n).normalized()
        out_n = b1.cross(t).normalized()
        hw, ht = width * 0.5, thick * 0.5
        rings.append([
            bm_t.verts.new(p - b1 * hw - out_n * ht),
            bm_t.verts.new(p + b1 * hw - out_n * ht),
            bm_t.verts.new(p + b1 * hw + out_n * ht),
            bm_t.verts.new(p - b1 * hw + out_n * ht),
        ])
    limit = n if closed else n - 1
    for i in range(limit):
        inext = (i + 1) % n
        for j in range(4):
            jn = (j + 1) % 4
            bm_t.faces.new((rings[i][j], rings[i][jn], rings[inext][jn], rings[inext][j]))
    if not closed:
        bm_t.faces.new((rings[0][3], rings[0][2], rings[0][1], rings[0][0]))
        bm_t.faces.new((rings[-1][0], rings[-1][1], rings[-1][2], rings[-1][3]))

# 2. Reshape Cinghie_Petto (4.3 & 4.4):
#    - Strap 1: top of LEFT shoulder (X +0.13, Z 1.41) -> breastbone (X 0, Z 1.25) -> RIGHT hip (X -0.15, Z 1.04)
#      and over shoulder down the back to diving helmet harness (X +0.11, Y +0.14, Z 1.22)
#    - Strap 2: top of RIGHT shoulder (X -0.13, Z 1.41) -> breastbone (X 0, Z 1.25) -> LEFT hip (X +0.15, Z 1.04)
#      and over shoulder down the back to diving helmet harness (X -0.11, Y +0.14, Z 1.22)
#    - Width 0.035, thickness 0.008, RGB (0.36, 0.22, 0.12)
#    - Horizontal chest strap at Z 1.20, 0.03 wide (4.4)
cinghie_obj = bpy.data.objects.get("Cinghie_Petto")
if cinghie_obj:
    cinghie_obj.data.materials.clear()
    cinghie_obj.data.materials.append(mat_cuoio_cintura)
    bm = bmesh.new()

    def front_strap_pt(x_val, z_val, extra_out=0.005):
        rx, ry, y_off = torso_profile(z_val)
        rx_e = rx + 0.008
        ry_e = ry + 0.012
        u = max(-0.98, min(0.98, x_val / rx_e))
        y_val = y_off - (ry_e + extra_out) * math.sqrt(max(0.04, 1.0 - u * u))
        return (x_val, y_val, z_val)

    for sign_x, extra in ((1.0, 0.005), (-1.0, 0.009)):
        pts = [
            # Back harness end (meets helmet collar ring at top-left / top-right)
            (sign_x * 0.115,  0.145, 1.240),
            (sign_x * 0.125,  0.105, 1.350),
            (sign_x * 0.130,  0.035, 1.412),
            (sign_x * 0.130, -0.025, 1.410),  # Top of shoulder (X +-0.13, Z 1.41)
        ]
        # Across chest passing through (0, Z=1.25) to opposite hip (-+0.15, Z=1.04)
        n_f = 15
        for k in range(1, n_f + 1):
            t = k / float(n_f)
            # Quadratic path through (sign_x*0.13, 1.41) at t=0, (0.0, 1.25) at t=0.5, (-sign_x*0.15, 1.04) at t=1.0
            xk = (1 - t) * (1 - 2 * t) * (sign_x * 0.13) + 4 * t * (1 - t) * 0.0 + t * (2 * t - 1) * (-sign_x * 0.15)
            zk = (1 - t) * (1 - 2 * t) * 1.410 + 4 * t * (1 - t) * 1.250 + t * (2 * t - 1) * 1.040
            pts.append(front_strap_pt(xk, zk, extra_out=extra))
        add_strap_to_bm(bm, pts, width=0.035, thick=0.008, closed=False)

    # 4.4 Horizontal brown strap around the chest just under the breasts, Z 1.20, 0.03 wide
    rx_c, ry_c, yo_c = torso_profile(1.20)
    h_pts = []
    for k in range(32):
        th = 2.0 * math.pi * k / 32.0
        h_pts.append(((rx_c + 0.006) * math.cos(th), yo_c + (ry_c + 0.006) * math.sin(th), 1.200))
    add_strap_to_bm(bm, h_pts, width=0.030, thick=0.008, closed=True)

    bm.normal_update()
    bm.to_mesh(cinghie_obj.data)
    bm.free()
    cinghie_obj.data.update()

# Helper to add a brass buckle with frame and pin to a bmesh
def add_buckle_to_bm(bm_t, center, width, height, thick, rot_euler_deg, with_pin=True):
    from mathutils import Euler
    rot_m = Euler([math.radians(a) for a in rot_euler_deg], 'XYZ').to_matrix()
    c_v = Vector(center)
    hw, hh, ht = width * 0.5, height * 0.5, thick * 0.5
    iw, ih = hw * 0.68, hh * 0.66
    outer = [bm_t.verts.new(c_v + rot_m @ Vector((sx * hw, sy * ht, sz * hh))) for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    inner = [bm_t.verts.new(c_v + rot_m @ Vector((sx * iw, sy * ht, sz * ih))) for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4):
        inext = (i + 1) % 4
        bm_t.faces.new((outer[i], outer[inext], inner[inext], inner[i]))
        bm_t.faces.new((outer[4 + inext], outer[4 + i], inner[4 + i], inner[4 + inext]))
        bm_t.faces.new((outer[i], outer[4 + i], outer[4 + inext], outer[inext]))
        bm_t.faces.new((inner[inext], inner[4 + inext], inner[4 + i], inner[i]))
    if with_pin:
        # Center vertical bar + horizontal pin
        pw, pt = width * 0.07, ht * 0.85
        pin_v = [bm_t.verts.new(c_v + rot_m @ Vector((sx * pw, sy * pt, sz * ih))) for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for i in range(4):
            inext = (i + 1) % 4
            bm_t.faces.new((pin_v[i], pin_v[4 + i], pin_v[4 + inext], pin_v[inext]))

# 3. Reshape Fibbie_Petto (4.3: small square brass buckle 0.03 x 0.03 on each strap at Z 1.30)
fibbie_petto_obj = bpy.data.objects.get("Fibbie_Petto")
if fibbie_petto_obj:
    fibbie_petto_obj.data.materials.clear()
    fibbie_petto_obj.data.materials.append(mat_ottone)
    bm = bmesh.new()
    # At Z=1.30 along the two cross straps, X is approximately +-0.044
    rx_b, ry_b, yo_b = torso_profile(1.30)
    y_b = yo_b - ry_b - 0.016
    add_buckle_to_bm(bm, ( 0.044, y_b, 1.300), 0.030, 0.030, 0.010, (6, -38, 10), with_pin=True)
    add_buckle_to_bm(bm, (-0.044, y_b, 1.300), 0.030, 0.030, 0.010, (6,  38, -10), with_pin=True)
    bm.normal_update()
    bm.to_mesh(fibbie_petto_obj.data)
    bm.free()
    fibbie_petto_obj.data.update()

# 4. Reshape Cinture_Vita (4.5 Main belt: 0.06 high, Z 1.06 to 1.12, 0.006 thick, standing 0.006 out of jacket;
#    4.6 Lower hip belt: 0.04 high, slanting from Z 1.00 at X +0.17 to Z 0.94 at X -0.17)
cinture_obj = bpy.data.objects.get("Cinture_Vita")
if cinture_obj:
    cinture_obj.data.materials.clear()
    cinture_obj.data.materials.append(mat_cuoio_cintura)
    bm = bmesh.new()

    # 4.5 Main belt at Z = 1.09 (spanning 1.06 to 1.12 -> height 0.06), thickness 0.006, standing 0.006 out of jacket
    rx_w, ry_w, yo_w = torso_profile(1.09)
    # Centerline stands 0.006 + 0.003 = 0.009 outside jacket surface
    belt1_pts = []
    for k in range(36):
        th = 2.0 * math.pi * k / 36.0
        belt1_pts.append(((rx_w + 0.009) * math.cos(th), yo_w + (ry_w + 0.009) * math.sin(th), 1.090))
    add_strap_to_bm(bm, belt1_pts, width=0.060, thick=0.006, closed=True)

    # 4.6 Lower hip belt: 0.04 high, slanting: Z 1.00 at X +0.17 (left) and Z 0.94 at X -0.17 (right)
    belt2_pts = []
    for k in range(36):
        th = 2.0 * math.pi * k / 36.0
        cx, sy = math.cos(th), math.sin(th)
        z_b2 = 0.970 + 0.030 * cx  # +1 -> 1.00, -1 -> 0.94
        rx_2, ry_2, yo_2 = torso_profile(z_b2)
        # Ensure X reaches +-0.17 at sides
        rx_use = max(rx_2 + 0.008, 0.170)
        ry_use = ry_2 + 0.008
        belt2_pts.append((rx_use * cx, yo_2 + ry_use * sy, z_b2))
    add_strap_to_bm(bm, belt2_pts, width=0.040, thick=0.006, closed=True)

    bm.normal_update()
    bm.to_mesh(cinture_obj.data)
    bm.free()
    cinture_obj.data.update()

# 5. Reshape Fibbie_Vita (4.5: at centre front of main belt a rectangular brass buckle 0.07 wide, 0.05 high, with frame and pin)
fibbie_vita_obj = bpy.data.objects.get("Fibbie_Vita")
if fibbie_vita_obj:
    fibbie_vita_obj.data.materials.clear()
    fibbie_vita_obj.data.materials.append(mat_ottone)
    bm = bmesh.new()
    rx_w, ry_w, yo_w = torso_profile(1.09)
    y_front_w = yo_w - (ry_w + 0.013)
    add_buckle_to_bm(bm, (0.000, y_front_w, 1.090), 0.070, 0.050, 0.010, (0, 0, 0), with_pin=True)
    # Also small buckle on the slanting lower hip belt
    rx_2, ry_2, yo_2 = torso_profile(0.97)
    add_buckle_to_bm(bm, (0.032, yo_2 - (ry_2 + 0.012), 0.976), 0.042, 0.042, 0.009, (0, 10, 0), with_pin=True)
    bm.normal_update()
    bm.to_mesh(fibbie_vita_obj.data)
    bm.free()
    fibbie_vita_obj.data.update()

# 6. Reshape Medaglione_Cintura (4.7: round brass disc 0.04 across, hanging on a short cord 0.04 below main buckle, centre at Z 0.99, X 0)
med_obj = bpy.data.objects.get("Medaglione_Cintura")
if med_obj:
    med_obj.data.materials.clear()
    med_obj.data.materials.append(mat_ottone)
    med_obj.data.materials.append(mat_cuoio_scuro)
    bm = bmesh.new()
    rx_m, ry_m, yo_m = torso_profile(0.99)
    y_med = yo_m - (ry_m + 0.014)

    # Round brass disc 0.04 across (radius 0.020), centre at (0.0, y_med, 0.99)
    ret = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=0.020)
    for v in ret["verts"]:
        v.co.y *= 0.25
        v.co += Vector((0.000, y_med, 0.990))
    for f in bm.faces:
        f.smooth = True
        f.material_index = 0

    # Short cord 0.04 long from bottom of main buckle (Z=1.065) to top of medallion (Z=1.008)
    cord_pts = [(0.000, y_med + 0.002, 1.065), (0.000, y_med + 0.001, 1.035), (0.000, y_med, 1.008)]
    add_strap_to_bm(bm, cord_pts, width=0.006, thick=0.005, closed=False)
    for f in bm.faces:
        if f.calc_center_median().z > 1.012:
            f.material_index = 1

    bm.normal_update()
    bm.to_mesh(med_obj.data)
    bm.free()
    med_obj.data.update()

log("=== VERIFICA MISURE GROUP 4 ===")
g_vs = giacca_obj.data.vertices
b_vs = cinture_obj.data.vertices
m_vs = med_obj.data.vertices
log(f"Giacca + Gonnellino Z: {min(v.co.z for v in g_vs):.4f} .. {max(v.co.z for v in g_vs):.4f}m (target 0.80..1.42), larghezza max: {max(v.co.x for v in g_vs)-min(v.co.x for v in g_vs):.4f}m (target 0.38)")
log(f"Cinture Z: {min(v.co.z for v in b_vs):.4f} .. {max(v.co.z for v in b_vs):.4f}m (main belt 1.06..1.12, hip belt 0.94..1.00)")
log(f"Medaglione centro X={(min(v.co.x for v in m_vs)+max(v.co.x for v in m_vs))/2:.4f}, diametro={max(v.co.x for v in m_vs)-min(v.co.x for v in m_vs):.4f}m (target X=0, diam=0.04)")

bpy.ops.wm.save_mainfile()
render_viste("rev_4")
