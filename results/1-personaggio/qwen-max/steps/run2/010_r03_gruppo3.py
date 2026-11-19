import math, random
from mathutils import Vector

def clamp(v, a, b): return max(a, min(b, v))
random.seed(11)
O = bpy.data.objects

def clump(name, base, direction, length, thick, mat="Capelli", bend=0.25):
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(radius1=thick, radius2=thick * 0.2, depth=length, vertices=8, location=(0, 0, 0))
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(rotation=True)
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-4: side = Vector((1, 0, 0))
    side.normalize()
    for v in o.data.vertices:
        t = clamp((v.co.z + length / 2) / length, 0, 1)
        v.co += side * (bend * length * t * t)
    o.location = Vector(base) + d * (length / 2)
    bpy.ops.object.transform_apply(location=True)
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[mat])
    bpy.ops.object.shade_smooth()
    return o

# --- fix capelli: ciuffi pieni che seguono il cranio, non aculei ---
HC = Vector((0, 0.005, 1.60))
n = 40
for k in range(8):  # lati pieni, quasi verticali verso il basso
    sx = 1 if k % 2 == 0 else -1
    y = -0.05 + (k // 2) * 0.035
    base = HC + Vector((sx * 0.070, y, 0.055))
    d = Vector((sx * 0.22, 0.05, -1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.09, 0.12), random.uniform(0.016, 0.022)); n += 1
for k in range(6):  # nuca piena
    x = -0.05 + k * 0.02
    base = HC + Vector((x, 0.075, 0.05))
    d = Vector((0.08 * (k - 2.5), 0.22, -1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.09, 0.12), random.uniform(0.016, 0.022)); n += 1
for k in range(6):  # volume sopra, onda irregolare
    a = math.radians(k * 60 + 25)
    base = HC + Vector((0.045 * math.cos(a), 0.055 * math.sin(a), 0.075))
    d = Vector((0.35 * math.cos(a), 0.35 * math.sin(a), 1.0))
    clump("Ciuffo.%02d" % n, base, d, random.uniform(0.045, 0.06), random.uniform(0.016, 0.022)); n += 1
hair = O["Capelli"]
for v in hair.data.vertices:
    v.co.x *= 1.05; v.co.y *= 1.05
hair.data.update()
log("Ciuffi totali:", n)

def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

mat("Colletto", (0.30, 0.33, 0.38), 0.9)
bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.05, vertices=14, location=(0, 0, 1.435))
col = bpy.context.active_object
col.name = "CollettoCamicia"
col.data.materials.clear(); col.data.materials.append(bpy.data.materials["Colletto"])
bpy.ops.object.shade_smooth()

# colletto alto del mantello: arco aperto davanti, svasato
cols, rows = 17, 4
verts, faces = [], []
for i in range(rows):
    t = i / (rows - 1)
    for j in range(cols):
        th = math.radians(-140 + 280 * j / (cols - 1))
        back = clamp(1 - abs(th) / math.radians(140), 0, 1)
        h = 0.08 + 0.04 * back
        r = 0.075 + 0.022 * t
        z = 1.40 + t * h
        verts.append((r * math.sin(th), r * math.cos(th), z))
for i in range(rows - 1):
    for j in range(cols - 1):
        a = i * cols + j
        faces.append((a, a + 1, a + 1 + cols, a + cols))
me = bpy.data.meshes.new("CollettoMantello")
me.from_pydata(verts, [], faces); me.update()
ob = bpy.data.objects.new("CollettoMantello", me)
bpy.context.scene.collection.objects.link(ob)
ob.data.materials.append(bpy.data.materials["Mantello"])
sol = ob.modifiers.new("Sol", 'SOLIDIFY'); sol.thickness = 0.006
bpy.context.view_layer.objects.active = ob
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.object.shade_smooth()
bpy.ops.wm.save_mainfile()
render_viste("rev_3", viste=["fronte", "tre_quarti", "destra"])
