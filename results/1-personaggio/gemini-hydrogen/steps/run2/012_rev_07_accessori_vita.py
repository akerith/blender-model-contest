import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 7: Waist gear
# - 7.1 Coiled 3-strand twisted rope on right hip (-X), 4 overlapping loops Z 0.92..0.72
# - 7.2 Right-hip horizontal brass-and-leather canister (0.20x0.07) at (-0.24, -0.03, 0.90)
# - 7.3 Right-hip round leather pouch with flap (0.09x0.06x0.08) at (-0.20, 0.02, 0.99)
# - 7.4 Left-hip map tube (0.45x0.075, Z 0.98..0.53) at (+0.22, -0.02) + outer thinner cylinder (0.35x0.05)
# - 7.5 Torn cream cloth hanging on left between map tube and leg (0.07 wide, Z 0.98..0.62)
# - 7.6 Three small brown leather pouches (0.06x0.05x0.03) along the belt at back and sides

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.65, metallic=0.0, spec=0.35):
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

mat_rope         = set_mat_srgb("CordaCanapa", (0.70, 0.62, 0.47), roughness=0.88, spec=0.18)
mat_leather      = set_mat_srgb("PelleMarrone", (0.36, 0.22, 0.12), roughness=0.65, spec=0.35)
mat_leather_dark = set_mat_srgb("PelleScura", (0.24, 0.14, 0.08), roughness=0.66, spec=0.35)
mat_brass        = set_mat_srgb("Ottone", (0.62, 0.45, 0.20), roughness=0.35, metallic=1.0, spec=0.50)
mat_cloth_cream  = set_mat_srgb("CamiciaBeige", (0.82, 0.76, 0.64), roughness=0.90, spec=0.18)
mat_shell        = set_mat_srgb("Conchiglie", (0.88, 0.85, 0.78), roughness=0.45, spec=0.40)

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

def add_twisted_rope_loop(bm, center_pts, radius=0.0075, turns=9.0, n_cross=9, mat_idx=0):
    # Closed 3-strand twisted trefoil rope profile along center_pts
    m = len(center_pts)
    rings = []
    # Compute smooth Frenet-like frames
    prev_u = None
    for i in range(m):
        p = center_pts[i]
        t = (center_pts[(i + 1) % m] - center_pts[(i - 1) % m]).normalized()
        if prev_u is None:
            ref = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            u = t.cross(ref).normalized()
        else:
            u = (prev_u - t * prev_u.dot(t)).normalized()
        v = t.cross(u).normalized()
        prev_u = u
        twist = 2.0 * math.pi * turns * (i / m)
        ring = []
        for k in range(n_cross):
            ang = 2.0 * math.pi * k / n_cross
            # 3-lobed twisted rope cross section (thickness ~0.015 -> outer radius ~0.0078)
            r_mod = radius * (0.76 + 0.28 * math.cos(3.0 * (ang - twist)))
            pt = p + u * (r_mod * math.cos(ang)) + v * (r_mod * math.sin(ang))
            ring.append(bm.verts.new(pt))
        rings.append(ring)
    for i in range(m):
        r0 = rings[i]
        r1 = rings[(i + 1) % m]
        for k in range(n_cross):
            kn = (k + 1) % n_cross
            f = bm.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
            f.material_index = mat_idx

def add_pouch(bm, center, rot_mat, sx, sy, sz, mat_body=1, mat_strap=2, mat_brass=3):
    # Rounded leather pouch with overlapping curved flap + tiny brass rivet
    # Local space: Y+ = outward from body, X = width, Z = height
    m_base = Matrix.Translation(center) @ rot_mat
    # Pouch body (beveled/subdivided rounded cube)
    res_b = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.bevel(bm, geom=res_b["verts"] + list({e for v in res_b["verts"] for e in v.link_edges}),
                    offset=0.14, segments=2, affect='EDGES')
    # Collect all new verts of body
    body_verts = [v for v in bm.verts if v.index == -1 or True]  # safer: transform via tag before adding next
    # Actually let's build cleanly in sub-bmesh and merge, or transform just created verts!
    return

def make_pouch_to_bm(bm_target, center, normal_out, sx, sy, sz, mat_body=1, mat_flap=2, mat_brass=3):
    # Build pouch in temporary bmesh so bevel & transforms never touch existing bm_target geometry
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=0.18, segments=2, affect='EDGES')
    for v in tmp.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    for f in tmp.faces:
        f.material_index = mat_body

    # Flap covering top and upper 60% of outward (+Y) face
    tmp_flap = bmesh.new()
    bmesh.ops.create_cube(tmp_flap, size=1.0)
    bmesh.ops.bevel(tmp_flap, geom=tmp_flap.edges[:], offset=0.18, segments=1, affect='EDGES')
    for v in tmp_flap.verts:
        v.co.x *= sx * 1.06
        v.co.y *= sy * 0.42
        v.co.z *= sz * 0.65
        v.co.y += sy * 0.34
        v.co.z += sz * 0.22
    for f in tmp_flap.faces:
        f.material_index = mat_flap

    # Brass clasp button on flap
    bmesh.ops.create_uvsphere(
        tmp_flap, u_segments=8, v_segments=6, radius=min(sx, sz) * 0.11,
        matrix=Matrix.Translation((0.0, sy * 0.56, sz * 0.02)) @ Matrix.Diagonal((1.0, 0.5, 1.0, 1.0))
    )
    for v in tmp_flap.verts[-26:]:
        for f in v.link_faces:
            f.material_index = mat_brass

    # Merge tmp & tmp_flap into bm_target transformed to world pose
    nrm = normal_out.normalized()
    up = Vector((0, 0, 1))
    right = up.cross(nrm).normalized()
    up_ortho = nrm.cross(right).normalized()
    rot = Matrix((right, nrm, up_ortho)).transposed().to_4x4()
    xform = Matrix.Translation(center) @ rot

    for src in (tmp, tmp_flap):
        vmap = {}
        for v in src.verts:
            vmap[v] = bm_target.verts.new(xform @ v.co)
        for f in src.faces:
            nf = bm_target.faces.new([vmap[v] for v in f.verts])
            nf.material_index = f.material_index
        src.free()

# 1. AccessoriDestra (7.1 Coiled rope, 7.2 Horizontal canister, 7.3 Round pouch, + 7.6 Belt pouches!)
bm_r = bmesh.new()

# 7.1 Coiled rope on RIGHT hip (-X): 4 overlapping twisted loops hanging from lower belt (X -0.17, Z 0.98) down to Z 0.72
#     Each loop oval ~0.18 high, 0.10 wide, rope thickness 0.015 (radius 0.0075)
for k in range(4):
    # Stagger loops slightly in X (-0.162 .. -0.188) and Y (+0.015 .. -0.025) and Z
    cx = -0.172 - k * 0.006
    cy = 0.010 - k * 0.008
    cz = 0.822 - k * 0.004
    pts = []
    n_loop = 32
    for i in range(n_loop):
        ang = 2.0 * math.pi * i / n_loop
        # Oval 0.17..0.19 high (rz=0.088), 0.10 wide (ry=0.050), tilted slightly outward at bottom
        py = cy + 0.050 * math.cos(ang)
        pz = cz + 0.092 * math.sin(ang)
        px = cx - 0.012 * (1.0 - math.sin(ang)) * 0.5 + 0.006 * math.sin(ang * 2.0)
        pts.append(Vector((px, py, pz)))
    add_twisted_rope_loop(bm_r, pts, radius=0.0076, turns=8.0, n_cross=9, mat_idx=0)

# Leather keeper strap holding the rope bundle to the lower belt at X -0.17, Z 0.95
res_rk = bmesh.ops.create_cube(
    bm_r, size=1.0,
    matrix=Matrix.Translation((-0.176, -0.004, 0.925)) @ Matrix.Diagonal((0.046, 0.030, 0.055, 1.0))
)
tag_res(res_rk["verts"], 2)

# 7.2 Right-hip canister (in front of rope, lower): brass & leather cylinder lying almost horizontal,
#     0.20 long, 0.07 across (r=0.035), centre at X -0.24, Z 0.90, Y -0.03, brass end caps & 2 brass bands!
can_c = Vector((-0.24, -0.03, 0.90))
# Almost horizontal along Y (15 deg nose-down tilt forward, 10 deg out)
can_rot = Matrix.Rotation(math.radians(90 - 14), 4, 'X') @ Matrix.Rotation(math.radians(-8), 4, 'Y')
can_mat = Matrix.Translation(can_c) @ can_rot

# Leather main cylinder body (0.20 long, 0.07 across)
res_cb = bmesh.ops.create_cone(
    bm_r, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.034, radius2=0.034, depth=0.165,
    matrix=can_mat
)
tag_res(res_cb["verts"], 1)

# Brass end caps (at both ends of 0.20m length)
for dz in (-0.088, 0.088):
    res_ec = bmesh.ops.create_cone(
        bm_r, cap_ends=True, cap_tris=False, segments=20,
        radius1=0.0365, radius2=0.0365, depth=0.024,
        matrix=can_mat @ Matrix.Translation((0, 0, dz))
    )
    tag_res(res_ec["verts"], 3)

# Two brass bands around the canister
for dz in (-0.038, 0.038):
    res_bd = bmesh.ops.create_cone(
        bm_r, cap_ends=True, cap_tris=False, segments=20,
        radius1=0.0365, radius2=0.0365, depth=0.014,
        matrix=can_mat @ Matrix.Translation((0, 0, dz))
    )
    tag_res(res_bd["verts"], 3)

# Short leather hanger straps tying canister up to lower belt / pouch
for dz in (-0.038, 0.038):
    p_band = can_mat @ Vector((0, 0, dz))
    res_st = bmesh.ops.create_cube(
        bm_r, size=1.0,
        matrix=Matrix.Translation((p_band.x + 0.022, p_band.y, 0.93)) @ Matrix.Rotation(math.radians(-22), 4, 'Y') @ Matrix.Diagonal((0.012, 0.016, 0.070, 1.0))
    )
    tag_res(res_st["verts"], 2)

# 7.3 Round leather pouch on right hip above canister: flattened sphere 0.09 x 0.06 x 0.08 with flap, centre X -0.20, Z 0.99
pouch_c = Vector((-0.20, 0.005, 0.99))
res_rp = bmesh.ops.create_uvsphere(
    bm_r, u_segments=16, v_segments=12, radius=1.0,
    matrix=Matrix.Translation(pouch_c) @ Matrix.Diagonal((0.030, 0.045, 0.040, 1.0)) # 0.06 thick X, 0.09 wide Y, 0.08 high Z!
)
tag_res(res_rp["verts"], 1)

# Leather flap over outer top of round pouch
res_rf = bmesh.ops.create_uvsphere(
    bm_r, u_segments=14, v_segments=10, radius=1.0,
    matrix=Matrix.Translation(pouch_c + Vector((-0.006, 0.0, 0.008))) @ Matrix.Diagonal((0.029, 0.046, 0.035, 1.0))
)
tag_res(res_rf["verts"], 2)

# Small brass button on pouch flap
res_rb = bmesh.ops.create_cone(
    bm_r, cap_ends=True, cap_tris=False, segments=10,
    radius1=0.007, radius2=0.007, depth=0.006,
    matrix=Matrix.Translation(pouch_c + Vector((-0.033, 0.0, -0.004))) @ Matrix.Rotation(math.radians(90), 4, 'Y')
)
tag_res(res_rb["verts"], 3)

# 7.6 Three small brown leather pouches along the belt (~0.06 x 0.05 x 0.03) at back & sides
make_pouch_to_bm(bm_r, Vector((-0.11,  0.115, 1.01)), Vector((-0.65, 0.75, 0.0)), 0.060, 0.030, 0.052, mat_body=1, mat_flap=2, mat_brass=3)
make_pouch_to_bm(bm_r, Vector(( 0.10,  0.118, 1.02)), Vector(( 0.55, 0.82, 0.0)), 0.060, 0.030, 0.052, mat_body=1, mat_flap=2, mat_brass=3)
make_pouch_to_bm(bm_r, Vector(( 0.165, 0.065, 1.01)), Vector(( 0.88, 0.48, 0.0)), 0.060, 0.030, 0.050, mat_body=1, mat_flap=2, mat_brass=3)

bmesh.ops.recalc_face_normals(bm_r, faces=bm_r.faces[:])
ob_r = bpy.data.objects.get("AccessoriDestra")
ob_r.data.materials.clear()
for m in (mat_rope, mat_leather, mat_leather_dark, mat_brass):
    ob_r.data.materials.append(m)
bm_r.to_mesh(ob_r.data)
bm_r.free()
for p in ob_r.data.polygons:
    p.use_smooth = True
ob_r.data.update()

# 2. TuboMappe_L (7.4):
#    Main tall cylinder: 0.45 long, 0.075 across (r=0.0375), Z 0.98 down to Z 0.53, centre X +0.22, Y -0.02
#    Brown leather body, brass cap at top and bottom (0.04 high each), 2 leather straps around it.
#    Second thinner cylinder beside it on outside: 0.35 long, 0.05 across (r=0.025)
bm_l = bmesh.new()

main_c = Vector((0.22, -0.02, 0.755)) # midpoint of Z 0.98 .. 0.53 (0.45 long)
# Keep nearly vertical (tiny 4 deg hang tilt so top stays at 0.98 and bottom at 0.53)
main_rot = Matrix.Rotation(math.radians(-4), 4, 'X') @ Matrix.Rotation(math.radians(3), 4, 'Y')
main_mat = Matrix.Translation(main_c) @ main_rot

# Leather body (0.45 - 2*0.04 = 0.37 inner leather + caps overlapping cleanly -> 0.45 total)
res_tb = bmesh.ops.create_cone(
    bm_l, cap_ends=True, cap_tris=False, segments=20,
    radius1=0.0370, radius2=0.0370, depth=0.38,
    matrix=main_mat
)
tag_res(res_tb["verts"], 0)

# Brass top cap & bottom cap (each 0.04 high, outer radius 0.0385 -> 0.077 across)
for dz in (-0.205, 0.205):
    res_tc = bmesh.ops.create_cone(
        bm_l, cap_ends=True, cap_tris=False, segments=20,
        radius1=0.0385, radius2=0.0385, depth=0.040,
        matrix=main_mat @ Matrix.Translation((0, 0, dz))
    )
    tag_res(res_tc["verts"], 1)

# Second thinner cylinder beside it on outside (+X): 0.35 long, 0.05 across (r=0.025)
sub_c = main_mat @ Vector((0.064, 0.005, 0.01))
sub_mat = Matrix.Translation(sub_c) @ main_rot
res_sb = bmesh.ops.create_cone(
    bm_l, cap_ends=True, cap_tris=False, segments=16,
    radius1=0.0245, radius2=0.0245, depth=0.29,
    matrix=sub_mat
)
tag_res(res_sb["verts"], 0)

# Brass end caps on second cylinder
for dz in (-0.155, 0.155):
    res_sc = bmesh.ops.create_cone(
        bm_l, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.0260, radius2=0.0260, depth=0.035,
        matrix=sub_mat @ Matrix.Translation((0, 0, dz))
    )
    tag_res(res_sc["verts"], 1)

# Two leather straps wrapping around main tube & connecting to second tube + belt hanger
for dz in (-0.09, 0.11):
    # Strap ring on main tube
    res_st1 = bmesh.ops.create_cone(
        bm_l, cap_ends=True, cap_tris=False, segments=20,
        radius1=0.0395, radius2=0.0395, depth=0.022,
        matrix=main_mat @ Matrix.Translation((0, 0, dz))
    )
    tag_res(res_st1["verts"], 2)
    # Strap ring on second tube
    res_st2 = bmesh.ops.create_cone(
        bm_l, cap_ends=True, cap_tris=False, segments=16,
        radius1=0.0270, radius2=0.0270, depth=0.022,
        matrix=sub_mat @ Matrix.Translation((0, 0, dz - 0.01))
    )
    tag_res(res_st2["verts"], 2)
    # Bridge joining the two tubes
    res_br = bmesh.ops.create_cube(
        bm_l, size=1.0,
        matrix=main_mat @ Matrix.Translation((0.040, 0.002, dz)) @ Matrix.Diagonal((0.035, 0.025, 0.022, 1.0))
    )
    tag_res(res_br["verts"], 2)

# Hanger strap attaching top of main map tube cleanly to lower belt at X +0.18, Z 1.00
res_hg = bmesh.ops.create_cube(
    bm_l, size=1.0,
    matrix=Matrix.Translation((0.192, -0.018, 0.96)) @ Matrix.Rotation(math.radians(24), 4, 'Y') @ Matrix.Diagonal((0.014, 0.026, 0.085, 1.0))
)
tag_res(res_hg["verts"], 2)

bmesh.ops.recalc_face_normals(bm_l, faces=bm_l.faces[:])
ob_l = bpy.data.objects.get("TuboMappe_L")
ob_l.data.materials.clear()
for m in (mat_leather, mat_brass, mat_leather_dark):
    ob_l.data.materials.append(m)
bm_l.to_mesh(ob_l.data)
bm_l.free()
for p in ob_l.data.polygons:
    p.use_smooth = True
ob_l.data.update()

# 3. Add 7.5 Torn cream cloth hanging from lower belt on her left (+X) between map tube and leg:
#    0.07 wide, from Z 0.98 down to Z 0.62, with ragged lower end. Put in MantelloDettagli alongside 3 shells!
ob_md = bpy.data.objects.get("MantelloDettagli")
bm_d = bmesh.new()
bm_d.from_mesh(ob_md.data)

# Keep shells (z > 1.25), drop any old strips (z < 1.25)
del_old = [v for v in bm_d.verts if v.co.z < 1.25]
if del_old:
    bmesh.ops.delete(bm_d, geom=del_old, context='VERTS')

if mat_cloth_cream.name not in [m.name for m in ob_md.data.materials if m]:
    ob_md.data.materials.append(mat_cloth_cream)
cloth_idx = [m.name for m in ob_md.data.materials].index(mat_cloth_cream.name)

# Build draped torn cream cloth strip hanging between left thigh (X~0.14) and map tube (X~0.20)
# Centered at X +0.175, Y -0.045, width ~0.07 across Y/X diagonal, Z 0.98 down to Z 0.62
nu_t = 6
nv_t = 9
# Ragged lower Z profile from 0.62 to 0.72
rag_end = [0.71, 0.65, 0.69, 0.62, 0.67, 0.63, 0.70]
cloth_grid = []
for iv in range(nv_t + 1):
    tv = iv / nv_t
    row = []
    for iu in range(nu_t + 1):
        tu = iu / nu_t  # 0..1 across width 0.07
        z_bot = rag_end[iu]
        z = 0.985 * (1.0 - tv) + z_bot * tv
        # Slight sway and drape folds
        w_span = 0.068 * (1.0 - 0.12 * tv)
        s_off = (tu - 0.5) * w_span
        fold = 0.006 * math.sin(tu * math.pi * 3.0) * tv
        x = 0.175 + 0.012 * tv + s_off * 0.25 + fold
        y = -0.035 + 0.015 * tv + s_off * 0.95
        row.append(bm_d.verts.new(Vector((x, y, z))))
    cloth_grid.append(row)

c_faces = []
for iv in range(nv_t):
    for iu in range(nu_t):
        f = bm_d.faces.new((cloth_grid[iv][iu], cloth_grid[iv][iu + 1], cloth_grid[iv + 1][iu + 1], cloth_grid[iv + 1][iu]))
        f.material_index = cloth_idx
        c_faces.append(f)
bmesh.ops.solidify(bm_d, geom=c_faces, thickness=0.004)
bmesh.ops.recalc_face_normals(bm_d, faces=bm_d.faces[:])
bm_d.to_mesh(ob_md.data)
bm_d.free()
for p in ob_md.data.polygons:
    p.use_smooth = True
ob_md.data.update()

# Log Group 7 stats
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ("AccessoriDestra", "TuboMappe_L", "MantelloDettagli"):
    ob = bpy.data.objects.get(name)
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    log(f"{name}: tris={len(me.loop_triangles)}, X=({min(p.x for p in pts):.3f}..{max(p.x for p in pts):.3f}), Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
    ev.to_mesh_clear()

bpy.ops.wm.save_mainfile()
render_viste("rev_7")
