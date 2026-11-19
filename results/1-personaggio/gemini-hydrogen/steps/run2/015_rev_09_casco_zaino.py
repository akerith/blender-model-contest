import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 9: Diving helmet and back gear
# - 9.1 Helmet on upper back ON TOP of cape: centre (0, +0.25, 1.30), top 1.47, bottom 1.13, 0.32 wide x 0.30 deep
# - 9.2 Brass dome + collar ring (breastplate rim) 0.03 high, 0.30 across
# - 9.3 Main backward porthole (+Y): 0.13 across glass, 0.02 wide brass frame sticking out 0.025,
#       slightly transparent shiny glass (0.55, 0.70, 0.65) + brass cross grille (0.008 wide)
# - 9.4 Two side portholes (-X, +X): 0.07 across with brass frame + glass
# - 9.5 Rivets: 12 around main porthole, 16 around collar ring (0.008 across)
# - 9.6 Two vertical raised brass bands (0.015 wide) left & right of main porthole
# - 9.7 Aged brass (0.62, 0.45, 0.20) + dark brass edges (0.35, 0.24, 0.10)
# - 9.8 Two ribbed corrugated hoses (0.03 across): -X coils into 0.12 flat spiral disc at (-0.12, 0.20, 1.00);
#       +X goes down & forward under arm to belt (+0.17, Z 1.02)
# - 9.9 Bedroll (0.34 long, 0.11 across) at (0, +0.22, 1.06), cream-tan canvas (0.66, 0.58, 0.45), 2 straps at X +-0.10
# - 9.10 2 loops of twisted beige rope (0.12 long) hanging from helmet bottom over bedroll
# - 9.11 Harness connecting chest straps over shoulders to helmet collar ring + horizontal back waist strap holding bedroll

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

mat_brass        = set_mat_srgb("Ottone", (0.62, 0.45, 0.20), roughness=0.35, metallic=1.0, spec=0.50)
mat_brass_dark   = set_mat_srgb("OttoneScuro", (0.35, 0.24, 0.10), roughness=0.42, metallic=1.0, spec=0.45)
mat_glass        = set_mat_srgb("VetroOblo", (0.55, 0.70, 0.65), roughness=0.08, metallic=0.05, spec=0.70, transmission=0.65, alpha=0.72)
mat_glass_back   = set_mat_srgb("InternoCasco", (0.14, 0.16, 0.15), roughness=0.75, metallic=0.40, spec=0.25)
mat_bedroll      = set_mat_srgb("SaccoZaino", (0.66, 0.58, 0.45), roughness=0.90, spec=0.18)
mat_leather      = set_mat_srgb("PelleMarrone", (0.36, 0.22, 0.12), roughness=0.65, spec=0.35)
mat_hose         = set_mat_srgb("TubiGomma", (0.24, 0.20, 0.16), roughness=0.68, spec=0.28)
mat_rope         = set_mat_srgb("CordaCanapa", (0.70, 0.62, 0.47), roughness=0.88, spec=0.18)

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

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

def add_annular_frame(bm, center, rot_mat, r_in, r_out, depth, segs=24, mat_idx=0):
    # Builds a crisp hollow cylindrical ring frame
    rings = []
    pts_prof = [
        (r_in,  -depth * 0.5),
        (r_out, -depth * 0.5),
        (r_out,  depth * 0.5),
        (r_in,   depth * 0.5),
    ]
    mat_w = Matrix.Translation(center) @ rot_mat
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        ca, sa = math.cos(ang), math.sin(ang)
        rings.append([bm.verts.new(mat_w @ Vector((r * ca, r * sa, dz))) for r, dz in pts_prof])
    for i in range(segs):
        r0 = rings[i]
        r1 = rings[(i + 1) % segs]
        for k in range(4):
            kn = (k + 1) % 4
            f = bm.faces.new((r0[k], r1[k], r1[kn], r0[kn]))
            f.material_index = mat_idx

# 1. Rebuild CascoPalombaro (9.1 - 9.7):
#    Centre (0, 0.25, 1.30), top 1.47, bottom 1.13, 0.32 wide (rx=0.16), 0.30 deep (ry=0.15)
#    Materials: 0: mat_brass, 1: mat_brass_dark, 2: mat_glass, 3: mat_glass_back
bm_c = bmesh.new()
h_c = Vector((0.0, 0.25, 1.30))

# A. Smooth brass dome (Z 1.16..1.47) + flared collar ring (Z 1.13..1.16, 0.30 across r=0.15)
#    Dome profile: rounder at top, flattening slightly at bottom onto collar ring
dome_prof = [
    # (z_local, rx, ry, mat_idx) -> z_world = 1.30 + z_local
    (-0.170, 0.145, 0.138, 1), # bottom edge of collar ring Z=1.13
    (-0.170, 0.152, 0.146, 0), # outer collar rim Z=1.13 (0.304 across)
    (-0.145, 0.152, 0.146, 0), # collar ring top bevel
    (-0.140, 0.136, 0.128, 1), # dark neck seam where dome meets collar (Z=1.16)
    (-0.120, 0.142, 0.134, 0), # lower dome flare
    (-0.070, 0.155, 0.146, 0), # lower-mid dome
    ( 0.000, 0.160, 0.150, 0), # equator: 0.32 wide x 0.30 deep!
    ( 0.065, 0.152, 0.142, 0),
    ( 0.115, 0.126, 0.118, 0),
    ( 0.148, 0.088, 0.082, 0),
    ( 0.165, 0.045, 0.042, 0),
    ( 0.170, 0.012, 0.011, 0), # dome apex Z=1.47!
]
n_dome = 32
dome_rings = []
for zl, rx, ry, mid in dome_prof:
    z = h_c.z + zl
    dome_rings.append([Vector((h_c.x + rx * math.cos(2*math.pi*i/n_dome),
                               h_c.y + ry * math.sin(2*math.pi*i/n_dome), z)) for i in range(n_dome)])
vr_d = add_loft(bm_c, dome_rings, cap_start=True, cap_end=True, mat_idx=0)
# Color dark seam & collar bottom edge
for i_ring, (_, _, _, mid) in enumerate(dome_prof):
    if i_ring < len(dome_prof) - 1 and (mid == 1 or dome_prof[i_ring + 1][3] == 1):
        for v in vr_d[i_ring]:
            for f in v.link_faces:
                if any(vv in vr_d[i_ring] for vv in f.verts) and any(vv in vr_d[i_ring + 1] for vv in f.verts):
                    f.material_index = 1

# B. Main porthole on +Y face (looking backwards):
#    Window 0.13 across (r_glass=0.065), frame 0.02 wide (r_out=0.085), sticking out 0.025
#    Note: dome back surface at Z=1.31 is Y = 0.25 + 0.15 = 0.40 -> frame sticks out to ~0.415
ph_c = Vector((0.0, 0.392, 1.310))
rot_back = Matrix.Rotation(math.radians(-90), 4, 'X') # local +Z -> +Y
# Outer brass frame (r_in=0.065, r_out=0.085)
add_annular_frame(bm_c, ph_c + Vector((0, 0.008, 0)), rot_back, r_in=0.065, r_out=0.086, depth=0.030, segs=24, mat_idx=0)
# Inner dark brass bezel lip
add_annular_frame(bm_c, ph_c + Vector((0, 0.012, 0)), rot_back, r_in=0.060, r_out=0.066, depth=0.024, segs=24, mat_idx=1)

# Backing dark plate behind glass so glass has depth
res_bk = bmesh.ops.create_cone(
    bm_c, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.064, radius2=0.064, depth=0.006,
    matrix=Matrix.Translation(ph_c + Vector((0, -0.002, 0))) @ rot_back
)
tag_res(res_bk["verts"], 3)

# Slightly transparent shiny glass (0.13 across -> r=0.064)
res_gl = bmesh.ops.create_cone(
    bm_c, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.064, radius2=0.064, depth=0.004,
    matrix=Matrix.Translation(ph_c + Vector((0, 0.011, 0))) @ rot_back
)
tag_res(res_gl["verts"], 2)

# Brass cross grille dividing porthole into 4 parts (2 bars, 0.008 wide)
for sx, sz in ((0.134, 0.008), (0.008, 0.134)):
    res_gr = bmesh.ops.create_cube(
        bm_c, size=1.0,
        matrix=Matrix.Translation(ph_c + Vector((0, 0.018, 0))) @ Matrix.Diagonal((sx, 0.008, sz, 1.0))
    )
    tag_res(res_gr["verts"], 0)

# C. 12 Rivets (0.008 across -> r=0.004) around main porthole
for k in range(12):
    ang = 2.0 * math.pi * k / 12
    rx = ph_c.x + 0.0755 * math.cos(ang)
    rz = ph_c.z + 0.0755 * math.sin(ang)
    res_rv = bmesh.ops.create_uvsphere(
        bm_c, u_segments=6, v_segments=4, radius=0.0042,
        matrix=Matrix.Translation((rx, ph_c.y + 0.023, rz))
    )
    tag_res(res_rv["verts"], 1)

# D. 16 Rivets (0.008 across -> r=0.004) around collar ring (Z=1.145)
for k in range(16):
    ang = 2.0 * math.pi * k / 16
    rx = h_c.x + 0.153 * math.cos(ang)
    ry = h_c.y + 0.147 * math.sin(ang)
    res_cr = bmesh.ops.create_uvsphere(
        bm_c, u_segments=6, v_segments=4, radius=0.0042,
        matrix=Matrix.Translation((rx, ry, 1.145))
    )
    tag_res(res_cr["verts"], 1)

# E. Side portholes (-X and +X): 0.07 across (r_out=0.035, r_in=0.024) with brass frame + glass + cross bar
for s in (1.0, -1.0):
    sph_c = Vector((0.156 * s, 0.250, 1.310))
    rot_s = Matrix.Rotation(math.radians(90 * s), 4, 'Y')
    add_annular_frame(bm_c, sph_c, rot_s, r_in=0.023, r_out=0.035, depth=0.022, segs=16, mat_idx=0)
    add_annular_frame(bm_c, sph_c + Vector((0.003 * s, 0, 0)), rot_s, r_in=0.020, r_out=0.024, depth=0.018, segs=16, mat_idx=1)
    res_sgl = bmesh.ops.create_cone(
        bm_c, cap_ends=True, cap_tris=False, segments=14,
        radius1=0.022, radius2=0.022, depth=0.004,
        matrix=Matrix.Translation(sph_c + Vector((0.005 * s, 0, 0))) @ rot_s
    )
    tag_res(res_sgl["verts"], 2)
    res_sgr = bmesh.ops.create_cube(
        bm_c, size=1.0,
        matrix=Matrix.Translation(sph_c + Vector((0.008 * s, 0, 0))) @ Matrix.Diagonal((0.006, 0.006, 0.048, 1.0))
    )
    tag_res(res_sgr["verts"], 1)

# F. Two vertical raised brass bands (0.015 wide) from top of dome down to collar, left & right of main porthole
for s in (1.0, -1.0):
    # Strip along dome meridian at X ~ +-0.105 on back (+Y) and over crown to collar!
    band_pts = []
    band_norms = []
    # Trace from collar front-top? Spec says: "from top of the dome down to the collar, 0.015 wide, on left and right of main porthole"
    for i in range(13):
        t = i / 12.0  # 0 = top apex (Z=1.47), 1 = collar seam (Z=1.16)
        phi = t * math.pi * 0.62  # angle down from top
        # Back-side meridian tilted +-38 deg from +Y towards +-X
        az = s * math.radians(40)
        z = h_c.z + 0.170 * math.cos(phi)
        r_xy = math.sin(phi)
        x = h_c.x + 0.161 * r_xy * math.sin(az)
        y = h_c.y + 0.151 * r_xy * math.cos(az)
        p = Vector((x, y, z))
        nrm = Vector(((x - h_c.x) / 0.16, (y - h_c.y) / 0.15, (z - h_c.z) / 0.17)).normalized()
        band_pts.append(p)
        band_norms.append(nrm)

    b_rings = []
    for i in range(len(band_pts)):
        p = band_pts[i]
        nrm = band_norms[i]
        if i == 0:
            tang = (band_pts[1] - band_pts[0]).normalized()
        elif i == len(band_pts) - 1:
            tang = (band_pts[-1] - band_pts[-2]).normalized()
        else:
            tang = (band_pts[i + 1] - band_pts[i - 1]).normalized()
        side = tang.cross(nrm).normalized()
        hw = 0.0075 # 0.015 wide
        th = 0.005
        b_rings.append([
            p - side * hw - nrm * 0.002,
            p + side * hw - nrm * 0.002,
            p + side * (hw * 0.85) + nrm * th,
            p - side * (hw * 0.85) + nrm * th,
        ])
    add_loft(bm_c, b_rings, cap_start=True, cap_end=True, mat_idx=1)

# Top brass vent/lifting lug on upper dome
res_top = bmesh.ops.create_cone(
    bm_c, cap_ends=True, cap_tris=False, segments=12,
    radius1=0.020, radius2=0.015, depth=0.022,
    matrix=Matrix.Translation(h_c + Vector((0, 0.0, 0.162)))
)
tag_res(res_top["verts"], 1)

bmesh.ops.recalc_face_normals(bm_c, faces=bm_c.faces[:])
ob_c = bpy.data.objects.get("CascoPalombaro")
ob_c.data.materials.clear()
for m in (mat_brass, mat_brass_dark, mat_glass, mat_glass_back):
    ob_c.data.materials.append(m)
bm_c.to_mesh(ob_c.data)
bm_c.free()
for p in ob_c.data.polygons:
    p.use_smooth = True
ob_c.data.update()

# 2. Rebuild ZainoTubi (9.8 Hoses, 9.9 Bedroll, 9.10 Hanging rope loops, 9.11 Back harness & waist strap):
#    Materials: 0: mat_bedroll, 1: mat_leather, 2: mat_hose, 3: mat_brass_dark, 4: mat_rope
bm_z = bmesh.new()

# A. 9.9 Bedroll: horizontal roll 0.34 long, 0.11 across (r=0.055), centre (0, +0.22, 1.06),
#    cream-tan canvas (0.66, 0.58, 0.45), held by 2 brown leather straps (0.02 wide) at X=-0.10 & +0.10
roll_c = Vector((0.0, 0.22, 1.06))
rot_x90 = Matrix.Rotation(math.radians(90), 4, 'Y')
res_roll = bmesh.ops.create_cone(
    bm_z, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.055, radius2=0.055, depth=0.34,
    matrix=Matrix.Translation(roll_c) @ rot_x90
)
tag_res(res_roll["verts"], 0)

# Rolled canvas end detail rings at X=+-0.17
for sx in (-0.170, 0.170):
    res_re = bmesh.ops.create_cone(
        bm_z, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.034, radius2=0.034, depth=0.008,
        matrix=Matrix.Translation(roll_c + Vector((sx, 0, 0))) @ rot_x90
    )
    tag_res(res_re["verts"], 4)

# Two brown leather straps (0.02 wide) around bedroll at X=-0.10 and X=+0.10
for dx in (-0.10, 0.10):
    res_bs = bmesh.ops.create_cone(
        bm_z, cap_ends=True, cap_tris=False, segments=20,
        radius1=0.058, radius2=0.058, depth=0.020,
        matrix=Matrix.Translation(roll_c + Vector((dx, 0, 0))) @ rot_x90
    )
    tag_res(res_bs["verts"], 1)

# B. 9.8 Two ribbed corrugated hoses (0.03 across -> max r=0.0155, groove r=0.0120)
def add_corrugated_hose(bm_target, ctrl_pts, r_outer=0.0155, r_inner=0.0118, n_rib_steps=38, n_sides=8, mat_idx=2):
    # Subdivide/resample smooth polyline along ctrl_pts via Catmull-Rom / quadratic Bezier-like smoothing
    dense = []
    # Smooth subdivision (Chaikin-style or cubic interpolation)
    ext = [ctrl_pts[0]] + list(ctrl_pts) + [ctrl_pts[-1]]
    samples = []
    n_per_seg = 12
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n_per_seg):
            t = k / n_per_seg
            t2, t3 = t * t, t * t * t
            pt = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            samples.append(pt)
    samples.append(ctrl_pts[-1])

    # Compute arc-length parameter and resample n_rib_steps evenly spaced points
    dists = [0.0]
    for i in range(1, len(samples)):
        dists.append(dists[-1] + (samples[i] - samples[i - 1]).length)
    total_len = dists[-1]
    pts = []
    for k in range(n_rib_steps + 1):
        target_d = total_len * (k / n_rib_steps)
        # Find segment
        idx = 0
        while idx < len(dists) - 2 and dists[idx + 1] < target_d:
            idx += 1
        seg_l = max(1e-6, dists[idx + 1] - dists[idx])
        frac = (target_d - dists[idx]) / seg_l
        pts.append(samples[idx].lerp(samples[idx + 1], frac))

    rings = []
    prev_u = None
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        if prev_u is None:
            ref = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
            u = t.cross(ref).normalized()
        else:
            u = (prev_u - t * prev_u.dot(t)).normalized()
        v = t.cross(u).normalized()
        prev_u = u
        # Alternating rib / groove every step!
        r = r_outer if (i % 2 == 0) else r_inner
        rings.append([p + u * (r * math.cos(2 * math.pi * k / n_sides))
                        + v * (r * math.sin(2 * math.pi * k / n_sides)) for k in range(n_sides)])
    add_loft(bm_target, rings, cap_start=True, cap_end=True, mat_idx=mat_idx)

# Brass hose outlets at lower sides of helmet (X=+-0.14, Y=0.25, Z=1.18)
for s in (1.0, -1.0):
    res_nozz = bmesh.ops.create_cone(
        bm_z, cap_ends=True, cap_tris=False, segments=12,
        radius1=0.020, radius2=0.017, depth=0.032,
        matrix=Matrix.Translation((0.138 * s, 0.245, 1.18)) @ Matrix.Rotation(math.radians(35 * s), 4, 'Y')
    )
    tag_res(res_nozz["verts"], 3)

# Right side (-X) hose: goes down from helmet (-0.145, 0.24, 1.17) and coils into a FLAT SPIRAL DISC
# (0.12 across -> outer radius 0.060) hanging at X=-0.12, Y=+0.20, Z=1.00!
spiral_pts = [
    Vector((-0.142, 0.242, 1.170)),
    Vector((-0.165, 0.232, 1.105)),
    Vector((-0.162, 0.215, 1.045)),
]
# Spiral disc in YZ/XZ plane (visible cleanly in side view AND back view at X=-0.12, Y=0.20, Z=1.00!)
# Make spiral face slightly angled outward (-X / +Y) so it reads clearly in both back and right-side drawings!
disc_c = Vector((-0.135, 0.215, 0.995))
n_sp = 22
for i in range(n_sp):
    t = i / (n_sp - 1)
    ang = math.radians(110) + t * math.pi * 3.2  # 1.6 full turns spiralling inward from r=0.056 to r=0.016
    r_sp = 0.056 * (1.0 - 0.72 * t)
    # Plane perpendicular to (-0.65, 0.75, 0) -> u along (-0.75, -0.65, 0), v along (0, 0, 1)
    u_dir = Vector((-0.65, -0.76, 0.0)).normalized()
    v_dir = Vector((0.0, 0.0, 1.0))
    spiral_pts.append(disc_c + u_dir * (r_sp * math.cos(ang)) + v_dir * (r_sp * math.sin(ang)))

add_corrugated_hose(bm_z, spiral_pts, r_outer=0.0155, r_inner=0.0118, n_rib_steps=44, n_sides=8, mat_idx=2)

# Left side (+X) hose: goes down from helmet (+0.145, 0.24, 1.17) and forward under her arm towards belt at X=+0.17, Z=1.02
left_hose_pts = [
    Vector((0.142, 0.242, 1.170)),
    Vector((0.175, 0.235, 1.115)),
    Vector((0.192, 0.190, 1.055)),
    Vector((0.190, 0.120, 1.020)),
    Vector((0.172, 0.055, 1.020)), # tucks cleanly into waist belt at X=+0.17, Z=1.02!
]
add_corrugated_hose(bm_z, left_hose_pts, r_outer=0.0155, r_inner=0.0118, n_rib_steps=32, n_sides=8, mat_idx=2)

# C. 9.10 Two loops of beige twisted rope (0.12 long) hanging from helmet bottom (Z~1.13) over bedroll (Z~1.00)
def add_twisted_rope(bm_target, pts, radius=0.0075, turns=4.5, n_cross=8, mat_idx=4):
    m = len(pts)
    rings = []
    prev_u = None
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == m - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        if prev_u is None:
            ref = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
            u = t.cross(ref).normalized()
        else:
            u = (prev_u - t * prev_u.dot(t)).normalized()
        v = t.cross(u).normalized()
        prev_u = u
        twist = 2.0 * math.pi * turns * (i / max(1, m - 1))
        rings.append([
            bm_target.verts.new(p + u * (radius * (0.76 + 0.28 * math.cos(3 * (2*math.pi*k/n_cross - twist))) * math.cos(2*math.pi*k/n_cross))
                                  + v * (radius * (0.76 + 0.28 * math.cos(3 * (2*math.pi*k/n_cross - twist))) * math.sin(2*math.pi*k/n_cross)))
            for k in range(n_cross)
        ])
    for i in range(m - 1):
        for k in range(n_cross):
            kn = (k + 1) % n_cross
            f = bm_target.faces.new((rings[i][k], rings[i][kn], rings[i + 1][kn], rings[i + 1][k]))
            f.material_index = mat_idx

for k_loop, (off_x, off_y, z_drop) in enumerate(((-0.015, 0.282, 0.995), (0.015, 0.292, 1.005))):
    r_pts = []
    for i in range(19):
        t = i / 18.0
        ang = t * math.pi  # U-loop hanging down from helmet collar (Z=1.14) over back of bedroll (Y=0.285..0.295) down to Z=1.00
        px = off_x - 0.055 * math.cos(ang)
        pz = 1.135 - (1.135 - z_drop) * math.sin(ang)
        py = 0.265 + (off_y - 0.265) * math.sin(ang)
        r_pts.append(Vector((px, py, pz)))
    add_twisted_rope(bm_z, r_pts, radius=0.0075, turns=5.0, n_cross=8, mat_idx=4)

# D. 9.11 Harness:
#    1) Back straps from shoulders connecting to helmet collar ring at top-left & top-right (+-0.11, +0.16, 1.16)
#    2) Horizontal waist strap around back holding the bedroll!
def add_flat_strap(bm_target, pts, norms, width=0.028, thick=0.007, mat_idx=1):
    rings = []
    m = len(pts)
    for i in range(m):
        p = pts[i]
        nrm = norms[i].normalized()
        tang = (pts[min(m-1, i+1)] - pts[max(0, i-1)]).normalized()
        side = tang.cross(nrm).normalized()
        nrm = side.cross(tang).normalized()
        hw = width * 0.5
        rings.append([
            bm_target.verts.new(p - side * hw),
            bm_target.verts.new(p + side * hw),
            bm_target.verts.new(p + side * hw + nrm * thick),
            bm_target.verts.new(p - side * hw + nrm * thick),
        ])
    for i in range(m - 1):
        for k in range(4):
            kn = (k + 1) % 4
            f = bm_target.faces.new((rings[i][k], rings[i][kn], rings[i + 1][kn], rings[i + 1][k]))
            f.material_index = mat_idx
    bm_target.faces.new(rings[0][::-1]).material_index = mat_idx
    bm_target.faces.new(rings[-1]).material_index = mat_idx

for s in (1.0, -1.0):
    # Shoulder strap from front/shoulder (s*0.13, 0.04, 1.40) -> over cape collar base -> helmet collar ring (s*0.125, 0.17, 1.15)
    h_pts = [
        Vector((0.125 * s, 0.045, 1.405)),
        Vector((0.130 * s, 0.115, 1.355)),
        Vector((0.125 * s, 0.155, 1.260)),
        Vector((0.125 * s, 0.175, 1.155)),
    ]
    h_norms = [Vector((0.2*s, 0.8, 0.5)), Vector((0.3*s, 0.9, 0.1)), Vector((0.3*s, 0.9, 0.0)), Vector((0.4*s, 0.9, -0.1))]
    add_flat_strap(bm_z, h_pts, h_norms, width=0.030, thick=0.008, mat_idx=1)

# Horizontal waist strap around back holding bedroll (wraps from X=-0.16, Y=+0.10 to back of bedroll Y=+0.278 to X=+0.16, Y=+0.10)
wb_pts = [
    Vector((-0.155, 0.085, 1.06)),
    Vector((-0.168, 0.175, 1.06)),
    Vector((-0.120, 0.268, 1.06)),
    Vector(( 0.000, 0.276, 1.06)),
    Vector(( 0.120, 0.268, 1.06)),
    Vector(( 0.168, 0.175, 1.06)),
    Vector(( 0.155, 0.085, 1.06)),
]
wb_norms = [Vector((p.x, p.y - 0.05, 0.0)).normalized() for p in wb_pts]
add_flat_strap(bm_z, wb_pts, wb_norms, width=0.026, thick=0.007, mat_idx=1)

bmesh.ops.recalc_face_normals(bm_z, faces=bm_z.faces[:])
ob_z = bpy.data.objects.get("ZainoTubi")
ob_z.data.materials.clear()
for m in (mat_bedroll, mat_leather, mat_hose, mat_brass_dark, mat_rope):
    ob_z.data.materials.append(m)
bm_z.to_mesh(ob_z.data)
bm_z.free()
for p in ob_z.data.polygons:
    p.use_smooth = True
ob_z.data.update()

# Log Group 9 & overall triangle count
depsgraph = bpy.context.evaluated_depsgraph_get()
total_tris = 0
for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    if obj.type == 'MESH':
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        t = len(me.loop_triangles)
        total_tris += t
        if obj.name in ("CascoPalombaro", "ZainoTubi"):
            pts = [obj.matrix_world @ v.co for v in me.vertices]
            log(f"{obj.name}: tris={t}, X=({min(p.x for p in pts):.3f}..{max(p.x for p in pts):.3f}), Y=({min(p.y for p in pts):.3f}..{max(p.y for p in pts):.3f}), Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
        ev.to_mesh_clear()
log(f"CURRENT_TOTAL_TRIS={total_tris} (max 40000)")

bpy.ops.wm.save_mainfile()
render_viste("rev_9")
