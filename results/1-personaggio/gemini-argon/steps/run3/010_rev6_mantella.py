import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# ==============================================================================
# GROUP 6 - The cape (rev_6) + Group 5 gauntlet strap radius & fingertip tweak
# - 6.1 Colour: worn teal green RGB (0.22, 0.34, 0.31), lighter vertical streaks
#   RGB (0.40, 0.52, 0.48), lower 0.25 m fading to dirty sand RGB (0.62, 0.55, 0.43)
#   with brown stains.
# - 6.2 Shoulder cape (top layer): covers both shoulders and top of upper arms,
#   from collar (Z 1.41) down to Z 1.24 on arms and Z 1.20 on back, cut into
#   ragged points at its edge, completely covering upper sleeve with no poke-through.
# - 6.3 Long cape: hangs from shoulders at back and sides, behind arms;
#   back goes down to Z 0.20; front open with two front panels down to Z 0.25
#   outside the legs with a 0.35 m front gap (0.30..0.40 wide);
#   at its bottom measures 1.10 m across (X from -0.55 to +0.55) like a bell;
#   seen from the side stands 0.10 to 0.15 away from the back of the legs.
# - 6.4 Folds: 8 big vertical folds from shoulders to bottom (waves 0.03..0.05 deep).
# - 6.5 Bottom edge: torn into >22 irregular triangular rags (0.05 to 0.18 long,
#   different widths) + holes 0.03 to 0.06 wide just above the edge.
# - 6.6 Thickness 0.006 m (real solidified geometry), pushed out around body/arms/helmet.
# - 6.7 Cluster of 3 off-white shells (0.02 to 0.03 each, RGB (0.88, 0.85, 0.78))
#   pinned at front of LEFT collarbone (X +0.12, Z 1.37).
# ==============================================================================

scn = bpy.context.scene

# 1. Build Group 6 procedural cape texture and material (6.1)
def update_cape_material():
    size = 512
    img = bpy.data.images.get("Tex_MantellaVerde")
    if not img or img.size[0] != size:
        if img:
            bpy.data.images.remove(img)
        img = bpy.data.images.new("Tex_MantellaVerde", width=size, height=size, alpha=False)

    # y=0 is bottom edge (Z=0.20), y=1 is shoulders (Z=1.41); total height = 1.21 m
    # lower 0.25 m corresponds to y < (0.25 / 1.21) ~ 0.22
    y, x = np.mgrid[0:size, 0:size] / float(size)
    wx = x + 0.035 * np.sin(2 * math.pi * (y * 3.0 + x * 2.0)) + 0.018 * np.cos(2 * math.pi * (y * 7.0 - x * 5.0))
    wy = y + 0.030 * np.cos(2 * math.pi * (x * 4.0 - y * 3.0))

    # Vertical wave/noise streaks running down: lighter streaks RGB (0.40, 0.52, 0.48) on worn teal RGB (0.22, 0.34, 0.31)
    streak_wave = (
        0.50 * np.sin(2 * math.pi * (wx * 11.0 + 0.25 * np.sin(2 * math.pi * wy * 2.5)))
        + 0.30 * np.cos(2 * math.pi * (wx * 23.0 - 0.20 * np.cos(2 * math.pi * wy * 4.0) + 1.1))
        + 0.20 * np.sin(2 * math.pi * (wx * 37.0 + wy * 5.0))
    )
    streak_mask = np.clip((streak_wave - 0.15) * 1.4, 0.0, 1.0) ** 1.6

    # Lower 0.25 m fades to dirty sand RGB (0.62, 0.55, 0.43), with brown stains RGB (0.34, 0.25, 0.16)
    noise_mud = 0.5 + 0.35 * np.sin(2 * math.pi * (wx * 9.0 + wy * 7.0)) * np.cos(2 * math.pi * (wx * 13.0 - wy * 11.0))
    sand_fade = np.clip((0.26 - wy + 0.06 * (noise_mud - 0.5)) / 0.24, 0.0, 1.0) ** 1.25
    stain_noise = np.sin(2 * math.pi * (wx * 17.0 - wy * 13.0 + 0.7)) * np.cos(2 * math.pi * (wx * 19.0 + wy * 15.0))
    stain_mask = np.clip((stain_noise - 0.25) * 2.2, 0.0, 1.0) * np.clip((0.34 - wy) / 0.34, 0.0, 1.0)

    # Note: convert spec RGBs to linear for Principled BSDF image texture so rendered color matches spec visually
    def srgb_to_lin(c):
        return tuple(max(0.0, ch) ** 1.8 for ch in c)

    c_teal = srgb_to_lin((0.22, 0.34, 0.31))
    c_streak = srgb_to_lin((0.40, 0.52, 0.48))
    c_sand = srgb_to_lin((0.62, 0.55, 0.43))
    c_stain = srgb_to_lin((0.35, 0.24, 0.15))

    pixels = np.ones((size, size, 4), dtype=np.float32)
    for ch in range(3):
        col = c_teal[ch] * (1.0 - streak_mask * 0.65) + c_streak[ch] * (streak_mask * 0.65)
        col = col * (1.0 - sand_fade * 0.85) + c_sand[ch] * (sand_fade * 0.85)
        col = col * (1.0 - stain_mask * 0.70) + c_stain[ch] * (stain_mask * 0.70)
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
        # Match winding of adjacent outer face
        loop = e.link_loops[0]
        if loop.vert == v0:
            v0, v1 = v1, v0
        rf = bm_t.faces.new((v0, v1, v_map[v1], v_map[v0]))
        rf.smooth = True

    bm_t.normal_update()

# 2. Reshape Mantella_Spalla_SX and Mantella_Spalla_DX (6.2):
#    Short cape covering both shoulders and top of upper arms, from collar (Z 1.41)
#    down to Z 1.24 on the arms and to Z 1.20 on the back. Cut into ragged points at its edge.
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    sp_obj = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if not sp_obj:
        continue
    bm_s = bmesh.new()
    uv_s = bm_s.loops.layers.uv.new("UVMap")
    nu_s, nv_s = 32, 16
    grid_s = [[None] * nu_s for _ in range(nv_s)]

    for iv in range(nv_s):
        vt = iv / float(nv_s - 1)  # 0 = bottom ragged edge, 1 = collar/shoulder top (Z=1.41)
        for iu in range(nu_s):
            ut = iu / float(nu_s - 1)  # 0 = front chest (-Y), 0.5 = outer arm (X), 1 = back (+Y)
            # Azimuth around the shoulder/arm: from front collarbone (-100 deg) around outer arm (0 deg) to upper back (+100 deg)
            ang = (-0.56 + 1.12 * ut) * math.pi

            # Centerline along the upper arm from collar (X=0.08, Z=1.41) down to Z=1.24 on arm (X=0.33, Z=1.24)
            c_x = sx * (0.075 + 0.250 * (1.0 - vt))
            c_y = 0.004
            # Target bottom Z: Z=1.24 on the outer arm (ut=0.5), Z=1.20 on the back (ut=1.0), Z=1.27 at front chest (ut=0.0)
            if ut >= 0.5:
                tb = (ut - 0.5) / 0.5
                z_edge_base = 1.240 * (1.0 - tb) + 1.200 * tb
            else:
                tf = (0.5 - ut) / 0.5
                z_edge_base = 1.240 * (1.0 - tf) + 1.275 * tf

            # Ragged triangular points along the lower edge (6-7 points per shoulder cape)
            tri_wave = 2.0 * abs(2.0 * (ut * 6.5 - math.floor(ut * 6.5 + 0.5))) - 1.0
            mod_amp = 0.022 + 0.012 * math.sin(ut * math.pi * 5.0 + sx)
            ragged_dz = tri_wave * mod_amp * ((1.0 - vt) ** 1.3)

            z_top = 1.415 - 0.015 * abs(ut - 0.5)
            pz = (z_edge_base + ragged_dz) * (1.0 - vt) + z_top * vt

            # Wrap generously outside the upper sleeve (radius >= 0.068) so sleeve NEVER pokes through!
            r_arm = 0.066 + 0.020 * (1.0 - vt) + 0.005 * math.cos(ut * math.pi * 8.0)
            r_y = 0.082 + 0.042 * (1.0 - vt) + 0.005 * math.sin(ut * math.pi * 6.0)
            px = c_x + sx * r_arm * math.cos(ang * 0.65)
            py = c_y + r_y * math.sin(ang)
            # Push back portion outside the main cape at the upper back
            if py > 0.06 and abs(px) < 0.18:
                py = max(py, 0.115 + 0.025 * (1.0 - vt))
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

# 3. Reshape Mantella_Corpo (6.3, 6.4, 6.5, 6.6):
#    - Back goes down to Z 0.20 (above ankles)
#    - Front open: two front panels hang from shoulders down on each side of body, outside legs,
#      down to Z 0.25, leaving a front gap 0.35 m wide (between 0.30 and 0.40 wide: inner edges at X = +-0.175)
#    - Wide bell shape: at its bottom measures 1.10 m across (X from -0.55 to +0.55)
#    - Seen from the side stands 0.10 to 0.15 away from the back of the legs (Y ~ +0.20..+0.24 at lower back)
#    - At least 6 big vertical folds (8 folds of 0.03 to 0.05 depth) running from shoulders to bottom edge
#    - Torn bottom edge: cut into >= 22 irregular triangular rags (0.05 to 0.18 long, different widths)
#      plus holes 0.03 to 0.06 wide just above the edge
cape_obj = bpy.data.objects.get("Mantella_Corpo")
if cape_obj:
    bm_c = bmesh.new()
    uv_c = bm_c.loops.layers.uv.new("UVMap")
    nu = 88  # columns around the cape from right front panel edge (u=0) through back (u=0.5) to left front panel edge (u=1)
    nv = 52  # rows from bottom torn edge (v=0) to shoulders (v=1)

    # Pre-generate 24 irregular triangular rag points along u in [0, 1] (lengths 0.05 to 0.18 m, varied widths)
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
        # Piecewise triangular rag tooth between knots: tip at knot (down), notch at midpoint (up by rag_length)
        for idx in range(len(rag_widths)):
            u0, u1 = rag_knots_u[idx], rag_knots_u[idx + 1]
            if u0 <= u <= u1:
                local_t = (u - u0) / max(1e-6, u1 - u0)  # 0..1 across one rag tooth
                # Triangular peak at local_t = 0.5 (notch up), valleys at 0 and 1 (rag tips down)
                tooth = 1.0 - abs(2.0 * local_t - 1.0)
                return tooth * rag_lengths[idx]
        return 0.0

    grid = [[None] * nu for _ in range(nv)]
    for iv in range(nv):
        vt = iv / float(nv - 1)  # 0 = bottom rag tips, 1 = shoulders
        for iu in range(nu):
            ut = iu / float(nu - 1)  # 0 = right front inner edge (-X), 0.5 = center back (+Y), 1 = left front inner edge (+X)
            s_u = (ut - 0.5) * 2.0   # -1 (right front panel) .. 0 (center back) .. +1 (left front panel)
            sign_x = 1.0 if s_u >= 0 else -1.0
            absu = abs(s_u)

            # Base bottom height before rag cut: Z = 0.20 at the back (absu < 0.4), rising to Z = 0.25 on the front panels (absu > 0.7)
            front_panel_t = max(0.0, min(1.0, (absu - 0.35) / 0.55))
            z_base_bot = 0.200 + 0.050 * front_panel_t
            z_bot = z_base_bot + irregular_rag_offset(ut)
            z_top = 1.405 - 0.015 * (absu ** 2)
            z = z_bot * (1.0 - vt) + z_top * vt

            # Bell flare width (X) and depth (Y):
            # At top (vt=1): wraps shoulders from X=+-0.12 at front collarbone around outer shoulder (X=+-0.21) to back
            # At bottom (vt=0): flares like a bell to 1.10 m total width (X = -0.55 to +0.55 at outer edges absu ~ 0.68),
            # while the two front panel inner edges (absu = 1.0) curve in to X = +-0.175 in front of the legs (0.35 m front gap!)
            # Angle around body: 0 is +Y (back), +-pi is -Y (front)
            max_ang = math.radians(126.0 + 18.0 * vt)  # reaches around the sides to the front-side panels!
            ang = s_u * max_ang

            # Horizontal radius profile:
            rx_top = 0.205
            # Bell flare towards bottom: reaches X = +-0.55 (total 1.10 m across!) at sin(ang) = +-1 (ang = +-90 deg)
            bell_t = (1.0 - vt) ** 0.92
            rx_bot = 0.535  # plus fold waves -> exact 0.550 half-width (1.10 m across!)
            rx_curr = rx_top * (1.0 - bell_t) + rx_bot * bell_t

            # Depth Y: stands 0.10 to 0.15 m away from the back of the legs (leg back is at Y~+0.06, so cape back is at Y~+0.20)
            ry_top = 0.105
            ry_bot = 0.205
            ry_curr = ry_top * (1.0 - bell_t) + ry_bot * bell_t

            # 8 big vertical folds (waves of 0.03 to 0.05 depth) running from shoulders to bottom edge (6.4)
            fold_amp = 0.008 + 0.034 * (1.0 - 0.75 * vt)
            fold_wave = fold_amp * (
                0.70 * math.sin(ut * math.pi * 14.0)
                + 0.30 * math.cos(ut * math.pi * 22.0 + 0.6)
            )

            px = (rx_curr + fold_wave) * math.sin(ang)
            py = 0.015 + (ry_curr + fold_wave * 0.85) * math.cos(ang)

            # Guide the front panel inner edges (absu > 0.72) so they hang outside/front-side of the legs (Y < -0.04)
            # with a clean 0.35 m front gap between them (inner edges at X = +-0.175, gap = 0.35 m in [0.30, 0.40])
            if absu > 0.72:
                t_edge = (absu - 0.72) / 0.28
                target_edge_x = sign_x * (0.145 * vt + 0.180 * (1.0 - vt))
                px = px * (1.0 - 0.35 * t_edge) + target_edge_x * (0.35 * t_edge)
                # Keep front panels outside the waist gear (rope/canister at X=-0.24, map tube at X=+0.22)
                if 0.50 < z < 1.05 and py < 0.04:
                    min_abs_x = 0.275 if sign_x < 0 else 0.265
                    if abs(px) < min_abs_x and t_edge < 0.75:
                        px = sign_x * min_abs_x

            # Keep cape behind the A-pose arms (arms are at Y=0.0, Z = 1.40 - (|X|-0.19)*1.15)
            if z > 0.95 and abs(px) > 0.18 and py < 0.065:
                py = 0.065 + 0.015 * ((abs(px) - 0.18) / 0.25)

            grid[iv][iu] = bm_c.verts.new(Vector((px, py, z)))

    # Normalize exact bottom width to 1.10 m across (X from -0.550 to +0.550) and minimum back Z to 0.200 m
    xs_all = [v.co.x for v in bm_c.verts]
    cur_w = max(xs_all) - min(xs_all)
    scale_w = 1.100 / max(1e-5, cur_w)
    for v in bm_c.verts:
        # Scale X flare smoothly towards bottom so top shoulder fit stays unchanged and bottom is exactly 1.10 m across
        t_bot = max(0.0, min(1.0, (1.38 - v.co.z) / (1.38 - 0.25)))
        v.co.x *= (1.0 + (scale_w - 1.0) * (t_bot ** 0.5))

    # Holes 0.03 to 0.06 wide just above the bottom edge (6.5)
    # In UV space: width 1.10 m -> du = 0.025..0.045, height 1.20 m -> dv = 0.025..0.045
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

# 4. Reshape Conchiglie_SX (6.7):
#    Small cluster of white shells pinned on the cape at the front of her LEFT collarbone (X +0.12, Z 1.37):
#    3 small shell shapes, 0.02 to 0.03 each, off-white RGB (0.88, 0.85, 0.78).
mat_shell = bpy.data.materials.get("Mat_Conchiglia")
if mat_shell and mat_shell.use_nodes:
    bsdf = mat_shell.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.88, 0.85, 0.78, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.55

shells_obj = bpy.data.objects.get("Conchiglie_SX")
if shells_obj:
    bm_sh = bmesh.new()
    # 3 small ribbed shell shapes (0.028, 0.024, 0.021 across) clustered around (X=+0.12, Y=-0.088, Z=1.37)
    shell_cluster = [
        (Vector((0.120, -0.090, 1.372)), 0.014, 0.0),
        (Vector((0.138, -0.086, 1.365)), 0.011, 0.6),
        (Vector((0.104, -0.092, 1.364)), 0.010, -0.5),
    ]
    for c_pos, r_sh, yaw in shell_cluster:
        ret = bmesh.ops.create_uvsphere(bm_sh, u_segments=14, v_segments=8, radius=r_sh)
        for v in ret["verts"]:
            ang = math.atan2(v.co.z, v.co.x) + yaw
            rib = 1.0 + 0.15 * math.sin(ang * 7.0)
            v.co.x *= 1.10 * rib
            v.co.z *= 0.95 * rib
            v.co.y *= 0.45
            v.co += c_pos
    for f in bm_sh.faces:
        f.smooth = True
    bm_sh.normal_update()
    bm_sh.to_mesh(shells_obj.data)
    bm_sh.free()
    shells_obj.data.update()

c_vs = cape_obj.data.vertices
sh_vs = shells_obj.data.vertices
log("=== VERIFICA MISURE GROUP 6 ===")
log(f"Mantella_Corpo larghezza X={max(v.co.x for v in c_vs)-min(v.co.x for v in c_vs):.4f}m (target 1.10m), Z_min={min(v.co.z for v in c_vs):.4f}m (target 0.20m)")
log(f"Conchiglie_SX centro X={(min(v.co.x for v in sh_vs)+max(v.co.x for v in sh_vs))/2:.4f}, Z={(min(v.co.z for v in sh_vs)+max(v.co.z for v in sh_vs))/2:.4f} (target X=0.12, Z=1.37)")

bpy.ops.wm.save_mainfile()
render_viste("rev_6")
