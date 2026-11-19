exec(open(r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro\lib.py", encoding="utf-8").read())
clear("E_")
B = ["Chest", "Spine"]
C0 = V((0.0, 0.335, 1.255))
R = 0.145
# dome
sphere("E_cupola", C0, R, 24, 14, scale=(1.0, 0.92, 1.05), mat="ottone", bones=B)
# lower corselet (collar)
loft("E_collare", [(C0 + V((0, -0.01, -0.13)), 0.13, 0.12, 0.12), (C0 + V((0, -0.01, -0.165)), 0.148, 0.135, 0.135),
                   (C0 + V((0, -0.01, -0.19)), 0.155, 0.14, 0.14), (C0 + V((0, -0.01, -0.205)), 0.148, 0.133, 0.133)],
     seg=24, mat="ottone_scuro", bones=B)
for i in range(12):
    a = 2 * math.pi * i / 12
    p = C0 + V((math.cos(a) * 0.154, -0.01 + math.sin(a) * 0.14, -0.185))
    sphere("E_bullone_c%d" % i, p, 0.009, 8, 4, mat="ottone", bones=B)
# equator + meridian bands
torus("E_fascia_eq", C0 + V((0, 0, -0.03)), 0.143, 0.007, 32, 6, normal=(0, 0, 1), mat="ottone_scuro", bones=B,
      scale=(1.0, 0.93))
torus("E_fascia_mer", C0, 0.148, 0.006, 32, 6, normal=(1, 0, 0), mat="ottone_scuro", bones=B, scale=(0.93, 1.05))
# main porthole facing back (+Y)
fp = C0 + V((0, 0.128, 0.0))
tube("E_oblo_base", fp - V((0, 0.02, 0)), fp + V((0, 0.012, 0)), 0.078, 0.075, 24, "ottone_scuro", B)
torus("E_oblo_ghiera", fp + V((0, 0.012, 0)), 0.067, 0.013, 24, 8, normal=(0, 1, 0), mat="ottone", bones=B)
sphere("E_oblo_vetro", fp + V((0, 0.004, 0)), 0.058, 16, 8, scale=(1, 0.3, 1), mat="vetro", bones=B)
for ang in (0, 90):
    box("E_grata%d" % ang, fp + V((0, 0.018, 0)), (0.11, 0.008, 0.008), mat="ottone", bones=B,
        rot=Matrix.Rotation(math.radians(ang), 3, "Y"))
for i in range(8):
    a = 2 * math.pi * i / 8 + 0.4
    sphere("E_oblo_bull%d" % i, fp + V((math.cos(a) * 0.069, 0.024, math.sin(a) * 0.069)), 0.0075, 8, 4,
           mat="ottone", bones=B)
# side portholes
for sx in (1, -1):
    sp = C0 + V((0.138 * sx, 0.01, 0.005))
    torus("E_oblo_lat%d" % sx, sp, 0.042, 0.011, 20, 6, normal=(sx, 0, 0), mat="ottone", bones=B)
    sphere("E_vetro_lat%d" % sx, sp, 0.036, 12, 6, scale=(0.3, 1, 1), mat="vetro", bones=B)
# top porthole + valve
tp = C0 + V((0, 0.03, 0.148))
torus("E_oblo_alto", tp, 0.032, 0.009, 18, 6, normal=(0, 0.3, 1), mat="ottone", bones=B)
sphere("E_vetro_alto", tp, 0.028, 12, 6, scale=(1, 1, 0.3), mat="vetro", bones=B)
tube("E_valvola", C0 + V((0.07, -0.02, 0.12)), C0 + V((0.10, -0.02, 0.16)), 0.016, 0.014, 10, "ottone", B)
torus("E_valv_rot", C0 + V((0.10, -0.02, 0.165)), 0.02, 0.004, 14, 6, normal=(0.6, 0, 0.8), mat="ottone_scuro", bones=B)
# curved pipe arching over one side (as in the drawing)
pts = [C0 + V((0.10, 0.05, 0.10)), C0 + V((0.15, 0.09, 0.12)), C0 + V((0.19, 0.12, 0.06)), C0 + V((0.19, 0.12, -0.04)),
       C0 + V((0.16, 0.10, -0.13))]
path_tube("E_tubo_arco", pts, 0.014, 10, "ottone", B)
# hoses going down to the roll, with brass rings
for sx in (1, -1):
    pts = [C0 + V((0.12 * sx, 0.05, -0.08)), C0 + V((0.17 * sx, 0.06, -0.18)), C0 + V((0.18 * sx, 0.03, -0.27)),
           C0 + V((0.15 * sx, 0.0, -0.33)), C0 + V((0.10 * sx, -0.02, -0.30))]
    path_tube("E_tubo%d" % sx, pts, 0.013, 10, "cuoio_scuro", B)
    for j in range(1, 4):
        torus("E_tubo_anello%d_%d" % (sx, j), pts[j], 0.0145, 0.004, 10, 4, normal=(pts[j + 1] - pts[j - 1]),
              mat="ottone_scuro", bones=B)
# coiled hose on her left side under the helmet
for i in range(3):
    torus("E_spirale%d" % i, C0 + V((0.155 + 0.012 * i, -0.05, -0.30)), 0.055 - 0.012 * i, 0.010, 18, 6,
          normal=(1, 0, 0), mat="cuoio_scuro", bones=B + ["Hips"])
# bedroll under the helmet (horizontal)
rc = V((0.0, 0.29, 1.0))
tube("E_rotolo", rc - V((0.16, 0, 0)), rc + V((0.16, 0, 0)), 0.058, 0.058, 18, "lino", ["Spine", "Hips"], rings=2)
for sx in (1, -1):
    tube("E_rotolo_fine%d" % sx, rc + V((0.16 * sx, 0, 0)), rc + V((0.168 * sx, 0, 0)), 0.05, 0.03, 18, "lino",
         ["Spine", "Hips"])
    p = rc + V((0.10 * sx, 0, 0))
    tube("E_rotolo_cinghia%d" % sx, p - V((0.012, 0, 0)), p + V((0.012, 0, 0)), 0.063, 0.063, 18, "cuoio",
         ["Spine", "Hips"])
# rope wrapped around the collar area
for i in range(2):
    torus("E_corda%d" % i, C0 + V((0, -0.01, -0.215 - 0.02 * i)), 0.14 - 0.01 * i, 0.009, 28, 6, normal=(0, 0, 1),
          mat="corda", bones=B, scale=(1.0, 0.9))
# straps holding the pack to the body
for sx in (1, -1):
    pts = [V((0.10 * sx, 0.10, 1.40)), V((0.11 * sx, 0.20, 1.37)), C0 + V((0.10 * sx, -0.02, 0.08))]
    loft("E_cinghia%d" % sx, [(p, 0.02, 0.004, 0.004) for p in pts], seg=6, mat="cuoio", bones=B, up=V((0, 1, 0.3)))

log("triangoli:", tri_count())
save()
render_viste("p06", viste=["destra", "retro", "tre_quarti"])
render_parte("p06_elmo", ["E_"], ["retro", "destra", "alto"])
