import math
import bmesh
from mathutils import Vector

O = bpy.data.objects
def clamp(v, a, b): return max(a, min(b, v))
def setmat(o, nm):
    o.data.materials.clear(); o.data.materials.append(bpy.data.materials[nm])
def boot_r(z): return 0.045 + (0.060 - 0.045) * clamp((z - 0.08) / 0.34, 0, 1)

def boot_part(s, sd):
    cx = sd * 0.13
    b = O["Stivale." + s]
    for v in b.data.vertices:
        x, y, z = v.co
        if z > 0.055:
            zn = 0.06 + (z - 0.06) * 1.2
            rr = math.sqrt((x - cx) ** 2 + y * y)
            if rr > 1e-5:
                k = boot_r(zn) / 0.072
                x = cx + (x - cx) * k; y = y * k
            z = zn
        else:
            y = (y + 0.06) * 1.04 - 0.06
        v.co = (x, y, z)
    b.data.update()
    bev = b.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.008; bev.segments = 2; bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(40)
    bpy.context.view_layer.objects.active = b
    bpy.ops.object.modifier_apply(modifier=bev.name)
    setmat(b, "Stivali")
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, -0.055, 0.01))
    so = bpy.context.active_object
    so.name = "Suola." + s; so.scale = (0.105, 0.28, 0.02)
    setmat(so, "Suola")
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0.05, 0.015))
    he = bpy.context.active_object
    he.name = "Tacco." + s; he.scale = (0.09, 0.07, 0.03)
    setmat(he, "Suola")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.04, vertices=14, location=(cx, 0, 0.40))
    cu = bpy.context.active_object
    cu.name = "StivaleRisvolto." + s
    setmat(cu, "Stivali"); bpy.ops.object.shade_smooth()
    for i in range(8):
        z = 0.10 + i * (0.30 / 7)
        yf = -boot_r(z) - 0.002
        for sx in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.006, vertices=6, location=(cx + sx * 0.015, yf, z), rotation=(math.radians(90), 0, 0))
            e = bpy.context.active_object
            e.name = "Occhiello.%s.%d.%d" % (s, i, sx)
            setmat(e, "OttoneScuro")
        if i < 7:
            z2 = 0.10 + (i + 1) * (0.30 / 7)
            yf2 = -boot_r(z2) - 0.004
            for sx in (-1, 1):
                p1 = Vector((cx + sx * 0.015, yf, z)); p2 = Vector((cx - sx * 0.015, yf2, z2))
                d = p2 - p1
                bpy.ops.mesh.primitive_cylinder_add(radius=0.002, depth=d.length, vertices=6, location=(p1 + p2) / 2)
                lc = bpy.context.active_object
                lc.name = "LaccioX.%s.%d.%d" % (s, i, sx)
                lc.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
                setmat(lc, "Laccio")

def rest_part(s, sd):
    cx = sd * 0.13
    rings = sorted([O[n] for n in O.keys() if n.startswith("Laccio.%s." % s)], key=lambda o: o.bound_box[0][2])
    for o, z, R in ((rings[0], 0.09, boot_r(0.09) + 0.004), (rings[1], 0.38, boot_r(0.38) + 0.004), (rings[2], 0.56, 0.060)):
        for v in o.data.vertices:
            x, y, zz = v.co
            th = math.atan2(y, x)
            ring = Vector((0.074 * math.cos(th), 0.074 * math.sin(th), 0))
            off = Vector((x, y, zz)) - ring
            v.co = ring * (R / 0.074) + off
        o.data.update()
        cs = [Vector(c) for c in o.bound_box]
        cc = (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2
        for v in o.data.vertices: v.co = Vector(v.co) - cc + Vector((cx, 0, z))
        o.data.update()
        setmat(o, "CuoioScuro")
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, -boot_r(z) - 0.008, z))
        fb = bpy.context.active_object
        fb.name = "StivaleFibbia.%s.%.2f" % (s, z)
        fb.scale = (0.012, 0.008, 0.015)
        setmat(fb, "Ottone")
    k = O["Ginocchiera." + s]
    cs = [Vector(c) for c in k.bound_box]
    cc = (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2
    for v in k.data.vertices:
        v.co = (Vector(v.co) - cc) * Vector((1.0, 0.38, 1.0)) + Vector((cx, -0.075, 0.50))
    k.data.update()
    for z in (0.44, 0.56):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.058, minor_radius=0.005, major_segments=12, minor_segments=5, location=(cx, 0, z))
        t = bpy.context.active_object
        t.name = "GinocchieraFascia.%s.%.2f" % (s, z)
        setmat(t, "CuoioScuro"); bpy.ops.object.shade_smooth()
    fa = O["Fascia." + s]
    cs = [Vector(c) for c in fa.bound_box]
    cc = (Vector([min(c[i] for c in cs) for i in range(3)]) + Vector([max(c[i] for c in cs) for i in range(3)])) / 2
    for v in fa.data.vertices: v.co = Vector(v.co) - cc + Vector((cx, 0, 0.43))
    fa.data.update()
    for z in (0.41, 0.45):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.058, minor_radius=0.010, major_segments=12, minor_segments=5, location=(cx, 0, z))
        t = bpy.context.active_object
        t.name = "FasciaExtra.%s.%.2f" % (s, z)
        setmat(t, "Manica"); bpy.ops.object.shade_smooth()
    for z in (0.47, 0.51, 0.55):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.056, minor_radius=0.004, major_segments=12, minor_segments=4, location=(cx, 0, z))
        t = bpy.context.active_object
        t.name = "Piega.%s.%.2f" % (s, z)
        bm = bmesh.new(); bm.from_mesh(t.data)
        kill = [v for v in bm.verts if v.co.y < -0.01]
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        bm.to_mesh(t.data); bm.free(); t.data.update()
        setmat(t, "Pantaloni"); bpy.ops.object.shade_smooth()

boot_part("R", -1)
rest_part("L", 1)
rest_part("R", -1)
bpy.ops.wm.save_mainfile()
render_viste("rev_8", viste=["fronte", "destra", "tre_quarti"])
