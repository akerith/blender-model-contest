import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 2: Head, face and hair (~6,000 tris for face + hair)

# 1. Update materials for skin, eyes, eyebrows, hair, white streak, lips
def set_mat(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_skin       = set_mat("Pelle", (0.85, 0.68, 0.58), roughness=0.55)
mat_hair       = set_mat("CapelliScuri", (0.10, 0.08, 0.07), roughness=0.68)
mat_hair_white = set_mat("CapelliBianchi", (0.80, 0.80, 0.78), roughness=0.58)
mat_eye_white  = set_mat("OcchioBianco", (0.88, 0.87, 0.84), roughness=0.18)
mat_iris       = set_mat("OcchioIride", (0.13, 0.08, 0.05), roughness=0.12)
mat_lips       = set_mat("Labbra", (0.64, 0.42, 0.37), roughness=0.48)
mat_mouth_line = set_mat("LineaBocca", (0.28, 0.16, 0.14), roughness=0.55)

# Helper loft/rings
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

def make_oval(center, rx, ry, n=24):
    cx, cy, cz = center
    return [Vector((cx + rx * math.cos(2 * math.pi * i / n),
                    cy + ry * math.sin(2 * math.pi * i / n),
                    cz)) for i in range(n)]

def make_limb_rings(p0, p1, r_list, n=14):
    axis = (Vector(p1) - Vector(p0)).normalized()
    ref = Vector((0, -1, 0)) if abs(axis.y) < 0.9 else Vector((1, 0, 0))
    right = axis.cross(ref).normalized()
    fwd = right.cross(axis).normalized()
    rings = []
    for t, rx, ry in r_list:
        c = Vector(p0).lerp(Vector(p1), t)
        rings.append([c + right * (rx * math.cos(2 * math.pi * i / n))
                        + fwd * (ry * math.sin(2 * math.pi * i / n)) for i in range(n)])
    return rings

def smooth_gauss(dx, dy, sx, sy):
    return math.exp(-0.5 * ((dx / sx) ** 2 + (dy / sy) ** 2))

# 2. Rebuild CorpoBase head & face cleanly while keeping exact Group 1 body proportions
bm = bmesh.new()

torso_specs = [
    ((0.0, 0.010, 0.855), 0.145, 0.095),
    ((0.0, 0.015, 0.900), 0.162, 0.105),
    ((0.0, 0.008, 0.980), 0.146, 0.094),
    ((0.0, 0.002, 1.080), 0.128, 0.084),
    ((0.0, -0.006, 1.180), 0.140, 0.092),
    ((0.0, -0.012, 1.270), 0.152, 0.100),
    ((0.0, -0.005, 1.350), 0.155, 0.092),
    ((0.0, 0.000, 1.405), 0.148, 0.082),
    ((0.0, 0.000, 1.445), 0.055, 0.053),  # neck width 0.11
    ((0.0, 0.000, 1.495), 0.050, 0.050),
]
add_loft(bm, [make_oval(c, rx, ry, 20) for c, rx, ry in torso_specs])

# Arms and Legs (same exact Group 1 positions)
for s in (1.0, -1.0):
    p_sh = Vector((0.185 * s, 0.0, 1.40))
    p_el = Vector((0.382 * s, 0.010, 1.185))
    p_wr = Vector((0.540 * s, 0.0, 0.990))
    bmesh.ops.create_uvsphere(
        bm, u_segments=12, v_segments=8, radius=0.046,
        matrix=Matrix.Translation((0.158 * s, 0.0, 1.392)) @ Matrix.Diagonal((1.0, 0.92, 0.95, 1.0))
    )
    add_loft(bm, make_limb_rings(p_sh, p_el, [
        (0.0, 0.044, 0.042), (0.35, 0.040, 0.038), (0.75, 0.036, 0.034), (1.0, 0.033, 0.032)
    ], n=12))
    add_loft(bm, make_limb_rings(p_el, p_wr, [
        (0.0, 0.033, 0.032), (0.4, 0.031, 0.030), (0.8, 0.026, 0.024), (1.0, 0.023, 0.020)
    ], n=12))

    p_hp = Vector((0.095 * s, 0.0, 0.90))
    p_kn = Vector((0.112 * s, -0.004, 0.49))
    p_an = Vector((0.130 * s, 0.0, 0.08))
    add_loft(bm, make_limb_rings(p_hp, p_kn, [
        (0.0, 0.070, 0.072), (0.4, 0.058, 0.060), (0.85, 0.048, 0.050), (1.0, 0.046, 0.048)
    ], n=12))
    add_loft(bm, make_limb_rings(p_kn, p_an, [
        (0.0, 0.046, 0.048), (0.35, 0.048, 0.050), (0.75, 0.038, 0.040), (1.0, 0.034, 0.036)
    ], n=12))

# Sculpted Female Head (chin 1.475 -> skull top 1.66, width 0.15, depth 0.19)
# High-res radial-cylindrical grid for crisp nose, eye sockets, brow ridge, cheekbones, chin, jaw
head_z_profile = [
    (1.474, 0.000, 0.028, 0.035),  # under chin center
    (1.476, -0.015, 0.036, 0.050), # chin tip (1.475)
    (1.490, -0.016, 0.050, 0.064), # lower jaw / chin curve
    (1.505, -0.014, 0.057, 0.074), # mouth level (1.505)
    (1.522, -0.012, 0.062, 0.079), # philtrum / jaw angle
    (1.538, -0.010, 0.068, 0.084), # nostrils / lower cheek
    (1.555, -0.008, 0.073, 0.089), # cheekbones
    (1.572, -0.006, 0.074, 0.092), # lower eye socket
    (1.585, -0.004, 0.075, 0.094), # eye level (1.585, width 0.15, depth ~0.19)
    (1.598, -0.003, 0.074, 0.095), # brow ridge
    (1.616,  0.000, 0.072, 0.093), # mid forehead
    (1.635,  0.004, 0.065, 0.085), # upper forehead
    (1.650,  0.007, 0.048, 0.065), # crown curve
    (1.660,  0.009, 0.018, 0.025), # skull top (1.66)
]

n_head = 36
head_rings = []
for row_i, (z, cy, rx, ry) in enumerate(head_z_profile):
    ring = []
    for i in range(n_head):
        # ang=0 is -Y (front), +pi/2 is +X, pi is +Y (back)
        ang = 2.0 * math.pi * i / n_head
        x = rx * math.sin(ang)
        y = cy - ry * math.cos(ang)

        # Apply facial sculpting ONLY on front half (cos(ang) > 0)
        front_fac = max(0.0, math.cos(ang))
        if front_fac > 0.05:
            # 1. Narrower egg jaw/chin taper at front
            if z < 1.54:
                t_j = (1.54 - z) / (1.54 - 1.475)
                x *= (1.0 - 0.18 * t_j * (front_fac ** 1.5))

            # 2. Eye sockets (centered at X=+-0.0325, Z=1.585) -> recess inward (+Y)
            for s in (-1.0, 1.0):
                sock = smooth_gauss(x - 0.0325 * s, z - 1.585, 0.018, 0.011)
                y += 0.009 * sock

            # 3. Brow ridge (Z~1.599) -> slight forward projection
            brow = smooth_gauss(x, z - 1.600, 0.042, 0.009)
            y -= 0.004 * brow

            # 4. Nose wedge (bridge Z=1.580 down to tip Z=1.535, sticking out 0.020)
            if 1.523 <= z <= 1.588:
                if z >= 1.536:
                    t_n = (1.588 - z) / (1.588 - 1.536)
                    nose_proj = 0.021 * (t_n ** 0.75) + 0.002
                    nose_w = 0.0065 + 0.0045 * (t_n ** 1.2)
                else:
                    # under-nose slant back to philtrum
                    t_u = (z - 1.523) / (1.536 - 1.523)
                    nose_proj = 0.023 * (t_u ** 1.3)
                    nose_w = 0.010
                y -= nose_proj * math.exp(-0.5 * (x / nose_w) ** 2)

            # 5. Cheekbones (X=+-0.042, Z=1.558)
            for s in (-1.0, 1.0):
                cheek = smooth_gauss(x - 0.042 * s, z - 1.558, 0.018, 0.014)
                y -= 0.004 * cheek

            # 6. Lips & mouth groove (Z=1.505, width 0.045)
            up_lip = smooth_gauss(x, z - 1.510, 0.018, 0.004)
            lo_lip = smooth_gauss(x, z - 1.499, 0.016, 0.0045)
            m_crease = smooth_gauss(x, z - 1.505, 0.022, 0.0022)
            y -= 0.0045 * up_lip + 0.0040 * lo_lip - 0.0035 * m_crease

            # 7. Chin point (X=0, Z=1.480)
            chin_pt = smooth_gauss(x, z - 1.482, 0.018, 0.010)
            y -= 0.005 * chin_pt

        ring.append(Vector((x, y, z)))
    head_rings.append(ring)

add_loft(bm, head_rings, cap_start=True, cap_end=True)

# Ears (Z 1.55 to 1.59, Y=0.0, X=+-0.075)
for s in (1.0, -1.0):
    ear_rings = [
        [Vector((0.070 * s, 0.002 + 0.010 * math.sin(a), 1.570 + 0.019 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.080 * s, 0.006 + 0.009 * math.sin(a), 1.570 + 0.017 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.083 * s, 0.009 + 0.006 * math.sin(a), 1.570 + 0.011 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
    ]
    add_loft(bm, ear_rings, cap_start=True, cap_end=True)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
obj_body = bpy.data.objects.get("CorpoBase")
bm.to_mesh(obj_body.data)
bm.free()
obj_body.data.materials.clear()
obj_body.data.materials.append(mat_skin)
obj_body.data.update()

# 3. Rebuild DettagliVolto (eyes set slightly into face, dark brows, closed straight lips)
bm_f = bmesh.new()

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

for s in (1.0, -1.0):
    # Eye center at X=+-0.0325, Z=1.585, set slightly into socket (Y=-0.0845)
    # 0.03 wide (rx=0.015), almond height (rz=0.0065)
    eye_c = Vector((0.0325 * s, -0.0835, 1.585))
    # Sclera ellipsoid (mat_idx=3 -> mat_eye_white)
    res_s = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=10, radius=1.0,
        matrix=Matrix.Translation(eye_c) @ Matrix.Rotation(math.radians(-10 * s), 4, 'Z') @ Matrix.Diagonal((0.0145, 0.008, 0.0068, 1.0))
    )
    tag_res(res_s["verts"], 3)

    # Dark brown iris disc set slightly forward on sclera (mat_idx=0 -> mat_iris)
    res_i = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=8, radius=1.0,
        matrix=Matrix.Translation(eye_c + Vector((0.001 * s, -0.0042, 0.0))) @ Matrix.Diagonal((0.0065, 0.0045, 0.0062, 1.0))
    )
    tag_res(res_i["verts"], 0)

    # Upper eyelid crease / lash line framing the top of eye (mat_idx=1 -> mat_hair)
    lash_pts = [
        Vector((0.0185 * s, -0.0865, 1.5855)),
        Vector((0.0260 * s, -0.0905, 1.5905)),
        Vector((0.0335 * s, -0.0910, 1.5912)),
        Vector((0.0415 * s, -0.0880, 1.5890)),
        Vector((0.0470 * s, -0.0825, 1.5850)),
    ]
    lash_rings = []
    for idx, p in enumerate(lash_pts):
        r = 0.0016 if 0 < idx < 4 else 0.0008
        lash_rings.append([p + Vector((0, r * math.cos(a), r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, lash_rings, cap_start=True, cap_end=True, mat_idx=1)

    # Eyebrow: 0.012 above eyes (Z~1.597), straight, angled DOWN towards nose (mat_idx=1)
    # Inner end (near nose) lower: Z=1.594, outer end higher: Z=1.603
    brow_pts = [
        (Vector((0.014 * s, -0.0925, 1.594)), 0.0030, 0.0028),
        (Vector((0.025 * s, -0.0930, 1.597)), 0.0032, 0.0026),
        (Vector((0.037 * s, -0.0890, 1.601)), 0.0028, 0.0023),
        (Vector((0.049 * s, -0.0815, 1.602)), 0.0022, 0.0016),
    ]
    brow_rings = []
    for p, ry, rz in brow_pts:
        brow_rings.append([p + Vector((0, ry * math.cos(a), rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, brow_rings, cap_start=True, cap_end=True, mat_idx=1)

# Mouth: closed straight line at Z=1.505, 0.045 wide (X=-0.0225..+0.0225), lips not smiling
# Sculpted upper & lower lip overlay flush on face + thin dark center line
lip_xs = [-0.0225, -0.013, 0.0, 0.013, 0.0225]
lip_ys = [-0.077, -0.084, -0.0875, -0.084, -0.077]
# Dark closed mouth line (mat_idx=4 -> mat_mouth_line)
mline_rings = []
for lx, ly in zip(lip_xs, lip_ys):
    r = 0.0011 if abs(lx) < 0.02 else 0.0005
    mline_rings.append([Vector((lx, ly - r * math.cos(a), 1.505 + r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
add_loft(bm_f, mline_rings, cap_start=True, cap_end=True, mat_idx=4)

# Subtle lip tint strips above/below mouth line (mat_idx=2 -> mat_lips)
for dz, rz_top in ((0.0028, 0.0022), (-0.0028, 0.0024)):
    l_rings = []
    for lx, ly in zip(lip_xs, lip_ys):
        f_w = max(0.3, 1.0 - (abs(lx) / 0.024) ** 2)
        rz = rz_top * f_w
        ry = 0.0025 * f_w
        l_rings.append([Vector((lx, ly + 0.001 - ry * math.cos(a), 1.505 + dz + rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, l_rings, cap_start=True, cap_end=True, mat_idx=2)

bmesh.ops.recalc_face_normals(bm_f, faces=bm_f.faces[:])
obj_face = bpy.data.objects.get("DettagliVolto")
bm_f.to_mesh(obj_face.data)
bm_f.free()
obj_face.data.materials.clear()
for m in (mat_iris, mat_hair, mat_lips, mat_eye_white, mat_mouth_line):
    obj_face.data.materials.append(m)
obj_face.data.update()

# 4. Rebuild Capelli (at least 25 wavy, messy pointed clumps + inner base cap; ~3,500 tris)
#    Top height Z=1.70 (0.04 above skull 1.66), width 0.19 at top, sides to Z=1.50, back nape Z=1.48
#    White streak sweeping from parting back & right (+X in front / left of back picture, matching 1-personaggio.webp!)
bm_h = bmesh.new()

# Inner scalp base cap (tucked cleanly under clumps so there are zero bald gaps)
cap_specs = [
    ((0.0, 0.015, 1.515), 0.068, 0.082),
    ((0.0, 0.012, 1.565), 0.075, 0.092),
    ((0.0, 0.008, 1.615), 0.077, 0.096),
    ((0.0, 0.008, 1.652), 0.070, 0.088),
    ((0.0, 0.010, 1.678), 0.048, 0.062),
    ((0.0, 0.012, 1.690), 0.020, 0.026),
]
add_loft(bm_h, [make_oval(c, rx, ry, 20) for c, rx, ry in cap_specs], cap_start=True, cap_end=True, mat_idx=0)

def add_clump(bm_target, pts, widths, thicknesses, mat_idx=0, n_sides=6):
    # Sculpted tapered wavy lock with diamond/lens cross-section pointing down and outward
    rings = []
    m = len(pts)
    for i, (p, w, th) in enumerate(zip(pts, widths, thicknesses)):
        p = Vector(p)
        if i == 0:
            tangent = (Vector(pts[1]) - p).normalized()
        elif i == m - 1:
            tangent = (p - Vector(pts[-2])).normalized()
        else:
            tangent = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        # Outward normal from head center (0, 0, 1.58)
        out = (p - Vector((0.0, 0.0, 1.58)))
        out = (out - tangent * out.dot(tangent))
        if out.length < 1e-4:
            out = Vector((0, 0, 1))
        else:
            out.normalize()
        side = tangent.cross(out).normalized()
        ring = []
        for k in range(n_sides):
            ang = 2.0 * math.pi * k / n_sides
            # Lens-like section (wider tangentially along skull, slightly ridged outward)
            ring.append(p + side * (w * 0.5 * math.cos(ang)) + out * (th * 0.5 * math.sin(ang)))
        rings.append(ring)
    # Sharp pointed tip cap
    tip = Vector(pts[-1]) + (Vector(pts[-1]) - Vector(pts[-2])).normalized() * 0.012
    vr = add_loft(bm_target, rings, cap_start=True, cap_end=False, mat_idx=mat_idx)
    v_tip = bm_target.verts.new(tip)
    last_r = vr[-1]
    for k in range(n_sides):
        kn = (k + 1) % n_sides
        f = bm_target.faces.new((last_r[k], last_r[kn], v_tip))
        f.material_index = mat_idx

# Build ~40 layered wavy messy hair clumps!
# A. Top volume & crown clumps (reaching Z=1.70 and width 0.19 -> X=+-0.095)
dark_clumps = [
    # Crown top arching left (-X)
    ([(-0.015, -0.02, 1.682), (-0.045, -0.025, 1.696), (-0.075, -0.020, 1.675), (-0.092, -0.010, 1.625), (-0.095, -0.005, 1.575)],
     [0.032, 0.036, 0.034, 0.026, 0.012], [0.024, 0.028, 0.024, 0.018, 0.008]),
    ([(-0.018,  0.02, 1.682), (-0.050,  0.025, 1.698), (-0.082,  0.028, 1.668), (-0.095,  0.032, 1.610), (-0.092,  0.038, 1.545)],
     [0.034, 0.038, 0.034, 0.026, 0.012], [0.024, 0.028, 0.024, 0.018, 0.008]),
    ([(-0.010,  0.05, 1.675), (-0.040,  0.068, 1.685), (-0.070,  0.075, 1.645), (-0.082,  0.082, 1.575), (-0.078,  0.088, 1.505)],
     [0.032, 0.036, 0.032, 0.024, 0.012], [0.024, 0.026, 0.024, 0.018, 0.008]),

    # Crown top arching right (+X)
    ([(0.010,  0.03, 1.685), (0.045,  0.035, 1.698), (0.080,  0.032, 1.668), (0.095,  0.034, 1.610), (0.093,  0.040, 1.545)],
     [0.034, 0.038, 0.034, 0.026, 0.012], [0.024, 0.028, 0.024, 0.018, 0.008]),
    ([(0.020, -0.01, 1.680), (0.055, -0.012, 1.690), (0.085, -0.008, 1.655), (0.095,  0.000, 1.595), (0.092,  0.010, 1.530)],
     [0.032, 0.036, 0.032, 0.025, 0.012], [0.024, 0.026, 0.022, 0.016, 0.008]),
    ([(0.015,  0.06, 1.675), (0.048,  0.072, 1.682), (0.074,  0.080, 1.640), (0.084,  0.085, 1.570), (0.078,  0.092, 1.498)],
     [0.032, 0.036, 0.032, 0.024, 0.012], [0.024, 0.026, 0.022, 0.016, 0.008]),

    # Forehead & bangs (above eyebrows Z ~1.605, framing the face)
    ([(-0.022, -0.052, 1.678), (-0.036, -0.086, 1.650), (-0.044, -0.098, 1.622), (-0.040, -0.095, 1.598)],
     [0.026, 0.028, 0.022, 0.010], [0.020, 0.022, 0.016, 0.007]),
    ([(-0.012, -0.060, 1.675), (-0.018, -0.094, 1.646), (-0.014, -0.102, 1.620), (-0.008, -0.098, 1.602)],
     [0.024, 0.024, 0.018, 0.008], [0.018, 0.020, 0.014, 0.006]),
    ([(-0.038, -0.045, 1.670), (-0.062, -0.074, 1.638), (-0.072, -0.078, 1.598), (-0.076, -0.062, 1.555)],
     [0.028, 0.030, 0.024, 0.011], [0.020, 0.022, 0.018, 0.008]),
    ([(-0.048, -0.032, 1.662), (-0.074, -0.050, 1.620), (-0.084, -0.046, 1.568), (-0.082, -0.034, 1.515)],
     [0.028, 0.028, 0.022, 0.010], [0.020, 0.022, 0.016, 0.007]),

    # Right side (-X) covering ear down to jaw Z=1.50 (wavy flicked tips)
    ([(-0.055, -0.010, 1.652), (-0.085, -0.012, 1.600), (-0.090, -0.008, 1.545), (-0.094, -0.005, 1.500)],
     [0.030, 0.032, 0.026, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([(-0.058,  0.015, 1.648), (-0.086,  0.020, 1.595), (-0.090,  0.025, 1.540), (-0.096,  0.028, 1.498)],
     [0.030, 0.032, 0.025, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([(-0.054,  0.042, 1.642), (-0.080,  0.052, 1.585), (-0.084,  0.058, 1.535), (-0.088,  0.062, 1.495)],
     [0.030, 0.030, 0.024, 0.010], [0.022, 0.022, 0.018, 0.008]),
    # Mid-layer side flares (-X)
    ([(-0.065, -0.025, 1.625), (-0.088, -0.032, 1.578), (-0.092, -0.030, 1.535), (-0.084, -0.024, 1.502)],
     [0.024, 0.026, 0.020, 0.009], [0.018, 0.018, 0.014, 0.006]),
    ([(-0.068,  0.030, 1.615), (-0.090,  0.038, 1.568), (-0.096,  0.042, 1.525), (-0.102,  0.045, 1.498)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Left side (+X) covering ear down to jaw Z=1.50
    ([(0.048, -0.038, 1.655), (0.075, -0.052, 1.610), (0.084, -0.044, 1.558), (0.082, -0.032, 1.508)],
     [0.028, 0.028, 0.022, 0.010], [0.020, 0.022, 0.016, 0.007]),
    ([(0.056, -0.010, 1.652), (0.085, -0.012, 1.600), (0.090, -0.008, 1.545), (0.094, -0.004, 1.500)],
     [0.030, 0.032, 0.026, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([(0.058,  0.015, 1.648), (0.086,  0.020, 1.595), (0.090,  0.025, 1.540), (0.096,  0.028, 1.498)],
     [0.030, 0.032, 0.025, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([(0.054,  0.042, 1.642), (0.080,  0.052, 1.585), (0.084,  0.058, 1.535), (0.088,  0.062, 1.495)],
     [0.030, 0.030, 0.024, 0.010], [0.022, 0.022, 0.018, 0.008]),
    # Mid-layer side flares (+X)
    ([(0.065, -0.025, 1.625), (0.088, -0.032, 1.578), (0.092, -0.030, 1.535), (0.084, -0.024, 1.502)],
     [0.024, 0.026, 0.020, 0.009], [0.018, 0.018, 0.014, 0.006]),
    ([(0.068,  0.030, 1.615), (0.090,  0.038, 1.568), (0.096,  0.042, 1.525), (0.102,  0.045, 1.498)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Back upper & nape clumps (uneven points down to Z=1.48)
    ([(0.000,  0.068, 1.675), (0.000,  0.104, 1.625), (0.000,  0.108, 1.555), (-0.004,  0.102, 1.482)],
     [0.034, 0.036, 0.028, 0.012], [0.024, 0.026, 0.020, 0.008]),
    ([(-0.028,  0.064, 1.670), (-0.036,  0.098, 1.615), (-0.034,  0.102, 1.545), (-0.038,  0.098, 1.480)],
     [0.032, 0.034, 0.026, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([( 0.028,  0.064, 1.670), ( 0.036,  0.098, 1.615), ( 0.034,  0.102, 1.545), ( 0.038,  0.098, 1.480)],
     [0.032, 0.034, 0.026, 0.011], [0.022, 0.024, 0.018, 0.008]),
    ([(-0.052,  0.054, 1.655), (-0.066,  0.084, 1.595), (-0.064,  0.088, 1.535), (-0.068,  0.088, 1.485)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([( 0.052,  0.054, 1.655), ( 0.066,  0.084, 1.595), ( 0.064,  0.088, 1.535), ( 0.068,  0.088, 1.485)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),

    # Lower back staggered nape points (shorter tousled wisps at Z=1.48..1.52)
    ([(-0.016,  0.085, 1.575), (-0.018,  0.098, 1.530), (-0.022,  0.095, 1.482)],
     [0.024, 0.022, 0.009], [0.018, 0.016, 0.007]),
    ([( 0.016,  0.085, 1.575), ( 0.018,  0.098, 1.530), ( 0.022,  0.095, 1.482)],
     [0.024, 0.022, 0.009], [0.018, 0.016, 0.007]),
    ([(-0.044,  0.072, 1.565), (-0.048,  0.086, 1.520), (-0.052,  0.088, 1.486)],
     [0.024, 0.022, 0.009], [0.018, 0.016, 0.007]),
    ([( 0.044,  0.072, 1.565), ( 0.048,  0.086, 1.520), ( 0.052,  0.088, 1.486)],
     [0.024, 0.022, 0.009], [0.018, 0.016, 0.007]),

    # Tousled crown top spikes/waves for messy silhouette
    ([(-0.005, -0.035, 1.682), (-0.030, -0.052, 1.698), (-0.055, -0.062, 1.675), (-0.072, -0.065, 1.630)],
     [0.024, 0.026, 0.022, 0.010], [0.018, 0.020, 0.016, 0.008]),
    ([(-0.010,  0.005, 1.685), (-0.015,  0.015, 1.700), (-0.032,  0.042, 1.688), (-0.045,  0.075, 1.645)],
     [0.026, 0.028, 0.024, 0.012], [0.018, 0.020, 0.018, 0.008]),
    ([( 0.002,  0.000, 1.685), ( 0.005,  0.025, 1.700), ( 0.000,  0.062, 1.682), (-0.004,  0.090, 1.635)],
     [0.026, 0.028, 0.024, 0.012], [0.018, 0.020, 0.018, 0.008]),
]

for pts, ws, ths in dark_clumps:
    add_clump(bm_h, pts, ws, ths, mat_idx=0, n_sides=6)

# B. White streak clumps (~0.03 wide total):
#    Starts near parting (X=-0.015..-0.025), sweeps over forehead to the right of front view (+X)
#    AND continues back over crown so in back view it is visible on top slightly left of picture (+X)!
white_clumps = [
    # Main front-sweeping streak (visible in front, left-side, and slight peek in right-side)
    ([(-0.020, -0.048, 1.685), (0.008, -0.078, 1.676), (0.038, -0.088, 1.648), (0.058, -0.080, 1.608), (0.062, -0.068, 1.575)],
     [0.022, 0.026, 0.024, 0.018, 0.008], [0.018, 0.022, 0.020, 0.014, 0.006]),
    ([(0.000, -0.056, 1.680), (0.025, -0.085, 1.662), (0.052, -0.084, 1.628), (0.072, -0.068, 1.588), (0.076, -0.054, 1.555)],
     [0.018, 0.022, 0.020, 0.016, 0.007], [0.015, 0.018, 0.016, 0.012, 0.006]),
    # Crown-to-back white streak extension (visible in back view on top slightly to left of picture = +X)
    ([(-0.010, -0.032, 1.690), (0.012,  0.005, 1.700), (0.024,  0.045, 1.692), (0.028,  0.082, 1.662), (0.025,  0.100, 1.622)],
     [0.020, 0.024, 0.024, 0.020, 0.009], [0.016, 0.020, 0.020, 0.015, 0.007]),
]
for pts, ws, ths in white_clumps:
    add_clump(bm_h, pts, ws, ths, mat_idx=1, n_sides=6)

bmesh.ops.recalc_face_normals(bm_h, faces=bm_h.faces[:])
obj_hair = bpy.data.objects.get("Capelli")
bm_h.to_mesh(obj_hair.data)
bm_h.free()
obj_hair.data.materials.clear()
obj_hair.data.materials.append(mat_hair)
obj_hair.data.materials.append(mat_hair_white)
obj_hair.data.update()

# Smooth shading on head & hair & face details
for name in ("CorpoBase", "Capelli", "DettagliVolto"):
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.shade_smooth()

# Log triangle counts for Group 2
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ("CorpoBase", "DettagliVolto", "Capelli"):
    ob = bpy.data.objects.get(name)
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    log(f"{name}: tris={len(me.loop_triangles)}, X=({min(p.x for p in pts):.3f}..{max(p.x for p in pts):.3f}), Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
    ev.to_mesh_clear()

bpy.ops.wm.save_mainfile()
render_viste("rev_2")
