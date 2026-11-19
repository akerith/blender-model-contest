import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Group 2 (refined): Head, face and hair (~5,500 tris), sRGB->Linear accurate colors,
# visible white streak, refined nose/eyes/mouth/brows, smooth shading via mesh data.

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.6, metallic=0.0, spec=0.5):
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

# 2.3 Skin, eyes, eyebrows, hair, white streak (exact spec sRGB colors)
mat_skin       = set_mat_srgb("Pelle", (0.85, 0.68, 0.58), roughness=0.58, spec=0.35)
mat_hair       = set_mat_srgb("CapelliScuri", (0.10, 0.08, 0.07), roughness=0.72, spec=0.25)
mat_hair_white = set_mat_srgb("CapelliBianchi", (0.80, 0.80, 0.78), roughness=0.62, spec=0.28)
mat_eye_white  = set_mat_srgb("OcchioBianco", (0.90, 0.89, 0.86), roughness=0.18, spec=0.5)
mat_iris       = set_mat_srgb("OcchioIride", (0.14, 0.08, 0.05), roughness=0.10, spec=0.7)
mat_lips       = set_mat_srgb("Labbra", (0.64, 0.42, 0.38), roughness=0.52, spec=0.35)
mat_mouth_line = set_mat_srgb("LineaBocca", (0.28, 0.15, 0.13), roughness=0.60, spec=0.2)

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

# 1. CorpoBase: Group 1 body + refined sculpted female head (chin 1.475 -> skull top 1.66, 0.15x0.19)
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

# Head mesh: 0.15 wide (rx=0.075), 0.19 deep (ry=0.095), chin Z=1.475 -> skull Z=1.66
head_z_profile = [
    (1.475, -0.012, 0.026, 0.034), # rounded small chin tip
    (1.486, -0.014, 0.042, 0.052), # chin-jaw
    (1.500, -0.013, 0.052, 0.066), # lower lip
    (1.512, -0.011, 0.058, 0.074), # upper lip
    (1.528, -0.009, 0.064, 0.081), # jaw / philtrum
    (1.545, -0.007, 0.069, 0.086), # lower cheek
    (1.562, -0.005, 0.073, 0.090), # cheekbones
    (1.576, -0.004, 0.074, 0.092), # under-eye
    (1.588, -0.003, 0.075, 0.094), # eye level (0.15 wide)
    (1.602, -0.002, 0.074, 0.095), # brow (0.19 deep)
    (1.620,  0.001, 0.071, 0.092), # forehead
    (1.638,  0.004, 0.063, 0.083), # upper forehead
    (1.652,  0.007, 0.045, 0.062), # crown
    (1.660,  0.008, 0.018, 0.024), # skull top (1.66)
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
            # Narrower egg taper towards chin
            if z < 1.545:
                t_j = (1.545 - z) / (1.545 - 1.475)
                x *= (1.0 - 0.24 * t_j * (front_fac ** 1.4))

            # Subtle eye socket depression (X=+-0.0325, Z=1.585)
            for s in (-1.0, 1.0):
                sock = smooth_gauss(x - 0.0325 * s, z - 1.585, 0.017, 0.010)
                y += 0.0065 * sock

            # Subtle brow ridge (Z=1.600)
            brow = smooth_gauss(x, z - 1.601, 0.040, 0.008)
            y -= 0.003 * brow

            # Crisp refined nose wedge: Z=1.58 down to Z=1.53, sticking out 0.020
            if 1.525 <= z <= 1.584:
                if z >= 1.536:
                    t_n = (1.584 - z) / (1.584 - 1.536)
                    nose_proj = 0.0195 * (t_n ** 0.85) + 0.001
                    nose_w = 0.0045 + 0.0040 * (t_n ** 1.3)
                else:
                    t_u = (z - 1.525) / (1.536 - 1.525)
                    nose_proj = 0.0205 * (t_u ** 1.4)
                    nose_w = 0.0080
                y -= nose_proj * math.exp(-0.5 * (x / nose_w) ** 2)

            # Cheekbone fullness
            for s in (-1.0, 1.0):
                cheek = smooth_gauss(x - 0.040 * s, z - 1.560, 0.016, 0.013)
                y -= 0.003 * cheek

            # Subtle lips contour (Z=1.505)
            up_lip = smooth_gauss(x, z - 1.509, 0.018, 0.0035)
            lo_lip = smooth_gauss(x, z - 1.500, 0.016, 0.0040)
            y -= 0.0025 * up_lip + 0.0022 * lo_lip

            # Chin tip projection
            chin_pt = smooth_gauss(x, z - 1.480, 0.014, 0.008)
            y -= 0.0035 * chin_pt

        ring.append(Vector((x, y, z)))
    head_rings.append(ring)

add_loft(bm, head_rings, cap_start=True, cap_end=True)

# Ears (Z 1.55 to 1.59, Y=0.0)
for s in (1.0, -1.0):
    ear_rings = [
        [Vector((0.068 * s, 0.002 + 0.009 * math.sin(a), 1.570 + 0.018 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.078 * s, 0.006 + 0.008 * math.sin(a), 1.570 + 0.016 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
        [Vector((0.080 * s, 0.008 + 0.005 * math.sin(a), 1.570 + 0.010 * math.cos(a))) for a in [2*math.pi*i/10 for i in range(10)]],
    ]
    add_loft(bm, ear_rings, cap_start=True, cap_end=True)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
obj_body = bpy.data.objects.get("CorpoBase")
bm.to_mesh(obj_body.data)
bm.free()
obj_body.data.materials.clear()
obj_body.data.materials.append(mat_skin)
for p in obj_body.data.polygons:
    p.use_smooth = True
obj_body.data.update()

# 2. DettagliVolto: clear expressive almond eyes set slightly into sockets, dark determined brows, closed lips
bm_f = bmesh.new()

def tag_res(verts_list, mat_idx):
    vset = set(verts_list)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

for s in (1.0, -1.0):
    # Eyes at Z=1.585, X=+-0.0325 (0.065 apart), 0.03 wide, set neatly in socket
    eye_c = Vector((0.0325 * s, -0.0855, 1.585))
    res_s = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=10, radius=1.0,
        matrix=Matrix.Translation(eye_c) @ Matrix.Rotation(math.radians(-12 * s), 4, 'Z') @ Matrix.Diagonal((0.0145, 0.0075, 0.0062, 1.0))
    )
    tag_res(res_s["verts"], 3)

    # Dark brown iris (slightly larger so it reads clearly!)
    res_i = bmesh.ops.create_uvsphere(
        bm_f, u_segments=14, v_segments=8, radius=1.0,
        matrix=Matrix.Translation(eye_c + Vector((-0.001 * s, -0.0046, 0.0))) @ Matrix.Diagonal((0.0068, 0.0042, 0.0060, 1.0))
    )
    tag_res(res_i["verts"], 0)

    # Upper & lower dark lash/eyelid rim framing the almond eye
    lash_pts = [
        Vector((0.0185 * s, -0.0875, 1.5850)),
        Vector((0.0255 * s, -0.0912, 1.5898)),
        Vector((0.0330 * s, -0.0915, 1.5905)),
        Vector((0.0410 * s, -0.0885, 1.5885)),
        Vector((0.0468 * s, -0.0830, 1.5850)),
    ]
    lash_rings = []
    for idx, p in enumerate(lash_pts):
        r = 0.0017 if 0 < idx < 4 else 0.0009
        lash_rings.append([p + Vector((0, r * math.cos(a), r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, lash_rings, cap_start=True, cap_end=True, mat_idx=1)

    # Straight dark eyebrows 0.012 above eyes, angled down towards nose (serious determined look)
    brow_pts = [
        (Vector((0.013 * s, -0.0938, 1.5945)), 0.0028, 0.0026),
        (Vector((0.024 * s, -0.0942, 1.5975)), 0.0028, 0.0024),
        (Vector((0.036 * s, -0.0902, 1.6005)), 0.0026, 0.0022),
        (Vector((0.049 * s, -0.0825, 1.6020)), 0.0020, 0.0015),
    ]
    brow_rings = []
    for p, ry, rz in brow_pts:
        brow_rings.append([p + Vector((0, ry * math.cos(a), rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, brow_rings, cap_start=True, cap_end=True, mat_idx=1)

# Closed straight mouth at Z=1.505, 0.045 wide (sitting cleanly in front of skin surface)
lip_xs = [-0.0225, -0.014, -0.006, 0.0, 0.006, 0.014, 0.0225]
lip_ys = [-0.0765, -0.0830, -0.0865, -0.0878, -0.0865, -0.0830, -0.0765]

# Lips body slightly proud of face surface
for dz, rz_top in ((0.0022, 0.0024), (-0.0025, 0.0026)):
    l_rings = []
    for lx, ly in zip(lip_xs, lip_ys):
        f_w = max(0.35, 1.0 - (abs(lx) / 0.024) ** 2)
        rz = rz_top * f_w
        ry = 0.0024 * f_w
        l_rings.append([Vector((lx, ly - 0.0012 - ry * math.cos(a), 1.505 + dz + rz * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
    add_loft(bm_f, l_rings, cap_start=True, cap_end=True, mat_idx=2)

# Closed straight mouth seam line (mat_idx=4)
mline_rings = []
for lx, ly in zip(lip_xs, lip_ys):
    r = 0.0011 if abs(lx) < 0.02 else 0.0006
    mline_rings.append([Vector((lx, ly - 0.0028 - r * math.cos(a), 1.505 + r * math.sin(a))) for a in [2*math.pi*k/6 for k in range(6)]])
add_loft(bm_f, mline_rings, cap_start=True, cap_end=True, mat_idx=4)

bmesh.ops.recalc_face_normals(bm_f, faces=bm_f.faces[:])
obj_face = bpy.data.objects.get("DettagliVolto")
bm_f.to_mesh(obj_face.data)
bm_f.free()
obj_face.data.materials.clear()
for m in (mat_iris, mat_hair, mat_lips, mat_eye_white, mat_mouth_line):
    obj_face.data.materials.append(m)
for p in obj_face.data.polygons:
    p.use_smooth = True
obj_face.data.update()

# 3. Capelli: messy, layered wavy short hair (<= 1.700 Z, 0.19 wide at top, side Z 1.50, nape Z 1.48)
#    >= 35 distinct tapered wavy clumps + prominent white streak clearly visible on top layer!
bm_h = bmesh.new()

# Tight under-cap (well inside clumps, max Z 1.682)
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
    tip = Vector(pts[-1]) + (Vector(pts[-1]) - Vector(pts[-2])).normalized() * 0.010
    tip.z = min(tip.z, 1.698)
    vr = add_loft(bm_target, rings, cap_start=True, cap_end=False, mat_idx=mat_idx)
    v_tip = bm_target.verts.new(tip)
    last_r = vr[-1]
    for k in range(n_sides):
        kn = (k + 1) % n_sides
        f = bm_target.faces.new((last_r[k], last_r[kn], v_tip))
        f.material_index = mat_idx

# Dark wavy clumps (38 clumps, max Z <= 1.698)
dark_clumps = [
    # Top crown sweeping left (-X)
    ([(-0.015, -0.025, 1.676), (-0.045, -0.025, 1.690), (-0.072, -0.020, 1.665), (-0.088, -0.012, 1.615), (-0.095, -0.005, 1.560)],
     [0.032, 0.035, 0.032, 0.024, 0.010], [0.020, 0.024, 0.022, 0.016, 0.007]),
    ([(-0.016,  0.015, 1.678), (-0.048,  0.022, 1.692), (-0.078,  0.025, 1.660), (-0.092,  0.030, 1.602), (-0.094,  0.036, 1.538)],
     [0.034, 0.036, 0.032, 0.024, 0.010], [0.022, 0.024, 0.022, 0.016, 0.007]),
    ([(-0.012,  0.050, 1.670), (-0.040,  0.066, 1.678), (-0.068,  0.074, 1.635), (-0.080,  0.080, 1.570), (-0.078,  0.086, 1.502)],
     [0.032, 0.034, 0.030, 0.022, 0.010], [0.020, 0.022, 0.020, 0.016, 0.007]),

    # Top crown sweeping right (+X, leaving outer track clear for white streak!)
    ([(0.018,  0.035, 1.675), (0.050,  0.042, 1.685), (0.080,  0.040, 1.652), (0.092,  0.042, 1.595), (0.092,  0.046, 1.532)],
     [0.032, 0.034, 0.030, 0.024, 0.010], [0.020, 0.022, 0.020, 0.016, 0.007]),
    ([(0.032, -0.005, 1.668), (0.062, -0.002, 1.672), (0.086,  0.004, 1.638), (0.094,  0.010, 1.580), (0.092,  0.018, 1.520)],
     [0.030, 0.032, 0.028, 0.022, 0.010], [0.020, 0.022, 0.018, 0.014, 0.007]),
    ([(0.020,  0.062, 1.668), (0.050,  0.072, 1.674), (0.074,  0.080, 1.630), (0.082,  0.084, 1.562), (0.078,  0.088, 1.495)],
     [0.030, 0.032, 0.028, 0.022, 0.010], [0.020, 0.022, 0.020, 0.014, 0.007]),

    # Forehead & messy bangs (framing brow Z ~1.605)
    ([(-0.022, -0.052, 1.672), (-0.034, -0.084, 1.648), (-0.042, -0.095, 1.622), (-0.038, -0.092, 1.602)],
     [0.026, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([(-0.012, -0.058, 1.670), (-0.018, -0.090, 1.644), (-0.016, -0.098, 1.620), (-0.010, -0.094, 1.604)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(-0.036, -0.044, 1.665), (-0.058, -0.072, 1.634), (-0.068, -0.076, 1.595), (-0.072, -0.062, 1.552)],
     [0.028, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([(-0.046, -0.030, 1.658), (-0.072, -0.048, 1.618), (-0.080, -0.044, 1.565), (-0.080, -0.032, 1.512)],
     [0.028, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),

    # Right side (-X) wavy layered locks covering ear down to jaw Z=1.50
    ([(-0.054, -0.010, 1.648), (-0.082, -0.012, 1.598), (-0.088, -0.008, 1.545), (-0.096, -0.006, 1.500)],
     [0.030, 0.032, 0.025, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.056,  0.015, 1.645), (-0.084,  0.020, 1.592), (-0.088,  0.025, 1.540), (-0.098,  0.028, 1.498)],
     [0.030, 0.032, 0.025, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.052,  0.040, 1.640), (-0.078,  0.050, 1.582), (-0.082,  0.056, 1.535), (-0.088,  0.062, 1.495)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.020, 0.016, 0.007]),
    ([(-0.064, -0.024, 1.622), (-0.086, -0.030, 1.576), (-0.088, -0.028, 1.532), (-0.078, -0.022, 1.502)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(-0.066,  0.028, 1.612), (-0.088,  0.036, 1.566), (-0.094,  0.042, 1.525), (-0.104,  0.046, 1.498)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Left side (+X) wavy layered locks covering ear down to jaw Z=1.50
    ([(0.048, -0.036, 1.645), (0.074, -0.050, 1.602), (0.082, -0.042, 1.552), (0.080, -0.030, 1.505)],
     [0.028, 0.028, 0.022, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([(0.054, -0.010, 1.648), (0.082, -0.012, 1.598), (0.088, -0.008, 1.545), (0.096, -0.005, 1.500)],
     [0.030, 0.032, 0.025, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(0.056,  0.015, 1.645), (0.084,  0.020, 1.592), (0.088,  0.025, 1.540), (0.098,  0.028, 1.498)],
     [0.030, 0.032, 0.025, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(0.052,  0.040, 1.640), (0.078,  0.050, 1.582), (0.082,  0.056, 1.535), (0.088,  0.062, 1.495)],
     [0.028, 0.030, 0.024, 0.010], [0.020, 0.020, 0.016, 0.007]),
    ([(0.064, -0.024, 1.622), (0.086, -0.030, 1.576), (0.088, -0.028, 1.532), (0.078, -0.022, 1.502)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),
    ([(0.066,  0.028, 1.612), (0.088,  0.036, 1.566), (0.094,  0.042, 1.525), (0.104,  0.046, 1.498)],
     [0.024, 0.024, 0.018, 0.008], [0.016, 0.018, 0.014, 0.006]),

    # Back wavy layered locks ending at nape Z=1.48 (curving naturally along head, not sticking straight out)
    ([(0.000,  0.064, 1.668), (-0.002,  0.098, 1.615), (-0.004,  0.102, 1.550), (-0.006,  0.092, 1.482)],
     [0.034, 0.035, 0.028, 0.011], [0.022, 0.024, 0.018, 0.007]),
    ([(-0.026,  0.060, 1.662), (-0.034,  0.094, 1.608), (-0.034,  0.098, 1.545), (-0.036,  0.088, 1.480)],
     [0.032, 0.032, 0.026, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([( 0.026,  0.060, 1.662), ( 0.034,  0.094, 1.608), ( 0.034,  0.098, 1.545), ( 0.036,  0.088, 1.480)],
     [0.032, 0.032, 0.026, 0.010], [0.020, 0.022, 0.018, 0.007]),
    ([(-0.050,  0.050, 1.648), (-0.064,  0.080, 1.590), (-0.064,  0.084, 1.535), (-0.066,  0.080, 1.484)],
     [0.028, 0.030, 0.024, 0.010], [0.018, 0.020, 0.016, 0.007]),
    ([( 0.050,  0.050, 1.648), ( 0.064,  0.080, 1.590), ( 0.064,  0.084, 1.535), ( 0.066,  0.080, 1.484)],
     [0.028, 0.030, 0.024, 0.010], [0.018, 0.020, 0.016, 0.007]),

    # Lower nape wisps (staggered)
    ([(-0.014,  0.082, 1.572), (-0.016,  0.094, 1.528), (-0.020,  0.088, 1.482)],
     [0.024, 0.022, 0.009], [0.016, 0.015, 0.006]),
    ([( 0.014,  0.082, 1.572), ( 0.016,  0.094, 1.528), ( 0.020,  0.088, 1.482)],
     [0.024, 0.022, 0.009], [0.016, 0.015, 0.006]),
    ([(-0.042,  0.068, 1.562), (-0.046,  0.082, 1.520), (-0.050,  0.078, 1.486)],
     [0.022, 0.020, 0.009], [0.016, 0.014, 0.006]),
    ([( 0.042,  0.068, 1.562), ( 0.046,  0.082, 1.520), ( 0.050,  0.078, 1.486)],
     [0.022, 0.020, 0.009], [0.016, 0.014, 0.006]),

    # Top tousled locks (max Z 1.696, adding organic silhouette break-up)
    ([(-0.008, -0.038, 1.678), (-0.032, -0.054, 1.692), (-0.056, -0.062, 1.668), (-0.072, -0.062, 1.622)],
     [0.024, 0.026, 0.022, 0.010], [0.016, 0.018, 0.015, 0.007]),
    ([(-0.010,  0.005, 1.682), (-0.018,  0.020, 1.694), (-0.035,  0.045, 1.682), (-0.048,  0.074, 1.638)],
     [0.026, 0.028, 0.024, 0.011], [0.018, 0.018, 0.016, 0.007]),
    ([(-0.002,  0.002, 1.682), (-0.005,  0.028, 1.694), (-0.008,  0.062, 1.676), (-0.010,  0.088, 1.628)],
     [0.026, 0.026, 0.022, 0.011], [0.018, 0.018, 0.015, 0.007]),
]

for pts, ws, ths in dark_clumps:
    add_clump(bm_h, pts, ws, ths, mat_idx=0, n_sides=6)

# Prominent White Streak clumps (~0.03 wide total) placed OUTSIDE the dark layer so they are cleanly visible!
# Starts near parting (X=-0.012) and sweeps over forehead to her left (+X, right of front drawing)
# AND goes back over crown slightly on +X (left of back drawing)!
white_clumps = [
    # Front-sweeping white streak (prominent in front and left-side views)
    ([(-0.014, -0.052, 1.685), (0.012, -0.082, 1.676), (0.042, -0.092, 1.648), (0.062, -0.082, 1.608), (0.064, -0.068, 1.572)],
     [0.022, 0.026, 0.024, 0.018, 0.009], [0.018, 0.020, 0.018, 0.014, 0.007]),
    ([(0.004, -0.058, 1.682), (0.028, -0.086, 1.662), (0.054, -0.088, 1.625), (0.072, -0.070, 1.585), (0.076, -0.054, 1.550)],
     [0.018, 0.022, 0.020, 0.016, 0.008], [0.015, 0.018, 0.016, 0.012, 0.006]),
    # Crown-to-back white streak (visibly sitting ON TOP of dark crown from Z=1.698 down to back Y=+0.095!)
    ([(-0.008, -0.040, 1.688), (0.012, -0.004, 1.698), (0.024,  0.038, 1.694), (0.028,  0.076, 1.668), (0.026,  0.100, 1.622)],
     [0.022, 0.028, 0.026, 0.022, 0.010], [0.018, 0.022, 0.020, 0.016, 0.008]),
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
for p in obj_hair.data.polygons:
    p.use_smooth = True
obj_hair.data.update()

# Log Group 2 info
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
