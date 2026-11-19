import bpy

# Svuota la scena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Crea un cubo (lato 2m, da z=0 a z=2 se centrato a z=1)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 1.0))
cubo = bpy.context.active_object
cubo.name = "Cubo"

# Crea una sfera sopra il cubo (raggio 0.8m, centrata a z=2.8)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0.0, 0.0, 2.8))
sfera = bpy.context.active_object
sfera.name = "Sfera"

# Crea una luce del sole
bpy.ops.object.light_add(type='SUN', location=(4.0, -4.0, 8.0))
sole = bpy.context.active_object
sole.name = "Sole"
sole.data.energy = 3.0
sole.rotation_euler = (0.6, 0.2, 0.8)

# Scrive nel log i nomi degli oggetti
nomi_oggetti = [obj.name for obj in bpy.data.objects]
log("Oggetti nella scena:", nomi_oggetti)

# Chiama render_viste
render_viste("prova", viste=["fronte", "tre_quarti"])
