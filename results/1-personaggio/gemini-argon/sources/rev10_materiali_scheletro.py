import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ==============================================================================
# GROUP 10 - Materials pass, triangles, skeleton (rev_10 & rev_prova_osso)
# - True anatomical egg-shaped head profile in front & side views (chin at Y=-0.074,
#   Z=1.475; mouth Z=1.505, 0.045 wide; nose wedge Z=1.53..1.58 sticking out 0.02;
#   eyes Z=1.585, 0.065 apart, 0.03 wide; angled eyebrows Z=1.597).
# - Wavy, messy hair clumps (0.19 wide at top, Z=1.70, forehead locks, side locks to Z=1.50, back to Z=1.48).
# - Exact Group 10.4 triangle distribution (< 40,000 total: face & hair ~6,300,
#   hands ~3,936 (~1,968 each), cape ~6,400, helmet ~4,472, rope & hoses ~3,868).
# - Group 10.5 & 10.6 skeleton binding and 30-degree UpperArm.L swing test.
# ==============================================================================

scn = bpy.context.scene

# ------------------------------------------------------------------------------
# 1. Refine Testa, Occhi, Sopracciglia, Labbra, and Capelli_Scuri for anatomical profile & ~6,300 tris
# ------------------------------------------------------------------------------
o_head = bpy.data.objects.get("Testa")
if o_head:
    bm = bmesh.new()
    # 36 x 26 UV sphere = 1,800 triangles on Testa -> total face + hair ~ 6,300 triangles (10.4!)
    bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=26, radius=1.0)
    for v in bm.verts:
        ux, uy, uz = v.co.x, v.co.y, v.co.z
        tz = 0.5 * (uz + 1.0)  # 0 at chin (Z=1.475), 1 at skull top (Z=1.660)
        z = 1.475 + tz * (1.660 - 1.475)
        th = math.atan2(uy, ux)  # -pi/2 is front (-Y), +pi/2 is back (+Y)
        ct, st = math.cos(th), math.sin(th)

        # Cylindrical egg profile so side profile has a real human face, chin, and jaw!
        # Round cap only at very bottom chin (tz < 0.07) and top of skull (tz > 0.84)
        cap = 1.0
        if tz < 0.07:
            cap = math.sin((tz / 0.07) * math.pi * 0.5) ** 0.55
        elif tz > 0.84:
            cap = math.sin(((1.0 - tz) / 0.16) * math.pi * 0.5) ** 0.65

        # Width X: narrower at chin (rx=0.036 at Z=1.48), widening along jaw to 0.075 (0.15 wide) at ears/temples (Z=1.56..1.62)
        if tz < 0.48:
            t_j = tz / 0.48
            rx = (0.034 + 0.041 * (t_j ** 0.75)) * cap
        else:
            rx = 0.075 * cap

        # Depth Y: front face plane sits at Y ~ -0.075 from chin (Z=1.48) to forehead (Z=1.63);
        # back of skull reaches Y = +0.095 (total depth 0.19 m including nose tip at Y = -0.095!)
        if st < 0.0:  # front half (-Y)
            if tz < 0.45:
                t_f = tz / 0.45
                ry_f = (0.068 + 0.008 * (t_f ** 0.6)) * cap
            else:
                ry_f = 0.076 * cap
            # Flatten front face slightly so eyes, nose and mouth sit on a natural facial plane
            front_flat = 1.0 - 0.10 * (abs(st) ** 2)
            py = st * ry_f * front_flat
        else:         # back half (+Y)
            if tz < 0.35:
                # Nape / under-jaw curves into neck at Z=1.48..1.53
                t_b = tz / 0.35
                ry_b = (0.055 + 0.040 * (t_b ** 0.8)) * cap
            else:
                ry_b = 0.095 * cap
            py = st * ry_b

        px = ct * rx

        # Facial features on the front (-Y, st < -0.25):
        if st < -0.25:
            w_front = min(1.0, (-st - 0.25) / 0.75)
            # Slight eye socket indentation at Z=1.585, X=+-0.0325
            for sx_e in (-1.0, 1.0):
                d2_e = ((px - sx_e * 0.0325) / 0.017) ** 2 + ((z - 1.585) / 0.010) ** 2
                if d2_e < 1.8:
                    py += 0.0045 * math.exp(-d2_e) * w_front

            # Nose: small wedge from Z 1.58 down to Z 1.53, sticking out 0.02 from the face (-0.075 -> -0.095)
            if 1.524 <= z <= 1.584:
                w_n = 0.007 + 0.006 * max(0.0, (1.580 - z) / 0.050)
                nx_f = max(0.0, 1.0 - (abs(px) / (w_n * 1.45)) ** 1.8)
                if nx_f > 0.0:
                    if z >= 1.534:
                        nz_f = max(0.0, min(1.0, (1.582 - z) / (1.582 - 1.534)))
                    else:
                        nz_f = max(0.0, (z - 1.524) / (1.534 - 1.524))
                    py -= 0.020 * nx_f * nz_f * w_front

            # Rounded chin prominence at Z=1.482..1.492
            d2_c = (px / 0.020) ** 2 + ((z - 1.485) / 0.010) ** 2
            if d2_c < 2.0:
                py -= 0.0035 * math.exp(-d2_c) * w_front

        v.co = Vector((px, py, z))

    # Normalize exact bounding box of Testa: X in [-0.075, +0.075] (0.15 wide), Y in [-0.095, +0.095] (0.19 deep), Z in [1.475, 1.660]
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

# Direct vertex lookup for exact front surface Y on Testa around (x_q, z_q)
def exact_face_y(x_q, z_q):
    near = [v.co.y for v in o_head.data.vertices if v.co.y < 0.0 and abs(v.co.x - x_q) < 0.014 and abs(v.co.z - z_q) < 0.012]
    if near:
        return min(near)
    return -0.072

# Rebuild Occhi geometry cleanly inside existing Occhi object so sclera (0.03 wide), dark brown iris, pupil, and upper lash are 100% distinct
occhi_obj = bpy.data.objects.get("Occhi")
if occhi_obj:
    occhi_obj.data.materials.clear()
    occhi_obj.data.materials.append(bpy.data.materials["Mat_OcchioBianco"])  # 0
    occhi_obj.data.materials.append(bpy.data.materials["Mat_Iride"])         # 1
    occhi_obj.data.materials.append(bpy.data.materials["Mat_Pupilla"])       # 2
    bm = bmesh.new()

    for sx in (-1.0, 1.0):
        cx_e = sx * 0.0325  # 0.065 apart centre to centre
        cz_e = 1.585        # eyes at Z 1.585
        # 1) White sclera almond: 0.030 wide (rx=0.015), 0.011 high (rz=0.0055)
        ret_w = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
        for v in ret_w["verts"]:
            px = cx_e + v.co.x * 0.0150
            almond = max(0.20, 1.0 - 0.65 * (v.co.x ** 2))
            pz = cz_e + v.co.z * 0.0058 * almond
            y_base = exact_face_y(px, cz_e)
            py = y_base - 0.0012 + v.co.y * 0.0030
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 0

        # 2) Dark brown iris disc: 0.012 wide (rx=0.006), 0.0105 high (rz=0.0052)
        ret_i = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
        for v in ret_i["verts"]:
            px = cx_e + v.co.x * 0.0062
            pz = cz_e + v.co.z * 0.0052
            y_base = exact_face_y(px, cz_e)
            py = y_base - 0.0036 + v.co.y * 0.0015
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 1

        # 3) Dark pupil center: 0.0055 wide
        ret_p = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
        for v in ret_p["verts"]:
            px = cx_e + v.co.x * 0.0028
            pz = cz_e + v.co.z * 0.0028
            y_base = exact_face_y(px, cz_e)
            py = y_base - 0.0046 + v.co.y * 0.0010
            v.co = Vector((px, py, pz))
            for f in v.link_faces:
                f.smooth = True
                f.material_index = 2

    bm.normal_update()
    bm.to_mesh(occhi_obj.data)
    bm.free()
    occhi_obj.data.update()

# Position Sopracciglia: dark straight eyebrows 0.012 above eyes (Z=1.597), angled down towards nose
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (-1.0, 1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        xmin, xmax = min(abs(v.co.x) for v in vs), max(abs(v.co.x) for v in vs)
        zmin, zmax = min(v.co.z for v in vs), max(v.co.z for v in vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            tz = (v.co.z - zmin) / max(1e-5, zmax - zmin) - 0.5
            x_new = sx * (0.014 + t * (0.049 - 0.014))
            z_line = 1.5935 + t * 0.0075
            y_base = exact_face_y(x_new, z_line)
            v.co = Vector((x_new, y_base - 0.0035, z_line + tz * 0.0045))
    brows_obj.data.update()

# Position Labbra: closed straight line at Z 1.505, 0.045 wide, lips not smiling
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
        z_new = 1.505 + tz * 0.0055 * taper
        y_base = exact_face_y(x_new, 1.505)
        v.co = Vector((x_new, y_base - 0.0028 + ty * 0.0025, z_new))
    labbra_obj.data.update()

# Reshape Capelli_Scuri so the side & crown clumps flare out into distinct wavy messy locks (0.19 wide at top, Z=1.70, not flat-sided)
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
            # Individual hair clump: give it a natural outward wave & pointed tip
            cx = sum(v.co.x for v in c_verts) / len(c_verts)
            zmin_c = min(v.co.z for v in c_verts)
            zmax_c = max(v.co.z for v in c_verts)
            for v in c_verts:
                tz = (v.co.z - zmin_c) / max(1e-5, zmax_c - zmin_c)  # 0 at tip, 1 at root
                # Wave + outward flare in middle/tip of clump
                wave = 0.010 * math.sin(tz * math.pi * 1.5 + (c_idx % 5) * 0.8) * (1.0 - 0.5 * tz)
                v.co.x += math.copysign(wave, cx)
            c_idx += 1
    # Smoothly normalize Capelli_Scuri X width to 0.190 m ([-0.095, +0.095]) and max Z to 1.700 m
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

# ------------------------------------------------------------------------------
# 2. Adjust triangle counts to match Group 10.4 exactly:
#    - Hands (Mano_SX, Mano_DX): ~1,968 triangles each (~3,936 total, target "hands about 4,000 (2,000 each)")
#    - Cape (Mantella_Corpo + Mantella_Spalla_SX/DX + Mantella_Colletto): ~6,400 triangles (target "cape about 6,000")
#    - Total triangles for character < 40,000 (~36,500)
# ------------------------------------------------------------------------------
for side in ("SX", "DX"):
    mano_obj = bpy.data.objects.get(f"Mano_{side}")
    if mano_obj:
        mano_obj.data.calc_loop_triangles()
        if len(mano_obj.data.loop_triangles) < 1200:
            bm = bmesh.new()
            bm.from_mesh(mano_obj.data)
            # Subdivide edges once and smooth slightly -> ~2,624 -> decimate to ~1,980 triangles per hand!
            bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
            bmesh.ops.smooth_vert(bm, verts=bm.verts[:], factor=0.25, use_axis_x=True, use_axis_y=True, use_axis_z=True)
            bm.normal_update()
            bm.to_mesh(mano_obj.data)
            bm.free()
            mod = mano_obj.modifiers.new(name="Hand_2k", type='DECIMATE')
            mod.decimate_type = 'COLLAPSE'
            mod.ratio = 1980.0 / 2624.0
            with bpy.context.temp_override(object=mano_obj, active_object=mano_obj, selected_objects=[mano_obj], selected_editable_objects=[mano_obj]):
                bpy.ops.object.modifier_apply(modifier=mod.name)
            mano_obj.data.update()

# Optimize Mantella_Corpo from 18,248 to ~4,200 triangles and Mantella_Spalla_SX/DX from 2,038 to ~750 triangles each
# so total cape (Mantella_Corpo + Mantella_Spalla_SX/DX + Mantella_Colletto) is ~6,440 triangles ("cape about 6,000"!)
for c_name, target_t in (("Mantella_Corpo", 4200), ("Mantella_Spalla_SX", 750), ("Mantella_Spalla_DX", 750)):
    c_obj = bpy.data.objects.get(c_name)
    if c_obj:
        c_obj.data.calc_loop_triangles()
        curr_t = len(c_obj.data.loop_triangles)
        if curr_t > target_t * 1.15:
            mod = c_obj.modifiers.new(name="Cape_6k", type='DECIMATE')
            mod.decimate_type = 'COLLAPSE'
            mod.ratio = float(target_t) / float(curr_t)
            with bpy.context.temp_override(object=c_obj, active_object=c_obj, selected_objects=[c_obj], selected_editable_objects=[c_obj]):
                bpy.ops.object.modifier_apply(modifier=mod.name)
            c_obj.data.update()

# Recalculate normals outside on all meshes (10.2) and log per-object triangle counts (10.4)
mesh_objects = [o for o in scn.objects if o.type == 'MESH' and not o.name.startswith("_gara")]
for obj in mesh_objects:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = True
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

log("=== CONTEGGIO TRIANGOLI PER OGGETTO (Group 10.4) ===")
total_tris = 0
for obj in sorted(mesh_objects, key=lambda x: x.name):
    obj.data.calc_loop_triangles()
    t_count = len(obj.data.loop_triangles)
    total_tris += t_count
    log(f"  {obj.name}: {t_count} triangoli")
log(f"TOTALE TRIANGOLI PERSONAGGIO: {total_tris} (limite massimo: 40.000)")

# ------------------------------------------------------------------------------
# 3. Re-bind modified meshes (Testa, Occhi, Mano_SX/DX, Mantella_Corpo, Mantella_Spalla_SX/DX) to Armature
# ------------------------------------------------------------------------------
arm_obj = bpy.data.objects.get("Armature")
bone_specs = [
    ("Hips",       (0.000,  0.000, 0.950), (0.000,  0.000, 1.100)),
    ("Spine",      (0.000,  0.000, 1.100), (0.000,  0.000, 1.270)),
    ("Chest",      (0.000,  0.000, 1.270), (0.000,  0.000, 1.450)),
    ("Neck",       (0.000,  0.000, 1.450), (0.000,  0.000, 1.500)),
    ("Head",       (0.000,  0.000, 1.500), (0.000,  0.000, 1.700)),
    ("Shoulder.L", (0.040,  0.000, 1.430), (0.190,  0.000, 1.400)),
    ("UpperArm.L", (0.190,  0.000, 1.400), (0.380,  0.000, 1.180)),
    ("LowerArm.L", (0.380,  0.000, 1.180), (0.540,  0.000, 0.990)),
    ("Hand.L",     (0.540,  0.000, 0.990), (0.605,  0.000, 0.920)),
    ("Shoulder.R", (-0.040, 0.000, 1.430), (-0.190, 0.000, 1.400)),
    ("UpperArm.R", (-0.190, 0.000, 1.400), (-0.380, 0.000, 1.180)),
    ("LowerArm.R", (-0.380, 0.000, 1.180), (-0.540, 0.000, 0.990)),
    ("Hand.R",     (-0.540, 0.000, 0.990), (-0.605, 0.000, 0.920)),
    ("UpperLeg.L", (0.100,  0.000, 0.900), (0.115,  0.000, 0.490)),
    ("LowerLeg.L", (0.115,  0.000, 0.490), (0.130,  0.000, 0.080)),
    ("Foot.L",     (0.130,  0.000, 0.080), (0.130, -0.100, 0.030)),
    ("Toes.L",     (0.130, -0.100, 0.030), (0.130, -0.190, 0.015)),
    ("UpperLeg.R", (-0.100, 0.000, 0.900), (-0.115, 0.000, 0.490)),
    ("LowerLeg.R", (-0.115, 0.000, 0.490), (-0.130, 0.000, 0.080)),
    ("Foot.R",     (-0.130, 0.000, 0.080), (-0.130, -0.100, 0.030)),
    ("Toes.R",     (-0.130, -0.100, 0.030), (-0.130, -0.190, 0.015)),
]
bone_segs = {bname: (Vector(h_co), Vector(t_co)) for bname, h_co, t_co in bone_specs}

def dist_pt_seg(pt, a, b):
    ab = b - a
    lsq = ab.length_squared
    if lsq < 1e-8:
        return (pt - a).length
    t = max(0.0, min(1.0, (pt - a).dot(ab) / lsq))
    return (pt - (a + ab * t)).length

for oname in ("Testa", "Occhi", "Sopracciglia", "Labbra", "Capelli_Scuri"):
    o = bpy.data.objects.get(oname)
    if o:
        o.vertex_groups.clear()
        vg = o.vertex_groups.new(name="Head")
        vg.add([v.index for v in o.data.vertices], 1.0, 'REPLACE')

for side, s_tag in (("SX", "L"), ("DX", "R")):
    mo = bpy.data.objects.get(f"Mano_{side}")
    if mo:
        mo.vertex_groups.clear()
        vg = mo.vertex_groups.new(name=f"Hand.{s_tag}")
        vg.add([v.index for v in mo.data.vertices], 1.0, 'REPLACE')
    so = bpy.data.objects.get(f"Mantella_Spalla_{side}")
    if so:
        so.vertex_groups.clear()
        vg_sh = so.vertex_groups.new(name=f"Shoulder.{s_tag}")
        vg_ua = so.vertex_groups.new(name=f"UpperArm.{s_tag}")
        for v in so.data.vertices:
            d_sh = dist_pt_seg(v.co, *bone_segs[f"Shoulder.{s_tag}"])
            d_ua = dist_pt_seg(v.co, *bone_segs[f"UpperArm.{s_tag}"])
            w_sh = 1.0 / ((d_sh + 0.02) ** 2.5)
            w_ua = 1.0 / ((d_ua + 0.02) ** 2.5)
            tot = w_sh + w_ua
            vg_sh.add([v.index], w_sh / tot, 'REPLACE')
            vg_ua.add([v.index], w_ua / tot, 'REPLACE')

co_cape = bpy.data.objects.get("Mantella_Corpo")
if co_cape:
    co_cape.vertex_groups.clear()
    torso_leg_bnames = ["Hips", "Spine", "Chest", "Shoulder.L", "Shoulder.R", "UpperLeg.L", "LowerLeg.L", "UpperLeg.R", "LowerLeg.R"]
    vgs = {bn: co_cape.vertex_groups.new(name=bn) for bn in torso_leg_bnames}
    for v in co_cape.data.vertices:
        ws = []
        for bn in torso_leg_bnames:
            if bn.endswith(".L") and v.co.x < 0:
                continue
            if bn.endswith(".R") and v.co.x > 0:
                continue
            d = dist_pt_seg(v.co, *bone_segs[bn])
            ws.append((bn, 1.0 / ((d + 0.025) ** 3.0)))
        ws.sort(key=lambda x: x[1], reverse=True)
        top2 = ws[:2]
        tot = sum(w for _, w in top2)
        for bn, w in top2:
            vgs[bn].add([v.index], w / tot, 'REPLACE')

# ------------------------------------------------------------------------------
# 4. GROUP 10.6 TEST: Rotate UpperArm.L by 30 degrees (swinging the arm up/forward),
#    render "rev_prova_osso" (fronte, tre_quarti), then reset UpperArm.L back to 0!
# ------------------------------------------------------------------------------
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pbone = arm_obj.pose.bones.get("UpperArm.L")
if pbone:
    pbone.rotation_mode = 'XYZ'
    pbone.rotation_euler = (math.radians(30.0), 0.0, math.radians(-20.0))
    bpy.context.view_layer.update()

render_viste("rev_prova_osso", viste=["fronte", "tre_quarti"])

if pbone:
    pbone.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()

bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_mainfile()
render_viste("rev_10")
