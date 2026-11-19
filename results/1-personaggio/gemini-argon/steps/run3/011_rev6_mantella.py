import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# ==============================================================================
# GROUP 6 - The cape (rev_6) - Exact arch over shoulders, behind hip gear,
# and true sRGB worn teal / lighter streaks / dirty sand texture.
# ==============================================================================

scn = bpy.context.scene

def update_cape_material():
    size = 512
    img = bpy.data.images.get("Tex_MantellaVerde")
    if not img or img.size[0] != size:
        if img:
            bpy.data.images.remove(img)
        img = bpy.data.images.new("Tex_MantellaVerde", width=size, height=size, alpha=False)

    # Note: Blender's 8-bit image texture node is in sRGB space by default, so write exact spec sRGB values!
    y, x = np.mgrid[0:size, 0:size] / float(size)
    wx = x + 0.035 * np.sin(2 * math.pi * (y * 3.0 + x * 2.0)) + 0.018 * np.cos(2 * math.pi * (y * 7.0 - x * 5.0))
    wy = y + 0.030 * np.cos(2 * math.pi * (x * 4.0 - y * 3.0))

    # Lighter streaks RGB (0.40, 0.52, 0.48) running down on worn teal green RGB (0.22, 0.34, 0.31)
    streak_wave = (
        0.50 * np.sin(2 * math.pi * (wx * 11.0 + 0.25 * np.sin(2 * math.pi * wy * 2.5)))
        + 0.30 * np.cos(2 * math.pi * (wx * 23.0 - 0.20 * np.cos(2 * math.pi * wy * 4.0) + 1.1))
        + 0.20 * np.sin(2 * math.pi * (wx * 37.0 + wy * 5.0))
    )
    streak_mask = np.clip((streak_wave - 0.10) * 1.35, 0.0, 1.0) ** 1.5

    # Lower 0.25 m fades to dirty sand colour RGB (0.62, 0.55, 0.43), with brown stains
    noise_mud = 0.5 + 0.35 * np.sin(2 * math.pi * (wx * 9.0 + wy * 7.0)) * np.cos(2 * math.pi * (wx * 13.0 - wy * 11.0))
    sand_fade = np.clip((0.25 - wy + 0.05 * (noise_mud - 0.5)) / 0.23, 0.0, 1.0) ** 1.2
    stain_noise = np.sin(2 * math.pi * (wx * 17.0 - wy * 13.0 + 0.7)) * np.cos(2 * math.pi * (wx * 19.0 + wy * 15.0))
    stain_mask = np.clip((stain_noise - 0.22) * 2.2, 0.0, 1.0) * np.clip((0.32 - wy) / 0.32, 0.0, 1.0)

    c_teal = (0.22, 0.34, 0.31)
    c_streak = (0.40, 0.52, 0.48)
    c_sand = (0.62, 0.55, 0.43)
    c_stain = (0.36, 0.26, 0.17)

    pixels = np.ones((size, size, 4), dtype=np.float32)
    for ch in range(3):
        col = c_teal[ch] * (1.0 - streak_mask * 0.55) + c_streak[ch] * (streak_mask * 0.55)
        col = col * (1.0 - sand_fade * 0.85) + c_sand[ch] * (sand_fade * 0.85)
        col = col * (1.0 - stain_mask * 0.65) + c_stain[ch] * (stain_mask * 0.65)
        pixels[:, :, ch] = np.clip(col, 0.0, 1.0)

    img.pixels.foreach_set(pixels.ravel())
    img.pack()

    mat = bpy.data.materials.get("Mat_MantellaVerde")
    if not mat:
        mat = bpy.data.materials.new("Mat_MantellaVerde")
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.22, 0.34, 0.31, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.20
    tnode = next((n for n in nodes if n.type == 'TEX_IMAGE'), None) or nodes.new("ShaderNodeTexImage")
    tnode.image = img
    links.new(tnode.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

mat_cape = update_cape_material()

def solidify_cape_bm(bm_t, thickness=0.006):
    loose_v = [v for v in bm_t.verts if not v.link_faces]
    if loose_v:
        bmesh.ops.delete(bm_t, geom=loose_v, context='VERTS')
    bm_t.normal_update()
    uv_lay = bm_t.loops.layers.uv.active
    orig_verts = bm_t.verts[:]
    orig_faces = bm_t.faces[:]
    orig_edges = [e for e in bm_t.edges if len(e.link_faces) == 1]

    v_map = {}
    for v in orig_verts:
        n = v.normal.normalized() if v.normal.length > 1e-6 else Vector((0, 1, 0))
        nv = bm_t.verts.new(v.co - n * thickness)
        v_map[v] = nv

    for f in orig_faces:
        f.smooth = True
        uvs = [l[uv_lay].uv.copy() for l in f.loops] if uv_lay else None
        nf = bm_t.faces.new([v_map[v] for v in reversed(f.verts)])
        nf.smooth = True
        if uv_lay and uvs:
            for l, uv_val in zip(nf.loops, reversed(uvs)):
                l[uv_lay].uv = uv_val

    for e in orig_edges:
        v0, v1 = e.verts[0], e.verts[1]
        loop = e.link_loops[0]
        if loop.vert == v0:
            v0, v1 = v1, v0
        rf = bm_t.faces.new((v0, v1, v_map[v1], v_map[v0]))
        rf.smooth = True

    bm_t.normal_update()

# 2. Reshape Mantella_Spalla_SX and Mantella_Spalla_DX (6.2):
#    Arches cleanly OVER the top of the shoulder and upper sleeve (from collar Z=1.42
#    down to Z=1.24 on the arms and Z=1.20 on the back), cut into ragged points at its edge.
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    sp_obj = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if not sp_obj:
        continue
    bm_s = bmesh.new()
    uv_s = bm_s.loops.layers.uv.new("UVMap")
    nu_s, nv_s = 32, 16
    grid_s = [[None] * nu_s for _ in range(nv_s)]

    for iv in range(nv_s):
        vt = iv / float(nv_s - 1)  # 0 = lower ragged hem (Z~1.24 on arm, Z~1.20 on back), 1 = neck/collar root (Z~1.42)
        s = 1.0 - vt               # 0 at collar root, 1 at lower hem
        for iu in range(nu_s):
            ut = iu / float(nu_s - 1)  # 0 = front chest (-Y), 0.5 = top/outer arm, 1 = back (+Y)
            # Angle across the arm cross-section: -pi/2 is front (-Y), 0 is top of arm (+Z / outer X), +pi/2 is back (+Y)
            ang = (ut - 0.5) * math.pi * 1.15

            # Follow the upper arm centerline from collar (X=0.075, Z=1.41) over shoulder (X=0.19, Z=1.40) to mid-upper-arm (X=0.31, Z=1.26)
            x_arm = 0.075 + 0.240 * s
            if x_arm <= 0.185:
                z_arm = 1.410 - 0.010 * ((x_arm - 0.075) / 0.110)
            else:
                z_arm = 1.400 - (x_arm - 0.185) * 1.15

            # Arch OVER the top of the sleeve (sleeve radius is 0.050, so top arch radius is 0.064!)
            # and drape down on front/back so at s=1 (hem) it reaches Z=1.24 on the arm and Z=1.20 on the back!
            r_y = 0.074 + 0.032 * s
            top_lift = (0.062 * (1.0 - 0.55 * s)) * max(0.0, math.cos(ang))
            side_drape = (0.045 * s) * (abs(math.sin(ang)) ** 1.2)
            back_extra = (0.040 * s) * max(0.0, math.sin(ang)) ** 1.4  # lowers back hem to Z=1.20

            # Ragged triangular points along the lower edge (7 irregular teeth)
            tri_wave = 2.0 * abs(2.0 * (ut * 6.5 - math.floor(ut * 6.5 + 0.5))) - 1.0
            ragged_dz = tri_wave * (0.022 + 0.010 * math.sin(ut * 11.0 + sx)) * (s ** 1.4)
            fold_r = 0.005 * math.cos(ut * math.pi * 9.0) * s

            px = sx * (x_arm + (0.018 * s + fold_r) * math.cos(ang))
            py = 0.004 + (r_y + fold_r) * math.sin(ang)
            pz = z_arm + top_lift - side_drape - back_extra + ragged_dz

            # Push back of shoulder cape outside the long cape at the upper back
            if py > 0.05 and abs(px) < 0.20:
                py = max(py, 0.115 + 0.020 * s)

            grid_s[iv][iu] = bm_s.verts.new(Vector((px, py, pz)))

    for iv in range(nv_s - 1):
        for iu in range(nu_s - 1):
            f = bm_s.faces.new((grid_s[iv][iu], grid_s[iv][iu + 1], grid_s[iv + 1][iu + 1], grid_s[iv + 1][iu]))
            for loop, (uu, vv) in zip(f.loops, ((iu, iv), (iu + 1, iv), (iu + 1, iv + 1), (iu, iv + 1))):
                loop[uv_s].uv = (uu / float(nu_s - 1), 0.72 + 0.28 * (vv / float(nv_s - 1)))

    solidify_cape_bm(bm_s, thickness=0.0055)
    bm_s.to_mesh(sp_obj.data)
    bm_s.free()
    sp_obj.data.update()

# 3. Reshape Mantella_Corpo (6.3 - 6.6):
#    - Back goes down to Z 0.20; front panels go down to Z 0.25 on each side of the body,
#      outside the legs, with a 0.36 m front gap (inner edges at X = +-0.18),
#      and staying BEHIND the arms and hip gear (Y >= +0.02 at Z > 0.45) so hip gear is 100% visible!
#    - Bottom width 1.10 m across (X from -0.55 to +0.55).
cape_obj = bpy.data.objects.get("Mantella_Corpo")
if cape_obj:
    bm_c = bmesh.new()
    uv_c = bm_c.loops.layers.uv.new("UVMap")
    nu = 88
    nv = 52

    rag_knots_u = [0.0]
    rag_lengths = [0.06, 0.15, 0.05, 0.17, 0.08, 0.14, 0.06, 0.18, 0.07, 0.13, 0.05, 0.16,
                   0.09, 0.17, 0.06, 0.15, 0.05, 0.18, 0.08, 0.14, 0.06, 0.16, 0.07, 0.12]
    rag_widths =  [0.8,  1.2,  0.7,  1.3,  0.9,  1.1,  0.8,  1.4,  0.7,  1.1,  0.9,  1.3,
                   0.8,  1.2,  0.7,  1.3,  0.9,  1.2,  0.8,  1.1,  0.7,  1.2,  0.9,  0.8]
    tot_w = sum(rag_widths)
    acc = 0.0
    for w in rag_widths:
        acc += w / tot_w
        rag_knots_u.append(acc)
    rag_knots_u[-1] = 1.0

    def irregular_rag_offset(u):
        for idx in range(len(rag_widths)):
            u0, u1 = rag_knots_u[idx], rag_knots_u[idx + 1]
            if u0 <= u <= u1:
                local_t = (u - u0) / max(1e-6, u1 - u0)
                tooth = 1.0 - abs(2.0 * local_t - 1.0)
                return tooth * rag_lengths[idx]
        return 0.0

    grid = [[None] * nu for _ in range(nv)]
    for iv in range(nv):
        vt = iv / float(nv - 1)  # 0 = bottom rag tips, 1 = shoulders
        for iu in range(nu):
            ut = iu / float(nu - 1)
            s_u = (ut - 0.5) * 2.0   # -1 (right front panel edge) .. 0 (center back) .. +1 (left front panel edge)
            sign_x = 1.0 if s_u >= 0 else -1.0
            absu = abs(s_u)

            front_panel_t = max(0.0, min(1.0, (absu - 0.35) / 0.55))
            z_base_bot = 0.200 + 0.050 * front_panel_t
            z_bot = z_base_bot + irregular_rag_offset(ut)
            z_top = 1.402 - 0.015 * (absu ** 2)
            z = z_bot * (1.0 - vt) + z_top * vt

            # At top (vt=1) wraps over shoulders to front collarbone (138 deg);
            # below shoulders (vt<0.85) stays behind arms & hip gear (max_ang ~ 98 deg)
            max_ang = math.radians(96.0 + 42.0 * (vt ** 1.8))
            ang = s_u * max_ang

            bell_t = (1.0 - vt) ** 0.90
            rx_curr = 0.195 * (1.0 - bell_t) + 0.535 * bell_t
            ry_curr = 0.105 * (1.0 - bell_t) + 0.205 * bell_t

            # 8 big vertical folds (waves of 0.03 to 0.05 depth)
            fold_amp = 0.008 + 0.034 * (1.0 - 0.75 * vt)
            fold_wave = fold_amp * (
                0.70 * math.sin(ut * math.pi * 14.0)
                + 0.30 * math.cos(ut * math.pi * 22.0 + 0.6)
            )

            px = (rx_curr + fold_wave) * math.sin(ang)
            py = 0.020 + (ry_curr + fold_wave * 0.85) * math.cos(ang)

            # Two front panels hang down on each side of the body, outside the legs, down to Z 0.25,
            # leaving a 0.36 m gap in front (inner edges at X = +-0.18..0.20, outer edges flaring to +-0.55)
            if absu > 0.78 and vt < 0.75:
                t_edge = (absu - 0.78) / 0.22
                # Curve the inner front panel edges slightly inward in X (to X = +-0.19) while staying behind hip gear (py >= 0.015)
                inner_x = sign_x * (0.185 + 0.035 * (1.0 - vt))
                px = px * (1.0 - 0.45 * t_edge) + inner_x * (0.45 * t_edge)
                py = max(py, -0.015 * (1.0 - vt))

            # Never cut through arms or hip gear (arms at Y=0, hip gear at Y <= 0.02)
            if z > 0.50 and py < 0.025 and vt < 0.88:
                py = 0.025 + 0.020 * ((z - 0.50) / 0.90)

            grid[iv][iu] = bm_c.verts.new(Vector((px, py, z)))

    # Normalize exact bottom width to 1.10 m across (X from -0.550 to +0.550)
    xs_all = [v.co.x for v in bm_c.verts]
    cur_w = max(xs_all) - min(xs_all)
    scale_w = 1.100 / max(1e-5, cur_w)
    for v in bm_c.verts:
        t_bot = max(0.0, min(1.0, (1.38 - v.co.z) / (1.38 - 0.25)))
        v.co.x *= (1.0 + (scale_w - 1.0) * (t_bot ** 0.5))

    holes = [
        (0.16, 0.11, 0.020, 0.028),
        (0.27, 0.14, 0.024, 0.034),
        (0.38, 0.09, 0.018, 0.026),
        (0.49, 0.12, 0.022, 0.032),
        (0.61, 0.10, 0.020, 0.028),
        (0.73, 0.15, 0.024, 0.034),
        (0.84, 0.11, 0.019, 0.027),
    ]

    for iv in range(nv - 1):
        for iu in range(nu - 1):
            uc = (iu + 0.5) / float(nu - 1)
            vc = (iv + 0.5) / float(nv - 1)
            in_hole = False
            for hu, hv, ru, rv in holes:
                if ((uc - hu) / ru) ** 2 + ((vc - hv) / rv) ** 2 < 1.0:
                    in_hole = True
                    break
            if in_hole:
                continue
            f = bm_c.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
            for loop, (uu, vv) in zip(f.loops, ((iu, iv), (iu + 1, iv), (iu + 1, iv + 1), (iu, iv + 1))):
                loop[uv_c].uv = (uu / float(nu - 1), vv / float(nv - 1))

    solidify_cape_bm(bm_c, thickness=0.006)
    bm_c.to_mesh(cape_obj.data)
    bm_c.free()
    cape_obj.data.update()

c_vs = cape_obj.data.vertices
log("=== VERIFICA MISURE GROUP 6 (aggiornata) ===")
log(f"Mantella_Corpo larghezza X={max(v.co.x for v in c_vs)-min(v.co.x for v in c_vs):.4f}m (target 1.10m), Z_min={min(v.co.z for v in c_vs):.4f}m (target 0.20m)")

bpy.ops.wm.save_mainfile()
render_viste("rev_6")
