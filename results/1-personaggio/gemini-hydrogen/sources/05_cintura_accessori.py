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

mat_leather = get_or_make_mat("PelleMarrone", (0.16, 0.10, 0.07), roughness=0.52)
mat_leather_dark = get_or_make_mat("PelleScura", (0.10, 0.07, 0.05), roughness=0.48)
mat_brass = get_or_make_mat("Ottone", (0.66, 0.50, 0.24), roughness=0.36, metallic=0.88)
mat_rope = get_or_make_mat("CordaCanapa", (0.68, 0.61, 0.48), roughness=0.90)
mat_silver = get_or_make_mat("MetalloChiaro", (0.72, 0.74, 0.75), roughness=0.30, metallic=0.85)
mat_paper = get_or_make_mat("Pergamena", (0.80, 0.73, 0.58), roughness=0.82)

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

def add_tube(bm, pts, r, n=10, mat_idx=0, closed=False):
    rings = []
    m = len(pts)
    for i, p in enumerate(pts):
        if closed:
            t = (pts[(i + 1) % m] - pts[(i - 1) % m]).normalized()
        elif i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == m - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = u.cross(t).normalized()
        rings.append([p + u * (r * math.cos(2 * math.pi * k / n)) + v * (r * math.sin(2 * math.pi * k / n)) for k in range(n)])
    if closed:
        rings.append(rings[0])
    add_loft(bm, rings, cap_start=not closed, cap_end=not closed, mat_idx=mat_idx)

def make_ring_oval(cx, cy, cz, rx, ry, n=24, tilt_y=0.0):
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        x = rx * math.cos(ang)
        y = ry * math.sin(ang)
        z = cz + tilt_y * math.cos(ang)
        pts.append(Vector((cx + x, cy + y, z)))
    return pts

# 1. Cintura e cinghie sul torace
bm_c = bmesh.new()

# Cintura principale in vita (z=1.02)
r_top = make_ring_oval(0, -0.005, 1.045, 0.132, 0.102, 24)
r_bot = make_ring_oval(0, -0.005, 0.998, 0.136, 0.105, 24)
add_loft(bm_c, [r_bot, r_top], cap_start=False, cap_end=False, mat_idx=0)
bmesh.ops.solidify(bm_c, geom=bm_c.faces[:], thickness=0.008)

# Fibbia in ottone al centro davanti
res = bmesh.ops.create_cube(bm_c, size=1.0,
                            matrix=Matrix.Translation((0.0, -0.108, 1.022)) @ Matrix.Diagonal((0.048, 0.014, 0.052, 1.0)))
tag_faces(res["verts"], 2)

# Seconda cintura obliqua bassa + ciondolo bussola
r2_top = make_ring_oval(0, 0.0, 0.965, 0.155, 0.114, 24, tilt_y=0.025)
r2_bot = make_ring_oval(0, 0.0, 0.935, 0.158, 0.116, 24, tilt_y=0.025)
add_loft(bm_c, [r2_bot, r2_top], cap_start=False, cap_end=False, mat_idx=1)

# Ciondolo rotondo sul davanti
res = bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=14,
                            radius1=0.018, radius2=0.018, depth=0.008,
                            matrix=Matrix.Translation((0.025, -0.122, 0.915)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
tag_faces(res["verts"], 3)

# Cinghie incrociate sul torace
cross_1 = [
    Vector((-0.11, -0.085, 1.33)),
    Vector((-0.045, -0.128, 1.23)),
    Vector((0.0, -0.132, 1.18)),
    Vector((0.055, -0.122, 1.11)),
    Vector((0.12, -0.092, 1.045)),
]
add_tube(bm_c, cross_1, 0.011, n=6, mat_idx=1)

cross_2 = [
    Vector((0.11, -0.085, 1.33)),
    Vector((0.045, -0.128, 1.23)),
    Vector((0.0, -0.132, 1.18)),
    Vector((-0.055, -0.122, 1.11)),
    Vector((-0.12, -0.092, 1.045)),
]
add_tube(bm_c, cross_2, 0.011, n=6, mat_idx=1)

# Fibbia al centro del petto
res = bmesh.ops.create_cube(bm_c, size=1.0,
                            matrix=Matrix.Translation((0.0, -0.136, 1.18)) @ Matrix.Diagonal((0.032, 0.012, 0.032, 1.0)))
tag_faces(res["verts"], 2)

mesh_c = bpy.data.meshes.new("CinturaCinghieMesh")
bm_c.to_mesh(mesh_c)
bm_c.free()
obj_c = bpy.data.objects.new("CinturaCinghie", mesh_c)
bpy.context.collection.objects.link(obj_c)
for m in (mat_leather, mat_leather_dark, mat_brass, mat_silver):
    obj_c.data.materials.append(m)

# 2. Corda arrotolata + Borraccia sul fianco DESTRO (-X)
bm_r = bmesh.new()

# Corda arrotolata (5 spire verticali)
rope_center = Vector((-0.175, -0.055, 0.80))
for k in range(5):
    off_x = (k - 2) * 0.011
    off_y = (k - 2) * 0.004
    pts = []
    for i in range(18):
        ang = 2 * math.pi * i / 18
        px = rope_center.x + off_x + 0.015 * math.cos(ang)
        py = rope_center.y + off_y + 0.048 * math.cos(ang)
        pz = rope_center.z + 0.115 * math.sin(ang)
        pts.append(Vector((px, py, pz)))
    add_tube(bm_r, pts, 0.009, n=8, mat_idx=0, closed=True)

# Laccio di cuoio che tiene la corda alla cintura
res = bmesh.ops.create_cube(bm_r, size=1.0,
                            matrix=Matrix.Translation((-0.165, -0.055, 0.92)) @ Matrix.Diagonal((0.055, 0.024, 0.035, 1.0)))
tag_faces(res["verts"], 1)

# Borraccia rotonda e contenitore sul fianco destro dietro la corda
res = bmesh.ops.create_uvsphere(bm_r, u_segments=14, v_segments=10, radius=0.055,
                                matrix=Matrix.Translation((-0.195, 0.035, 0.85)) @ Matrix.Diagonal((0.65, 1.0, 1.05, 1.0)))
tag_faces(res["verts"], 1)
res = bmesh.ops.create_cone(bm_r, cap_ends=True, cap_tris=False, segments=10,
                            radius1=0.014, radius2=0.016, depth=0.025,
                            matrix=Matrix.Translation((-0.195, 0.035, 0.915)))
tag_faces(res["verts"], 2)

# Contenitore cilindrico sotto la borraccia
res = bmesh.ops.create_cone(bm_r, cap_ends=True, cap_tris=False, segments=14,
                            radius1=0.034, radius2=0.034, depth=0.14,
                            matrix=Matrix.Translation((-0.20, 0.035, 0.72)))
tag_faces(res["verts"], 1)

mesh_r = bpy.data.meshes.new("AccessoriDestraMesh")
bm_r.to_mesh(mesh_r)
bm_r.free()
obj_r = bpy.data.objects.new("AccessoriDestra", mesh_r)
bpy.context.collection.objects.link(obj_r)
for m in (mat_rope, mat_leather, mat_brass):
    obj_r.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT')
obj_r.select_set(True)
bpy.context.view_layer.objects.active = obj_r
bpy.ops.object.shade_smooth()

# 3. Tubo portamappe sul fianco SINISTRO (+X)
bm_l = bmesh.new()
tube_pos = Vector((0.205, -0.02, 0.72))
tube_rot = Matrix.Rotation(math.radians(-10), 4, 'X') @ Matrix.Rotation(math.radians(6), 4, 'Y')
tube_mat = Matrix.Translation(tube_pos) @ tube_rot

# Corpo del tubo in cuoio
res = bmesh.ops.create_cone(bm_l, cap_ends=True, cap_tris=False, segments=16,
                            radius1=0.033, radius2=0.033, depth=0.33,
                            matrix=tube_mat)
tag_faces(res["verts"], 0)

# Tappi in ottone (fondo e anelli di rinforzo)
for dz in (-0.165, -0.06, 0.06, 0.155):
    res = bmesh.ops.create_cone(bm_l, cap_ends=True, cap_tris=False, segments=16,
                                radius1=0.036, radius2=0.036, depth=0.022,
                                matrix=tube_mat @ Matrix.Translation((0, 0, dz)))
    tag_faces(res["verts"], 1)

# Pergamena / mappa arrotolata che spunta dall'alto
res = bmesh.ops.create_cone(bm_l, cap_ends=True, cap_tris=False, segments=14,
                            radius1=0.024, radius2=0.026, depth=0.08,
                            matrix=tube_mat @ Matrix.Translation((0, 0, 0.185)))
tag_faces(res["verts"], 2)

mesh_l = bpy.data.meshes.new("TuboMappe_LMesh")
bm_l.to_mesh(mesh_l)
bm_l.free()
obj_l = bpy.data.objects.new("TuboMappe_L", mesh_l)
bpy.context.collection.objects.link(obj_l)
for m in (mat_leather, mat_brass, mat_paper):
    obj_l.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT')
obj_l.select_set(True)
bpy.context.view_layer.objects.active = obj_l
bpy.ops.object.shade_smooth()

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 05 in", blend_path)
render_viste("05_accessori", viste=["fronte", "destra", "retro", "sinistra", "tre_quarti"])
