import bpy
import bmesh
import math
from mathutils import Vector, Matrix

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = LAVORO + r"\personaggio.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

def get_or_make_mat(name, color, roughness=0.85, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_cape = get_or_make_mat("MantelloVerde", (0.20, 0.33, 0.29), roughness=0.86)
mat_cape_lining = get_or_make_mat("MantelloStrappo", (0.58, 0.56, 0.49), roughness=0.90)
mat_shell = get_or_make_mat("Conchiglie", (0.82, 0.78, 0.72), roughness=0.45)

# 1. Mantello verde strappato (griglia aperta avvolta dietro + spalle, con pieghe e orlo frastagliato)
bm = bmesh.new()

# Parametri: u in [-1, 1] (angolo da davanti-destra a dietro a davanti-sinistra)
# v in [0, 1] (0 = colletto alto, 1 = orlo inferiore strappato)
nu = 36
nv = 18

# Profilo strappi all'orlo (v=1): altezze Z diverse per creare punte e strappi
def tear_z(u_norm):
    # u_norm in [-1, 1], 0 = centro schiena
    base = 0.34 + 0.14 * abs(u_norm)
    jag = 0.08 * math.sin(u_norm * 19.0) + 0.05 * math.cos(u_norm * 31.0) + 0.03 * math.sin(u_norm * 47.0)
    return max(0.24, min(0.55, base + jag))

grid = []
for iv in range(nv + 1):
    v = iv / nv
    row = []
    for iu in range(nu + 1):
        u_norm = -1.0 + 2.0 * (iu / nu)  # -1 (front-right) .. 0 (back) .. +1 (front-left)
        # Angolo: 0 = dietro (+Y), +-135 deg = davanti-lati
        if v < 0.14:
            # Colletto avvolgente attorno al collo (aperto solo davanti al centro)
            max_ang = math.radians(150)
        elif v < 0.32:
            # Spalle: copre fino a davanti
            max_ang = math.radians(142)
        else:
            # Schiena e fianchi: si apre gradualmente davanti così si vedono tunica e cintura
            max_ang = math.radians(135 - 35 * ((v - 0.32) / 0.68))

        ang = u_norm * max_ang  # 0 = +Y (dietro), +pi/2 = +X, -pi/2 = -X
        # Raggio X e Y
        if v < 0.10:
            # Colletto alto
            t_c = v / 0.10
            rx = 0.072 + 0.018 * t_c
            ry = 0.072 + 0.015 * t_c
            z = 1.445 - 0.065 * t_c
            cx, cy = 0.0, 0.008
        elif v < 0.28:
            # Spalle (da collo a metà braccio superiore)
            t_s = (v - 0.10) / 0.18
            rx = 0.090 + 0.155 * t_s
            ry = 0.087 + 0.065 * t_s
            z = 1.38 - 0.12 * t_s
            cx, cy = 0.0, 0.020 * t_s
        else:
            # Drappeggio lungo la schiena fino all'orlo strappato
            t_d = (v - 0.28) / 0.72
            rx = 0.245 + 0.145 * t_d
            ry = 0.152 + 0.085 * t_d
            z_end = tear_z(u_norm)
            z = 1.26 * (1.0 - t_d) + z_end * t_d
            cx, cy = 0.0, 0.020 + 0.045 * t_d

        # Pieghe verticali del tessuto
        fold = 0.016 * math.sin(u_norm * 14.0) * min(1.0, max(0.0, (v - 0.15) / 0.5))
        x = cx + (rx + fold) * math.sin(ang)
        y = cy + (ry + fold) * math.cos(ang)

        # Assicura che sulle spalle il mantello stia sopra le maniche (z leggermente rialzato ai lati)
        if 0.12 <= v <= 0.32 and abs(math.sin(ang)) > 0.6:
            z += 0.015

        row.append(bm.verts.new(Vector((x, y, z))))
    grid.append(row)

for iv in range(nv):
    for iu in range(nu):
        v00 = grid[iv][iu]
        v10 = grid[iv][iu + 1]
        v11 = grid[iv + 1][iu + 1]
        v01 = grid[iv + 1][iu]
        bm.faces.new((v00, v10, v11, v01))

mesh_cape = bpy.data.meshes.new("MantelloVerdeMesh")
bm.to_mesh(mesh_cape)
bm.free()

obj_cape = bpy.data.objects.new("MantelloVerde", mesh_cape)
bpy.context.collection.objects.link(obj_cape)
obj_cape.data.materials.append(mat_cape)

# Solidify leggero per dare spessore al mantello (visibile da davanti e dietro)
mod_sol = obj_cape.modifiers.new("Spessore", 'SOLIDIFY')
mod_sol.thickness = 0.007
mod_sol.offset = 0.0
bpy.ops.object.select_all(action='DESELECT')
obj_cape.select_set(True)
bpy.context.view_layer.objects.active = obj_cape
bpy.ops.object.modifier_apply(modifier="Spessore")
bpy.ops.object.shade_smooth()

# 2. Stracci chiari interni ai fianchi (visibili davanti ai lati della tunica) + Conchiglie sul petto sinistro (+X)
bm_d = bmesh.new()
for s in (1.0, -1.0):
    # Striscia di tessuto chiaro strappato che pende dal fianco sotto il mantello
    p_top = Vector((0.165*s, -0.02, 0.85))
    p_mid = Vector((0.185*s, -0.01, 0.68))
    p_bot = Vector((0.175*s, 0.01, 0.50))
    w = 0.028
    v0 = bm_d.verts.new(p_top + Vector((-w, 0, 0)))
    v1 = bm_d.verts.new(p_top + Vector((w, 0, 0)))
    v2 = bm_d.verts.new(p_mid + Vector((w*0.8, 0, 0)))
    v3 = bm_d.verts.new(p_mid + Vector((-w*0.8, 0, 0)))
    v4 = bm_d.verts.new(p_bot + Vector((0, 0, 0)))
    f1 = bm_d.faces.new((v0, v1, v2, v3))
    f2 = bm_d.faces.new((v3, v2, v4))
    f1.material_index = 0
    f2.material_index = 0

# Due piccole conchiglie fermaglio sul lato sinistro del petto (+X, -Y)
for pos, rad in ((Vector((0.085, -0.088, 1.335)), 0.016), (Vector((0.112, -0.082, 1.325)), 0.013)):
    res = bmesh.ops.create_uvsphere(bm_d, u_segments=10, v_segments=6, radius=rad,
                                    matrix=Matrix.Translation(pos) @ Matrix.Diagonal((1.0, 0.45, 1.15, 1.0)))
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = 1

mesh_d = bpy.data.meshes.new("MantelloDettagliMesh")
bm_d.to_mesh(mesh_d)
bm_d.free()
obj_d = bpy.data.objects.new("MantelloDettagli", mesh_d)
bpy.context.collection.objects.link(obj_d)
obj_d.data.materials.append(mat_cape_lining)
obj_d.data.materials.append(mat_shell)

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 03 in", blend_path)
render_viste("03_mantello", viste=["fronte", "destra", "retro", "tre_quarti"])
