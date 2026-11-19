import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Matrix, Euler

# ==============================================================================
# PASSO 3: Correzione spalle mantella e luce retro + Casco da palombaro in ottone
#          sulla schiena (con oblò, griglie, bulloni, valvole e tubi) + Sacca
#          arrotolata inferiore + Corda a spire e borraccia sul fianco destro +
#          Astuccio cilindrico sul fianco sinistro + Bussola/manometro da polso SX
# ==============================================================================

scn = bpy.context.scene

# 1. Correggi orientamento Luce_Back per illuminare bene la vista posteriore ("retro")
luce_back = bpy.data.objects.get("Luce_Back")
if luce_back:
    luce_back.location = (0.6, 3.2, 3.2)
    luce_back.rotation_euler = (math.radians(-50.0), math.radians(10.0), math.radians(8.0))
    luce_back.data.energy = 2.6

# Materiali aggiuntivi per vetro oblò, quadrante verde, corda e astuccio pergamena
def ensure_extra_mats():
    if "Mat_VetroOblo" not in bpy.data.materials:
        m = bpy.data.materials.new("Mat_VetroOblo")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.12, 0.24, 0.22, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.12
        bsdf.inputs["Metallic"].default_value = 0.25
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.08, 0.22, 0.18, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.35

    if "Mat_QuadranteVerde" not in bpy.data.materials:
        m = bpy.data.materials.new("Mat_QuadranteVerde")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.28, 0.68, 0.52, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.15
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.25, 0.65, 0.48, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.85

    if "Mat_Corda" not in bpy.data.materials:
        m = bpy.data.materials.new("Mat_Corda")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.55, 0.44, 0.31, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85

    if "Mat_Pergamena" not in bpy.data.materials:
        m = bpy.data.materials.new("Mat_Pergamena")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.58, 0.47, 0.34, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.72

ensure_extra_mats()
mat_ottone = bpy.data.materials["Mat_Ottone"]
mat_cuoio_scuro = bpy.data.materials["Mat_CuoioScuro"]
mat_cuoio_medio = bpy.data.materials["Mat_CuoioMedio"]
mat_cuoio_chiaro = bpy.data.materials["Mat_CuoioChiaro"]
mat_metallo_scuro = bpy.data.materials["Mat_MetalloScuro"]
mat_vetro = bpy.data.materials["Mat_VetroOblo"]
mat_quadrante = bpy.data.materials["Mat_QuadranteVerde"]
mat_corda = bpy.data.materials["Mat_Corda"]
mat_pergamena = bpy.data.materials["Mat_Pergamena"]

# Pulizia di eventuali oggetti del passo 3 già presenti
p3_prefixes = (
    "Casco_", "Tubo_Casco", "Sacca_", "Corda_", "Borraccia_", "Astuccio_", "Strumento_Polso"
)
for obj in list(bpy.data.objects):
    if obj.type == "MESH" and obj.name.startswith(p3_prefixes):
        m = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(m)

# ==============================================================================
# 2. CORREZIONE MORBIDA DELLE SPALLE DELLA MANTELLA (elimina le punte a Z=1.41)
# ==============================================================================
cape_body = bpy.data.objects.get("Mantella_Corpo")
if cape_body:
    for v in cape_body.data.vertices:
        if v.co.z > 1.25 and abs(v.co.x) > 0.14:
            # Abbassa dolcemente il profilo esterno della spalla seguendo il deltoide
            excess_x = (abs(v.co.x) - 0.14) / 0.16
            max_allowed_z = 1.375 - 0.095 * (excess_x ** 1.1)
            if v.co.z > max_allowed_z:
                v.co.z = max_allowed_z
    cape_body.data.update()

for side, sx in (("SX", 1.0), ("DX", -1.0)):
    sp = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if sp:
        for v in sp.data.vertices:
            # Espandi leggermente la mantellina sulla spalla per coprire del tutto la manica beige sopra
            v.co.z += 0.008
            v.co.y *= 1.08
        sp.data.update()

# ==============================================================================
# 3. FUNZIONI HELPER GEOMETRICHE PER TUBI, CILINDRI E OBLÒ
# ==============================================================================
def create_tube(name, pts, radii, mat, segs=14, closed=False, cap_ends=True, corr_amp=0.0, corr_freq=18):
    bm = bmesh.new()
    rings = []
    n = len(pts)
    for i in range(n):
        c = Vector(pts[i])
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
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
        v_t = i / max(1, n - 1)
        ring_v = []
        rmod = 1.0 + (corr_amp * math.sin(v_t * math.pi * corr_freq) if corr_amp else 0.0)
        for j in range(segs):
            th = 2.0 * math.pi * j / segs
            pt = c + b1 * (rx * rmod * math.cos(th)) + b2 * (ry * rmod * math.sin(th))
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
# 4. CASCO DA PALOMBARO IN OTTONE SULLA SCHIENA (Z=1.08..1.45, Y=0.20)
# ==============================================================================
def build_diving_helmet():
    h_center = Vector((0.0, 0.205, 1.255))

    # A) Calotta principale in ottone con gorgiera inferiore svasata
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=20, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        rx, ry, rz = 0.142, 0.132, 0.152
        # Appiattisci leggermente il lato verso la schiena (y < -0.5)
        if y < -0.45:
            y = -0.45 + (y + 0.45) * 0.45
        # Svasatura a campana sul colletto inferiore (z < -0.65)
        if z < -0.65:
            flare = (-z - 0.65) / 0.35
            rx += 0.018 * flare
            ry += 0.016 * flare
        v.co = h_center + Vector((x * rx, y * ry, z * rz))
    for f in bm.faces:
        f.smooth = True
    m_dome = bpy.data.meshes.new("Casco_Calotta")
    bm.normal_update()
    bm.to_mesh(m_dome)
    bm.free()
    o_dome = bpy.data.objects.new("Casco_Calotta", m_dome)
    scn.collection.objects.link(o_dome)
    o_dome.data.materials.append(mat_ottone)

    # Anello/flangia di giunzione alla base del casco (Z=1.135)
    ring_base = []
    for k in range(24):
        th = 2.0 * math.pi * k / 24.0
        ring_base.append((0.144 * math.cos(th), 0.205 + 0.128 * math.sin(th), 1.135))
    create_tube("Casco_Flangia_Base", ring_base, (0.014, 0.016), mat_ottone, segs=10, closed=True)

    # Funzione per costruire un oblò completo di cornice in ottone, bulloni, lente in vetro e griglia a croce
    def build_porthole(tag, center_pt, normal_dir, up_dir, radius):
        n_vec = Vector(normal_dir).normalized()
        u_vec = Vector(up_dir).normalized()
        r_vec = u_vec.cross(n_vec).normalized()
        u_vec = n_vec.cross(r_vec).normalized()
        c_pt = Vector(center_pt)

        # 1. Cornice circolare spessa in ottone
        frame_pts = []
        n_ring = 24
        for k in range(n_ring):
            th = 2.0 * math.pi * k / n_ring
            pt = c_pt + (r_vec * math.cos(th) + u_vec * math.sin(th)) * radius
            frame_pts.append(tuple(pt))
        create_tube(f"Casco_Cornice_{tag}", frame_pts, (0.014, 0.018), mat_ottone, segs=10, closed=True)

        # 2. Lente convessa in vetro scuro/verde
        bm_g = bmesh.new()
        bmesh.ops.create_uvsphere(bm_g, u_segments=18, v_segments=10, radius=1.0)
        for v in bm_g.verts:
            local = r_vec * (v.co.x * radius * 0.92) + u_vec * (v.co.y * radius * 0.92) + n_vec * (max(0.0, v.co.z) * 0.018)
            v.co = c_pt + local
        for f in bm_g.faces:
            f.smooth = True
        m_g = bpy.data.meshes.new(f"Casco_Vetro_{tag}")
        bm_g.to_mesh(m_g)
        bm_g.free()
        o_g = bpy.data.objects.new(f"Casco_Vetro_{tag}", m_g)
        scn.collection.objects.link(o_g)
        o_g.data.materials.append(mat_vetro)

        # 3. Griglia protettiva bombata in ottone (2 sbarre verticali + 2 sbarre orizzontali)
        for bar_idx, offset_frac in enumerate((-0.36, 0.36)):
            chord = math.sqrt(max(0.05, 1.0 - offset_frac ** 2)) * radius * 0.96
            # Sbarra verticale
            v_pts = []
            # Sbarra orizzontale
            h_pts = []
            for s in range(7):
                st = -1.0 + 2.0 * s / 6.0
                arch = 0.020 * (1.0 - st ** 2) + 0.008
                p_v = c_pt + r_vec * (offset_frac * radius) + u_vec * (st * chord) + n_vec * arch
                p_h = c_pt + u_vec * (offset_frac * radius) + r_vec * (st * chord) + n_vec * arch
                v_pts.append(tuple(p_v))
                h_pts.append(tuple(p_h))
            create_tube(f"Casco_GrigliaV_{tag}_{bar_idx}", v_pts, 0.0045, mat_ottone, segs=8)
            create_tube(f"Casco_GrigliaH_{tag}_{bar_idx}", h_pts, 0.0045, mat_ottone, segs=8)

        # 4. Bulloni sulla cornice (8 bulloni)
        bm_b = bmesh.new()
        for k in range(8):
            th = 2.0 * math.pi * k / 8.0 + math.pi / 8.0
            b_pos = c_pt + (r_vec * math.cos(th) + u_vec * math.sin(th)) * (radius * 1.03) + n_vec * 0.013
            ret = bmesh.ops.create_uvsphere(bm_b, u_segments=6, v_segments=4, radius=0.0055)
            for v in ret["verts"]:
                v.co += b_pos
        m_b = bpy.data.meshes.new(f"Casco_Bulloni_{tag}")
        bm_b.to_mesh(m_b)
        bm_b.free()
        o_b = bpy.data.objects.new(f"Casco_Bulloni_{tag}", m_b)
        scn.collection.objects.link(o_b)
        o_b.data.materials.append(mat_ottone)

    # Oblò grande posteriore (+Y)
    build_porthole("Retro", (0.0, 0.332, 1.258), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 0.078)
    # Cerniera/chiusura laterale dell'oblò posteriore (visibile a destra nel retro)
    create_tube("Casco_Cerniera_Retro", [(0.082, 0.320, 1.235), (0.092, 0.320, 1.258), (0.082, 0.320, 1.280)], 0.011, mat_ottone, segs=8)

    # Oblò laterali sinistro (+X) e destro (-X) (ben visibili nelle viste laterali!)
    build_porthole("SX", (0.138, 0.205, 1.255), (1.0, 0.05, 0.0), (0.0, 0.0, 1.0), 0.054)
    build_porthole("DX", (-0.138, 0.205, 1.255), (-1.0, 0.05, 0.0), (0.0, 0.0, 1.0), 0.054)

    # Valvola/torretta superiore centrale (Z=1.40..1.455) e raccordo obliquo spalla SX (visibile anche di fronte!)
    create_tube("Casco_Valvola_Top", [(0.0, 0.205, 1.395), (0.0, 0.205, 1.430), (0.0, 0.205, 1.455)], [0.032, 0.026, 0.030], mat_ottone, segs=12)
    create_tube("Casco_Valvola_SpallaSX", [(0.075, 0.175, 1.375), (0.105, 0.155, 1.415), (0.118, 0.145, 1.432)], [0.022, 0.019, 0.023], mat_ottone, segs=10)

    # Tubi corrugati di respirazione che avvolgono la base del casco
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        hose_pts = [
            (sx * 0.035, 0.315, 1.125),
            (sx * 0.110, 0.295, 1.115),
            (sx * 0.158, 0.240, 1.130),
            (sx * 0.165, 0.170, 1.175),
            (sx * 0.135, 0.115, 1.235),
        ]
        create_tube(f"Tubo_Casco_{side}", hose_pts, 0.017, mat_ottone, segs=12, corr_amp=0.14, corr_freq=16)

build_diving_helmet()

# ==============================================================================
# 5. SACCA ARROTOLATA SOTTO IL CASCO + CINGHIE E TUBI PENDENTI (Z=0.82..1.09)
# ==============================================================================
def build_backpack_roll():
    # Sacca cilindrica orizzontale in cuoio/tela sotto il casco (da X=-0.105 a X=+0.105, Y=0.235, Z=1.015)
    roll_pts = [
        (-0.108, 0.235, 1.015),
        (-0.055, 0.240, 1.012),
        (0.000,  0.242, 1.010),
        (0.055,  0.240, 1.012),
        (0.108,  0.235, 1.015),
    ]
    create_tube("Sacca_Arrotolata", roll_pts, [0.052, 0.056, 0.055, 0.056, 0.052], mat_cuoio_chiaro, segs=16)

    # Due cinghie verticali in cuoio scuro che stringono la sacca
    for side, sx in (("SX", 0.062), ("DX", -0.062)):
        strap_ring = []
        for k in range(18):
            th = 2.0 * math.pi * k / 18.0
            strap_ring.append((sx, 0.238 + 0.058 * math.cos(th), 1.012 + 0.058 * math.sin(th)))
        create_tube(f"Sacca_Cinghia_{side}", strap_ring, (0.006, 0.013), mat_cuoio_scuro, segs=8, closed=True)

    # Cinghie/tubi curvi che scendono sotto la sacca (ben visibili nel retro e nei profili a Z=0.83..0.98)
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        loop_pts = [
            (sx * 0.085, 0.215, 0.985),
            (sx * 0.095, 0.235, 0.900),
            (sx * 0.072, 0.215, 0.840),
            (sx * 0.035, 0.175, 0.865),
            (sx * 0.020, 0.145, 0.955),
        ]
        create_tube(f"Sacca_Tubo_Basso_{side}", loop_pts, 0.012, mat_cuoio_medio, segs=10)

build_backpack_roll()

# ==============================================================================
# 6. CORDA ARROTOLATA E BORRACCIA SUL FIANCO DESTRO (-X, sinistra nel frontale)
# ==============================================================================
def build_right_hip_gear():
    # A) Corda arrotolata a 5 spire ovali pendenti dalla cintura sul fianco anteriore destro (-X)
    for loop_i in range(5):
        n_pts = 28
        rope_pts = []
        # Ogni spira è leggermente sfalsata in X/Y e varia in lunghezza Z (da Z=0.95 fino a Z=0.66..0.72)
        z_top = 0.955
        z_bot = 0.665 + 0.014 * (loop_i % 3)
        z_mid = 0.5 * (z_top + z_bot)
        rz = 0.5 * (z_top - z_bot)
        rx_loop = 0.018 + 0.004 * loop_i
        ry_loop = 0.042 + 0.004 * (loop_i % 2)
        cx_base = -0.138 - 0.007 * loop_i
        cy_base = -0.058 + 0.005 * loop_i

        for k in range(n_pts):
            th = 2.0 * math.pi * k / n_pts
            # Spira ovale inclinata lungo il fianco/coscia destra
            dz = rz * math.cos(th)
            d_perp = math.sin(th)
            px = cx_base - 0.015 * (1.0 - math.cos(th)) + rx_loop * d_perp * 0.45
            py = cy_base + ry_loop * d_perp
            pz = z_mid + dz
            rope_pts.append((px, py, pz))
        create_tube(f"Corda_Spira_{loop_i}", rope_pts, 0.0075, mat_corda, segs=8, closed=True)

    # Passante in cuoio che tiene la corda appesa alla cintura (Z=0.955)
    holder_pts = [
        (-0.125, -0.068, 0.985),
        (-0.158, -0.072, 0.955),
        (-0.172, -0.045, 0.945),
        (-0.135, -0.038, 0.975),
    ]
    create_tube("Corda_Passante", holder_pts, (0.006, 0.012), mat_cuoio_scuro, segs=8, closed=True)

    # B) Borraccia/contenitore cilindrico con calotta sferica sul fianco esterno destro (-X)
    # Inclinato leggermente verso l'esterno (visibile a sinistra nella vista frontale!)
    flask_pts = [
        (-0.168, -0.032, 0.915),  # Collo/tappo superiore
        (-0.185, -0.030, 0.875),  # Calotta bombata superiore
        (-0.198, -0.028, 0.830),  # Corpo alto
        (-0.215, -0.025, 0.770),  # Corpo medio
        (-0.230, -0.022, 0.715),  # Fondo borraccia
    ]
    flask_rads = [0.020, 0.044, 0.040, 0.038, 0.036]
    create_tube("Borraccia_Corpo_DX", flask_pts, flask_rads, mat_cuoio_medio, segs=16)

    # Ghiere/cinturini in cuoio scuro e ottone sulla borraccia
    for t_f in (0.35, 0.75):
        c_f = Vector(flask_pts[1]).lerp(Vector(flask_pts[-1]), t_f)
        ax = (Vector(flask_pts[-1]) - Vector(flask_pts[1])).normalized()
        b1 = ax.cross(Vector((0, 1, 0))).normalized()
        b2 = b1.cross(ax).normalized()
        r_f = 0.041
        ring_f = [tuple(c_f + b1 * (r_f * math.cos(2 * math.pi * k / 14)) + b2 * (r_f * math.sin(2 * math.pi * k / 14))) for k in range(14)]
        create_tube(f"Borraccia_Cinghia_{int(t_f*10)}", ring_f, (0.005, 0.010), mat_cuoio_scuro, segs=8, closed=True)

build_right_hip_gear()

# ==============================================================================
# 7. ASTUCCIO CILINDRICO LUNGO SUL FIANCO SINISTRO (+X, destra nel frontale)
# ==============================================================================
def build_left_hip_gear():
    # Astuccio cilindrico lungo in pergamena/cuoio chiaro con ghiere in ottone (Z=0.58..0.94)
    case_top = Vector((0.178, -0.032, 0.935))
    case_bot = Vector((0.232, -0.010, 0.575))
    case_pts = [tuple(case_top.lerp(case_bot, k / 6.0)) for k in range(7)]
    create_tube("Astuccio_Cilindro_SX", case_pts, 0.036, mat_pergamena, segs=18)

    # 4 ghiere/fasce in ottone e cuoio lungo il cilindro
    ax = (case_bot - case_top).normalized()
    b1 = ax.cross(Vector((0, 1, 0))).normalized()
    b2 = b1.cross(ax).normalized()
    for idx, t_c in enumerate((0.06, 0.34, 0.68, 0.94)):
        c_c = case_top.lerp(case_bot, t_c)
        r_c = 0.039
        ring_c = [tuple(c_c + b1 * (r_c * math.cos(2 * math.pi * k / 16)) + b2 * (r_c * math.sin(2 * math.pi * k / 16))) for k in range(16)]
        mat_band = mat_ottone if idx in (0, 3) else mat_cuoio_scuro
        create_tube(f"Astuccio_Fascia_{idx}", ring_c, (0.005, 0.011), mat_band, segs=8, closed=True)

    # Tubo/strumento secondario più sottile affiancato all'astuccio
    rod_top = Vector((0.155, -0.068, 0.925))
    rod_bot = Vector((0.195, -0.052, 0.640))
    create_tube("Astuccio_TuboPiccolo_SX", [tuple(rod_top.lerp(rod_bot, k / 4.0)) for k in range(5)], 0.014, mat_cuoio_scuro, segs=12)

    # Cinghietti di sospensione alla cintura obliqua
    for t_s in (0.15, 0.55):
        p_case = case_top.lerp(case_bot, t_s)
        p_belt = Vector((0.145, -0.030, 0.945))
        create_tube(f"Astuccio_Sospensione_{int(t_s*10)}", [tuple(p_belt), tuple(p_case)], (0.005, 0.010), mat_cuoio_scuro, segs=8)

build_left_hip_gear()

# ==============================================================================
# 8. STRUMENTO / BUSSOLA DA POLSO SULL'AVAMBRACCIO SINISTRO (+X)
# ==============================================================================
def build_wrist_instrument():
    # Posizionato sul dorso/esterno del guanto sinistro (+X) a metà avambraccio
    w_center = Vector((0.448, -0.038, 1.072))
    # Normale orientata verso l'esterno-avanti dell'avambraccio sinistro
    n_vec = Vector((0.55, -0.62, 0.56)).normalized()
    u_vec = Vector((-0.68, 0.12, 0.72)).normalized()
    r_vec = u_vec.cross(n_vec).normalized()
    u_vec = n_vec.cross(r_vec).normalized()
    rad = 0.036

    # Cassa circolare in ottone
    bezel_pts = []
    for k in range(20):
        th = 2.0 * math.pi * k / 20.0
        bezel_pts.append(tuple(w_center + (r_vec * math.cos(th) + u_vec * math.sin(th)) * rad))
    create_tube("Strumento_Polso_Cassa", bezel_pts, (0.009, 0.012), mat_ottone, segs=10, closed=True)

    # Quadrante verde luminoso interno
    bm_d = bmesh.new()
    bmesh.ops.create_uvsphere(bm_d, u_segments=16, v_segments=8, radius=1.0)
    for v in bm_d.verts:
        v.co = w_center + r_vec * (v.co.x * rad * 0.85) + u_vec * (v.co.y * rad * 0.85) + n_vec * (v.co.z * 0.006)
    for f in bm_d.faces:
        f.smooth = True
    m_d = bpy.data.meshes.new("Strumento_Polso_Quadrante")
    bm_d.to_mesh(m_d)
    bm_d.free()
    o_d = bpy.data.objects.new("Strumento_Polso_Quadrante", m_d)
    scn.collection.objects.link(o_d)
    o_d.data.materials.append(mat_quadrante)

tris = sum(len(o.data.polygons) for o in scn.objects if o.type == "MESH")
log(f"Passo 3 completato: Poligoni totali={tris}")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("passo3_accessori", viste=["fronte", "destra", "retro", "sinistra", "tre_quarti"])
