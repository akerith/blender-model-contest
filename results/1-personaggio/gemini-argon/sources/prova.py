import bpy

# Svuota la scena rimuovendo tutti gli oggetti esistenti
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Crea un cubo
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 1.0))
cubo = bpy.context.view_layer.objects.active
cubo.name = "Cubo"

# Crea una sfera sopra il cubo
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0.0, 0.0, 2.8))
sfera = bpy.context.view_layer.objects.active
sfera.name = "Sfera"

# Crea una luce del sole
bpy.ops.object.light_add(type='SUN', location=(4.0, -4.0, 8.0))
sole = bpy.context.view_layer.objects.active
sole.name = "Sole"
sole.data.energy = 3.0
sole.rotation_euler = (0.6, 0.2, 0.8)

# Scrive nel log i nomi degli oggetti
nomi_oggetti = [obj.name for obj in bpy.data.objects]
log("Oggetti nella scena:", nomi_oggetti)

# Chiama render_viste
render_viste("prova", viste=["fronte", "tre_quarti"])
