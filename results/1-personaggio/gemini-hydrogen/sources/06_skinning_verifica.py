import bpy
import bmesh
from mathutils import Vector

LAVORO = r"C:\Users\USER\gara-modelli\concorrenti\gemini-hydrogen\lavoro"
blend_path = LAVORO + r"\personaggio.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

# 0. Pulizia duplicati da esecuzioni ripetute degli step precedenti
old_guanti = bpy.data.objects.get("GuantiBussola")
if old_guanti:
    bpy.data.objects.remove(old_guanti, do_unlink=True)

for base_name in ("TunicaManiche", "Pantaloni", "StivaliGinocchiera", "MantelloVerde",
                  "MantelloDettagli", "CinturaCinghie", "AccessoriDestra", "TuboMappe_L"):
    newer = bpy.data.objects.get(base_name + ".001")
    older = bpy.data.objects.get(base_name)
    if newer and older:
        bpy.data.objects.remove(older, do_unlink=True)
        newer.name = base_name

# 1. Rimuovi facce nascoste di CorpoBase sotto il collo (z < 1.38) per evitare poke-through
body = bpy.data.objects.get("CorpoBase")
if body:
    bm = bmesh.new()
    bm.from_mesh(body.data)
    faces_del = [f for f in bm.faces if f.calc_center_median().z < 1.38]
    bmesh.ops.delete(bm, geom=faces_del, context='FACES')
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()

# 2. Rifinisci vetro oblò e aggiungi variazione procedurale a mantello e pelle
mat_glass = bpy.data.materials.get("VetroOblo")
if mat_glass and mat_glass.use_nodes:
    bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.04, 0.08, 0.09, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.08
        bsdf.inputs["Metallic"].default_value = 0.15

def add_fabric_noise(mat_name, col_a, col_b, scale=18.0):
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if not bsdf:
        return
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 6.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*col_a, 1.0)
    ramp.color_ramp.elements[1].position = 0.70
    ramp.color_ramp.elements[1].color = (*col_b, 1.0)
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

add_fabric_noise("MantelloVerde", (0.16, 0.28, 0.24), (0.26, 0.38, 0.33), scale=14.0)
add_fabric_noise("TunicaBluGrigia", (0.09, 0.14, 0.18), (0.14, 0.19, 0.24), scale=20.0)

# 3. Collegamento all'Armatura (Skinning)
arm = bpy.data.objects.get("Armatura")
if not arm:
    raise RuntimeError("Armatura non trovata!")

# Assicura che tutte le trasformazioni siano applicate prima dello skinning
bpy.context.view_layer.objects.active = arm
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.parent = None
        for mod in list(obj.modifiers):
            if mod.type == 'ARMATURE':
                obj.modifiers.remove(mod)
        obj.vertex_groups.clear()

organic_meshes = [
    "CorpoBase", "TunicaManiche", "Pantaloni", "StivaliGinocchiera",
    "Guanti", "MantelloVerde", "MantelloDettagli", "CinturaCinghie"
]

rigid_bindings = {
    "DettagliVolto": "Head",
    "Capelli": "Head",
    "BussolaPolso_L": "Forearm_L",
    "CascoPalombaro": "Chest",
    "ZainoTubi": "Chest",
    "AccessoriDestra": "Pelvis",
    "TuboMappe_L": "Pelvis",
}

def point_seg_dist(p, a, b):
    ab = b - a
    l2 = ab.length_squared
    if l2 < 1e-8:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
    proj = a + ab * t
    return (p - proj).length

bone_segs = {b.name: (arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local) for b in arm.data.bones}

def bind_smooth_weights(obj, allowed_bones=None, split_legs=False):
    obj.parent = arm
    mod = obj.modifiers.new("Armatura", 'ARMATURE')
    mod.object = arm
    vgs = {bname: obj.vertex_groups.new(name=bname) for bname in bone_segs}
    for v in obj.data.vertices:
        wp = obj.matrix_world @ v.co
        weights = []
        for bname, (h, t) in bone_segs.items():
            if allowed_bones is not None and bname not in allowed_bones:
                continue
            if split_legs:
                if wp.x > 0.015 and bname.endswith("_R") and ("Thigh" in bname or "Shin" in bname or "Foot" in bname or "Toe" in bname):
                    continue
                if wp.x < -0.015 and bname.endswith("_L") and ("Thigh" in bname or "Shin" in bname or "Foot" in bname or "Toe" in bname):
                    continue
            d = point_seg_dist(wp, h, t)
            w = 1.0 / ((d + 0.015) ** 3.2)
            weights.append((w, bname))
        weights.sort(reverse=True)
        top4 = weights[:4]
        tot = sum(w for w, _ in top4)
        if tot > 0:
            for w, bname in top4:
                vgs[bname].add([v.index], w / tot, 'REPLACE')

body_bones = set(bone_segs.keys())
cape_bones = {"Pelvis", "Spine", "Chest", "Neck", "Shoulder_L", "Shoulder_R"}

for name in organic_meshes:
    obj = bpy.data.objects.get(name)
    if not obj:
        continue
    if name in ("MantelloVerde", "MantelloDettagli"):
        bind_smooth_weights(obj, allowed_bones=cape_bones, split_legs=False)
    else:
        bind_smooth_weights(obj, allowed_bones=body_bones, split_legs=True)

# Pesi rigidi 1.0 per testa e accessori
for name, bone_name in rigid_bindings.items():
    obj = bpy.data.objects.get(name)
    if not obj:
        continue
    obj.parent = arm
    mod = obj.modifiers.new("Armatura", 'ARMATURE')
    mod.object = arm
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')

# 4. Conteggio triangoli e verifica altezza
total_tris = 0
min_z, max_z = 999.0, -999.0
depsgraph = bpy.context.evaluated_depsgraph_get()
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        tris = len(me.loop_triangles)
        total_tris += tris
        for v in me.vertices:
            wz = (obj.matrix_world @ v.co).z
            if wz < min_z:
                min_z = wz
            if wz > max_z:
                max_z = wz
        ev.to_mesh_clear()
        log(f"  {obj.name}: {tris} triangoli")

log(f"TOTALE TRIANGOLI: {total_tris} (limite 40000)")
log(f"ALTEZZA: {max_z - min_z:.3f} m (da Z={min_z:.3f} a Z={max_z:.3f})")
log(f"OSSA ARMATURA: {len(arm.data.bones)} -> {[b.name for b in arm.data.bones]}")

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log("Salvato passo 06 in", blend_path)
render_viste("06_verifica", viste=["fronte", "destra", "retro", "tre_quarti"])
