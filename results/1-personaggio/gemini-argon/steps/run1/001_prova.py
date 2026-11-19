import bpy

# Svuota la scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Crea un cubo
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
cubo = bpy.context.active_object
cubo.name = "Cubo"

# Crea una sfera sopra il cubo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 2.8))
sfera = bpy.context.active_object
sfera.name = "Sfera"

# Crea una luce del sole
bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sole = bpy.context.active_object
sole.name = "Sole"
sole.rotation_euler = (0.6, 0.2, 0.5)

# Scrive nel log i nomi degli oggetti
nomi = [obj.name for obj in bpy.data.objects]
log("Oggetti nella scena:", ", ".join(nomi))

# Chiama render_viste
render_viste("prova", viste=["fronte", "tre_quarti"])
