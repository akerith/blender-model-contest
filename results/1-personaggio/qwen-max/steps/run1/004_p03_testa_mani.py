import math
import bmesh
from mathutils import Vector

def box(name, loc, dim, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = dim
    return o

def cyl(name, loc, r, depth, rot=(0, 0, 0), verts=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o

def sphere(name, loc, r, seg=16, ring=8, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return o

def setmat(o, nm):
    o.data.materials.clear()
    o.data.materials.append(bpy.data.materials[nm])

hair = sphere("Capelli", (0, 0.005, 1.615), 0.10, scale=(0.92, 1.02, 1.0))
bm = bmesh.new()
bm.from_mesh(hair.data)
for v in list(bm.verts):
    wz = 1.615 + v.co.z
    wy = 0.005 + v.co.y * 1.02
    if wz < 1.60 or (wy < -0.045 and wz < 1.665):
        bm.verts.remove(v)
bm.to_mesh(hair.data)
bm.free()
sol = hair.modifiers.new("Sol", 'SOLIDIFY')
sol.thickness = 0.012
bpy.ops.object.modifier_apply(modifier=sol.name)
setmat(hair, "Capelli")
hair["bone"] = "head"

streak = box("Ciuffo", (0.04, -0.085, 1.66), (0.02, 0.03, 0.06), (0, math.radians(-10), 0))
setmat(streak, "Bianco")
streak["bone"] = "head"

for s, sx in (("L", 1), ("R", -1)):
    e = sphere("Occhio." + s, (sx * 0.035, -0.088, 1.62), 0.012, seg=8, ring=6)
    setmat(e, "Occhi")
    e["bone"] = "head"
    b = box("Sopracciglio." + s, (sx * 0.035, -0.092, 1.645), (0.025, 0.008, 0.006))
    setmat(b, "Capelli")
    b["bone"] = "head"

nose = cyl("Naso", (0, -0.098, 1.60), 0.008, 0.025, rot=(math.radians(-90), 0, 0), verts=8)
setmat(nose, "Pelle")
nose["bone"] = "head"
mouth = box("Bocca", (0, -0.092, 1.565), (0.02, 0.006, 0.005))
setmat(mouth, "Labbra")
mouth["bone"] = "head"

for s, sx in (("L", 1), ("R", -1)):
    d = Vector((sx * 0.05, 0, -0.13))
    palm = box("Palmo." + s, (sx * 0.405, 0, 0.855), (0.05, 0.06, 0.11))
    palm.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    thumb = box("Pollice." + s, (sx * 0.375, -0.03, 0.88), (0.02, 0.03, 0.05))
    bpy.ops.object.select_all(action='DESELECT')
    palm.select_set(True)
    thumb.select_set(True)
    bpy.context.view_layer.objects.active = palm
    bpy.ops.object.join()
    hand = bpy.context.active_object
    hand.name = "Mano." + s
    setmat(hand, "Guanti")
    hand["bone"] = "hand." + s

    fd = Vector((sx * 0.08, 0, -0.24)).normalized()
    br = cyl("Bracciale." + s, (sx * 0.34, 0, 1.04), 0.046, 0.13, verts=12)
    br.rotation_euler = fd.to_track_quat('Z', 'Y').to_euler()
    setmat(br, "CuoioScuro")
    br["bone"] = "forearm." + s

gauge = cyl("Gauge", (0.40, -0.045, 0.94), 0.022, 0.018, rot=(math.radians(90), 0, 0), verts=12)
setmat(gauge, "Ottone")
gauge["bone"] = "hand.L"

render_viste("p03_testa", viste=["fronte", "tre_quarti"])
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")