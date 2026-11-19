import math

cols, rows = 29, 20
verts, faces = [], []
for i in range(rows):
    t = i / (rows - 1)
    for j in range(cols):
        th = math.radians(-125 + 250 * j / (cols - 1))
        hem = 0.78 + 0.10 * abs(math.sin(j * 0.9))
        if j % 4 == 2:
            hem += 0.06
        if j in (5, 12, 20, 24):
            hem += 0.12
        r = 0.20 + 0.16 * t + 0.012 * math.sin(th * 6 + t * 2)
        z = 1.45 - t * (1.45 - hem)
        x = r * math.sin(th)
        y = 0.02 + r * math.cos(th) * 0.9
        verts.append((x, y, z))
for i in range(rows - 1):
    for j in range(cols - 1):
        a = i * cols + j
        faces.append((a, a + 1, a + 1 + cols, a + cols))

mesh = bpy.data.meshes.new("Mantello")
mesh.from_pydata(verts, [], faces)
mesh.update()
ob = bpy.data.objects.new("Mantello", mesh)
bpy.context.scene.collection.objects.link(ob)
ob.data.materials.append(bpy.data.materials["Mantello"])
ob.data.materials.append(bpy.data.materials["MantelloInt"])
sol = ob.modifiers.new("Sol", 'SOLIDIFY')
sol.thickness = 0.012
sol.material_offset = 1
sol.use_rim = True
bpy.context.view_layer.objects.active = ob
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.object.shade_smooth()
ob["bone"] = "chest"
log("Tri mantello:", sum(len(p.vertices) - 2 for p in ob.data.polygons))

render_viste("p05_mantello", viste=["fronte", "retro", "tre_quarti"])
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\USER\gara-modelli\concorrenti\qwen-max\lavoro\personaggio.blend")