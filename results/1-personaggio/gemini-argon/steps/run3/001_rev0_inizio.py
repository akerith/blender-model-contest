import bpy

log("=== LISTA OGGETTI IN SCENA (rev_inizio) ===")
total_tris = 0
for obj in bpy.data.objects:
    tris = 0
    if obj.type == 'MESH' and obj.data:
        obj.data.calc_loop_triangles()
        tris = len(obj.data.loop_triangles)
        total_tris += tris
    loc = tuple(round(c, 4) for c in obj.location)
    dim = tuple(round(c, 4) for c in obj.dimensions)
    log(f"Oggetto: {obj.name} | Tipo: {obj.type} | Triangoli: {tris} | Location: {loc} | Dimensions: {dim}")

log(f"Totale triangoli scena: {total_tris}")
render_viste("rev_inizio")
