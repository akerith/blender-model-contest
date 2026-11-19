exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 3 - neck, shirt collar, cape collar (the existing stand-up collar is re-shaped through its UVs)
Mn = bpy.data.objects["Mantello"]
me = Mn.data
uv = {}
for l in me.loops:
    uv[l.vertex_index] = me.uv_layers[0].data[l.index].uv.copy()
n = 0
for isl in islands(Mn):
    if len(isl["v"]) > 200:
        continue
    inner = isl["mat"] == "mantello_interno"
    for i in isl["v"]:
        u, v = uv[i].x, 1 - uv[i].y
        th = (2 * u - 1) * 140
        top = 1.52 - 0.04 * (abs(th) / 140) ** 1.5      # 1.52 at the back, 1.48 at the front corners
        z = 1.40 + v * (top - 1.40)
        off = -0.006 if inner else 0.0
        rx, ry = 0.090 + 0.034 * v + off, 0.086 + 0.036 * v + off   # leans out
        me.vertices[i].co = Vector((rx * math.sin(rad(th)), 0.004 + ry * math.cos(rad(th)), z))
        n += 1
me.update()
log("cape collar vertices re-shaped:", n)
# neck: 0.11 wide between 1.45 and 1.49
idx = pick("Corpo", "pelle")
lo, hi = bbox("Corpo", idx)
log("neck box before", [round(x, 3) for x in lo], [round(x, 3) for x in hi])
move("Corpo", idx, lambda p: Vector((p.x * 0.11 / (hi.x - lo.x), p.y * 0.11 / (hi.y - lo.y) * 0.95, p.z + (0.01 if p.z > 1.44 else 0))))
# shirt collar: high grey-blue band around the neck, 1.41 .. 1.46 (new piece)
ring = g_loft([((0, 0.002, 1.405), 0.071, 0.068), ((0, 0.0, 1.435), 0.064, 0.062), ((0, -0.002, 1.462), 0.0605, 0.059),
               ((0, -0.002, 1.462), 0.054, 0.053)], n=16, cap0=False, cap1=False, axes=((1, 0, 0), (0, 1, 0)))
new("colletto_camicia", ring, "camicia", 0)
salva()
render_viste("rev_3", viste=["fronte", "destra", "retro"])
shot("rev_3_collo", (0, 0, 1.45), 0.5, d=(0.5, -1, 0.3))
