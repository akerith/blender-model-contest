exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())

# --- helmet: bigger and closer to the back ---
clear("E_cinghia")
C0 = V((0.0, 0.335, 1.255))
NEW = V((0.0, 0.305, 1.245))
for ob in bpy.data.objects:
    if ob.name.startswith("E_") and not ob.name.startswith("E_rotolo"):
        for v in ob.data.vertices:
            v.co = NEW + (v.co - C0) * 1.13
    elif ob.name.startswith("E_rotolo"):
        for v in ob.data.vertices:
            v.co = v.co + V((0, -0.025, 0.0))
            v.co.x *= 1.12

# --- hands: turn the palm so the hand opens toward the front view, slightly larger ---
for s, sx in ((".L", 1), (".R", -1)):
    d = V((ARM_D.x * sx, 0, ARM_D.z))
    W = V((WRI.x * sx, WRI.y, WRI.z))
    rot = Matrix.Rotation(math.radians(48 * sx), 3, d)
    for ob in bpy.data.objects:
        n = ob.name
        if n.endswith(s) and (n.startswith("C_palmo") or n.startswith("C_dito") or n.startswith("C_pollice")):
            for v in ob.data.vertices:
                v.co = W + rot @ ((v.co - W) * 1.15)

# --- muted colours, closer to the drawing ---
MATS.update({
    "lino": ((0.40, 0.34, 0.26), 0.9, 0.0),
    "corda": ((0.36, 0.28, 0.17), 0.95, 0.0),
    "cuoio": ((0.15, 0.08, 0.042), 0.55, 0.0),
    "cuoio_scuro": ((0.075, 0.045, 0.03), 0.5, 0.0),
    "camicia": ((0.045, 0.07, 0.115), 0.8, 0.0),
    "gilet": ((0.05, 0.055, 0.065), 0.65, 0.0),
    "pantaloni": ((0.075, 0.065, 0.058), 0.85, 0.0),
    "pelle": ((0.66, 0.45, 0.36), 0.55, 0.0),
})
for k in MATS:
    if bpy.data.materials.get(k):
        M(k)
# write back into lib so later steps keep the same colours
p = os.path.join(LAVORO, "lib.py")
src = open(p, encoding="utf-8").read()
if "MATS.update(" not in src:
    src = src.replace("\n\ndef M(name):", """
MATS.update({
    "lino": ((0.40, 0.34, 0.26), 0.9, 0.0),
    "corda": ((0.36, 0.28, 0.17), 0.95, 0.0),
    "cuoio": ((0.15, 0.08, 0.042), 0.55, 0.0),
    "cuoio_scuro": ((0.075, 0.045, 0.03), 0.5, 0.0),
    "camicia": ((0.045, 0.07, 0.115), 0.8, 0.0),
    "gilet": ((0.05, 0.055, 0.065), 0.65, 0.0),
    "pantaloni": ((0.075, 0.065, 0.058), 0.85, 0.0),
    "pelle": ((0.66, 0.45, 0.36), 0.55, 0.0),
})


def M(name):""", 1)
    open(p, "w", encoding="utf-8").write(src)

log("triangoli:", tri_count())
save()
render_viste("p07", viste=["fronte", "destra", "retro", "tre_quarti"])
