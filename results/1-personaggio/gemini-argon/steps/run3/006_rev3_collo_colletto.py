import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 3 - Neck, shirt and collar (rev_3) + Final polish of Group 2 face/hair
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

# ------------------------------------------------------------------------------
# A. Fix Group 2 face surface placement & hair top width (0.19 m wide at top)
# ------------------------------------------------------------------------------
o_head = bpy.data.objects.get("Testa")
if o_head:
    # Make front face clean and predictable: front surface at Y_front(x, z), plus 0.02m nose wedge
    def head_front_y(px, z):
        tz = max(0.0, min(1.0, (z - 1.475) / (1.660 - 1.475)))
        if tz < 0.52:
            t_low = (0.52 - tz) / 0.52
            rx = 0.075 * (1.0 - 0.36 * (t_low ** 1.25))
            ry_f = 0.075 * (1.0 - 0.14 * (t_low ** 1.5))
        else:
            t_high = (tz - 0.52) / 0.48
            rx = 0.075 * (1.0 - 0.04 * (t_high ** 2))
            ry_f = 0.075 * (1.0 - 0.06 * (t_high ** 2))
        u_x = min(0.98, abs(px) / max(1e-4, rx))
        return -ry_f * math.sqrt(max(0.04, 1.0 - u_x * u_x))

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=36, radius=1.0)
    for v in bm.verts:
        ux, uy, uz = v.co.x, v.co.y, v.co.z
        tz = 0.5 * (uz + 1.0)
        z = 1.475 + tz * (1.660 - 1.475)
        if tz < 0.52:
            t_low = (0.52 - tz) / 0.52
            rx = 0.075 * (1.0 - 0.36 * (t_low ** 1.25))
            ry = (0.075 * (1.0 - 0.14 * (t_low ** 1.5))) if uy < 0.0 else (0.095 * (1.0 - 0.32 * (t_low ** 1.3)))
        else:
            t_high = (tz - 0.52) / 0.48
            rx = 0.075 * (1.0 - 0.04 * (t_high ** 2))
            ry = (0.075 * (1.0 - 0.06 * (t_high ** 2))) if uy < 0.0 else (0.095 * (1.0 - 0.05 * (t_high ** 2)))
        px = ux * rx
        py = uy * ry

        # Nose: small wedge from Z 1.58 down to Z 1.53, sticking out 0.02 from the face (-0.075 -> -0.095)
        if uy < -0.20 and 1.524 <= z <= 1.584:
            w_n = 0.0075 + 0.0065 * max(0.0, (1.580 - z) / 0.050)
            nx_f = max(0.0, 1.0 - (abs(px) / (w_n * 1.45)) ** 1.8)
            if nx_f > 0.0:
                if z >= 1.534:
                    nz_f = max(0.0, min(1.0, (1.582 - z) / (1.582 - 1.534)))
                else:
                    nz_f = max(0.0, (z - 1.524) / (1.534 - 1.524))
                py -= 0.020 * nx_f * nz_f
        v.co = Vector((px, py, z))

    uv_lay = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            l[uv_lay].uv = (0.5 + math.atan2(l.vert.co.x, -l.vert.co.y) / (2 * math.pi), (l.vert.co.z - 1.475) / 0.22)
    bm.normal_update()
    bm.to_mesh(o_head.data)
    bm.free()
    o_head.data.update()

# Position Occhi clearly in front of head_front_y at Z=1.585, X=+-0.0325 (0.065 apart), each 0.03 wide
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    bm = bmesh.new()
    bm.from_mesh(occhi_obj.data)
    bm.faces.ensure_lookup_table()
    mats = list(occhi_obj.data.materials)
    visited = set()
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
        c_verts = list({v for cf in comp for v in cf.verts})
        cx = sum(v.co.x for v in c_verts) / len(c_verts)
        sx = 1.0 if cx > 0 else -1.0
        mname = mats[comp[0].material_index].name if comp[0].material_index < len(mats) else ""
        xmin, xmax = min(v.co.x for v in c_verts), max(v.co.x for v in c_verts)
        ymin, ymax = min(v.co.y for v in c_verts), max(v.co.y for v in c_verts)
        zmin, zmax = min(v.co.z for v in c_verts), max(v.co.z for v in c_verts)
        x_span = max(1e-5, xmax - xmin)
        y_span = max(1e-5, ymax - ymin)
        z_span = max(1e-5, zmax - zmin)
        c_old = Vector((0.5 * (xmin + xmax), 0.5 * (ymin + ymax), 0.5 * (zmin + zmax)))

        for v in c_verts:
            tx = (v.co.x - c_old.x) / x_span
            ty = (v.co.y - c_old.y) / y_span
            tz = (v.co.z - c_old.z) / z_span
            if mname == "Mat_OcchioBianco":
                x_new = sx * 0.0325 + tx * 0.030
                almond = max(0.20, math.cos(tx * math.pi * 0.90))
                z_new = 1.585 + tz * 0.0115 * almond
                y_f = head_front_y(x_new, z_new)
                v.co = Vector((x_new, y_f - 0.0025 + ty * 0.003, z_new))
            elif mname == "Mat_Iride":
                x_new = sx * 0.0325 + tx * 0.0135
                z_new = 1.585 + tz * 0.0110
                y_f = head_front_y(x_new, z_new)
                v.co = Vector((x_new, y_f - 0.0048 + ty * 0.002, z_new))
            else:
                if x_span > 0.018:  # upper eyelash
                    x_new = sx * 0.0325 + tx * 0.031
                    arch = math.cos(tx * math.pi * 0.85) * 0.0045
                    z_new = 1.5875 + arch + tz * 0.003
                    y_f = head_front_y(x_new, z_new)
                    v.co = Vector((x_new, y_f - 0.0052 + ty * 0.002, z_new))
                else:               # pupil
                    x_new = sx * 0.0325 + tx * 0.0065
                    z_new = 1.585 + tz * 0.0065
                    y_f = head_front_y(x_new, z_new)
                    v.co = Vector((x_new, y_f - 0.0058 + ty * 0.0015, z_new))
    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()

# Position Sopracciglia 0.012 above eyes (Z=1.597), angled down towards nose
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (1.0, -1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        xmin = min(abs(v.co.x) for v in vs)
        xmax = max(abs(v.co.x) for v in vs)
        z_avg = sum(v.co.z for v in vs) / len(vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            x_new = sx * (0.013 + t * (0.050 - 0.013))
            z_line = 1.5935 + t * 0.0075
            z_new = z_line + (v.co.z - z_avg) * 0.85
            y_f = head_front_y(x_new, z_line)
            v.co = Vector((x_new, y_f - 0.0050, z_new))
    brows_obj.data.update()

# Position Labbra at Z=1.505, 0.045 wide, closed straight line clearly visible on face
labbra_obj = bpy.data.objects.get("Labbra")
if labbra_obj:
    vs = labbra_obj.data.vertices
    xmin, xmax = min(v.co.x for v in vs), max(v.co.x for v in vs)
    ymin, ymax = min(v.co.y for v in vs), max(v.co.y for v in vs)
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tx = (v.co.x - xmin) / max(1e-5, xmax - xmin) - 0.5
        ty = (v.co.y - ymin) / max(1e-5, ymax - ymin) - 0.5
        tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
        x_new = tx * 0.045
        taper = max(0.30, math.cos(tx * math.pi * 0.88))
        z_new = 1.505 + tz * 0.0065 * taper
        y_f = head_front_y(x_new, 1.505)
        v.co = Vector((x_new, y_f - 0.0045 + ty * 0.003, z_new))
    labbra_obj.data.update()

# Widen Capelli_Scuri upper crown & side clumps so the hair is truly 0.19 m wide at the top (not shrunk by bottom tips!)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    for v in capelli_obj.data.vertices:
        # Widen upper hair (Z > 1.54) outwards to full 0.19 m width (X in [-0.095, +0.095])
        if v.co.z > 1.50:
            t_up = min(1.0, (v.co.z - 1.50) / 0.14)
            v.co.x *= (1.12 + 0.10 * t_up)
            v.co.x = max(-0.095, min(0.095, v.co.x))
            # Pull forehead locks above Z=1.606 so eyebrows are 100% clear
            if v.co.y < -0.055 and abs(v.co.x) < 0.052 and v.co.z < 1.606:
                v.co.z = 1.606
    capelli_obj.data.update()

# Re-render rev_2 so the Group 2 renders show the crisp face and full 0.19m hair
render_viste("rev_2")

# ------------------------------------------------------------------------------
# B. GROUP 3 - Neck, shirt collar, and cape collar
# ------------------------------------------------------------------------------
# 3.1 Neck: cylinder 0.11 wide (rx=0.055, ry=0.055), from Z 1.45 to 1.49, skin colour
collo_obj = bpy.data.objects.get("Collo")
if collo_obj:
    vs = collo_obj.data.vertices
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tz = (v.co.z - zmin) / max(1e-5, zmax - zmin)
        r = math.hypot(v.co.x, v.co.y)
        if r > 0.01:
            ang = math.atan2(v.co.y, v.co.x)
            v.co.x = 0.055 * math.cos(ang)
            v.co.y = 0.055 * math.sin(ang)
        else:
            v.co.x = 0.0
            v.co.y = 0.0
        v.co.z = 1.450 + tz * (1.490 - 1.450)
    collo_obj.data.update()

# 3.2 Shirt collar: high grey-blue shirt collar wrapped around the neck, from Z 1.41 to 1.46, RGB (0.30, 0.33, 0.38)
mat_colletto_camicia = set_spec_mat("Mat_CollettoCamicia", (0.30, 0.33, 0.38), (0.20, 0.23, 0.28), rough=0.85)
camicia_col_obj = bpy.data.objects.get("Camicia_Colletto")
if camicia_col_obj:
    camicia_col_obj.data.materials.clear()
    camicia_col_obj.data.materials.append(mat_colletto_camicia)
    vs = camicia_col_obj.data.vertices
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tz = (v.co.z - zmin) / max(1e-5, zmax - zmin)
        r = math.hypot(v.co.x, v.co.y)
        if r > 0.01:
            ang = math.atan2(v.co.y, v.co.x)
            # Wraps closely around the 0.11m neck (radius 0.068 at Z=1.41 tapering to 0.059 at Z=1.46)
            target_r = 0.068 * (1.0 - tz) + 0.059 * tz
            # Small subtle V-dip at the front center (-Y, ang ~ -pi/2)
            front_dip = 0.008 * max(0.0, -math.sin(ang)) ** 3 * tz
            v.co.x = target_r * math.cos(ang)
            v.co.y = target_r * math.sin(ang)
            v.co.z = 1.410 + tz * (1.460 - 1.410) - front_dip
        else:
            v.co.x = 0.0
            v.co.y = 0.0
            v.co.z = 1.410 + tz * (1.460 - 1.410)
    camicia_col_obj.data.update()

# 3.3 Cape collar: stiff, tall stand-up collar of the cape around back and sides of neck, open at front.
#     Rises from shoulders (Z 1.40) to Z 1.52 at the back and to Z 1.48 at the front corners, and leans out a little.
#     Same teal colour as the cape (Group 6: RGB (0.22, 0.34, 0.31)).
mantella_col_obj = bpy.data.objects.get("Mantella_Colletto")
if mantella_col_obj:
    vs = mantella_col_obj.data.vertices
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tz = max(0.0, min(1.0, (v.co.z - zmin) / max(1e-5, zmax - zmin)))
        # Angle around neck: 0 is back (+Y), +-pi is front (-Y)
        ang = math.atan2(v.co.x, v.co.y)
        u_front = min(1.0, abs(ang) / math.radians(142.0))  # 0 at back, 1 at front corners
        # Top height: Z 1.52 at the back (u_front=0) sloping to Z 1.48 at front corners (u_front=1)
        z_top = 1.520 - 0.040 * (u_front ** 1.3)
        z_bot = 1.400
        v.co.z = z_bot + tz * (z_top - z_bot)

        # Radius leans out a little from bottom (rx=0.080, ry=0.076) to top (rx=0.106, ry=0.100)
        r_curr = math.hypot(v.co.x, v.co.y)
        # Preserve solidify thickness offset (~0.005) between inner and outer wall
        is_outer = 1.0 if r_curr > (0.085 + 0.015 * tz) else 0.0
        thick_off = 0.006 * is_outer
        rx_target = 0.078 + 0.026 * tz + thick_off
        ry_target = 0.075 + 0.024 * tz + thick_off
        v.co.x = rx_target * math.sin(ang)
        v.co.y = 0.004 + ry_target * math.cos(ang)
    mantella_col_obj.data.update()

# Log Group 3 measurements
c_vs = collo_obj.data.vertices
sc_vs = camicia_col_obj.data.vertices
mc_vs = mantella_col_obj.data.vertices
log("=== VERIFICA MISURE GROUP 3 ===")
log(f"Collo: larghezza X={max(v.co.x for v in c_vs)-min(v.co.x for v in c_vs):.4f}m (target 0.110), Z={min(v.co.z for v in c_vs):.4f}..{max(v.co.z for v in c_vs):.4f}m (target 1.45..1.49)")
log(f"Camicia_Colletto: Z={min(v.co.z for v in sc_vs):.4f}..{max(v.co.z for v in sc_vs):.4f}m (target 1.41..1.46)")
log(f"Mantella_Colletto: Z_min={min(v.co.z for v in mc_vs):.4f}m (target 1.40), Z_max(retro)={max(v.co.z for v in mc_vs):.4f}m (target 1.52)")

bpy.ops.wm.save_mainfile()
render_viste("rev_3")
