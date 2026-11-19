Project 1 prompt. Paste it in the same chat used for the setup (Blender may still be open).
Replace NAME with the contestant name.

---------------------------------------------------------------------------------

Start project 1: the character ("personaggio"). Your contest name is NAME.

1. Re-read the "personaggio" section of REGOLE.md and look closely at riferimenti/1-personaggio.webp. Only that image is the reference.
2. Run `python -c "import time; print(time.strftime('%H:%M'))"` and write the start time in concorrenti/NAME/lavoro/NOTE-personaggio.md. You have 2 hours from that time.
3. If Blender is not open, start it with `python -I kit/gara.py avvia NAME`.
4. Before modelling, write a short plan in NOTE-personaggio.md: the parts you will build, the order, and how you will reach the triangle limit.
5. Build the character in small steps with `python -I kit/gara.py passo NAME <file.py>`. After each important step, call render_viste on the views that matter, look at the images, compare them with the reference and fix what is wrong before moving on. Save the .blend in your lavoro folder after every step.
6. When it is done, or when the 2 hours are up: export personaggio.glb, run render_viste("finale_personaggio"), and complete NOTE-personaggio.md (end time, number of steps, triangles, bones, what is missing).

Work on your own until the end without asking me anything, unless something blocks you completely. At the end, reply in simple Italian: what you made, what came out well, what did not.
