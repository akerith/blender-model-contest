import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# FINAL FACE & WAVY HAIR SILHOUETTE POLISH + DELIVERY (D1, D2, D3)
# ==============================================================================

scn = bpy.context.scene
o_head = bpy.data.objects.get("Testa")

def exact_face_y(x_q, z_q):
    near = [v.co.y for v in o_head.data.vertices if v.co.y < 0.0 and abs(v.co.x - x_q) < 0.013 and abs(v.co.z - z_q) < 0.011]
    if near:
        return min(near)
    return -0.072

# 1. Make Occhi (Z=1.585, 0.065 apart, 0.03 wide) super clear, with full dark-brown iris and crisp upper lash arch
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        cx_e = sx * 0.0325
        cz_e = 1.585
        # White sclera (0.030 wide, 0.013 high)
        ret_w = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
        for v in ret_w["verts"]:
            px = cx_e + v.co.x * 0.0150
            almond = max(0.22, 1.0 - 0.68 * (v.co.x ** 2))
            pz = cz_e + v.co.z * 0.0068 * almond
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0032 + v.co.y * 0.0020
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0
        # Dark brown iris (0.014 wide, 0.012 high)
        ret_i = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
        for v in ret_i["verts"]:
            px = cx_e + v.co.x * 0.0072
            pz = cz_e + v.co.z * 0.0062
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0048 + v.co.y * 0.0012
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 1
        # Dark pupil (0.007 wide)
        ret_p = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
        for v in ret_p["verts"]:
            px = cx_e + v.co.x * 0.0036
            pz = cz_e + v.co.z * 0.0036
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0056 + v.co.y * 0.0008
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
        # Bold upper lash arch across the 0.030 eye width
        ret_l = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=1.0)
        for v in ret_l["verts"]:
            px = cx_e + v.co.x * 0.0158
            arch = 0.0050 * (1.0 - 0.72 * (v.co.x ** 2))
            pz = cz_e + arch + v.co.z * 0.0020
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0052 + v.co.y * 0.0012
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()
    occhi_obj.vertex_groups.clear()
    occhi_obj.vertex_groups.new(name="Head").add([v.index for v in occhi_obj.data.vertices], 1.0, 'REPLACE')

# 2. Make Sopracciglia (0.012 above eyes -> Z=1.597) bold and angled down towards nose
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (-1.0, 1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        xmin, xmax = min(abs(v.co.x) for v in vs), max(abs(v.co.x) for v in vs)
        zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
            x_new = sx * (0.012 + t * (0.050 - 0.012))
            z_line = 1.5930 + t * 0.0085  # average Z = 1.597
            y_b = exact_face_y(x_new, z_line)
            v.co = Vector((x_new, y_b - 0.0052, z_line + tz * 0.0055))
    brows_obj.data.update()

# 3. Make Labbra (Z=1.505, 0.045 wide) clearly visible on the front of the face
labbra_obj = bpy.data.objects.get("Labbra")
if labbra_obj:
    vs = labbra_obj.data.vertices
    xmin, xmax = min(v.co.x for v in vs), max(v.co.x for v in vs)
    ymin, ymax = min(v.co.y for v in vs), max(v.co.y for v in vs)
    zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
    for v in vs:
        tx = (v.co.x - xmin) / max(1e-5, xmax - xmin) - 0.5
        ty = (v.co.y - ymin) / max(1e-5, ymax - ymin) - 0.5
        tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
        x_new = tx * 0.045
        taper = max(0.25, math.cos(tx * math.pi * 0.88))
        z_new = 1.505 + tz * 0.0065 * taper
        y_b = exact_face_y(x_new, 1.505)
        v.co = Vector((x_new, y_b - 0.0042 + ty * 0.0025, z_new))
    labbra_obj.data.update()

# 4. Make Capelli_Scuri locks flick outwards at temples & sides (wavy messy clumps, 0.19 m wide at top, Z=1.70 m)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    bm = bmesh.new()
    bm.from_mesh(capelli_obj.data)
    bm.faces.ensure_lookup_table()
    visited = set()
    c_idx = 0
    for f in bm.faces:
        if f.index in visited:
            continue
        comp = []
        q = [f]
        visited.add(f.index)
        while q:
            c = q.pop()
            comp.append(c)
            for v in c.verts:
                for lf in v.link_faces:
                    if lf.index not in visited:
                        visited.add(lf.index)
                        q.append(lf)
        c_verts = list({v for cf in comp for v in cf.verts})
        if len(c_verts) < 150:
            cx = sum(v.co.x for v in c_verts) / len(c_verts)
            cy = sum(v.co.y for v in c_verts) / len(c_verts)
            zmin_c = min(v.co.z for v in c_verts)
            zmax_c = max(v.co.z for v in c_verts)
            # Outward sideways flick on side/temple clumps so they don't hang straight down
            if abs(cx) > 0.035:
                sx_c = 1.0 if cx > 0 else -1.0
                for v in c_verts:
                    tz = (v.co.z - zmin_c) / max(1e-5, zmax_c - zmin_c)  # 0 at tip, 1 at crown
                    # S-curve wave + outward flick at the tip (tz -> 0)
                    flick_x = sx_c * (0.016 * ((1.0 - tz) ** 1.4) * (1.0 if c_idx % 2 == 0 else 0.55)
                                      + 0.007 * math.sin(tz * math.pi * 2.0 + c_idx))
                    lift_z = 0.008 * ((1.0 - tz) ** 1.5) * (1 if c_idx % 3 == 0 else 0)
                    v.co.x += flick_x
                    v.co.z += lift_z
            c_idx += 1

    # Normalize Capelli_Scuri total width to 0.190 m ([-0.095, +0.095]) and max Z to 1.700 m
    xs_h = [v.co.x for v in bm.verts]
    zs_h = [v.co.z for v in bm.verts]
    xmin_h, xmax_h = min(xs_h), max(xs_h)
    zmax_h = max(zs_h)
    for v in bm.verts:
        v.co.x = -0.095 + ((v.co.x - xmin_h) / max(1e-5, xmax_h - xmin_h)) * 0.190
        if v.co.z > 1.60:
            v.co.z = 1.60 + (v.co.z - 1.60) * ((1.700 - 1.60) / max(1e-5, zmax_h - 1.60))

    bm.normal_update()
    bm.to_mesh(capelli_obj.data)
    bm.free()
    capelli_obj.data.update()

mesh_objects = [o for o in scn.objects if o.type == 'MESH' and not o.name.startswith("_gara")]
total_tris = sum(len(o.data.loop_triangles) or (o.data.calc_loop_triangles() or len(o.data.loop_triangles)) for o in mesh_objects)
log(f"Totale finale triangoli: {total_tris} (<= 40.000)")

render_viste("rev_10")

blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
glb_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.glb"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.object.select_all(action='DESELECT')
arm_obj = bpy.data.objects.get("Armature")
if arm_obj:
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
for o in mesh_objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=True, export_yup=True)

render_viste("finale_revisione_personaggio")
