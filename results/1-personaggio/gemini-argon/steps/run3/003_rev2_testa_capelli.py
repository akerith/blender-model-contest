import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 2 - Head, face and hair (rev_2)
# - Rebuilds ONLY the one piece "Testa" (Rule A3: round-1 decimate collapsed
#   facial topology around nose/mouth/chin).
# - Reshapes existing Occhi, Sopracciglia, Labbra, Orecchie, Capelli_Scuri,
#   and Ciocca_Bianca in-place, adding wavy hair clumps to Capelli_Scuri.
# ==============================================================================

scn = bpy.context.scene

# 1. Update Group 2 materials (2.3, 2.4, 2.5)
def set_mat_color(mat_name, rgb, rough=0.65):
    m = bpy.data.materials.get(mat_name)
    if not m:
        m = bpy.data.materials.new(mat_name)
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Disconnect noise image texture on skin/hair if it dulls the specified RGB
        for link in list(m.node_tree.links):
            if link.to_socket == bsdf.inputs["Base Color"]:
                m.node_tree.links.remove(link)
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
    return m

mat_pelle = set_mat_color("Mat_Pelle", (0.85, 0.68, 0.58), rough=0.55)
mat_labbra = set_mat_color("Mat_Labbra", (0.68, 0.44, 0.38), rough=0.50)
mat_occhio = set_mat_color("Mat_OcchioBianco", (0.92, 0.90, 0.88), rough=0.20)
mat_iride = set_mat_color("Mat_Iride", (0.18, 0.11, 0.07), rough=0.15)
mat_pupilla = set_mat_color("Mat_Pupilla", (0.04, 0.03, 0.03), rough=0.10)
mat_capelli = set_mat_color("Mat_CapelliScuri", (0.10, 0.08, 0.07), rough=0.65)
mat_bianco = set_mat_color("Mat_CapelliBianchi", (0.80, 0.80, 0.78), rough=0.60)

# 2. Delete and rebuild the ONE piece allowed by Rule A3: "Testa"
old_testa = bpy.data.objects.get("Testa")
if old_testa:
    old_m = old_testa.data
    bpy.data.objects.remove(old_testa, do_unlink=True)
    bpy.data.meshes.remove(old_m)

bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=36, radius=1.0)

for v in bm.verts:
    # uvsphere: x, y, z in [-1, 1]
    ux, uy, uz = v.co.x, v.co.y, v.co.z

    # Base egg shape: 0.15 wide (rx=0.075), 0.19 deep (ry=0.095), Z from 1.475 (chin) to 1.660 (top of skull)
    # Map uz in [-1, 1] -> Z in [1.475, 1.660]
    tz = 0.5 * (uz + 1.0)  # 0 at chin (1.475), 1 at crown (1.660)
    z = 1.475 + tz * (1.660 - 1.475)

    # Egg taper in lower half (narrower at chin, jaw going from chin Z=1.475 up to below ears Z=1.545)
    if tz < 0.52:
        t_low = (0.52 - tz) / 0.52  # 0 at mid-head, 1 at chin
        rx = 0.075 * (1.0 - 0.42 * (t_low ** 1.25))
        if uy < 0.0:  # front jaw/chin
            ry = 0.088 * (1.0 - 0.18 * (t_low ** 1.5))
        else:         # back of skull/nape
            ry = 0.095 * (1.0 - 0.35 * (t_low ** 1.3))
    else:
        t_high = (tz - 0.52) / 0.48
        rx = 0.075 * (1.0 - 0.04 * (t_high ** 2))
        ry = 0.095 * (1.0 - 0.04 * (t_high ** 2))

    px = ux * rx
    py = uy * ry

    # Facial features on the -Y side (front of head)
    if uy < -0.15:
        front = min(1.0, (-uy - 0.15) / 0.85)
        # Slight planar flattening of front face
        py *= (1.0 - 0.08 * front)

        # Eye sockets at Z = 1.585, X = +-0.0325 (0.065 apart), each 0.03 wide (2.2)
        for sx_e in (-1.0, 1.0):
            dx_e = (px - sx_e * 0.0325) / 0.017
            dz_e = (z - 1.585) / 0.012
            d2_e = dx_e * dx_e + dz_e * dz_e
            if d2_e < 2.5:
                py += 0.0075 * math.exp(-d2_e) * front

        # Brow ridge just above eyes (Z = 1.598)
        dz_b = (z - 1.598) / 0.009
        if abs(dz_b) < 2.2 and abs(px) < 0.055:
            py -= 0.0035 * math.exp(-dz_b * dz_b) * front

        # Cheekbones at Z = 1.555, X = +-0.046
        for sx_c in (-1.0, 1.0):
            d2_c = ((px - sx_c * 0.046) / 0.022) ** 2 + ((z - 1.555) / 0.020) ** 2
            if d2_c < 2.5:
                px += sx_c * 0.0035 * math.exp(-d2_c) * front
                py -= 0.0035 * math.exp(-d2_c) * front

        # Nose: small wedge from Z = 1.58 down to Z = 1.53, sticking out 0.02 from the face (2.2)
        if 1.522 <= z <= 1.588:
            # Wedge width: narrower at bridge (Z=1.58), slightly wider at base (Z=1.535)
            w_nose = 0.007 + 0.006 * max(0.0, (1.580 - z) / 0.050)
            nx_fac = max(0.0, 1.0 - (abs(px) / (w_nose * 1.6)) ** 1.6)
            if nx_fac > 0.0:
                if z >= 1.536:
                    # Ramp out from 0 at Z=1.585 to 0.020 at nose tip Z=1.536
                    nz_fac = max(0.0, min(1.0, (1.584 - z) / (1.584 - 1.536))) ** 0.9
                else:
                    # Underside of nose wedge returning to upper lip at Z=1.524
                    nz_fac = max(0.0, (z - 1.524) / (1.536 - 1.524))
                py -= 0.020 * nx_fac * nz_fac * front

        # Subtle mouth groove at Z = 1.505, width 0.045 (2.2)
        if abs(px) < 0.026 and 1.494 < z < 1.516:
            mx_fac = math.cos((px / 0.026) * math.pi * 0.5) ** 2
            lip_bump = math.exp(-((z - 1.509) / 0.004) ** 2) + 0.9 * math.exp(-((z - 1.501) / 0.004) ** 2)
            lip_line = math.exp(-((z - 1.505) / 0.0018) ** 2)
            py -= (0.0035 * lip_bump - 0.0025 * lip_line) * mx_fac * front

        # Small rounded chin at Z = 1.475..1.488 (2.2)
        d2_chin = (px / 0.020) ** 2 + ((z - 1.482) / 0.012) ** 2
        if d2_chin < 2.5:
            py -= 0.0055 * math.exp(-d2_chin) * front

    v.co = Vector((px, py, z))

# Normalize exact bounding box of Testa: X in [-0.075, +0.075], Y in [-0.095, +0.095], Z in [1.475, 1.660]
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

uv_lay = bm.loops.layers.uv.new("UVMap")
for f in bm.faces:
    f.smooth = True
    for l in f.loops:
        co = l.vert.co
        l[uv_lay].uv = (0.5 + math.atan2(co.x, -co.y) / (2 * math.pi), (co.z - 1.475) / 0.22)

m_head = bpy.data.meshes.new("Testa")
bm.normal_update()
bm.to_mesh(m_head)
bm.free()
m_head.materials.append(mat_pelle)
o_head = bpy.data.objects.new("Testa", m_head)
scn.collection.objects.link(o_head)

# Helper to find approximate face surface Y on Testa at (x, z)
def face_surface_y(x_q, z_q):
    best_y = -0.078
    best_d = 999.0
    for v in o_head.data.vertices:
        if v.co.y < 0.0:
            d = (v.co.x - x_q) ** 2 + (v.co.z - z_q) ** 2
            if d < best_d:
                best_d = d
                best_y = v.co.y
    return best_y

# 3. Reshape existing Occhi in-place (2.2: Z 1.585, 0.065 apart -> X = +-0.0325, each eye 0.03 wide -> rx=0.015)
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    bm = bmesh.new()
    bm.from_mesh(occhi_obj.data)
    bm.faces.ensure_lookup_table()
    mats = list(occhi_obj.data.materials)

    # Separate into connected components per side & material
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
        c_old = Vector((
            sum(v.co.x for v in c_verts) / len(c_verts),
            sum(v.co.y for v in c_verts) / len(c_verts),
            sum(v.co.z for v in c_verts) / len(c_verts),
        ))
        x_span = max(1e-5, max(v.co.x for v in c_verts) - min(v.co.x for v in c_verts))
        y_span = max(1e-5, max(v.co.y for v in c_verts) - min(v.co.y for v in c_verts))
        z_span = max(1e-5, max(v.co.z for v in c_verts) - min(v.co.z for v in c_verts))

        ey_surf = face_surface_y(sx * 0.0325, 1.585)
        if mname == "Mat_OcchioBianco":
            target_c = Vector((sx * 0.0325, ey_surf + 0.0020, 1.585))
            target_s = (0.030, 0.012, 0.013)
        elif mname == "Mat_Iride":
            target_c = Vector((sx * 0.0325, ey_surf - 0.0022, 1.585))
            target_s = (0.013, 0.005, 0.012)
        else:
            # Pupil or upper lash line
            if z_span < 0.006 and x_span > 0.015:
                target_c = Vector((sx * 0.0325, ey_surf - 0.0030, 1.590))
                target_s = (0.031, 0.006, 0.004)
            else:
                target_c = Vector((sx * 0.0325, ey_surf - 0.0035, 1.585))
                target_s = (0.0065, 0.004, 0.0065)

        for v in c_verts:
            v.co.x = target_c.x + ((v.co.x - c_old.x) / x_span) * target_s[0]
            v.co.y = target_c.y + ((v.co.y - c_old.y) / y_span) * target_s[1]
            v.co.z = target_c.z + ((v.co.z - c_old.z) / z_span) * target_s[2]

    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()

# 4. Reshape existing Sopracciglia in-place (2.2: dark straight eyebrows 0.012 above eyes -> Z=1.597, angled down towards nose)
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        if not vs:
            continue
        xmin = min(abs(v.co.x) for v in vs)
        xmax = max(abs(v.co.x) for v in vs)
        z_avg = sum(v.co.z for v in vs) / len(vs)
        y_avg = sum(v.co.y for v in vs) / len(vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)  # 0 at inner (nose), 1 at outer
            x_new = sx * (0.014 + t * (0.050 - 0.014))
            # Straight line angled down towards the nose, average Z = 1.597 (0.012 above 1.585)
            z_line = 1.593 + t * 0.008
            y_surf = face_surface_y(x_new, z_line)
            v.co.x = x_new
            v.co.z = z_line + (v.co.z - z_avg) * 0.85
            v.co.y = y_surf - 0.002 + (v.co.y - y_avg) * 0.6
    brows_obj.data.update()

# 5. Reshape existing Labbra in-place (2.2: closed straight line at Z 1.505, 0.045 wide, lips not smiling)
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
        z_new = 1.505 + tz * 0.0055 * (1.0 - 0.6 * (abs(tx) * 2.0) ** 2)
        y_surf = face_surface_y(x_new, 1.505)
        v.co.x = x_new
        v.co.y = y_surf - 0.001 + ty * 0.004
        v.co.z = z_new
    labbra_obj.data.update()

# 6. Reshape existing Orecchie in-place (2.2: Z 1.55 to 1.59, on both sides at X = +-0.075)
orecchie_obj = bpy.data.objects.get("Orecchie")
if orecchie_obj:
    for sx in (1.0, -1.0):
        vs = [v for v in orecchie_obj.data.vertices if (v.co.x * sx) > 0]
        if not vs:
            continue
        xmin, xmax = min(v.co.x for v in vs), max(v.co.x for v in vs)
        ymin, ymax = min(v.co.y for v in vs), max(v.co.y for v in vs)
        zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
        for v in vs:
            tx = (v.co.x - xmin) / max(1e-5, xmax - xmin)
            ty = (v.co.y - ymin) / max(1e-5, ymax - ymin)
            tz = (v.co.z - zmin) / max(1e-5, zmax - zmin)
            v.co.x = sx * (0.068 + tx * 0.014)
            v.co.y = -0.012 + ty * 0.024
            v.co.z = 1.550 + tz * (1.590 - 1.550)
    orecchie_obj.data.update()

# 7. Reshape existing Capelli_Scuri and add wavy pointed clumps (2.4: at least 25 clumps,
#    total 0.19 wide at top, Z_max=1.70, forehead locks down to just above eyebrows Z~1.605,
#    sides cover ears and end at Z=1.50, back ends at nape Z=1.48 with uneven points)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    bm = bmesh.new()
    bm.from_mesh(capelli_obj.data)
    bm.faces.ensure_lookup_table()

    # Reshape existing islands in Capelli_Scuri so they sit closely around the skull without looking like a wide helmet
    visited = set()
    island_idx = 0
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
        if len(c_verts) > 200:
            # This is the inner hair base cap: shrink it slightly so the individual clumps stand out in relief
            for v in c_verts:
                v.co.x *= 0.88
                v.co.y *= 0.90
                if v.co.z < 1.52:
                    v.co.z = 1.52
                if v.co.y < -0.075 and v.co.z < 1.615:
                    v.co.z = 1.615
        else:
            # Existing clump: make it wavy, pointed outwards at the tip, ending at Z=1.50 on sides and Z=1.48 at back
            cx = sum(v.co.x for v in c_verts) / len(c_verts)
            cy = sum(v.co.y for v in c_verts) / len(c_verts)
            zmin_c = min(v.co.z for v in c_verts)
            zmax_c = max(v.co.z for v in c_verts)
            is_back = cy > 0.03 and abs(cx) < 0.065
            target_z_bot = (1.475 + 0.012 * (island_idx % 3)) if is_back else (1.495 + 0.015 * (island_idx % 3))
            target_z_top = 1.685 + 0.015 * ((island_idx % 4) / 3.0)
            for v in c_verts:
                tz = (v.co.z - zmin_c) / max(1e-5, zmax_c - zmin_c)  # 0 at tip, 1 at crown
                v.co.z = target_z_bot + tz * (target_z_top - target_z_bot)
                # Wavy outward flick at the bottom tip
                wave = 0.008 * math.sin(tz * math.pi * 2.5 + island_idx * 1.1)
                flick = 0.014 * ((1.0 - tz) ** 1.6) * (1.0 if island_idx % 2 == 0 else 0.5)
                rad_xy = math.hypot(v.co.x, v.co.y)
                if rad_xy > 1e-4:
                    scale_r = (rad_xy + wave + flick) / rad_xy
                    v.co.x *= scale_r
                    v.co.y *= scale_r
            island_idx += 1

    # Add extra pointed clumps on top, forehead (down to Z=1.605 above eyebrows), sides (Z=1.50) and back nape (Z=1.48)
    def add_hair_clump_to_bm(bm_target, pts, rads_xy):
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
                ring.append(bm_target.verts.new(c + b1 * (rx * math.cos(th)) + b2 * (ry * math.sin(th))))
            rings.append(ring)
        for i in range(n - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_target.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True
        # Pointed ends
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm_target.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_target.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True

    # Forehead locks falling down to just above the eyebrows (Z = 1.606..1.612)
    forehead_clumps = [
        [(-0.028, -0.025, 1.688), (-0.042, -0.072, 1.662), (-0.052, -0.094, 1.635), (-0.046, -0.098, 1.608)],
        [(-0.032, -0.030, 1.685), (-0.062, -0.074, 1.655), (-0.078, -0.088, 1.620), (-0.088, -0.082, 1.585)],
        [( 0.010, -0.030, 1.692), ( 0.028, -0.078, 1.665), ( 0.038, -0.096, 1.636), ( 0.032, -0.099, 1.608)],
        [( 0.025, -0.020, 1.690), ( 0.056, -0.072, 1.658), ( 0.074, -0.088, 1.622), ( 0.086, -0.080, 1.582)],
        # Messy upper volume clumps standing up 0.04 above skull (Z=1.70) and 0.19 wide at top
        [(-0.020,  0.000, 1.695), (-0.058, -0.015, 1.692), (-0.086, -0.020, 1.660), (-0.095, -0.015, 1.620)],
        [( 0.015,  0.005, 1.698), ( 0.058, -0.010, 1.694), ( 0.086, -0.015, 1.662), ( 0.095, -0.010, 1.622)],
        [(-0.015,  0.025, 1.696), (-0.062,  0.035, 1.685), (-0.090,  0.040, 1.640), (-0.094,  0.045, 1.585)],
        [( 0.015,  0.025, 1.696), ( 0.062,  0.035, 1.685), ( 0.090,  0.040, 1.640), ( 0.094,  0.045, 1.585)],
        # Back nape uneven clumps ending at Z = 1.48
        [(-0.045,  0.075, 1.600), (-0.058,  0.096, 1.540), (-0.065,  0.092, 1.480)],
        [(-0.018,  0.082, 1.595), (-0.022,  0.100, 1.535), (-0.026,  0.096, 1.478)],
        [( 0.018,  0.082, 1.595), ( 0.022,  0.100, 1.535), ( 0.026,  0.096, 1.482)],
        [( 0.045,  0.075, 1.600), ( 0.058,  0.096, 1.540), ( 0.065,  0.092, 1.479)],
    ]
    clump_rads = [(0.010, 0.008), (0.018, 0.013), (0.015, 0.011), (0.003, 0.003)]
    for c_pts in forehead_clumps:
        r_use = clump_rads[:len(c_pts)]
        r_use[-1] = (0.003, 0.003)
        add_hair_clump_to_bm(bm, c_pts, r_use)

    # Normalize Capelli_Scuri top width to 0.19 (X in [-0.095, +0.095]) and max Z to 1.700
    xs_h = [v.co.x for v in bm.verts]
    zs_h = [v.co.z for v in bm.verts]
    hx_min, hx_max = min(xs_h), max(xs_h)
    hz_max = max(zs_h)
    for v in bm.verts:
        v.co.x = -0.095 + ((v.co.x - hx_min) / max(1e-5, hx_max - hx_min)) * 0.190
        if v.co.z > 1.60:
            v.co.z = 1.60 + (v.co.z - 1.60) * ((1.700 - 1.60) / max(1e-5, hz_max - 1.60))

    bm.normal_update()
    bm.to_mesh(capelli_obj.data)
    bm.free()
    capelli_obj.data.update()

# 8. Reshape existing Ciocca_Bianca in-place (2.5: on her RIGHT side of the forehead (-X),
#    starting at the parting at X -0.03 and going back and to the right (-X) over the top
#    of the head, about 0.03 wide, RGB (0.80, 0.80, 0.78), visible in front, side, and back views!)
bianca_obj = bpy.data.objects.get("Ciocca_Bianca")
if bianca_obj:
    bm = bmesh.new()
    bm.from_mesh(bianca_obj.data)
    bm.faces.ensure_lookup_table()
    visited = set()
    lock_islands = []
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
        lock_islands.append(list({v for cf in comp for v in cf.verts}))

    # Reshape the 3 existing white lock islands so together they form the 0.03-wide white streak:
    # - Starts at parting X = -0.03 on the right forehead (-X, Y = -0.096, Z = 1.635..1.675)
    # - Sweeps over the right-top of the head (-X = -0.03..-0.06, Z = 1.69..1.70) and back over the crown
    #   (reaching Y = +0.098 at the back-top of the head so it is clearly visible in the back view too!)
    streak_paths = [
        # Main front-to-back arch starting at parting X=-0.03 on right forehead (-X) and going over the top to the back
        [(-0.018, -0.098, 1.622), (-0.030, -0.092, 1.665), (-0.042, -0.045, 1.698), (-0.045, 0.025, 1.699), (-0.038, 0.088, 1.668), (-0.032, 0.104, 1.615)],
        # Second strand sweeping from parting X=-0.03 to her right temple (-X)
        [(-0.030, -0.075, 1.678), (-0.052, -0.092, 1.652), (-0.072, -0.082, 1.612), (-0.084, -0.060, 1.568)],
        # Third strand along the top-back crown so the white streak is ~0.03 wide and visible on top in front & back views
        [(-0.025, -0.085, 1.675), (-0.022, -0.030, 1.700), ( 0.012,  0.035, 1.698), ( 0.024, 0.096, 1.660), ( 0.026, 0.105, 1.605)],
    ]

    for idx, c_verts in enumerate(lock_islands):
        path = [Vector(p) for p in streak_paths[idx % len(streak_paths)]]
        # Parameterize existing vertices along their major axis
        pts_old = [v.co.copy() for v in c_verts]
        p_start = min(pts_old, key=lambda p: p.y - p.z * 0.5)
        p_end = max(pts_old, key=lambda p: p.y - p.z * 0.5)
        axis_old = p_end - p_start
        alen = max(1e-5, axis_old.length)
        adir = axis_old / alen

        for v in c_verts:
            t = max(0.0, min(1.0, (v.co - p_start).dot(adir) / alen))
            # Interpolate along path
            seg_f = t * (len(path) - 1)
            si = min(len(path) - 2, int(seg_f))
            st = seg_f - si
            c_new = path[si].lerp(path[si + 1], st)
            t_dir = (path[si + 1] - path[si]).normalized()
            # Keep local cross-section offset (~0.015 radius -> 0.03 total width)
            c_old = p_start + adir * (t * alen)
            off = v.co - c_old
            taper = 0.35 + 0.65 * math.sin(t * math.pi)
            v.co = c_new + off * (0.85 * taper)

    bm.normal_update()
    bm.to_mesh(bianca_obj.data)
    bm.free()
    bianca_obj.data.update()

# Verify Group 2 measurements
t_vs = bpy.data.objects["Testa"].data.vertices
h_vs = bpy.data.objects["Capelli_Scuri"].data.vertices
e_vs = bpy.data.objects["Occhi"].data.vertices
l_vs = bpy.data.objects["Labbra"].data.vertices
log(f"=== VERIFICA MISURE GROUP 2 ===")
log(f"Testa Z: {min(v.co.z for v in t_vs):.4f} .. {max(v.co.z for v in t_vs):.4f} (target 1.475..1.660)")
log(f"Testa X width: {max(v.co.x for v in t_vs)-min(v.co.x for v in t_vs):.4f} (target 0.150), Y depth: {max(v.co.y for v in t_vs)-min(v.co.y for v in t_vs):.4f} (target 0.190)")
log(f"Occhi Z medio: {sum(v.co.z for v in e_vs)/len(e_vs):.4f} (target 1.585)")
log(f"Bocca Z medio: {sum(v.co.z for v in l_vs)/len(l_vs):.4f} (target 1.505), larghezza: {max(v.co.x for v in l_vs)-min(v.co.x for v in l_vs):.4f} (target 0.045)")
log(f"Capelli Z_max: {max(v.co.z for v in h_vs):.4f} (target 1.700), larghezza X: {max(v.co.x for v in h_vs)-min(v.co.x for v in h_vs):.4f} (target 0.190)")

bpy.ops.wm.save_mainfile()
render_viste("rev_2")
