exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# GROUP 10 (first half) - triangles, materials with the colours of the description, parts joined by the bone they follow
import numpy as np, os
os.makedirs(TEXD, exist_ok=True)

# ---- 10.4 fewer triangles in the cape: every second row of the long part is dissolved (hem and yoke kept) ----
Mn = bpy.data.objects["Mantello"]
me = Mn.data
coll = set(i for isl in islands(Mn) if len(isl["v"]) <= 200 for i in isl["v"])
inner_mi = [k for k, m in enumerate(me.materials) if m.name == "mantello_interno"][0]
t0 = sum(len(p.vertices) - 2 for p in me.polygons)
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
cols = {}
for v in bm.verts:
    if v.index in coll or not v.link_loops:
        continue
    uv = v.link_loops[0][uvl].uv
    if 0.2499 < uv.x < 0.7501:
        cols.setdefault((v.link_faces[0].material_index == inner_mi, int(round(uv.x * 144))), []).append((1 - uv.y, v))
rank, last = {}, {}
for key, lst in cols.items():
    lst.sort(key=lambda x: x[0])
    for r, (_, v) in enumerate(lst):
        rank[v] = r
        last[v] = len(lst) - 1
sel = []
for e in bm.edges:
    a, b = e.verts
    if a in rank and b in rank and rank[a] == rank[b] and rank[a] % 2 == 1 and rank[a] >= 3 \
            and rank[a] < last[a] - 2 and rank[b] < last[b] - 2:
        sel.append(e)
bmesh.ops.dissolve_edges(bm, edges=sel, use_verts=True)
bm.to_mesh(me)
bm.free()
me.update()
log("cape triangles: %d -> %d (edges dissolved %d)" % (t0, sum(len(p.vertices) - 2 for p in me.polygons), len(sel)))


# ---- 10.1 materials ----
def tnoise(n, cells, seed):
    rs = np.random.RandomState(seed)
    g = rs.rand(cells, cells)
    x = np.linspace(0, cells, n, endpoint=False)
    xi = x.astype(int)
    xf = x - xi
    xf = xf * xf * (3 - 2 * xf)
    x1 = (xi + 1) % cells
    a, b, c, d = g[xi][:, xi], g[xi][:, x1], g[x1][:, xi], g[x1][:, x1]
    X, Y = xf[None, :], xf[:, None]
    return (a * (1 - X) + b * X) * (1 - Y) + (c * (1 - X) + d * X) * Y


def tfbm(n, seed):
    return tnoise(n, 4, seed) * 0.42 + tnoise(n, 8, seed + 1) * 0.28 + tnoise(n, 16, seed + 2) * 0.18 + tnoise(n, 48, seed + 3) * 0.12


def make_image(name, rgb):
    n = rgb.shape[0]
    img = bpy.data.images.get(name)
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(name, n, n, alpha=False)
    px = np.ones((n, n, 4), dtype=np.float32)
    px[..., :3] = np.clip(rgb, 0.02, 0.97)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = TEXD + "\\" + name + ".png"
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


def setm(name, rgb, metal, rough, tex=None, alpha=None):
    m = mat(name, lin(rgb), metal, rough)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:
        nt.nodes.remove(n)
    if tex is not None:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = tex
        t.location = (-350, 300)
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    return m


T = 256
tu = np.linspace(0, 1, T, endpoint=False)[None, :].repeat(T, 0)
tv = np.linspace(0, 1, T, endpoint=False)[:, None].repeat(T, 1)


def detail(name, rgb, metal, rough, contrast=0.4, seed=0, weave=0.0, stain=None, amt=0.45, patina=None):
    f1, f2, f3 = tfbm(T, seed + 1), tfbm(T, seed + 11), tfbm(T, seed + 21)
    base = np.array(rgb)
    col = base[None, None, :] * (1 - contrast / 2 + contrast * f1[..., None])
    if weave:
        col = col * (1 + weave * np.sin(tu * 2 * np.pi * 40) * np.sin(tv * 2 * np.pi * 40))[..., None]
    st = base * 0.55 if stain is None else np.array(stain)
    m = np.clip((f2 - 0.55) * 5, 0, 1)[..., None] * amt
    col = col * (1 - m) + st[None, None, :] * m
    if patina is not None:
        m = np.clip((f3 - 0.60) * 6, 0, 1)[..., None] * 0.6
        col = col * (1 - m) + np.array(patina)[None, None, :] * (0.85 + 0.3 * f1[..., None]) * m
    setm(name, rgb, metal, rough, tex=make_image("tex_" + name, col))


BR = (0.62, 0.45, 0.20)
detail("cuoio", (0.34, 0.205, 0.11), 0, 0.65, 0.45, 1)
detail("cuoio_scuro", (0.26, 0.16, 0.09), 0, 0.65, 0.45, 2)
detail("cuoio_cinghie", (0.20, 0.12, 0.07), 0, 0.65, 0.4, 14)
detail("lino", (0.82, 0.76, 0.64), 0, 0.92, 0.22, 3, weave=0.02, stain=(0.62, 0.54, 0.40), amt=0.4)
detail("tela", (0.66, 0.58, 0.45), 0, 0.9, 0.25, 15, weave=0.03, stain=(0.45, 0.38, 0.27), amt=0.4)
detail("pantaloni", (0.22, 0.19, 0.16), 0, 0.9, 0.3, 4, weave=0.02)
detail("tunica", (0.13, 0.16, 0.22), 0, 0.88, 0.3, 5, weave=0.02)
detail("corpetto", (0.13, 0.16, 0.22), 0, 0.85, 0.3, 6, weave=0.015)
detail("camicia", (0.30, 0.33, 0.38), 0, 0.9, 0.22, 12, weave=0.02)
detail("ottone", BR, 1.0, 0.35, 0.3, 7, stain=(0.35, 0.24, 0.10), amt=0.55, patina=(0.36, 0.52, 0.44))
detail("ottone_scuro", (0.52, 0.375, 0.165), 1.0, 0.4, 0.3, 8, stain=(0.35, 0.24, 0.10), amt=0.7, patina=(0.34, 0.50, 0.42))
detail("corda", (0.70, 0.62, 0.47), 0, 0.9, 0.3, 9, stain=(0.50, 0.42, 0.29), amt=0.4)
detail("tubo", (0.24, 0.16, 0.11), 0, 0.6, 0.4, 10)
detail("capelli", (0.10, 0.08, 0.07), 0, 0.5, 0.5, 13)
detail("lacci", (0.55, 0.42, 0.28), 0, 0.8, 0.25, 16)
setm("pelle", (0.85, 0.68, 0.58), 0, 0.6)
setm("capelli_bianchi", (0.80, 0.80, 0.78), 0, 0.5)
setm("bianco", (0.88, 0.85, 0.78), 0, 0.45)
setm("iride", (0.20, 0.12, 0.07), 0, 0.3)
setm("labbra", (0.62, 0.38, 0.34), 0, 0.5)
setm("scuro", (0.12, 0.08, 0.06), 0, 0.8)
setm("vetro", (0.55, 0.70, 0.65), 0.0, 0.08, alpha=0.6)
setm("vetro_verde", (0.25, 0.55, 0.35), 0.0, 0.1, alpha=0.85)
# cape: worn teal, lighter streaks running down, lower part fading to dirty sand with brown stains
N = 512
uu = np.linspace(0, 1, N, endpoint=False)[None, :].repeat(N, 0)
vv = np.linspace(0, 1, N)[:, None].repeat(N, 1)          # 0 = hem, 1 = collar
f1, f2, f3, f4 = [np.kron(tfbm(256, s), np.ones((2, 2))) for s in (31, 41, 51, 61)]
col = np.array((0.22, 0.34, 0.31))[None, None, :] * (0.80 + 0.42 * f1[..., None])
streak = np.clip((np.sin(uu * 2 * np.pi * 21 + f2 * 7 + np.sin(vv * 9) * 0.8) - 0.45) / 0.55, 0, 1) * np.clip((f3 - 0.38) * 3.5, 0, 1) * 0.75
col = col * (1 - streak[..., None]) + np.array((0.40, 0.52, 0.48))[None, None, :] * streak[..., None]
col *= (1 + 0.07 * np.sin(uu * 2 * np.pi * 24 + 1.0))[..., None]              # soft fold shading
d = np.clip((0.25 - vv) / 0.25, 0, 1) ** 0.7 * (0.55 + 0.9 * f3)
d = np.clip(d + np.clip((f4 - 0.62) * 6, 0, 1) * 0.5 * np.clip((0.45 - vv) / 0.45, 0, 1), 0, 0.95)
sand = np.array((0.62, 0.55, 0.43))[None, None, :] * (0.85 + 0.3 * f2[..., None])
st = np.clip((f1 - 0.56) * 7, 0, 1)[..., None] * 0.7
sand = sand * (1 - st) + np.array((0.36, 0.26, 0.16))[None, None, :] * st
col = col * (1 - d[..., None]) + sand * d[..., None]
setm("mantello", (0.22, 0.34, 0.31), 0, 0.92, tex=make_image("tex_mantello", col))
setm("mantello_interno", (0.15, 0.23, 0.21), 0, 0.95, tex=make_image("tex_mantello_interno", col * 0.66))
log("materials:", len([m for m in bpy.data.materials if m.users]))

# ---- parts joined by the bone they follow ----
BASE = {0: "Corpo", 1: "Elmo", 2: "Fianchi", 3: "Bracciale", 4: "Testa", 5: "Mantello"}
for o in scn.objects:
    if o.type == "MESH":
        o.vertex_groups.clear()
        log("  piece %-26s %6d tris  bind %s" % (o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), o.get("bind")))
for t, bn in BASE.items():
    base = bpy.data.objects[bn]
    others = [o for o in scn.objects if o.type == "MESH" and o.get("bind") == t and o is not base]
    if not others:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for o in others + [base]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
for o in scn.objects:
    if o.type == "MESH":
        o.data.uv_layers[0].active_render = True
        log("OBJECT %-10s %6d tris, %d materials" % (o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), len(o.data.materials)))
salva()
render_viste("rev_10a")
