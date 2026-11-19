import bpy
import bmesh
import math
import os
import numpy as np
from mathutils import Vector, Matrix

# Group 6: The cape (two-layer: short ragged shoulder cape + wide 1.10m bell-flaring torn long cape
# with >=6 deep vertical folds, >=20 irregular bottom rags, real geometric holes, 0.006 thickness,
# tall stand-up collar from Group 3, 3 ribbed off-white shells at (+0.12, 1.37),
# and painted UV PNG texture with teal vertical streaks, 0.25m sand fade, and brown stains).

TEX_DIR = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro\texture"
os.makedirs(TEX_DIR, exist_ok=True)
CAPE_TEX_PATH = os.path.join(TEX_DIR, "cape_albedo.png")

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

# Quick fix from Group 4: ensure Strap 1 upper chest brass buckle (+X, Z~1.30) sits proud of strap
ob_belt = bpy.data.objects.get("CinturaCinghie")
if ob_belt:
    for poly in ob_belt.data.polygons:
        if poly.material_index == 2 and 1.275 <= poly.center.z <= 1.325 and poly.center.y < -0.07:
            for vi in poly.vertices:
                ob_belt.data.vertices[vi].co.y -= 0.004
    ob_belt.data.update()

# 1. Generate high-res Cape Albedo PNG texture (1024x1024) in texture/
#    - Base worn teal green sRGB (0.22, 0.34, 0.31)
#    - Lighter vertical streaks sRGB (0.40, 0.52, 0.48)
#    - Lower 0.25m (v < 0.22 in UV where v=0 is bottom hem) fades to dirty sand (0.62, 0.55, 0.43) + brown stains!
W, H = 1024, 1024
rng = np.random.default_rng(42)

# Multi-octave smooth 2D value noise via numpy bilinear upsampling
def smooth_noise_2d(grid_w, grid_h, out_w, out_h, seed_rng):
    base = seed_rng.random((grid_h, grid_w), dtype=np.float32)
    # Periodic horizontal wrap, clamped vertical
    ys = np.linspace(0, grid_h - 1, out_h, endpoint=False)
    xs = np.linspace(0, grid_w, out_w, endpoint=False)
    y0 = np.floor(ys).astype(int)
    y1 = np.minimum(y0 + 1, grid_h - 1)
    fy = (ys - y0)[:, None]
    fy = fy * fy * (3.0 - 2.0 * fy)
    x0 = np.floor(xs).astype(int) % grid_w
    x1 = (x0 + 1) % grid_w
    fx = (xs - np.floor(xs))[None, :]
    fx = fx * fx * (3.0 - 2.0 * fx)
    v00 = base[np.ix_(y0, x0)]
    v10 = base[np.ix_(y0, x1)]
    v01 = base[np.ix_(y1, x0)]
    v11 = base[np.ix_(y1, x1)]
    top = v00 * (1.0 - fx) + v10 * fx
    bot = v01 * (1.0 - fx) + v11 * fx
    return top * (1.0 - fy) + bot * fy

# Vertical streaks (anisotropic: high frequency in X, very low in Y)
streaks = (
    0.55 * smooth_noise_2d(48, 5, W, H, rng) +
    0.30 * smooth_noise_2d(96, 10, W, H, rng) +
    0.15 * smooth_noise_2d(180, 20, W, H, rng)
)
streaks = np.clip((streaks - 0.36) / 0.32, 0.0, 1.0)

# Blotchy fabric wear & brown stains
blotch = (
    0.50 * smooth_noise_2d(14, 14, W, H, rng) +
    0.32 * smooth_noise_2d(28, 28, W, H, rng) +
    0.18 * smooth_noise_2d(64, 64, W, H, rng)
)

# Vertical coordinate v_tex: row 0 in blender image buffer = bottom (hem), row H-1 = top (shoulders)
v_arr = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]

# Lower 0.25m of ~1.20m long cape corresponds to bottom ~21% (v in 0.0..0.24)
sand_mask = np.clip(1.0 - (v_arr - 0.04) / 0.22, 0.0, 1.0)
sand_mask = np.clip(sand_mask + (blotch - 0.5) * 0.28 * (v_arr < 0.34), 0.0, 1.0)

# Brown mud/water stains concentrated near bottom & scattered mid-lower cape
stain_mask = np.clip((blotch - 0.58) / 0.26, 0.0, 1.0) * np.clip(1.0 - v_arr * 1.4, 0.15, 1.0)

col_teal = np.array([0.22, 0.34, 0.31], dtype=np.float32)[None, None, :]
col_streak = np.array([0.40, 0.52, 0.48], dtype=np.float32)[None, None, :]
col_sand = np.array([0.62, 0.55, 0.43], dtype=np.float32)[None, None, :]
col_stain = np.array([0.33, 0.24, 0.16], dtype=np.float32)[None, None, :]

rgb = col_teal * (1.0 - streaks[:, :, None] * 0.72) + col_streak * (streaks[:, :, None] * 0.72)
rgb = rgb * (1.0 - sand_mask[:, :, None]) + col_sand * sand_mask[:, :, None]
rgb = rgb * (1.0 - stain_mask[:, :, None] * 0.75) + col_stain * (stain_mask[:, :, None] * 0.75)

# Fine cloth weave subtle grain
weave = smooth_noise_2d(256, 256, W, H, rng) - 0.5
rgb = np.clip(rgb + weave[:, :, None] * 0.04, 0.03, 0.92)

rgba = np.ones((H, W, 4), dtype=np.float32)
rgba[:, :, :3] = rgb

img = bpy.data.images.get("CapeAlbedo")
if img:
    bpy.data.images.remove(img)
img = bpy.data.images.new("CapeAlbedo", width=W, height=H, alpha=False)
img.pixels.foreach_set(rgba.ravel())
img.filepath_raw = CAPE_TEX_PATH
img.file_format = 'PNG'
img.save()
img.colorspace_settings.name = 'sRGB'

# Create/update MantelloVerde material using CapeAlbedo image texture (works in Blender & GLB!)
mat_cape = bpy.data.materials.get("MantelloVerde") or bpy.data.materials.new("MantelloVerde")
mat_cape.use_nodes = True
nt = mat_cape.node_tree
nt.nodes.clear()
out_n = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
tex_n = nt.nodes.new("ShaderNodeTexImage")
tex_n.image = img
bsdf.inputs["Roughness"].default_value = 0.90
if "Specular IOR Level" in bsdf.inputs:
    bsdf.inputs["Specular IOR Level"].default_value = 0.15
nt.links.new(tex_n.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"], out_n.inputs["Surface"])

# Shell material
mat_shell = bpy.data.materials.get("Conchiglie") or bpy.data.materials.new("Conchiglie")
mat_shell.use_nodes = True
bsdf_s = mat_shell.node_tree.nodes.get("Principled BSDF")
if bsdf_s:
    bsdf_s.inputs["Base Color"].default_value = (*tuple(srgb_to_lin(c) for c in (0.88, 0.85, 0.78)), 1.0)
    bsdf_s.inputs["Roughness"].default_value = 0.45

# 2. Rebuild MantelloVerde mesh in-place:
#    A) Stand-up collar (Z 1.40..1.52 back / 1.48 front corners)
#    B) Long cape (bell-flared to 1.10m wide at bottom, Z=0.20 at back, Z=0.25 at front panels,
#       open front gap 0.32..0.38 wide, behind arms, >=6 folds of 0.03..0.05 depth,
#       >=20 irregular bottom rags of 0.05..0.18 length, 5 geometric holes near edge,
#       kept behind back Z 1.12..1.45 so helmet sits cleanly ON TOP of cape!)
#    C) Short shoulder cape (top layer, Z 1.40 down to Z 1.24 on arms & Z 1.20 on back, ragged edge)

bm = bmesh.new()
uv_layer = bm.loops.layers.uv.new("UVMap")

def set_face_uv(face, uvs):
    for loop, (u, v) in zip(face.loops, uvs):
        loop[uv_layer].uv = (u, v)

# A. Tall Stand-up Collar (UVs mapped to top clean teal part v in 0.85..0.98)
nu_col, nv_col = 32, 4
grid_col = []
for iv in range(nv_col + 1):
    tv = iv / nv_col
    row = []
    for iu in range(nu_col + 1):
        u = -1.0 + 2.0 * (iu / nu_col)
        ang = u * math.radians(130 + 6 * tv)
        rx = 0.086 + 0.036 * (tv ** 0.9)
        ry = 0.082 + 0.026 * (tv ** 0.9)
        z_top = 1.520 - 0.040 * (abs(u) ** 1.4)
        z_bot = 1.392 - 0.005 * abs(u)
        z = z_bot + (z_top - z_bot) * tv
        ripple = 0.003 * math.sin(u * 10.0) * tv
        x = (rx + ripple) * math.sin(ang)
        y = 0.005 + (ry + ripple) * math.cos(ang)
        row.append((bm.verts.new(Vector((x, y, z))), iu / nu_col, 0.84 + 0.14 * tv))
    grid_col.append(row)

col_faces = []
for iv in range(nv_col):
    for iu in range(nu_col):
        v00, u00, w00 = grid_col[iv][iu]
        v10, u10, w10 = grid_col[iv][iu + 1]
        v11, u11, w11 = grid_col[iv + 1][iu + 1]
        v01, u01, w01 = grid_col[iv + 1][iu]
        f = bm.faces.new((v00, v10, v11, v01))
        f.material_index = 0
        set_face_uv(f, [(u00, w00), (u10, w10), (u11, w11), (u01, w01)])
        col_faces.append(f)

# B. Long Cape:
#    64 columns around from front-right panel -> back -> front-left panel
#    22 rows from shoulder line down to ragged bottom hem (Z ~ 0.20 back, 0.25 front)
nu_lc = 64
nv_lc = 22

# Non-periodic irregular rag profile (>= 20 varied triangular rags 0.05..0.18 long)
# At u in [-1, 1]: 0 is back center, +-1 is front panel edges
rag_anchors_u = np.linspace(-1.0, 1.0, 45)
rag_rng = np.random.default_rng(107)
# Alternating high valleys and deep tips of varied widths & lengths (0.05 to 0.18)
rag_depths = np.zeros(45)
for idx in range(45):
    if idx % 2 == 0:
        # Tip (deep)
        rag_depths[idx] = rag_rng.uniform(0.00, 0.06)
    else:
        # Tear notch (high)
        rag_depths[idx] = rag_rng.uniform(0.08, 0.18)

def sample_rag_offset(u):
    return float(np.interp(u, rag_anchors_u, rag_depths))

# Hole centers (u_center, v_center, rx_uv, rv_uv) just above the ragged edge (v near 0.78..0.88)
holes = [
    (-0.68, 0.80, 0.042, 0.048),
    (-0.26, 0.84, 0.036, 0.045),
    ( 0.08, 0.82, 0.045, 0.050),
    ( 0.42, 0.78, 0.040, 0.046),
    ( 0.74, 0.83, 0.038, 0.045),
]

grid_lc = []
for iv in range(nv_lc + 1):
    tv = iv / nv_lc  # 0 = top shoulder/collar, 1 = ragged bottom
    row = []
    for iu in range(nu_lc + 1):
        tu = iu / nu_lc
        u = -1.0 + 2.0 * tu  # -1 (front-right panel) .. 0 (back) .. +1 (front-left panel)

        # Angle around body (0 = +Y back, +pi/2 = +X left, -pi/2 = -X right)
        # Keep front opening gap 0.34..0.38 wide across chest/legs (max_ang ~ 132 deg -> front edges at +-0.18..+-0.22)
        # AND pass BEHIND arms (arms sit at Y=0, X=+-0.18..+-0.66)!
        # So at upper body (tv < 0.38), front panels curve smoothly behind arms (max_ang ~ 122 deg at chest, widening cleanly below!)
        if tv < 0.12:
            # Anchored under stand-up collar & shoulder cape behind shoulders
            max_ang = math.radians(128)
        elif tv < 0.42:
            # Passes cleanly BEHIND arms (Y > 0.04 at sides) while front inner lapels frame jacket
            max_ang = math.radians(118 + 8 * math.sin((tv - 0.12) / 0.30 * math.pi))
        else:
            # Flares out wide into bell below waist/arms: front panel edges sit around +-0.22..+-0.26 (gap ~0.44? Wait: keep gap 0.34..0.38!)
            max_ang = math.radians(134)

        ang = u * max_ang

        # Base bottom height Z: 0.20 at back (u=0), 0.25 at front panels (|u|=1), plus irregular rag cuts!
        z_tip_base = 0.20 + 0.05 * (abs(u) ** 1.3)
        z_bot = z_tip_base + sample_rag_offset(u)
        z_top = 1.395 - 0.025 * (abs(u) ** 1.6)
        z = z_top * (1.0 - tv) + z_bot * tv

        # Bell flare width: at bottom reaches 1.10m across (rx = 0.55m!)
        # At top rx ~ 0.15m (behind collar/shoulders), flaring smoothly to rx = 0.55m at tv=1!
        rx = 0.155 + 0.405 * (tv ** 1.15)

        # Depth Y & side clearance:
        # Back legs are around Y=+0.05..+0.06 -> cape back should stand 0.10..0.15 away (Y = +0.16..+0.20)
        # Front panels stay outside legs (X ~ +-0.18..+-0.26 at front edge) and behind arms (at Z>0.90)!
        ry_back = 0.105 + 0.085 * (tv ** 1.05)

        # 7 deep vertical folds (0.035..0.045 depth) running from shoulders to bottom edge!
        # Suppress folds slightly right behind the diving helmet (z in 1.10..1.42 and |u| < 0.32) so helmet rests cleanly ON TOP!
        helmet_zone = 1.0
        if 1.05 < z < 1.44 and abs(u) < 0.35:
            helmet_zone = 0.25 + 0.75 * (abs(u) / 0.35)

        fold_amp = (0.038 * (tv ** 0.85)) * helmet_zone
        fold_wave = math.sin(u * math.pi * 7.0)  # 7 full fold waves across back & sides!
        fold_sub = 0.010 * math.cos(u * math.pi * 13.0 + 0.7) * (tv ** 1.1)

        r_x_eff = rx + (fold_amp * fold_wave + fold_sub) * 0.45
        r_y_eff = ry_back + fold_amp * fold_wave + fold_sub

        x = r_x_eff * math.sin(ang)
        y = 0.020 + r_y_eff * math.cos(ang)

        # Guarantee cape stays behind arms (arms are at Y=0.0, radius 0.055 at Z 1.0..1.38, |X|>0.18)
        if 0.85 <= z <= 1.40 and abs(x) > 0.165:
            # Push cape behind arm corridor (Y >= 0.068)
            min_y = 0.068 * max(0.0, min(1.0, (z - 0.85) / 0.25))
            if y < min_y:
                y = min_y

        # Guarantee cape stays behind diving helmet clearance? No! Helmet is ON TOP of cape (Y +0.11..+0.40, Z 1.13..1.47)
        # So cape must stay in front of helmet front (Y <= +0.125) in helmet back region (|x|<0.16, z>1.08)
        if 1.08 <= z <= 1.44 and abs(x) < 0.16:
            y = min(y, 0.118)

        # Guarantee cape stays outside front torso/hips/pockets
        if y < 0.0:
            min_abs_x = 0.165 + 0.06 * tv
            if abs(x) < min_abs_x:
                x = math.copysign(min_abs_x, x if abs(x) > 1e-4 else u)

        # UV: u_tex = tu (0..1), v_tex = 1.0 - tv (1 at top, 0 at bottom hem -> matches 0.25m sand fade!)
        v_uv = max(0.0, min(1.0, (z - 0.20) / 1.20))
        row.append((bm.verts.new(Vector((x, y, z))), tu, v_uv))
    grid_lc.append(row)

lc_faces = []
for iv in range(nv_lc):
    for iu in range(nu_lc):
        tu_mid = (iu + 0.5) / nu_lc
        u_mid = -1.0 + 2.0 * tu_mid
        tv_mid = (iv + 0.5) / nv_lc
        # Check if inside any geometric tear hole
        in_hole = False
        for hu, hv, hru, hrv in holes:
            if ((u_mid - hu) / hru) ** 2 + ((tv_mid - hv) / hrv) ** 2 < 1.0:
                in_hole = True
                break
        if in_hole:
            continue
        v00, u00, w00 = grid_lc[iv][iu]
        v10, u10, w10 = grid_lc[iv][iu + 1]
        v11, u11, w11 = grid_lc[iv + 1][iu + 1]
        v01, u01, w01 = grid_lc[iv + 1][iu]
        f = bm.faces.new((v00, v10, v11, v01))
        f.material_index = 0
        set_face_uv(f, [(u00, w00), (u10, w10), (u11, w11), (u01, w01)])
        lc_faces.append(f)

# C. Short Shoulder Cape (top layer, 6.2):
#    Covers both shoulders and top of upper arms, from collar (Z 1.40) down to Z 1.24 on arms & Z 1.20 on back,
#    cut into irregular ragged points at its bottom edge!
nu_sc = 36
nv_sc = 7
sc_rag_u = np.linspace(-1.0, 1.0, 23)
sc_rag_z = np.array([0.04 if i % 2 == 0 else -0.025 for i in range(23)])

grid_sc = []
for iv in range(nv_sc + 1):
    tv = iv / nv_sc
    row = []
    for iu in range(nu_sc + 1):
        tu = iu / nu_sc
        u = -1.0 + 2.0 * tu  # -1 (front-right chest) .. 0 (back) .. +1 (front-left chest)
        ang = u * math.radians(146)  # wraps around to front collarbone X=+-0.12!

        # Height: top 1.405 at collar -> ragged bottom ~1.24 over arms (|u| ~ 0.45..0.8), ~1.20 at back (u=0), ~1.30 at front chest
        z_top = 1.406 - 0.012 * (abs(u) ** 1.5)
        rag_dz = float(np.interp(u, sc_rag_u, sc_rag_z))
        z_bot = 1.200 + 0.055 * (abs(u) ** 1.2) + 0.055 * max(0.0, abs(u) - 0.72) / 0.28 + rag_dz
        z = z_top * (1.0 - tv) + z_bot * tv

        # Radial wrap: flares smoothly out over the puffy upper arm shoulders!
        # Shoulder top X at Z=1.40 is ~0.20, at Z=1.24 arm X is ~0.34!
        # Keep front chest edge neatly at |X| >= 0.095..0.115 so jacket & cross straps remain visible
        shoulder_arc = math.sin(min(1.0, tv * 1.4) * math.pi * 0.5)
        rx = 0.095 + 0.210 * shoulder_arc + 0.045 * (tv ** 1.3)
        ry = 0.090 + 0.032 * shoulder_arc + 0.012 * (tv ** 1.2)

        fold = 0.009 * math.sin(u * math.pi * 6.0) * tv
        x = (rx + fold) * math.sin(ang)
        y = 0.005 + (ry + fold) * math.cos(ang)

        # Keep back of shoulder cape tucked cleanly in front of diving helmet (Y <= 0.112 at |X|<0.15)
        if abs(x) < 0.155 and y > 0.112:
            y = 0.112
        # Keep front-chest collarbone drape hugging jacket (Y around -0.088..-0.105)
        if y < -0.06 and abs(x) > 0.14:
            # Flare over arms slightly forward/outward so arms never poke through top of shoulder cape!
            y = max(y, -0.065 - 0.015 * (1.0 - tv))

        v_uv = 0.60 + 0.35 * (1.0 - tv)
        row.append((bm.verts.new(Vector((x, y, z))), tu, v_uv))
    grid_sc.append(row)

sc_faces = []
for iv in range(nv_sc):
    for iu in range(nu_sc):
        v00, u00, w00 = grid_sc[iv][iu]
        v10, u10, w10 = grid_sc[iv][iu + 1]
        v11, u11, w11 = grid_sc[iv + 1][iu + 1]
        v01, u01, w01 = grid_sc[iv + 1][iu]
        f = bm.faces.new((v00, v10, v11, v01))
        f.material_index = 0
        set_face_uv(f, [(u00, w00), (u10, w10), (u11, w11), (u01, w01)])
        sc_faces.append(f)

# Solidify all three cape layers (thickness 0.006) preserving UVs!
bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.006)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

ob_cape = bpy.data.objects.get("MantelloVerde")
ob_cape.data.materials.clear()
ob_cape.data.materials.append(mat_cape)
bm.to_mesh(ob_cape.data)
bm.free()
for p in ob_cape.data.polygons:
    p.use_smooth = True
ob_cape.data.update()

# 3. Rebuild MantelloDettagli (6.7): 3 sculpted ribbed white shells at LEFT collarbone (X +0.12, Z 1.37)
#    (Also keep single clean placeholder or drop old wrong right-side strip — 7.5 will add the left-side torn cloth cleanly!)
bm_d = bmesh.new()

def add_scallop_shell(bm_target, center, normal, up_dir, radius, mat_idx=0):
    # Builds a real fan-shaped ribbed scallop shell
    nrm = normal.normalized()
    up = (up_dir - nrm * up_dir.dot(nrm)).normalized()
    right = up.cross(nrm).normalized()
    n_ribs = 9
    n_rings = 4
    verts_grid = []
    # Hinge base point
    v_hinge = bm_target.verts.new(center - up * (radius * 0.45))
    for ir in range(1, n_rings + 1):
        tr = ir / n_rings
        r_cur = radius * (0.35 + 0.65 * tr)
        row = []
        for k in range(n_ribs):
            tk = -1.0 + 2.0 * (k / (n_ribs - 1))  # -1..+1
            ang = tk * math.radians(62)
            # Fluted radial ribs
            flute = 0.0022 * math.cos(k * math.pi) * math.sin(tr * math.pi * 0.85)
            dome = 0.0045 * math.sin(tr * math.pi * 0.85) * (1.0 - 0.5 * tk * tk)
            p = (center - up * (radius * 0.35)
                 + up * (r_cur * math.cos(ang))
                 + right * (r_cur * math.sin(ang))
                 + nrm * (dome + flute))
            row.append(bm_target.verts.new(p))
        verts_grid.append(row)
    # Fan triangles from hinge to first ring
    for k in range(n_ribs - 1):
        f = bm_target.faces.new((v_hinge, verts_grid[0][k], verts_grid[0][k + 1]))
        f.material_index = mat_idx
    # Quads across rings
    for ir in range(n_rings - 1):
        for k in range(n_ribs - 1):
            f = bm_target.faces.new((verts_grid[ir][k], verts_grid[ir + 1][k], verts_grid[ir + 1][k + 1], verts_grid[ir][k + 1]))
            f.material_index = mat_idx
    bmesh.ops.solidify(bm_target, geom=[f for f in bm_target.faces if v_hinge in f.verts or any(v in verts_grid[-1] for v in f.verts)], thickness=0.003)

# Cluster of 3 shells pinned on cape at front of LEFT collarbone (X +0.12, Z 1.37)
shell_specs = [
    (Vector((0.114, -0.072, 1.374)), Vector((0.35, -0.90, 0.25)), Vector((-0.2, 0.1, 1.0)), 0.015),
    (Vector((0.132, -0.065, 1.364)), Vector((0.45, -0.85, 0.25)), Vector((0.1, 0.1, 1.0)),  0.013),
    (Vector((0.105, -0.078, 1.356)), Vector((0.28, -0.92, 0.20)), Vector((-0.3, 0.1, 0.9)), 0.011),
]
for pos, nrm, upd, rad in shell_specs:
    add_scallop_shell(bm_d, pos, nrm, upd, rad, mat_idx=0)

bmesh.ops.recalc_face_normals(bm_d, faces=bm_d.faces[:])
ob_md = bpy.data.objects.get("MantelloDettagli")
ob_md.data.materials.clear()
ob_md.data.materials.append(mat_shell)
bm_d.to_mesh(ob_md.data)
bm_d.free()
for p in ob_md.data.polygons:
    p.use_smooth = True
ob_md.data.update()

# Log Group 6 stats
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in ("MantelloVerde", "MantelloDettagli"):
    ob = bpy.data.objects.get(name)
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    pts = [ob.matrix_world @ v.co for v in me.vertices]
    log(f"{name}: tris={len(me.loop_triangles)}, X=({min(p.x for p in pts):.3f}..{max(p.x for p in pts):.3f}), width={max(p.x for p in pts)-min(p.x for p in pts):.3f}, Z=({min(p.z for p in pts):.3f}..{max(p.z for p in pts):.3f})")
    ev.to_mesh_clear()

bpy.ops.wm.save_mainfile()
render_viste("rev_6")
