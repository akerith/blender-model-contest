import bpy

# Svuota la scena
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Crea un cubo
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.5))
cubo = bpy.context.active_object
cubo.name = "Cubo"

# Crea una sfera sopra il cubo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0.0, 0.0, 1.5))
sfera = bpy.context.active_object
sfera.name = "Sfera"

# Crea una luce del sole
bpy.ops.object.light_add(type='SUN', location=(3.0, -3.0, 5.0))
sole = bpy.context.active_object
sole.name = "Sole"
sole.data.energy = 3.0
sole.rotation_euler = (0.6, 0.2, 0.5)

# Scrive nel log i nomi degli oggetti
log("Oggetti in scena:", [obj.name for obj in bpy.data.objects])

# Renderizza le viste richieste
render_viste("prova", viste=["fronte", "tre_quarti"])
