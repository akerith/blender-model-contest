import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 2 (v3): Head, face and hair (~5,200 tris), materials assigned BEFORE bm.to_mesh
# so multi-material indices (iris, sclera, brows, lips, white streak) are preserved!

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.6, metallic=0.0, spec=0.4):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        lin = tuple(srgb_to_lin(x) for x in col_srgb)
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat

mat_skin       = set_mat_srgb("Pelle", (0.85, 0.68, 0.58), roughness=0.58, spec=0.32)
mat_hair       = set_mat_srgb("CapelliScuri", (0.10, 0.08, 0.07), roughness=0.72, spec=0.22)
mat_hair_white = set_mat_srgb("CapelliBianchi", (0.80, 0.80, 0.78), roughness=0.62, spec=0.25)
mat_eye_white  = set_mat_srgb("OcchioBianco", (0.90, 0.89, 0.86), roughness=0.18, spec=0.45)
mat_iris       = set_mat_srgb("OcchioIride", (0.14, 0.08, 0.05), roughness=0.10, spec=0.65)
mat_lips       = set_mat_srgb("Labbra", (0.68, 0.45, 0.40), roughness=0.52, spec=0.30)
mat_mouth_line = set_mat_srgb("LineaBocca", (0.34, 0.19, 0.16), roughness=0.60, spec=0.15)

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

def make_limb_rings(p0, p1, r_list, n=12):
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

def apply_bm_with_mats(obj, bm, mats, smooth=True):
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = smooth
    obj.data.update()

# 1. CorpoBase: body + refined sculpted female head (chin 1.475 -> skull top 1.66, 0.15x0.19)
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
    ((0.0, 0.000, 1.445), 0.055, 0.053),
    ((0.0, 0.000, 1.495), 0.050, 0.050),
]
add_loft(bm, [make_oval(c, rx, ry, 20) for c, rx, ry in torso_specs])

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

head_z_profile = [
    (1.475, -0.012, 0.025, 0.032),
    (1.486, -0.014, 0.040, 0.050),
    (1.500, -0.013, 0.050, 0.065),
    (1.512, -0.011, 0.056, 0.073),
    (1.528, -0.009, 0.062, 0.080),
    (1.545, -0.007, 0.068, 0.085),
    (1.562, -0.005, 0.072, 0.089),
    (1.576, -0.004, 0.074, 0.092),
    (1.588, -0.003, 0.075, 0.094),
    (1.602, -0.002, 0.074, 0.095),
    (1.620,  0.001, 0.071, 0.092),
    (1.638,  0.004, 0.063, 0.083),
    (1.652,  0.007, 0.045, 0.062),
    (1.660,  0.008, 0.018, 0.024),
]

n_head = 36
head_rings = []
for z, cy, rx, ry in head_z_profile:
    ring = []
    for i in range(n_head):
        ang = 2.0 * math.pi * i / n_head
        x = rx * math.sin(ang)
        y = cy - ry * math.cos(ang)

        front_fac = max(0.0, math.cos(ang))
        if front_fac > 0.05:
            if z < 1.545:
                t_j = (1.545 - z) / (1.545 - 1.475)
                x *= (1.0 - 0.25 * t_j * (front_fac ** 1.4))

            for s in (-1.0, 1.0):
                sock = smooth_gauss(x - 0.0325 * s, z - 1.585, 0.017, 0.010)
                y += 0.0065 * sock

            brow = smooth_gauss(x, z - 1.601, 0.040, 0.008)
            y -= 0.003 * brow

            if 1.525 <= z <= 1.584:
                if z >= 1.536:
                    t_n = (1.584 - z) / (1.584 - 1.536)
                    nose_proj = 0.019 * (t_n ** 0.85) + 0.001
                    nose_w = 0.0045 + 0.0038 * (t_n ** 1.3)
                else:
                    t_u = (z - 1.525) / (1.536 - 1.525)
                    nose_proj = 0.020 * (t_u ** 1.4)
                    nose_w = 0.0075
                y -= nose_proj * math.exp(-0.5 * (x / nose_w) ** 2)

            for s in (-1.0, 1.0):
                cheek = smooth_gauss(x - 0.040 * s, z - 1.560, 0.016, 0.013)
                y -= 0.003 * cheek

            up_lip = smooth_gauss(x, z - 1.509, 0.018, 0.0035)
            lo_lip = smooth_gauss(x, z - 1.500, 0.016, 0.0040)
            y -= 0.0020 * up_lip + 0.0018 * lo_lip

            chin_pt = smooth_gauss(x, z - 1.480, 0.014, 0.008)
            y -= 0.003 * chin_pt

        ring.append(Vector((x, y, z)))
    head_rings.append(ring)

add_loft(bm, head_rings, cap_start=True, cap_end=True)

for s in (1.0, -1.0):
    ear_rings = [
        [Vector((0.068 * s, 0.002 + 0.009 * math.sin(a), 1.570 + 0.018 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.078 * s, 0.006 + 0.008 * math.sin(a), 1.570 + 0.016 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.080 * s, 0.008 + 0.005 * math.sin(a), 1.570 + 0.010 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
    ]
    add_loft(bm, ear_rings, cap_start=True, cap_end=True)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
apply_bm_with_mats(bpy.data.objects.get("CorpoBase"), bm, [mat_skin], smooth=True)

# 2. DettagliVolto: eyes, dark brows, closed lips (materials set BEFORE bm.to_mesh!)
bm_f = bmesh.new()

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

for s in (1.0, -1.0):
    eye_c = Vector((0.0325 * s, -0.0845, 1.585))
    # Sclera (mat_idx=3)
    res_s = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=10, radius=1.0,
        matrix=Matrix.Translation(eye_c) @ Matrix.Rotation(math.radians(-10 * s), 4, 'Z') @ Matrix.Diagonal((0.0140, 0.0075, 0.0058, 1.0))
    )
    tag_res(res_s["verts"], 3)

    # Iris (mat_idx=0)
    res_i = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=8, radius=1.0,
        matrix=Matrix.Translation(eye_c + Vector((-0.0005 * s, -0.0048, 0.0))) @ Matrix.Diagonal((0.0062, 0.0040, 0.0056, 1.0))
    )
    tag_res(res_i["verts"], 0)

    # Upper lash/eyelid (mat_idx=1)
    lash_pts = [
        Vector((0.0185 * s, -0.0870, 1.5845)),
        Vector((0.0255 * s, -0.0908, 1.5892)),
        Vector((0.0330 * s, -0.0912, 1.5898)),
        Vector((0.0410 * s, -0.0882, 1.5880)),
        Vector((0.0465 * s, -0.0825, 1.5845)),
    ]
    lash_rings = []
    for idx, p in enumerate(lash_pts):
        r = 0.0015 if 0 < idx < 4 else 0.0008
        lash_rings.append([p + Vector((0, r * math.cos(a), r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, lash_rings, cap_start=True, cap_end=True, mat_idx=1)

    # Straight dark eyebrows 0.012 above eyes, angled down towards nose (mat_idx=1)
    brow_pts = [
        (Vector((0.013 * s, -0.0935, 1.5945)), 0.0026, 0.0025),
        (Vector((0.024 * s, -0.0938, 1.5975)), 0.0026, 0.0023),
        (Vector((0.036 * s, -0.0898, 1.6005)), 0.0024, 0.0020),
        (Vector((0.049 * s, -0.0820, 1.6020)), 0.0018, 0.0014),
    ]
    brow_rings = []
    for p, ry, rz in brow_pts:
        brow_rings.append([p + Vector((0, ry * math.cos(a), rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, brow_rings, cap_start=True, cap_end=True, mat_idx=1)

# Lips + mouth line at Z=1.505, width 0.045 (mat_idx 2 & 4)
lip_xs = [-0.022, -0.013, -0.006, 0.0, 0.006, 0.013, 0.022]
lip_ys = [-0.0755, -0.0820, -0.0855, -0.0868, -0.0855, -0.0820, -0.0755]

for dz, rz_top in ((0.0020, 0.0022), (-0.0022, 0.0024)):
    l_rings = []
    for lx, ly in zip(lip_xs, lip_ys):
        f_w = max(0.30, 1.0 - (abs(lx) / 0.0235) ** 2)
        rz = rz_top * f_w
        ry = 0.0022 * f_w
        l_rings.append([Vector((lx, ly - 0.0008 - ry * math.cos(a), 1.505 + dz + rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, l_rings, cap_start=True, cap_end=True, mat_idx=2)

mline_rings = []
for lx, ly in zip(lip_xs, lip_ys):
    r = 0.0008 if abs(lx) < 0.018 else 0.0004
    mline_rings.append([Vector((lx, ly - 0.0022 - r * math.cos(a), 1.505 + r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
add_loft(bm_f, mline_rings, cap_start=True, cap_end=True, mat_idx=4)

bmesh.ops.recalc_face_normals(bm_f, faces=bm_f.faces[:])
apply_bm_with_mats(
    bpy.data.objects.get("DettagliVolto"), bm_f,
    [mat_iris, mat_hair, mat_lips, mat_eye_white, mat_mouth_line],
    smooth=True
)

# 3. Capelli: wavy short messy hair (<= 1.700 Z, 0.19 wide at top, side Z 1.50, nape Z 1.48)
#    >= 35 wavy clumps + clearly visible white streak (mat_idx=1)!
bm_h = bmesh.new()

cap_specs = [
    ((0.0, 0.015, 1.520), 0.068, 0.082),
    ((0.0, 0.012, 1.568), 0.074, 0.090),
    ((0.0, 0.008, 1.615), 0.075, 0.092),
    ((0.0, 0.008, 1.648), 0.068, 0.084),
    ((0.0, 0.010, 1.672), 0.046, 0.058),
    ((0.0, 0.012, 1.682), 0.018, 0.024),
]
add_loft(bm_h, [make_oval(c, rx, ry, 20) for c, rx, ry in cap_specs], cap_start=True, cap_end=True, mat_idx=0)

def add_clump(bm_target, pts, widths, thicknesses, mat_idx=0, n_sides=6):
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
        out = p - Vector((0.0, 0.0, 1.575))
        out = out - tangent * out.dot(tangent)
        if out.length < 1e-4:
            out = Vector((0, 0, 1))
        else:
            out.normalize()
        side = tangent.cross(out).normalized()
        ring = []
        for k in range(n_sides):
            ang = 2.0 * math.pi * k / n_sides
            ring.append(p + side * (w * 0.5 * math.cos(ang)) + out * (th * 0.5 * math.sin(ang)))
        rings.append(ring)
    tip = Vector(pts[-1]) + (Vector(pts[-1]) - Vector(pts[-2])).normalized() * 0.008
    tip.z = min(tip.z, 1.698)
    vr = add_loft(bm_target, rings, cap_start=True, cap_end=False, mat_idx=mat_idx)
    v_tip = bm_target.verts.new(tip)
    last_r = vr[-1]
    for k in range(n_sides):
        kn = (k + 1) % n_sides
        f = bm_target.faces.new((last_r[k], last_r[kn], v_tip))
        f.material_index = mat_idx

dark_clumps = [
    # Crown sweeping left (-X)
    ([(-0.016, -0.025, 1.675), (-0.045, -0.025, 1.688), (-0.072, -0.020, 1.662), (-0.088, -0.012, 1.615), (-0.098, -0.005, 1.562)],
     [0.032, 0.035, 0.032, 0.024, 0.010], [0.020, 0.022, 0.020, 0.016, 0.007]),
    ([(-0.016,  0.015, 1.676), (-0.048,  0.022, 1.690), (-0.078,  0.025, 1.658), (-0.092,  0.030, 1.602), (-0.098,  0.036, 1.542)],
     [0.034, 0.036, 0.032, 0.024, 0.010], [0.022, 0.022, 0.020, 0.016, 0.007]),
    ([(-0.012,  0.050, 1.670), (-0.040,  0.066, 1.676), (-0.068,  0.074, 1.635), (-0.080,  0.080, 1.570), (-0.082,  0.086, 1.505)],
     [0.032, 0.034, 0.030, 0.022, 0.010], [0.020, 0.022, 0.020, 0.016, 0.007]),

    # Crown sweeping right (+X, leaving outer crown open for white streak)
    ([(0.028,  0.032, 1.670), (0.056,  0.040, 1.678), (0.082,  0.038, 1.648), (0.092,  0.042, 1.592), (0.096,  0.048, 1.535)],
     [0.030, 0.032, 0.028, 0.022, 0.010], [0.018, 0.020, 0.018, 0.014, 0.007]),
    ([(0.038, -0.005, 1.662), (0.066,  0.000, 1.666), (0.086,  0.006, 1.632), (0.094,  0.012, 1.576), (0.096,  0.020, 1.522)],
     [0.028, 0.030, 0.026, 0.020, 0.010], [0.018, 0.020, 0.018, 0.014, 0.007]),
    ([(0.026,  0.060, 1.664), (0.054,  0.070, 1.670), (0.076,  0.078, 1.628), (0.084,  0.082, 1.560), (0.082,  0.088, 1.498)],
     [0.030, 0.032, 0.028, 0.022, 0.010], [0.018, 0.020, 0.018, 0.014, 0.007]),

    # Forehead & messy bangs (framing brow without hiding eyes!)
    ([(-0.022, -0.052, 1.672), (-0.034, -0.084, 1.648), (-0.044, -0.094, 1.624), (-0.048, -0.090, 1.608)],
     [0.026, 0.028, 0.022, 0.010], [0.018, 0.020, 0.015, 0.007]),
    ([(-0.012, -0.058, 1.670), (-0.018, -0.090, 1.646), (-0.018, -0.096, 1.624), (-0.014, -0.094, 1.608)],
     [0.022, 0.022, 0.016, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(-0.036, -0.044, 1.665), (-0.060, -0.070, 1.632), (-0.072, -0.072, 1.592), (-0.078, -0.055, 1.552)],
     [0.028, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([(-0.048, -0.028, 1.656), (-0.074, -0.044, 1.615), (-0.084, -0.038, 1.562), (-0.088, -0.024, 1.512)],
     [0.028, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),

    # Right side (-X) wavy flicked locks to jaw Z=1.50 (flaring slightly out at tips like reference)
    ([(-0.054, -0.010, 1.648), (-0.082, -0.012, 1.598), (-0.088, -0.008, 1.545), (-0.100, -0.004, 1.502)],
     [0.030, 0.032, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.056,  0.015, 1.645), (-0.084,  0.020, 1.592), (-0.088,  0.025, 1.540), (-0.102,  0.028, 1.500)],
     [0.030, 0.032, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.052,  0.040, 1.640), (-0.078,  0.050, 1.582), (-0.082,  0.056, 1.535), (-0.092,  0.062, 1.498)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.020, 0.016, 0.007]),
    ([(-0.064, -0.020, 1.622), (-0.086, -0.024, 1.576), (-0.090, -0.022, 1.535), (-0.096, -0.018, 1.505)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(-0.066,  0.028, 1.612), (-0.088,  0.036, 1.566), (-0.094,  0.042, 1.528), (-0.106,  0.046, 1.502)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Left side (+X) wavy flicked locks to jaw Z=1.50
    ([(0.050, -0.034, 1.640), (0.076, -0.046, 1.598), (0.084, -0.038, 1.550), (0.090, -0.026, 1.508)],
     [0.026, 0.026, 0.020, 0.009], [0.018, 0.018, 0.014, 0.006]),
    ([(0.054, -0.010, 1.648), (0.082, -0.012, 1.598), (0.088, -0.008, 1.545), (0.100, -0.004, 1.502)],
     [0.030, 0.032, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(0.056,  0.015, 1.645), (0.084,  0.020, 1.592), (0.088,  0.025, 1.540), (0.102,  0.028, 1.500)],
     [0.030, 0.032, 0.024, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(0.052,  0.040, 1.640), (0.078,  0.050, 1.582), (0.082,  0.056, 1.535), (0.092,  0.062, 1.498)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.020, 0.016, 0.007]),
    ([(0.064, -0.020, 1.622), (0.086, -0.024, 1.576), (0.090, -0.022, 1.535), (0.096, -0.018, 1.505)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(0.066,  0.028, 1.612), (0.088,  0.036, 1.566), (0.094,  0.042, 1.528), (0.106,  0.046, 1.502)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Back wavy layered locks ending cleanly at nape Z=1.48
    ([(0.000,  0.064, 1.666), (-0.002,  0.096, 1.615), (-0.004,  0.100, 1.550), (-0.006,  0.086, 1.482)],
     [0.034, 0.035, 0.028, 0.011], [0.022, 0.024, 0.018, 0.007]),
    ([(-0.026,  0.060, 1.660), (-0.034,  0.092, 1.608), (-0.034,  0.096, 1.545), (-0.036,  0.082, 1.480)],
     [0.032, 0.032, 0.026, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([( 0.026,  0.060, 1.660), ( 0.034,  0.092, 1.608), ( 0.034,  0.096, 1.545), ( 0.036,  0.082, 1.480)],
     [0.032, 0.032, 0.026, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.050,  0.050, 1.646), (-0.064,  0.078, 1.590), (-0.064,  0.082, 1.535), (-0.066,  0.076, 1.484)],
     [0.028, 0.030, 0.024, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([( 0.050,  0.050, 1.646), ( 0.064,  0.078, 1.590), ( 0.064,  0.082, 1.535), ( 0.066,  0.076, 1.484)],
     [0.028, 0.030, 0.024, 0.010], [0.018, 0.020, 0.016, 0.007]),

    # Lower nape wisps
    ([(-0.014,  0.080, 1.572), (-0.016,  0.092, 1.528), (-0.020,  0.084, 1.482)],
     [0.024, 0.022, 0.009], [0.016, 0.015, 0.006]),
    ([( 0.014,  0.080, 1.572), ( 0.016,  0.092, 1.528), ( 0.020,  0.084, 1.482)],
     [0.024, 0.022, 0.009], [0.016, 0.015, 0.006]),
    ([(-0.042,  0.068, 1.562), (-0.046,  0.080, 1.520), (-0.050,  0.074, 1.486)],
     [0.022, 0.020, 0.009], [0.016, 0.014, 0.006]),
    ([( 0.042,  0.068, 1.562), ( 0.046,  0.080, 1.520), ( 0.050,  0.074, 1.486)],
     [0.022, 0.020, 0.009], [0.016, 0.014, 0.006]),

    # Top tousled crown locks (max Z 1.694)
    ([(-0.008, -0.038, 1.676), (-0.032, -0.054, 1.690), (-0.056, -0.062, 1.666), (-0.072, -0.060, 1.622)],
     [0.024, 0.026, 0.022, 0.010], [0.016, 0.018, 0.015, 0.007]),
    ([(-0.010,  0.005, 1.680), (-0.018,  0.020, 1.692), (-0.035,  0.045, 1.680), (-0.048,  0.074, 1.638)],
     [0.026, 0.028, 0.024, 0.011], [0.018, 0.018, 0.016, 0.007]),
    ([(-0.002,  0.002, 1.680), (-0.005,  0.028, 1.692), (-0.008,  0.062, 1.674), (-0.010,  0.086, 1.628)],
     [0.026, 0.026, 0.022, 0.011], [0.018, 0.018, 0.015, 0.007]),
]
for pts, ws, ths in dark_clumps:
    add_clump(bm_h, pts, ws, ths, mat_idx=0, n_sides=6)

# Prominent White Streak (mat_idx=1) clearly ON TOP of the dark crown & bangs!
white_clumps = [
    ([(-0.012, -0.052, 1.682), (0.014, -0.082, 1.672), (0.044, -0.090, 1.644), (0.064, -0.080, 1.605), (0.068, -0.064, 1.568)],
     [0.022, 0.026, 0.024, 0.018, 0.009], [0.018, 0.020, 0.018, 0.014, 0.007]),
    ([(0.006, -0.058, 1.678), (0.030, -0.086, 1.658), (0.056, -0.086, 1.622), (0.074, -0.068, 1.582), (0.080, -0.050, 1.548)],
     [0.018, 0.022, 0.020, 0.016, 0.008], [0.015, 0.018, 0.016, 0.012, 0.006]),
    ([(-0.006, -0.040, 1.686), (0.014, -0.004, 1.695), (0.024,  0.038, 1.690), (0.028,  0.076, 1.664), (0.026,  0.098, 1.618)],
     [0.022, 0.028, 0.026, 0.022, 0.010], [0.018, 0.022, 0.020, 0.016, 0.008]),
]
for pts, ws, ths in white_clumps:
    add_clump(bm_h, pts, ws, ths, mat_idx=1, n_sides=6)

bmesh.ops.recalc_face_normals(bm_h, faces=bm_h.faces[:])
apply_bm_with_mats(
    bpy.data.objects.get("Capelli"), bm_h,
    [mat_hair, mat_hair_white],
    smooth=True
)

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
