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
teal = np.array([0.30, 0.46, 0.41])
for k in range(3):
    base[..., k] = teal[k] * (0.78 + 0.5 * f1)
# weave: fine vertical / horizontal threads
weave = 0.03 * np.sin(uu * N * 1.2) + 0.03 * np.sin(vv * N * 1.2)
base += weave[..., None]
# soft fold shading (vertical bands)
base *= (1 + 0.10 * np.sin(uu * 2 * np.pi * 11 + f2 * 5))[..., None]
# pale wavy marks
wav = np.sin(vv * 46 + f2 * 16 + uu * 7)
mark = np.clip((wav - 0.90) / 0.10, 0, 1) * np.clip((f3 - 0.38) * 4, 0, 1) * 0.55
pale = np.array([0.66, 0.78, 0.72])
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

save()
render_viste("p06", viste=["retro", "fronte"])
