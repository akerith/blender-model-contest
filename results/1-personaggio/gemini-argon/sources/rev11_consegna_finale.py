import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 10 FINALIZATION & SECTION D DELIVERY (rev_10 & finale_revisione_personaggio)
# - Refines feminine egg-shaped jaw taper, curved almond eyes with upper lash,
#   and messy outward-pointing wavy hair locks fuller at the top (0.19 m wide).
# - Brings total triangle count to ~37,200 (< 40,000 limit) by lowering segments
#   only on small round/secondary pieces (never hands or face), matching 10.4.
# - Saves personaggio.blend (D1), exports personaggio.glb (D2), and renders
#   finale_revisione_personaggio (D3).
# ==============================================================================

scn = bpy.context.scene

# 1. Refine Testa egg-shaped jaw taper (narrower at chin, smooth feminine jawline)
o_head = bpy.data.objects.get("Testa")
if o_head:
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=26, radius=1.0)
    for v in bm.verts:
        ux, uy, uz = v.co.x, v.co.y, v.co.z
        tz = 0.5 * (uz + 1.0)  # 0 at chin (Z=1.475), 1 at skull top (Z=1.660)
        z = 1.475 + tz * (1.660 - 1.475)
        th = math.atan2(uy, ux)
        ct, st = math.cos(th), math.sin(th)

        cap = 1.0
        if tz < 0.08:
            cap = math.sin((tz / 0.08) * math.pi * 0.5) ** 0.65
        elif tz > 0.84:
            cap = math.sin(((1.0 - tz) / 0.16) * math.pi * 0.5) ** 0.65

        # Egg shape: narrower at chin (rx=0.022 at chin, tapering smoothly along jaw up to 0.075 at temples)
        if tz < 0.52:
            t_j = tz / 0.52
            rx = (0.022 + 0.053 * (t_j ** 1.15)) * cap
        else:
            t_top = (tz - 0.52) / 0.48
            rx = 0.075 * (1.0 - 0.05 * (t_top ** 2)) * cap

        if st < 0.0:  # front half (-Y)
            if tz < 0.48:
                t_f = tz / 0.48
                ry_f = (0.064 + 0.012 * (t_f ** 0.85)) * cap
            else:
                ry_f = 0.076 * cap
            front_flat = 1.0 - 0.08 * (abs(st) ** 2)
            py = st * ry_f * front_flat
        else:         # back half (+Y)
            if tz < 0.35:
                t_b = tz / 0.35
                ry_b = (0.052 + 0.043 * (t_b ** 0.85)) * cap
            else:
                ry_b = 0.095 * cap
            py = st * ry_b

        px = ct * rx

        if st < -0.25:
            w_front = min(1.0, (-st - 0.25) / 0.75)
            # Eye socket recess at Z=1.585, X=+-0.0325
            for sx_e in (-1.0, 1.0):
                d2_e = ((px - sx_e * 0.0325) / 0.017) ** 2 + ((z - 1.585) / 0.010) ** 2
                if d2_e < 1.8:
                    py += 0.0040 * math.exp(-d2_e) * w_front
            # Nose wedge from Z 1.58 down to Z 1.53, sticking out 0.02 from the face
            if 1.524 <= z <= 1.584:
                w_n = 0.0068 + 0.0058 * max(0.0, (1.580 - z) / 0.050)
                nx_f = max(0.0, 1.0 - (abs(px) / (w_n * 1.45)) ** 1.8)
                if nx_f > 0.0:
                    if z >= 1.534:
                        nz_f = max(0.0, min(1.0, (1.582 - z) / (1.582 - 1.534)))
                    else:
                        nz_f = max(0.0, (z - 1.524) / (1.534 - 1.524))
                    py -= 0.020 * nx_f * nz_f * w_front
            # Small rounded chin at Z=1.482
            d2_c = (px / 0.018) ** 2 + ((z - 1.483) / 0.010) ** 2
            if d2_c < 2.0:
                py -= 0.0035 * math.exp(-d2_c) * w_front

        v.co = Vector((px, py, z))

    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    zmin, zmax = min(zs), max(zs)
    for v in bm.verts:
        v.co.x = -0.075 + ((v.co.x - xmin) / (xmax - xmin)) * 0.150
        v.co.y = -0.095 + ((v.co.y - ymin) / (ymax - ymin)) * 0.190
        v.co.z = 1.475 + ((v.co.z - zmin) / (zmax - zmin)) * (1.660 - 1.475)

    uv_lay = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            l[uv_lay].uv = (0.5 + math.atan2(l.vert.co.x, -l.vert.co.y) / (2 * math.pi), (l.vert.co.z - 1.475) / 0.22)
    bm.normal_update()
    bm.to_mesh(o_head.data)
    bm.free()
    o_head.data.update()

def exact_face_y(x_q, z_q):
    near = [v.co.y for v in o_head.data.vertices if v.co.y < 0.0 and abs(v.co.x - x_q) < 0.012 and abs(v.co.z - z_q) < 0.010]
    if near:
        return min(near)
    return -0.072

# Re-curve Occhi along exact_face_y(px, pz) with upper lash line so eyes look crisp and expressive
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        cx_e = sx * 0.0325
        cz_e = 1.585
        # White sclera almond (0.030 wide) curving with the face at each vertex's px
        ret_w = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
        for v in ret_w["verts"]:
            px = cx_e + v.co.x * 0.0150
            almond = max(0.18, 1.0 - 0.72 * (v.co.x ** 2))
            pz = cz_e + v.co.z * 0.0056 * almond
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0022 + v.co.y * 0.0022
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0
        # Dark brown iris (0.0125 wide)
        ret_i = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
        for v in ret_i["verts"]:
            px = cx_e + v.co.x * 0.0062
            pz = cz_e + v.co.z * 0.0052
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0040 + v.co.y * 0.0012
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 1
        # Dark pupil + thin upper lash arch
        ret_p = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
        for v in ret_p["verts"]:
            px = cx_e + v.co.x * 0.0028
            pz = cz_e + v.co.z * 0.0028
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0048 + v.co.y * 0.0008
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
        # Upper lash line framing top of eye
        ret_l = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
        for v in ret_l["verts"]:
            px = cx_e + v.co.x * 0.0155
            arch = 0.0042 * (1.0 - 0.70 * (v.co.x ** 2))
            pz = cz_e + arch + v.co.z * 0.0014
            y_b = exact_face_y(px, cz_e)
            py = y_b - 0.0042 + v.co.y * 0.0012
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()

# Update Labbra position on new jaw surface (Z=1.505, 0.045 wide)
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
        taper = max(0.25, math.cos(tx * math.pi * 0.90))
        z_new = 1.505 + tz * 0.0052 * taper
        y_b = exact_face_y(x_new, 1.505)
        v.co = Vector((x_new, y_b - 0.0026 + ty * 0.0022, z_new))
    labbra_obj.data.update()

# Shape Capelli_Scuri so it is fuller/wider at the upper crown & temples (0.19 m wide at Z=1.60..1.66)
# and tapers with messy outward-pointing locks towards jaw height (Z=1.50)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    for v in capelli_obj.data.vertices:
        z = v.co.z
        # Widen upper hair (Z in 1.57..1.67) and taper lower sides (Z in 1.48..1.55) with messy waves
        if 1.56 <= z <= 1.68:
            bulge = math.sin(((z - 1.56) / 0.12) * math.pi)
            v.co.x *= (1.0 + 0.12 * bulge)
        elif z < 1.56:
            t_low = (1.56 - z) / 0.08
            flick = 0.008 * math.sin(v.co.y * 45.0 + z * 55.0)
            v.co.x = v.co.x * (1.0 - 0.14 * t_low) + math.copysign(flick * t_low, v.co.x)
    xs_h = [v.co.x for v in capelli_obj.data.vertices]
    xmin_h, xmax_h = min(xs_h), max(xs_h)
    for v in capelli_obj.data.vertices:
        v.co.x = -0.095 + ((v.co.x - xmin_h) / max(1e-5, xmax_h - xmin_h)) * 0.190
    capelli_obj.data.update()

# Re-assign Head vertex group on Testa and Occhi
for oname in ("Testa", "Occhi"):
    o = bpy.data.objects.get(oname)
    if o:
        o.vertex_groups.clear()
        vg = o.vertex_groups.new(name="Head")
        vg.add([v.index for v in o.data.vertices], 1.0, 'REPLACE')

# ------------------------------------------------------------------------------
# 2. Reduce triangle counts ONLY on non-face, non-hand pieces so total < 40,000 (~37,000)
# ------------------------------------------------------------------------------
reduction_targets = [
    ("Corda_Fianco_DX", 1900),
    ("Sacca_Arrotolata", 1150),
    ("Ginocchiere", 760),
    ("Lacci_Stivale_SX", 380),
    ("Lacci_Stivale_DX", 380),
    ("Pantalone_SX", 680),
    ("Pantalone_DX", 680),
    ("Stivale_SX", 680),
    ("Stivale_DX", 680),
    ("Manica_SX", 580),
    ("Manica_DX", 580),
    ("Giacca_Torso", 1350),
    ("Tasca_Tonda_DX", 360),
    ("Conchiglie_SX", 300),
    ("Fascia_Gamba_SX", 280),
    ("Fascia_Gamba_DX", 280),
    ("Tasche_Cintura", 280),
    ("Medaglione_Cintura", 220),
    ("Astuccio_SX", 440),
    ("Casco_Palombaro", 3900),
]

for obj_name, target_tris in reduction_targets:
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        continue
    obj.data.calc_loop_triangles()
    curr_tris = len(obj.data.loop_triangles)
    if curr_tris > target_tris:
        for m_old in list(obj.modifiers):
            if m_old.type == 'ARMATURE':
                obj.modifiers.remove(m_old)
        mod = obj.modifiers.new(name="Trim_10_4", type='DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = float(target_tris) / float(curr_tris)
        with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj], selected_editable_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        amod = obj.modifiers.new(name="Armature", type='ARMATURE')
        amod.object = bpy.data.objects.get("Armature")
        obj.data.update()

mesh_objects = [o for o in scn.objects if o.type == 'MESH' and not o.name.startswith("_gara")]
log("=== CONTEGGIO FINALE TRIANGOLI PER OGGETTO (Group 10.4) ===")
total_tris = 0
for obj in sorted(mesh_objects, key=lambda x: x.name):
    obj.data.calc_loop_triangles()
    t_count = len(obj.data.loop_triangles)
    total_tris += t_count
    log(f"  {obj.name}: {t_count} triangoli")
log(f"TOTALE FINALE TRIANGOLI PERSONAGGIO: {total_tris} (limite massimo: 40.000)")

# Category summary check for 10.4
face_hair_t = sum(len(bpy.data.objects[n].data.loop_triangles) for n in ("Testa", "Occhi", "Sopracciglia", "Labbra", "Orecchie", "Capelli_Scuri", "Ciocca_Bianca") if bpy.data.objects.get(n))
hands_t = sum(len(bpy.data.objects[n].data.loop_triangles) for n in ("Mano_SX", "Mano_DX") if bpy.data.objects.get(n))
cape_t = sum(len(bpy.data.objects[n].data.loop_triangles) for n in ("Mantella_Corpo", "Mantella_Spalla_SX", "Mantella_Spalla_DX", "Mantella_Colletto") if bpy.data.objects.get(n))
helmet_t = len(bpy.data.objects["Casco_Palombaro"].data.loop_triangles)
rope_hoses_t = sum(len(bpy.data.objects[n].data.loop_triangles) for n in ("Corda_Fianco_DX", "Tubi_Casco") if bpy.data.objects.get(n))
log(f"Distribuzione: Volto+Capelli={face_hair_t} (~6000), Mani={hands_t} (~4000), Mantella={cape_t} (~6000), Casco={helmet_t} (~5000), Corda+Tubi={rope_hoses_t} (~4000)")

# Update rev_10 renders
render_viste("rev_10")

# ------------------------------------------------------------------------------
# 3. SECTION D - Delivery (D1, D2, D3)
# ------------------------------------------------------------------------------
blend_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.blend"
glb_path = r"C:\Users\USER\gara-modelli\concorrenti\gemini-argon\lavoro\personaggio.glb"

# D1. Save personaggio.blend
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
log(f"D1: Salvato {blend_path}")

# D2. Export personaggio.glb (glTF binary, the armature included, +Y up as Blender's exporter does)
bpy.ops.object.select_all(action='DESELECT')
arm_obj = bpy.data.objects.get("Armature")
if arm_obj:
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
for o in mesh_objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=True, export_yup=True)
log(f"D2: Esportato {glb_path}")

# D3. Run render_viste("finale_revisione_personaggio")
render_viste("finale_revisione_personaggio")
