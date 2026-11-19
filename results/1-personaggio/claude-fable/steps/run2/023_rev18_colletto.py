exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# FIX: in group 6 the stand-up collar was moved together with the cape by mistake (it became a coarse sheet inside
# the cape). Its columns (u) and rows are still readable from the UVs: back to the collar shape of group 3.
Mn = bpy.data.objects["Mantello"]
me = Mn.data
uvd = me.uv_layers[0].data
loops_of = {}
for l in me.loops:
    loops_of.setdefault(l.vertex_index, []).append(l.index)
n = 0
for isl in islands(Mn):
    if len(isl["v"]) != 76:
        continue
    inner = isl["mat"] == "mantello_interno"
    for i in isl["v"]:
        uv = uvd[loops_of[i][0]].uv
        u = uv.x
        r = round((1 - uv.y) / (0.98 if 0.2499 < u < 0.7501 else 0.30) * 3)
        v = max(0, min(3, r)) / 3
        th = (2 * u - 1) * 140
        top = 1.52 - 0.04 * (abs(th) / 140) ** 1.5      # 1.52 at the back, 1.48 at the front corners
        z = 1.40 + v * (top - 1.40)
        off = -0.006 if inner else 0.0
        rx, ry = 0.090 + 0.034 * v + off, 0.086 + 0.036 * v + off
        me.vertices[i].co = Vector((rx * math.sin(rad(th)), 0.004 + ry * math.cos(rad(th)), z))
        for li in loops_of[i]:
            uvd[li].uv.y = 0.74 + 0.2 * (1 - v)       # teal part of the cape texture
        n += 1
me.update()
log("collar vertices put back:", n)
for isl in islands(Mn):
    if len(isl["v"]) == 76:
        log("collar box", [round(x, 3) for x in isl["lo"]], [round(x, 3) for x in isl["hi"]])
salva()
render_viste("rev_18", viste=["fronte", "retro"])
shot("rev_18_collo", (0, 0, 1.45), 0.5, d=(0.5, -1, 0.3))
shot("rev_18_fianco_dx", (-0.18, 0, 0.88), 0.5, d=(-0.6, -1, 0.15))
