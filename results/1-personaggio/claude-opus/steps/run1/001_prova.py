import bpy

# empty the scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for coll in (bpy.data.meshes, bpy.data.lights, bpy.data.materials):
    for item in list(coll):
        if item.users == 0:
            coll.remove(item)

# cube with a sphere on top
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
bpy.context.object.name = "Cubo"
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 1.4))
bpy.context.object.name = "Sfera"
bpy.ops.object.shade_smooth()

# sun light
bpy.ops.object.light_add(type="SUN", location=(3, -3, 5))
sole = bpy.context.object
sole.name = "Sole"
sole.data.energy = 3.0
sole.rotation_euler = (0.8, 0.2, 0.6)

log("oggetti: " + ", ".join(o.name for o in bpy.context.scene.objects))
render_viste("prova", viste=["fronte", "tre_quarti"])
