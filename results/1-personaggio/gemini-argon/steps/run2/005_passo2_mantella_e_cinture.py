import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# ==============================================================================
# PASSO 2: Rifinitura dettagli testa/stivali + Mantella verde strappata a doppio
#          strato con colletto, spallacci, pieghe, strappi e fori + Conchiglie
#          sulla spalla + Imbracatura sul petto + Cinture in vita e medaglione.
# ==============================================================================

scn = bpy.context.scene

def make_cape_tex(name, size=512):
    """Texture procedurale per la mantella: verde muschio/acqua in alto, macchie di usura
    e sfumatura fangosa/ocra verso il lembo inferiore strappato."""
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    y, x = np.mgrid[0:size, 0:size] / float(size)  # y=0 fondo mantella, y=1 spalle
    # Pieghe verticali e rumore organico
    folds = 0.5 + 0.5 * np.sin(2 * math.pi * x * 9.0 + 0.4 * np.sin(2 * math.pi * y * 4.0))
    noise1 = np.sin(2 * math.pi * (x * 7.0 + y * 5.0)) * np.cos(2 * math.pi * (x * 11.0 - y * 8.0))
    noise2 = np.sin(2 * math.pi * (x * 23.0 - y * 19.0 + 1.7))
    wear = np.clip(0.5 + 0.35 * noise1 + 0.20 * noise2, 0.0, 1.0)
    # Fango/usura concentrati nel terzo inferiore (y < 0.38)
    mud_mask = np.clip((0.42 - y) / 0.42, 0.0, 1.0) ** 1.4
    mud_mask = np.clip(mud_mask * (0.65 + 0.6 * wear), 0.0, 1.0)
    # Graffi chiari sparsi
    scratches = np.clip((np.sin(2 * math.pi * (x * 31.0 + y * 17.0)) * np.cos(2 * math.pi * (x * 29.0 - y * 37.0)) - 0.78) * 4.5, 0.0, 1.0)

    c_green_dark = (0.14, 0.22, 0.19)
    c_green_light = (0.25, 0.35, 0.30)
    c_mud = (0.38, 0.34, 0.27)
    c_scratch = (0.48, 0.50, 0.44)

    pixels = np.ones((size, size, 4), dtype=np.float32)
    mix_g = np.clip(0.35 * folds + 0.65 * wear, 0.0, 1.0)
    for ch in range(3):
        col = c_green_dark[ch] * (1.0 - mix_g) + c_green_light[ch] * mix_g
        col = col * (1.0 - mud_mask * 0.75) + c_mud[ch] * (mud_mask * 0.75)
        col = col * (1.0 - scratches * 0.55) + c_scratch[ch] * (scratches * 0.55)
        pixels[:, :, ch] = np.clip(col, 0.0, 1.0)

    img.pixels.foreach_set(pixels.ravel())
    img.pack()
    return img

def get_or_create_cape_mat():
    name = "Mat_MantellaVerde"
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.84
    bsdf.inputs["Metallic"].default_value = 0.0
    img = make_cape_tex("Tex_MantellaVerde")
    tnode = nodes.new("ShaderNodeTexImage")
    tnode.image = img
    links.new(tnode.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

def get_or_create_shell_mat():
    name = "Mat_Conchiglia"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.76, 0.71, 0.62, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    return mat

mat_cape = get_or_create_cape_mat()
mat_shell = get_or_create_shell_mat()
mat_cuoio_scuro = bpy.data.materials["Mat_CuoioScuro"]
mat_cuoio_medio = bpy.data.materials["Mat_CuoioMedio"]
mat_cuoio_chiaro = bpy.data.materials["Mat_CuoioChiaro"]
mat_ottone = bpy.data.materials["Mat_Ottone"]
mat_camicia = bpy.data.materials["Mat_Camicia"]
mat_capelli_scuri = bpy.data.materials["Mat_CapelliScuri"]
mat_labbra = bpy.data.materials["Mat_Labbra"]

# Pulizia di eventuali oggetti del passo 2 già presenti
p2_prefixes = (
    "Mantella", "Conchiglia", "Cinghia_Petto", "Fibbia", "Cintura", "Medaglione", "Lembo_Stoffa"
)
for obj in list(bpy.data.objects):
    if obj.type == "MESH" and obj.name.startswith(p2_prefixes):
        m = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(m)

# ==============================================================================
# 1. PICCOLE CORREZIONI SU SUOLA STIVALI, LABBRA E SILHOUETTE CAPELLI
# ==============================================================================
for side in ("SX", "DX"):
    sole = bpy.data.objects.get(f"Stivale_Suola_{side}")
    if sole:
        for v in sole.data.vertices:
            # Ritira leggermente la punta anteriore della suola sotto la tomaia
            if v.co.y < -0.142:
                v.co.y = -0.142

# Rendi il materiale labbra più naturale e meno lucido
mat_labbra.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.68
mat_labbra.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.58, 0.36, 0.31, 1.0)
for lname, dz in (("Labbro_Sup", 0.006), ("Labbro_Inf", 0.006)):
    lobj = bpy.data.objects.get(lname)
    if lobj:
        for v in lobj.data.vertices:
            v.co.z += dz
            v.co.y += 0.0015

# Rendi la silhouette dei capelli più mossa e raccolta verso la nuca/tempie
for obj in scn.objects:
    if obj.type == "MESH" and obj.name.startswith("Ciocca_Scura_"):
        for v in obj.data.vertices:
            if v.co.z < 1.58:
                t_low = (1.58 - v.co.z) / 0.10
                # Avvicina le punte inferiori alla testa/collo per evitare l'effetto "a tenda"
                v.co.x *= (1.0 - 0.16 * t_low)
        obj.data.update()

# ==============================================================================
# 2. COSTRUZIONE MANTELLA VERDE STRAPPATA (CORPO, SPALLACCI E COLLETTO ALTO)
# ==============================================================================
def solidify_bmesh(bm, thickness=0.0045):
    """Dà spessore reale alla mesh di stoffa così è visibile da entrambi i lati in Blender e Unity."""
    bm.normal_update()
    geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
    bmesh.ops.solidify(bm, geom=geom, thickness=thickness)
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True

def build_torn_cape():
    # A) CORPO PRINCIPALE DELLA MANTELLA (da Z=1.37 spalle fino a Z=0.18..0.44 polpacci)
    bm = bmesh.new()
    nu = 68  # colonne lungo l'arco (da fianco sinistro anteriore a fianco destro anteriore passando per il retro)
    nv = 44  # righe verticali dall'alto (v=1) al basso (v=0)

    # Profilo di strappo irregolare sul fondo per ogni colonna u in [0, 1]
    def bottom_tear_z(u):
        # Strappi profondi a V come nel riferimento (vista frontale e posteriore)
        waves = (
            0.055 * math.sin(u * math.pi * 7.0 + 0.4)
            + 0.045 * math.cos(u * math.pi * 13.0 - 0.8)
            + 0.035 * math.sin(u * math.pi * 23.0 + 1.5)
            + 0.025 * math.cos(u * math.pi * 37.0)
        )
        # I bordi anteriori (u vicino a 0 o 1) salgono verso i fianchi/cosce
        edge_lift = 0.22 * (max(0.0, 0.18 - u) / 0.18) ** 1.4 + 0.22 * (max(0.0, u - 0.82) / 0.18) ** 1.4
        return 0.29 + waves + edge_lift

    grid = [[None] * nu for _ in range(nv)]
    uv_coords = [[(0.0, 0.0)] * nu for _ in range(nv)]

    for iv in range(nv):
        v_t = iv / float(nv - 1)  # 0.0 = fondo strappato, 1.0 = spalle/collo
        for iu in range(nu):
            u_t = iu / float(nu - 1)  # 0.0 = lato destro ant (-X), 0.5 = centro retro (+Y), 1.0 = lato sinistro ant (+X)
            # Angolo azimutale attorno al personaggio:
            # In alto (v_t=1) copre anche il davanti delle spalle (da -145° a +145° rispetto a +Y retro)
            # In basso (v_t=0) si apre sul davanti (da -92° a +92° rispetto a +Y retro)
            max_ang = math.radians(92.0 + 55.0 * (v_t ** 1.2))
            ang = (u_t - 0.5) * 2.0 * max_ang  # ang=0 è +Y (retro), ang>0 è +X (SX), ang<0 è -X (DX)

            z_bot = bottom_tear_z(u_t)
            z_top = 1.375 - 0.035 * (abs(u_t - 0.5) * 2.0) ** 2
            z = z_bot * (1.0 - v_t) + z_top * v_t

            # Semilarghezza X e semiprofondità Y della mantella a questa altezza
            # In alto avvolge le spalle, scendendo si allarga ad A dietro e sui lati
            rx_base = 0.205 * v_t + 0.365 * (1.0 - v_t)
            ry_base = 0.108 * v_t + 0.165 * (1.0 - v_t)

            # Evita compenetrazione con i fianchi/gonna giacca e con le braccia in posa A
            if 0.72 < z < 1.08:
                hip_bump = math.sin((z - 0.72) / 0.36 * math.pi)
                rx_base += 0.028 * hip_bump
                ry_base += 0.022 * hip_bump
            if z > 1.08 and abs(ang) > math.radians(52.0):
                # Solleva/allarga sopra le braccia in posa A (Manica/Spalla)
                arm_zone = min(1.0, (abs(ang) - math.radians(52.0)) / math.radians(50.0)) * ((z - 1.08) / 0.30)
                rx_base += 0.085 * arm_zone
                z += 0.045 * arm_zone

            # Pieghe drappeggiate verticali profonde
            fold_depth = (0.006 + 0.024 * (1.0 - v_t)) * (
                0.65 * math.sin(u_t * math.pi * 10.0)
                + 0.35 * math.cos(u_t * math.pi * 18.0 + 0.7)
            )
            rx = rx_base + fold_depth
            ry = ry_base + fold_depth

            px = rx * math.sin(ang)
            py = 0.015 + ry * math.cos(ang)
            v_vert = bm.verts.new(Vector((px, py, z)))
            grid[iv][iu] = v_vert
            uv_coords[iv][iu] = (u_t, v_t)

    uv_layer = bm.loops.layers.uv.verify()

    # Fori e squarci irregolari nella metà inferiore della mantella (come nel riferimento)
    holes = [
        # (u_center, v_center, ru, rv)
        (0.28, 0.16, 0.032, 0.055),
        (0.36, 0.09, 0.025, 0.045),
        (0.64, 0.14, 0.030, 0.052),
        (0.74, 0.22, 0.026, 0.048),
        (0.47, 0.07, 0.022, 0.045),
        (0.19, 0.11, 0.024, 0.042),
        (0.81, 0.12, 0.024, 0.042),
    ]

    for iv in range(nv - 1):
        for iu in range(nu - 1):
            u_c = (iu + 0.5) / float(nu - 1)
            v_c = (iv + 0.5) / float(nv - 1)
            # Controlla se questa faccia cade dentro un foro/strappo
            in_hole = False
            for hu, hv, ru, rv in holes:
                if ((u_c - hu) / ru) ** 2 + ((v_c - hv) / rv) ** 2 < 1.0:
                    in_hole = True
                    break
            # Tagli verticali profondi dal bordo inferiore
            for tear_u, tear_w, tear_h in ((0.23, 0.016, 0.14), (0.41, 0.015, 0.12), (0.58, 0.016, 0.15), (0.77, 0.016, 0.13)):
                if abs(u_c - tear_u) < tear_w * (1.0 - v_c / tear_h) and v_c < tear_h:
                    in_hole = True
                    break
            if in_hole:
                continue

            v00 = grid[iv][iu]
            v10 = grid[iv][iu + 1]
            v11 = grid[iv + 1][iu + 1]
            v01 = grid[iv + 1][iu]
            f = bm.faces.new((v00, v10, v11, v01))
            f.smooth = True
            for loop, (uu, vv) in zip(f.loops, (uv_coords[iv][iu], uv_coords[iv][iu + 1], uv_coords[iv + 1][iu + 1], uv_coords[iv + 1][iu])):
                loop[uv_layer].uv = (uu, vv)

    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0005)
    solidify_bmesh(bm, thickness=0.005)

    m_cape = bpy.data.meshes.new("Mantella_Corpo")
    bm.to_mesh(m_cape)
    bm.free()
    o_cape = bpy.data.objects.new("Mantella_Corpo", m_cape)
    scn.collection.objects.link(o_cape)
    o_cape.data.materials.append(mat_cape)

    # B) MANTELLINA SULLE SPALLE E BRACCIA SUPERIORI (copre le spalle e scende strappata sulle maniche beige)
    for side, sx in (("SX", 1.0), ("DX", -1.0)):
        bm_s = bmesh.new()
        nu_s, nv_s = 28, 16
        grid_s = [[None] * nu_s for _ in range(nv_s)]
        uv_s = bm_s.loops.layers.uv.verify()
        for iv in range(nv_s):
            vt = iv / float(nv_s - 1)  # 0 = bordo basso strappato sulla manica, 1 = collo/spalla alta
            for iu in range(nu_s):
                ut = iu / float(nu_s - 1)  # 0 = petto anteriore (-Y), 0.5 = esterno spalla (X), 1 = schiena (+Y)
                ang = (-0.82 + 1.64 * ut) * (math.pi * 0.5)  # centrato sull'esterno del braccio
                # Linea centrale lungo la spalla/braccio superiore
                c_arm = Vector((sx * (0.085 + 0.195 * (1.0 - vt)), 0.006, 1.385 - 0.195 * (1.0 - vt)))
                # Raggio avvolgente attorno alla spalla/manica
                r_x = 0.055 + 0.025 * (1.0 - vt)
                r_y = 0.072 + 0.042 * (1.0 - vt)
                tear = 0.022 * math.sin(ut * math.pi * 9.0 + sx) * (1.0 - vt)
                fold = 0.006 * math.cos(ut * math.pi * 7.0)
                px = c_arm.x + sx * (r_x + fold) * math.cos(ang * 0.7)
                py = c_arm.y + (r_y + fold) * math.sin(ang)
                pz = c_arm.z + tear + 0.018 * math.cos(ang) * vt
                grid_s[iv][iu] = bm_s.verts.new(Vector((px, py, pz)))

        for iv in range(nv_s - 1):
            for iu in range(nu_s - 1):
                f = bm_s.faces.new((grid_s[iv][iu], grid_s[iv][iu + 1], grid_s[iv + 1][iu + 1], grid_s[iv + 1][iu]))
                for loop in f.loops:
                    loop[uv_s].uv = (iu / float(nu_s - 1), 0.65 + 0.35 * (iv / float(nv_s - 1)))

        solidify_bmesh(bm_s, thickness=0.0045)
        m_s = bpy.data.meshes.new(f"Mantella_Spalla_{side}")
        bm_s.to_mesh(m_s)
        bm_s.free()
        o_s = bpy.data.objects.new(f"Mantella_Spalla_{side}", m_s)
        scn.collection.objects.link(o_s)
        o_s.data.materials.append(mat_cape)

    # C) ALTO COLLETTO STRUTTURATO DELLA MANTELLA (dietro e ai lati del collo, aperto a V davanti)
    bm_c = bmesh.new()
    nu_c, nv_c = 32, 10
    grid_c = [[None] * nu_c for _ in range(nv_c)]
    uv_c = bm_c.loops.layers.uv.verify()
    for iv in range(nv_c):
        vt = iv / float(nv_c - 1)  # 0 = base collo (Z=1.35), 1 = bordo alto colletto (Z=1.475)
        for iu in range(nu_c):
            ut = iu / float(nu_c - 1)
            # Angolo da -140° (petto ant DX) a +140° (petto ant SX) passando per 0° (+Y retro)
            ang = (ut - 0.5) * 2.0 * math.radians(142.0)
            front_taper = max(0.0, (abs(ut - 0.5) - 0.32) / 0.18)
            z = 1.355 + (0.115 * (1.0 - 0.45 * front_taper)) * vt
            rx = 0.088 + 0.022 * vt + 0.012 * front_taper
            ry = 0.082 + 0.020 * vt
            px = rx * math.sin(ang)
            py = 0.004 + ry * math.cos(ang)
            grid_c[iv][iu] = bm_c.verts.new(Vector((px, py, z)))

    for iv in range(nv_c - 1):
        for iu in range(nu_c - 1):
            f = bm_c.faces.new((grid_c[iv][iu], grid_c[iv][iu + 1], grid_c[iv + 1][iu + 1], grid_c[iv + 1][iu]))
            for loop in f.loops:
                loop[uv_c].uv = (iu / float(nu_c - 1), 0.8 + 0.2 * (iv / float(nv_c - 1)))

    solidify_bmesh(bm_c, thickness=0.005)
    m_c = bpy.data.meshes.new("Mantella_Colletto")
    bm_c.to_mesh(m_c)
    bm_c.free()
    o_c = bpy.data.objects.new("Mantella_Colletto", m_c)
    scn.collection.objects.link(o_c)
    o_c.data.materials.append(mat_cape)

build_torn_cape()

# ==============================================================================
# 3. CONCHIGLIE / CIRRIPEDI SULLA SPALLA SINISTRA (+X) DELLA MANTELLA
# ==============================================================================
shell_specs = [
    ((0.125, -0.078, 1.342), 0.018, (25, 15, -30)),
    ((0.152, -0.072, 1.335), 0.014, (30, 22, -10)),
    ((0.105, -0.082, 1.330), 0.012, (20, -10, -45)),
    ((0.140, -0.064, 1.352), 0.011, (15, 25, 10)),
]
for idx, (loc, rad, rot_d) in enumerate(shell_specs):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=rad)
    for v in bm.verts:
        # Forma a conchiglia nervata
        rib = 1.0 + 0.14 * math.sin(math.atan2(v.co.y, v.co.x) * 7.0)
        v.co.x *= 1.15 * rib
        v.co.y *= 0.95 * rib
        v.co.z *= 0.55
    for f in bm.faces:
        f.smooth = True
    m_sh = bpy.data.meshes.new(f"Conchiglia_{idx}")
    bm.to_mesh(m_sh)
    bm.free()
    o_sh = bpy.data.objects.new(f"Conchiglia_{idx}", m_sh)
    scn.collection.objects.link(o_sh)
    o_sh.location = loc
    o_sh.rotation_euler = tuple(math.radians(a) for a in rot_d)
    o_sh.data.materials.append(mat_shell)

# ==============================================================================
# 4. IMBRACATURA IN CUOIO SUL PETTO E CINTURE IN VITA CON FIBBIE E MEDAGLIONE
# ==============================================================================
def make_strap_curve(name, pts, width, thick, mat, closed=False):
    """Crea una cinghia piatta in cuoio lungo una lista di punti 3D attorno al busto."""
    bm = bmesh.new()
    rings = []
    n = len(pts)
    for i in range(n):
        p = Vector(pts[i])
        if closed:
            t = (Vector(pts[(i + 1) % n]) - Vector(pts[(i - 1) % n])).normalized()
        elif i == 0:
            t = (Vector(pts[1]) - p).normalized()
        elif i == n - 1:
            t = (p - Vector(pts[-2])).normalized()
        else:
            t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
        # Normale uscente dal busto (nel piano XY)
        out_n = Vector((p.x, p.y, 0.0)).normalized()
        if out_n.length < 0.001:
            out_n = Vector((0.0, -1.0, 0.0))
        binorm = t.cross(out_n).normalized()
        out_n = binorm.cross(t).normalized()
        # Sezione rettangolare smussata a 4 vertici
        hw, ht = width * 0.5, thick * 0.5
        r_verts = [
            bm.verts.new(p - binorm * hw - out_n * ht),
            bm.verts.new(p + binorm * hw - out_n * ht),
            bm.verts.new(p + binorm * hw + out_n * ht),
            bm.verts.new(p - binorm * hw + out_n * ht),
        ]
        rings.append(r_verts)

    limit = n if closed else n - 1
    for i in range(limit):
        inext = (i + 1) % n
        for j in range(4):
            jn = (j + 1) % 4
            f = bm.faces.new((rings[i][j], rings[i][jn], rings[inext][jn], rings[inext][j]))
            f.smooth = False

    if not closed:
        bm.faces.new((rings[0][3], rings[0][2], rings[0][1], rings[0][0]))
        bm.faces.new((rings[-1][0], rings[-1][1], rings[-1][2], rings[-1][3]))

    m = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(m)
    bm.free()
    o = bpy.data.objects.new(name, m)
    scn.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

def make_buckle(name, center, width, height, thick, rot_deg, mat):
    """Crea una fibbia rettangolare cava in ottone con ardiglione."""
    bm = bmesh.new()
    hw, hh, ht = width * 0.5, height * 0.5, thick * 0.5
    iw, ih = hw * 0.62, hh * 0.62
    # 8 vertici esterni e 8 interni
    outer = [bm.verts.new(Vector((sx * hw, sy * ht, sz * hh))) for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    inner = [bm.verts.new(Vector((sx * iw, sy * ht, sz * ih))) for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4):
        inext = (i + 1) % 4
        # Fronte, retro, esterno, interno
        bm.faces.new((outer[i], outer[inext], inner[inext], inner[i]))
        bm.faces.new((outer[4 + inext], outer[4 + i], inner[4 + i], inner[4 + inext]))
        bm.faces.new((outer[i], outer[4 + i], outer[4 + inext], outer[inext]))
        bm.faces.new((inner[inext], inner[4 + inext], inner[4 + i], inner[i]))
    m = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(m)
    bm.free()
    o = bpy.data.objects.new(name, m)
    scn.collection.objects.link(o)
    o.location = center
    o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    o.data.materials.append(mat)
    return o

# A) Cinghie diagonali incrociate sul petto (dalle spalle ai fianchi opposti)
diag1_pts = []
diag2_pts = []
for k in range(15):
    t = k / 14.0
    # Cinghia 1: da spalla SX (+X, Z=1.34) a fianco DX (-X, Z=1.04) passando sul petto (-Y)
    x1 = 0.115 * (1.0 - t) - 0.125 * t
    z1 = 1.345 * (1.0 - t) + 1.045 * t
    # Raggio Y sul petto anteriore
    y1 = -0.008 - (0.118 + 0.015 * math.sin(t * math.pi)) * math.sqrt(max(0.15, 1.0 - (x1 / 0.165) ** 2))
    diag1_pts.append((x1, y1, z1))

    # Cinghia 2: da spalla DX (-X, Z=1.34) a fianco SX (+X, Z=1.08)
    x2 = -0.115 * (1.0 - t) + 0.125 * t
    z2 = 1.345 * (1.0 - t) + 1.085 * t
    y2 = -0.012 - (0.120 + 0.015 * math.sin(t * math.pi)) * math.sqrt(max(0.15, 1.0 - (x2 / 0.165) ** 2))
    diag2_pts.append((x2, y2, z2))

make_strap_curve("Cinghia_Petto_Diag1", diag1_pts, 0.024, 0.007, mat_cuoio_scuro, closed=False)
make_strap_curve("Cinghia_Petto_Diag2", diag2_pts, 0.024, 0.007, mat_cuoio_medio, closed=False)

# Fibbie in ottone sulle cinghie pettorali
make_buckle("Fibbia_Petto_1", (0.045, -0.128, 1.255), 0.030, 0.026, 0.009, (8, -38, 12), mat_ottone)
make_buckle("Fibbia_Petto_2", (-0.048, -0.128, 1.245), 0.030, 0.026, 0.009, (8, 38, -12), mat_ottone)

# Cinghia orizzontale sotto il petto (Z=1.10) con fibbia centrale
chest_h_pts = []
for k in range(28):
    th = 2.0 * math.pi * k / 28.0
    chest_h_pts.append((0.144 * math.cos(th), -0.005 + 0.106 * math.sin(th), 1.102))
make_strap_curve("Cinghia_Petto_Orizz", chest_h_pts, 0.022, 0.007, mat_cuoio_scuro, closed=True)
make_buckle("Fibbia_Petto_Orizz", (0.0, -0.112, 1.102), 0.032, 0.028, 0.009, (0, 0, 0), mat_ottone)

# B) DOPPIA CINTURA IN VITA (Cintura principale orizzontale Z=1.00 + Cintura obliqua Z=1.00->0.93)
belt1_pts = []
belt2_pts = []
for k in range(32):
    th = 2.0 * math.pi * k / 32.0
    cx, sy = math.cos(th), math.sin(th)
    belt1_pts.append((0.138 * cx, 0.000 + 0.101 * sy, 1.005))
    # La seconda cintura scende obliqua verso il fianco sinistro (+X)
    z2 = 0.968 - 0.034 * cx
    rx2 = 0.146 + 0.010 * (1.0 - (z2 - 0.93) / 0.07)
    ry2 = 0.106 + 0.006 * (1.0 - (z2 - 0.93) / 0.07)
    belt2_pts.append((rx2 * cx, 0.001 + ry2 * sy, z2))

make_strap_curve("Cintura_Vita_Principale", belt1_pts, 0.040, 0.010, mat_cuoio_medio, closed=True)
make_strap_curve("Cintura_Vita_Obliqua", belt2_pts, 0.034, 0.009, mat_cuoio_scuro, closed=True)

# Fibbie delle cinture in vita
make_buckle("Fibbia_Vita_Principale", (0.000, -0.105, 1.005), 0.046, 0.048, 0.012, (0, 0, 0), mat_ottone)
make_buckle("Fibbia_Vita_Obliqua", (0.038, -0.104, 0.958), 0.038, 0.038, 0.011, (0, -14, -15), mat_ottone)

# C) MEDAGLIONE / BUSSOLA TONDA CHIARA APPESA ALLA CINTURA FRONTALE (X=-0.022, Z=0.945)
bm_med = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.021) if False else None
bmesh.ops.create_uvsphere(bm_med, u_segments=18, v_segments=10, radius=0.021)
for v in bm_med.verts:
    v.co.y *= 0.35
for f in bm_med.faces:
    f.smooth = True
m_med = bpy.data.meshes.new("Medaglione_Cintura")
bm_med.to_mesh(m_med)
bm_med.free()
o_med = bpy.data.objects.new("Medaglione_Cintura", m_med)
scn.collection.objects.link(o_med)
o_med.location = (-0.022, -0.110, 0.946)
o_med.data.materials.append(mat_shell)

# D) LEMBI DI STOFFA LOGORA CHIARA SUI FIANCHI SOTTO LA CINTURA (visibili davanti e di lato)
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    bm_t = bmesh.new()
    nu_t, nv_t = 8, 14
    grid_t = [[None] * nu_t for _ in range(nv_t)]
    for iv in range(nv_t):
        vt = iv / float(nv_t - 1)  # 0=punta bassa (Z=0.58), 1=cintura (Z=0.95)
        z = 0.58 + 0.37 * vt
        taper = 0.25 + 0.75 * vt
        for iu in range(nu_t):
            ut = (iu / float(nu_t - 1)) - 0.5
            ang = sx * math.radians(65.0) + ut * 0.42 * taper
            rx = 0.168 + 0.012 * (1.0 - vt) + 0.005 * math.sin(vt * 9.0 + ut * 6.0)
            ry = 0.112 + 0.010 * (1.0 - vt)
            px = rx * math.sin(ang)
            py = -0.015 - ry * abs(math.cos(ang)) * 0.65
            pz = z + 0.022 * math.sin(ut * math.pi * 3.0) * (1.0 - vt)
            grid_t[iv][iu] = bm_t.verts.new(Vector((px, py, pz)))
    for iv in range(nv_t - 1):
        for iu in range(nu_t - 1):
            bm_t.faces.new((grid_t[iv][iu], grid_t[iv][iu + 1], grid_t[iv + 1][iu + 1], grid_t[iv + 1][iu]))
    solidify_bmesh(bm_t, thickness=0.003)
    m_t = bpy.data.meshes.new(f"Lembo_Stoffa_{side}")
    bm_t.to_mesh(m_t)
    bm_t.free()
    o_t = bpy.data.objects.new(f"Lembo_Stoffa_{side}", m_t)
    scn.collection.objects.link(o_t)
    o_t.data.materials.append(mat_camicia)

tris = sum(len(o.data.polygons) for o in scn.objects if o.type == "MESH")
log(f"Passo 2 completato: Poligoni totali={tris}")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render_viste("passo2_mantella", viste=["fronte", "destra", "retro", "tre_quarti"])
