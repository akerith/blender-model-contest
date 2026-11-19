import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# ==============================================================================
# PASSO 4: Rifinitura generale di alta qualità:
#   1. Creazione effettiva dello strumento/bussola da polso SX (con quadrante verde,
#      cassa in ottone, ghiera e cinturini).
#   2. Eliminazione della compenetrazione tra manica beige e mantellina sulle spalle.
#   3. Avvicinamento della sacca arrotolata alla schiena e tubi curvi morbidi.
#   4. Texture organica senza pattern regolari per la mantella verde strappata.
#   5. Rifinitura bocca/labbra, collo/colletto e ciocche di capelli mosse (altezza 1.70 m).
# ==============================================================================

scn = bpy.context.scene

mat_ottone = bpy.data.materials["Mat_Ottone"]
mat_cuoio_scuro = bpy.data.materials["Mat_CuoioScuro"]
mat_cuoio_medio = bpy.data.materials["Mat_CuoioMedio"]
mat_cuoio_chiaro = bpy.data.materials["Mat_CuoioChiaro"]
mat_quadrante = bpy.data.materials["Mat_QuadranteVerde"]
mat_labbra = bpy.data.materials["Mat_Labbra"]
mat_capelli_scuri = bpy.data.materials["Mat_CapelliScuri"]
mat_capelli_bianchi = bpy.data.materials["Mat_CapelliBianchi"]

def create_tube(name, pts, radii, mat, segs=14, closed=False, cap_ends=True):
    if name in bpy.data.objects:
        old = bpy.data.objects[name]
        m_old = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        bpy.data.meshes.remove(m_old)
    bm = bmesh.new()
    rings = []
    n = len(pts)
    for i in range(n):
        c = Vector(pts[i])
        r = radii[i] if (isinstance(radii, list) and len(radii) == n) else radii
        rx, ry = r if isinstance(r, (list, tuple)) else (r, r)
        if closed:
            t = (Vector(pts[(i + 1) % n]) - Vector(pts[(i - 1) % n])).normalized()
        elif i == 0:
            t = (Vector(pts[1]) - c).normalized()
        elif i == n - 1:
            t = (c - Vector(pts[-2])).normalized()
        else:
            t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        b1 = t.cross(up).normalized()
        b2 = b1.cross(t).normalized()
        ring_v = []
        for j in range(segs):
            th = 2.0 * math.pi * j / segs
            pt = c + b1 * (rx * math.cos(th)) + b2 * (ry * math.sin(th))
            ring_v.append(bm.verts.new(pt))
        rings.append(ring_v)

    limit = n if closed else n - 1
    for i in range(limit):
        inext = (i + 1) % n
        for j in range(segs):
            jn = (j + 1) % segs
            f = bm.faces.new((rings[i][j], rings[i][jn], rings[inext][jn], rings[inext][j]))
            f.smooth = True

    if not closed and cap_ends:
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = False

    m = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(m)
    bm.free()
    o = bpy.data.objects.new(name, m)
    scn.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

# ==============================================================================
# 1. STRUMENTO DA POLSO / BUSSOLA SULL'AVAMBRACCIO SINISTRO (+X)
# ==============================================================================
for obj in list(bpy.data.objects):
    if obj.name.startswith("Strumento_Polso"):
        m = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(m)

# Posizionato sull'esterno/fronte dell'avambraccio sinistro (+X), ben visibile!
w_center = Vector((0.445, -0.042, 1.070))
n_vec = Vector((0.48, -0.72, 0.50)).normalized()
u_vec = Vector((-0.65, 0.05, 0.76)).normalized()
r_vec = u_vec.cross(n_vec).normalized()
u_vec = n_vec.cross(r_vec).normalized()
rad = 0.040

# Base cilindrica in ottone sul guanto
bm_wb = bmesh.new()
bmesh.ops.create_uvsphere(bm_wb, u_segments=20, v_segments=10, radius=1.0)
for v in bm_wb.verts:
    v.co = w_center + r_vec * (v.co.x * rad * 1.02) + u_vec * (v.co.y * rad * 1.02) + n_vec * (v.co.z * 0.014 - 0.004)
for f in bm_wb.faces:
    f.smooth = True
m_wb = bpy.data.meshes.new("Strumento_Polso_Base")
bm_wb.to_mesh(m_wb)
bm_wb.free()
o_wb = bpy.data.objects.new("Strumento_Polso_Base", m_wb)
scn.collection.objects.link(o_wb)
o_wb.data.materials.append(mat_ottone)

# Cornice/ghiera circolare in ottone
bezel_pts = []
for k in range(24):
    th = 2.0 * math.pi * k / 24.0
    bezel_pts.append(tuple(w_center + n_vec * 0.008 + (r_vec * math.cos(th) + u_vec * math.sin(th)) * rad))
create_tube("Strumento_Polso_Cassa", bezel_pts, (0.010, 0.013), mat_ottone, segs=10, closed=True)

# Quadrante verde acqua luminoso
bm_d = bmesh.new()
bmesh.ops.create_uvsphere(bm_d, u_segments=18, v_segments=8, radius=1.0)
for v in bm_d.verts:
    v.co = w_center + n_vec * 0.008 + r_vec * (v.co.x * rad * 0.84) + u_vec * (v.co.y * rad * 0.84) + n_vec * (max(0.0, v.co.z) * 0.007)
for f in bm_d.faces:
    f.smooth = True
m_d = bpy.data.meshes.new("Strumento_Polso_Quadrante")
bm_d.to_mesh(m_d)
bm_d.free()
o_d = bpy.data.objects.new("Strumento_Polso_Quadrante", m_d)
scn.collection.objects.link(o_d)
o_d.data.materials.append(mat_quadrante)

# Lancetta/indicatore centrale in ottone sul quadrante
hand_pts = [
    tuple(w_center + n_vec * 0.016 - u_vec * 0.012),
    tuple(w_center + n_vec * 0.017),
    tuple(w_center + n_vec * 0.016 + (u_vec * 0.7 + r_vec * 0.5) * 0.024),
]
create_tube("Strumento_Polso_Lancetta", hand_pts, 0.003, mat_ottone, segs=6)

# ==============================================================================
# 2. ELIMINAZIONE COMPENETRAZIONE MANICA BEIGE / MANTELLINA SPALLE
# ==============================================================================
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    manica = bpy.data.objects.get(f"Manica_{side}")
    if manica:
        # Stringi il raggio della manica nella parte alta (Z > 1.21) che sta sotto la mantellina
        for v in manica.data.vertices:
            if v.co.z > 1.20:
                t_up = min(1.0, (v.co.z - 1.20) / 0.14)
                # Centro approssimato dell'asse del braccio a questa Z
                u_arm = (1.35 - v.co.z) / 0.25
                cx = sx * (0.155 + 0.245 * u_arm)
                cy = 0.010
                scale_in = 1.0 - 0.34 * t_up
                v.co.x = cx + (v.co.x - cx) * scale_in
                v.co.y = cy + (v.co.y - cy) * scale_in
                v.co.z -= 0.010 * t_up
        manica.data.update()

    spalla = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if spalla:
        for v in spalla.data.vertices:
            # Allarga leggermente l'involucro della mantellina lungo Y per avvolgere bene il braccio
            v.co.y *= 1.18
            if abs(v.co.x) > 0.16:
                v.co.z += 0.006
        spalla.data.update()

# ==============================================================================
# 3. AVVICINAMENTO SACCA ARROTOLATA ALLA SCHIENA E TUBI MORBIDI
# ==============================================================================
for name_s in ("Sacca_Arrotolata", "Sacca_Cinghia_SX", "Sacca_Cinghia_DX"):
    o_s = bpy.data.objects.get(name_s)
    if o_s:
        for v in o_s.data.vertices:
            v.co.y -= 0.042
            v.co.z += 0.015
        o_s.data.update()

for side, sx in (("SX", 1.0), ("DX", -1.0)):
    # Ricrea i tubi pendenti sotto la sacca con 18 punti morbidi e aderenti alla mantella
    loop_pts = []
    for k in range(18):
        t = k / 17.0
        ang = t * math.pi
        px = sx * (0.082 * (1.0 - t) + 0.024 * t + 0.015 * math.sin(ang))
        py = 0.185 - 0.025 * t + 0.018 * math.sin(ang)
        pz = 1.00 - 0.145 * math.sin(ang) - 0.02 * t
        loop_pts.append((px, py, pz))
    create_tube(f"Sacca_Tubo_Basso_{side}", loop_pts, 0.0115, mat_cuoio_medio, segs=10)

# ==============================================================================
# 4. TEXTURE ORGANICA DELLA MANTELLA VERDE (senza puntini regolari)
# ==============================================================================
def update_organic_cape_tex():
    img = bpy.data.images.get("Tex_MantellaVerde")
    if not img:
        return
    size = img.size[0]
    y, x = np.mgrid[0:size, 0:size] / float(size)
    # Distorsione di dominio (domain warping) per eliminare qualsiasi griglia regolare
    wx = x + 0.06 * np.sin(2 * math.pi * (y * 3.0 + x * 2.0)) + 0.03 * np.cos(2 * math.pi * (y * 7.0 - x * 4.0))
    wy = y + 0.06 * np.cos(2 * math.pi * (x * 4.0 - y * 3.0)) + 0.03 * np.sin(2 * math.pi * (x * 6.0 + y * 5.0))

    # Pieghe drappeggiate verticali morbide
    drape = 0.5 + 0.5 * np.sin(2 * math.pi * wx * 8.0)
    # Rumore organico a più ottave sfasate
    n1 = np.sin(2 * math.pi * (wx * 5.0 + wy * 3.0 + 0.5)) * np.cos(2 * math.pi * (wx * 4.0 - wy * 6.0))
    n2 = np.sin(2 * math.pi * (wx * 11.0 - wy * 9.0 + 1.9)) * np.cos(2 * math.pi * (wx * 7.0 + wy * 12.0))
    wear = np.clip(0.5 + 0.32 * n1 + 0.18 * n2, 0.0, 1.0)

    # Sfumatura fangosa/usurata sul fondo strappato (y < 0.36)
    mud = np.clip((0.38 - wy) / 0.38, 0.0, 1.0) ** 1.5
    mud = np.clip(mud * (0.6 + 0.5 * wear), 0.0, 1.0)

    c_dark = (0.13, 0.21, 0.18)
    c_mid = (0.24, 0.34, 0.29)
    c_mud = (0.37, 0.33, 0.26)

    pixels = np.ones((size, size, 4), dtype=np.float32)
    mix_v = np.clip(0.45 * drape + 0.55 * wear, 0.0, 1.0)
    for ch in range(3):
        col = c_dark[ch] * (1.0 - mix_v) + c_mid[ch] * mix_v
        col = col * (1.0 - mud * 0.72) + c_mud[ch] * (mud * 0.72)
        pixels[:, :, ch] = np.clip(col, 0.0, 1.0)
    img.pixels.foreach_set(pixels.ravel())
    img.pack()

update_organic_cape_tex()

# ==============================================================================
# 5. RIFINITURA BOCCA/LABBRA, COLLO E ALTEZZA CAPELLI (1.700 m esatti)
# ==============================================================================
# Sostituisci le due mezze labbra separate con labbra morbide unite senza fessura chiara
for lname in ("Labbro_Sup", "Labbro_Inf"):
    if lname in bpy.data.objects:
        o = bpy.data.objects[lname]
        m = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(m)

mat_labbra.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.52, 0.31, 0.27, 1.0)
mat_labbra.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.65

lip_pts = [
    (-0.015, -0.075, 1.520),
    (-0.007, -0.079, 1.522),
    (0.000,  -0.080, 1.521),
    (0.007,  -0.079, 1.522),
    (0.015,  -0.075, 1.520),
]
create_tube("Labbra", lip_pts, [(0.0018, 0.0020), (0.0038, 0.0042), (0.0040, 0.0045), (0.0038, 0.0042), (0.0018, 0.0020)], mat_labbra, segs=12)

# Alza leggermente il colletto interno beige così il collo ha proporzioni perfette
colletto_in = bpy.data.objects.get("Camicia_Colletto")
if colletto_in:
    for v in colletto_in.data.vertices:
        if v.co.z > 1.40:
            v.co.z += 0.012
    colletto_in.data.update()

# Normalizza l'altezza massima esattamente a 1.700 m (con Z min = 0.000 m)
pts_all = [o.matrix_world @ Vector(c) for o in scn.objects if o.type == "MESH" for c in o.bound_box]
min_z = min(p.z for p in pts_all)
max_z = max(p.z for p in pts_all)
# Portiamo i vertici più alti dei capelli esattamente a 1.700 m
hair_objs = [o for o in scn.objects if o.type == "MESH" and (o.name.startswith("Capelli") or o.name.startswith("Ciocca"))]
curr_top = max( (o.matrix_world @ v.co).z for o in hair_objs for v in o.data.vertices )
dz_top = 1.700 - curr_top
for o in hair_objs:
    for v in o.data.vertices:
        if v.co.z > 1.62:
            t_h = (v.co.z - 1.62) / (curr_top - 1.62)
            v.co.z += dz_top * t_h
    o.data.update()

pts_all = [o.matrix_world @ Vector(c) for o in scn.objects if o.type == "MESH" for c in o.bound_box]
min_z = min(p.z for p in pts_all)
max_z = max(p.z for p in pts_all)
tris = sum(len(p.vertices) - 2 for o in scn.objects if o.type == "MESH" for p in o.data.polygons)
log(f"Passo 4 completato: Z_min={min_z:.4f}m, Z_max={max_z:.4f}m, Altezza={max_z-min_z:.4f}m, Triangoli={tris}")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("passo4_rifinitura", viste=["fronte", "destra", "retro", "sinistra", "tre_quarti"])
