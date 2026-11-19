exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-fable\lavoro\rev_lib.py").read())
# last touches after looking at the final renders: hair top back to 1.70, cape folds and streaks easier to see
import numpy as np
T_ = bpy.data.objects["Testa"]
zmax = max(v.co.z for v in T_.data.vertices)
if zmax > 1.7001:
    k = (1.70 - 1.655) / (zmax - 1.655)
    for v in T_.data.vertices:
        if v.co.z > 1.655:
            v.co.z = 1.655 + (v.co.z - 1.655) * k
    T_.data.update()
log("hair top: %.3f -> %.3f" % (zmax, max(v.co.z for v in T_.data.vertices)))


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


def put(name, rgb):
    img = bpy.data.images[name]
    n = rgb.shape[0]
    px = np.ones((n, n, 4), dtype=np.float32)
    px[..., :3] = np.clip(rgb, 0.02, 0.97)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = TEXD + "\\" + name + ".png"
    img.file_format = "PNG"
    img.save()
    img.pack()


N = 512
uu = np.linspace(0, 1, N, endpoint=False)[None, :].repeat(N, 0)
vv = np.linspace(0, 1, N)[:, None].repeat(N, 1)          # 0 = hem, 1 = collar
f1, f2, f3, f4 = [np.kron(tfbm(256, s), np.ones((2, 2))) for s in (31, 41, 51, 61)]
col = np.array((0.22, 0.34, 0.31))[None, None, :] * (0.82 + 0.38 * f1[..., None])
# the same wave as the modelled folds (long part: u 0.25 .. 0.75): ridges lighter, valleys darker
pr = np.radians((4 * uu - 2) * 150.0)
fold = np.sin(12 * pr + 1.2 * np.sin(3.1 * pr + 1.0))
amt = np.clip((0.97 - vv) / 0.45, 0, 1) * ((uu > 0.25) & (uu < 0.75))
col *= (1 + 0.20 * fold * amt)[..., None]
# lighter streaks running down
streak = np.clip((np.sin(uu * 2 * np.pi * 17 + f2 * 8 + np.sin(vv * 7) * 0.7) - 0.25) / 0.75, 0, 1) ** 1.6 * np.clip((f3 - 0.30) * 3, 0, 1) * 0.8
col = col * (1 - streak[..., None]) + np.array((0.40, 0.52, 0.48))[None, None, :] * streak[..., None]
# lower part: dirty sand with brown stains
d = np.clip((0.25 - vv) / 0.25, 0, 1) ** 0.7 * (0.55 + 0.9 * f3)
d = np.clip(d + np.clip((f4 - 0.62) * 6, 0, 1) * 0.5 * np.clip((0.45 - vv) / 0.45, 0, 1), 0, 0.95)
sand = np.array((0.62, 0.55, 0.43))[None, None, :] * (0.85 + 0.3 * f2[..., None]) * (1 + 0.10 * fold * amt)[..., None]
st = np.clip((f1 - 0.56) * 7, 0, 1)[..., None] * 0.7
sand = sand * (1 - st) + np.array((0.36, 0.26, 0.16))[None, None, :] * st
col = col * (1 - d[..., None]) + sand * d[..., None]
put("tex_mantello", col)
put("tex_mantello_interno", col * 0.66)
log("cape texture redone (folds + streaks)")
salva()
render_viste("rev_12", viste=["fronte", "retro"])
