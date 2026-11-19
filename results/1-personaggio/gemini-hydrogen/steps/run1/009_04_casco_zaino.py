import bpy
import bmesh
import math
from mathutils import Vector, Matrix

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = LAVORO + r"\personaggio.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

def get_or_make_mat(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_brass = get_or_make_mat("Ottone", (0.66, 0.50, 0.24), roughness=0.36, metallic=0.88)
mat_brass_dark = get_or_make_mat("OttoneScuro", (0.42, 0.32, 0.16), roughness=0.45, metallic=0.85)
mat_glass = get_or_make_mat("VetroOblo", (0.12, 0.16, 0.17), roughness=0.12, metallic=0.1)
mat_pack = get_or_make_mat("SaccoZaino", (0.46, 0.40, 0.31), roughness=0.85)
mat_leather_dark = get_or_make_mat("PelleScura", (0.10, 0.07, 0.05), roughness=0.48)
mat_hose = get_or_make_mat("TubiGomma", (0.24, 0.21, 0.17), roughness=0.72)

def tag_faces(res_verts, mat_idx):
    vset = set(res_verts)
    for v in vset:
        for f in v.link_faces:
            if all(fv in vset for fv in f.verts):
                f.material_index = mat_idx

def add_loft(bm, rings, cap_start=True, cap_end=True, mat_idx=0):
    n = len(rings[0])
    vert_rings = [[bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(len(vert_rings) - 1):
        r0, r1 = vert_rings[i], vert_rings[i + 1]
        for j in range(n):
            jn = (j + 1) % n
            f = bm.faces.new((r0[j], r0[jn], r1[jn], r1[j]))
            f.material_index = mat_idx
    if cap_start:
        f = bm.faces.new(vert_rings[0][::-1])
        f.material_index = mat_idx
    if cap_end:
        f = bm.faces.new(vert_rings[-1])
        f.material_index = mat_idx

def add_tube(bm, pts, r, n=10, mat_idx=0):
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = u.cross(t).normalized()
        rings.append([p + u * (r * math.cos(2 * math.pi * k / n)) + v * (r * math.sin(2 * math.pi * k / n)) for k in range(n)])
    add_loft(bm, rings, mat_idx=mat_idx)

# 1. Casco da palombaro in ottone sulla schiena
bm_c = bmesh.new()
h_center = Vector((0.0, 0.225, 1.265))

# Cupola principale del casco
res = bmesh.ops.create_uvsphere(bm_c, u_segments=24, v_segments=16, radius=0.135,
                                matrix=Matrix.Translation(h_center) @ Matrix.Diagonal((0.95, 1.0, 1.08, 1.0)))
tag_faces(res["verts"], 0)

# Collare inferiore del casco
res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=20,
                            radius1=0.115, radius2=0.105, depth=0.04,
                            matrix=Matrix.Translation(h_center + Vector((0, 0, -0.13))))
tag_faces(res["verts"], 1)

# Oblò posteriore (+Y) con cornice, vetro, croce e bulloni
porthole_c = h_center + Vector((0.0, 0.115, 0.01))
rot_y90 = Matrix.Rotation(math.radians(90), 4, 'X')

# Cornice esterna oblò
res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=20,
                            radius1=0.088, radius2=0.082, depth=0.035,
                            matrix=Matrix.Translation(porthole_c) @ rot_y90)
tag_faces(res["verts"], 1)

# Vetro oblò (leggermente più avanti)
res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=20,
                            radius1=0.068, radius2=0.068, depth=0.012,
                            matrix=Matrix.Translation(porthole_c + Vector((0, 0.014, 0))) @ rot_y90)
tag_faces(res["verts"], 2)

# Griglia a croce sull'oblò
res = bmesh.ops.create_cube(bm_c, size=1.0,
                            matrix=Matrix.Translation(porthole_c + Vector((0, 0.021, 0))) @ Matrix.Diagonal((0.145, 0.008, 0.010, 1.0)))
tag_faces(res["verts"], 0)
res = bmesh.ops.create_cube(bm_c, size=1.0,
                            matrix=Matrix.Translation(porthole_c + Vector((0, 0.021, 0))) @ Matrix.Diagonal((0.010, 0.008, 0.145, 1.0)))
tag_faces(res["verts"], 0)

# Bulloni attorno all'oblò
for k in range(12):
    ang = 2 * math.pi * k / 12
    bx = porthole_c.x + 0.077 * math.cos(ang)
    bz = porthole_c.z + 0.077 * math.sin(ang)
    res = bmesh.ops.create_uvsphere(bm_c, u_segments=6, v_segments=4, radius=0.006,
                                    matrix=Matrix.Translation((bx, porthole_c.y + 0.018, bz)))
    tag_faces(res["verts"], 0)

# Valvole laterali e sfiato superiore
for s in (1.0, -1.0):
    res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=12,
                                radius1=0.028, radius2=0.022, depth=0.035,
                                matrix=Matrix.Translation(h_center + Vector((0.125*s, 0.0, 0.01))) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
    tag_faces(res["verts"], 1)

# Valvola superiore destra (-X)
res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=12,
                            radius1=0.024, radius2=0.018, depth=0.04,
                            matrix=Matrix.Translation(h_center + Vector((-0.07, -0.02, 0.13))))
tag_faces(res["verts"], 1)

mesh_c = bpy.data.meshes.new("CascoPalombaroMesh")
bm_c.to_mesh(mesh_c)
bm_c.free()
obj_c = bpy.data.objects.new("CascoPalombaro", mesh_c)
bpy.context.collection.objects.link(obj_c)
for m in (mat_brass, mat_brass_dark, mat_glass):
    obj_c.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT')
obj_c.select_set(True)
bpy.context.view_layer.objects.active = obj_c
bpy.ops.object.shade_smooth()

# 2. Sacco arrotolato sotto il casco + cinghie + tubi flessibili
bm_z = bmesh.new()
pack_c = Vector((0.0, 0.21, 1.04))
res = bmesh.ops.create_cone(bm_z, cap_ends=True, cap_tris=False, segments=18,
                            radius1=0.062, radius2=0.062, depth=0.22,
                            matrix=Matrix.Translation(pack_c) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
tag_faces(res["verts"], 0)

# Cinghie di fissaggio attorno al sacco
for dx in (-0.065, 0.065):
    res = bmesh.ops.create_cone(bm_z, cap_ends=False, cap_tris=False, segments=18,
                                radius1=0.065, radius2=0.065, depth=0.020,
                                matrix=Matrix.Translation(pack_c + Vector((dx, 0, 0))) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
    tag_faces(res["verts"], 1)

# Tubi flessibili dal casco ai fianchi/sotto il sacco
hose_1 = [
    h_center + Vector((0.12, 0.01, -0.01)),
    Vector((0.15, 0.25, 1.15)),
    Vector((0.13, 0.27, 0.99)),
    Vector((0.04, 0.25, 0.92)),
    Vector((-0.07, 0.24, 0.94)),
    Vector((-0.13, 0.22, 1.05)),
]
add_tube(bm_z, hose_1, 0.013, n=10, mat_idx=2)

hose_2 = [
    h_center + Vector((-0.12, 0.01, -0.01)),
    Vector((-0.145, 0.24, 1.13)),
    Vector((-0.12, 0.25, 0.98)),
    Vector((-0.06, 0.23, 0.96)),
]
add_tube(bm_z, hose_2, 0.012, n=10, mat_idx=2)

# Cinghie dello zaino che passano sopra le spalle
for s in (1.0, -1.0):
    strap_pts = [
        Vector((0.09*s, 0.16, 1.28)),
        Vector((0.08*s, 0.08, 1.37)),
        Vector((0.07*s, -0.06, 1.35)),
        Vector((0.08*s, -0.11, 1.22)),
    ]
    add_tube(bm_z, strap_pts, 0.011, n=6, mat_idx=1)

mesh_z = bpy.data.meshes.new("ZainoTubiMesh")
bm_z.to_mesh(mesh_z)
bm_z.free()
obj_z = bpy.data.objects.new("ZainoTubi", mesh_z)
bpy.context.collection.objects.link(obj_z)
for m in (mat_pack, mat_leather_dark, mat_hose):
    obj_z.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT')
obj_z.select_set(True)
bpy.context.view_layer.objects.active = obj_z
bpy.ops.object.shade_smooth()

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 04 in", blend_path)
render_viste("04_casco", viste=["fronte", "destra", "retro", "tre_quarti"])
