import math
from mathutils import Vector

def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

mat("Pelle", (0.75, 0.57, 0.47), 0.6)
mat("Tunica", (0.12, 0.15, 0.21), 0.85)
mat("Manica", (0.55, 0.48, 0.38), 0.9)
mat("Pantaloni", (0.22, 0.15, 0.10), 0.9)
mat("Stivali", (0.13, 0.09, 0.06), 0.7)
mat("Cuoio", (0.28, 0.18, 0.10), 0.7)
mat("CuoioScuro", (0.16, 0.11, 0.07), 0.7)
mat("Corda", (0.62, 0.52, 0.36), 0.95)
mat("Mantello", (0.09, 0.32, 0.22), 0.9)
mat("MantelloInt", (0.68, 0.60, 0.44), 0.95)
mat("Ottone", (0.72, 0.50, 0.20), 0.35, 1.0)
mat("OttoneScuro", (0.45, 0.32, 0.14), 0.45, 1.0)
v = mat("Vetro", (0.7, 0.85, 0.9), 0.1)
v.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.25
if hasattr(v, "surface_render_method"):
    v.surface_render_method = 'BLENDED'
me = mat("Medusa", (0.2, 0.8, 1.0), 0.4)
nb = me.node_tree.nodes["Principled BSDF"]
nb.inputs["Emission Color"].default_value = (0.2, 0.8, 1.0, 1)
nb.inputs["Emission Strength"].default_value = 5.0
mat("Gomma", (0.07, 0.07, 0.08), 0.8)
mat("Capelli", (0.10, 0.08, 0.06), 0.85)
mat("Bianco", (0.85, 0.85, 0.82), 0.8)
mat("Occhi", (0.04, 0.04, 0.05), 0.4)
mat("Labbra", (0.45, 0.28, 0.25), 0.7)
mat("Guanti", (0.09, 0.09, 0.11), 0.8)
mat("Telo", (0.45, 0.45, 0.47), 0.95)

def box(name, loc, dim):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = dim
    return o

def cyl(name, loc, r, depth, rot=(0, 0, 0), verts=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return o

def limb(name, p1, p2, r1, r2):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d.length, vertices=12, location=(p1 + p2) / 2)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

def sphere(name, loc, r, seg=16, ring=8, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return o

parts = []
parts.append(box("bacino", (0, 0, 1.00), (0.30, 0.20, 0.18)))
t = cyl("torso", (0, 0, 1.22), 0.16, 0.34, verts=16)
t.scale = (1, 0.7, 1)
parts.append(t)
parts.append(box("spalle", (0, 0, 1.37), (0.40, 0.20, 0.14)))
parts.append(cyl("collo", (0, 0, 1.46), 0.05, 0.12))
parts.append(sphere("testa", (0, 0, 1.60), 0.095, scale=(0.9, 1.0, 1.05)))
for s, sx in (("L", 1), ("R", -1)):
    parts.append(limb("braccio." + s, (sx * 0.19, 0, 1.42), (sx * 0.30, 0, 1.16), 0.05, 0.042))
    parts.append(limb("avambraccio." + s, (sx * 0.30, 0, 1.16), (sx * 0.38, 0, 0.92), 0.042, 0.033))
    parts.append(limb("coscia." + s, (sx * 0.09, 0, 0.95), (sx * 0.10, 0, 0.50), 0.08, 0.058))
    parts.append(limb("polpaccio." + s, (sx * 0.10, 0, 0.50), (sx * 0.10, 0, 0.10), 0.058, 0.042))
    parts.append(box("piede." + s, (sx * 0.10, -0.05, 0.05), (0.09, 0.24, 0.09)))

bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[1]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
body = bpy.context.active_object
body.name = "Corpo"

mod = body.modifiers.new("Remesh", 'REMESH')
mod.mode = 'VOXEL'
mod.voxel_size = 0.02
mod.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=mod.name)
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
log("Tri dopo remesh:", tris)
if tris > 7000:
    dec = body.modifiers.new("Decimate", 'DECIMATE')
    dec.ratio = 7000.0 / tris
    bpy.ops.object.modifier_apply(modifier=dec.name)
    tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
log("Tri corpo:", tris)

body.data.materials.clear()
for nm in ("Pelle", "Tunica", "Manica", "Pantaloni"):
    body.data.materials.append(bpy.data.materials[nm])
for p in body.data.polygons:
    c = p.center
    if c.z >= 1.47:
        p.material_index = 0
    elif abs(c.x) > 0.16 and c.z > 0.90:
        p.material_index = 1 if c.z > 1.14 else 2
    elif c.z < 0.97:
        p.material_index = 3
    else:
        p.material_index = 1

render_viste("p02_corpo", viste=["fronte", "destra"])
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")