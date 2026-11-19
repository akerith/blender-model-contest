import bpy
import bmesh
import math
from mathutils import Vector

# Group 3: Neck, shirt collar and stiff tall stand-up cape collar

def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def set_mat_srgb(name, col_srgb, roughness=0.88, metallic=0.0, spec=0.25):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Clear any old links so Base Color shows accurate sRGB->linear color
        for lnk in list(mat.node_tree.links):
            if lnk.to_socket == bsdf.inputs["Base Color"]:
                mat.node_tree.links.remove(lnk)
        lin = tuple(srgb_to_lin(x) for x in col_srgb)
        bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat

mat_shirt_collar = set_mat_srgb("CollettoCamicia", (0.30, 0.33, 0.38), roughness=0.88)
mat_cape         = set_mat_srgb("MantelloVerde", (0.22, 0.34, 0.31), roughness=0.90)

# Clamp Capelli max Z to exact 1.700 m
ob_hair = bpy.data.objects.get("Capelli")
if ob_hair:
    for v in ob_hair.data.vertices:
        if v.co.z > 1.700:
            v.co.z = 1.700
    ob_hair.data.update()

# 1. Shirt collar (Z 1.41 to 1.46) inside TunicaManiche
#    Keep TunicaManiche's jacket & sleeves intact for Group 4/5, replace its old inner beige collar (z>1.37 & r<0.075)
ob_tm = bpy.data.objects.get("TunicaManiche")
if ob_tm:
    bm_t = bmesh.new()
    bm_t.from_mesh(ob_tm.data)

    # Remove old inner collar vertices (above z=1.39 and within radius 0.085 of neck center)
    del_verts = [v for v in bm_t.verts if v.co.z > 1.385 and (v.co.x ** 2 + v.co.y ** 2) ** 0.5 < 0.085]
    if del_verts:
        bmesh.ops.delete(bm_t, geom=del_verts, context='VERTS')

    # Add mat_shirt_collar slot if not present
    if mat_shirt_collar.name not in [m.name for m in ob_tm.data.materials if m]:
        ob_tm.data.materials.append(mat_shirt_collar)
    collar_mat_idx = [m.name for m in ob_tm.data.materials].index(mat_shirt_collar.name)

    # Build wrapped high shirt collar (Z 1.41 to 1.46) with front V-overlap notch and thickness
    nu_c = 28
    nv_c = 4
    grid_c = []
    for iv in range(nv_c + 1):
        tv = iv / nv_c
        z_base = 1.405 + tv * 0.055  # 1.405 .. 1.460
        row = []
        for iu in range(nu_c + 1):
            u = -1.0 + 2.0 * (iu / nu_c)  # -1 (front-right) .. 0 (back +Y) .. +1 (front-left)
            ang = u * math.radians(172)   # small front opening at -Y
            rx = 0.066 - 0.004 * tv
            ry = 0.064 - 0.004 * tv
            # Subtle V-notch dip at front corners
            z = z_base - 0.012 * (max(0.0, abs(u) - 0.78) / 0.22) * tv
            x = rx * math.sin(ang)
            y = ry * math.cos(ang)
            row.append(bm_t.verts.new(Vector((x, y, z))))
        grid_c.append(row)

    collar_faces = []
    for iv in range(nv_c):
        for iu in range(nu_c):
            f = bm_t.faces.new((grid_c[iv][iu], grid_c[iv][iu + 1], grid_c[iv + 1][iu + 1], grid_c[iv + 1][iu]))
            f.material_index = collar_mat_idx
            collar_faces.append(f)

    bmesh.ops.solidify(bm_t, geom=collar_faces, thickness=0.005)
    bmesh.ops.recalc_face_normals(bm_t, faces=bm_t.faces[:])
    bm_t.to_mesh(ob_tm.data)
    bm_t.free()
    for p in ob_tm.data.polygons:
        p.use_smooth = True
    ob_tm.data.update()

# 2. Cape tall stand-up collar (Z 1.40 -> 1.52 at back, 1.48 at front corners, leaning out, open at front)
#    Update upper collar region of MantelloVerde (retaining lower cape until Group 6)
ob_cape = bpy.data.objects.get("MantelloVerde")
if ob_cape:
    bm_c = bmesh.new()
    bm_c.from_mesh(ob_cape.data)

    # Remove old tight collar faces at z > 1.395 near neck
    del_c = [v for v in bm_c.verts if v.co.z > 1.395 and (v.co.x ** 2 + v.co.y ** 2) ** 0.5 < 0.13]
    if del_c:
        bmesh.ops.delete(bm_c, geom=del_c, context='VERTS')

    # Build stiff, tall flared stand-up cape collar around back and sides, open at front
    # Rises from shoulder seam (Z 1.40) to Z 1.52 at back (+Y) and Z 1.48 at front corners (+-132 deg)
    nu = 32
    nv = 5
    grid = []
    for iv in range(nv + 1):
        tv = iv / nv  # 0 = base (Z 1.39..1.40), 1 = top edge (Z 1.52 back, 1.48 front corners)
        row = []
        for iu in range(nu + 1):
            u = -1.0 + 2.0 * (iu / nu)  # -1 (front-right corner) .. 0 (back) .. +1 (front-left corner)
            max_ang = math.radians(130 + 6 * tv)  # open front gap ~100 deg at front
            ang = u * max_ang
            # Base radius hugs shoulders outside shirt collar (0.085), top flares outward (0.122 X, 0.110 Y)
            rx = 0.086 + 0.036 * (tv ** 0.9)
            ry = 0.082 + 0.026 * (tv ** 0.9)
            # Height: 1.395 at base -> 1.52 at back (u=0), 1.48 at front corners (|u|=1)
            z_top = 1.520 - 0.040 * (abs(u) ** 1.4)
            z_bot = 1.392 - 0.005 * abs(u)
            z = z_bot + (z_top - z_bot) * tv
            # Subtle fabric ripple along collar
            ripple = 0.003 * math.sin(u * 10.0) * tv
            x = (rx + ripple) * math.sin(ang)
            y = 0.005 + (ry + ripple) * math.cos(ang)
            row.append(bm_c.verts.new(Vector((x, y, z))))
        grid.append(row)

    col_faces = []
    for iv in range(nv):
        for iu in range(nu):
            f = bm_c.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
            f.material_index = 0
            col_faces.append(f)

    bmesh.ops.solidify(bm_c, geom=col_faces, thickness=0.007)
    bmesh.ops.recalc_face_normals(bm_c, faces=bm_c.faces[:])

    ob_cape.data.materials.clear()
    ob_cape.data.materials.append(mat_cape)
    bm_c.to_mesh(ob_cape.data)
    bm_c.free()
    for p in ob_cape.data.polygons:
        p.use_smooth = True
    ob_cape.data.update()

log("Group 3 complete: Neck, shirt collar (1.41..1.46), tall cape collar (1.40..1.52 back / 1.48 front).")
bpy.ops.wm.save_mainfile()
render_viste("rev_3")
