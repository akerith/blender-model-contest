import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ==============================================================================
# GROUP 7 - Waist gear: rope, pouches, cases (rev_7) + Shoulder cape sleeve fix
# - 7.1 Coiled rope on RIGHT hip (-X): 4 overlapping loops of beige rope
#   RGB (0.70, 0.62, 0.47), thickness 0.015, hanging from lower belt at X -0.17,
#   Z 0.98, reaching down to Z 0.72, oval loops ~0.16-0.24 high and 0.10 wide,
#   real 3-strand twisted cord geometry.
# - 7.2 Right-hip canister: brass and leather cylinder lying almost horizontal,
#   0.20 long, 0.07 across, centre at X -0.24, Z 0.90, Y -0.03, with brass end
#   caps and two brass bands (RGB (0.62, 0.45, 0.20), metallic 1.0, roughness 0.35).
# - 7.3 Round leather pouch on right hip above canister: flattened sphere
#   0.09 x 0.06 x 0.08 with a flap, centre X -0.20, Z 0.99.
# - 7.4 Map tube on LEFT hip (+X): tall cylinder hanging vertically from lower belt,
#   0.45 long, 0.075 across, from Z 0.98 down to Z 0.53, centre X +0.22, Y -0.02;
#   brown leather body, brass cap at top and bottom (each 0.04 high), two leather
#   straps around it; next to it on the outside (+X) a second thinner cylinder
#   0.35 long, 0.05 across.
# - 7.5 Torn piece of cream cloth hanging from lower belt on her left, between
#   map tube and leg: 0.07 wide, from Z 0.98 down to Z 0.62, ragged lower end.
# - 7.6 Three small brown leather pouches along the belt, each 0.06 x 0.05 x 0.03,
#   at the back and on the sides of the belt.
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

mat_corda = set_spec_mat("Mat_Corda", (0.70, 0.62, 0.47), (0.56, 0.47, 0.33), rough=0.88)
mat_ottone = set_spec_mat("Mat_Ottone", (0.62, 0.45, 0.20), (0.58, 0.40, 0.16), rough=0.35, metal=1.0)
mat_cuoio_medio = set_spec_mat("Mat_CuoioMedio", (0.36, 0.22, 0.12), (0.24, 0.13, 0.06), rough=0.65)
mat_cuoio_scuro = set_spec_mat("Mat_CuoioScuro", (0.24, 0.14, 0.08), (0.14, 0.07, 0.035), rough=0.66)
mat_stoffa_crema = set_spec_mat("Mat_ManicaLino", (0.82, 0.76, 0.64), (0.68, 0.60, 0.46), rough=0.88)

def add_cylinder_along_axis(bm_t, p_start, p_end, radius_start, radius_end=None, segs=18, cap_ends=True, mat_idx=0):
    if radius_end is None:
        radius_end = radius_start
    p0 = Vector(p_start)
    p1 = Vector(p_end)
    axis = (p1 - p0).normalized()
    up = Vector((0, 1, 0)) if abs(axis.y) < 0.9 else Vector((1, 0, 0))
    b1 = axis.cross(up).normalized()
    b2 = b1.cross(axis).normalized()
    rings = []
    for p, r in ((p0, radius_start), (p1, radius_end)):
        ring = [bm_t.verts.new(p + b1 * (r * math.cos(2 * math.pi * j / segs)) + b2 * (r * math.sin(2 * math.pi * j / segs))) for j in range(segs)]
        rings.append(ring)
    for j in range(segs):
        jn = (j + 1) % segs
        f = bm_t.faces.new((rings[0][j], rings[0][jn], rings[1][jn], rings[1][j]))
        f.smooth = True
        f.material_index = mat_idx
    if cap_ends:
        for idx, inv in ((0, True), (1, False)):
            c_pt = p0 if idx == 0 else p1
            cv = bm_t.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = False
                f.material_index = mat_idx

# 1. Reshape Corda_Fianco_DX (7.1):
#    Bundle of 4 overlapping oval loops of beige rope RGB (0.70, 0.62, 0.47), rope thickness 0.015 (radius 0.0075),
#    hanging from lower belt at X -0.17, Z 0.98, reaching down to Z 0.72.
#    Each loop is an oval (~0.16..0.24 high and 0.10 wide in Y), real twisted cord (3-strand helical relief).
corda_obj = bpy.data.objects.get("Corda_Fianco_DX")
if corda_obj:
    corda_obj.data.materials.clear()
    corda_obj.data.materials.append(mat_corda)
    bm = bmesh.new()

    # 4 overlapping oval loops hanging from (X=-0.17, Z=0.98) and staggered down to Z=0.72
    loop_configs = [
        # (z_top, z_bot, x_top, x_bot, y_center, ry_width, tilt_x)
        (0.980, 0.780, -0.165, -0.175, -0.025, 0.050,  0.008),
        (0.975, 0.750, -0.172, -0.184, -0.020, 0.052, -0.006),
        (0.965, 0.730, -0.178, -0.192, -0.015, 0.050,  0.007),
        (0.955, 0.720, -0.185, -0.198, -0.010, 0.048, -0.005),
    ]
    n_path = 44
    n_sect = 12
    r_base = 0.0075  # 0.015 rope thickness

    for li, (zt, zb, xt, xb, yc, ry_w, tilt) in enumerate(loop_configs):
        z_mid = 0.5 * (zt + zb)
        rz_h = 0.5 * (zt - zb)
        pts = []
        for k in range(n_path):
            th = 2.0 * math.pi * k / n_path
            ct, st = math.cos(th), math.sin(th)
            u_down = 0.5 * (1.0 - ct)  # 0 at top, 1 at bottom
            px = (xt * (1.0 - u_down) + xb * u_down) + tilt * st
            py = yc + ry_w * st
            pz = z_mid + rz_h * ct
            pts.append(Vector((px, py, pz)))

        rings = []
        for k in range(n_path):
            c = pts[k]
            t_vec = (pts[(k + 1) % n_path] - pts[(k - 1) % n_path]).normalized()
            up = Vector((1, 0, 0)) if abs(t_vec.x) < 0.85 else Vector((0, 1, 0))
            b1 = t_vec.cross(up).normalized()
            b2 = b1.cross(t_vec).normalized()
            u_len = k / float(n_path)
            ring = []
            for j in range(n_sect):
                ang = 2.0 * math.pi * j / n_sect
                # 3-strand helical twist ridge along the cord (real twisted cord!)
                twist = 0.22 * math.cos(3.0 * ang - 2.0 * math.pi * u_len * 14.0)
                r_curr = r_base * (1.0 + twist)
                ring.append(bm.verts.new(c + b1 * (r_curr * math.cos(ang)) + b2 * (r_curr * math.sin(ang))))
            rings.append(ring)

        for k in range(n_path):
            kn = (k + 1) % n_path
            for j in range(n_sect):
                jn = (j + 1) % n_sect
                f = bm.faces.new((rings[k][j], rings[k][jn], rings[kn][jn], rings[kn][j]))
                f.smooth = True

    bm.normal_update()
    bm.to_mesh(corda_obj.data)
    bm.free()
    corda_obj.data.update()

# 2. Reshape Borraccia_DX (7.2 Right-hip canister):
#    Brass and leather cylinder lying almost horizontal, 0.20 long, 0.07 across (radius 0.035),
#    centre at X -0.24, Z 0.90, Y -0.03. Brass end caps and two brass bands.
canister_obj = bpy.data.objects.get("Borraccia_DX")
if canister_obj:
    canister_obj.data.materials.clear()
    canister_obj.data.materials.append(mat_cuoio_medio)
    canister_obj.data.materials.append(mat_ottone)
    bm = bmesh.new()

    c_can = Vector((-0.240, -0.030, 0.900))
    # Almost horizontal axis (along Y with slight tilt in X and Z)
    can_dir = Vector((-0.18, -0.96, -0.21)).normalized()
    p_back = c_can - can_dir * 0.100  # total length 0.20 m
    p_front = c_can + can_dir * 0.100

    # Leather body cylinder (0.07 across -> radius 0.035)
    add_cylinder_along_axis(bm, p_back, p_front, 0.035, 0.035, segs=18, cap_ends=True, mat_idx=0)
    # Two brass end caps (each 0.025 long, radius 0.0365)
    add_cylinder_along_axis(bm, p_back - can_dir * 0.002, p_back + can_dir * 0.025, 0.0365, 0.0365, segs=18, cap_ends=True, mat_idx=1)
    add_cylinder_along_axis(bm, p_front - can_dir * 0.025, p_front + can_dir * 0.002, 0.0365, 0.0365, segs=18, cap_ends=True, mat_idx=1)
    # Two brass bands around the body
    for t_b in (0.35, 0.65):
        pb0 = p_back.lerp(p_front, t_b - 0.04)
        pb1 = p_back.lerp(p_front, t_b + 0.04)
        add_cylinder_along_axis(bm, pb0, pb1, 0.0368, 0.0368, segs=18, cap_ends=True, mat_idx=1)

    bm.normal_update()
    bm.to_mesh(canister_obj.data)
    bm.free()
    canister_obj.data.update()

# 3. Create / update Tasca_Tonda_DX (7.3):
#    Round leather pouch on her right hip, above the canister: flattened sphere 0.09 x 0.06 x 0.08
#    with a flap, centre X -0.20, Z 0.99.
pouch_r_obj = bpy.data.objects.get("Tasca_Tonda_DX") or bpy.data.objects.get("Lembo_Stoffa_DX")
if pouch_r_obj:
    pouch_r_obj.name = "Tasca_Tonda_DX"
    pouch_r_obj.data.name = "Tasca_Tonda_DX"
else:
    m_pr = bpy.data.meshes.new("Tasca_Tonda_DX")
    pouch_r_obj = bpy.data.objects.new("Tasca_Tonda_DX", m_pr)
    scn.collection.objects.link(pouch_r_obj)

pouch_r_obj.data.materials.clear()
pouch_r_obj.data.materials.append(mat_cuoio_medio)
pouch_r_obj.data.materials.append(mat_ottone)
bm = bmesh.new()
c_pr = Vector((-0.200, -0.035, 0.990))
# Flattened sphere 0.09 x 0.06 x 0.08 (rx=0.030 along X, ry=0.045 along Y, rz=0.040 along Z)
ret = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0)
for v in ret["verts"]:
    v.co = c_pr + Vector((v.co.x * 0.032, v.co.y * 0.045, v.co.z * 0.040))
for f in bm.faces:
    f.smooth = True
    f.material_index = 0
# Flap over the top/outer half of the pouch + tiny brass button
ret_f = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
for v in ret_f["verts"]:
    if v.co.z < -0.15:
        v.co.z = -0.15
    v.co = c_pr + Vector((v.co.x * 0.034 - 0.002, v.co.y * 0.047, v.co.z * 0.042 + 0.003))
for f in bm.faces:
    f.smooth = True
ret_b = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.006)
for v in ret_b["verts"]:
    v.co += c_pr + Vector((-0.033, 0.0, -0.005))
for v in ret_b["verts"]:
    for f in v.link_faces:
        f.material_index = 1
bm.normal_update()
bm.to_mesh(pouch_r_obj.data)
bm.free()
pouch_r_obj.data.update()

# 4. Reshape Astuccio_SX (7.4 Map tube on her LEFT hip (+X)):
#    - Tall cylinder hanging vertically from lower belt, 0.45 long, 0.075 across (radius 0.0375),
#      from Z 0.98 down to Z 0.53, centre X +0.22, Y -0.02.
#    - Brown leather body, brass cap at top and bottom (each 0.04 high), two leather straps around it.
#    - Beside it, next to it on the outside (+X ~ +0.285), a second thinner cylinder 0.35 long, 0.05 across (radius 0.025).
map_obj = bpy.data.objects.get("Astuccio_SX")
if map_obj:
    map_obj.data.materials.clear()
    map_obj.data.materials.append(mat_cuoio_medio)
    map_obj.data.materials.append(mat_ottone)
    map_obj.data.materials.append(mat_cuoio_scuro)
    bm = bmesh.new()

    p_top = Vector((0.220, -0.020, 0.980))
    p_bot = Vector((0.220, -0.020, 0.530))
    # Main leather body (0.45 long, 0.075 across -> radius 0.0375)
    add_cylinder_along_axis(bm, p_bot + Vector((0, 0, 0.038)), p_top - Vector((0, 0, 0.038)), 0.0375, 0.0375, segs=20, cap_ends=True, mat_idx=0)
    # Brass cap at top (Z 0.94 to 0.98, 0.04 high) and bottom (Z 0.53 to 0.57, 0.04 high)
    add_cylinder_along_axis(bm, Vector((0.220, -0.020, 0.940)), p_top, 0.0390, 0.0390, segs=20, cap_ends=True, mat_idx=1)
    add_cylinder_along_axis(bm, p_bot, Vector((0.220, -0.020, 0.570)), 0.0390, 0.0390, segs=20, cap_ends=True, mat_idx=1)
    # Two leather straps around the map tube + suspension straps to lower hip belt (Z=1.00 at X=+0.17)
    for z_s in (0.830, 0.680):
        add_cylinder_along_axis(bm, Vector((0.220, -0.020, z_s - 0.010)), Vector((0.220, -0.020, z_s + 0.010)), 0.0395, 0.0395, segs=20, cap_ends=True, mat_idx=2)
    add_cylinder_along_axis(bm, Vector((0.170, -0.020, 1.000)), Vector((0.220, -0.020, 0.960)), 0.007, 0.007, segs=8, cap_ends=True, mat_idx=2)

    # Second thinner cylinder beside it on the OUTSIDE (+X): 0.35 long (Z 0.93 down to 0.58), 0.05 across (radius 0.025)
    p2_top = Vector((0.282, -0.020, 0.930))
    p2_bot = Vector((0.282, -0.020, 0.580))
    add_cylinder_along_axis(bm, p2_bot, p2_top, 0.0250, 0.0250, segs=16, cap_ends=True, mat_idx=2)
    # Brass rim caps on second cylinder
    add_cylinder_along_axis(bm, p2_top - Vector((0, 0, 0.025)), p2_top, 0.0262, 0.0262, segs=16, cap_ends=True, mat_idx=1)
    add_cylinder_along_axis(bm, p2_bot, p2_bot + Vector((0, 0, 0.025)), 0.0262, 0.0262, segs=16, cap_ends=True, mat_idx=1)

    bm.normal_update()
    bm.to_mesh(map_obj.data)
    bm.free()
    map_obj.data.update()

# 5. Reshape Lembo_Stoffa_SX (7.5):
#    Torn piece of cream cloth hanging from lower belt on her left, between map tube (X=+0.22) and leg (X=+0.15):
#    0.07 wide, from Z 0.98 down to Z 0.62, with a ragged lower end.
cloth_obj = bpy.data.objects.get("Lembo_Stoffa_SX")
if cloth_obj:
    cloth_obj.data.materials.clear()
    cloth_obj.data.materials.append(mat_stoffa_crema)
    bm = bmesh.new()
    nu_t, nv_t = 10, 16
    grid_t = [[None] * nu_t for _ in range(nv_t)]
    for iv in range(nv_t):
        vt = iv / float(nv_t - 1)  # 0 = ragged lower end (Z~0.62), 1 = lower belt (Z=0.98)
        for iu in range(nu_t):
            ut = iu / float(nu_t - 1)  # 0..1 across 0.07 width
            # Ragged lower end at Z=0.62
            tri = 2.0 * abs(2.0 * (ut * 3.5 - math.floor(ut * 3.5 + 0.5))) - 1.0
            z_bot = 0.620 + (0.025 + 0.020 * tri)
            pz = z_bot * (1.0 - vt) + 0.980 * vt
            # Sits between left leg (X~0.155) and map tube (X~0.185), oriented so its 0.07 width shows in front/side views
            px = 0.162 + 0.022 * ut + 0.005 * math.sin(vt * math.pi * 2.0)
            py = -0.055 + 0.065 * (ut - 0.5) + 0.006 * math.cos(ut * math.pi * 3.0) * (1.0 - vt)
            grid_t[iv][iu] = bm.verts.new(Vector((px, py, pz)))
    for iv in range(nv_t - 1):
        for iu in range(nu_t - 1):
            f = bm.faces.new((grid_t[iv][iu], grid_t[iv][iu + 1], grid_t[iv + 1][iu + 1], grid_t[iv + 1][iu]))
            f.smooth = True
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.003)
    bm.normal_update()
    bm.to_mesh(cloth_obj.data)
    bm.free()
    cloth_obj.data.update()

# 6. Create Tasche_Cintura (7.6):
#    3 small brown leather pouches along the belt, each about 0.06 x 0.05 x 0.03, at the back and on the sides of the belt.
pouches_obj = bpy.data.objects.get("Tasche_Cintura")
if not pouches_obj:
    m_p = bpy.data.meshes.new("Tasche_Cintura")
    pouches_obj = bpy.data.objects.new("Tasche_Cintura", m_p)
    scn.collection.objects.link(pouches_obj)

pouches_obj.data.materials.clear()
pouches_obj.data.materials.append(mat_cuoio_scuro)
bm = bmesh.new()
pouch_placements = [
    # (center, rot_z_deg): front-left hip, back-left waist, back-right waist
    (Vector(( 0.145, -0.075, 1.035)),  35.0),
    (Vector(( 0.095,  0.098, 1.060)), 145.0),
    (Vector((-0.095,  0.098, 1.060)), -145.0),
]
for c_p, rot_z in pouch_placements:
    rm = Euler((0.0, 0.0, math.radians(rot_z)), 'XYZ').to_matrix()
    ret = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.5)
    for v in ret["verts"]:
        # Rounded box 0.06 wide x 0.03 thick x 0.05 high
        sx_p = math.copysign(abs(v.co.x * 2.0) ** 0.65, v.co.x) * 0.030
        sy_p = math.copysign(abs(v.co.y * 2.0) ** 0.65, v.co.y) * 0.015
        sz_p = math.copysign(abs(v.co.z * 2.0) ** 0.65, v.co.z) * 0.025
        v.co = c_p + rm @ Vector((sx_p, sy_p, sz_p))
for f in bm.faces:
    f.smooth = True
bm.normal_update()
bm.to_mesh(pouches_obj.data)
bm.free()
pouches_obj.data.update()

log("=== VERIFICA MISURE GROUP 7 ===")
r_vs = corda_obj.data.vertices
cn_vs = canister_obj.data.vertices
mp_vs = map_obj.data.vertices
log(f"Corda_Fianco_DX Z: {min(v.co.z for v in r_vs):.4f}..{max(v.co.z for v in r_vs):.4f}m (target 0.72..0.98)")
log(f"Borraccia_DX centro: X={(min(v.co.x for v in cn_vs)+max(v.co.x for v in cn_vs))/2:.4f}, Y={(min(v.co.y for v in cn_vs)+max(v.co.y for v in cn_vs))/2:.4f}, Z={(min(v.co.z for v in cn_vs)+max(v.co.z for v in cn_vs))/2:.4f} (target -0.24, -0.03, 0.90)")
log(f"Astuccio_SX Z: {min(v.co.z for v in mp_vs):.4f}..{max(v.co.z for v in mp_vs):.4f}m (target 0.53..0.98)")

bpy.ops.wm.save_mainfile()
render_viste("rev_7")
