import bpy
scn = bpy.context.scene
bpy.data.objects["Sole"].data.energy = 2.2
w = scn.world
w.node_tree.nodes["Background"].inputs[1].default_value = 0.75
bpy.ops.wm.save_mainfile()
render_viste("finale_revisione_personaggio")
log("Luce ribilanciata: sole 2.2, world 0.75")
