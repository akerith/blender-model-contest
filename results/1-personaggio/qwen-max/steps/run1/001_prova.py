for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cubo = bpy.context.active_object
cubo.name = "Cubo"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 2.8))
sfera = bpy.context.active_object
sfera.name = "Sfera"

bpy.ops.object.light_add(type='SUN', location=(0, 0, 6))
sole = bpy.context.active_object
sole.name = "Sole"
sole.data.energy = 3

log("Oggetti in scena:", ", ".join(o.name for o in bpy.data.objects))

render_viste("prova", viste=["fronte", "tre_quarti"])