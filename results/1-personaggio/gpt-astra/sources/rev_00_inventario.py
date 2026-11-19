for ob in sorted(bpy.context.scene.objects, key=lambda ob: ob.name):
    triangles = 0
    if ob.type == 'MESH':
        ob.data.calc_loop_triangles()
        triangles = len(ob.data.loop_triangles)
    log(ob.name, ob.type, 'triangles', triangles, 'location', tuple(ob.location), 'dimensions', tuple(ob.dimensions))
render_viste('rev_inizio')
