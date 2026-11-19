exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# check: is the new cape texture really on the cape? (the streaks were not visible in the back view)
import numpy as np
m = bpy.data.materials["mantello"]
for n in m.node_tree.nodes:
    if n.type == "TEX_IMAGE":
        img = n.image
        log("node image:", img.name, tuple(img.size), img.filepath_raw, "packed", bool(img.packed_file), img.colorspace_settings.name)
        px = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        px = px.reshape(img.size[1], img.size[0], 4)
        row = px[int(img.size[1] * 0.6), ::16, :3]
        log("row at v=0.6, G channel:", " ".join("%.2f" % x for x in row[:, 1]))
Mn = bpy.data.objects["Mantello"]
uv = Mn.data.uv_layers
log("uv layers:", [(u.name, u.active, u.active_render) for u in uv])
us = [uv[0].data[l.index].uv.x for l in Mn.data.loops]
vs = [uv[0].data[l.index].uv.y for l in Mn.data.loops]
log("uv range u %.3f..%.3f v %.3f..%.3f" % (min(us), max(us), min(vs), max(vs)))
shot("rev_13_mantello_retro", (0, 0.2, 0.75), 1.3, d=(0.25, 1, 0.15))
