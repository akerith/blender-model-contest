bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.context.object.name = 'Cubo'

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(0, 0, 2.75))
bpy.context.object.name = 'Sfera'

bpy.ops.object.light_add(type='SUN', location=(4, -4, 6))
bpy.context.object.name = 'Sole'
bpy.context.object.rotation_euler = (0.45, -0.45, -0.4)
bpy.context.object.data.energy = 3

log('Oggetti della scena: ' + ', '.join(sorted(obj.name for obj in bpy.context.scene.objects)))
render_viste("prova", viste=["fronte", "tre_quarti"])
