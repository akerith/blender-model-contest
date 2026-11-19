"""Model contest kit: the same Blender link for every contestant.

  python -I kit/gara.py avvia <nome> [file.blend]  start Blender on screen, linked to concorrenti/<nome>
                                                (with a .blend: Blender opens that saved work)
  python -I kit/gara.py passo <nome> <file.py>  run one step file in that Blender, wait, print the log
  python -I kit/gara.py stato <nome>            is the link up? how many steps so far?

Run from the folder C:\\Users\\USER\\gara-modelli. A step file is plain Blender Python: `bpy`
is there, `log(...)` writes to the step log, `render_viste("name")` renders the scene from fixed
angles (fronte, destra, retro, sinistra, tre_quarti, alto) into the outbox, `OUTBOX` is the
outbox path. Only one Blender at a time on this PC.
"""
import os, sys, time, shutil, subprocess, glob

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "kit")


def dirs(nome):
    base = os.path.join(ROOT, "concorrenti", nome)
    d = {k: os.path.join(base, k) for k in ("inbox", "outbox", "lavoro")}
    for p in d.values():
        os.makedirs(p, exist_ok=True)
    return base, d


def blender_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq blender.exe"], capture_output=True, text=True).stdout
    return "blender.exe" in out.lower()


def avvia(nome, blend=None):
    base, d = dirs(nome)
    if blender_running():
        print("Blender is already running. Only one at a time: close it first.")
        return 1
    ready = os.path.join(d["outbox"], "ready.txt")
    if os.path.exists(ready):
        os.remove(ready)
    # steps from an earlier run are not re-run: move them aside
    old = glob.glob(os.path.join(d["inbox"], "*.py"))
    if old:
        arch = os.path.join(base, "passi-precedenti", time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(arch)
        for f in old:
            shutil.move(f, arch)
    if blend and not os.path.isfile(blend):
        print("File not found:", blend)
        return 1
    cmd = [BLENDER] + ([os.path.abspath(blend)] if blend else [])
    subprocess.Popen(cmd + ["--python", os.path.join(KIT, "collegamento.py"), "--", d["inbox"], d["outbox"]],
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0), close_fds=True)
    for _ in range(120):
        if os.path.exists(ready):
            print("Link up, Blender", open(ready).read().strip(), "- contestant folder:", base)
            if blend:
                print("Opened:", os.path.abspath(blend), "- save it again with bpy.ops.wm.save_mainfile()")
            else:
                print("Blender starts empty each time: save your work as .blend in", d["lavoro"])
            return 0
        time.sleep(1)
    print("Blender did not answer within 2 minutes.")
    return 1


def passo(nome, file, attesa=900):
    base, d = dirs(nome)
    if not os.path.exists(os.path.join(d["outbox"], "ready.txt")) or not blender_running():
        print("The link is not up: run  python -I kit/gara.py avvia", nome)
        return 1
    n = len(glob.glob(os.path.join(d["inbox"], "*.py"))) + 1
    stem = os.path.splitext(os.path.basename(file))[0]
    name = "%03d_%s" % (n, stem)
    logf = os.path.join(d["outbox"], name + ".log")
    if os.path.exists(logf):  # a log with this name from an earlier Blender run: not this step's
        os.remove(logf)
    tmp = os.path.join(d["inbox"], name + ".tmp")
    shutil.copyfile(file, tmp)
    os.replace(tmp, os.path.join(d["inbox"], name + ".py"))  # never read half-written
    t0 = time.time()
    while time.time() - t0 < attesa:
        if os.path.exists(logf):
            time.sleep(0.3)
            print(open(logf, encoding="utf-8").read())
            print("--- step", name, "took %.0f s" % (time.time() - t0))
            print("window screenshot:", os.path.join(d["outbox"], name + "_schermo.png"))
            print("renders are in:", d["outbox"])
            return 0
        if not blender_running():
            print("Blender closed or crashed during the step.")
            return 1
        time.sleep(0.5)
    print("No answer after", attesa, "s: the step is still running or Blender is stuck.")
    return 1


def stato(nome):
    base, d = dirs(nome)
    up = os.path.exists(os.path.join(d["outbox"], "ready.txt")) and blender_running()
    steps = len(glob.glob(os.path.join(d["inbox"], "*.py")))
    print("link:", "up" if up else "down", "| steps in this run:", steps, "| folder:", base)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "avvia":
        sys.exit(avvia(a[1], a[2] if len(a) >= 3 else None))
    if len(a) >= 3 and a[0] == "passo":
        sys.exit(passo(a[1], a[2]))
    if len(a) >= 2 and a[0] == "stato":
        sys.exit(stato(a[1]))
    print(__doc__)
    sys.exit(2)
