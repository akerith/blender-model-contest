import math
from mathutils import Vector, Matrix

SAVE = r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend"
# il file giro1 e' stato riaperto dal passo r01d_apri (contesto fresco)

def clamp(v, a, b): return max(a, min(b, v))
def prof(z, pts):
    if z <= pts[0][0]: return pts[0][1]
    for (z0, f0), (z1, f1) in zip(pts, pts[1:]):
        if z <= z1: return f0 + (f1 - f0) * (z - z0) / (z1 - z0)
    return pts[-1][1]

p = bpy.data.objects["Personaggio"]
bpy.ops.object.select_all(action='DESELECT')
p.select_set(True)
bpy.context.view_layer.objects.active = p
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

def bb(o):
    cs = [Vector(c) for c in o.bound_box]
    mn = Vector([min(c[i] for c in cs) for i in range(3)])
    mx = Vector([max(c[i] for c in cs) for i in range(3)])
    return mn, mx
def tris(o): return sum(len(q.vertices) - 2 for q in o.data.polygons)
def used(o): return set(o.data.materials[q.material_index].name for q in o.data.polygons if o.data.materials[q.material_index])

ANG = math.radians(19.8)
PIV = {1: Vector((0.19, 0, 1.40)), -1: Vector((-0.19, 0, 1.40))}
def armM(s):
    q = PIV[s]
    return Matrix.Translation(q) @ Matrix.Rotation(-s * ANG, 4, 'Y') @ Matrix.Scale(1.017, 4) @ Matrix.Translation(-q)
MARM = {1: armM(1), -1: armM(-1)}
def head_tf(v): return Vector((v.x * 0.877, v.y, 1.570 + (v.z - 1.586) * 0.925))
def leg_tf(v):
    if v.z < 0.92 and abs(v.x) < 0.25:
        return Vector((v.x + (1 if v.x >= 0 else -1) * 0.03 * (0.92 - v.z) / 0.84, v.y, v.z))
    return v
def body_tf(co):
    if co.z > 1.50: return head_tf(co)
    if co.z < 1.0 and abs(co.x) < 0.2:
        co.z -= 0.05 * clamp((1.0 - co.z) / 0.14, 0, 1)
    if 0.90 < co.z < 1.25 and abs(co.x) < 0.22 and abs(co.y) < 0.14:
        co.x *= prof(co.z, [(0.90, 1.08), (1.08, 0.845), (1.25, 1.0)])
        co.y *= prof(co.z, [(0.90, 1.10), (1.08, 0.80), (1.25, 1.0)])
    co = leg_tf(co)
    if 0.78 < co.z < 1.44 and abs(co.x) > 0.14:
        sd = 1 if co.x > 0 else -1
        w = clamp((abs(co.x) - 0.15) / 0.07, 0, 1)
        co = co.lerp(MARM[sd] @ co, w)
    return co

HEAD_PARTS = {"Capelli", "Ciuffo", "Occhio.L", "Occhio.R", "Sopracciglio.L", "Sopracciglio.R", "Naso", "Bocca"}
ARM_PARTS = {"Bracciale.L", "Bracciale.R", "Gauge", "Mano.L", "Mano.R"}
named = {}
corda_n = 0
laccio_n = {"L": 0, "R": 0}
tasca_n = 0
for o in [x for x in bpy.data.objects if x.type == 'MESH']:
    mn, mx = bb(o)
    cx, cy, cz = (mn + mx) / 2
    dx, dy, dz = mx - mn
    t = tris(o)
    mats = used(o)
    s = "L" if cx >= 0 else "R"
    nm = None
    if t > 3000: nm = "Corpo"
    elif "MantelloInt" in mats and t > 500: nm = "Mantello"
    elif mats == {"Mantello"} and t > 200: nm = "MantelloSpalle"
    elif "Capelli" in mats: nm = "Capelli" if dz > 0.08 else "Sopracciglio." + s
    elif "Bianco" in mats: nm = "Ciuffo"
    elif "Occhi" in mats: nm = "Occhio." + s
    elif "Pelle" in mats: nm = "Naso"
    elif "Labbra" in mats: nm = "Bocca"
    elif "Guanti" in mats: nm = "Mano." + s
    elif "Gomma" in mats: nm = "Tubo." + s
    elif "Vetro" in mats: nm = "ObloVetro"
    elif "Corda" in mats:
        corda_n += 1; nm = "Corda%d" % corda_n
    elif "Stivali" in mats: nm = "Stivale." + s
    elif "Manica" in mats: nm = "Fascia." + s
    elif "Cuoio" in mats: nm = "Cintura" if dx > 0.2 else "Ginocchiera." + s
    elif "CuoioScuro" in mats:
        if mx.z > 1.2: nm = "Cinghia." + s
        elif mx.z < 0.4:
            laccio_n[s] += 1; nm = "Laccio.%s.%d" % (s, laccio_n[s])
        elif abs(cx) > 0.25: nm = "Bracciale." + s
        else:
            tasca_n += 1; nm = "Tasca.%d" % tasca_n
    elif "Ottone" in mats:
        if max(dx, dy, dz) > 0.2: nm = "Casco"
        elif mn.y > 0.3:
            if dx > 0.05 and dz > 0.05: nm = "Oblo"
            elif dz > 0.05: nm = "GrigliaV"
            else: nm = "GrigliaO"
        elif mx.z > 1.3: nm = "Chiusura"
        elif abs(cx) > 0.2: nm = "Gauge"
        else: nm = "Fibbia"
    elif "OttoneScuro" in mats:
        if mx.z > 1.35: nm = "ValvolaAlta"
        elif mx.z > 1.1 and dx > 0.15: nm = "CascoCollare"
        elif abs(cx) > 0.05: nm = "Valvola." + s
        else: nm = "Contenitore"
    if nm is None: nm = "Pezzo.%s" % o.name
    o.name = nm
    named[nm] = o
    if nm == "Corpo":
        for v in o.data.vertices: v.co = body_tf(Vector(v.co))
    elif nm in HEAD_PARTS:
        for v in o.data.vertices: v.co = head_tf(Vector(v.co))
    elif nm in ARM_PARTS:
        sd = 1 if cx >= 0 else -1
        for v in o.data.vertices: v.co = MARM[sd] @ Vector(v.co)
    elif nm.startswith(("Stivale.", "Laccio.", "Ginocchiera.", "Fascia.")):
        for v in o.data.vertices: v.co = leg_tf(Vector(v.co))
    o.data.update()

log("Pezzi:", len(named))
for nm in sorted(named): log("  %s tri %d" % (nm, tris(named[nm])))

arm = bpy.data.objects["Scheletro"]
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
POS = {
    "pelvis": ((0, 0, 0.95), (0, 0, 1.08)),
    "spine": ((0, 0, 1.08), (0, 0, 1.22)),
    "chest": ((0, 0, 1.22), (0, 0, 1.45)),
    "neck": ((0, 0, 1.45), (0, 0, 1.50)),
    "head": ((0, 0, 1.50), (0, 0, 1.70)),
}
for sd, s in (("L", 1), ("R", -1)):
    POS["clavicle." + sd] = ((s * 0.03, 0, 1.45), (s * 0.19, 0, 1.40))
    POS["upper_arm." + sd] = ((s * 0.19, 0, 1.40), (s * 0.38, 0, 1.18))
    POS["forearm." + sd] = ((s * 0.38, 0, 1.18), (s * 0.54, 0, 0.99))
    POS["hand." + sd] = ((s * 0.54, 0, 0.99), (s * 0.615, 0, 0.905))
    POS["thigh." + sd] = ((s * 0.11, 0, 0.90), (s * 0.125, 0, 0.49))
    POS["shin." + sd] = ((s * 0.125, 0, 0.49), (s * 0.13, 0, 0.08))
    POS["foot." + sd] = ((s * 0.13, 0, 0.08), (s * 0.13, -0.10, 0.02))
for nm, (h, t) in POS.items():
    eb[nm].head = h; eb[nm].tail = t
for sd, s in (("L", 1), ("R", -1)):
    b = eb.new("toes." + sd)
    b.head = (s * 0.13, -0.10, 0.02); b.tail = (s * 0.13, -0.19, 0.02)
    b.parent = eb["foot." + sd]
bpy.ops.object.mode_set(mode='OBJECT')
log("Ossa:", len(arm.data.bones))
zs = [v.co.z for v in named["Corpo"].data.vertices]
log("Corpo zmin %.3f zmax %.3f" % (min(zs), max(zs)))
bpy.ops.wm.save_as_mainfile(filepath=SAVE)
render_viste("rev_1")
