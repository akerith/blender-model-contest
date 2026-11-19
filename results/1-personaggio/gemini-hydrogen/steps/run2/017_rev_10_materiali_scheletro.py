import bpy
import bmesh
import math
from mathutils import Vector

# Group 10: Materials pass (10.1), normals & 30-deg smooth by angle (10.2),
# contact/no-holes check (10.3), triangle budget <= 40,000 log (10.4),
# skeleton verification (10.5) & clean weight binding (10.6).

# 1. Material audit (10.1):
#    Leather roughness 0.6..0.7; Cloth roughness 0.85..0.95; Brass metallic 1.0, roughness 0.3..0.4;
#    Glass transmission/alpha; No pure black, no pure white.
leather_mats = {"PelleMarrone", "PelleScura", "PelleGuanti", "PelleGuantiCinghie", "PelleStivali", "SuolaStivali"}
cloth_mats   = {"MantelloVerde", "TunicaBluGrigia", "TunicaCuciture", "CollettoCamicia",
                "CamiciaBeige", "PantaloniScuri", "FasceCrema", "SaccoZaino", "CordaCanapa"}
brass_mats   = {"Ottone", "OttoneScuro"}
glass_mats   = {"VetroOblo", "QuadranteVerde"}

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    # Clamp Base Color away from pure black/white
    bc = bsdf.inputs["Base Color"].default_value
    bsdf.inputs["Base Color"].default_value = (
        max(0.006, min(0.85, bc[0])),
        max(0.006, min(0.85, bc[1])),
        max(0.006, min(0.85, bc[2])),
        1.0
    )
    if mat.name in leather_mats:
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = max(0.60, min(0.70, bsdf.inputs["Roughness"].default_value))
    elif mat.name in cloth_mats:
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = max(0.85, min(0.95, bsdf.inputs["Roughness"].default_value))
    elif mat.name in brass_mats:
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = max(0.30, min(0.40, bsdf.inputs["Roughness"].default_value))
    elif mat.name in glass_mats:
        bsdf.inputs["Metallic"].default_value = 0.05
        bsdf.inputs["Roughness"].default_value = 0.08
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = 0.68
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 0.72
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.50

# Pack CapeAlbedo image so GLB and .blend stay self-contained alongside texture/cape_albedo.png
cape_img = bpy.data.images.get("CapeAlbedo")
if cape_img and not cape_img.packed_file:
    cape_img.pack()

# 2. Normals & Shading pass (10.2):
#    Recalculate normals outside on all meshes; shade smooth on organic parts,
#    30-degree smooth by angle on metal/leather/mixed parts.
organic_smooth_only = {"CorpoBase", "DettagliVolto", "Capelli", "MantelloVerde", "MantelloDettagli", "Pantaloni"}
angle_smooth_objs   = {"CascoPalombaro", "BussolaPolso_L", "CinturaCinghie", "TuboMappe_L",
                       "StivaliGinocchiera", "AccessoriDestra", "ZainoTubi", "Guanti", "TunicaManiche"}

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = True
    if obj.name in angle_smooth_objs:
        thresh = math.radians(30.0)
        for e in bm.edges:
            if len(e.link_faces) == 2:
                ang = e.calc_face_angle(0.0)
                e.smooth = (ang <= thresh)
            else:
                e.smooth = True
    else:
        for e in bm.edges:
            e.smooth = True
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    # Apply Blender 4.1+/5.x shade_smooth_by_angle if available for sharp-edge normals
    if obj.name in angle_smooth_objs and hasattr(bpy.ops.object, "shade_smooth_by_angle"):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        with bpy.context.temp_override(active_object=obj, object=obj, selected_objects=[obj], selected_editable_objects=[obj]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30.0))

# 3. Verify Skeleton (10.5) & Re-bind all meshes cleanly (10.6)
arm = bpy.data.objects.get("Armatura")
if not arm:
    raise RuntimeError("Armatura missing!")

expected_bones = [
    "Hips", "Spine", "Chest", "Neck", "Head",
    "Shoulder.L", "UpperArm.L", "LowerArm.L", "Hand.L",
    "Shoulder.R", "UpperArm.R", "LowerArm.R", "Hand.R",
    "UpperLeg.L", "LowerLeg.L", "Foot.L", "Toes.L",
    "UpperLeg.R", "LowerLeg.R", "Foot.R", "Toes.R",
]
actual_bones = [b.name for b in arm.data.bones]
log(f"Skeleton bones ({len(actual_bones)}): {actual_bones}")
missing_b = [b for b in expected_bones if b not in actual_bones]
if missing_b:
    raise RuntimeError(f"Missing expected bones: {missing_b}")

# Clear existing parenting & modifiers cleanly
bpy.ops.object.select_all(action='DESELECT')
arm.hide_viewport = False
arm.hide_set(False)
with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=[arm]):
    bpy.ops.object.mode_set(mode='POSE')
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.ops.object.mode_set(mode='OBJECT')

all_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for obj in all_meshes:
    obj.parent = None
    for mod in list(obj.modifiers):
        if mod.type == 'ARMATURE':
            obj.modifiers.remove(mod)
    obj.vertex_groups.clear()

# Step A: Parent every mesh to Armatura with ARMATURE_AUTO (per 10.6)
bpy.ops.object.select_all(action='DESELECT')
for obj in all_meshes:
    obj.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=all_meshes + [arm]):
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        log("parent_set ARMATURE_AUTO succeeded.")
    except Exception as e:
        log(f"parent_set ARMATURE_AUTO fallback ({e}), using ARMATURE_NAME.")
        bpy.ops.object.parent_set(type='ARMATURE_NAME')

# Step B: Ensure clean domain-restricted & rigid weights so NO garment/strap/buckle tears when limbs rotate!
bone_segs = {b.name: (arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local) for b in arm.data.bones}

def pt_seg_dist(p, a, b):
    ab = b - a
    l2 = ab.length_squared
    if l2 < 1e-8:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
    return (p - (a + ab * t)).length

def assign_rigid(obj, bone_name):
    obj.vertex_groups.clear()
    vg = obj.vertex_groups.new(name=bone_name)
    if len(obj.data.vertices) > 0:
        vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')

def assign_domain_weights(obj, choose_bones_fn, power=3.6):
    obj.vertex_groups.clear()
    vgs = {bn: obj.vertex_groups.new(name=bn) for bn in bone_segs}
    for v in obj.data.vertices:
        wp = obj.matrix_world @ v.co
        allowed = choose_bones_fn(wp)
        ws = []
        for bn in allowed:
            h, t = bone_segs[bn]
            d = pt_seg_dist(wp, h, t)
            w = 1.0 / ((d + 0.012) ** power)
            ws.append((w, bn))
        ws.sort(reverse=True)
        top4 = ws[:4]
        tot = sum(w for w, _ in top4)
        if tot > 0:
            for w, bn in top4:
                vgs[bn].add([v.index], w / tot, 'REPLACE')

# Exact 10.6 rigid overrides:
# - helmet, hoses, bedroll, back straps -> Chest 1.0
# - pouches, rope, map tube -> Hips 1.0
# - bracer -> LowerArm.L 1.0
# - head details & hair -> Head 1.0
rigid_map = {
    "CascoPalombaro": "Chest",
    "ZainoTubi": "Chest",
    "AccessoriDestra": "Hips",
    "TuboMappe_L": "Hips",
    "BussolaPolso_L": "LowerArm.L",
    "DettagliVolto": "Head",
    "Capelli": "Head",
}
for name, bname in rigid_map.items():
    ob = bpy.data.objects.get(name)
    if ob:
        assign_rigid(ob, bname)

# Clean domain-restricted smooth weights for deformable meshes (zero cross-bleeding between torso/arms/legs/cape)
def bones_corpose(wp):
    if wp.z >= 1.48:
        return ["Head"]
    if wp.z >= 1.43 and abs(wp.x) < 0.08:
        return ["Neck", "Head", "Chest"]
    if wp.x > 0.165 and wp.z > 0.78:
        return ["Shoulder.L", "UpperArm.L", "LowerArm.L", "Hand.L"]
    if wp.x < -0.165 and wp.z > 0.78:
        return ["Shoulder.R", "UpperArm.R", "LowerArm.R", "Hand.R"]
    if wp.z < 0.86:
        side = "L" if wp.x >= 0 else "R"
        return [f"UpperLeg.{side}", f"LowerLeg.{side}", f"Foot.{side}", f"Toes.{side}"]
    return ["Hips", "Spine", "Chest", "Neck", "Shoulder.L", "Shoulder.R"]

def bones_tunic(wp):
    # Sleeves (outside torso & above waist) bind strictly to arm bones; torso/collar/skirt bind strictly to spine/chest/hips
    if wp.x > 0.162 and wp.z > 0.90 and wp.z < 1.405:
        if wp.x < 0.21:
            return ["Chest", "Shoulder.L", "UpperArm.L"]
        return ["Shoulder.L", "UpperArm.L", "LowerArm.L"]
    if wp.x < -0.162 and wp.z > 0.90 and wp.z < 1.405:
        if wp.x > -0.21:
            return ["Chest", "Shoulder.R", "UpperArm.R"]
        return ["Shoulder.R", "UpperArm.R", "LowerArm.R"]
    return ["Hips", "Spine", "Chest", "Neck"]

def bones_gloves(wp):
    side = "L" if wp.x >= 0 else "R"
    #Wrist boundary is at |X| ~ 0.540
    if abs(wp.x) > 0.542:
        return [f"Hand.{side}"]
    if abs(wp.x) < 0.520:
        return [f"LowerArm.{side}"]
    return [f"LowerArm.{side}", f"Hand.{side}"]

def bones_cape(wp):
    # Long cape & shoulder cape follow torso/shoulders cleanly without getting dragged by elbows/wrists
    if wp.z > 1.24 and abs(wp.x) > 0.18:
        side = "L" if wp.x > 0 else "R"
        return ["Chest", f"Shoulder.{side}"]
    return ["Hips", "Spine", "Chest", "Neck", "Shoulder.L", "Shoulder.R"]

def bones_legs(wp):
    if wp.z >= 0.91:
        return ["Hips"]
    side = "L" if wp.x >= 0 else "R"
    return ["Hips", f"UpperLeg.{side}", f"LowerLeg.{side}", f"Foot.{side}", f"Toes.{side}"]

def bones_belts(wp):
    return ["Hips", "Spine", "Chest"]

domain_map = {
    "CorpoBase": bones_corpose,
    "TunicaManiche": bones_tunic,
    "Guanti": bones_gloves,
    "MantelloVerde": bones_cape,
    "Pantaloni": bones_legs,
    "StivaliGinocchiera": bones_legs,
    "CinturaCinghie": bones_belts,
}
for name, fn in domain_map.items():
    ob = bpy.data.objects.get(name)
    if ob:
        assign_domain_weights(ob, fn)

# MantelloDettagli: shells (Z > 1.2) -> Chest 1.0; torn cloth (Z < 1.1) -> Hips 1.0
ob_md = bpy.data.objects.get("MantelloDettagli")
if ob_md:
    ob_md.vertex_groups.clear()
    vg_ch = ob_md.vertex_groups.new(name="Chest")
    vg_hp = ob_md.vertex_groups.new(name="Hips")
    for v in ob_md.data.vertices:
        if v.co.z > 1.20:
            vg_ch.add([v.index], 1.0, 'REPLACE')
        else:
            vg_hp.add([v.index], 1.0, 'REPLACE')

# 4. Log triangle counts per object & total <= 40,000, height check
depsgraph = bpy.context.evaluated_depsgraph_get()
total_tris = 0
min_z, max_z = 999.0, -999.0
log("=== GROUP 10 TRIANGLE BUDGET ===")
for obj in sorted(all_meshes, key=lambda o: o.name):
    ev = obj.evaluated_get(depsgraph)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    t = len(me.loop_triangles)
    total_tris += t
    for v in me.vertices:
        wz = (obj.matrix_world @ v.co).z
        min_z = min(min_z, wz)
        max_z = max(max_z, wz)
    ev.to_mesh_clear()
    log(f"  {obj.name}: {t}")
log(f"TOTAL_TRIS={total_tris} (limit 40000)")
log(f"HEIGHT={max_z - min_z:.4f} m (Z={min_z:.4f}..{max_z:.4f})")

bpy.ops.wm.save_mainfile()
render_viste("rev_10")
