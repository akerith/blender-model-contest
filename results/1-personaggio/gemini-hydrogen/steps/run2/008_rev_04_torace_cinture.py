import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 4: Torso (jacket with front vertical seams, open-sided tunic skirt),
# cross bandoliers with buckles at Z=1.30, under-bust horizontal strap at Z=1.20,
# main belt (1.06..1.12) with framed brass buckle + pin, slanted lower hip belt, medallion.

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.88, metallic=0.0, spec=0.3):
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

mat_jacket       = set_mat_srgb("TunicaBluGrigia", (0.13, 0.16, 0.22), roughness=0.88, spec=0.22)
mat_jacket_seam  = set_mat_srgb("TunicaCuciture", (0.07, 0.09, 0.13), roughness=0.92, spec=0.15)
mat_shirt_collar = set_mat_srgb("CollettoCamicia", (0.30, 0.33, 0.38), roughness=0.88, spec=0.22)
mat_shirt_sleeve = set_mat_srgb("CamiciaBeige", (0.82, 0.76, 0.64), roughness=0.90, spec=0.20)
mat_leather      = set_mat_srgb("PelleMarrone", (0.36, 0.22, 0.12), roughness=0.65, spec=0.35)
mat_leather_dark = set_mat_srgb("PelleScura", (0.24, 0.14, 0.08), roughness=0.66, spec=0.35)
mat_brass        = set_mat_srgb("Ottone", (0.62, 0.45, 0.20), roughness=0.35, metallic=1.0, spec=0.5)
mat_pants        = set_mat_srgb("PantaloniScuri", (0.22, 0.19, 0.16), roughness=0.88, spec=0.20)

# Helper: exact torso radius profile (matches Group 1 & 4.1)
# Z: 1.42 (collar), 1.40 (shoulders), 1.27 (chest 0.32x0.21), 1.08 (waist 0.27x0.18), 0.90 (hips 0.34x0.22)
def torso_profile(z):
    # Returns (cy, rx, ry)
    pts = [
        (0.80,  0.008, 0.185, 0.120),
        (0.90,  0.010, 0.172, 0.112), # hips ~0.344 x 0.224
        (0.98,  0.006, 0.158, 0.104),
        (1.06,  0.000, 0.138, 0.092),
        (1.08,  0.000, 0.135, 0.090), # waist 0.27 x 0.18
        (1.18, -0.006, 0.148, 0.098),
        (1.27, -0.012, 0.160, 0.105), # chest 0.32 x 0.21
        (1.35, -0.005, 0.158, 0.095),
        (1.40,  0.000, 0.140, 0.082),
        (1.425, 0.000, 0.072, 0.068), # jacket collar rim
    ]
    if z <= pts[0][0]:
        return pts[0][1], pts[0][2], pts[0][3]
    if z >= pts[-1][0]:
        return pts[-1][1], pts[-1][2], pts[-1][3]
    for i in range(len(pts) - 1):
        z0, cy0, rx0, ry0 = pts[i]
        z1, cy1, rx1, ry1 = pts[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return (cy0 + t * (cy1 - cy0), rx0 + t * (rx1 - rx0), ry0 + t * (ry1 - ry0))
    return 0.0, 0.14, 0.09

def jacket_surface_pt(ang_from_front, z, extra_offset=0.0):
    # ang=0 is -Y (front), +pi/2 is +X (her left), pi is +Y (back)
    cy, rx, ry = torso_profile(z)
    rx += extra_offset
    ry += extra_offset
    x = rx * math.sin(ang_from_front)
    y = cy - ry * math.cos(ang_from_front)
    return Vector((x, y, z))

# 0. Ensure CorpoBase hip/pelvis core sits cleanly inside trousers/jacket (no poke-through at side slits)
ob_body = bpy.data.objects.get("CorpoBase")
if ob_body:
    for v in ob_body.data.vertices:
        if 0.85 <= v.co.z <= 1.41 and abs(v.co.x) < 0.165:
            # Keep body core 8 mm inside jacket/pants outer dimensions
            cy, rx, ry = torso_profile(v.co.z)
            r_cur = ((v.co.x / max(rx, 1e-4)) ** 2 + ((v.co.y - cy) / max(ry, 1e-4)) ** 2) ** 0.5
            if r_cur > 0.88:
                scale = 0.88 / r_cur
                v.co.x *= scale
                v.co.y = cy + (v.co.y - cy) * scale
    ob_body.data.update()

# Also extend Pantaloni top pelvis cleanly up to Z=1.06 so side slits of tunic skirt show trousers (not skin!)
ob_p = bpy.data.objects.get("Pantaloni")
if ob_p:
    bm_p = bmesh.new()
    bm_p.from_mesh(ob_p.data)
    # Remove any prior pelvis cap we might add on re-run (z > 0.89 and centered)
    old_pelvis = [v for v in bm_p.verts if v.co.z > 0.91]
    if old_pelvis:
        bmesh.ops.delete(bm_p, geom=old_pelvis, context='VERTS')
    pelvis_rings = []
    for z in (0.85, 0.90, 0.98, 1.06):
        cy, rx, ry = torso_profile(z)
        # Slightly inside jacket/skirt (rx-0.012, ry-0.010) -> ~0.32 wide at hips
        pelvis_rings.append([
            Vector(((rx - 0.008) * math.sin(2*math.pi*i/20), cy - (ry - 0.008) * math.cos(2*math.pi*i/20), z))
            for i in range(20)
        ])
    vr = [[bm_p.verts.new(p) for p in ring] for ring in pelvis_rings]
    for i in range(len(vr) - 1):
        for j in range(20):
            jn = (j + 1) % 20
            f = bm_p.faces.new((vr[i][j], vr[i][jn], vr[i+1][jn], vr[i+1][j]))
            f.material_index = 0
    f_top = bm_p.faces.new(vr[-1])
    f_top.material_index = 0
    f_bot = bm_p.faces.new(vr[0][::-1])
    f_bot.material_index = 0
    bmesh.ops.recalc_face_normals(bm_p, faces=bm_p.faces[:])
    bm_p.to_mesh(ob_p.data)
    bm_p.free()
    for p in ob_p.data.polygons:
        p.use_smooth = True
    ob_p.data.update()

# 1. Update TunicaManiche: keep shirt collar (Group 3) + existing sleeves (for Group 5),
#    replace jacket torso + build 5 vertical front seam grooves + open-sided tunic skirt (1.06 -> 0.80)
ob_tm = bpy.data.objects.get("TunicaManiche")
bm_t = bmesh.new()
bm_t.from_mesh(ob_tm.data)

# Delete old jacket torso & skirt (keep sleeves at |x|>0.16 & z<1.39, and keep shirt collar at z>1.40 & r<0.08)
del_jacket = []
for v in bm_t.verts:
    r_xy = (v.co.x ** 2 + v.co.y ** 2) ** 0.5
    is_collar = (v.co.z >= 1.402 and r_xy < 0.075)
    is_sleeve = (abs(v.co.x) > 0.175 and v.co.z < 1.38)
    if not is_collar and not is_sleeve:
        del_jacket.append(v)
if del_jacket:
    bmesh.ops.delete(bm_t, geom=del_jacket, context='VERTS')

# Setup material indices on TunicaManiche:
# 0: mat_jacket, 1: mat_shirt_sleeve, 2: mat_shirt_collar, 3: mat_jacket_seam
# First remap any existing collar faces before replacing materials
old_mats = [m.name if m else "" for m in ob_tm.data.materials]
for f in bm_t.faces:
    mname = old_mats[f.material_index] if f.material_index < len(old_mats) else ""
    if mname == "CollettoCamicia":
        f.material_index = 2
    elif mname == "CamiciaBeige":
        f.material_index = 1
    else:
        f.material_index = 0

# Build Jacket body (Z 1.06 to 1.425) with 5 vertical front seam grooves!
# Groove angles on front (-Y, ang=0): at x = -0.09, -0.045, 0.0, +0.045, +0.09 -> approx ang = -0.60, -0.29, 0.0, +0.29, +0.60
# Use dense angular grid on front so each groove has 2 walls + bottom channel
ang_samples = []
# Front has dense points around 5 vertical seam grooves; back has uniform points
seam_angs = [-0.62, -0.30, 0.0, 0.30, 0.62]
n_u = 64
for i in range(n_u):
    a = -math.pi + 2.0 * math.pi * (i / n_u)
    ang_samples.append(a)

z_levels = [1.06, 1.09, 1.13, 1.18, 1.23, 1.27, 1.32, 1.37, 1.405, 1.425]
jacket_grid = []
for z in z_levels:
    cy, rx, ry = torso_profile(z)
    row = []
    for a in ang_samples:
        # Check proximity to any of the 5 vertical front seams
        groove = 0.0
        for sa in seam_angs:
            d = abs(a - sa)
            if d < 0.06 and z < 1.415:
                groove = max(groove, math.exp(-0.5 * (d / 0.025) ** 2))
        r_off = -0.0035 * groove
        # Slight tailored bust/waist contour
        x = (rx + r_off) * math.sin(a)
        y = cy - (ry + r_off) * math.cos(a)
        row.append((bm_t.verts.new(Vector((x, y, z))), groove))
    jacket_grid.append(row)

jacket_faces = []
for iv in range(len(z_levels) - 1):
    for iu in range(n_u):
        iun = (iu + 1) % n_u
        v00, g00 = jacket_grid[iv][iu]
        v10, g10 = jacket_grid[iv][iun]
        v11, g11 = jacket_grid[iv + 1][iun]
        v01, g01 = jacket_grid[iv + 1][iu]
        f = bm_t.faces.new((v00, v10, v11, v01))
        avg_g = 0.25 * (g00 + g10 + g11 + g01)
        f.material_index = 3 if avg_g > 0.38 else 0
        jacket_faces.append(f)

# Cap jacket top into neck/collar cleanly (bridge top ring inward to collar base)
top_ring = [pair[0] for pair in jacket_grid[-1]]
inner_top = [bm_t.verts.new(Vector((v.co.x * 0.72, v.co.y * 0.72, 1.422))) for v in top_ring]
for iu in range(n_u):
    iun = (iu + 1) % n_u
    f = bm_t.faces.new((top_ring[iu], top_ring[iun], inner_top[iun], inner_top[iu]))
    f.material_index = 0

# Build Tunic Skirt (Z 1.06 down to Z 0.80 at front and back, OPEN ON SIDES, ~0.38 wide, uneven bottom hem!)
def build_skirt_panel(bm_target, is_front=True):
    # Front panel covers ang in [-70 deg, +70 deg] around -Y; Back panel covers [+110 deg, +250 deg] around +Y
    nu_s = 18
    nv_s = 7
    a_start = math.radians(-72) if is_front else math.radians(108)
    a_end   = math.radians(72)  if is_front else math.radians(252)
    s_grid = []
    for iv in range(nv_s + 1):
        tv = iv / nv_s  # 0 = top (Z 1.065), 1 = bottom hem (Z ~0.80..0.84 uneven)
        row = []
        for iu in range(nu_s + 1):
            tu = iu / nu_s
            ang = a_start + tu * (a_end - a_start)
            # Uneven hem: slightly shorter at corners, wavy asymmetric cut ~0.80..0.84
            edge_rise = 0.025 * ((2 * tu - 1) ** 4)
            wave = 0.014 * math.sin(tu * 9.5 + (0.0 if is_front else 1.7)) + 0.008 * math.cos(tu * 15.0)
            z_bot = 0.805 + edge_rise + wave
            z = 1.068 * (1.0 - tv) + z_bot * tv
            # Width: at waist 0.27 -> flares cleanly to 0.38 wide (rx = 0.19) at Z=0.80!
            cy = 0.002 + 0.006 * tv
            rx = 0.140 + 0.056 * (tv ** 0.85)  # hits ~0.196 -> 0.38-0.39 wide across hips!
            ry = 0.095 + 0.032 * (tv ** 0.85)
            # Subtle vertical pleat folds in tunic skirt
            pleat = 0.004 * math.sin(tu * math.pi * 4.0) * tv
            x = (rx + pleat) * math.sin(ang)
            y = cy - (ry + pleat) * math.cos(ang)
            row.append(bm_target.verts.new(Vector((x, y, z))))
        s_grid.append(row)
    s_faces = []
    for iv in range(nv_s):
        for iu in range(nu_s):
            f = bm_target.faces.new((s_grid[iv][iu], s_grid[iv][iu + 1], s_grid[iv + 1][iu + 1], s_grid[iv + 1][iu]))
            f.material_index = 0
            s_faces.append(f)
    bmesh.ops.solidify(bm_target, geom=s_faces, thickness=0.005)

build_skirt_panel(bm_t, is_front=True)
build_skirt_panel(bm_t, is_front=False)

bmesh.ops.recalc_face_normals(bm_t, faces=bm_t.faces[:])
ob_tm.data.materials.clear()
for m in (mat_jacket, mat_shirt_sleeve, mat_shirt_collar, mat_jacket_seam):
    ob_tm.data.materials.append(m)
bm_t.to_mesh(ob_tm.data)
bm_t.free()
for p in ob_tm.data.polygons:
    p.use_smooth = True
ob_tm.data.update()

# 2. Rebuild CinturaCinghie:
#    - 4.3 Two cross straps (0.035 wide x 0.008 thick) over chest & shoulders to back helmet harness + 2 brass buckles at Z=1.30
#    - 4.4 Horizontal brown strap around chest under breasts (Z=1.20, 0.03 wide)
#    - 4.5 Main belt (brown, 0.06 high, Z=1.06..1.12, standing 0.006 out) + rectangular brass buckle (0.07x0.05) with frame & pin
#    - 4.6 Lower hip belt (0.04 high, slanting Z=1.00 on left +X to Z=0.94 on right -X)
#    - 4.7 Medallion (brass disc 0.04 across on cord, centre at Z=0.99, X=0)

bm_c = bmesh.new()

def add_flat_strap_along_pts(bm_target, pts, normals, width=0.035, thick=0.008, mat_idx=0, closed=False):
    # Builds a crisp rectangular-section leather strap lying flush along pts with outward normals
    m = len(pts)
    rings = []
    for i in range(m):
        p = pts[i]
        nrm = normals[i].normalized()
        if closed:
            tang = (pts[(i + 1) % m] - pts[(i - 1) % m]).normalized()
        elif i == 0:
            tang = (pts[1] - pts[0]).normalized()
        elif i == m - 1:
            tang = (pts[-1] - pts[-2]).normalized()
        else:
            tang = (pts[i + 1] - pts[i - 1]).normalized()
        side = tang.cross(nrm).normalized()
        nrm = side.cross(tang).normalized()
        hw = width * 0.5
        # 4-corner beveled strap (6 verts around cross section so edges catch highlights nicely)
        ring = [
            p - side * hw,
            p + side * hw,
            p + side * (hw * 0.94) + nrm * thick,
            p - side * (hw * 0.94) + nrm * thick,
        ]
        rings.append([bm_target.verts.new(v) for v in ring])
    limit = m if closed else m - 1
    for i in range(limit):
        r0 = rings[i]
        r1 = rings[(i + 1) % m]
        for k in range(4):
            kn = (k + 1) % 4
            f = bm_target.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
            f.material_index = mat_idx
    if not closed:
        f0 = bm_target.faces.new(rings[0][::-1])
        f0.material_index = mat_idx
        f1 = bm_target.faces.new(rings[-1])
        f1.material_index = mat_idx

def add_brass_frame_buckle(bm_target, center, normal, up_dir, width, height, frame_w=0.006, depth=0.008, mat_idx=2, add_pin=True):
    # Builds a real hollow rectangular frame buckle + pin oriented to surface normal and up_dir
    nrm = normal.normalized()
    up = (up_dir - nrm * up_dir.dot(nrm)).normalized()
    right = up.cross(nrm).normalized()
    basis = Matrix((right, nrm, up)).transposed().to_4x4()
    mat_w = Matrix.Translation(center) @ basis

    def box(lx, ly, lz, sx, sy, sz):
        res = bmesh.ops.create_cube(
            bm_target, size=1.0,
            matrix=mat_w @ Matrix.Translation((lx, ly, lz)) @ Matrix.Diagonal((sx, sy, sz, 1.0))
        )
        vset = set(res["verts"])
        for v in vset:
            for f in v.link_faces:
                if all(fv in vset for fv in f.verts):
                    f.material_index = mat_idx

    hw = width * 0.5
    hh = height * 0.5
    # Top and bottom bars
    box(0, 0, hh - frame_w * 0.5, width, depth, frame_w)
    box(0, 0, -hh + frame_w * 0.5, width, depth, frame_w)
    # Left and right bars
    box(-hw + frame_w * 0.5, 0, 0, frame_w, depth, height - 2 * frame_w)
    box( hw - frame_w * 0.5, 0, 0, frame_w, depth, height - 2 * frame_w)
    if add_pin:
        # Center cross bar + horizontal tongue pin
        box(0, -depth * 0.1, 0, frame_w * 0.8, depth * 0.7, height - 1.5 * frame_w)
        box(hw * 0.45, depth * 0.35, 0, hw * 0.9, depth * 0.45, frame_w * 0.65)

# A. Cross straps (4.3):
#    Strap 1: LEFT shoulder (+0.13, Z 1.41) -> RIGHT hip (-0.15, Z 1.04) across chest at Z 1.25
#    Strap 2: RIGHT shoulder (-0.13, Z 1.41) -> LEFT hip (+0.15, Z 1.04)
#    AND continue over shoulders down back to meet diving helmet collar ring (Y ~+0.12..+0.15, Z ~1.16)
def build_bandolier(s_top, extra_layer=0.0):
    # Front segment from shoulder (s_top*0.13, Z 1.41) to opposite hip (-s_top*0.15, Z 1.04)
    # Back segment from shoulder down back to helmet harness (s_top*0.11, Z 1.15)
    pts = []
    norms = []
    # Back end up to shoulder top (8 steps)
    for i in range(8):
        t = i / 7.0
        z = 1.15 + t * (1.41 - 1.15)
        x = s_top * (0.11 + t * (0.13 - 0.11))
        cy, rx, ry = torso_profile(z)
        # Back surface (+Y)
        s_x = max(-0.95, min(0.95, x / rx))
        y = cy + ry * math.sqrt(max(0.05, 1.0 - s_x * s_x)) + 0.008 + extra_layer
        # At bottom back, angle slightly out towards helmet at Y=+0.15
        if i < 3:
            y += (3 - i) * 0.012
        pts.append(Vector((x, y, z)))
        norms.append(Vector((x / rx, (y - cy) / ry, 0.25 * t)).normalized())

    # Over shoulder top crest
    pts.append(Vector((s_top * 0.13, 0.00, 1.415 + extra_layer)))
    norms.append(Vector((0.15 * s_top, 0.0, 1.0)).normalized())

    # Front chest diagonal down to opposite hip (14 steps)
    for i in range(1, 15):
        t = i / 14.0
        z = 1.41 * (1.0 - t) + 1.04 * t
        x = (s_top * 0.13) * (1.0 - t) + (-s_top * 0.15) * t
        cy, rx, ry = torso_profile(z)
        # Front surface (-Y)
        s_x = max(-0.98, min(0.98, x / (rx + 0.002)))
        y = cy - (ry + 0.003 + extra_layer) * math.sqrt(max(0.02, 1.0 - s_x * s_x))
        pts.append(Vector((x, y, z)))
        norms.append(Vector((x / rx, (y - cy) / ry, 0.0)).normalized())

    add_flat_strap_along_pts(bm_c, pts, norms, width=0.035, thick=0.008, mat_idx=0, closed=False)

    # Small square brass buckle (0.03 x 0.03) on front strap at Z=1.30
    t_b = (1.41 - 1.30) / (1.41 - 1.04)
    xb = (s_top * 0.13) * (1.0 - t_b) + (-s_top * 0.15) * t_b
    cyb, rxb, ryb = torso_profile(1.30)
    yb = cyb - (ryb + 0.007 + extra_layer) * math.sqrt(max(0.05, 1.0 - (xb / rxb) ** 2))
    nrm_b = Vector((xb / rxb, (yb - cyb) / ryb, 0.0)).normalized()
    tang_b = Vector(((-s_top * 0.15) - (s_top * 0.13), 0.0, 1.04 - 1.41)).normalized()
    add_brass_frame_buckle(bm_c, Vector((xb, yb, 1.30)) + nrm_b * 0.004, nrm_b, tang_b,
                           width=0.030, height=0.030, frame_w=0.005, depth=0.008, mat_idx=2, add_pin=True)

build_bandolier(+1.0, extra_layer=0.000) # Strap 1: Left shoulder (+X) -> Right hip (-X)
build_bandolier(-1.0, extra_layer=0.006) # Strap 2: Right shoulder (-X) -> Left hip (+X)

# B. Horizontal brown strap around chest just under breasts (Z=1.20, 0.03 wide)
def add_closed_belt(bm_target, z_center_fn, height, thick=0.007, r_out=0.003, mat_idx=0, n=36):
    vr_bot = []
    vr_top = []
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        zc = z_center_fn(ang)
        p_mid = jacket_surface_pt(ang, zc, extra_offset=r_out)
        vr_bot.append(Vector((p_mid.x, p_mid.y, zc - height * 0.5)))
        vr_top.append(Vector((p_mid.x, p_mid.y, zc + height * 0.5)))
    v_b = [bm_target.verts.new(p) for p in vr_bot]
    v_t = [bm_target.verts.new(p) for p in vr_top]
    faces = []
    for i in range(n):
        inext = (i + 1) % n
        f = bm_target.faces.new((v_b[i], v_b[inext], v_t[inext], v_t[i]))
        f.material_index = mat_idx
        faces.append(f)
    bmesh.ops.solidify(bm_target, geom=faces, thickness=thick)

# 4.4 Horizontal under-bust chest strap at Z=1.20, 0.03 wide
add_closed_belt(bm_c, lambda a: 1.200, height=0.030, thick=0.007, r_out=0.001, mat_idx=0, n=36)

# 4.5 Main waist belt: brown leather, 0.06 high (Z 1.06..1.12), 0.006 thick, standing 0.006 out
add_closed_belt(bm_c, lambda a: 1.090, height=0.060, thick=0.006, r_out=0.006, mat_idx=0, n=40)

# Main rectangular brass buckle (0.07 wide x 0.05 high) with frame and pin at front center (X=0, Z=1.09)
p_mb = jacket_surface_pt(0.0, 1.090, extra_offset=0.012)
add_brass_frame_buckle(bm_c, p_mb, Vector((0, -1, 0)), Vector((0, 0, 1)),
                       width=0.070, height=0.050, frame_w=0.008, depth=0.010, mat_idx=2, add_pin=True)

# 4.6 Lower hip belt: 0.04 high, slanting higher on LEFT (Z 1.00 at X +0.17) and lower on RIGHT (Z 0.94 at X -0.17)
def slant_z(ang):
    # sin(ang) = +1 at +X (her left), -1 at -X (her right)
    return 0.970 + 0.030 * math.sin(ang)

add_closed_belt(bm_c, slant_z, height=0.040, thick=0.007, r_out=0.008, mat_idx=1, n=40)

# 4.7 Medallion: round brass disc 0.04 across, hanging on short cord 0.04 below main buckle, centre Z=0.99, X=0
p_med = jacket_surface_pt(0.0, 0.990, extra_offset=0.014)
# Cord from main buckle bottom (Z 1.065) down to medallion top (Z 1.01)
cord_pts = [
    jacket_surface_pt(0.0, 1.068, extra_offset=0.012),
    jacket_surface_pt(0.0, 1.038, extra_offset=0.012),
    jacket_surface_pt(0.0, 1.008, extra_offset=0.013),
]
add_flat_strap_along_pts(bm_c, cord_pts, [Vector((0, -1, 0))]*3, width=0.007, thick=0.004, mat_idx=1, closed=False)

# Brass medallion disc (0.04 diameter -> radius 0.020) + outer rim ring
res_m = bmesh.ops.create_cone(
    bm_c, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.020, radius2=0.020, depth=0.006,
    matrix=Matrix.Translation(p_med) @ Matrix.Rotation(math.radians(90), 4, 'X')
)
for v in res_m["verts"]:
    for f in v.link_faces:
        f.material_index = 2
# Inner raised boss detail on medallion
res_m2 = bmesh.ops.create_cone(
    bm_c, cap_ends=True, cap_tris=False, segments=16,
    radius1=0.012, radius2=0.010, depth=0.003,
    matrix=Matrix.Translation(p_med + Vector((0, -0.003, 0))) @ Matrix.Rotation(math.radians(90), 4, 'X')
)
for v in res_m2["verts"]:
    for f in v.link_faces:
        f.material_index = 2

bmesh.ops.recalc_face_normals(bm_c, faces=bm_c.faces[:])
ob_c = bpy.data.objects.get("CinturaCinghie")
ob_c.data.materials.clear()
for m in (mat_leather, mat_leather_dark, mat_brass):
    ob_c.data.materials.append(m)
bm_c.to_mesh(ob_c.data)
bm_c.free()
for p in ob_c.data.polygons:
    p.use_smooth = False
ob_c.data.update()

log("Group 4 complete: Jacket seams, open-sided tunic skirt, cross bandoliers, chest strap, belts, medallion.")
bpy.ops.wm.save_mainfile()
render_viste("rev_4")
