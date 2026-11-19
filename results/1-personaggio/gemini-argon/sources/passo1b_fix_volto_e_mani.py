import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# ==============================================================================
# PASSO 1B: Rifinitura volto (occhi e fronte ben visibili, profilo anatomico),
#           capelli che incorniciano il viso con ciocca bianca, mani proporzionate
#           e correzione normali sui tappi dei tubi.
# ==============================================================================

scn = bpy.context.scene
MATS = {m.name.replace("Mat_", "").lower(): m for m in bpy.data.materials}
# Mappa nomi rapidi
mat_map = {
    "pelle": bpy.data.materials["Mat_Pelle"],
    "labbra": bpy.data.materials["Mat_Labbra"],
    "occhio_bianco": bpy.data.materials["Mat_OcchioBianco"],
    "iride": bpy.data.materials["Mat_Iride"],
    "pupilla": bpy.data.materials["Mat_Pupilla"],
    "capelli_scuri": bpy.data.materials["Mat_CapelliScuri"],
    "capelli_bianchi": bpy.data.materials["Mat_CapelliBianchi"],
    "camicia": bpy.data.materials["Mat_Camicia"],
    "giacca_blu": bpy.data.materials["Mat_GiaccaBlu"],
    "pantaloni": bpy.data.materials["Mat_Pantaloni"],
    "cuoio_scuro": bpy.data.materials["Mat_CuoioScuro"],
    "cuoio_medio": bpy.data.materials["Mat_CuoioMedio"],
    "cuoio_chiaro": bpy.data.materials["Mat_CuoioChiaro"],
    "ottone": bpy.data.materials["Mat_Ottone"],
    "metallo_scuro": bpy.data.materials["Mat_MetalloScuro"],
}

def finalize_obj(obj, mat, smooth=True):
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            u = 0.5 + math.atan2(co.x, -co.y) / (2 * math.pi)
            v = co.z * 1.2
            loop[uv_layer].uv = (u, v)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj

# Rimuoviamo gli oggetti di testa, capelli, braccia e mani per ricostruirli puliti,
# e correggiamo le normali dei tappi sugli oggetti esistenti (torso, gambe, stivali)
prefixes_rebuild = (
    "Testa", "Labbro", "Occhio", "Iride", "Pupilla", "Sopracciglio", "Ciglia",
    "Orecchio", "Collo", "Capelli", "Ciocca", "Manica", "Guanto", "Cinturino_Guanto", "Dito"
)
for obj in list(bpy.data.objects):
    if obj.type == "MESH" and obj.name.startswith(prefixes_rebuild):
        m = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(m)

# Correzione shading dei tappi sugli oggetti rimasti (Giacca, Pantaloni, Stivali, ecc.)
for obj in scn.objects:
    if obj.type == "MESH":
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for f in bm.faces:
            # Se una faccia ha un vertice centrale di tappo (triangolo quasi orizzontale), flat shading
            if len(f.verts) == 3 and abs(f.normal.z) > 0.85:
                f.smooth = False
            else:
                f.smooth = True
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

def create_profiled_tube(name, centers, radii_xy, mat, segs=18, cap_ends=True, fold_amp=0.0, fold_freq=6):
    bm = bmesh.new()
    rings = []
    n_rings = len(centers)
    for i in range(n_rings):
        c = Vector(centers[i])
        rx, ry = radii_xy[i] if isinstance(radii_xy[i], (tuple, list)) else (radii_xy[i], radii_xy[i])
        if i == 0:
            t = (Vector(centers[1]) - c).normalized()
        elif i == n_rings - 1:
            t = (c - Vector(centers[-2])).normalized()
        else:
            t = (Vector(centers[i + 1]) - Vector(centers[i - 1])).normalized()
        up = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
        b1 = t.cross(up).normalized()
        b2 = b1.cross(t).normalized()
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
            f = bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
            f.smooth = True

    if cap_ends:
        for idx, invert in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[idx][jn], rings[idx][j], cv) if invert else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = False  # Evita artefatti sulle normali ai bordi

    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scn.collection.objects.link(obj)
    return finalize_obj(obj, mat, smooth=True)

# 1. RICOSTRUZIONE COLLO E TESTA FEMMINILE PROPORZIONATA
neck_pts = [
    (0.0, 0.004, 1.380),
    (0.0, 0.000, 1.430),
    (0.0, -0.005, 1.490),
]
create_profiled_tube("Collo", neck_pts, [(0.054, 0.050), (0.046, 0.044), (0.048, 0.046)], mat_map["pelle"], segs=20)

bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=28, radius=1.0)
head_center = Vector((0.0, -0.006, 1.560))

for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    rx = 0.072
    ry = 0.084
    rz = 0.096
    # Mandibola femminile affusolata verso il mento
    if z < 0.0:
        t_jaw = min(1.0, -z)
        rx *= (1.0 - 0.38 * (t_jaw ** 1.1))
        if y < 0.0:
            ry *= (1.0 - 0.14 * (t_jaw ** 1.4))
        else:
            ry *= (1.0 - 0.25 * (t_jaw ** 1.2))
    px = x * rx
    py = y * ry
    pz = z * rz

    if y < -0.10:
        front = min(1.0, (-y - 0.10) / 0.90)
        # Appiattimento leggero del piano facciale anteriore per dare struttura
        py *= (1.0 - 0.06 * front)
        # Zigomi alti
        cheek = math.exp(-((abs(x) - 0.50) ** 2 / 0.08 + (z + 0.08) ** 2 / 0.05))
        px += math.copysign(0.005 * cheek * front, x)
        py -= 0.004 * cheek * front
        # Incavo occhi morbido
        eye_sock = math.exp(-((abs(x) - 0.36) ** 2 / 0.040 + (z - 0.02) ** 2 / 0.025))
        py += 0.006 * eye_sock * front
        # Naso dritto e ben integrato nel volto
        nose_x = math.exp(-(x ** 2) / 0.012)
        if -0.32 < z < 0.12:
            # Profilo del naso: cresce da z=0.10 (radice) fino a z=-0.22 (punta) e rientra a z=-0.30
            if z >= -0.22:
                t_n = (0.12 - z) / 0.34
                nose_prof = (t_n ** 1.1) * 0.016
            else:
                t_n = max(0.0, (z + 0.32) / 0.10)
                nose_prof = t_n * 0.016
            py -= nose_prof * nose_x * front
        # Labbra morbide scolpite direttamente sulla mesh della faccia
        lip_x = math.exp(-(x ** 2) / 0.035)
        upper_lip = math.exp(-((z + 0.44) ** 2) / 0.004)
        lower_lip = math.exp(-((z + 0.54) ** 2) / 0.005)
        py -= (0.0055 * upper_lip + 0.0050 * lower_lip) * lip_x * front
        # Mento morbido
        chin = math.exp(-(x ** 2 / 0.04 + (z + 0.80) ** 2 / 0.035))
        py -= 0.005 * chin * front

    v.co = head_center + Vector((px, py, pz))

for f in bm.faces:
    f.smooth = True
m_head = bpy.data.meshes.new("Testa")
bm.normal_update()
bm.to_mesh(m_head)
bm.free()
o_head = bpy.data.objects.new("Testa", m_head)
scn.collection.objects.link(o_head)
finalize_obj(o_head, mat_map["pelle"], smooth=True)

# Labbra sottili integrate sulla superficie del viso (y ~ -0.078)
for lip_name, z_c, y_c, rz_s in [
    ("Labbro_Sup", 1.517, -0.0785, 0.0032),
    ("Labbro_Inf", 1.510, -0.0775, 0.0036),
]:
    lip_pts = [
        (-0.014, y_c + 0.003, z_c - 0.001),
        (-0.006, y_c - 0.001, z_c + (0.0008 if "Sup" in lip_name else -0.0005)),
        (0.000,  y_c - 0.0015, z_c),
        (0.006,  y_c - 0.001, z_c + (0.0008 if "Sup" in lip_name else -0.0005)),
        (0.014,  y_c + 0.003, z_c - 0.001),
    ]
    rads = [(0.0015, 0.0015), (0.0032, rz_s), (0.0035, rz_s), (0.0032, rz_s), (0.0015, 0.0015)]
    create_profiled_tube(lip_name, lip_pts, rads, mat_map["labbra"], segs=10)

# Occhi, iride, pupilla, ciglia, sopracciglia e orecchie (ben visibili!)
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    ex, ey, ez = sx * 0.026, -0.074, 1.562
    for part_n, r_s, y_shift, mat_k in [
        (f"Occhio_{side}", (0.0105, 0.0080, 0.0075), 0.0, "occhio_bianco"),
        (f"Iride_{side}", (0.0055, 0.0025, 0.0055), -0.0068, "iride"),
        (f"Pupilla_{side}", (0.0028, 0.0018, 0.0028), -0.0078, "pupilla"),
    ]:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
        for v in bm.verts:
            v.co = Vector((ex + v.co.x * r_s[0], ey + y_shift + v.co.y * r_s[1], ez + v.co.z * r_s[2]))
        for f in bm.faces:
            f.smooth = True
        m = bpy.data.meshes.new(part_n)
        bm.to_mesh(m)
        bm.free()
        o = bpy.data.objects.new(part_n, m)
        scn.collection.objects.link(o)
        finalize_obj(o, mat_map[mat_k], smooth=True)

    # Ciglia superiori marcate
    lash_pts = [
        (sx * 0.016, -0.079, 1.563),
        (sx * 0.026, -0.083, 1.567),
        (sx * 0.037, -0.078, 1.563),
    ]
    create_profiled_tube(f"Ciglia_{side}", lash_pts, [0.0015, 0.0024, 0.0018], mat_map["pupilla"], segs=8)

    # Sopracciglia ben definite e visibili sopra gli occhi
    brow_pts = [
        (sx * 0.011, -0.081, 1.575),
        (sx * 0.024, -0.085, 1.580),
        (sx * 0.038, -0.080, 1.579),
        (sx * 0.047, -0.072, 1.574),
    ]
    create_profiled_tube(f"Sopracciglio_{side}", brow_pts, [0.0028, 0.0036, 0.0030, 0.0016], mat_map["capelli_scuri"], segs=8)

    # Orecchie
    ear_pts = [
        (sx * 0.066, -0.006, 1.536),
        (sx * 0.073, -0.002, 1.554),
        (sx * 0.071, 0.004, 1.570),
    ]
    create_profiled_tube(f"Orecchio_{side}", ear_pts, [(0.006, 0.010), (0.008, 0.013), (0.005, 0.009)], mat_map["pelle"], segs=10)

# 2. CAPELLI MOSSI CHE INCORNICIANO IL VISO LASCIANDO SCOPERTI FRONTE E OCCHI
# Calotta posteriore e superiore
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=20, radius=1.0)
for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    # Ritaglia l'area del viso davanti (y < -0.15 e z < 0.35)
    if y < -0.10 and z < 0.38:
        y = -0.10 + (y + 0.10) * 0.25
        if z < 0.0:
            z = 0.05
    wave = 1.0 + 0.035 * math.sin(x * 10.0 + z * 7.0)
    v.co = Vector((
        x * 0.082 * wave,
        0.002 + y * 0.092 * wave,
        1.582 + z * 0.092 * wave
    ))
for f in bm.faces:
    f.smooth = True
m_hair = bpy.data.meshes.new("Capelli_Calotta")
bm.to_mesh(m_hair)
bm.free()
o_hair = bpy.data.objects.new("Capelli_Calotta", m_hair)
scn.collection.objects.link(o_hair)
finalize_obj(o_hair, mat_map["capelli_scuri"], smooth=True)

# Ciocche laterali e posteriori (ang da -0.68*pi a +0.68*pi così il viso davanti resta libero!)
n_locks = 24
for i in range(n_locks):
    ang = -math.pi * 0.68 + (math.pi * 1.36) * (i / (n_locks - 1))
    sx = math.sin(ang)
    cy = math.cos(ang)
    top_z = 1.675 + 0.016 * math.cos(i * 1.3)
    mid_r = 0.088 + 0.008 * (i % 3)
    # Le ciocche alle tempie si aprono leggermente verso l'esterno (wavy flare)
    side_flare = math.copysign(0.018, sx) if abs(ang) > math.pi * 0.42 else (0.010 * (1 if i % 2 == 0 else -1))
    end_z = 1.505 + 0.020 * (i % 2)
    pts = [
        (sx * 0.022, cy * 0.020, top_z),
        (sx * 0.068, cy * 0.072, 1.648),
        (sx * mid_r, cy * (mid_r + 0.004), 1.595),
        (sx * (mid_r + 0.010) + side_flare * 0.5, cy * mid_r, 1.545),
        (sx * (mid_r + 0.016) + side_flare, cy * (mid_r + 0.006), end_z),
    ]
    rads = [(0.014, 0.010), (0.022, 0.014), (0.025, 0.015), (0.019, 0.012), (0.005, 0.004)]
    create_profiled_tube(f"Ciocca_Scura_{i:02d}", pts, rads, mat_map["capelli_scuri"], segs=8)

# Ciocche alte sulla fronte destra (-X) che scendono di lato alla tempia SENZA coprire l'occhio
for k, z_bias in enumerate((0.0, -0.012)):
    pts = [
        (-0.005, -0.035, 1.672),
        (-0.038, -0.075, 1.648 + z_bias * 0.5),
        (-0.068, -0.072, 1.610 + z_bias),
        (-0.088, -0.052, 1.562 + z_bias),
        (-0.098, -0.035, 1.522 + z_bias),
    ]
    create_profiled_tube(f"Ciocca_TempiaDX_{k}", pts, [(0.014, 0.010), (0.020, 0.013), (0.020, 0.012), (0.015, 0.010), (0.005, 0.004)], mat_map["capelli_scuri"], segs=8)

# CIOCCA BIANCA ICONICA sulla parte superiore-sinistra (+X) che incornicia la fronte e scende alla tempia sinistra
white_locks = [
    [
        (-0.004, -0.042, 1.676),
        (0.024, -0.080, 1.656),
        (0.056, -0.082, 1.622),
        (0.078, -0.066, 1.580),
        (0.090, -0.048, 1.540),
    ],
    [
        (0.006, -0.028, 1.684),
        (0.038, -0.072, 1.664),
        (0.068, -0.074, 1.630),
        (0.086, -0.055, 1.588),
    ],
    [
        (-0.008, -0.048, 1.668),
        (0.016, -0.084, 1.644),
        (0.044, -0.085, 1.615),
        (0.066, -0.072, 1.586),
    ],
]
for idx, wpts in enumerate(white_locks):
    rads = [(0.013, 0.009), (0.021, 0.013), (0.020, 0.012), (0.014, 0.009), (0.005, 0.004)][:len(wpts)]
    create_profiled_tube(f"Ciocca_Bianca_{idx}", wpts, rads, mat_map["capelli_bianchi"], segs=8)

# 3. BRACCIA, SPALLE MORBIDE E GUANTI CON MANI BEN VISIBILI E PROPORZIONATE
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    # Manica che parte morbida dentro la spalla del busto (Z=1.35) fino a metà avambraccio
    sleeve_pts = [
        (sx * 0.145, 0.006, 1.345),
        (sx * 0.185, 0.010, 1.330),
        (sx * 0.245, 0.014, 1.270),
        (sx * 0.305, 0.016, 1.205),
        (sx * 0.355, 0.012, 1.150),  # Gomito
        (sx * 0.400, 0.004, 1.100),
    ]
    sleeve_rads = [
        (0.044, 0.046),
        (0.055, 0.057),
        (0.053, 0.055),
        (0.051, 0.053),
        (0.049, 0.051),
        (0.042, 0.043),
    ]
    create_profiled_tube(f"Manica_{side}", sleeve_pts, sleeve_rads, mat_map["camicia"], segs=18, fold_amp=0.06, fold_freq=6)

    # Guanto lungo in cuoio (avambraccio -> polso -> dorso della mano)
    glove_pts = [
        (sx * 0.375, 0.008, 1.128),  # Bordo largo sull'avambraccio
        (sx * 0.415, 0.002, 1.084),
        (sx * 0.455, -0.006, 1.040),
        (sx * 0.488, -0.014, 1.002),  # Polso
        (sx * 0.522, -0.022, 0.964),  # Metà palmo
        (sx * 0.548, -0.028, 0.935),  # Nocche delle dita
    ]
    glove_rads = [
        (0.053, 0.055),
        (0.048, 0.050),
        (0.043, 0.045),
        (0.037, 0.040),
        (0.042, 0.026),  # Palmo più largo nel piano del braccio/fronte e più piatto di spessore!
        (0.040, 0.022),
    ]
    create_profiled_tube(f"Guanto_{side}", glove_pts, glove_rads, mat_map["cuoio_scuro"], segs=18, fold_amp=0.02, fold_freq=5)

    # Cinturini sul guanto
    for t_s, r_s in ((0.22, 0.051), (0.62, 0.041)):
        c_s = Vector(glove_pts[0]).lerp(Vector(glove_pts[3]), t_s)
        axis = (Vector(glove_pts[3]) - Vector(glove_pts[0])).normalized()
        b1 = axis.cross(Vector((0, 1, 0))).normalized()
        b2 = b1.cross(axis).normalized()
        s_ring = [tuple(c_s + b1 * (r_s * math.cos(2 * math.pi * k / 14)) + b2 * (r_s * math.sin(2 * math.pi * k / 14))) for k in range(15)]
        create_profiled_tube(f"Cinturino_Guanto_{side}_{int(t_s*10)}", s_ring, [0.0055] * len(s_ring), mat_map["cuoio_medio"], segs=8, cap_ends=False)

    # Dita ben distribuite e visibili sia di fronte che di lato (come nella posa A del riferimento)
    arm_dir = Vector((sx * 0.65, -0.15, -0.74)).normalized()
    # Vettore di apertura delle dita (mignolo più esterno/posteriore, indice più interno/anteriore)
    spread_vec = Vector((-sx * 0.42, -0.82, -0.38)).normalized()
    curl_vec = Vector((-sx * 0.55, 0.35, -0.75)).normalized()

    knuckle_center = Vector((sx * 0.546, -0.027, 0.937))
    finger_specs = [
        # (nome, offset lungo spread_vec, lunghezza, raggio base, angolo divaricazione)
        ("Indice",  0.026, 0.072, 0.0105,  0.14),
        ("Medio",   0.008, 0.078, 0.0110,  0.04),
        ("Anulare", -0.010, 0.072, 0.0102, -0.05),
        ("Mignolo", -0.026, 0.058, 0.0090, -0.15),
    ]
    for fname, s_off, flen, r_b, sp_a in finger_specs:
        f_start = knuckle_center + spread_vec * s_off
        f_d1 = (arm_dir + spread_vec * sp_a).normalized()
        f_d2 = (f_d1 * 0.85 + curl_vec * 0.25).normalized()
        f_d3 = (f_d1 * 0.70 + curl_vec * 0.45).normalized()
        p0 = f_start
        p1 = p0 + f_d1 * (flen * 0.42)
        p2 = p1 + f_d2 * (flen * 0.33)
        p3 = p2 + f_d3 * (flen * 0.25)
        create_profiled_tube(f"Dito_{fname}_{side}", [p0, p1, p2, p3], [r_b, r_b * 0.90, r_b * 0.78, r_b * 0.60], mat_map["cuoio_scuro"], segs=8)

    # Pollice ben aperto verso l'interno/basso (come nel riferimento frontale)
    thumb_base = Vector((sx * 0.515, -0.038, 0.960))
    t_d1 = Vector((sx * 0.22, -0.55, -0.80)).normalized()
    t_d2 = Vector((sx * 0.10, -0.45, -0.88)).normalized()
    tp0 = thumb_base
    tp1 = tp0 + t_d1 * 0.034
    tp2 = tp1 + t_d2 * 0.030
    create_profiled_tube(f"Dito_Pollice_{side}", [tp0, tp1, tp2], [0.0130, 0.0110, 0.0085], mat_map["cuoio_scuro"], segs=8)

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("passo1b_corpo", viste=["fronte", "destra", "tre_quarti"])
