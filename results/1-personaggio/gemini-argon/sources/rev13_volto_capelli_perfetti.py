import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# FINAL HEAD EGG-TAPER & 0.19m WIDE WAVY HAIR FRAMING + DELIVERY (D1, D2, D3)
# ==============================================================================

scn = bpy.context.scene

# 1. Refine Testa: true egg shape (0.15 m wide at upper parietal skull Z~1.60,
#    0.19 m deep, Z from 1.475 chin to 1.660 skull top; front face tapers gracefully
#    from cheekbones 0.124 m wide down to jaw 0.090 m at mouth Z=1.505 and small rounded chin at Z=1.475)
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
        if tz < 0.07:
            cap = math.sin((tz / 0.07) * math.pi * 0.5) ** 0.65
        elif tz > 0.82:
            cap = math.sin(((1.0 - tz) / 0.18) * math.pi * 0.5) ** 0.65

        # Egg width X: widest at parietal cranium (tz ~ 0.68, Z ~ 1.60 -> rx = 0.075, full width 0.15 m),
        # narrower on the front facial plane and tapering down the jaw to a small rounded chin!
        if tz < 0.65:
            t_j = tz / 0.65
            rx_back = (0.020 + 0.055 * (t_j ** 0.95)) * cap
            rx_front = (0.016 + 0.046 * (t_j ** 1.15)) * cap  # narrower front jaw/cheeks!
        else:
            t_top = (tz - 0.65) / 0.35
            rx_back = 0.075 * (1.0 - 0.06 * (t_top ** 2)) * cap
            rx_front = 0.062 * (1.0 - 0.08 * (t_top ** 2)) * cap

        front_w = 0.5 * (1.0 - st)  # 1 at front (-Y), 0 at back (+Y)
        rx = rx_back * (1.0 - 0.45 * (front_w ** 1.5)) + rx_front * (0.45 * (front_w ** 1.5))

        if st < 0.0:  # front half (-Y)
            if tz < 0.48:
                t_f = tz / 0.48
                ry_f = (0.064 + 0.012 * (t_f ** 0.85)) * cap
            else:
                ry_f = 0.076 * cap
            py = st * ry_f * (1.0 - 0.06 * (abs(st) ** 2))
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
                w_n = 0.0065 + 0.0055 * max(0.0, (1.580 - z) / 0.050)
                nx_f = max(0.0, 1.0 - (abs(px) / (w_n * 1.45)) ** 1.8)
                if nx_f > 0.0:
                    if z >= 1.534:
                        nz_f = max(0.0, min(1.0, (1.582 - z) / (1.582 - 1.534)))
                    else:
                        nz_f = max(0.0, (z - 1.524) / (1.534 - 1.524))
                    py -= 0.020 * nx_f * nz_f * w_front
            # Small rounded chin at Z=1.482
            d2_c = (px / 0.016) ** 2 + ((z - 1.483) / 0.010) ** 2
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
    o_head.vertex_groups.clear()
    o_head.vertex_groups.new(name="Head").add([v.index for v in o_head.data.vertices], 1.0, 'REPLACE')

def exact_face_y(x_q, z_q):
    near = [v.co.y for v in o_head.data.vertices if v.co.y < 0.0 and abs(v.co.x - x_q) < 0.013 and abs(v.co.z - z_q) < 0.011]
    if near:
        return min(near)
    return -0.072

# Re-seat Occhi, Sopracciglia, Labbra onto the refined egg face
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        cx_e = sx * 0.0325
        cz_e = 1.585
        ret_w = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
        for v in ret_w["verts"]:
            px = cx_e + v.co.x * 0.0150
            almond = max(0.22, 1.0 - 0.68 * (v.co.x ** 2))
            pz = cz_e + v.co.z * 0.0068 * almond
            y_b = exact_face_y(px, cz_e)
            v.co = Vector((px, y_b - 0.0032 + v.co.y * 0.0020, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0
        ret_i = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
        for v in ret_i["verts"]:
            px = cx_e + v.co.x * 0.0072
            pz = cz_e + v.co.z * 0.0062
            y_b = exact_face_y(px, cz_e)
            v.co = Vector((px, y_b - 0.0048 + v.co.y * 0.0012, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 1
        ret_p = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
        for v in ret_p["verts"]:
            px = cx_e + v.co.x * 0.0036
            pz = cz_e + v.co.z * 0.0036
            y_b = exact_face_y(px, cz_e)
            v.co = Vector((px, y_b - 0.0056 + v.co.y * 0.0008, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
        ret_l = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=1.0)
        for v in ret_l["verts"]:
            px = cx_e + v.co.x * 0.0158
            arch = 0.0050 * (1.0 - 0.72 * (v.co.x ** 2))
            pz = cz_e + arch + v.co.z * 0.0020
            y_b = exact_face_y(px, cz_e)
            v.co = Vector((px, y_b - 0.0052 + v.co.y * 0.0012, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2
    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()
    occhi_obj.vertex_groups.clear()
    occhi_obj.vertex_groups.new(name="Head").add([v.index for v in occhi_obj.data.vertices], 1.0, 'REPLACE')

brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (-1.0, 1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        xmin, xmax = min(abs(v.co.x) for v in vs), max(abs(v.co.x) for v in vs)
        zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
            x_new = sx * (0.012 + t * (0.048 - 0.012))
            z_line = 1.5930 + t * 0.0085
            y_b = exact_face_y(x_new, z_line)
            v.co = Vector((x_new, y_b - 0.0052, z_line + tz * 0.0055))
    brows_obj.data.update()

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

# 2. Rebuild Capelli_Scuri clumps so the UPPER hair (Z=1.56..1.68) actually spans the full 0.19 m width
#    (X = -0.095 to +0.095, wider than the 0.15 m head!), with 32 wavy pointed locks framing the face and nape!
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    def add_clump(pts, rads_xy):
        segs = 8
        rings = []
        n = len(pts)
        for i in range(n):
            c = Vector(pts[i])
            rx, ry = rads_xy[i]
            if i == 0:
                t = (Vector(pts[1]) - c).normalized()
            elif i == n - 1:
                t = (c - Vector(pts[-2])).normalized()
            else:
                t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
            up = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
            b1 = t.cross(up).normalized()
            b2 = b1.cross(t).normalized()
            ring = [bm.verts.new(c + b1 * (rx * math.cos(2 * math.pi * j / segs)) + b2 * (ry * math.sin(2 * math.pi * j / segs))) for j in range(segs)]
            rings.append(ring)
        for i in range(n - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True
                for l in f.loops:
                    l[uv_lay].uv = (j / float(segs), i / float(n - 1))
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True

    # Inner scalp core covering top & back of skull
    ret = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=1.0)
    for v in ret["verts"]:
        x, y, z = v.co.x, v.co.y, v.co.z
        if y < -0.10 and z < 0.38:
            y = -0.10 + (y + 0.10) * 0.2
            z = max(z, 0.28)
        if z < -0.52:
            z = -0.52
        v.co = Vector((x * 0.080, 0.008 + y * 0.092, 1.595 + z * 0.088))
    for f in bm.faces:
        f.smooth = True

    # 22 radial clumps around sides and back: upper half flares out to X = +-0.092 (so with clump radius it is 0.19 m wide across the top & temples!)
    n_rad = 22
    for i in range(n_rad):
        ut = i / float(n_rad - 1)
        ang = (-0.70 + 1.40 * ut) * math.pi
        sx = math.sin(ang)
        cy = math.cos(ang)
        is_back = abs(ang) < math.pi * 0.35
        z_top = 1.690 + 0.010 * ((i + 1) % 2)
        z_bot = (1.478 + 0.012 * (i % 3)) if is_back else (1.500 + 0.016 * (i % 3))
        # Wide full volume at Z=1.60..1.65 (0.19 m total width!), with wavy S-curve and outward pointed tip
        w_out = 0.086 + 0.006 * (i % 2)
        tip_out = 0.082 + 0.012 * ((i + 1) % 2)
        pts = [
            (sx * 0.020, 0.005 + cy * 0.020, z_top),
            (sx * (w_out * 0.85), 0.005 + cy * 0.082, 1.662),
            (sx * w_out, 0.005 + cy * 0.100, 1.610),
            (sx * (w_out * 0.92), 0.005 + cy * 0.098, 1.555),
            (sx * tip_out, 0.005 + cy * 0.095, z_bot),
        ]
        rads = [(0.014, 0.011), (0.024, 0.018), (0.024, 0.018), (0.017, 0.013), (0.003, 0.003)]
        add_clump(pts, rads)

    # 10 messy upper-side & forehead locks (giving the iconic wide, wavy, wind-blown explorer hair silhouette of 1-personaggio.webp!)
    messy_locks = [
        # Upper side wings flaring out at Z=1.60..1.66 to X = +-0.094
        [(-0.015, -0.010, 1.698), (-0.060, -0.025, 1.685), (-0.088, -0.032, 1.640), (-0.094, -0.035, 1.585)],
        [( 0.015, -0.010, 1.698), ( 0.060, -0.025, 1.685), ( 0.088, -0.032, 1.640), ( 0.094, -0.035, 1.585)],
        [(-0.018,  0.015, 1.696), (-0.065,  0.010, 1.678), (-0.090,  0.012, 1.622), (-0.094,  0.015, 1.555)],
        [( 0.018,  0.015, 1.696), ( 0.065,  0.010, 1.678), ( 0.090,  0.012, 1.622), ( 0.094,  0.015, 1.555)],
        # Front-side cheek-framing locks (hugging temples at X=+-0.062..0.084 and flicking outwards at Z=1.51)
        [(-0.028, -0.035, 1.686), (-0.060, -0.070, 1.648), (-0.072, -0.066, 1.585), (-0.086, -0.056, 1.515)],
        [( 0.028, -0.035, 1.686), ( 0.060, -0.070, 1.648), ( 0.072, -0.066, 1.585), ( 0.086, -0.056, 1.515)],
        # Forehead locks falling down to just above the eyebrows (Z = 1.608)
        [(-0.024, -0.038, 1.688), (-0.042, -0.078, 1.662), (-0.048, -0.091, 1.634), (-0.044, -0.092, 1.608)],
        [(-0.008, -0.042, 1.688), (-0.018, -0.080, 1.660), (-0.022, -0.091, 1.633), (-0.018, -0.092, 1.609)],
        [( 0.008, -0.042, 1.690), ( 0.020, -0.080, 1.662), ( 0.026, -0.091, 1.634), ( 0.022, -0.092, 1.608)],
        [( 0.024, -0.038, 1.688), ( 0.044, -0.076, 1.660), ( 0.052, -0.089, 1.632), ( 0.048, -0.090, 1.609)],
    ]
    for pts in messy_locks:
        rads = [(0.014, 0.010), (0.022, 0.016), (0.018, 0.013), (0.004, 0.003)]
        add_clump(pts, rads)

    # Normalize exact hair width to 0.190 m ([-0.095, +0.095]) and max Z to 1.700 m
    xs_h = [v.co.x for v in bm.verts]
    zs_h = [v.co.z for v in bm.verts]
    xmin_h, xmax_h = min(xs_h), max(xs_h)
    zmax_h = max(zs_h)
    for v in bm.verts:
        v.co.x = -0.095 + ((v.co.x - xmin_h) / (xmax_h - xmin_h)) * 0.190
        if v.co.z > 1.60:
            v.co.z = 1.60 + (v.co.z - 1.60) * ((1.700 - 1.60) / (zmax_h - 1.60))

    bm.normal_update()
    bm.to_mesh(capelli_obj.data)
    bm.free()
    capelli_obj.data.update()
    capelli_obj.vertex_groups.clear()
    capelli_obj.vertex_groups.new(name="Head").add([v.index for v in capelli_obj.data.vertices], 1.0, 'REPLACE')

mesh_objects = [o for o in scn.objects if o.type == 'MESH' and not o.name.startswith("_gara")]
total_tris = 0
for o in mesh_objects:
    o.data.calc_loop_triangles()
    total_tris += len(o.data.loop_triangles)
log(f"Totale finale triangoli: {total_tris} (limite massimo: 40.000)")

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
