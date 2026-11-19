import bpy
import bmesh
import math
from mathutils import Vector, Matrix

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"

# 1. Pulizia completa della scena
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.images):
    for item in list(block):
        if item.users == 0:
            block.remove(item)

# Mondo neutro chiaro per vedere bene dettagli e ombre
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.28, 0.30, 0.33, 1.0)
    bg.inputs[1].default_value = 0.8

# Luci di studio (Key, Fill, Rim)
def add_light(name, ltype, loc, rot, energy, color=(1, 1, 1), size=2.0):
    bpy.ops.object.light_add(type=ltype, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = rot
    ob.data.energy = energy
    ob.data.color = color
    if ltype == 'AREA':
        ob.data.size = size
    return ob

add_light("KeyLight", 'SUN', (2.5, -3.0, 4.0), (math.radians(50), math.radians(15), math.radians(35)), 2.8, (1.0, 0.97, 0.92))
add_light("FillLight", 'AREA', (-2.5, -2.5, 1.8), (math.radians(75), 0, math.radians(-45)), 80.0, (0.85, 0.92, 1.0), size=2.5)
add_light("RimLight", 'AREA', (0.5, 2.8, 2.2), (math.radians(115), 0, math.radians(170)), 110.0, (0.95, 0.98, 1.0), size=2.0)

# Helper materiali
def make_mat(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_skin = make_mat("Pelle", (0.76, 0.56, 0.45), roughness=0.55)
mat_hair = make_mat("CapelliScuri", (0.09, 0.075, 0.065), roughness=0.65)
mat_hair_white = make_mat("CapelliBianchi", (0.84, 0.83, 0.80), roughness=0.55)
mat_eye_white = make_mat("OcchioBianco", (0.92, 0.92, 0.90), roughness=0.2)
mat_iris = make_mat("OcchioIride", (0.18, 0.24, 0.19), roughness=0.15)
mat_lips = make_mat("Labbra", (0.58, 0.32, 0.28), roughness=0.45)

# 2. Creazione Armatura (1.70 m, posa A, pronta per Unity)
arm_data = bpy.data.armatures.new("ArmaturaData")
arm_obj = bpy.data.objects.new("Armatura", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

def add_bone(name, head, tail, parent=None, connect=False, roll=0.0):
    b = arm_data.edit_bones.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    b.roll = roll
    if parent:
        b.parent = arm_data.edit_bones[parent]
        b.use_connect = connect
    return b

add_bone("Pelvis", (0, 0, 0.88), (0, 0, 0.97))
add_bone("Spine", (0, 0, 0.97), (0, -0.01, 1.15), "Pelvis", True)
add_bone("Chest", (0, -0.01, 1.15), (0, 0.0, 1.38), "Spine", True)
add_bone("Neck", (0, 0.0, 1.38), (0, 0.005, 1.47), "Chest", True)
add_bone("Head", (0, 0.005, 1.47), (0, 0.005, 1.68), "Neck", True)

for side, s in (("L", 1.0), ("R", -1.0)):
    add_bone(f"Shoulder_{side}", (0.04*s, 0.01, 1.35), (0.155*s, 0.015, 1.36), "Chest", False)
    add_bone(f"UpperArm_{side}", (0.155*s, 0.015, 1.36), (0.35*s, 0.01, 1.16), f"Shoulder_{side}", True)
    add_bone(f"Forearm_{side}", (0.35*s, 0.01, 1.16), (0.52*s, -0.02, 0.97), f"UpperArm_{side}", True)
    add_bone(f"Hand_{side}", (0.52*s, -0.02, 0.97), (0.60*s, -0.035, 0.88), f"Forearm_{side}", True)

    add_bone(f"Thigh_{side}", (0.095*s, 0.0, 0.88), (0.115*s, -0.01, 0.48), "Pelvis", False)
    add_bone(f"Shin_{side}", (0.115*s, -0.01, 0.48), (0.115*s, 0.02, 0.08), f"Thigh_{side}", True)
    add_bone(f"Foot_{side}", (0.115*s, 0.02, 0.08), (0.115*s, -0.09, 0.02), f"Shin_{side}", True)
    add_bone(f"Toe_{side}", (0.115*s, -0.09, 0.02), (0.115*s, -0.17, 0.01), f"Foot_{side}", True)

bpy.ops.object.mode_set(mode='OBJECT')
arm_obj.show_in_front = True

# Helper per creare tubi/forme loftate con bmesh
def add_loft(bm, rings, cap_start=True, cap_end=True):
    # rings: lista di liste di Vector (tutte della stessa lunghezza)
    n = len(rings[0])
    vert_rings = []
    for ring in rings:
        v_ring = [bm.verts.new(p) for p in ring]
        vert_rings.append(v_ring)
    for i in range(len(vert_rings) - 1):
        r0, r1 = vert_rings[i], vert_rings[i + 1]
        for j in range(n):
            jn = (j + 1) % n
            bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
    if cap_start:
        bm.faces.new(vert_rings[0][::-1])
    if cap_end:
        bm.faces.new(vert_rings[-1])
    return vert_rings

def make_ring(center, rx, ry, n=16, rot_x=0.0):
    pts = []
    cx, cy, cz = center
    ca, sa = math.cos(rot_x), math.sin(rot_x)
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        x = rx * math.cos(ang)
        y0 = ry * math.sin(ang)
        y = y0 * ca
        z = y0 * sa
        pts.append(Vector((cx + x, cy + y, cz + z)))
    return pts

def make_limb_rings(p0, p1, r_list, n=12):
    # r_list: lista di (t, rx, ry) lungo l'asse p0 -> p1
    axis = (Vector(p1) - Vector(p0)).normalized()
    ref = Vector((0, -1, 0)) if abs(axis.y) < 0.9 else Vector((1, 0, 0))
    right = axis.cross(ref).normalized()
    fwd = right.cross(axis).normalized()
    rings = []
    for t, rx, ry in r_list:
        c = Vector(p0).lerp(Vector(p1), t)
        ring = []
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            ring.append(c + right * (rx * math.cos(ang)) + fwd * (ry * math.sin(ang)))
        rings.append(ring)
    return rings

# 3. Corpo base + Testa
bm = bmesh.new()

# Torso + Collo (da z=0.84 a z=1.48)
torso_specs = [
    ((0, 0.01, 0.84), 0.145, 0.105),   # bacino basso
    ((0, 0.005, 0.92), 0.150, 0.105),  # fianchi
    ((0, -0.005, 1.03), 0.115, 0.085), # vita
    ((0, -0.015, 1.18), 0.135, 0.105), # torace / seno
    ((0, 0.0, 1.32), 0.150, 0.095),    # spalle
    ((0, 0.005, 1.39), 0.065, 0.060),  # base collo
    ((0, 0.005, 1.48), 0.048, 0.048),  # alto collo
]
add_loft(bm, [make_ring(c, rx, ry, 18) for c, rx, ry in torso_specs])

# Testa scolpita con profilo femminile pulito (da z=1.46 a z=1.695)
head_specs = [
    ((0, -0.01, 1.465), 0.042, 0.052),  # mento/mascella bassa
    ((0, -0.022, 1.495), 0.058, 0.072), # mento/bocca
    ((0, -0.015, 1.540), 0.068, 0.085), # zigomi
    ((0, -0.005, 1.585), 0.072, 0.092), # fronte bassa
    ((0, 0.005, 1.635), 0.069, 0.090),  # fronte alta
    ((0, 0.012, 1.678), 0.050, 0.068),  # sommità cranio
    ((0, 0.015, 1.695), 0.020, 0.028),  # apice
]
add_loft(bm, [make_ring(c, rx, ry, 20) for c, rx, ry in head_specs])

# Naso
nose_rings = [
    make_ring((0, -0.092, 1.575), 0.010, 0.010, 8),
    make_ring((0, -0.106, 1.545), 0.011, 0.012, 8),
    make_ring((0, -0.096, 1.535), 0.010, 0.009, 8),
]
add_loft(bm, nose_rings)

# Orecchie
for s in (1.0, -1.0):
    ear_rings = [
        make_ring((0.070*s, 0.008, 1.555), 0.008, 0.016, 8),
        make_ring((0.078*s, 0.012, 1.555), 0.005, 0.012, 8),
    ]
    add_loft(bm, ear_rings)

# Braccia (spalla -> polso)
for s in (1.0, -1.0):
    arm_rings = make_limb_rings(
        (0.14*s, 0.015, 1.35), (0.52*s, -0.02, 0.97),
        [(0.0, 0.048, 0.046), (0.25, 0.042, 0.040), (0.50, 0.036, 0.035), (0.75, 0.034, 0.033), (1.0, 0.026, 0.024)],
        n=12
    )
    add_loft(bm, arm_rings)
    # Mani (palmo + dita stilizzate per guanti)
    hand_rings = make_limb_rings(
        (0.52*s, -0.02, 0.97), (0.61*s, -0.038, 0.87),
        [(0.0, 0.026, 0.022), (0.35, 0.034, 0.016), (0.70, 0.030, 0.012), (1.0, 0.016, 0.008)],
        n=10
    )
    add_loft(bm, hand_rings)
    # Pollice
    thumb_rings = make_limb_rings(
        (0.54*s, -0.035, 0.945), (0.575*s, -0.065, 0.90),
        [(0.0, 0.011, 0.011), (0.6, 0.009, 0.009), (1.0, 0.006, 0.006)],
        n=8
    )
    add_loft(bm, thumb_rings)

# Gambe (anca -> caviglia)
for s in (1.0, -1.0):
    leg_rings = make_limb_rings(
        (0.095*s, 0.0, 0.88), (0.115*s, 0.02, 0.08),
        [(0.0, 0.072, 0.075), (0.25, 0.062, 0.064), (0.50, 0.048, 0.050), (0.70, 0.050, 0.052), (1.0, 0.036, 0.038)],
        n=14
    )
    add_loft(bm, leg_rings)

mesh_body = bpy.data.meshes.new("CorpoBaseMesh")
bm.to_mesh(mesh_body)
bm.free()

obj_body = bpy.data.objects.new("CorpoBase", mesh_body)
bpy.context.collection.objects.link(obj_body)
obj_body.data.materials.append(mat_skin)
bpy.ops.object.select_all(action='DESELECT')
obj_body.select_set(True)
bpy.context.view_layer.objects.active = obj_body
bpy.ops.object.shade_smooth()

# 4. Occhi, Sopracciglia e Labbra
bm_f = bmesh.new()
for s in (1.0, -1.0):
    # Bulbo oculare
    bmesh.ops.create_uvsphere(bm_f, u_segments=12, v_segments=8, radius=0.012,
                              matrix=Matrix.Translation((0.027*s, -0.088, 1.568)))
    # Sopracciglia
    brow_rings = [
        make_ring((0.015*s, -0.096, 1.584), 0.003, 0.003, 6),
        make_ring((0.029*s, -0.094, 1.588), 0.003, 0.003, 6),
        make_ring((0.044*s, -0.086, 1.585), 0.002, 0.002, 6),
    ]
    add_loft(bm_f, brow_rings)

# Labbra
lip_rings = [
    make_ring((-0.018, -0.091, 1.515), 0.003, 0.004, 6),
    make_ring((0.0, -0.096, 1.515), 0.005, 0.006, 6),
    make_ring((0.018, -0.091, 1.515), 0.003, 0.004, 6),
]
add_loft(bm_f, lip_rings)

mesh_face = bpy.data.meshes.new("DettagliVoltoMesh")
bm_f.to_mesh(mesh_face)
bm_f.free()
obj_face = bpy.data.objects.new("DettagliVolto", mesh_face)
bpy.context.collection.objects.link(obj_face)
obj_face.data.materials.append(mat_iris)
obj_face.data.materials.append(mat_hair)
obj_face.data.materials.append(mat_lips)
# Assegna materiali per faccia in base a Z e Y
for poly in obj_face.data.polygons:
    cz = poly.center.z
    if cz < 1.53:
        poly.material_index = 2  # labbra
    elif cz > 1.578:
        poly.material_index = 1  # sopracciglia
    else:
        poly.material_index = 0  # occhi

# 5. Capelli corti mossi con ciocca bianca sul davanti sinistro (+X, -Y)
bm_h = bmesh.new()
# Calotta base capelli
cap_specs = [
    ((0, 0.012, 1.560), 0.074, 0.094),
    ((0, 0.012, 1.610), 0.078, 0.098),
    ((0, 0.015, 1.660), 0.072, 0.090),
    ((0, 0.018, 1.698), 0.038, 0.050),
]
add_loft(bm_h, [make_ring(c, rx, ry, 18) for c, rx, ry in cap_specs])

def add_strand(bm_target, pts, radii, mat_idx=0):
    rings = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        rings.append(make_ring(p, r, r * 0.75, 8))
    v_rings = add_loft(bm_target, rings)
    # assegna material_index alle facce create
    ring_verts = set(v for vr in v_rings for v in vr)
    for f in bm_target.faces:
        if all(v in ring_verts for v in f.verts):
            f.material_index = mat_idx

# Ciocche laterali e posteriori (scure = mat 0)
strands_dark = [
    ([(-0.04, -0.07, 1.67), (-0.07, -0.05, 1.62), (-0.082, -0.03, 1.56)], [0.022, 0.020, 0.010]),
    ([(-0.06, 0.01, 1.66), (-0.085, 0.01, 1.60), (-0.088, 0.02, 1.53)], [0.025, 0.022, 0.010]),
    ([(0.05, 0.01, 1.66), (0.084, 0.01, 1.60), (0.086, 0.02, 1.53)], [0.025, 0.022, 0.010]),
    ([(-0.04, 0.07, 1.65), (-0.05, 0.10, 1.58), (-0.055, 0.105, 1.50)], [0.026, 0.024, 0.012]),
    ([(0.0, 0.075, 1.65), (0.0, 0.108, 1.57), (0.0, 0.11, 1.49)], [0.028, 0.025, 0.012]),
    ([(0.04, 0.07, 1.65), (0.05, 0.10, 1.58), (0.055, 0.105, 1.50)], [0.026, 0.024, 0.012]),
    ([(-0.02, -0.08, 1.67), (-0.03, -0.095, 1.63), (-0.045, -0.095, 1.59)], [0.020, 0.016, 0.008]),
]
for pts, rads in strands_dark:
    add_strand(bm_h, pts, rads, 0)

# Ciocca bianca frontale destra del disegno (lato +X della testa, vicino alla fronte)
strands_white = [
    ([(0.015, -0.075, 1.675), (0.042, -0.088, 1.635), (0.062, -0.075, 1.585)], [0.018, 0.016, 0.008]),
    ([(0.025, -0.068, 1.680), (0.055, -0.078, 1.630), (0.074, -0.062, 1.575)], [0.015, 0.014, 0.007]),
]
for pts, rads in strands_white:
    add_strand(bm_h, pts, rads, 1)

mesh_hair = bpy.data.meshes.new("CapelliMesh")
bm_h.to_mesh(mesh_hair)
bm_h.free()
obj_hair = bpy.data.objects.new("Capelli", mesh_hair)
bpy.context.collection.objects.link(obj_hair)
obj_hair.data.materials.append(mat_hair)
obj_hair.data.materials.append(mat_hair_white)
bpy.ops.object.select_all(action='DESELECT')
obj_hair.select_set(True)
bpy.context.view_layer.objects.active = obj_hair
bpy.ops.object.shade_smooth()

# Salva .blend e renderizza
blend_path = LAVORO + r"\personaggio.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 01 in", blend_path)
render_viste("01_base", viste=["fronte", "destra", "retro", "tre_quarti"])
