import math
import bmesh
from mathutils import Vector

O = bpy.data.objects
def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m
mat("Pelle", (0.85, 0.68, 0.58), 0.6)
mat("Occhi", (0.09, 0.06, 0.04), 0.4)
mat("Capelli", (0.10, 0.08, 0.07), 0.85)
mat("Bianco", (0.80, 0.80, 0.78), 0.8)
mat("Tunica", (0.13, 0.16, 0.22), 0.9)
mat("Labbra", (0.35, 0.22, 0.20), 0.7)
mat("MantelloInt", (0.68, 0.60, 0.44), 0.95)
v = mat("Vetro", (0.55, 0.70, 0.65), 0.1)
v.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.35
if hasattr(v, "surface_render_method"): v.surface_render_method = 'BLENDED'

# ciuffo bianco piu' visibile da dietro
for n in O.keys():
    if n.startswith("CiuffoB.") or n == "Ciuffo":
        o = O[n]
        for vv in o.data.vertices:
            vv.co = Vector(vv.co) + Vector((0, 0.022, 0.012))
        o.data.update()

# vecchie cinghie -> harness posteriore verso il collare del casco
for s, sd in (("L", 1), ("R", -1)):
    o = O["Cinghia." + s]
    cs = [Vector(c) for c in o.bound_box]
    cc = (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2
    for vv in o.data.vertices:
        p = (Vector(vv.co) - cc) * Vector((1.2, 0.7, 0.75))
        vv.co = p + Vector((sd * 0.115, 0.13, 1.28))
    o.rotation_euler = (math.radians(20), 0, 0)
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials["Cuoio"])

# normali fuori + shading
ORGANIC = ("Corpo", "Capelli", "Ciuffo", "Mano.", "Mantello", "Corda", "Tubo", "Spirale", "Bedroll", "Orecchio", "TascaRotonda", "LoopCasco")
tot = 0
for o in O:
    if o.type != 'MESH': continue
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    if o.name.startswith(ORGANIC):
        bpy.ops.object.shade_smooth()
    else:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    t = sum(len(p.vertices) - 2 for p in o.data.polygons)
    tot += t
    log("TRI %s %d" % (o.name, t))
log("TRI TOTALI:", tot)

# scheletro: nomi esatti della specifica
arm = O["Scheletro"]
REN = {"pelvis": "Hips", "spine": "Spine", "chest": "Chest", "neck": "Neck", "head": "Head",
       "clavicle.L": "Shoulder.L", "upper_arm.L": "UpperArm.L", "forearm.L": "LowerArm.L", "hand.L": "Hand.L",
       "thigh.L": "UpperLeg.L", "shin.L": "LowerLeg.L", "foot.L": "Foot.L", "toes.L": "Toes.L",
       "clavicle.R": "Shoulder.R", "upper_arm.R": "UpperArm.R", "forearm.R": "LowerArm.R", "hand.R": "Hand.R",
       "thigh.R": "UpperLeg.R", "shin.R": "LowerLeg.R", "foot.R": "Foot.R", "toes.R": "Toes.R"}
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
for old, new in REN.items():
    arm.data.edit_bones[old].name = new
bpy.ops.object.mode_set(mode='OBJECT')
log("Ossa:", ", ".join(b.name for b in arm.data.bones))

# pulizia skin vecchia
for o in O:
    if o.type != 'MESH': continue
    for m in list(o.modifiers):
        if m.type == 'ARMATURE': o.modifiers.remove(m)
    o.vertex_groups.clear()
    o.parent = None

RIGID = {}
for n in O.keys():
    if n.startswith(("Casco", "Oblo", "Griglia", "Rivetto", "BandaCasco", "Valvola", "Tubo.", "TuboCosta", "Spirale", "Bedroll", "LoopCasco", "HarnessAttacco", "CinturaSchiena", "Bandoliera", "Cinghia.", "CollettoMantello")):
        RIGID[n] = "Chest"
    elif n.startswith(("Tasca", "Corda", "Contenitore", "Canister", "TuboMappe", "TuboSottile", "TelaStrappata", "Cintura", "Fibbia", "Medaglione", "Cordino", "Gonna")):
        RIGID[n] = "Hips"
    elif n.startswith(("Gauge",)):
        RIGID[n] = "LowerArm.L"
    elif n.startswith(("Manica.", "ManicaRollo")):
        RIGID[n] = "UpperArm." + n.split(".")[1]
    elif n.startswith(("Guanto",)):
        RIGID[n] = "LowerArm." + n.split(".")[1]
    elif n.startswith("Mano."):
        RIGID[n] = "Hand." + n.split(".")[1]
    elif n.startswith(("Capelli", "Ciuffo", "Occhio", "Sopracciglio", "Naso", "Bocca", "Orecchio")):
        RIGID[n] = "Head"
    elif n == "CollettoCamicia":
        RIGID[n] = "Neck"
AUTO = [n for n in O.keys() if O[n].type == 'MESH' and n not in RIGID]
for n, bone in RIGID.items():
    o = O[n]
    g = o.vertex_groups.new(name=bone)
    g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    md = o.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    o.parent = arm
for n in AUTO:
    o = O[n]
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
log("Auto weights su:", ", ".join(sorted(AUTO)))
bpy.ops.wm.save_mainfile()
render_viste("rev_10", viste=["fronte", "retro", "tre_quarti"])
