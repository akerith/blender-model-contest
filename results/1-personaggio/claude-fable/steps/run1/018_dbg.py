o = bpy.data.objects["Personaggio"]
me = o.data
log("uv layers:", [u.name for u in me.uv_layers], "active:", me.uv_layers.active.name if me.uv_layers.active else None)
uvl = me.uv_layers[0]
import random
idx = [i for i, p in enumerate(me.polygons) if me.materials[p.material_index].name == "mantello"]
log("cape polys:", len(idx))
for i in idx[:3] + idx[2000:2003]:
    p = me.polygons[i]
    log([tuple(round(c, 3) for c in uvl.data[li].uv) for li in p.loop_indices])
m = bpy.data.materials["mantello"]
for n in m.node_tree.nodes:
    log(n.type, n.name, [(l.from_node.name, l.to_socket.name) for l in m.node_tree.links if l.to_node == n])
t = [n for n in m.node_tree.nodes if n.type == "TEX_IMAGE"][0]
log(t.image, t.image.size[:], t.image.has_data, t.image.colorspace_settings.name)
