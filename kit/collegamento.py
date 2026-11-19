# Live link for the model contest. Blender runs, in order, the step files that appear in INBOX
# and writes a log, a screenshot of the window and any renders to OUTBOX.
# Started by gara.py; never started by hand.
import bpy, os, sys, glob, traceback
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
INBOX, OUTBOX = args[0], args[1]
done, pending, LOG = set(), [], []


def log(*a):
    LOG.append(" ".join(str(x) for x in a))


def ctx():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    return dict(window=win, screen=win.screen, area=area, region=region)


VIEWS = {
    "fronte": (0, -1, 0),
    "destra": (1, 0, 0),
    "retro": (0, 1, 0),
    "sinistra": (-1, 0, 0),
    "tre_quarti": (1, -1, 0.6),
    "alto": (0, -0.001, 1),
}


def render_viste(nome, viste=None, risoluzione=960):
    """Render the visible objects from fixed angles into OUTBOX/<nome>_<vista>.png.
    Uses the scene's own engine, lights and world. Returns the list of files."""
    scn = bpy.context.scene
    objs = [o for o in scn.objects
            if o.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"} and o.visible_get()
            and not o.name.startswith("_gara")]
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    if not pts:
        log("render_viste: nothing visible to render")
        return []
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    center, size = (mn + mx) / 2, max((mx - mn).length, 0.01)
    cam_data = bpy.data.cameras.new("_gara_cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = size * 1.05
    cam_data.clip_end = size * 20
    cam = bpy.data.objects.new("_gara_cam", cam_data)
    scn.collection.objects.link(cam)
    r = scn.render
    old = (scn.camera, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath)
    files = []
    try:
        scn.camera = cam
        r.resolution_x = r.resolution_y = risoluzione
        r.resolution_percentage = 100
        for v in (viste or VIEWS):
            d = Vector(VIEWS[v]).normalized()
            cam.location = center + d * size * 3
            cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
            path = os.path.join(OUTBOX, "%s_%s.png" % (nome, v))
            r.filepath = path
            bpy.ops.render.render(write_still=True)
            files.append(path)
    finally:
        scn.camera, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath = old
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cam_data)
    log("render_viste:", ", ".join(os.path.basename(f) for f in files))
    return files


NS = {"bpy": bpy, "log": log, "ctx": ctx, "render_viste": render_viste, "OUTBOX": OUTBOX}


def tick():
    try:
        if pending:
            name, text = pending.pop(0)
            try:
                c = ctx()
                with bpy.context.temp_override(window=c["window"], screen=c["screen"]):
                    bpy.ops.screen.screenshot(filepath=os.path.join(OUTBOX, name + "_schermo.png"))
            except Exception as e:
                text += "\nscreenshot failed: %r" % (e,)
            open(os.path.join(OUTBOX, name + ".log"), "w", encoding="utf-8").write(text)
            return 0.3
        for f in sorted(glob.glob(os.path.join(INBOX, "*.py"))):
            name = os.path.splitext(os.path.basename(f))[0]
            if name in done:
                continue
            done.add(name)
            LOG.clear()
            try:
                src = open(f, encoding="utf-8").read()
                with bpy.context.temp_override(**ctx()):
                    exec(compile(src, f, "exec"), NS)
                text = "OK\n" + "\n".join(LOG)
            except Exception:
                text = "ERROR\n" + "\n".join(LOG) + "\n" + traceback.format_exc()
            pending.append((name, text))
            return 1.0  # let the window redraw before the screenshot
    except Exception:
        open(os.path.join(OUTBOX, "bridge-error.log"), "a", encoding="utf-8").write(traceback.format_exc())
    return 0.4


bpy.app.timers.register(tick, first_interval=2.0, persistent=True)
open(os.path.join(OUTBOX, "ready.txt"), "w").write(bpy.app.version_string)
