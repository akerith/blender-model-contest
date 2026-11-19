import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Matrix, Euler

# ==============================================================================
# PASSO 1: Impostazione scena, luci, materiali e corpo base (testa, capelli,
#          torso, giacca, maniche, pantaloni, ginocchiera, stivali, guanti)
# ==============================================================================

# 1. Pulizia scena
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
for img in list(bpy.data.images):
    bpy.data.images.remove(img)

scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'
scn.unit_settings.scale_length = 1.0

# Impostazione motore di render e illuminazione studio
if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys():
    scn.render.engine = "BLENDER_EEVEE_NEXT"
elif "BLENDER_EEVEE" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys():
    scn.render.engine = "BLENDER_EEVEE"

# World background grigio scuro neutro con luce ambientale morbida
if not scn.world:
    scn.world = bpy.data.worlds.new("World")
scn.world.use_nodes = True
wnodes = scn.world.node_tree.nodes
bg_node = wnodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.14, 0.145, 0.155, 1.0)
    bg_node.inputs[1].default_value = 0.85

def add_light(name, ltype, loc, rot_deg, energy, color=(1.0, 1.0, 1.0), size=1.5):
    ldata = bpy.data.lights.new(name, type=ltype)
    ldata.energy = energy
    ldata.color = color
    if hasattr(ldata, "size"):
        ldata.size = size
    lobj = bpy.data.objects.new(name, ldata)
    scn.collection.objects.link(lobj)
    lobj.location = loc
    lobj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    return lobj

# Key light (calda frontale-destra), Fill light (morbida sinistra), Rim/Back light (per retro e contorni)
add_light("Luce_Key", "SUN", (2.5, -3.0, 3.5), (48, 12, 32), 2.8, (1.0, 0.96, 0.90))
add_light("Luce_Fill", "SUN", (-3.0, -2.0, 2.2), (55, -15, -42), 1.3, (0.88, 0.93, 1.0))
add_light("Luce_Back", "SUN", (0.5, 3.2, 3.0), (-48, 8, 165), 2.2, (0.98, 0.95, 0.88))

# ==============================================================================
# 2. Generatore di texture procedurali via codice (compatibili glTF e Blender)
# ==============================================================================
def make_noise_tex(name, c1, c2, roughness_var=0.08, scale=8.0, grad_z=0.0, size=256):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    y, x = np.mgrid[0:size, 0:size] / float(size)
    # Rumore multi-frequenza deterministico
    n = (
        0.50 * np.sin(2 * math.pi * (x * scale + 0.3 * np.cos(2 * math.pi * y * scale))) *
               np.cos(2 * math.pi * (y * scale - 0.3 * np.sin(2 * math.pi * x * scale)))
        + 0.30 * np.sin(2 * math.pi * (x * scale * 2.3 + y * scale * 1.7 + 1.2))
        + 0.20 * np.cos(2 * math.pi * (x * scale * 5.1 - y * scale * 4.3 + 2.7))
    )
    t = np.clip(0.5 + 0.45 * n + grad_z * (0.5 - y), 0.0, 1.0)
    pixels = np.ones((size, size, 4), dtype=np.float32)
    for ch in range(3):
        pixels[:, :, ch] = c1[ch] * (1.0 - t) + c2[ch] * t
    img.pixels.foreach_set(pixels.ravel())
    img.pack()
    return img

def make_mat(name, base_col, rough=0.65, metal=0.0, tex_col2=None, tex_scale=6.0, grad_z=0.0, emission=None, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base_col, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 2.5
    if alpha < 1.0 and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    if tex_col2 is not None:
        img = make_noise_tex(name + "_tex", base_col, tex_col2, scale=tex_scale, grad_z=grad_z)
        tnode = nodes.new("ShaderNodeTexImage")
        tnode.image = img
        links.new(tnode.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

MATS = {
    "pelle": make_mat("Mat_Pelle", (0.76, 0.56, 0.45), rough=0.52, tex_col2=(0.68, 0.47, 0.37), tex_scale=3.0),
    "labbra": make_mat("Mat_Labbra", (0.56, 0.31, 0.28), rough=0.42),
    "occhio_bianco": make_mat("Mat_OcchioBianco", (0.92, 0.90, 0.88), rough=0.15),
    "iride": make_mat("Mat_Iride", (0.22, 0.14, 0.09), rough=0.12),
    "pupilla": make_mat("Mat_Pupilla", (0.02, 0.02, 0.02), rough=0.08),
    "capelli_scuri": make_mat("Mat_CapelliScuri", (0.09, 0.075, 0.065), rough=0.58, tex_col2=(0.15, 0.12, 0.10), tex_scale=10.0),
    "capelli_bianchi": make_mat("Mat_CapelliBianchi", (0.82, 0.80, 0.76), rough=0.48, tex_col2=(0.62, 0.60, 0.57), tex_scale=8.0),
    "camicia": make_mat("Mat_Camicia", (0.56, 0.52, 0.45), rough=0.78, tex_col2=(0.44, 0.40, 0.34), tex_scale=7.0),
    "giacca_blu": make_mat("Mat_GiaccaBlu", (0.14, 0.19, 0.23), rough=0.68, tex_col2=(0.20, 0.26, 0.30), tex_scale=6.0),
    "pantaloni": make_mat("Mat_Pantaloni", (0.24, 0.21, 0.18), rough=0.76, tex_col2=(0.17, 0.15, 0.13), tex_scale=7.0),
    "cuoio_scuro": make_mat("Mat_CuoioScuro", (0.18, 0.12, 0.08), rough=0.48, tex_col2=(0.25, 0.17, 0.11), tex_scale=6.0),
    "cuoio_medio": make_mat("Mat_CuoioMedio", (0.29, 0.19, 0.12), rough=0.52, tex_col2=(0.21, 0.13, 0.08), tex_scale=6.0),
    "cuoio_chiaro": make_mat("Mat_CuoioChiaro", (0.48, 0.37, 0.26), rough=0.62, tex_col2=(0.36, 0.27, 0.18), tex_scale=7.0),
    "ottone": make_mat("Mat_Ottone", (0.64, 0.47, 0.22), rough=0.34, metal=0.85, tex_col2=(0.45, 0.32, 0.14), tex_scale=6.0),
    "metallo_scuro": make_mat("Mat_MetalloScuro", (0.22, 0.21, 0.19), rough=0.42, metal=0.75),
}

# ==============================================================================
# 3. Funzioni geometriche di supporto (tubi profilati, loft, UV automatiche)
# ==============================================================================
def finalize_obj(obj, mat, smooth=True):
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    # Genera una mappa UV cilindrica/box semplice così le texture procedurali funzionano ovunque
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        f.smooth = smooth
        for loop in f.loops:
            co = loop.vert.co
            u = 0.5 + math.atan2(co.x, -co.y) / (2 * math.pi)
            v = (co.z) * 1.2
            loop[uv_layer].uv = (u, v)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj

def create_profiled_tube(name, centers, radii_xy, mat, rot_angles=None, segs=18, cap_ends=True, fold_amp=0.0, fold_freq=6):
    """Crea una mesh tubolare lungo una serie di centri 3D con raggi (rx, ry) ed eventuali pieghe."""
    bm = bmesh.new()
    rings = []
    n_rings = len(centers)
    for i in range(n_rings):
        c = Vector(centers[i])
        rx, ry = radii_xy[i] if isinstance(radii_xy[i], (tuple, list)) else (radii_xy[i], radii_xy[i])
        # Calcolo tangente
        if i == 0:
            t = (Vector(centers[1]) - c).normalized()
        elif i == n_rings - 1:
            t = (c - Vector(centers[-2])).normalized()
        else:
            t = (Vector(centers[i + 1]) - Vector(centers[i - 1])).normalized()
        # Base ortonormale
        up = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
        b1 = t.cross(up).normalized()
        b2 = b1.cross(t).normalized()
        if rot_angles and rot_angles[i] != 0:
            ang = rot_angles[i]
            b1_new = b1 * math.cos(ang) + b2 * math.sin(ang)
            b2 = -b1 * math.sin(ang) + b2 * math.cos(ang)
            b1 = b1_new

        ring_verts = []
        v_param = i / max(1, n_rings - 1)
        for j in range(segs):
            theta = 2.0 * math.pi * j / segs
            r_mod = 1.0
            if fold_amp != 0.0:
                r_mod += fold_amp * math.sin(v_param * math.pi * fold_freq + 2.0 * theta) * math.sin(v_param * math.pi)
            pt = c + b1 * (rx * r_mod * math.cos(theta)) + b2 * (ry * r_mod * math.sin(theta))
            ring_verts.append(bm.verts.new(pt))
        rings.append(ring_verts)

    for i in range(n_rings - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))

    if cap_ends:
        for idx, invert in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                if invert:
                    bm.faces.new((rings[idx][jn], rings[idx][j], cv))
                else:
                    bm.faces.new((rings[idx][j], rings[idx][jn], cv))

    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scn.collection.objects.link(obj)
    return finalize_obj(obj, mat, smooth=True)

# ==============================================================================
# 4. TESTA, VOLTO SCOLPITO, OCCHI, SOPRACCIGLIA E CAPELLI CON CIOCCA BIANCA
# ==============================================================================
def build_head_and_hair():
    # Costruzione testa da sfera UV rimodellata con funzioni anatomiche
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=24, radius=1.0)
    head_center = Vector((0.0, -0.01, 1.56))

    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        # Proporzioni base del cranio femminile
        rx = 0.074
        ry = 0.088
        rz = 0.098
        # Restringimento mandibola e mento (parte inferiore anteriore)
        if z < 0.0:
            jaw_t = min(1.0, -z)
            rx *= (1.0 - 0.34 * (jaw_t ** 1.15))
            ry *= (1.0 - 0.16 * (jaw_t ** 1.3))
        px = x * rx
        py = y * ry
        pz = z * rz

        # Fronte e zigomi (verso -Y che è la faccia anteriore)
        if y < -0.15:
            front = min(1.0, (-y - 0.15) / 0.85)
            # Zigomi
            cheek = math.exp(-((abs(x) - 0.52) ** 2 / 0.09 + (z + 0.12) ** 2 / 0.06))
            px += math.copysign(0.006 * cheek * front, x)
            py -= 0.005 * cheek * front
            # Cavità oculari
            eye_socket = math.exp(-((abs(x) - 0.38) ** 2 / 0.045 + (z - 0.02) ** 2 / 0.032))
            py += 0.0085 * eye_socket * front
            # Arcata sopraccigliare
            brow = math.exp(-((abs(x) - 0.36) ** 2 / 0.07 + (z - 0.16) ** 2 / 0.018))
            py -= 0.0055 * brow * front
            # Ponte e punta del naso
            nose_bridge = math.exp(-(x ** 2 / 0.016 + (z + 0.06) ** 2 / 0.055))
            nose_tip = math.exp(-(x ** 2 / 0.018 + (z + 0.24) ** 2 / 0.018))
            py -= (0.013 * nose_bridge + 0.018 * nose_tip) * front
            pz -= 0.003 * nose_tip * front
            # Mento pronunciato
            chin = math.exp(-(x ** 2 / 0.045 + (z + 0.82) ** 2 / 0.04))
            py -= 0.009 * chin * front
            pz -= 0.005 * chin * front

        v.co = head_center + Vector((px, py, pz))

    mesh = bpy.data.meshes.new("Testa")
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    head_obj = bpy.data.objects.new("Testa", mesh)
    scn.collection.objects.link(head_obj)
    finalize_obj(head_obj, MATS["pelle"], smooth=True)

    # Labbra (superiore e inferiore) per dare definizione al viso
    for lip_name, z_off, y_off, rz_s, col_mat in [
        ("Labbro_Sup", 1.500, -0.091, 0.0045, MATS["labbra"]),
        ("Labbro_Inf", 1.493, -0.090, 0.0050, MATS["labbra"]),
    ]:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=1.0)
        for v in bm.verts:
            x_w = v.co.x * 0.019
            t_edge = max(0.0, 1.0 - (v.co.x ** 2))
            cupid = -0.0012 * math.cos(v.co.x * math.pi * 2) if "Sup" in lip_name else 0.0
            v.co = Vector((
                x_w,
                y_off - v.co.y * 0.006 * t_edge + 0.003 * (v.co.x ** 2),
                z_off + v.co.z * rz_s * t_edge + cupid
            ))
        m = bpy.data.meshes.new(lip_name)
        bm.to_mesh(m)
        bm.free()
        o = bpy.data.objects.new(lip_name, m)
        scn.collection.objects.link(o)
        finalize_obj(o, col_mat, smooth=True)

    # Occhi (sclera, iride, pupilla, palpebra/ciglia superiori, sopracciglia, orecchie)
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        ex, ey, ez = sx * 0.028, -0.080, 1.560
        # Bulbo oculare
        for part_n, r_s, y_shift, mat_k in [
            (f"Occhio_{side}", (0.011, 0.009, 0.0085), 0.0, "occhio_bianco"),
            (f"Iride_{side}", (0.0058, 0.003, 0.0058), -0.0072, "iride"),
            (f"Pupilla_{side}", (0.0030, 0.002, 0.0030), -0.0082, "pupilla"),
        ]:
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
            for v in bm.verts:
                v.co = Vector((ex + v.co.x * r_s[0], ey + y_shift + v.co.y * r_s[1], ez + v.co.z * r_s[2]))
            m = bpy.data.meshes.new(part_n)
            bm.to_mesh(m)
            bm.free()
            o = bpy.data.objects.new(part_n, m)
            scn.collection.objects.link(o)
            finalize_obj(o, MATS[mat_k], smooth=True)

        # Sopracciglia espressive (leggermente aggrottate da esploratrice)
        brow_pts = [
            (sx * 0.012, -0.088, 1.572),
            (sx * 0.026, -0.091, 1.577),
            (sx * 0.040, -0.086, 1.576),
            (sx * 0.049, -0.077, 1.571),
        ]
        create_profiled_tube(f"Sopracciglio_{side}", brow_pts, [0.0028, 0.0035, 0.0030, 0.0015], MATS["capelli_scuri"], segs=8)

        # Ciglia superiori / rima palpebrale
        lash_pts = [
            (sx * 0.017, -0.085, 1.562),
            (sx * 0.028, -0.089, 1.565),
            (sx * 0.039, -0.084, 1.561),
        ]
        create_profiled_tube(f"Ciglia_{side}", lash_pts, [0.0016, 0.0022, 0.0016], MATS["pupilla"], segs=6)

        # Orecchie
        ear_pts = [
            (sx * 0.068, -0.008, 1.535),
            (sx * 0.075, -0.002, 1.552),
            (sx * 0.074, 0.003, 1.568),
        ]
        create_profiled_tube(f"Orecchio_{side}", ear_pts, [(0.006, 0.010), (0.007, 0.013), (0.005, 0.009)], MATS["pelle"], segs=8)

    # Collo anatomico
    neck_pts = [
        (0.0, 0.005, 1.375),
        (0.0, 0.000, 1.425),
        (0.0, -0.006, 1.475),
    ]
    create_profiled_tube("Collo", neck_pts, [(0.056, 0.052), (0.048, 0.046), (0.050, 0.048)], MATS["pelle"], segs=18)

    # Calotta base dei capelli scuri
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=18, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        if z < -0.35 and y < -0.15:
            # Lascia scoperto il viso davanti
            z = -0.10
            y = 0.05
        wave = 1.0 + 0.04 * math.sin(x * 9.0 + z * 6.0) * math.cos(y * 8.0)
        v.co = Vector((
            x * 0.086 * wave,
            -0.004 + y * 0.097 * wave,
            1.578 + z * 0.098 * wave
        ))
    m_hair = bpy.data.meshes.new("Capelli_Calotta")
    bm.to_mesh(m_hair)
    bm.free()
    o_hair = bpy.data.objects.new("Capelli_Calotta", m_hair)
    scn.collection.objects.link(o_hair)
    finalize_obj(o_hair, MATS["capelli_scuri"], smooth=True)

    # Ciocche di capelli scuri mosse (attorno a nuca, tempie, lati e sommità fino a Z=1.70)
    n_locks = 26
    for i in range(n_locks):
        ang = -math.pi * 0.78 + (math.pi * 1.56) * (i / (n_locks - 1))
        # ang=0 è dietro (+Y), ang=+-pi è davanti (-Y)
        sx = math.sin(ang)
        cy = math.cos(ang)
        is_front_side = abs(ang) > math.pi * 0.58
        top_z = 1.685 + 0.014 * math.sin(i * 1.7)
        mid_r = 0.092 + 0.008 * (i % 3)
        end_z = 1.545 if is_front_side else (1.485 + 0.025 * (i % 2))
        flare = 0.016 * (1 if i % 2 == 0 else -1)
        pts = [
            (sx * 0.025, cy * 0.025, top_z),
            (sx * 0.072, cy * 0.076, 1.650),
            (sx * mid_r, cy * (mid_r + 0.006), 1.595),
            (sx * (mid_r + 0.008) + flare * 0.4, cy * (mid_r + 0.005), 1.540),
            (sx * (mid_r + 0.014) + flare, cy * (mid_r + 0.010), end_z),
        ]
        rads = [(0.014, 0.009), (0.022, 0.013), (0.024, 0.014), (0.018, 0.011), (0.005, 0.004)]
        create_profiled_tube(f"Ciocca_Scura_{i:02d}", pts, rads, MATS["capelli_scuri"], segs=8)

    # Ciocche frontali scure sul lato destro (-X)
    for k, x_off in enumerate((-0.025, -0.052, -0.074)):
        pts = [
            (-0.010, -0.035, 1.675),
            (x_off * 0.85, -0.082, 1.645),
            (x_off * 1.15, -0.095, 1.602 - k * 0.012),
            (x_off * 1.30 - 0.010, -0.082, 1.555 - k * 0.018),
        ]
        create_profiled_tube(f"Ciocca_FronteDX_{k}", pts, [(0.012, 0.008), (0.018, 0.011), (0.016, 0.010), (0.004, 0.003)], MATS["capelli_scuri"], segs=8)

    # CARATTERISTICA CIOCCA BIANCA sul lato sinistro del personaggio (+X, a destra guardando di fronte)
    white_locks = [
        [
            (0.004, -0.045, 1.676),
            (0.028, -0.088, 1.652),
            (0.055, -0.098, 1.615),
            (0.076, -0.086, 1.572),
            (0.088, -0.068, 1.538),
        ],
        [
            (0.012, -0.032, 1.682),
            (0.042, -0.082, 1.660),
            (0.068, -0.092, 1.622),
            (0.085, -0.074, 1.580),
        ],
        [
            (-0.002, -0.052, 1.668),
            (0.018, -0.093, 1.640),
            (0.040, -0.098, 1.608),
        ],
    ]
    for idx, wpts in enumerate(white_locks):
        rads = [(0.012, 0.008), (0.019, 0.011), (0.017, 0.010), (0.011, 0.007), (0.004, 0.003)][:len(wpts)]
        create_profiled_tube(f"Ciocca_Bianca_{idx}", wpts, rads, MATS["capelli_bianchi"], segs=8)

build_head_and_hair()

# ==============================================================================
# 5. TORSO, GIACCA BLU-ARDESIA, COLLETTO INTERNO E FALDE (PEPLUM)
# ==============================================================================
def build_torso_and_jacket():
    # Profilo del busto/giacca da Z=0.84 (fianchi/falda) a Z=1.39 (spalle/collo)
    torso_z = [0.83, 0.88, 0.94, 1.00, 1.06, 1.13, 1.20, 1.26, 1.32, 1.37, 1.395]
    # Raggi (rx=semilarghezza, ry=semiprofondità) e offset Y
    torso_spec = [
        # (z, rx, ry, y_off)
        (0.83, 0.172, 0.118, 0.005),   # Bordo inferiore falda giacca (peplum)
        (0.88, 0.165, 0.112, 0.004),   # Fianchi superiori
        (0.94, 0.148, 0.102, 0.002),   # Vita bassa (sotto cintura)
        (1.00, 0.130, 0.094, 0.000),   # Punto vita stretto
        (1.06, 0.134, 0.098, -0.002),  # Vita alta
        (1.13, 0.144, 0.106, -0.006),  # Costato inferiore
        (1.20, 0.156, 0.118, -0.012),  # Petto/seno
        (1.26, 0.158, 0.114, -0.008),  # Petto alto
        (1.32, 0.172, 0.100, 0.000),   # Linea clavicole/spalle
        (1.37, 0.145, 0.082, 0.004),   # Sommità spalle
        (1.395, 0.072, 0.064, 0.004),  # Base collo
    ]
    bm = bmesh.new()
    segs = 32
    rings = []
    for z, rx, ry, y_off in torso_spec:
        ring = []
        for j in range(segs):
            th = 2.0 * math.pi * j / segs
            cx = math.cos(th)
            sy = math.sin(th)
            # Modellazione anatomica del busto anteriore (sy < 0 è fronte -Y)
            r_x, r_y = rx, ry
            if 1.14 <= z <= 1.28 and sy < -0.15:
                bust = math.exp(-((abs(cx) - 0.45) ** 2 / 0.12 + (z - 1.21) ** 2 / 0.0035))
                r_y += 0.018 * bust * (-sy)
            # Leggera apertura frontale sulla falda inferiore (z < 0.92)
            if z < 0.92 and sy < -0.85:
                r_y *= 0.95
            # Pieghe verticali sul tessuto della giacca
            fold = 0.003 * math.sin(th * 10.0) * (1.0 if z < 0.96 else 0.4)
            pt = Vector(((r_x + fold) * cx, y_off + (r_y + fold) * sy, z))
            ring.append(bm.verts.new(pt))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for j in range(segs):
            jn = (j + 1) % segs
            bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))

    # Chiudi fondo e cima
    for idx, inv in ((0, True), (-1, False)):
        c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
        cv = bm.verts.new(c_pt)
        for j in range(segs):
            jn = (j + 1) % segs
            bm.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))

    m_torso = bpy.data.meshes.new("Giacca_Torso")
    bm.normal_update()
    bm.to_mesh(m_torso)
    bm.free()
    o_torso = bpy.data.objects.new("Giacca_Torso", m_torso)
    scn.collection.objects.link(o_torso)
    finalize_obj(o_torso, MATS["giacca_blu"], smooth=True)

    # Camicia/colletto beige interno visibile attorno al collo e sullo scollo a V
    collar_pts = [
        (0.0, -0.015, 1.335),
        (0.0, -0.005, 1.385),
        (0.0, 0.000, 1.425),
    ]
    create_profiled_tube("Camicia_Colletto", collar_pts, [(0.078, 0.072), (0.068, 0.064), (0.062, 0.058)], MATS["camicia"], segs=20, fold_amp=0.04, fold_freq=4)

    # Pannelli/cuciture orizzontali sul petto della giacca blu (come nel riferimento)
    for z_band in (1.09, 1.15, 1.22):
        band_pts = []
        for k in range(11):
            t = -1.0 + 2.0 * k / 10.0
            ang = -math.pi * 0.5 + t * 0.95
            rx = 0.148 if z_band < 1.18 else 0.158
            ry = 0.114 if z_band < 1.18 else 0.125
            band_pts.append((rx * math.cos(ang), -0.008 + ry * math.sin(ang), z_band))
        create_profiled_tube(f"Fascia_Petto_{int(z_band*100)}", band_pts, [(0.007, 0.011)] * len(band_pts), MATS["giacca_blu"], segs=8)

    # Bacino interno per unire torso e gambe senza fessure
    pelvis_pts = [(0.0, 0.005, 0.79), (0.0, 0.005, 0.85), (0.0, 0.004, 0.91)]
    create_profiled_tube("Bacino_Pantaloni", pelvis_pts, [(0.135, 0.095), (0.152, 0.104), (0.148, 0.100)], MATS["pantaloni"], segs=20)

build_torso_and_jacket()

# ==============================================================================
# 6. GAMBE, PANTALONI, GINOCCHIERA DESTRA, FASCE E STIVALI ALLACCIATI
# ==============================================================================
def build_legs_and_boots():
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        # 1. Pantaloni (dalla pelvi Z=0.84 fino a sotto il ginocchio Z=0.40)
        pant_centers = [
            (sx * 0.088, 0.006, 0.84),
            (sx * 0.094, 0.003, 0.74),
            (sx * 0.098, -0.002, 0.64),
            (sx * 0.103, -0.008, 0.55),
            (sx * 0.106, -0.010, 0.48),  # Ginocchio
            (sx * 0.108, -0.004, 0.41),  # Sotto il ginocchio
        ]
        pant_radii = [
            (0.084, 0.088),
            (0.080, 0.082),
            (0.072, 0.074),
            (0.064, 0.066),
            (0.058, 0.060),
            (0.054, 0.055),
        ]
        create_profiled_tube(f"Pantalone_{side}", pant_centers, pant_radii, MATS["pantaloni"], segs=20, fold_amp=0.045, fold_freq=7)

        # 2. Fasce di stoffa chiara sotto il ginocchio (Z=0.39..0.44, visibili sopra il bordo dello stivale)
        wrap_centers = [
            (sx * 0.107, -0.005, 0.445),
            (sx * 0.109, -0.003, 0.415),
            (sx * 0.110, 0.000, 0.385),
        ]
        create_profiled_tube(f"Fascia_Gamba_{side}", wrap_centers, [(0.057, 0.058), (0.056, 0.057), (0.053, 0.054)], MATS["camicia"], segs=18, fold_amp=0.04, fold_freq=6)

        # 3. Gambale dello stivale alto (da Z=0.10 caviglia a Z=0.40 sotto il ginocchio)
        boot_shaft_centers = [
            (sx * 0.110, -0.001, 0.400),  # Bordo alto risvolto
            (sx * 0.110, 0.001, 0.355),   # Fine risvolto superiore
            (sx * 0.111, 0.004, 0.280),   # Polpaccio
            (sx * 0.113, 0.002, 0.190),   # Stinco basso
            (sx * 0.114, -0.002, 0.110),  # Caviglia
            (sx * 0.114, -0.010, 0.065),  # Collo del piede
        ]
        boot_shaft_radii = [
            (0.061, 0.063),
            (0.059, 0.061),
            (0.058, 0.062),
            (0.051, 0.054),
            (0.046, 0.051),
            (0.048, 0.058),
        ]
        create_profiled_tube(f"Stivale_Gambale_{side}", boot_shaft_centers, boot_shaft_radii, MATS["cuoio_scuro"], segs=20, fold_amp=0.02, fold_freq=5)

        # Risvolto superiore dello stivale e cinturino con fibbia
        cuff_centers = [
            (sx * 0.110, -0.001, 0.405),
            (sx * 0.110, 0.000, 0.375),
            (sx * 0.110, 0.001, 0.345),
        ]
        create_profiled_tube(f"Stivale_Risvolto_{side}", cuff_centers, [(0.063, 0.065), (0.064, 0.066), (0.061, 0.063)], MATS["cuoio_medio"], segs=20)

        # Cinturino superiore dello stivale (Z=0.365)
        strap_ring = []
        for k in range(17):
            ang = 2.0 * math.pi * k / 16.0
            strap_ring.append((sx * 0.110 + 0.065 * math.cos(ang), 0.067 * math.sin(ang), 0.365))
        create_profiled_tube(f"Stivale_Cinturino_{side}", strap_ring, [(0.005, 0.011)] * len(strap_ring), MATS["cuoio_scuro"], segs=8, cap_ends=False)

        # Lacci incrociati sul davanti dello stivale (da Z=0.13 a Z=0.33)
        for z_lace in np.linspace(0.135, 0.320, 6):
            p_l = (sx * 0.112 - 0.024, -0.056, z_lace)
            p_m = (sx * 0.112, -0.063, z_lace + 0.014)
            p_r = (sx * 0.112 + 0.024, -0.056, z_lace + 0.028)
            create_profiled_tube(f"Laccio1_{side}_{int(z_lace*100)}", [p_l, p_m, p_r], [0.0035, 0.0038, 0.0035], MATS["cuoio_chiaro"], segs=6)
            p_l2 = (sx * 0.112 + 0.024, -0.056, z_lace)
            p_r2 = (sx * 0.112 - 0.024, -0.056, z_lace + 0.028)
            create_profiled_tube(f"Laccio2_{side}_{int(z_lace*100)}", [p_l2, p_m, p_r2], [0.0035, 0.0038, 0.0035], MATS["cuoio_chiaro"], segs=6)

        # 4. Piede e suola dello stivale (da Z=0.00 a Z=0.095, leggermente ruotato verso l'esterno)
        toe_yaw = sx * math.radians(10.0)
        c_yaw, s_yaw = math.cos(toe_yaw), math.sin(toe_yaw)
        def rot_foot(lx, ly, lz):
            rx = lx * c_yaw - ly * s_yaw
            ry = lx * s_yaw + ly * c_yaw
            return (sx * 0.114 + rx, ry, lz)

        foot_centers = [
            rot_foot(0.0, 0.050, 0.052),   # Tallone posteriore
            rot_foot(0.0, 0.005, 0.058),   # Caviglia/arco
            rot_foot(0.0, -0.055, 0.050),  # Dorso piede
            rot_foot(0.0, -0.115, 0.042),  # Punta anteriore
            rot_foot(0.0, -0.155, 0.032),  # Estremità punta arrotondata
        ]
        foot_radii = [
            (0.044, 0.046),
            (0.048, 0.052),
            (0.051, 0.044),
            (0.048, 0.036),
            (0.032, 0.022),
        ]
        # Costruiamo il piede e appiattiamo i vertici sotto Z=0.018 per poggiare a Z=0.00
        foot_obj = create_profiled_tube(f"Stivale_Piede_{side}", foot_centers, foot_radii, MATS["cuoio_scuro"], segs=18)
        for v in foot_obj.data.vertices:
            if v.co.z < 0.016:
                v.co.z = 0.014

        # Suola spessa e tacco (Z=0.000 .. Z=0.022)
        sole_centers = [
            rot_foot(0.0, 0.056, 0.011),
            rot_foot(0.0, 0.000, 0.011),
            rot_foot(0.0, -0.065, 0.011),
            rot_foot(0.0, -0.125, 0.011),
            rot_foot(0.0, -0.162, 0.012),
        ]
        sole_radii = [
            (0.047, 0.011),
            (0.044, 0.010),
            (0.054, 0.011),
            (0.051, 0.011),
            (0.035, 0.010),
        ]
        sole_obj = create_profiled_tube(f"Stivale_Suola_{side}", sole_centers, sole_radii, MATS["metallo_scuro"], segs=16)
        for v in sole_obj.data.vertices:
            if v.co.z < 0.006:
                v.co.z = 0.000

    # 5. GINOCCHIERA CORAZZATA SUL GINOCCHIO DESTRO (X < 0, a sinistra guardando di fronte) + Cinghia coscia DX
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0)
    for v in bm.verts:
        v.co = Vector((
            -0.106 + v.co.x * 0.056,
            -0.062 + v.co.y * 0.028,
            0.485 + v.co.z * 0.062
        ))
    m_kp = bpy.data.meshes.new("Ginocchiera_DX")
    bm.to_mesh(m_kp)
    bm.free()
    o_kp = bpy.data.objects.new("Ginocchiera_DX", m_kp)
    scn.collection.objects.link(o_kp)
    finalize_obj(o_kp, MATS["cuoio_scuro"], smooth=True)

    # Bordo metallico/cuoio della ginocchiera destra
    kp_ring = []
    for k in range(17):
        th = 2.0 * math.pi * k / 16.0
        kp_ring.append((-0.106 + 0.050 * math.cos(th), -0.066 - 0.008 * math.sin(th)**2, 0.485 + 0.056 * math.sin(th)))
    create_profiled_tube("Ginocchiera_Bordo_DX", kp_ring, [0.007] * len(kp_ring), MATS["cuoio_medio"], segs=8, cap_ends=False)

    # Cinghia orizzontale sulla coscia destra (Z=0.61)
    thigh_strap = []
    for k in range(17):
        th = 2.0 * math.pi * k / 16.0
        thigh_strap.append((-0.100 + 0.074 * math.cos(th), -0.004 + 0.076 * math.sin(th), 0.615))
    create_profiled_tube("Cinghia_Coscia_DX", thigh_strap, [(0.005, 0.012)] * len(thigh_strap), MATS["cuoio_scuro"], segs=8, cap_ends=False)

build_legs_and_boots()

# ==============================================================================
# 7. BRACCIA IN POSA "A", MANICHE CON PIEGHE E GUANTI IN CUOIO CON DITA
# ==============================================================================
def build_arms_and_gloves():
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        # Direzione braccio in posa "A": da spalla (0.18, 0.01, 1.35) a polso (0.485, -0.015, 1.015)
        # 1. Manica in stoffa beige (spalla -> gomito -> avambraccio alto)
        sleeve_pts = [
            (sx * 0.165, 0.010, 1.355),
            (sx * 0.230, 0.014, 1.290),
            (sx * 0.295, 0.018, 1.220),
            (sx * 0.355, 0.015, 1.155),  # Gomito
            (sx * 0.405, 0.004, 1.100),  # Ingresso nel guanto
        ]
        sleeve_rads = [
            (0.056, 0.058),
            (0.054, 0.056),
            (0.052, 0.054),
            (0.050, 0.052),
            (0.043, 0.044),
        ]
        create_profiled_tube(f"Manica_{side}", sleeve_pts, sleeve_rads, MATS["camicia"], segs=18, fold_amp=0.065, fold_freq=6)

        # 2. Guanto lungo in cuoio (avambraccio -> polso -> palmo)
        glove_pts = [
            (sx * 0.380, 0.009, 1.128),  # Bordo svasato del guanto sull'avambraccio
            (sx * 0.415, 0.002, 1.090),
            (sx * 0.455, -0.008, 1.045),
            (sx * 0.490, -0.016, 1.005),  # Polso
            (sx * 0.525, -0.022, 0.965),  # Palmo
            (sx * 0.545, -0.026, 0.942),  # Nocche
        ]
        glove_rads = [
            (0.052, 0.054),
            (0.047, 0.049),
            (0.042, 0.044),
            (0.036, 0.039),
            (0.032, 0.043),
            (0.026, 0.040),
        ]
        create_profiled_tube(f"Guanto_{side}", glove_pts, glove_rads, MATS["cuoio_scuro"], segs=18, fold_amp=0.025, fold_freq=5)

        # Cinturini sul guanto
        for t_s, r_s in ((0.25, 0.050), (0.65, 0.041)):
            c_s = Vector(glove_pts[0]).lerp(Vector(glove_pts[3]), t_s)
            axis = (Vector(glove_pts[3]) - Vector(glove_pts[0])).normalized()
            b1 = axis.cross(Vector((0, 1, 0))).normalized()
            b2 = b1.cross(axis).normalized()
            s_ring = [tuple(c_s + b1 * (r_s * math.cos(2 * math.pi * k / 14)) + b2 * (r_s * math.sin(2 * math.pi * k / 14))) for k in range(15)]
            create_profiled_tube(f"Cinturino_Guanto_{side}_{int(t_s*10)}", s_ring, [0.0055] * len(s_ring), MATS["cuoio_medio"], segs=8, cap_ends=False)

        # 3. Dita della mano (5 dita modellate in posa naturale aperta)
        arm_dir = Vector((sx * 0.66, -0.14, -0.74)).normalized()
        # Vettore lungo la larghezza del palmo (da mignolo +Y a indice -Y)
        palm_spread = Vector((0.0, -1.0, 0.0))
        palm_normal = arm_dir.cross(palm_spread).normalized() * sx

        finger_specs = [
            # (nome, y_off, length, rad_base, spread_angle)
            ("Indice", -0.026, 0.058, 0.0095, -0.10),
            ("Medio", -0.009, 0.064, 0.0100, -0.02),
            ("Anulare", 0.009, 0.059, 0.0092, 0.05),
            ("Mignolo", 0.025, 0.048, 0.0080, 0.13),
        ]
        knuckle_base = Vector((sx * 0.542, -0.025, 0.945))
        for fname, y_off, flen, r_b, sp_ang in finger_specs:
            f_start = knuckle_base + Vector((0.0, y_off, 0.0))
            f_dir = (arm_dir + Vector((0.0, -sp_ang, 0.0)) - palm_normal * 0.12).normalized()
            f_pts = [
                tuple(f_start),
                tuple(f_start + f_dir * (flen * 0.45)),
                tuple(f_start + (f_dir - palm_normal * 0.18).normalized() * (flen * 0.80)),
                tuple(f_start + (f_dir - palm_normal * 0.25).normalized() * flen),
            ]
            create_profiled_tube(f"Dito_{fname}_{side}", f_pts, [r_b, r_b * 0.88, r_b * 0.76, r_b * 0.58], MATS["cuoio_scuro"], segs=8)

        # Pollice (anteriore verso -Y)
        thumb_start = Vector((sx * 0.515, -0.048, 0.972))
        thumb_dir = Vector((sx * 0.48, -0.52, -0.70)).normalized()
        t_pts = [
            tuple(thumb_start),
            tuple(thumb_start + thumb_dir * 0.026),
            tuple(thumb_start + thumb_dir * 0.050),
        ]
        create_profiled_tube(f"Dito_Pollice_{side}", t_pts, [0.0115, 0.0098, 0.0075], MATS["cuoio_scuro"], segs=8)

build_arms_and_gloves()

# Controllo dimensioni e salvataggio
pts_all = [o.matrix_world @ Vector(c) for o in scn.objects if o.type == "MESH" for c in o.bound_box]
min_z = min(p.z for p in pts_all)
max_z = max(p.z for p in pts_all)
tris = sum(len(o.data.polygons) for o in scn.objects if o.type == "MESH")
log(f"Passo 1 completato: Z min={min_z:.3f}m, Z max={max_z:.3f}m, Altezza={max_z - min_z:.3f}m, Poligoni={tris}")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("passo1_corpo", viste=["fronte", "destra", "retro", "tre_quarti"])
