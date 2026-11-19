import math
from mathutils import Vector, Matrix

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

corpo_join, mant_join, spalle_join = [], [], []
accessori = {}
corda_n = 0
laccio_n = {"L": 0, "R": 0}
tasca_n = 0
for o in list(bpy.data.objects):
    if o.type != 'MESH': continue
    if o.name == "Corpo":  # frammento gia' trasformato nel passo precedente
        corpo_join.append(o); continue
    if o.name == "Mantello":
        mn, mx = bb(o)
        (spalle_join if mn.z > 1.30 else mant_join).append(o); continue
    mn, mx = bb(o)
    cx, cy, cz = (mn + mx) / 2
    dx, dy, dz = mx - mn
    t = tris(o)
    mats = set(m.name for m in o.data.materials if m)
    s = "L" if cx >= 0 else "R"
    if t > 3000 or len(mats) >= 3:
        for v in o.data.vertices: v.co = body_tf(Vector(v.co))
        o.data.update()
        corpo_join.append(o); continue
    if mats <= {"Mantello", "MantelloInt"}:
        if t > 500 and mn.z < 1.0: mant_join.append(o)
        elif t > 200 and mn.z > 1.2: spalle_join.append(o)
        elif mn.z > 1.30: spalle_join.append(o)
        else: mant_join.append(o)
        continue
    nm = None
    if "Capelli" in mats: nm = "Capelli" if dz > 0.08 else "Sopracciglio." + s
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
    accessori[nm] = o
    if nm in {"Capelli", "Ciuffo", "Occhio.L", "Occhio.R", "Sopracciglio.L", "Sopracciglio.R", "Naso", "Bocca"}:
        for v in o.data.vertices: v.co = head_tf(Vector(v.co))
    elif nm in {"Bracciale.L", "Bracciale.R", "Gauge", "Mano.L", "Mano.R"}:
        sd = 1 if cx >= 0 else -1
        for v in o.data.vertices: v.co = MARM[sd] @ Vector(v.co)
    elif nm.startswith(("Stivale.", "Laccio.", "Ginocchiera.", "Fascia.")):
        for v in o.data.vertices: v.co = leg_tf(Vector(v.co))
    o.data.update()

def join(lst, name):
    if not lst: return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in lst: o.select_set(True)
    bpy.context.view_layer.objects.active = lst[0]
    if len(lst) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    return ob

corpo = join(corpo_join, "Corpo")
mant = join(mant_join, "Mantello")
spalle = join(spalle_join, "MantelloSpalle")
log("Corpo tri", tris(corpo), "| Mantello tri", tris(mant), "| Spalle tri", tris(spalle))
log("Accessori:", len(accessori))
for nm in sorted(accessori): log("  %s tri %d" % (nm, tris(accessori[nm])))
zs = [v.co.z for v in corpo.data.vertices]
log("Corpo zmin %.3f zmax %.3f" % (min(zs), max(zs)))
bpy.ops.wm.save_mainfile()
render_viste("rev_1")
