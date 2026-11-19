import math, random
import bmesh
from mathutils import Vector

def clamp(v, a, b): return max(a, min(b, v))
random.seed(5)
O = bpy.data.objects

# --- fix gruppo 5: gauge, cinghie guanto, cima capelli ---
g = O["Gauge"]
cs = [Vector(c) for c in g.bound_box]
cc = (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2
W = Vector((0.54, 0, 0.99)); f = Vector((0.644, 0, -0.765)); n = Vector((0.765, 0, 0.644))
target = W - f * 0.06 + n * 0.040
for v in g.data.vertices: v.co = Vector(v.co) - cc + target
g.data.update()
for s, sd in (("L", 1), ("R", -1)):
    Ws = Vector((sd * 0.54, 0, 0.99)); fs = Vector((sd * 0.644, 0, -0.765)); ns = Vector((sd * 0.765, 0, 0.644))
    for k, t in enumerate((0.02, 0.10, 0.19)):
        c = Ws - fs * t
        rr = 0.0375 + (0.0475 - 0.0375) * (t / 0.21)
        O["GuantoCinghia.%s.%d" % (s, k)].location = c
        O["GuantoFibbia.%s.%d" % (s, k)].location = c + ns * (rr + 0.006)
for o in O:
    if o.type == 'MESH' and (o.name.startswith("Ciuffo.") or o.name.startswith("CiuffoB.")):
        for v in o.data.vertices:
            if v.co.z > 1.66: v.co.z = 1.66 + (v.co.z - 1.66) * 0.6
        o.data.update()
log("Fix gauge/straps/capelli applicati")

# --- mantello lungo: rimappo la griglia esistente (non la ricostruisco) ---
mant = O["Mantello"]
rag = [random.choice([0.0, 0.05, 0.09, 0.13, 0.18]) for _ in range(29)]
me = mant.data
for v in me.vertices:
    x, y, z = v.co
    th = math.atan2(x, (y - 0.02) / 0.9)
    j = int(round((math.degrees(th) + 125) / 250 * 28))
    j = clamp(j, 0, 28)
    hem_old = 0.78 + 0.10 * abs(math.sin(j * 0.9))
    if j % 4 == 2: hem_old += 0.06
    if j in (5, 12, 20, 24): hem_old += 0.12
    t = clamp((1.45 - z) / (1.45 - hem_old), 0, 1.1)
    phi = th * (161.5 / 125.0)
    a = 0.20 + 0.35 * t ** 1.15
    b = 0.09 + 0.13 * clamp((t - 0.25) / 0.75, 0, 1) ** 1.15
    fold = 1 + 0.06 * math.sin(6 * phi) * t
    hem = 0.20 if abs(phi) < math.radians(90) else 0.25
    hem -= rag[j]
    zn = 1.45 - t * (1.45 - hem)
    xn = a * fold * math.sin(phi)
    yn = b * fold * math.cos(phi)
    yn += 0.06 * clamp((0.4 - t) / 0.4, 0, 1) * clamp((abs(phi) - 1.05) / 1.05, 0, 1)
    v.co = (xn, yn, zn)
me.update()
# buchi sopra l'orlo: elimino poche facce (reshape, non rebuild)
bm = bmesh.new(); bm.from_mesh(me)
kill = []
for fc in bm.faces:
    c = fc.calc_center_median()
    if c.z < 0.42 and c.z > 0.24 and abs(c.x) > 0.30:
        if int(abs(c.x) * 40) % 7 == 0: kill.append(fc)
bmesh.ops.delete(bm, geom=kill, context='FACES')
bm.to_mesh(me); bm.free(); me.update()
bpy.ops.object.select_all(action='DESELECT')
mant.select_set(True); bpy.context.view_layer.objects.active = mant
bpy.ops.object.shade_smooth()

# --- mantello spalle: stessa rimappa, orlo a punte ---
sp = O["MantelloSpalle"]
rag2 = [random.choice([0.0, 0.03, 0.06]) for _ in range(25)]
for v in sp.data.vertices:
    x, y, z = v.co
    th = math.atan2(x, y / 0.85)
    r = math.sqrt(x * x + (y / 0.85) ** 2)
    t = clamp((r - 0.10) / 0.13, 0, 1.1)
    j = int(round((math.degrees(th) + 150) / 300 * 24))
    j = clamp(j, 0, 24)
    hem = 1.20 if abs(th) < math.radians(90) else 1.24
    hem -= rag2[j]
    a = 0.10 + 0.24 * t
    b = 0.09 + 0.02 * t
    v.co = (a * math.sin(th), b * math.cos(th), 1.47 - t * (1.47 - hem))
sp.data.update()
bpy.ops.object.select_all(action='DESELECT')
sp.select_set(True); bpy.context.view_layer.objects.active = sp
bpy.ops.object.shade_smooth()

# --- materiale mantello: teal + striature + fade sabbia in basso ---
m = bpy.data.materials["Mantello"]
nt = m.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.9
for n in list(nt.nodes):
    if n != bsdf and n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6, 6, 0.6)
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.62
mix1 = nt.nodes.new("ShaderNodeMixRGB"); mix1.blend_type = 'MIX'
mix1.inputs["Color1"].default_value = (0.22, 0.34, 0.31, 1)
mix1.inputs["Color2"].default_value = (0.40, 0.52, 0.48, 1)
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value = 0.20; mr.inputs["From Max"].default_value = 0.45
mr.inputs["To Min"].default_value = 1.0; mr.inputs["To Max"].default_value = 0.0
nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 9
mix2 = nt.nodes.new("ShaderNodeMixRGB"); mix2.blend_type = 'MIX'
mix2.inputs["Color2"].default_value = (0.62, 0.55, 0.43, 1)
mix3 = nt.nodes.new("ShaderNodeMixRGB"); mix3.blend_type = 'MULTIPLY'
mix3.inputs["Color2"].default_value = (0.75, 0.68, 0.55, 1)
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], mix1.inputs["Fac"])
nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
nt.links.new(mix1.outputs["Color"], mix2.inputs["Color1"])
nt.links.new(mr.outputs["Result"], mix2.inputs["Fac"])
nt.links.new(nz2.outputs["Fac"], mix3.inputs["Fac"])
nt.links.new(mix2.outputs["Color"], mix3.inputs["Color1"])
nt.links.new(mix3.outputs["Color"], bsdf.inputs["Base Color"])

# conchiglie bianche sulla clavicola sinistra
mc = bpy.data.materials.new("Conchiglia"); mc.use_nodes = True
b = mc.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.88, 0.85, 0.78, 1)
b.inputs["Roughness"].default_value = 0.8
for k in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.013, segments=10, ring_count=6,
                                         location=(0.115 + 0.012 * k, -0.095 + 0.008 * k, 1.37 - 0.006 * k))
    o = bpy.context.active_object
    o.name = "Conchiglia.%d" % k
    o.scale = (1, 0.6, 0.8)
    o.data.materials.append(mc)
    bpy.ops.object.shade_smooth()
log("Mantello tri:", sum(len(p.vertices) - 2 for p in mant.data.polygons))
bpy.ops.wm.save_mainfile()
render_viste("rev_6", viste=["fronte", "retro", "destra", "tre_quarti"])
