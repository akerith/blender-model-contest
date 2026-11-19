import bpy
import bmesh
import math
from mathutils import Vector, Matrix

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = LAVORO + r"\personaggio.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

def get_or_make_mat(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_tunic = get_or_make_mat("TunicaBluGrigia", (0.16, 0.22, 0.26), roughness=0.78)
mat_shirt = get_or_make_mat("CamiciaBeige", (0.64, 0.59, 0.50), roughness=0.82)
mat_pants = get_or_make_mat("PantaloniScuri", (0.20, 0.19, 0.17), roughness=0.80)
mat_leather = get_or_make_mat("PelleMarrone", (0.22, 0.14, 0.10), roughness=0.52)
mat_leather_dark = get_or_make_mat("PelleScura", (0.13, 0.09, 0.07), roughness=0.48)
mat_brass = get_or_make_mat("Ottone", (0.68, 0.52, 0.25), roughness=0.35, metallic=0.88)
mat_dial = get_or_make_mat("QuadranteVerde", (0.38, 0.55, 0.45), roughness=0.22)

def add_loft(bm, rings, cap_start=True, cap_end=True, mat_idx=0):
    n = len(rings[0])
    vert_rings = [[bm.verts.new(p) for p in ring] for ring in rings]
    faces = []
    for i in range(len(vert_rings) - 1):
        r0, r1 = vert_rings[i], vert_rings[i + 1]
        for j in range(n):
            jn = (j + 1) % n
            f = bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
            f.material_index = mat_idx
            faces.append(f)
    if cap_start:
        f = bm.faces.new(vert_rings[0][::-1])
        f.material_index = mat_idx
    if cap_end:
        f = bm.faces.new(vert_rings[-1])
        f.material_index = mat_idx
    return vert_rings

def make_ring(center, rx, ry, n=18, rot_x=0.0):
    pts = []
    cx, cy, cz = center
    ca, sa = math.cos(rot_x), math.sin(rot_x)
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        x = rx * math.cos(ang)
        y0 = ry * math.sin(ang)
        pts.append(Vector((cx + x, cy + y0 * ca, cz + y0 * sa)))
    return pts

def make_limb_rings(p0, p1, r_list, n=14):
    axis = (Vector(p1) - Vector(p0)).normalized()
    ref = Vector((0, -1, 0)) if abs(axis.y) < 0.9 else Vector((1, 0, 0))
    right = axis.cross(ref).normalized()
    fwd = right.cross(axis).normalized()
    rings = []
    for t, rx, ry in r_list:
        c = Vector(p0).lerp(Vector(p1), t)
        rings.append([c + right * (rx * math.cos(2 * math.pi * i / n)) + fwd * (ry * math.sin(2 * math.pi * i / n)) for i in range(n)])
    return rings

def new_mesh_obj(name, bm, mats, smooth=True):
    mesh = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    if smooth:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    return obj

# 1. Tunica / Giacca blu-grigia + Colletto camicia beige
bm_t = bmesh.new()
tunic_specs = [
    ((0, 0.01, 0.72), 0.185, 0.135),   # orlo inferiore tunica (sopra cosce)
    ((0, 0.008, 0.85), 0.165, 0.120),  # fianchi
    ((0, 0.002, 0.96), 0.145, 0.108),  # sotto cintura
    ((0, -0.005, 1.03), 0.122, 0.092), # vita stretta
    ((0, -0.015, 1.18), 0.144, 0.114), # torace
    ((0, 0.0, 1.32), 0.158, 0.104),    # spalle
    ((0, 0.005, 1.385), 0.068, 0.064), # base collo giacca
]
add_loft(bm_t, [make_ring(c, rx, ry, 20) for c, rx, ry in tunic_specs], mat_idx=0)

# Colletto interno camicia beige
collar_specs = [
    ((0, 0.005, 1.375), 0.058, 0.056),
    ((0, 0.005, 1.435), 0.054, 0.054),
]
add_loft(bm_t, [make_ring(c, rx, ry, 16) for c, rx, ry in collar_specs], mat_idx=1)

# Maniche beige arrotolate fino a metà avambraccio
for s in (1.0, -1.0):
    sleeve_rings = make_limb_rings(
        (0.15*s, 0.015, 1.335), (0.52*s, -0.02, 0.97),
        [(0.0, 0.056, 0.054), (0.25, 0.050, 0.048), (0.52, 0.046, 0.045),
         (0.62, 0.050, 0.049), (0.68, 0.046, 0.045), (0.70, 0.036, 0.035)],
        n=14
    )
    add_loft(bm_t, sleeve_rings, mat_idx=1)

new_mesh_obj("TunicaManiche", bm_t, [mat_tunic, mat_shirt])

# 2. Pantaloni scuri + fasce chiare sopra gli stivali
bm_p = bmesh.new()
for s in (1.0, -1.0):
    pant_rings = make_limb_rings(
        (0.095*s, 0.0, 0.90), (0.115*s, 0.02, 0.08),
        [(0.0, 0.080, 0.082), (0.25, 0.068, 0.070), (0.48, 0.054, 0.056), (0.64, 0.055, 0.057)],
        n=14
    )
    add_loft(bm_p, pant_rings, mat_idx=0)
    # Fasce chiare sopra lo stivale (t=0.60..0.68)
    wrap_rings = make_limb_rings(
        (0.095*s, 0.0, 0.90), (0.115*s, 0.02, 0.08),
        [(0.59, 0.058, 0.060), (0.65, 0.056, 0.058)],
        n=14
    )
    add_loft(bm_p, wrap_rings, mat_idx=1)

new_mesh_obj("Pantaloni", bm_p, [mat_pants, mat_shirt])

# 3. Stivali alti allacciati + suole + cinturini + Ginocchiera destra
bm_s = bmesh.new()
for s in (1.0, -1.0):
    # Gambale stivale (z=0.07..0.37)
    boot_rings = make_limb_rings(
        (0.115*s, 0.01, 0.37), (0.115*s, 0.02, 0.07),
        [(0.0, 0.062, 0.064), (0.12, 0.056, 0.058), (0.45, 0.050, 0.052), (0.85, 0.044, 0.046), (1.0, 0.046, 0.052)],
        n=14
    )
    add_loft(bm_s, boot_rings, mat_idx=0)
    # Risvolto superiore con fibbia
    cuff_rings = make_limb_rings(
        (0.115*s, 0.01, 0.375), (0.115*s, 0.012, 0.34),
        [(0.0, 0.066, 0.068), (1.0, 0.064, 0.066)],
        n=14
    )
    add_loft(bm_s, cuff_rings, mat_idx=1)
    # Piede dello stivale (tallone -> punta)
    foot_rings = [
        make_ring((0.115*s, 0.06, 0.045), 0.044, 0.045, 12, rot_x=math.radians(90)),
        make_ring((0.115*s, 0.00, 0.045), 0.046, 0.042, 12, rot_x=math.radians(90)),
        make_ring((0.115*s, -0.09, 0.036), 0.046, 0.034, 12, rot_x=math.radians(90)),
        make_ring((0.115*s, -0.16, 0.028), 0.036, 0.024, 12, rot_x=math.radians(90)),
        make_ring((0.115*s, -0.185, 0.022), 0.020, 0.015, 12, rot_x=math.radians(90)),
    ]
    add_loft(bm_s, foot_rings, mat_idx=0)
    # Suola spessa
    bmesh.ops.create_cube(bm_s, size=1.0,
                          matrix=Matrix.Translation((0.115*s, -0.055, 0.012)) @ Matrix.Diagonal((0.088, 0.24, 0.024, 1.0)))
    # Lacci frontali (piccole barrette orizzontali)
    for k in range(5):
        zk = 0.12 + k * 0.042
        bmesh.ops.create_cube(bm_s, size=1.0,
                              matrix=Matrix.Translation((0.115*s, -0.034, zk)) @ Matrix.Diagonal((0.032, 0.012, 0.007, 1.0)))

# Ginocchiera destra (-X)
bmesh.ops.create_uvsphere(bm_s, u_segments=12, v_segments=8, radius=0.050,
                          matrix=Matrix.Translation((-0.115, -0.036, 0.49)) @ Matrix.Diagonal((1.0, 0.55, 1.15, 1.0)))
for dz in (-0.022, 0.022):
    strap_r = [
        make_ring((-0.115, 0.0, 0.49 + dz), 0.058, 0.058, 14),
        make_ring((-0.115, 0.0, 0.478 + dz), 0.058, 0.058, 14),
    ]
    add_loft(bm_s, strap_r, mat_idx=1)

new_mesh_obj("StivaliGinocchiera", bm_s, [mat_leather, mat_leather_dark])

# 4. Guanti in pelle + Bussola da polso sinistra (+X)
bm_g = bmesh.new()
for s in (1.0, -1.0):
    # Risvolto guanto sull'avambraccio
    gauntlet_rings = make_limb_rings(
        (0.35*s, 0.01, 1.16), (0.52*s, -0.02, 0.97),
        [(0.42, 0.044, 0.042), (0.58, 0.040, 0.038), (0.98, 0.030, 0.028)],
        n=12
    )
    add_loft(bm_g, gauntlet_rings, mat_idx=0)
    # Mano guantata
    glove_hand = make_limb_rings(
        (0.52*s, -0.02, 0.97), (0.615*s, -0.038, 0.865),
        [(0.0, 0.030, 0.024), (0.35, 0.037, 0.018), (0.70, 0.032, 0.014), (1.0, 0.018, 0.009)],
        n=10
    )
    add_loft(bm_g, glove_hand, mat_idx=0)
    # Pollice guanto
    thumb_g = make_limb_rings(
        (0.54*s, -0.035, 0.945), (0.578*s, -0.068, 0.898),
        [(0.0, 0.013, 0.013), (0.6, 0.010, 0.010), (1.0, 0.007, 0.007)],
        n=8
    )
    add_loft(bm_g, thumb_g, mat_idx=0)

# Bussola / Strumento da polso sul braccio SINISTRO (+X)
compass_pos = Vector((0.46, -0.028, 1.035))
rot_arm = Matrix.Rotation(math.radians(-45), 4, 'Y')
bmesh.ops.create_cone(bm_g, cap_ends=True, cap_tris=False, segments=16,
                      radius1=0.032, radius2=0.030, depth=0.022,
                      matrix=Matrix.Translation(compass_pos + Vector((0.022, -0.01, 0.022))) @ rot_arm)
# Quadrante interno verde-chiaro (assegniamo mat 2 alle facce più esterne)
bmesh.ops.create_cone(bm_g, cap_ends=True, cap_tris=False, segments=16,
                      radius1=0.024, radius2=0.024, depth=0.006,
                      matrix=Matrix.Translation(compass_pos + Vector((0.030, -0.012, 0.030))) @ rot_arm)

obj_g = new_mesh_obj("GuantiBussola", bm_g, [mat_leather, mat_brass, mat_dial])
for poly in obj_g.data.polygons:
    if poly.center.x > 0.45 and poly.center.z > 1.02:
        if (poly.center - (compass_pos + Vector((0.030, -0.012, 0.030)))).length < 0.026:
            poly.material_index = 2
        else:
            poly.material_index = 1

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 02 in", blend_path)
render_viste("02_abiti", viste=["fronte", "destra", "retro", "tre_quarti"])
