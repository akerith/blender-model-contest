import bpy

depsgraph = bpy.context.evaluated_depsgraph_get()
total_tris = 0
log("=== OBJECT LIST ===")
for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    tris = 0
    if obj.type == "MESH":
        eval_obj = obj.evaluated_get(depsgraph)
        me = eval_obj.to_mesh()
        me.calc_loop_triangles()
        tris = len(me.loop_triangles)
        eval_obj.to_mesh_clear()
        total_tris += tris
    loc = tuple(round(v, 4) for v in obj.location)
    dim = tuple(round(v, 4) for v in obj.dimensions)
    log(f"{obj.name} | type={obj.type} | tris={tris} | loc={loc} | dim={dim}")
log(f"TOTAL_TRIS={total_tris}")

render_viste("rev_inizio")
