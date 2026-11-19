import math

# svuota la scena
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# cubo (lato 1 m, appoggiato a terra)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
cubo = bpy.context.object
cubo.name = "Cubo"

# sfera sopra il cubo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 1.4))
sfera = bpy.context.object
sfera.name = "Sfera"
bpy.ops.object.shade_smooth()

# luce del sole
bpy.ops.object.light_add(type='SUN', location=(3, -3, 5),
                         rotation=(math.radians(45), 0, math.radians(35)))
sole = bpy.context.object
sole.name = "Sole"
sole.data.energy = 3.0

log("Oggetti nella scena:")
for ob in bpy.data.objects:
    log(" -", ob.name, ob.type)

render_viste("prova", viste=["fronte", "tre_quarti"])
log("Render fatti in", OUTBOX)
