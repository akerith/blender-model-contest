# rebuild the whole character from the step scripts p01..p07 (no intermediate renders)
import os
_D = r"C:\Users\USER\gara-modelli\concorrenti\claude-opus\lavoro"
_real_render = render_viste
_FILES = ["p01_scheletro_corpo.py", "p02_testa_capelli.py", "p03_capelli_v2.py", "p04_vestiti.py",
          "p05_mantello.py", "p06_elmo.py", "p07_mani_colori_elmo.py"]
render_viste = lambda *a, **k: []
try:
    for _f in _FILES:
        exec(compile(open(os.path.join(_D, _f), encoding="utf-8").read(), _f, "exec"), globals())
        log("rifatto:", _f)
finally:
    render_viste = _real_render
log("view transform:", bpy.context.scene.view_settings.view_transform, "| motore:", bpy.context.scene.render.engine)
log("triangoli:", tri_count())
save()
render_viste("p10", viste=["fronte", "destra", "retro", "tre_quarti"])
render_parte("p10_testa", ["C_testa", "C_collo", "F_", "K_"], ["fronte", "tre_quarti"])
