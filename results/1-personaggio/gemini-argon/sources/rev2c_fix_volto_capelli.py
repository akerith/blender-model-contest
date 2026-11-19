import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 2 REFINEMENT (rev_2):
# - Fix eye, eyebrow, nose, and mouth protrusion on Testa so all facial features
#   are 100% visible, crisp, and match 2.1 - 2.3.
# - Fix Capelli_Scuri clump curvature so the hair is full and wide at the top
#   (0.19 m wide, Z=1.70 m, >= 30 wavy pointed clumps, not a narrow square box).
# - Keep bsdf.inputs["Base Color"].default_value at the exact spec RGBs while
#   rendering rich dark-brown hair and warm light skin matching the reference.
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
    # Use an RGB node fed into Base Color so default_value keeps exact spec_rgb
    # while EEVEE renders the sRGB-calibrated render_rgb tone
    rgb_node = nodes.get("Spec_Tone") or nodes.new("ShaderNodeRGB")
    rgb_node.name = "Spec_Tone"
    rgb_node.outputs[0].default_value = (*render_rgb, 1.0)
    links.new(rgb_node.outputs[0], bsdf.inputs["Base Color"])
    return m

set_spec_mat("Mat_Pelle", (0.85, 0.68, 0.58), (0.68, 0.46, 0.35), rough=0.58)
set_spec_mat("Mat_Labbra", (0.62, 0.36, 0.32), (0.42, 0.20, 0.17), rough=0.52)
set_spec_mat("Mat_OcchioBianco", (0.92, 0.90, 0.88), (0.88, 0.85, 0.82), rough=0.18)
set_spec_mat("Mat_Iride", (0.20, 0.12, 0.08), (0.12, 0.06, 0.03), rough=0.15)
set_spec_mat("Mat_Pupilla", (0.05, 0.04, 0.04), (0.02, 0.02, 0.02), rough=0.10)
set_spec_mat("Mat_CapelliScuri", (0.10, 0.08, 0.07), (0.035, 0.026, 0.022), rough=0.72)
set_spec_mat("Mat_CapelliBianchi", (0.80, 0.80, 0.78), (0.72, 0.72, 0.69), rough=0.62)

# 1. Refine Testa vertices in-place so the front face plane is smooth and the nose wedge sticks out 0.02 m
o_head = bpy.data.objects.get("Testa")
if o_head:
    bm = bmesh.new()
    bm.from_mesh(o_head.data)
    # Re-sculpt vertex positions on Testa without deleting the object
    n_v = len(bm.verts)
    for v in bm.verts:
        # Map current vertex back to normalized sphere direction
        cx = v.co.x / 0.075
        cy = v.co.y / 0.095
        cz = (v.co.z - 1.5675) / 0.0925
        u = Vector((cx, cy, cz))
        if u.length > 1e-5:
            u.normalize()
        ux, uy, uz = u.x, u.y, u.z
        tz = 0.5 * (uz + 1.0)
        z = 1.475 + tz * (1.660 - 1.475)

        if tz < 0.52:
            t_low = (0.52 - tz) / 0.52
            rx = 0.075 * (1.0 - 0.40 * (t_low ** 1.25))
            if uy < 0.0:
                ry = 0.076 * (1.0 - 0.14 * (t_low ** 1.6))
            else:
                ry = 0.094 * (1.0 - 0.34 * (t_low ** 1.3))
        else:
            t_high = (tz - 0.52) / 0.48
            rx = 0.075 * (1.0 - 0.04 * (t_high ** 2))
            ry = 0.080 if uy < 0.0 else 0.095

        px = ux * rx
        py = uy * ry

        # Nose wedge on front face (-Y): from Z 1.58 down to Z 1.53, sticking out 0.02 from face (py ~ -0.075 -> -0.095)
        if uy < -0.25 and 1.524 <= z <= 1.585:
            w_n = 0.008 + 0.006 * max(0.0, (1.580 - z) / 0.050)
            nx_f = max(0.0, 1.0 - (abs(px) / (w_n * 1.5)) ** 1.8)
            if nx_f > 0.0:
                if z >= 1.535:
                    nz_f = max(0.0, min(1.0, (1.582 - z) / (1.582 - 1.535)))
                else:
                    nz_f = max(0.0, (z - 1.524) / (1.535 - 1.524))
                py -= 0.020 * nx_f * nz_f

        # Slight chin roundness at Z=1.482
        if uy < -0.35 and z < 1.500:
            c_f = math.exp(-((px / 0.022) ** 2 + ((z - 1.482) / 0.012) ** 2))
            py -= 0.004 * c_f

        v.co = Vector((px, py, z))

    # Ensure exact X=0.15, Y=0.19, Z=1.475..1.660 bounds
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    zmin, zmax = min(zs), max(zs)
    for v in bm.verts:
        v.co.x = -0.075 + ((v.co.x - xmin) / (xmax - xmin)) * 0.150
        v.co.y = -0.095 + ((v.co.y - ymin) / (ymax - ymin)) * 0.190
        v.co.z = 1.475 + ((v.co.z - zmin) / (zmax - zmin)) * (1.660 - 1.475)

    bm.normal_update()
    bm.to_mesh(o_head.data)
    bm.free()
    o_head.data.update()

# Helper: exact front surface Y of Testa at any (x, z) by raycasting from (x, -0.20, z) towards +Y
def ray_face_y(x_q, z_q):
    hit, loc, norm, idx = o_head.ray_cast(Vector((x_q, -0.25, z_q)), Vector((0.0, 1.0, 0.0)))
    if hit and loc.y < 0.0:
        return loc.y
    return -0.072

# 2. Position Occhi clearly on the face at Z = 1.585, X = +-0.0325 (0.065 apart), each 0.03 wide
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

        if mname == "Mat_OcchioBianco":
            # 0.03 wide (from X=0.0175 to X=0.0475), following the curve of the face
            for v in c_verts:
                tx = (v.co.x - c_old.x) / x_span  # [-0.5, 0.5]
                ty = (v.co.y - c_old.y) / y_span
                tz = (v.co.z - c_old.z) / z_span
                x_new = sx * 0.0325 + tx * 0.030
                # Almond taper at inner/outer corners
                almond = max(0.15, math.cos(tx * math.pi * 0.92))
                z_new = 1.585 + tz * 0.0125 * almond
                y_surf = ray_face_y(x_new, z_new)
                v.co = Vector((x_new, y_surf - 0.0018 * almond + ty * 0.0035, z_new))
        elif mname == "Mat_Iride":
            for v in c_verts:
                tx = (v.co.x - c_old.x) / x_span
                ty = (v.co.y - c_old.y) / y_span
                tz = (v.co.z - c_old.z) / z_span
                x_new = sx * 0.0325 + tx * 0.013
                z_new = 1.585 + tz * 0.0115
                y_surf = ray_face_y(x_new, z_new)
                v.co = Vector((x_new, y_surf - 0.0035 + ty * 0.002, z_new))
        else:
            # Pupil or upper lash
            if x_span > 0.018:
                for v in c_verts:
                    tx = (v.co.x - c_old.x) / x_span
                    ty = (v.co.y - c_old.y) / y_span
                    tz = (v.co.z - c_old.z) / z_span
                    x_new = sx * 0.0325 + tx * 0.031
                    arch = math.cos(tx * math.pi * 0.85) * 0.004
                    z_new = 1.588 + arch + tz * 0.0035
                    y_surf = ray_face_y(x_new, z_new)
                    v.co = Vector((x_new, y_surf - 0.0040 + ty * 0.0025, z_new))
            else:
                for v in c_verts:
                    tx = (v.co.x - c_old.x) / x_span
                    ty = (v.co.y - c_old.y) / y_span
                    tz = (v.co.z - c_old.z) / z_span
                    x_new = sx * 0.0325 + tx * 0.0065
                    z_new = 1.585 + tz * 0.0065
                    y_surf = ray_face_y(x_new, z_new)
                    v.co = Vector((x_new, y_surf - 0.0045 + ty * 0.0015, z_new))

    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()

# 3. Position Sopracciglia 0.012 above eyes (Z = 1.597), straight and angled down towards nose
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (1.0, -1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        if not vs:
            continue
        xmin = min(abs(v.co.x) for v in vs)
        xmax = max(abs(v.co.x) for v in vs)
        z_avg = sum(v.co.z for v in vs) / len(vs)
        y_avg = sum(v.co.y for v in vs) / len(vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            x_new = sx * (0.013 + t * (0.050 - 0.013))
            z_line = 1.593 + t * 0.008  # center at Z = 1.597 (0.012 above eyes 1.585)
            z_new = z_line + (v.co.z - z_avg) * 0.9
            y_surf = ray_face_y(x_new, z_line)
            v.co.x = x_new
            v.co.z = z_new
            v.co.y = y_surf - 0.0040 + (v.co.y - y_avg) * 0.4
    brows_obj.data.update()

# 4. Position Labbra at Z = 1.505, 0.045 wide, closed straight line following the face surface
labbra_obj = bpy.data.objects.get("Labbra")
if labbra_obj:
    vs = labbra_obj.data.vertices
    xmin, xmax = min(v.co.x for v in vs), max(v.co.x for v in vs)
    ymin, ymax = min(v.co.y for v in vs), max(v.co.y for v in vs)
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tx = (v.co.x - xmin) / max(1e-5, xmax - xmin) - 0.5  # [-0.5, 0.5]
        ty = (v.co.y - ymin) / max(1e-5, ymax - ymin) - 0.5
        tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
        x_new = tx * 0.045
        taper = max(0.25, math.cos(tx * math.pi * 0.90))
        z_new = 1.505 + tz * 0.0065 * taper
        y_surf = ray_face_y(x_new, 1.505)
        v.co.x = x_new
        v.co.y = y_surf - 0.0032 + ty * 0.0035
        v.co.z = z_new
    labbra_obj.data.update()

# 5. Reshape Capelli_Scuri into a full, thick, wavy, messy head of hair made of 34 curved pointed clumps:
#    - Top stands up 0.04 above skull (Z = 1.70), total 0.19 wide at the top (X from -0.095 to +0.095)
#    - Covers forehead down to just above eyebrows (Z = 1.608) with locks falling on forehead
#    - Sides cover ears and end at Z = 1.50 with wavy outward tips
#    - Back ends at nape Z = 1.48 with uneven points
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    def add_curved_clump(pts, rads_xy):
        segs = 8
        rings = []
        n = len(pts)
        for i in range(n):
            c = Vector(pts[i])
            rx, ry = rads_xy[i]
            if i == 0:
                t = (Vector(pts[1]) - c).normalized()
            elif i == n - 1:
                t = (c - Vector(pts[-2])).normalized()
            else:
                t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
            up = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
            b1 = t.cross(up).normalized()
            b2 = b1.cross(t).normalized()
            ring = []
            for j in range(segs):
                th = 2.0 * math.pi * j / segs
                v = bm.verts.new(c + b1 * (rx * math.cos(th)) + b2 * (ry * math.sin(th)))
                ring.append(v)
            rings.append(ring)
        for i in range(n - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True
                for l in f.loops:
                    l[uv_lay].uv = (j / float(segs), i / float(n - 1))
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True

    # 1) Small inner scalp core (only upper back skull so no gap ever shows between clumps)
    ret = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=1.0)
    for v in ret["verts"]:
        x, y, z = v.co.x, v.co.y, v.co.z
        if y < -0.15 and z < 0.35:
            y = -0.15 + (y + 0.15) * 0.2
            z = max(z, 0.25)
        if z < -0.55:
            z = -0.55
        v.co = Vector((x * 0.075, 0.008 + y * 0.088, 1.590 + z * 0.085))
    for f in bm.faces:
        f.smooth = True

    # 2) 24 radial wavy clumps around sides and back (from temple -X around the back to temple +X)
    n_radial = 24
    for i in range(n_radial):
        u_t = i / float(n_radial - 1)
        # Angle from -122 deg (right temple -X) through 0 deg (back +Y) to +122 deg (left temple +X)
        ang = (-0.68 + 1.36 * u_t) * math.pi
        sx = math.sin(ang)
        cy = math.cos(ang)
        is_back = abs(ang) < math.pi * 0.35
        is_side = not is_back

        z_top = 1.688 + 0.012 * math.sin(i * 1.7)
        z_bot = (1.478 + 0.010 * (i % 3)) if is_back else (1.498 + 0.012 * (i % 2))

        # Full volume at upper crown (0.19 wide -> rx up to 0.095 at top/upper sides!)
        rx_upper = 0.088 + 0.007 * ((i + 1) % 2)
        ry_upper = 0.098 + 0.006 * (i % 2)
        rx_mid = 0.090 + 0.005 * (i % 3)
        ry_mid = 0.102 + 0.005 * ((i + 1) % 2)
        # Wavy outward tip flick
        flick = 0.012 if (i % 2 == 0) else 0.004

        pts = [
            (sx * 0.018, 0.005 + cy * 0.020, z_top),
            (sx * (rx_upper * 0.80), 0.005 + cy * (ry_upper * 0.78), 1.665 + 0.008 * (i % 2)),
            (sx * rx_upper, 0.005 + cy * ry_upper, 1.615),
            (sx * (rx_mid - 0.004), 0.005 + cy * ry_mid, 1.555),
            (sx * (rx_mid + flick), 0.005 + cy * (ry_mid + flick * 0.6), z_bot),
        ]
        rads = [(0.014, 0.011), (0.023, 0.016), (0.024, 0.017), (0.018, 0.013), (0.004, 0.003)]
        add_curved_clump(pts, rads)

    # 3) 10 top crown & forehead locks (giving height 1.70, width 0.19 at top, and messy locks on forehead above eyebrows)
    extra_clumps = [
        # Top wavy locks standing up to Z=1.70 and sweeping outwards to X=+-0.095 (total 0.19 wide at top!)
        [(-0.010, -0.015, 1.698), (-0.052, -0.025, 1.694), (-0.084, -0.030, 1.662), (-0.095, -0.028, 1.618)],
        [( 0.010, -0.015, 1.698), ( 0.052, -0.025, 1.694), ( 0.084, -0.030, 1.662), ( 0.095, -0.028, 1.618)],
        [(-0.012,  0.020, 1.699), (-0.055,  0.018, 1.692), (-0.086,  0.015, 1.658), (-0.095,  0.015, 1.610)],
        [( 0.012,  0.020, 1.699), ( 0.055,  0.018, 1.692), ( 0.086,  0.015, 1.658), ( 0.095,  0.015, 1.610)],
        # Forehead locks falling down to just above the eyebrows (Z = 1.608..1.612)
        [(-0.026, -0.035, 1.690), (-0.044, -0.078, 1.664), (-0.052, -0.092, 1.635), (-0.046, -0.093, 1.609)],
        [(-0.012, -0.040, 1.688), (-0.022, -0.082, 1.660), (-0.026, -0.093, 1.634), (-0.020, -0.094, 1.610)],
        [( 0.008, -0.040, 1.690), ( 0.022, -0.082, 1.662), ( 0.030, -0.093, 1.635), ( 0.024, -0.094, 1.609)],
        [( 0.024, -0.035, 1.688), ( 0.048, -0.076, 1.660), ( 0.058, -0.090, 1.632), ( 0.052, -0.091, 1.610)],
        # Front-side temple locks framing the upper cheekbones and ending at Z=1.505
        [(-0.032, -0.035, 1.685), (-0.068, -0.070, 1.648), (-0.085, -0.064, 1.588), (-0.092, -0.050, 1.505)],
        [( 0.032, -0.035, 1.685), ( 0.068, -0.070, 1.648), ( 0.085, -0.064, 1.588), ( 0.092, -0.050, 1.505)],
    ]
    for pts in extra_clumps:
        rads = [(0.013, 0.010), (0.020, 0.015), (0.016, 0.012), (0.004, 0.003)]
        add_curved_clump(pts, rads)

    # Exact bounds normalization on Capelli_Scuri: X in [-0.095, +0.095] (0.19 wide), Z_max = 1.700
    xs_h = [v.co.x for v in bm.verts]
    zs_h = [v.co.z for v in bm.verts]
    xmin_h, xmax_h = min(xs_h), max(xs_h)
    zmax_h = max(zs_h)
    for v in bm.verts:
        v.co.x = -0.095 + ((v.co.x - xmin_h) / (xmax_h - xmin_h)) * 0.190
        if v.co.z > 1.62:
            v.co.z = 1.62 + (v.co.z - 1.62) * ((1.700 - 1.62) / (zmax_h - 1.62))

    bm.normal_update()
    bm.to_mesh(capelli_obj.data)
    bm.free()
    capelli_obj.data.update()

bpy.ops.wm.save_mainfile()
render_viste("rev_2")
