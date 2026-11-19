import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ==============================================================================
# GROUP 10 - Materials pass, triangles, skeleton (rev_10 & rev_prova_osso)
# + Face eye-socket/mouth clarity and natural rounded hair crown contour
# ==============================================================================

scn = bpy.context.scene

# ------------------------------------------------------------------------------
# 0. Polish face features (eyes & mouth 100% visible) and rounded hair top arch
# ------------------------------------------------------------------------------
o_head = bpy.data.objects.get("Testa")
if o_head:
    for v in o_head.data.vertices:
        # Indent eye sockets at (X=+-0.0325, Z=1.585) by +0.006 in Y so the 0.03m eyes sit slightly into the face without being clipped
        if v.co.y < -0.03:
            for sx_e in (-1.0, 1.0):
                d2 = ((v.co.x - sx_e * 0.0325) / 0.018) ** 2 + ((v.co.z - 1.585) / 0.011) ** 2
                if d2 < 1.8:
                    v.co.y += 0.0065 * math.exp(-d2 * 1.2)
            # Subtle mouth indentation at Z=1.505 so Labbra sits cleanly in front
            d2_m = (v.co.x / 0.025) ** 2 + ((v.co.z - 1.505) / 0.008) ** 2
            if d2_m < 1.8:
                v.co.y += 0.0035 * math.exp(-d2_m * 1.2)
    o_head.data.update()

occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    for v in occhi_obj.data.vertices:
        v.co.y -= 0.0042
    occhi_obj.data.update()

labbra_obj = bpy.data.objects.get("Labbra")
if labbra_obj:
    for v in labbra_obj.data.vertices:
        v.co.y -= 0.0045
    labbra_obj.data.update()

brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for v in brows_obj.data.vertices:
        v.co.y -= 0.0025
    brows_obj.data.update()

# Round the top corners of Capelli_Scuri (remove the flat X=+-0.095 wall while keeping max width 0.190 m at Z~1.60..1.63 and max Z=1.700 m)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    for v in capelli_obj.data.vertices:
        if v.co.z > 1.615:
            # Smooth dome arch above Z=1.615 up to Z=1.700
            t_dome = min(1.0, (v.co.z - 1.615) / (1.700 - 1.615))
            max_rx_z = 0.095 * math.sqrt(max(0.08, 1.0 - (t_dome ** 1.5) * 0.78))
            if abs(v.co.x) > max_rx_z:
                v.co.x = math.copysign(max_rx_z + (abs(v.co.x) - max_rx_z) * 0.22, v.co.x)
        elif v.co.z < 1.545:
            # Wavy taper at lower tips near Z=1.48..1.545
            t_low = min(1.0, (1.545 - v.co.z) / 0.065)
            wave_x = 0.005 * math.sin(v.co.y * 55.0 + v.co.z * 40.0)
            v.co.x = v.co.x * (1.0 - 0.12 * t_low) + math.copysign(wave_x, v.co.x)
    # Normalize exact X width to 0.190 m
    xs_h = [v.co.x for v in capelli_obj.data.vertices]
    xmin_h, xmax_h = min(xs_h), max(xs_h)
    for v in capelli_obj.data.vertices:
        v.co.x = -0.095 + ((v.co.x - xmin_h) / max(1e-5, xmax_h - xmin_h)) * 0.190
    capelli_obj.data.update()

# ------------------------------------------------------------------------------
# 1. GROUP 10.1 - Materials check (Leather 0.6-0.7, Cloth 0.85-0.95, Brass metal 1.0 & rough 0.3-0.4, Glass alpha/transmission, no pure black/white)
# ------------------------------------------------------------------------------
mat_rules = {
    # Cloth materials: roughness 0.85 to 0.95
    "Mat_GiaccaBlu":       ((0.13, 0.16, 0.22), 0.88, 0.0, 1.0),
    "Mat_CucituraGiacca":  ((0.08, 0.10, 0.14), 0.90, 0.0, 1.0),
    "Mat_CollettoCamicia": ((0.30, 0.33, 0.38), 0.88, 0.0, 1.0),
    "Mat_ManicaLino":      ((0.82, 0.76, 0.64), 0.88, 0.0, 1.0),
    "Mat_Camicia":         ((0.82, 0.76, 0.64), 0.88, 0.0, 1.0),
    "Mat_MantellaVerde":   ((0.22, 0.34, 0.31), 0.88, 0.0, 1.0),
    "Mat_Pantaloni":       ((0.22, 0.19, 0.16), 0.88, 0.0, 1.0),
    "Mat_Corda":           ((0.70, 0.62, 0.47), 0.88, 0.0, 1.0),
    "Mat_LacciTan":        ((0.55, 0.42, 0.28), 0.86, 0.0, 1.0),
    "Mat_SaccaTela":       ((0.66, 0.58, 0.45), 0.88, 0.0, 1.0),
    "Mat_Pergamena":       ((0.58, 0.47, 0.34), 0.86, 0.0, 1.0),
    # Leather materials: roughness 0.6 to 0.7
    "Mat_CuoioMedio":      ((0.36, 0.22, 0.12), 0.65, 0.0, 1.0),
    "Mat_CuoioScuro":      ((0.24, 0.14, 0.08), 0.65, 0.0, 1.0),
    "Mat_CuoioChiaro":     ((0.48, 0.37, 0.26), 0.65, 0.0, 1.0),
    "Mat_GuantoCuoio":     ((0.26, 0.16, 0.09), 0.64, 0.0, 1.0),
    "Mat_CinturinoGuanto": ((0.20, 0.12, 0.07), 0.66, 0.0, 1.0),
    "Mat_StivaleCuoio":    ((0.30, 0.18, 0.10), 0.64, 0.0, 1.0),
    "Mat_SuolaScuro":      ((0.12, 0.08, 0.06), 0.68, 0.0, 1.0),
    # Brass materials: metallic 1.0, roughness 0.3 to 0.4
    "Mat_Ottone":          ((0.62, 0.45, 0.20), 0.35, 1.0, 1.0),
    "Mat_OttoneScuro":     ((0.35, 0.24, 0.10), 0.38, 1.0, 1.0),
    # Glass materials: transmission or alpha
    "Mat_VetroOblo":       ((0.55, 0.70, 0.65), 0.15, 0.0, 0.65),
    "Mat_QuadranteVerde":  ((0.25, 0.55, 0.35), 0.18, 0.0, 0.75),
    # Organic / skin / hair / shells (no pure black 0.0 or pure white 1.0)
    "Mat_Pelle":           ((0.85, 0.68, 0.58), 0.58, 0.0, 1.0),
    "Mat_Labbra":          ((0.62, 0.36, 0.32), 0.52, 0.0, 1.0),
    "Mat_OcchioBianco":    ((0.90, 0.88, 0.86), 0.20, 0.0, 1.0),
    "Mat_Iride":           ((0.20, 0.12, 0.08), 0.18, 0.0, 1.0),
    "Mat_Pupilla":         ((0.06, 0.05, 0.05), 0.15, 0.0, 1.0),
    "Mat_CapelliScuri":    ((0.10, 0.08, 0.07), 0.75, 0.0, 1.0),
    "Mat_CapelliBianchi":  ((0.80, 0.80, 0.78), 0.68, 0.0, 1.0),
    "Mat_Conchiglia":      ((0.88, 0.85, 0.78), 0.55, 0.0, 1.0),
}

for mname, (rgb, rough, metal, alpha) in mat_rules.items():
    m = bpy.data.materials.get(mname)
    if m and m.use_nodes:
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            bsdf.inputs["Metallic"].default_value = metal
            if alpha < 1.0:
                if "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = alpha
                if "Transmission Weight" in bsdf.inputs:
                    bsdf.inputs["Transmission Weight"].default_value = 0.55

# ------------------------------------------------------------------------------
# 2. GROUP 10.2 & 10.4 - Recalculate normals outside, shading, and triangle budget (< 40,000)
# ------------------------------------------------------------------------------
mesh_objects = [o for o in scn.objects if o.type == 'MESH' and not o.name.startswith("_gara")]

for obj in mesh_objects:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = True
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

# Check total triangles and log per object (10.4)
log("=== CONTEGGIO TRIANGOLI PER OGGETTO (Group 10.4) ===")
total_tris = 0
obj_tri_list = []
for obj in sorted(mesh_objects, key=lambda x: x.name):
    obj.data.calc_loop_triangles()
    t_count = len(obj.data.loop_triangles)
    total_tris += t_count
    obj_tri_list.append((obj, t_count))

# If total_tris > 39500, decimate only small round pieces (rivets, rope, laces) as instructed in 10.4
if total_tris > 39500:
    excess = total_tris - 37500
    for r_name in ("Corda_Fianco_DX", "Tubi_Casco", "Lacci_Stivale_SX", "Lacci_Stivale_DX", "Casco_Palombaro"):
        ro = bpy.data.objects.get(r_name)
        if ro and total_tris > 38500:
            ro.data.calc_loop_triangles()
            before_t = len(ro.data.loop_triangles)
            mod = ro.modifiers.new(name="Opt_10_4", type='DECIMATE')
            mod.decimate_type = 'COLLAPSE'
            mod.ratio = 0.72
            with bpy.context.temp_override(object=ro, active_object=ro, selected_objects=[ro], selected_editable_objects=[ro]):
                bpy.ops.object.modifier_apply(modifier=mod.name)
            ro.data.calc_loop_triangles()
            after_t = len(ro.data.loop_triangles)
            total_tris -= (before_t - after_t)

total_tris = 0
for obj in sorted(mesh_objects, key=lambda x: x.name):
    obj.data.calc_loop_triangles()
    t_count = len(obj.data.loop_triangles)
    total_tris += t_count
    log(f"  {obj.name}: {t_count} triangoli")
log(f"TOTALE TRIANGOLI PERSONAGGIO: {total_tris} (limite massimo: 40.000)")

# ------------------------------------------------------------------------------
# 3. GROUP 10.5 & 10.6 - Skeleton with exact bone names and binding
# ------------------------------------------------------------------------------
arm_obj = bpy.data.objects.get("Armature")
if not arm_obj:
    arm_data = bpy.data.armatures.new("Armature_Data")
    arm_obj = bpy.data.objects.new("Armature", arm_data)
    scn.collection.objects.link(arm_obj)

arm_obj.location = (0.0, 0.0, 0.0)
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
ebones = arm_obj.data.edit_bones
for b in list(ebones):
    ebones.remove(b)

bone_specs = [
    ("Hips",       None,         False, (0.000,  0.000, 0.950), (0.000,  0.000, 1.100)),
    ("Spine",      "Hips",       True,  (0.000,  0.000, 1.100), (0.000,  0.000, 1.270)),
    ("Chest",      "Spine",      True,  (0.000,  0.000, 1.270), (0.000,  0.000, 1.450)),
    ("Neck",       "Chest",      True,  (0.000,  0.000, 1.450), (0.000,  0.000, 1.500)),
    ("Head",       "Neck",       True,  (0.000,  0.000, 1.500), (0.000,  0.000, 1.700)),

    ("Shoulder.L", "Chest",      False, (0.040,  0.000, 1.430), (0.190,  0.000, 1.400)),
    ("UpperArm.L", "Shoulder.L", True,  (0.190,  0.000, 1.400), (0.380,  0.000, 1.180)),
    ("LowerArm.L", "UpperArm.L", True,  (0.380,  0.000, 1.180), (0.540,  0.000, 0.990)),
    ("Hand.L",     "LowerArm.L", True,  (0.540,  0.000, 0.990), (0.605,  0.000, 0.920)),

    ("Shoulder.R", "Chest",      False, (-0.040, 0.000, 1.430), (-0.190, 0.000, 1.400)),
    ("UpperArm.R", "Shoulder.R", True,  (-0.190, 0.000, 1.400), (-0.380, 0.000, 1.180)),
    ("LowerArm.R", "UpperArm.R", True,  (-0.380, 0.000, 1.180), (-0.540, 0.000, 0.990)),
    ("Hand.R",     "LowerArm.R", True,  (-0.540, 0.000, 0.990), (-0.605, 0.000, 0.920)),

    ("UpperLeg.L", "Hips",       False, (0.100,  0.000, 0.900), (0.115,  0.000, 0.490)),
    ("LowerLeg.L", "UpperLeg.L", True,  (0.115,  0.000, 0.490), (0.130,  0.000, 0.080)),
    ("Foot.L",     "LowerLeg.L", True,  (0.130,  0.000, 0.080), (0.130, -0.100, 0.030)),
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

def dist_pt_seg(pt, a, b):
    ab = b - a
    lsq = ab.length_squared
    if lsq < 1e-8:
        return (pt - a).length
    t = max(0.0, min(1.0, (pt - a).dot(ab) / lsq))
    return (pt - (a + ab * t)).length

bone_segs = {bname: (Vector(h_co), Vector(t_co)) for bname, _, _, h_co, t_co in bone_specs}

# Explicit rigid/semi-rigid bindings per 10.6:
# - helmet, hoses, bedroll and back straps follow Chest bone (weight 1.0 to Chest)
# - pouches, rope and map tube follow Hips bone
# - bracer follows LowerArm.L
rigid_chest_objs = {"Casco_Palombaro", "Tubi_Casco", "Sacca_Arrotolata", "Cinghie_Petto", "Fibbie_Petto", "Conchiglie_SX", "Mantella_Colletto"}
rigid_hips_objs = {"Corda_Fianco_DX", "Borraccia_DX", "Tasca_Tonda_DX", "Astuccio_SX", "Lembo_Stoffa_SX", "Tasche_Cintura", "Cinture_Vita", "Fibbie_Vita", "Medaglione_Cintura", "Bacino_Pantaloni"}
rigid_head_objs = {"Testa", "Occhi", "Sopracciglia", "Labbra", "Orecchie", "Capelli_Scuri", "Ciocca_Bianca"}

for obj in mesh_objects:
    obj.parent = arm_obj
    # Ensure single Armature modifier
    for mod in list(obj.modifiers):
        if mod.type == 'ARMATURE':
            obj.modifiers.remove(mod)
    amod = obj.modifiers.new(name="Armature", type='ARMATURE')
    amod.object = arm_obj

    obj.vertex_groups.clear()
    vgs = {bname: obj.vertex_groups.new(name=bname) for bname, _, _, _, _ in bone_specs}
    all_idx = [v.index for v in obj.data.vertices]

    if obj.name in rigid_chest_objs:
        vgs["Chest"].add(all_idx, 1.0, 'REPLACE')
    elif obj.name in rigid_hips_objs:
        vgs["Hips"].add(all_idx, 1.0, 'REPLACE')
    elif obj.name in rigid_head_objs:
        vgs["Head"].add(all_idx, 1.0, 'REPLACE')
    elif obj.name == "Strumento_Polso_SX":
        vgs["LowerArm.L"].add(all_idx, 1.0, 'REPLACE')
    elif obj.name in ("Collo", "Camicia_Colletto"):
        for v in obj.data.vertices:
            w_n = max(0.0, min(1.0, (v.co.z - 1.40) / 0.08))
            vgs["Neck"].add([v.index], w_n, 'REPLACE')
            vgs["Chest"].add([v.index], 1.0 - w_n, 'REPLACE')
    elif obj.name in ("Manica_SX", "Guanto_SX", "Cinturini_Guanto_SX", "Mano_SX",
                      "Manica_DX", "Guanto_DX", "Cinturini_Guanto_DX", "Mano_DX",
                      "Mantella_Spalla_SX", "Mantella_Spalla_DX"):
        side_tag = "L" if "SX" in obj.name else "R"
        if obj.name.startswith("Mano_"):
            vgs[f"Hand.{side_tag}"].add(all_idx, 1.0, 'REPLACE')
        elif obj.name.startswith("Mantella_Spalla_"):
            for v in obj.data.vertices:
                d_sh = dist_pt_seg(v.co, *bone_segs[f"Shoulder.{side_tag}"])
                d_ua = dist_pt_seg(v.co, *bone_segs[f"UpperArm.{side_tag}"])
                w_sh = 1.0 / ((d_sh + 0.02) ** 2.5)
                w_ua = 1.0 / ((d_ua + 0.02) ** 2.5)
                tot = w_sh + w_ua
                vgs[f"Shoulder.{side_tag}"].add([v.index], w_sh / tot, 'REPLACE')
                vgs[f"UpperArm.{side_tag}"].add([v.index], w_ua / tot, 'REPLACE')
        else:
            arm_bnames = [f"Shoulder.{side_tag}", f"UpperArm.{side_tag}", f"LowerArm.{side_tag}", f"Hand.{side_tag}"]
            for v in obj.data.vertices:
                ws = []
                for bn in arm_bnames:
                    d = dist_pt_seg(v.co, *bone_segs[bn])
                    ws.append((bn, 1.0 / ((d + 0.015) ** 3.5)))
                ws.sort(key=lambda x: x[1], reverse=True)
                top2 = ws[:2]
                tot = sum(w for _, w in top2)
                for bn, w in top2:
                    vgs[bn].add([v.index], w / tot, 'REPLACE')
    elif obj.name in ("Pantalone_SX", "Fascia_Gamba_SX", "Stivale_SX", "Lacci_Stivale_SX",
                      "Pantalone_DX", "Fascia_Gamba_DX", "Stivale_DX", "Lacci_Stivale_DX", "Ginocchiere"):
        for v in obj.data.vertices:
            side_tag = "L" if v.co.x >= 0 else "R"
            leg_bnames = [f"UpperLeg.{side_tag}", f"LowerLeg.{side_tag}", f"Foot.{side_tag}", f"Toes.{side_tag}"]
            ws = []
            for bn in leg_bnames:
                d = dist_pt_seg(v.co, *bone_segs[bn])
                ws.append((bn, 1.0 / ((d + 0.015) ** 3.5)))
            ws.sort(key=lambda x: x[1], reverse=True)
            top2 = ws[:2]
            tot = sum(w for _, w in top2)
            for bn, w in top2:
                vgs[bn].add([v.index], w / tot, 'REPLACE')
    else:
        # Giacca_Torso and Mantella_Corpo follow torso & leg bones (never pulled by arms/hands)
        torso_leg_bnames = ["Hips", "Spine", "Chest", "Shoulder.L", "Shoulder.R", "UpperLeg.L", "LowerLeg.L", "UpperLeg.R", "LowerLeg.R"]
        for v in obj.data.vertices:
            ws = []
            for bn in torso_leg_bnames:
                if bn.endswith(".L") and v.co.x < 0:
                    continue
                if bn.endswith(".R") and v.co.x > 0:
                    continue
                d = dist_pt_seg(v.co, *bone_segs[bn])
                ws.append((bn, 1.0 / ((d + 0.025) ** 3.0)))
            ws.sort(key=lambda x: x[1], reverse=True)
            top2 = ws[:2]
            tot = sum(w for _, w in top2)
            for bn, w in top2:
                vgs[bn].add([v.index], w / tot, 'REPLACE')

log(f"Ossa dello scheletro ({len(arm_obj.data.bones)}): " + ", ".join(b.name for b in arm_obj.data.bones))

# ------------------------------------------------------------------------------
# 4. GROUP 10.6 TEST: Rotate UpperArm.L by 30 degrees, render "rev_prova_osso"
#    with views fronte and tre_quarti, then put the bone back to 0!
# ------------------------------------------------------------------------------
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pbone = arm_obj.pose.bones.get("UpperArm.L")
if pbone:
    pbone.rotation_mode = 'XYZ'
    pbone.rotation_euler = (0.0, math.radians(30.0), 0.0)
    bpy.context.view_layer.update()

render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])

if pbone:
    pbone.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_mainfile()
render_viste("rev_10")
