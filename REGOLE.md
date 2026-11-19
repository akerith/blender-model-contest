# Blender model contest - the same rules for everyone

Contest folder: `C:\Users\USER\gara-modelli`. Reference images in `riferimenti\`.
Each contestant has its own folder `concorrenti\<name>\` (inbox, outbox, lavoro).

## How you work (the same for everyone)
- Blender 5.2 is open on the owner's screen and he watches. You drive it only through the kit:
  - `python -I kit/gara.py avvia <name>` opens Blender linked to your folder (one Blender at a time on this PC);
  - `python -I kit/gara.py passo <name> <file.py>` runs one of your Python files inside Blender, waits and prints the log;
  - inside a step file you have: `bpy`, `log(...)` (writes to the log), `render_viste("name")` (renders from the fixed views fronte, destra, retro, sinistra, tre_quarti, alto, saved in the outbox), `OUTBOX`.
- Look at your renders (the images in the outbox) to check your work and fix it. The window screenshot may be covered by Blender's splash screen: trust the renders.
- Work in small steps, one per part of the job, so the owner can follow the progress.
- Everything is built with code inside Blender: no models, textures or add-ons downloaded from the internet, no images made by other programs. Textures are made with nodes or with code.
- Do not read or touch the other contestants' folders. Write only in your own folder.
- Save your work often as a `.blend` in your `lavoro\` folder: when Blender reopens it starts empty.
- Time limit: 2 hours of work per project. When time is up, deliver what you have.
- Reply to the owner in simple Italian.

## Delivery for each project (in `concorrenti\<name>\lavoro\`)
- `<project>.blend` and `<project>.glb` (exported for Unity, metres, Y up, as Blender's glTF exporter does);
- the final renders with `render_viste("finale_<project>")`;
- `NOTE-<project>.md`: time spent, number of steps, triangle count, what is missing or did not work.

## The three projects (one at a time, only when the owner says so)
1. **personaggio** (character) - `riferimenti/1-personaggio.webp`. A woman explorer with a torn green cape, a diving helmet on her back, ropes, tubes, gloves and boots. The pose of the front and back views is the one that counts (arms open and angled down, an "A" pose); the side views are only for shapes and volumes. Height 1.70 m. A game model: at most 40,000 triangles, with a human skeleton (pelvis, spine, neck, head, arms, hands, legs, feet) bound to the mesh, ready to be animated in Unity.
2. **arma** (weapon) - `riferimenti/2-arma.webp`. A brass lantern-staff with a glowing jellyfish inside the glass, hanging tassels and a spike at the bottom. Length 1.60 m. The glass must be transparent and the jellyfish must emit light. At most 15,000 triangles. The tassels may vary a little (they change between the views in the drawing).
3. **scena** (scene) - `riferimenti/3-scena.webp` (top view). A mud road crossing a meadow diagonally; a wooden cart standing upright on its four wheels, with a broken side board and a cloth; a broken piece of shaft and a wooden crate on the ground; three horses lying on the ground (one chained to the cart's shaft, two chained to each other); five puddles; grass along the edges. Area 20 x 20 m. Rain is made in Blender (an effect, not required in the .glb). The scene must be **explorable**: a person 1.80 m tall walks inside it in first person; the ground is continuous, with no holes; the edges are closed (bushes, trees or rising ground) so nobody falls out; objects are solid and cannot be walked through. At most 300,000 triangles in total.

## How it is judged
The owner looks at the results without knowing who made them (the folders are renamed A, B, C...). What counts: likeness to the reference, quality and detail, how clean the model is for a game, and for the scene whether you can really walk in it (checked in Unity). Time and cost are noted.
