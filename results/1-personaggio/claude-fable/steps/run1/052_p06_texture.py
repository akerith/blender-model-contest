exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\lib.py").read())
import numpy as np
M = materials()


def vnoise(n, cells, seed):
    rs = np.random.RandomState(seed)
    g = rs.rand(cells + 2, cells + 2)
    x = np.linspace(0, cells, n, endpoint=False)
    xi = x.astype(int)
    xf = x - xi
    xf = xf * xf * (3 - 2 * xf)
    a, b = g[xi][:, xi], g[xi][:, xi + 1]
    c, d = g[xi + 1][:, xi], g[xi + 1][:, xi + 1]
    X, Y = xf[None, :], xf[:, None]
    return (a * (1 - X) + b * X) * (1 - Y) + (c * (1 - X) + d * X) * Y


def fbm(n, seed):
    return vnoise(n, 4, seed) * 0.45 + vnoise(n, 9, seed + 1) * 0.27 + vnoise(n, 20, seed + 2) * 0.17 + vnoise(n, 60, seed + 3) * 0.11


def make_image(name, rgb):
    n = rgb.shape[0]
    img = bpy.data.images.get(name)
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(name, n, n, alpha=False)
    px = np.ones((n, n, 4), dtype=np.float32)
    px[..., :3] = np.clip(rgb, 0, 1)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = LAV + "\\" + name + ".png"
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


def set_tex(material, img):
    nt = material.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for n in [n for n in nt.nodes if n.type == "TEX_IMAGE"]:
        nt.nodes.remove(n)
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.location = (-350, 300)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])


# ---- cape: worn teal cloth, pale water marks, mud and wear towards the hem ----
N = 512
uu = np.linspace(0, 1, N)[None, :].repeat(N, 0)
vv = np.linspace(0, 1, N)[:, None].repeat(N, 1)       # 0 = hem, 1 = collar
f1, f2, f3, f4 = fbm(N, 1), fbm(N, 20), fbm(N, 40), fbm(N, 60)
base = np.zeros((N, N, 3))
teal = np.array([0.27, 0.365, 0.335])
for k in range(3):
    base[..., k] = teal[k] * (0.78 + 0.5 * f1)
# weave: fine vertical / horizontal threads
weave = 0.012 * np.sin(uu * N * 0.9) + 0.012 * np.sin(vv * N * 0.9)

# soft fold shading (vertical bands)
base *= (1 + 0.10 * np.sin(uu * 2 * np.pi * 11 + f2 * 5))[..., None]
# pale wavy marks
wav = np.sin(vv * 46 + f2 * 16 + uu * 7)
mark = np.clip((wav - 0.90) / 0.10, 0, 1) * np.clip((f3 - 0.38) * 4, 0, 1) * 0.55
pale = np.array([0.58, 0.68, 0.63])
base = base * (1 - mark[..., None]) + pale * mark[..., None]
# mud / wear
d = np.clip((0.40 - vv) / 0.40, 0, 1) ** 0.8 * (0.25 + 1.3 * f3)
d += np.clip((f4 - 0.60) * 6, 0, 1) * 0.55 * np.clip(1.15 - vv, 0, 1)
d = np.clip(d, 0, 0.92)
mud = np.array([0.47, 0.38, 0.28])[None, None, :] * (0.8 + 0.5 * f2[..., None]) + np.array([0.22, 0.2, 0.15])[None, None, :] * (f1[..., None] > 0.55)
base = base * (1 - d[..., None]) + mud * d[..., None]
img = make_image("tex_mantello", base)
set_tex(M["cape"], img)
img2 = make_image("tex_mantello_interno", base * 0.62)
set_tex(M["capein"], img2)
log("cape textures done")

# ---- tiling detail textures for the other materials (grain, stains, patina) ----
def tnoise(n, cells, seed):
    rs = np.random.RandomState(seed)
    g = rs.rand(cells, cells)
    x = np.linspace(0, cells, n, endpoint=False)
    xi = x.astype(int)
    xf = x - xi
    xf = xf * xf * (3 - 2 * xf)
    x1 = (xi + 1) % cells
    a, b = g[xi][:, xi], g[xi][:, x1]
    c, d = g[x1][:, xi], g[x1][:, x1]
    X, Y = xf[None, :], xf[:, None]
    return (a * (1 - X) + b * X) * (1 - Y) + (c * (1 - X) + d * X) * Y


def tfbm(n, seed):
    return tnoise(n, 4, seed) * 0.42 + tnoise(n, 8, seed + 1) * 0.28 + tnoise(n, 16, seed + 2) * 0.18 + tnoise(n, 48, seed + 3) * 0.12


def srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


T = 256
tu = np.linspace(0, 1, T, endpoint=False)[None, :].repeat(T, 0)
tv = np.linspace(0, 1, T, endpoint=False)[:, None].repeat(T, 1)


def detail(key, name, hexcol, contrast=0.45, seed=0, weave=0.0, stain=None, stain_amt=0.0, patina=None):
    f1, f2, f3 = tfbm(T, seed + 1), tfbm(T, seed + 11), tfbm(T, seed + 21)
    col = srgb(hexcol)[None, None, :] * (1 - contrast / 2 + contrast * f1[..., None])
    if weave:
        col = col * (1 + weave * np.sin(tu * 2 * np.pi * 40) * np.sin(tv * 2 * np.pi * 40))[..., None]
    if stain is not None:
        m = np.clip((f2 - 0.55) * 5, 0, 1)[..., None] * stain_amt
        col = col * (1 - m) + srgb(stain)[None, None, :] * m
    if patina is not None:
        m = np.clip((f3 - 0.56) * 6, 0, 1)[..., None] * 0.75
        col = col * (1 - m) + srgb(patina)[None, None, :] * (0.85 + 0.3 * f1[..., None]) * m
    set_tex(M[key], make_image("tex_" + name, col))


M["hose"] = mat("tubo", "#4a3526", rough=0.55)
M["shirt"] = mat("camicia", "#7f8790", rough=0.9)
detail("leather", "cuoio", "#6a4630", 0.55, 1, stain="#3a2618", stain_amt=0.5)
detail("leatherd", "cuoio_scuro", "#45301f", 0.55, 2, stain="#22170f", stain_amt=0.5)
detail("linen", "lino", "#c2ad8c", 0.30, 3, weave=0.02, stain="#8a7355", stain_amt=0.45)
detail("pants", "pantaloni", "#54463c", 0.35, 4, weave=0.02, stain="#3a2e26", stain_amt=0.4)
detail("tunic", "tunica", "#34414f", 0.35, 5, weave=0.02, stain="#232c36", stain_amt=0.4)
detail("vest", "corpetto", "#2b3038", 0.45, 6, stain="#15181c", stain_amt=0.5)
detail("brass", "ottone", "#b89040", 0.35, 7, stain="#6e4f22", stain_amt=0.55, patina="#5f9482")
detail("brassd", "ottone_scuro", "#86632e", 0.40, 8, stain="#4a3418", stain_amt=0.5, patina="#5a8a7a")
detail("rope", "corda", "#b09a70", 0.35, 9, stain="#7a6646", stain_amt=0.5)
detail("hose", "tubo", "#523a28", 0.45, 10, stain="#2a1c12", stain_amt=0.5)
detail("shirt", "camicia", "#878f98", 0.25, 12, weave=0.02)
detail("hair", "capelli", "#2e2826", 0.5, 13)

# simple UVs (flat projection along the main direction of each face) where there are none
SC = 2.2
cnt = 0
for o in bpy.context.scene.objects:
    if o.type != "MESH" or "bones" not in o.keys() or o.data.uv_layers:
        continue
    me = o.data
    uvl = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        n = p.normal
        ax = max(range(3), key=lambda k: abs(n[k]))
        for li in p.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                uv = (c.y, c.z)
            elif ax == 1:
                uv = (c.x, c.z)
            else:
                uv = (c.x, c.y)
            uvl.data[li].uv = (uv[0] * SC, uv[1] * SC)
    me.uv_layers.active = uvl
    uvl.active_render = True
    cnt += 1
log("detail textures done, uv made for", cnt, "parts")

save()

