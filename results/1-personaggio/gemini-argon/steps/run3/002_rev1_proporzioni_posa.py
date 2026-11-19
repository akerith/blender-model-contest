import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 1 - Body proportions and pose (rev_1)
# Separates the joined round-1 character into its constituent logical mesh parts
# (preserving 100% of existing geometry, materials, and UVs) and reshapes/moves
# every body part to match all Group 1 specifications (1.1 - 1.6).
# ==============================================================================

scn = bpy.context.scene
main_obj = bpy.data.objects.get("Personaggio")

# Remove Armature modifier temporarily while reshaping geometry in rest pose
if main_obj:
    for mod in list(main_obj.modifiers):
        if mod.type == 'ARMATURE':
            main_obj.modifiers.remove(mod)
    main_obj.parent = None

# 1. Separate "Personaggio" into loose connected islands and classify each island
def classify_island(faces, mats):
    verts = {v for f in faces for v in f.verts}
    n_v = len(verts)
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]
    cx = sum(xs) / n_v
    cy = sum(ys) / n_v
    cz = sum(zs) / n_v
    z_min, z_max = min(zs), max(zs)
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    mat_idx = faces[0].material_index
    mname = mats[mat_idx].name if (0 <= mat_idx < len(mats) and mats[mat_idx]) else ""

    if mname == "Mat_Pelle":
        if cz > 1.50 and abs(cx) < 0.03:
            return "Testa"
        elif cz > 1.50:
            return "Orecchie"
        else:
            return "Collo"
    elif mname == "Mat_Labbra":
        return "Labbra"
    elif mname in ("Mat_OcchioBianco", "Mat_Iride", "Mat_Pupilla"):
        return "Occhi"
    elif mname == "Mat_CapelliScuri":
        if z_max < 1.595 and cy < -0.065:
            return "Sopracciglia"
        return "Capelli_Scuri"
    elif mname == "Mat_CapelliBianchi":
        return "Ciocca_Bianca"
    elif mname == "Mat_GiaccaBlu":
        return "Giacca_Torso"
    elif mname == "Mat_Pantaloni":
        if abs(cx) < 0.04:
            return "Bacino_Pantaloni"
        return "Pantalone_SX" if cx > 0 else "Pantalone_DX"
    elif mname == "Mat_Camicia":
        if cz > 1.30 and abs(cx) < 0.10:
            return "Camicia_Colletto"
        elif cz > 1.05:
            return "Manica_SX" if cx > 0 else "Manica_DX"
        elif cz > 0.55:
            return "Lembo_Stoffa_SX" if cx > 0 else "Lembo_Stoffa_DX"
        else:
            return "Fascia_Gamba_SX" if cx > 0 else "Fascia_Gamba_DX"
    elif mname == "Mat_MantellaVerde":
        if z_min < 0.65:
            return "Mantella_Corpo"
        elif z_min > 1.32 and abs(cx) < 0.05:
            return "Mantella_Colletto"
        else:
            return "Mantella_Spalla_SX" if cx > 0 else "Mantella_Spalla_DX"
    elif mname == "Mat_Conchiglia":
        return "Conchiglie_SX" if cz > 1.15 else "Medaglione_Cintura"
    elif mname == "Mat_Corda":
        return "Corda_Fianco_DX"
    elif mname == "Mat_Pergamena":
        return "Astuccio_SX"
    elif mname == "Mat_QuadranteVerde":
        return "Strumento_Polso_SX"
    elif mname == "Mat_VetroOblo":
        return "Casco_Palombaro"
    elif mname == "Mat_MetalloScuro":
        return "Stivale_SX" if cx > 0 else "Stivale_DX"
    elif mname == "Mat_Ottone":
        if cx > 0.30:
            return "Strumento_Polso_SX"
        elif cz < 0.98 and cx > 0.10:
            return "Astuccio_SX"
        elif cy > 0.08:
            if z_max < 1.245 and abs(cx) > 0.08:
                return "Tubi_Casco"
            return "Casco_Palombaro"
        elif cz > 1.05:
            return "Fibbie_Petto"
        else:
            return "Fibbie_Vita"
    else:
        # Leather materials: Mat_CuoioScuro, Mat_CuoioMedio, Mat_CuoioChiaro
        if abs(cx) > 0.32 and cz > 0.80:
            side = "SX" if cx > 0 else "DX"
            if z_max < 0.985:
                return f"Mano_{side}"
            elif (z_max - z_min) < 0.06:
                return f"Cinturini_Guanto_{side}"
            else:
                return f"Guanto_{side}"
        elif cz < 0.45:
            side = "SX" if cx > 0 else "DX"
            if mname == "Mat_CuoioChiaro":
                return f"Lacci_Stivale_{side}"
            return f"Stivale_{side}"
        elif 0.45 <= cz < 0.65 and cx < -0.05:
            return "Ginocchiera_DX"
        elif cy > 0.11:
            return "Sacca_Arrotolata"
        elif 0.65 <= cz < 1.02 and cx < -0.11:
            return "Borraccia_DX"
        elif 0.55 <= cz < 0.98 and cx > 0.13:
            return "Astuccio_SX"
        elif cz >= 1.03:
            return "Cinghie_Petto"
        else:
            return "Cinture_Vita"


if main_obj:
    bm = bmesh.new()
    bm.from_mesh(main_obj.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    mats = list(main_obj.data.materials)

    visited = set()
    groups = {}
    for f in bm.faces:
        if f.index in visited:
            continue
        comp = []
        queue = [f]
        visited.add(f.index)
        while queue:
            curr = queue.pop()
            comp.append(curr)
            for v in curr.verts:
                for lf in v.link_faces:
                    if lf.index not in visited:
                        visited.add(lf.index)
                        queue.append(lf)
        gname = classify_island(comp, mats)
        groups.setdefault(gname, []).extend(comp)

    uv_lay = bm.loops.layers.uv.active

    for gname, f_list in groups.items():
        nbm = bmesh.new()
        uv_new = nbm.loops.layers.uv.new("UVMap")
        v_map = {}
        used_mats = []
        mat_remap = {}
        for f in f_list:
            m_orig = mats[f.material_index] if (0 <= f.material_index < len(mats)) else None
            if m_orig not in mat_remap:
                mat_remap[m_orig] = len(used_mats)
                used_mats.append(m_orig)
            n_verts = []
            for v in f.verts:
                if v.index not in v_map:
                    nv = nbm.verts.new(v.co)
                    v_map[v.index] = nv
                n_verts.append(v_map[v.index])
            try:
                nf = nbm.faces.new(n_verts)
            except ValueError:
                continue
            nf.smooth = f.smooth
            nf.material_index = mat_remap[m_orig]
            if uv_lay:
                for l_old, l_new in zip(f.loops, nf.loops):
                    l_new[uv_new].uv = l_old[uv_lay].uv

        nmesh = bpy.data.meshes.new(gname)
        nbm.normal_update()
        nbm.to_mesh(nmesh)
        nbm.free()
        for m_item in used_mats:
            nmesh.materials.append(m_item)
        nobj = bpy.data.objects.new(gname, nmesh)
        scn.collection.objects.link(nobj)

    bm.free()
    old_mesh = main_obj.data
    bpy.data.objects.remove(main_obj, do_unlink=True)
    bpy.data.meshes.remove(old_mesh)

log(f"Separati {len([o for o in scn.objects if o.type=='MESH'])} oggetti logici dalla mesh Personaggio.")

# ==============================================================================
# 2. PIECEWISE COORDINATE RESHAPING FOR GROUP 1 PROPORTIONS & A-POSE
# ==============================================================================

def lerp_table(val, table):
    if val <= table[0][0]:
        return table[0][1]
    if val >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= val <= x1:
            t = (val - x0) / max(1e-8, x1 - x0)
            return y0 + t * (y1 - y0)
    return table[-1][1]

# A) HEAD, FACE AND HAIR (1.1, 1.2, 1.3):
#    - chin: 1.464 -> 1.475
#    - eyes: 1.562 -> 1.585
#    - top of skull: 1.656 -> 1.660
#    - top of hair: 1.700 -> 1.700
#    - head width: 0.144 -> 0.150 (scale X = 0.150 / 0.144 = 1.0417)
#    - head depth: 0.168 -> 0.190 (scale Y = 0.190 / 0.168 = 1.1310)
#    - center Y aligned so ear is at Y = 0.0 (1.5)
head_z_table = [
    (1.350, 1.420),
    (1.464, 1.475),  # chin
    (1.521, 1.505),  # mouth
    (1.562, 1.585),  # eyes
    (1.656, 1.660),  # top of skull
    (1.700, 1.700),  # top of hair
]

head_objs = ["Testa", "Occhi", "Sopracciglia", "Labbra", "Orecchie"]
for oname in head_objs:
    obj = bpy.data.objects.get(oname)
    if not obj:
        continue
    for v in obj.data.vertices:
        z_new = lerp_table(v.co.z, head_z_table)
        x_new = v.co.x * (0.150 / 0.144)
        y_new = (v.co.y + 0.006) * (0.190 / 0.168)
        v.co = Vector((x_new, y_new, z_new))
    obj.data.update()

# Ensure Testa has exact bounding box: Z=[1.475, 1.660], X=[-0.075, +0.075] (width 0.15), Y=[-0.095, +0.095] (depth 0.19)
testa_obj = bpy.data.objects.get("Testa")
if testa_obj:
    vs = testa_obj.data.vertices
    xs = [v.co.x for v in vs]
    ys = [v.co.y for v in vs]
    zs = [v.co.z for v in vs]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    zmin, zmax = min(zs), max(zs)
    for v in vs:
        tx = (v.co.x - xmin) / max(1e-6, xmax - xmin)
        ty = (v.co.y - ymin) / max(1e-6, ymax - ymin)
        tz = (v.co.z - zmin) / max(1e-6, zmax - zmin)
        v.co.x = -0.075 + tx * 0.150
        v.co.y = -0.095 + ty * 0.190
        v.co.z = 1.475 + tz * (1.660 - 1.475)
    testa_obj.data.update()

for oname in ["Capelli_Scuri", "Ciocca_Bianca"]:
    obj = bpy.data.objects.get(oname)
    if not obj:
        continue
    for v in obj.data.vertices:
        z_new = lerp_table(v.co.z, head_z_table)
        x_new = v.co.x * (0.190 / 0.184)
        y_new = (v.co.y + 0.004) * (0.215 / 0.195)
        v.co = Vector((x_new, y_new, z_new))
    obj.data.update()

# Normalize max Z of hair to exactly 1.700 m
hair_all_v = [v for n in ("Capelli_Scuri", "Ciocca_Bianca") if bpy.data.objects.get(n) for v in bpy.data.objects[n].data.vertices]
if hair_all_v:
    h_zmax = max(v.co.z for v in hair_all_v)
    h_zmin = min(v.co.z for v in hair_all_v)
    for v in hair_all_v:
        if v.co.z > 1.58:
            v.co.z = 1.58 + (v.co.z - 1.58) * ((1.700 - 1.58) / max(1e-6, h_zmax - 1.58))
    for n in ("Capelli_Scuri", "Ciocca_Bianca"):
        if bpy.data.objects.get(n):
            bpy.data.objects[n].data.update()

# B) NECK AND COLLARS (1.2, 1.3):
#    - Neck: cylinder 0.11 wide (rx=0.055), from Z 1.45 to 1.49
collo_obj = bpy.data.objects.get("Collo")
if collo_obj:
    vs = collo_obj.data.vertices
    zmin = min(v.co.z for v in vs)
    zmax = max(v.co.z for v in vs)
    for v in vs:
        tz = (v.co.z - zmin) / max(1e-6, zmax - zmin)
        ang = math.atan2(v.co.y, v.co.x)
        r_curr = math.hypot(v.co.x, v.co.y)
        if r_curr > 0.01:
            v.co.x = 0.055 * math.cos(ang)
            v.co.y = 0.055 * math.sin(ang)
        else:
            v.co.x = 0.0
            v.co.y = 0.0
        v.co.z = 1.445 + tz * (1.495 - 1.445)
    collo_obj.data.update()

# C) TORSO, JACKET, STRAPS, BELTS (1.2, 1.3, 1.5):
#    - base of neck / top of collar: 1.45
#    - shoulder joints: 1.40, full width 0.40 (rx = 0.20)
#    - chest fullest: 1.27, width 0.32 (rx = 0.16), depth 0.21 (ry = 0.105), slightly forward (y_c = -0.010)
#    - waist: 1.08, width 0.27 (rx = 0.135), depth 0.18 (ry = 0.090), y_c = 0.000
#    - hips: 0.90, width 0.34 (rx = 0.170), depth 0.22 (ry = 0.110), bottom slightly back (y_c = +0.010)
#    - crotch: 0.86; skirt bottom: 0.80
torso_z_map = [
    (0.780, 0.790),
    (0.830, 0.800),
    (0.850, 0.860),
    (0.880, 0.900),
    (0.940, 0.980),
    (1.005, 1.080),
    (1.102, 1.200),
    (1.200, 1.270),
    (1.320, 1.380),
    (1.350, 1.400),
    (1.395, 1.430),
    (1.440, 1.460),
]

# Target half-widths rx(z), half-depths ry(z), and y_offset(z) vs old rx_old(z), ry_old(z)
torso_rx_scale = [
    (0.80, 0.190 / 0.172),  # tunic skirt 0.38 wide
    (0.90, 0.170 / 0.165),  # hips 0.34 wide
    (1.08, 0.135 / 0.130),  # waist 0.27 wide
    (1.27, 0.160 / 0.156),  # chest 0.32 wide
    (1.38, 0.200 / 0.172),  # shoulders 0.40 wide
    (1.43, 0.065 / 0.072),  # collar base
]
torso_ry_scale = [
    (0.80, 0.115 / 0.118),
    (0.90, 0.110 / 0.112),  # hips 0.22 deep
    (1.08, 0.090 / 0.094),  # waist 0.18 deep
    (1.27, 0.105 / 0.125),  # chest 0.21 deep
    (1.40, 0.095 / 0.088),
]
torso_y_shift = [
    (0.80, +0.008),
    (0.90, +0.008),  # bottom a little back
    (1.08,  0.000),  # waist on vertical line Y=0
    (1.27, -0.008),  # chest a little forward
    (1.40,  0.000),  # shoulder on vertical line Y=0
    (1.46,  0.000),
]

torso_group_objs = [
    "Giacca_Torso", "Bacino_Pantaloni", "Camicia_Colletto", "Mantella_Colletto",
    "Cinghie_Petto", "Fibbie_Petto", "Cinture_Vita", "Fibbie_Vita", "Medaglione_Cintura",
    "Conchiglie_SX"
]
for oname in torso_group_objs:
    obj = bpy.data.objects.get(oname)
    if not obj:
        continue
    for v in obj.data.vertices:
        z_new = lerp_table(v.co.z, torso_z_map)
        sx_s = lerp_table(z_new, torso_rx_scale)
        sy_s = lerp_table(z_new, torso_ry_scale)
        dy_s = lerp_table(z_new, torso_y_shift)
        v.co.x = v.co.x * sx_s
        v.co.y = v.co.y * sy_s + dy_s
        v.co.z = z_new
    obj.data.update()

# D) ARMS, SLEEVES, GAUNTLETS, WRIST INSTRUMENT, HANDS (1.4):
#    - Left shoulder joint: (+0.19, 0.0, 1.40)
#    - Left elbow:          (+0.38, 0.0, 1.18) (length 0.2907 m, angle 49.2 deg below horizontal)
#    - Left wrist:          (+0.54, 0.0, 0.99) (length 0.2484 m, ~10 deg elbow bend)
#    - Left middle tip:     (+0.66, 0.0, 0.86) (length 0.1769 m)
#    - Seen from side: shoulder, elbow, wrist and fingertips all at Y = 0.0
def transform_arm_vertex(co, sx):
    ux = abs(co.x)
    # Old piecewise centerline points (X>0 side)
    p0_old = Vector((0.165, 0.008, 1.340))
    p1_old = Vector((0.355, 0.012, 1.150))
    p2_old = Vector((0.488, -0.014, 1.002))
    p3_old = Vector((0.588, -0.035, 0.873))

    # New piecewise centerline points (X>0 side)
    p0_new = Vector((0.190, 0.000, 1.400))
    p1_new = Vector((0.380, 0.000, 1.180))
    p2_new = Vector((0.540, 0.000, 0.990))
    p3_new = Vector((0.660, 0.000, 0.860))

    if ux <= p1_old.x:
        t = (ux - p0_old.x) / max(1e-6, p1_old.x - p0_old.x)
        c_old = p0_old.lerp(p1_old, t)
        c_new = p0_new.lerp(p1_new, t)
    elif ux <= p2_old.x:
        t = (ux - p1_old.x) / max(1e-6, p2_old.x - p1_old.x)
        c_old = p1_old.lerp(p2_old, t)
        c_new = p1_new.lerp(p2_new, t)
    else:
        t = (ux - p2_old.x) / max(1e-6, p3_old.x - p2_old.x)
        c_old = p2_old.lerp(p3_old, t)
        c_new = p2_new.lerp(p3_new, t)

    new_x = sx * c_new.x
    new_y = c_new.y + (co.y - c_old.y)
    new_z = c_new.z + (co.z - c_old.z)
    return Vector((new_x, new_y, new_z))

for side, sx in (("SX", 1.0), ("DX", -1.0)):
    arm_objs = [
        f"Manica_{side}",
        f"Guanto_{side}",
        f"Cinturini_Guanto_{side}",
        f"Mano_{side}",
    ]
    if side == "SX":
        arm_objs.append("Strumento_Polso_SX")
    for oname in arm_objs:
        obj = bpy.data.objects.get(oname)
        if not obj:
            continue
        for v in obj.data.vertices:
            v.co = transform_arm_vertex(v.co, sx)
        obj.data.update()

# E) LEGS AND BOOTS (1.2, 1.3, 1.5):
#    - hip joints: Z 0.90; crotch: Z 0.86
#    - knee joints: Z 0.49
#    - ankle joints: Z 0.08
#    - sole: Z 0.00
#    - boot centres at X = -0.13 (right) and X = +0.13 (left), pointing straight forward (-Y)
#    - upside-down narrow V from hips (X=+-0.10 at Z=0.90) to knees (X=+-0.115 at Z=0.49) to ankles/boots (X=+-0.13 at Z<=0.08)
leg_z_map = [
    (0.000, 0.000),
    (0.090, 0.080),  # ankle
    (0.400, 0.420),  # boot top
    (0.480, 0.490),  # knee
    (0.840, 0.900),  # hip joint
]
leg_cx_old = [
    (0.000, 0.114),
    (0.090, 0.114),
    (0.400, 0.110),
    (0.480, 0.106),
    (0.840, 0.088),
]
leg_cy_old = [
    (0.000, 0.000),
    (0.090, -0.002),
    (0.480, -0.010),
    (0.840, 0.006),
]
leg_cx_new = [
    (0.000, 0.130),
    (0.080, 0.130),
    (0.490, 0.115),
    (0.900, 0.100),
]

for side, sx in (("SX", 1.0), ("DX", -1.0)):
    leg_objs = [
        f"Pantalone_{side}",
        f"Fascia_Gamba_{side}",
        f"Stivale_{side}",
        f"Lacci_Stivale_{side}",
    ]
    if side == "DX":
        leg_objs.append("Ginocchiera_DX")
    for oname in leg_objs:
        obj = bpy.data.objects.get(oname)
        if not obj:
            continue
        for v in obj.data.vertices:
            co = v.co.copy()
            # Un-rotate the 10-degree outward foot yaw from Round 1 below Z=0.11
            if co.z < 0.11:
                w_yaw = 1.0 if co.z <= 0.075 else (0.11 - co.z) / 0.035
                ang = -sx * math.radians(10.0) * w_yaw
                ca, sa = math.cos(ang), math.sin(ang)
                lx = co.x - sx * 0.114
                ly = co.y
                co.x = sx * 0.114 + (lx * ca - ly * sa)
                co.y = lx * sa + ly * ca

            z_old = co.z
            z_new = lerp_table(z_old, leg_z_map)
            cx_o = sx * lerp_table(z_old, leg_cx_old)
            cy_o = lerp_table(z_old, leg_cy_old)
            cx_n = sx * lerp_table(z_new, leg_cx_new)
            cy_n = 0.0
            v.co.x = cx_n + (co.x - cx_o)
            v.co.y = cy_n + (co.y - cy_o)
            v.co.z = z_new
        obj.data.update()

# Ensure boot soles sit cleanly at Z = 0.000
for side in ("SX", "DX"):
    st = bpy.data.objects.get(f"Stivale_{side}")
    if st:
        zmin_s = min(v.co.z for v in st.data.vertices)
        for v in st.data.vertices:
            if v.co.z < 0.05:
                v.co.z = max(0.0, v.co.z - zmin_s)
        st.data.update()

# F) CAPE, WAIST GEAR AND BACK GEAR (shift with shoulders & waist so nothing intersects or floats)
for side, sx in (("SX", 1.0), ("DX", -1.0)):
    sp = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if sp:
        for v in sp.data.vertices:
            v.co.z += 0.055
            v.co.x *= 1.08
        sp.data.update()

cape_body = bpy.data.objects.get("Mantella_Corpo")
if cape_body:
    for v in cape_body.data.vertices:
        # Lift shoulder top from 1.375 to 1.41, keep bottom around 0.20..0.25
        t_z = max(0.0, min(1.0, (v.co.z - 0.22) / (1.375 - 0.22)))
        v.co.z += 0.045 * t_z
        # Widen slightly around hips/arms
        v.co.x *= (1.04 + 0.06 * (1.0 - t_z))
    cape_body.data.update()

# Lift waist gear by +0.055 in Z and +0.015 outward in X to sit on new hip belt
for oname in ["Corda_Fianco_DX", "Borraccia_DX", "Astuccio_SX", "Lembo_Stoffa_SX", "Lembo_Stoffa_DX"]:
    obj = bpy.data.objects.get(oname)
    if obj:
        for v in obj.data.vertices:
            v.co.z += 0.045
            v.co.x += math.copysign(0.015, v.co.x)
        obj.data.update()

# Lift back helmet and bedroll by +0.045 in Z to match new upper back (center Z=1.30)
for oname in ["Casco_Palombaro", "Tubi_Casco", "Sacca_Arrotolata"]:
    obj = bpy.data.objects.get(oname)
    if obj:
        for v in obj.data.vertices:
            v.co.z += 0.045
            v.co.y += 0.025
        obj.data.update()

# ==============================================================================
# 3. UPDATE ARMATURE BONES TO EXACT GROUP 1 & 10.5 JOINT POSITIONS
# ==============================================================================
arm_obj = bpy.data.objects.get("Armature")
if arm_obj and arm_obj.type == 'ARMATURE':
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    ebones = arm_obj.data.edit_bones
    for b in list(ebones):
        ebones.remove(b)

    bone_specs = [
        ("Hips",       None,         False, (0.000, 0.000, 0.950), (0.000, 0.000, 1.100)),
        ("Spine",      "Hips",       True,  (0.000, 0.000, 1.100), (0.000, 0.000, 1.270)),
        ("Chest",      "Spine",      True,  (0.000, 0.000, 1.270), (0.000, 0.000, 1.450)),
        ("Neck",       "Chest",      True,  (0.000, 0.000, 1.450), (0.000, 0.000, 1.500)),
        ("Head",       "Neck",       True,  (0.000, 0.000, 1.500), (0.000, 0.000, 1.700)),

        ("Shoulder.L", "Chest",      False, (0.040, 0.000, 1.430), (0.190, 0.000, 1.400)),
        ("UpperArm.L", "Shoulder.L", True,  (0.190, 0.000, 1.400), (0.380, 0.000, 1.180)),
        ("LowerArm.L", "UpperArm.L", True,  (0.380, 0.000, 1.180), (0.540, 0.000, 0.990)),
        ("Hand.L",     "LowerArm.L", True,  (0.540, 0.000, 0.990), (0.605, 0.000, 0.920)),

        ("Shoulder.R", "Chest",      False, (-0.040, 0.000, 1.430), (-0.190, 0.000, 1.400)),
        ("UpperArm.R", "Shoulder.R", True,  (-0.190, 0.000, 1.400), (-0.380, 0.000, 1.180)),
        ("LowerArm.R", "UpperArm.R", True,  (-0.380, 0.000, 1.180), (-0.540, 0.000, 0.990)),
        ("Hand.R",     "LowerArm.R", True,  (-0.540, 0.000, 0.990), (-0.605, 0.000, 0.920)),

        ("UpperLeg.L", "Hips",       False, (0.100, 0.000, 0.900), (0.115, 0.000, 0.490)),
        ("LowerLeg.L", "UpperLeg.L", True,  (0.115, 0.000, 0.490), (0.130, 0.000, 0.080)),
        ("Foot.L",     "LowerLeg.L", True,  (0.130, 0.000, 0.080), (0.130, -0.100, 0.030)),
        ("Toes.L",     "Foot.L",     True,  (0.130, -0.100, 0.030), (0.130, -0.190, 0.015)),

        ("UpperLeg.R", "Hips",       False, (-0.100, 0.000, 0.900), (-0.115, 0.000, 0.490)),
        ("LowerLeg.R", "UpperLeg.R", True,  (-0.115, 0.000, 0.490), (-0.130, 0.000, 0.080)),
        ("Foot.R",     "LowerLeg.R", True,  (-0.130, 0.000, 0.080), (-0.130, -0.100, 0.030)),
        ("Toes.R",     "Foot.R",     True,  (-0.130, -0.100, 0.030), (-0.130, -0.190, 0.015)),
    ]
    created = {}
    for bname, pname, conn, h_co, t_co in bone_specs:
        b = ebones.new(bname)
        b.head = Vector(h_co)
        b.tail = Vector(t_co)
        if pname and pname in created:
            b.parent = created[pname]
            b.use_connect = conn
        created[bname] = b
    bpy.ops.object.mode_set(mode='OBJECT')

# ==============================================================================
# 4. VERIFY MEASUREMENTS IN LOG AND RENDER rev_1
# ==============================================================================
all_mesh_verts = [o.matrix_world @ v.co for o in scn.objects if o.type == 'MESH' for v in o.data.vertices]
z_min_all = min(p.z for p in all_mesh_verts)
z_max_all = max(p.z for p in all_mesh_verts)
t_v = bpy.data.objects["Testa"].data.vertices
m_v = bpy.data.objects["Mano_SX"].data.vertices
tip_v = max(m_v, key=lambda v: v.co.x)

log(f"=== VERIFICA MISURE GROUP 1 ===")
log(f"Altezza totale: Z_min={z_min_all:.4f}m, Z_max={z_max_all:.4f}m (target 0.000..1.700m)")
log(f"Testa (cranio senza capelli): Z_min(mento)={min(v.co.z for v in t_v):.4f}m (target 1.475), Z_max(cranio)={max(v.co.z for v in t_v):.4f}m (target 1.660)")
log(f"Testa larghezza X={max(v.co.x for v in t_v)-min(v.co.x for v in t_v):.4f}m (target 0.150), profondita Y={max(v.co.y for v in t_v)-min(v.co.y for v in t_v):.4f}m (target 0.190)")
log(f"Punta dito medio SX: X={tip_v.co.x:.4f}, Y={tip_v.co.y:.4f}, Z={tip_v.co.z:.4f} (target X=0.66, Y=0.00, Z=0.86)")

bpy.ops.wm.save_mainfile()
render_viste("rev_1")
