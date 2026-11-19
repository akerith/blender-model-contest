import bpy
import bmesh
import math
from mathutils import Vector

# ==============================================================================
# GROUP 2 FIX (rev_2):
# - Fix lighting/specular washout on skin & dark hair while keeping exact RGBs
# - Make mouth (Z=1.505, 0.045 wide), eyes (Z=1.585, 0.065 apart, 0.03 wide),
#   and angled eyebrows (Z=1.597) crisp and clearly visible on the face
# - Keep forehead locks above eyebrows (Z >= 1.608) and temples outside the face
# - Make hair full on top and sides (0.19 wide at top, Z=1.70, >=25 wavy clumps)
# - Smooth white streak (Ciocca_Bianca) at X=-0.03 going back over the head
# ==============================================================================

scn = bpy.context.scene

# Adjust lighting and specular so (0.85, 0.68, 0.58) skin and (0.10, 0.08, 0.07) hair don't wash out
for l_name, energy in (("Luce_Key", 2.0), ("Luce_Fill", 1.0), ("Luce_Back", 2.0)):
    l_obj = bpy.data.objects.get(l_name)
    if l_obj and l_obj.data:
        l_obj.data.energy = energy

for m_name, rgb, rough, spec in [
    ("Mat_Pelle", (0.85, 0.68, 0.58), 0.62, 0.22),
    ("Mat_Labbra", (0.58, 0.35, 0.30), 0.55, 0.25),
    ("Mat_CapelliScuri", (0.10, 0.08, 0.07), 0.78, 0.12),
    ("Mat_CapelliBianchi", (0.80, 0.80, 0.78), 0.70, 0.18),
    ("Mat_Iride", (0.18, 0.11, 0.07), 0.15, 0.50),
]:
    mat = bpy.data.materials.get(m_name)
    if mat and mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = spec

o_head = bpy.data.objects.get("Testa")

def face_surface_y(x_q, z_q):
    best_y = -0.080
    best_d = 999.0
    for v in o_head.data.vertices:
        if v.co.y < 0.0:
            d = (v.co.x - x_q) ** 2 + (v.co.z - z_q) ** 2
            if d < best_d:
                best_d = d
                best_y = v.co.y
    return best_y

# 1. Make Labbra clearly visible on the front surface at Z = 1.505, width = 0.045
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
        taper = max(0.25, 1.0 - (abs(tx) * 2.0) ** 1.8)
        z_new = 1.505 + tz * 0.0065 * taper
        y_surf = face_surface_y(x_new, 1.505)
        v.co.x = x_new
        v.co.y = y_surf - 0.0028 + ty * 0.0045
        v.co.z = z_new
    labbra_obj.data.update()

# 2. Make Sopracciglia crisp and visible 0.012 above eyes (Z = 1.597), angled down towards nose
brows_obj = bpy.data.objects.get("Sopracciglia")
if brows_obj:
    for sx in (1.0, -1.0):
        vs = [v for v in brows_obj.data.vertices if (v.co.x * sx) > 0]
        if not vs:
            continue
        xmin = min(abs(v.co.x) for v in vs)
        xmax = max(abs(v.co.x) for v in vs)
        z_avg = sum(v.co.z for v in vs) / len(vs)
        y_avg = sum(v.co.y for v in vs) / len(vs)
        for v in vs:
            t = (abs(v.co.x) - xmin) / max(1e-5, xmax - xmin)
            x_new = sx * (0.013 + t * (0.049 - 0.013))
            z_line = 1.593 + t * 0.008  # average Z = 1.597 (0.012 above 1.585)
            y_surf = face_surface_y(x_new, z_line)
            v.co.x = x_new
            v.co.z = z_line + (v.co.z - z_avg) * 0.9
            v.co.y = y_surf - 0.0032 + (v.co.y - y_avg) * 0.5
    brows_obj.data.update()

# 3. Reshape Capelli_Scuri so it frames the face cleanly (no clumps inside the cheeks or below Z=1.606 on forehead)
#    and has full volume at the top/sides (0.19 wide at top, Z=1.70, sides ending at Z=1.50, back at Z=1.48)
capelli_obj = bpy.data.objects.get("Capelli_Scuri")
if capelli_obj:
    bm = bmesh.new()
    bm.from_mesh(capelli_obj.data)
    bm.faces.ensure_lookup_table()

    # Keep only the original clumps/cap and rebuild the extra clumps cleanly so they don't cover the face
    visited = set()
    comps = []
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
        comps.append(comp)

    # Remove the 12 extra clumps added in rev2 (they are the last 12 components) and replace them with better-positioned clumps
    if len(comps) > 27:
        for comp in comps[27:]:
            bmesh.ops.delete(bm, geom=comp, context='FACES')

    # Push any vertex of existing clumps out of the face mask (front face is |x| < 0.062, y < -0.055, z < 1.608)
    for v in bm.verts:
        # Ensure hair sits outside the skull
        if v.co.z > 1.50:
            dx = v.co.x / 0.078
            dy = v.co.y / 0.098
            dz = (v.co.z - 1.57) / 0.098
            r_ell = math.sqrt(dx * dx + dy * dy + dz * dz)
            if r_ell < 1.02 and v.co.y > -0.075:
                s_push = 1.03 / max(0.2, r_ell)
                v.co.x *= s_push
                v.co.y *= s_push
        # Keep the face area clear below eyebrows (Z < 1.608, Y < -0.055)
        if v.co.y < -0.050 and v.co.z < 1.608 and abs(v.co.x) < 0.062:
            if abs(v.co.x) < 0.038:
                v.co.z = max(v.co.z, 1.608)
            else:
                v.co.x = math.copysign(max(abs(v.co.x), 0.065), v.co.x)

    def add_clump(bm_t, pts, rads):
        segs = 8
        rings = []
        n = len(pts)
        for i in range(n):
            c = Vector(pts[i])
            rx, ry = rads[i]
            if i == 0:
                t = (Vector(pts[1]) - c).normalized()
            elif i == n - 1:
                t = (c - Vector(pts[-2])).normalized()
            else:
                t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
            up = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
            b1 = t.cross(up).normalized()
            b2 = b1.cross(t).normalized()
            ring = [bm_t.verts.new(c + b1 * (rx * math.cos(2 * math.pi * j / segs)) + b2 * (ry * math.sin(2 * math.pi * j / segs))) for j in range(segs)]
            rings.append(ring)
        for i in range(n - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm_t.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True

    # Wavy messy clumps: top crown (reaching Z=1.70 and X=+-0.095 -> 0.19 wide),
    # forehead fringe (down to Z=1.608 just above eyebrows), temples/sides (covering ears, ending at Z=1.50),
    # and back nape (ending at Z=1.48 with uneven points)
    new_clumps = [
        # Forehead fringe locks (stop at Z=1.608 just above eyebrows)
        [(-0.025, -0.035, 1.690), (-0.038, -0.082, 1.662), (-0.044, -0.096, 1.632), (-0.036, -0.097, 1.609)],
        [( 0.008, -0.035, 1.692), ( 0.024, -0.082, 1.664), ( 0.032, -0.096, 1.634), ( 0.025, -0.097, 1.609)],
        # Temple locks framing face outside the eyes and flaring out at Z=1.51..1.54
        [(-0.035, -0.030, 1.686), (-0.068, -0.072, 1.648), (-0.084, -0.068, 1.590), (-0.092, -0.055, 1.525)],
        [( 0.030, -0.030, 1.688), ( 0.068, -0.072, 1.648), ( 0.084, -0.068, 1.590), ( 0.092, -0.055, 1.525)],
        # Side wavy clumps covering ears and ending at Z=1.50, width 0.19 at top
        [(-0.025, -0.005, 1.696), (-0.072, -0.015, 1.675), (-0.095, -0.012, 1.615), (-0.088, -0.010, 1.550), (-0.094, -0.015, 1.500)],
        [( 0.025, -0.005, 1.696), ( 0.072, -0.015, 1.675), ( 0.095, -0.012, 1.615), ( 0.088, -0.010, 1.550), ( 0.094, -0.015, 1.500)],
        [(-0.025,  0.025, 1.694), (-0.075,  0.025, 1.668), (-0.094,  0.028, 1.605), (-0.086,  0.030, 1.545), (-0.091,  0.032, 1.502)],
        [( 0.025,  0.025, 1.694), ( 0.075,  0.025, 1.668), ( 0.094,  0.028, 1.605), ( 0.086,  0.030, 1.545), ( 0.091,  0.032, 1.502)],
        # Top messy crown volume reaching Z=1.70
        [(-0.010,  0.010, 1.700), (-0.052,  0.005, 1.695), (-0.085,  0.005, 1.655), (-0.095,  0.008, 1.605)],
        [( 0.010,  0.010, 1.700), ( 0.052,  0.005, 1.695), ( 0.085,  0.005, 1.655), ( 0.095,  0.008, 1.605)],
        # Back nape clumps ending at Z=1.48 with uneven points
        [(-0.048,  0.070, 1.610), (-0.062,  0.096, 1.545), (-0.068,  0.095, 1.480)],
        [(-0.016,  0.078, 1.605), (-0.022,  0.102, 1.540), (-0.025,  0.100, 1.478)],
        [( 0.016,  0.078, 1.605), ( 0.022,  0.102, 1.540), ( 0.025,  0.100, 1.482)],
        [( 0.048,  0.070, 1.610), ( 0.062,  0.096, 1.545), ( 0.068,  0.095, 1.480)],
    ]
    for pts in new_clumps:
        if len(pts) == 3:
            rads = [(0.014, 0.011), (0.018, 0.013), (0.003, 0.003)]
        elif len(pts) == 4:
            rads = [(0.012, 0.009), (0.019, 0.014), (0.015, 0.011), (0.003, 0.003)]
        else:
            rads = [(0.014, 0.010), (0.020, 0.015), (0.019, 0.014), (0.014, 0.010), (0.003, 0.003)]
        add_clump(bm, pts, rads)

    # Clamp hair width to 0.19 ([-0.095, +0.095]) and max Z to 1.700
    for v in bm.verts:
        v.co.x = max(-0.095, min(0.095, v.co.x))
        v.co.z = min(1.700, v.co.z)

    bm.normal_update()
    bm.to_mesh(capelli_obj.data)
    bm.free()
    capelli_obj.data.update()

# 4. Fix Ciocca_Bianca so it is completely smooth (no pinched triangles!), starting at parting X=-0.03
#    on her RIGHT forehead (-X), about 0.03 wide, and going back over the top of the head
bianca_obj = bpy.data.objects.get("Ciocca_Bianca")
if bianca_obj:
    bm = bmesh.new()
    bm.from_mesh(bianca_obj.data)
    # Instead of distorting individual decimated vertices, place the existing islands cleanly and add 2 smooth arches
    # Wait: let's reshape each connected component in Ciocca_Bianca as a clean tube or convex hull without self-intersection
    bmesh.ops.delete(bm, geom=bm.verts[:], context='VERTS')

    def add_white_clump(bm_t, pts, rads):
        segs = 10
        rings = []
        n = len(pts)
        for i in range(n):
            c = Vector(pts[i])
            rx, ry = rads[i]
            if i == 0:
                t = (Vector(pts[1]) - c).normalized()
            elif i == n - 1:
                t = (c - Vector(pts[-2])).normalized()
            else:
                t = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
            up = Vector((0, 0, 1)) if abs(t.z) < 0.85 else Vector((1, 0, 0))
            b1 = t.cross(up).normalized()
            b2 = b1.cross(t).normalized()
            ring = [bm_t.verts.new(c + b1 * (rx * math.cos(2 * math.pi * j / segs)) + b2 * (ry * math.sin(2 * math.pi * j / segs))) for j in range(segs)]
            rings.append(ring)
        for i in range(n - 1):
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[i][j], rings[i][jn], rings[i + 1][jn], rings[i + 1][j]))
                f.smooth = True
        for idx, inv in ((0, True), (-1, False)):
            c_pt = sum((v.co for v in rings[idx]), Vector((0, 0, 0))) / segs
            cv = bm_t.verts.new(c_pt)
            for j in range(segs):
                jn = (j + 1) % segs
                f = bm_t.faces.new((rings[idx][jn], rings[idx][j], cv) if inv else (rings[idx][j], rings[idx][jn], cv))
                f.smooth = True

    # Clump 1: Starts at parting X = -0.03 on her right forehead (-X) and sweeps back over the top of the head
    # (visible on top in back drawing, slightly to the left of the back picture = +X/+Y crown, and also on -X forehead)
    add_white_clump(
        bm,
        [
            (-0.038, -0.098, 1.615),  # forehead lock tip on her right side (-X)
            (-0.032, -0.092, 1.658),  # parting at X = -0.03
            (-0.025, -0.055, 1.694),  # front crown
            (-0.005,  0.010, 1.700),  # top of head
            ( 0.018,  0.075, 1.682),  # back crown (slightly left in back picture)
            ( 0.024,  0.104, 1.630),  # upper back of head
        ],
        [(0.004, 0.003), (0.015, 0.010), (0.016, 0.011), (0.016, 0.010), (0.014, 0.009), (0.004, 0.003)]
    )
    # Clump 2: Companion lock on her right forehead/temple (-X), starting at parting X = -0.03 and going back & right (-X)
    add_white_clump(
        bm,
        [
            (-0.030, -0.082, 1.672),
            (-0.048, -0.088, 1.655),
            (-0.064, -0.072, 1.622),
            (-0.074, -0.048, 1.582),
        ],
        [(0.010, 0.008), (0.014, 0.010), (0.012, 0.008), (0.003, 0.003)]
    )

    bm.normal_update()
    bm.to_mesh(bianca_obj.data)
    bm.free()
    bianca_obj.data.update()

bpy.ops.wm.save_mainfile()
render_viste("rev_2")
