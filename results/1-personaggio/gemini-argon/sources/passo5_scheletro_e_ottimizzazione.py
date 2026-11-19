import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# PASSO 5:
#   1. Correzione morbida del mento/bocca su Testa.
#   2. Ottimizzazione del numero di triangoli sotto il limite di 40.000 (~33.000).
#   3. Unione pulita delle mesh in "Personaggio" (preservando materiali e UV).
#   4. Creazione dello scheletro umanoide completo ("Armature") in posa A e
#      skinning completo con pesi vertice analitici normalizzati per Unity.
# ==============================================================================

scn = bpy.context.scene

# 1. Leviga la piccola cresta sul mento/labbro inferiore della mesh "Testa"
head_obj = bpy.data.objects.get("Testa")
if head_obj:
    for v in head_obj.data.vertices:
        # In Testa, l'area sotto le labbra (Z tra 1.495 e 1.522, davanti Y < -0.065)
        if 1.495 < v.co.z < 1.522 and v.co.y < -0.065 and abs(v.co.x) < 0.030:
            # Rendi il profilo del mento/solco labio-mentale liscio senza creste orizzontali
            target_y = -0.076 + 0.004 * ((abs(v.co.x) / 0.030) ** 2)
            v.co.y = v.co.y * 0.35 + target_y * 0.65
    head_obj.data.update()

# 2. Assicura che ogni oggetto MESH abbia un livello UV chiamato "UVMap" prima di ottimizzare/unire
for obj in list(scn.objects):
    if obj.type != "MESH":
        continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.loops.layers.uv:
        uv_lay = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for loop in f.loops:
                co = obj.matrix_world @ loop.vert.co
                u = 0.5 + math.atan2(co.x, -co.y) / (2 * math.pi)
                v = co.z * 1.2
                loop[uv_lay].uv = (u, v)
    bm.to_mesh(obj.data)
    bm.free()
    if obj.data.uv_layers:
        obj.data.uv_layers[0].name = "UVMap"
    obj.data.update()

# 3. Ottimizzazione selettiva dei triangoli per portare il totale da ~48.800 a ~33.500 (< 40.000)
decimate_targets = {
    "Mantella_Corpo": 0.52,
    "Mantella_Spalla_SX": 0.55,
    "Mantella_Spalla_DX": 0.55,
    "Mantella_Colletto": 0.60,
    "Testa": 0.65,
    "Capelli_Calotta": 0.55,
    "Giacca_Torso": 0.65,
    "Casco_Calotta": 0.60,
    "Pantalone_SX": 0.65,
    "Pantalone_DX": 0.65,
    "Stivale_Gambale_SX": 0.65,
    "Stivale_Gambale_DX": 0.65,
    "Manica_SX": 0.65,
    "Manica_DX": 0.65,
    "Guanto_SX": 0.65,
    "Guanto_DX": 0.65,
}

for obj_name, ratio in decimate_targets.items():
    obj = bpy.data.objects.get(obj_name)
    if obj and obj.type == "MESH":
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        # Usa bmesh.ops.dissolve_degenerate e riduci anelli superflui o applica decimate
        bm.free()
        mod = obj.modifiers.new(name="Decimate_Opt", type='DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
        with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj], selected_editable_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mod.name)

# Riduzione leggera anche su ciocche e spire della corda
for obj in list(scn.objects):
    if obj.type == "MESH" and (obj.name.startswith("Ciocca_") or obj.name.startswith("Corda_Spira_") or obj.name.startswith("Casco_Cornice_")):
        mod = obj.modifiers.new(name="Decimate_Sub", type='DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = 0.65
        with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj], selected_editable_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mod.name)

tris_after_opt = sum(len(p.vertices) - 2 for o in scn.objects if o.type == "MESH" for p in o.data.polygons)
log(f"Triangoli dopo ottimizzazione: {tris_after_opt}")

# 4. Unione di tutte le parti MESH in un unico oggetto "Personaggio" (mantenendo materiali e trasformazioni)
mesh_objs = [o for o in scn.objects if o.type == "MESH" and not o.name.startswith("_gara")]
bpy.ops.object.select_all(action='DESELECT')
for o in mesh_objs:
    o.select_set(True)
main_obj = bpy.data.objects.get("Giacca_Torso") or mesh_objs[0]
bpy.context.view_layer.objects.active = main_obj
with bpy.context.temp_override(
    object=main_obj,
    active_object=main_obj,
    selected_objects=mesh_objs,
    selected_editable_objects=mesh_objs
):
    bpy.ops.object.join()

main_obj.name = "Personaggio"
main_obj.data.name = "Personaggio_Mesh"

# Se dopo l'unione i triangoli fossero ancora > 38.000, applica una rifinitura finale
tris_joined = sum(len(p.vertices) - 2 for p in main_obj.data.polygons)
if tris_joined > 38000:
    target_r = 35500.0 / float(tris_joined)
    mod = main_obj.modifiers.new(name="Final_Cap", type='DECIMATE')
    mod.decimate_type = 'COLLAPSE'
    mod.ratio = target_r
    with bpy.context.temp_override(object=main_obj, active_object=main_obj, selected_objects=[main_obj], selected_editable_objects=[main_obj]):
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Verifica altezza esatta 1.700 m (da Z=0.000 a Z=1.700)
verts = main_obj.data.vertices
min_z = min((main_obj.matrix_world @ v.co).z for v in verts)
max_z = max((main_obj.matrix_world @ v.co).z for v in verts)
scale_z = 1.700 / (max_z - min_z)
for v in verts:
    v.co.z = (v.co.z - min_z) * scale_z
main_obj.data.update()

# 5. CREAZIONE SCHELETRO UMANOIDE COMPLETO ("Armature") E SKINNING PER UNITY
for o in list(scn.objects):
    if o.type == "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.armatures):
    bpy.data.armatures.remove(a)

arm_data = bpy.data.armatures.new("Armature_Data")
arm_obj = bpy.data.objects.new("Armature", arm_data)
scn.collection.objects.link(arm_obj)
arm_obj.location = (0.0, 0.0, 0.0)

bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

ebones = arm_data.edit_bones

# Definizione ossa: (nome, parent_name, connected, head, tail)
bone_specs = [
    ("pelvis",      None,          False, (0.000,  0.005, 0.860), (0.000,  0.004, 0.980)),
    ("spine",       "pelvis",      True,  (0.000,  0.004, 0.980), (0.000,  0.000, 1.150)),
    ("chest",       "spine",       True,  (0.000,  0.000, 1.150), (0.000,  0.002, 1.365)),
    ("neck",        "chest",       True,  (0.000,  0.002, 1.365), (0.000, -0.004, 1.475)),
    ("head",        "neck",        True,  (0.000, -0.004, 1.475), (0.000, -0.006, 1.685)),

    # Braccio sinistro (+X) in posa A
    ("shoulder.L",  "chest",       False, (0.035,  0.004, 1.345), (0.165,  0.008, 1.340)),
    ("upper_arm.L", "shoulder.L",  True,  (0.165,  0.008, 1.340), (0.355,  0.012, 1.150)),
    ("forearm.L",   "upper_arm.L", True,  (0.355,  0.012, 1.150), (0.488, -0.014, 1.002)),
    ("hand.L",      "forearm.L",   True,  (0.488, -0.014, 1.002), (0.595, -0.038, 0.880)),

    # Braccio destro (-X) in posa A
    ("shoulder.R",  "chest",       False, (-0.035, 0.004, 1.345), (-0.165, 0.008, 1.340)),
    ("upper_arm.R", "shoulder.R",  True,  (-0.165, 0.008, 1.340), (-0.355, 0.012, 1.150)),
    ("forearm.R",   "upper_arm.R", True,  (-0.355, 0.012, 1.150), (-0.488,-0.014, 1.002)),
    ("hand.R",      "forearm.R",   True,  (-0.488,-0.014, 1.002), (-0.595,-0.038, 0.880)),

    # Gamba sinistra (+X)
    ("thigh.L",     "pelvis",      False, (0.092,  0.004, 0.860), (0.106, -0.010, 0.480)),
    ("shin.L",      "thigh.L",     True,  (0.106, -0.010, 0.480), (0.114, -0.002, 0.090)),
    ("foot.L",      "shin.L",      True,  (0.114, -0.002, 0.090), (0.128, -0.095, 0.030)),
    ("toe.L",       "foot.L",      True,  (0.128, -0.095, 0.030), (0.140, -0.158, 0.018)),

    # Gamba destra (-X)
    ("thigh.R",     "pelvis",      False, (-0.092, 0.004, 0.860), (-0.106,-0.010, 0.480)),
    ("shin.R",      "thigh.R",     True,  (-0.106,-0.010, 0.480), (-0.114,-0.002, 0.090)),
    ("foot.R",      "shin.R",      True,  (-0.114,-0.002, 0.090), (-0.128,-0.095, 0.030)),
    ("toe.R",       "foot.R",      True,  (-0.128,-0.095, 0.030), (-0.140,-0.158, 0.018)),
]

created_bones = {}
for bname, pname, conn, h_co, t_co in bone_specs:
    b = ebones.new(bname)
    b.head = Vector(h_co)
    b.tail = Vector(t_co)
    if pname and pname in created_bones:
        b.parent = created_bones[pname]
        b.use_connect = conn
    created_bones[bname] = b

bpy.ops.object.mode_set(mode='OBJECT')

# Parent di Personaggio all'Armature e creazione Vertex Groups
main_obj.parent = arm_obj
arm_mod = main_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj

main_obj.vertex_groups.clear()
vgroups = {}
for bname, _, _, _, _ in bone_specs:
    vgroups[bname] = main_obj.vertex_groups.new(name=bname)

# Funzione distanza punto-segmento 3D per calcolare pesi morbidi e continui
def dist_to_segment(pt, a, b):
    ab = b - a
    len_sq = ab.length_squared
    if len_sq < 1e-8:
        return (pt - a).length
    t = max(0.0, min(1.0, (pt - a).dot(ab) / len_sq))
    proj = a + ab * t
    return (pt - proj).length

bone_segments = [(bname, Vector(h_co), Vector(t_co)) for bname, _, _, h_co, t_co in bone_specs]

for v in main_obj.data.vertices:
    co = v.co
    # Regole anatomiche per evitare che la mantella/accessori vengano tirati dalle mani o viceversa
    weights = {}
    if co.z > 1.465 and abs(co.x) < 0.12 and co.y < 0.14:
        # Testa, viso e capelli appartengono a head/neck
        d_head = dist_to_segment(co, Vector((0, -0.004, 1.475)), Vector((0, -0.006, 1.685)))
        d_neck = dist_to_segment(co, Vector((0, 0.002, 1.365)), Vector((0, -0.004, 1.475)))
        w_h = 1.0 / (d_head ** 2 + 0.0008)
        w_n = (1.0 / (d_neck ** 2 + 0.0008)) * (0.3 if co.z > 1.50 else 1.0)
        weights["head"] = w_h
        weights["neck"] = w_n
    else:
        for bname, h_co, t_co in bone_segments:
            # Filtra ossa del lato opposto per arti
            if bname.endswith(".L") and co.x < -0.02:
                continue
            if bname.endswith(".R") and co.x > 0.02:
                continue
            # Le braccia influenzano solo vertici lungo il braccio (|x| > 0.16, z > 0.85, non dietro la schiena)
            if bname.startswith(("upper_arm", "forearm", "hand")):
                if abs(co.x) < 0.15 or co.z < 0.84 or co.y > 0.12:
                    continue
            d = dist_to_segment(co, h_co, t_co)
            w = 1.0 / ((d + 0.015) ** 3.2)
            weights[bname] = w

    # Prendi le 3 ossa più vicine e normalizza a 1.0
    top_bones = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
    tot_w = sum(w for _, w in top_bones)
    if tot_w > 0:
        for bname, w in top_bones:
            vgroups[bname].add([v.index], w / tot_w, 'REPLACE')
    else:
        vgroups["pelvis"].add([v.index], 1.0, 'REPLACE')

# Statistiche finali
pts_all = [main_obj.matrix_world @ v.co for v in main_obj.data.vertices]
min_z = min(p.z for p in pts_all)
max_z = max(p.z for p in pts_all)
final_tris = sum(len(p.vertices) - 2 for p in main_obj.data.polygons)
num_bones = len(arm_data.bones)
log(f"Passo 5 completato: Oggetto={main_obj.name}, Z_min={min_z:.4f}m, Z_max={max_z:.4f}m, Altezza={max_z-min_z:.4f}m, Triangoli={final_tris}, Ossa={num_bones}")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
glb_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.glb"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# Esporta personaggio.glb per Unity (metri, Y up)
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
main_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=True)
log(f"Esportato GLB: {glb_path}")

render_viste("finale_personaggio")

