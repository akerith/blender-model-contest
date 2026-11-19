Revision round for project 1, the character. Your contest name is NAME.

You already built this character in round 1. Now you get ONE revision of 1 hour. You do not start again: you open your own saved work and you change it, part by part, following the description below exactly. Read this whole message before you do anything.

## A. Rules of this round

A1. Open your own work, never start from an empty scene. First copy your round-1 files so they stay as they are:
    - copy concorrenti/NAME/lavoro/personaggio.blend to concorrenti/NAME/lavoro/personaggio_giro1.blend
    - copy concorrenti/NAME/lavoro/personaggio.glb to concorrenti/NAME/lavoro/personaggio_giro1.glb
    - copy concorrenti/NAME/lavoro/NOTE-personaggio.md to concorrenti/NAME/lavoro/NOTE-personaggio_giro1.md
    Do not change those three copies after this.
A1b. Where commands run. Run every kit command (`avvia` and `passo`) OUTSIDE any sandbox or isolated environment of your program, as a normal process of the Windows user who is logged in. Inside a sandbox the kit cannot see Blender, the `python` command may be missing, and Blender opens on a hidden desktop. If your program asks for permission to run outside the sandbox, ask for it. After `avvia`, check that Blender is really running for the logged-in user: `tasklist /V /FI "IMAGENAME eq blender.exe"` must show the user name of the PC (not a sandbox user) and a window title that is not "N/A" or "N/D". If it does not, close that Blender and start it again outside the sandbox. If `python` is not found, use Blender's own Python: `"C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe"`.
A2. Make sure Blender is closed, then open your saved work with:
    `python -I kit/gara.py avvia NAME concorrenti/NAME/lavoro/personaggio.blend`
    Your first step file only writes in the log the list of all objects (name, type, triangle count, location, dimensions) and calls render_viste("rev_inizio"). Look at the six images before you change anything.
A3. Change what exists. Move, rotate, scale, bend, re-shape, add loops, add new pieces. You may delete and rebuild ONE piece only when that piece cannot be fixed (for example a hand that is a box): write in the notes which piece and why. Never delete the whole character, never clear the scene.
A4. Run `python -c "import time; print(time.strftime('%H:%M'))"` and write the start time in concorrenti/NAME/lavoro/NOTE-revisione-personaggio.md. You have 1 hour from that time.
A5. Work in the order of section C, one group per step file. After each group: save the .blend (bpy.ops.wm.save_mainfile()), call render_viste("rev_<number of the group>"), look at the images, compare them with riferimenti/1-personaggio.webp and with the numbers below, and fix what does not match before you go to the next group.
A6. If the hour is almost over, stop where you are and go to section D. A part done well is better than every part done badly.
A7. The model is made with code inside Blender: no downloads, no add-ons, nothing from the internet. Do not read or touch the other contestants' folders.
A7b. Image programs you MAY use, only for textures and small painted details (cloth stains, leather grain, the compass dial, rivet and stitch patterns, decals), only from the command line, and only on images you make yourself. They are already installed; using them is optional:
    - GIMP 3 (batch mode, Python plug-ins): `"C:\Users\USER\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe"`
    - Krita (Python scripts): `"C:\Program Files\Krita (x64)\bin\kritarunner.exe"`
    - Inkscape (draw an SVG, export it to PNG): `"C:\Program Files\WindowsApps\25415Inkscape.Inkscape_1.4.40.0_x64__9waqn51p1ttv2\VFS\ProgramFilesX64\Inkscape\bin\inkscape.exe"`
    Save every image you make in concorrenti/NAME/lavoro/texture/ and load it in Blender from there. Every other program on this PC is off limits, in particular any program that generates images or 3D with AI. Time spent on these programs counts in your hour.

## B. How to read the numbers

B1. Units are metres. Z is up. The floor is Z = 0. The character stands at the centre: the point between her feet is X = 0, Y = 0.
B2. She faces the "fronte" camera, which looks from -Y towards +Y. So her face and chest point to -Y, her back points to +Y.
B3. Her LEFT side is +X, her RIGHT side is -X. Careful: in the front drawing of the reference her right side is on the left of the picture.
B4. "Height" always means Z of that point above the floor. "Width" is size along X, "depth" is size along Y.
B5. The reference image has four drawings: 1 front, 2 her right side, 3 her left side, 4 back. The pose of drawings 1 and 4 is the one that counts. Drawings 2 and 3 show shapes and depth only (the arms are lowered there; ignore that).

## C. The character, part by part (do the groups in this order)

### Group 1 - Body proportions and pose (this is the most important group)

1.1 Total height 1.70 m, from the sole of the boots (Z = 0) to the top of the hair (Z = 1.70). Without hair the top of the skull is at 1.66 m.
1.2 Key heights (Z, metres):
    - top of hair 1.70; top of skull 1.66; eyes 1.585; chin 1.475
    - base of neck / top of the collar 1.45
    - shoulder joints 1.40
    - chest at its fullest 1.27
    - waist (narrowest point, where the main belt sits) 1.08
    - hip joints 0.90; crotch 0.86
    - knee joints 0.49
    - ankle joints 0.08
1.3 Key widths (X, metres, full width from side to side):
    - head 0.15, head depth 0.19
    - neck 0.11
    - shoulders, outside of one shoulder to outside of the other: 0.40
    - chest 0.32 wide, 0.21 deep
    - waist 0.27 wide, 0.18 deep
    - hips 0.34 wide, 0.22 deep
    - the feet stand apart: the centre of each boot is at X = -0.13 (right) and X = +0.13 (left). The legs go straight down from the hips to the feet, slightly apart, like an upside-down narrow "V".
1.4 The arms are the A pose of the front drawing:
    - each arm is straight, with only a small bend at the elbow (about 10 degrees) and the palm facing down and slightly back
    - each arm goes out and down at 50 degrees below the horizontal (0 degrees would be a T pose, 90 degrees would be the arm hanging along the body)
    - the arm is NOT in front of the body and NOT behind it: seen from the side, the shoulder, elbow, wrist and fingertips are all at the same Y as the shoulder (Y about 0.0)
    - lengths: shoulder joint to elbow 0.29; elbow to wrist 0.25; wrist to fingertip of the middle finger 0.18
    - with these numbers the left elbow sits at about X = +0.38, Z = 1.18; the left wrist at about X = +0.54, Z = 0.99; the left middle fingertip at about X = +0.66, Z = 0.86. The right arm is the mirror (negative X).
1.5 Seen from the side (drawings 2 and 3) she stands straight: the ear, shoulder, hip and ankle are on one vertical line. The chest is a little forward of the belly, the bottom a little back.
1.6 Check after this group: in rev_1_fronte the outline must look like a person in an "A": head, then shoulders, the two arms going down and out to hip height, two legs. If the arms hang along the body or stand out horizontally, fix them before going on.

### Group 2 - Head, face and hair

2.1 Head: an egg shape, narrower at the chin, 0.15 wide, 0.19 deep, 0.22 high from chin (1.475) to top of skull (1.66) without hair (the hair adds 0.04 on top).
2.2 Face (at the -Y side of the head):
    - eyes at Z 1.585, 0.065 apart (centre to centre), each eye 0.03 wide, set slightly into the face
    - dark straight eyebrows 0.012 above the eyes, angled down towards the nose (a serious, determined look)
    - nose: a small wedge, from Z 1.58 down to Z 1.53, sticking out 0.02 from the face
    - mouth: a closed straight line at Z 1.505, 0.045 wide, lips not smiling
    - chin small and rounded at Z 1.475; the jaw goes from the chin up to below the ears
    - ears on both sides at the height between the eyes and the nose (Z 1.55 to 1.59), mostly covered by hair
2.3 Skin colour: light warm skin, RGB about (0.85, 0.68, 0.58). Eyes dark brown. Eyebrows and hair the same dark colour.
2.4 Hair: short, thick, wavy and messy, dark brown almost black, RGB about (0.10, 0.08, 0.07).
    - On top it is full and stands up 0.04 above the skull, wider than the head (total 0.19 wide at the top).
    - It covers the forehead down to just above the eyebrows, with locks falling on the forehead.
    - On the sides it covers the ears and ends at Z 1.50 (jaw height).
    - At the back it ends at the nape, Z 1.48, with uneven points.
    - Build it from many clumps (stretched, bent, pointed pieces), at least 25, not one smooth helmet. Each clump is 0.02 to 0.04 thick and 0.06 to 0.12 long, pointing down and outwards.
2.5 White streak: one clump group on her RIGHT side of the forehead (-X), starting at the parting at X -0.03 and going back and to the right over the top of the head, about 0.03 wide. Colour light grey-white, RGB (0.80, 0.80, 0.78). In the back drawing it is visible on top of the head, slightly to the left of the picture.

### Group 3 - Neck, shirt and collar

3.1 Neck: a cylinder 0.11 wide, from Z 1.45 to 1.49, skin colour, almost hidden by the collar.
3.2 Shirt collar: a high grey-blue shirt collar wrapped around the neck, from Z 1.41 to 1.46, RGB (0.30, 0.33, 0.38).
3.3 Cape collar: a stiff, tall stand-up collar of the cape around the back and the sides of the neck, open at the front. It rises from the shoulders (Z 1.40) to Z 1.52 at the back and to Z 1.48 at the front corners, and leans out a little. Same teal colour as the cape (Group 6).

### Group 4 - Torso: jacket, straps, belts

4.1 Jacket (a fitted waistcoat-jacket): dark navy blue, RGB (0.13, 0.16, 0.22), covering the chest and the belly from the collar (Z 1.42) to the waist (Z 1.06). It follows the body shape of Group 1 (chest, then narrower at the waist). Add a few vertical seam lines (thin dark grooves) on the front, 4 to 6 of them.
4.2 Tunic skirt: under the main belt the navy tunic continues as a short skirt from Z 1.06 down to Z 0.80 at the front and the back, open on the sides, slightly wider than the hips (0.38 wide). The lower edge is uneven.
4.3 Cross straps on the chest (bandoliers): two brown leather straps, 0.035 wide and 0.008 thick, lying on the jacket:
    - strap 1 from the top of her LEFT shoulder (X +0.13, Z 1.41) across the chest to her RIGHT hip (X -0.15, Z 1.04)
    - strap 2 from the top of her RIGHT shoulder (X -0.13, Z 1.41) across the chest to her LEFT hip (X +0.15, Z 1.04)
    - they cross on the breastbone at about Z 1.25
    - both straps continue over the shoulders and down the back, where they meet the harness of the diving helmet (Group 9)
    - leather colour RGB (0.36, 0.22, 0.12); a small square brass buckle (0.03 x 0.03) on each strap at Z 1.30
4.4 A horizontal brown strap around the chest just under the breasts, Z 1.20, 0.03 wide.
4.5 Main belt: brown leather, 0.06 high, around the waist at Z 1.06 to 1.12, 0.006 thick, standing 0.006 out of the jacket. At the centre front a rectangular brass buckle 0.07 wide, 0.05 high, with a frame and a pin.
4.6 Lower hip belt: a second brown belt, 0.04 high, slanting: higher on her left (Z 1.00 at X +0.17) and lower on her right (Z 0.94 at X -0.17). The pouches and the rope hang from it.
4.7 Medallion: a round brass disc 0.04 across, hanging on a short cord 0.04 below the main buckle, centre at Z 0.99, X 0.

### Group 5 - Arms: sleeves, gloves, bracer, hands

5.1 Upper arms (shoulder to elbow): wide, puffy, cream linen sleeves, RGB (0.82, 0.76, 0.64), rolled up and bunched just above the elbow. They are thicker than the arm: 0.10 across at the shoulder, 0.11 at the roll above the elbow. Add 3 to 4 bulging rings (the rolled fabric) between Z 1.25 and the elbow.
5.2 Forearms: long brown leather gloves (gauntlets) from the hands up to 0.04 below the elbow. The gauntlet is 0.075 across at the wrist and 0.095 at its top cuff; the cuff is a flared ring 0.015 thick.
5.3 Three straps around each gauntlet: one at the top cuff, one in the middle of the forearm, one at the wrist; each 0.015 wide, darker leather RGB (0.20, 0.12, 0.07), with a tiny brass buckle 0.015 wide on the outside.
5.4 On her LEFT forearm (+X), on the outside, just above the wrist: a round brass bracer-gauge, a disc 0.055 across and 0.015 thick, with a green glass face RGB (0.25, 0.55, 0.35) and a thin brass rim. In the front drawing it is on the right of the picture; in the back drawing on the left of the picture.
5.5 Hands (gloved, the same brown leather as the gauntlets, RGB (0.26, 0.16, 0.09)):
    - palm: a flat block with rounded edges, 0.085 long, 0.08 wide, 0.03 thick
    - four fingers, each made of 3 segments (thick at the base, thinner at the tip), lengths: index 0.075, middle 0.085, ring 0.08, little 0.065, thickness about 0.018
    - the fingers are slightly spread (about 8 degrees between them) and slightly curled (each joint bent about 10 degrees towards the palm)
    - thumb: 2 segments plus a base, 0.065 long, starting at the side of the palm near the wrist, pointing forward and down at about 40 degrees from the index
    - the hand continues the line of the forearm, palm facing down and slightly back; it must touch the wrist (no gap, no floating hand)
    - each finger needs at least 8 sides around, so it looks round and not square

### Group 6 - The cape

6.1 Colour: worn teal green, RGB (0.22, 0.34, 0.31), with lighter streaks RGB (0.40, 0.52, 0.48) running down (make them with a noise or wave texture in the material). The lower 0.25 m of the cape fades to a dirty sand colour RGB (0.62, 0.55, 0.43), with brown stains.
6.2 Shoulder cape (top layer): a short cape covering both shoulders and the top of the upper arms, from the collar down to Z 1.24 on the arms and to Z 1.20 on the back. It is cut into ragged points at its edge.
6.3 Long cape: hangs from the shoulders at the back and on the sides, behind the arms (the arms come out in front of it).
    - At the back it goes down to Z 0.20 (a little above the ankles).
    - At the front it is open: two front panels hang from the shoulders down on each side of the body, outside the legs, down to Z 0.25. The front of the body (jacket, belt, legs) stays visible between the panels, a gap 0.30 to 0.40 wide.
    - It is wide: at its bottom the cape measures 1.10 m across from the left edge to the right edge, so it flares out from the shoulders like a bell; seen from the side it stands 0.10 to 0.15 away from the back of the legs.
6.4 Folds: at least 6 big vertical folds running from the shoulders to the bottom edge (waves of 0.03 to 0.05 depth), clearly visible in the back view.
6.5 Bottom edge: torn. Cut it into irregular triangular rags: at least 20 points, from 0.05 to 0.18 long, of different widths, some with holes 0.03 to 0.06 wide just above the edge. Not a straight edge and not a regular zig-zag.
6.6 The cape has thickness (0.005 to 0.01, Solidify modifier applied or real geometry) so it is not invisible from the inside, and it must not cut through the body, the arms or the helmet: where it would, push it out.
6.7 A small cluster of white shells pinned on the cape at the front of her LEFT collarbone (X +0.12, Z 1.37): 3 small shell shapes, 0.02 to 0.03 each, off-white RGB (0.88, 0.85, 0.78).

### Group 7 - Waist gear: rope, pouches, cases

7.1 Coiled rope on her RIGHT hip (-X): a bundle of 4 loops of beige rope, RGB (0.70, 0.62, 0.47), rope thickness 0.015, hanging from the lower belt at X -0.17, Z 0.98, the loops reaching down to Z 0.72. Each loop is an oval 0.16 high and 0.10 wide; the loops overlap. Make the rope a real twisted cord (a curve with a bevel and a twist, or a spiral of 2 or 3 strands), not a smooth tube.
7.2 Right-hip canister (in front of the rope, a bit lower): a brass and leather cylinder lying almost horizontal, 0.20 long, 0.07 across, centre at X -0.24, Z 0.90, Y -0.03. Brass end caps and two brass bands. Brass colour RGB (0.62, 0.45, 0.20), metallic 1.0, roughness 0.35.
7.3 A round leather pouch on her right hip, above the canister: a flattened sphere 0.09 x 0.06 x 0.08 with a flap, centre X -0.20, Z 0.99.
7.4 Map tube on her LEFT hip (+X): a tall cylinder hanging vertically from the lower belt, 0.45 long, 0.075 across, from Z 0.98 down to Z 0.53, centre X +0.22, Y -0.02. Leather body in brown, brass cap at the top and at the bottom (each 0.04 high), two leather straps around it. Beside it, next to it on the outside, a second thinner cylinder 0.35 long, 0.05 across.
7.5 A torn piece of cream cloth hanging from the lower belt on her left, between the map tube and the leg: 0.07 wide, from Z 0.98 down to Z 0.62, with a ragged lower end.
7.6 Small brown leather pouches along the belt: 3 of them, each about 0.06 x 0.05 x 0.03, at the back and on the sides of the belt.

### Group 8 - Legs and boots

8.1 Trousers: grey-brown, RGB (0.22, 0.19, 0.16), slightly loose, from the waist to the boots. Thigh 0.15 across at the top, 0.11 above the knee. Add 2 or 3 creases at the back of the knee.
8.2 Knee pads: round leather pads on both knees, 0.11 across and 0.025 thick, centre at Z 0.50, on the front of the knee, held by a strap around the leg above and below.
8.3 Shin wraps: just under the knee pad, a band of cream cloth wrapped around the leg, from Z 0.40 to Z 0.46, made of 3 overlapping rings.
8.4 Boots: tall brown leather boots, RGB (0.30, 0.18, 0.10).
    - The boot shaft goes from the ankle up to Z 0.42, 0.12 across at the top, 0.09 at the ankle.
    - The top of the shaft has a folded-down cuff 0.04 high, slightly wider.
    - Lacing at the front of the shaft: two rows of eyelets 0.03 apart, from Z 0.10 to Z 0.40, and 8 crossed laces (X shapes) between them, lace colour light tan RGB (0.55, 0.42, 0.28), lace thickness 0.004.
    - One strap with a brass buckle around the ankle (Z 0.09) and one around the top of the shaft (Z 0.38).
    - The foot: 0.27 long from heel to toe, 0.10 wide, toe slightly rounded, pointing straight forward (to -Y). Toe at Y -0.19, heel at Y +0.08.
    - Sole 0.02 thick, darker RGB (0.12, 0.08, 0.06); heel block 0.03 high at the back of the sole.

### Group 9 - The diving helmet and back gear

9.1 Position: the helmet is carried on her upper back, ON TOP of the cape (the cape is between her back and the helmet). Its centre is at X 0, Y +0.25, Z 1.30. Its top is at Z 1.47 (level with the base of the neck), its bottom at Z 1.13. It is 0.32 wide and 0.30 deep.
9.2 Shape: a brass dome, rounder at the top, flattening a bit at the bottom where it sits on a brass collar ring (the breastplate rim) 0.03 high, 0.30 across.
9.3 Main porthole: on the face of the helmet that looks BACKWARDS (towards +Y, so it is seen in the back view): a round window 0.13 across, its frame a thick brass ring 0.02 wide, sticking out 0.025. Inside: glass, RGB (0.55, 0.70, 0.65), slightly transparent and shiny, with a brass cross grille dividing it into 4 parts (2 thin bars, 0.008 wide).
9.4 Side portholes: one small round window on each side (towards -X and +X), 0.07 across, with a brass frame.
9.5 Rivets: a ring of small brass half-spheres (0.008 across) around the main porthole (12 of them) and around the collar ring (16 of them).
9.6 Brass bands: two vertical raised bands from the top of the dome down to the collar, 0.015 wide, on the left and right of the main porthole.
9.7 Colour: aged brass RGB (0.62, 0.45, 0.20), metallic 1.0, roughness 0.35, with darker edges RGB (0.35, 0.24, 0.10) where pieces meet.
9.8 Hoses: two ribbed hoses (made of many short rings, like a corrugated tube), 0.03 across, coming out of the lower sides of the helmet. On her right side (-X) the hose goes down and coils into a flat spiral disc, 0.12 across, hanging at X -0.12, Y +0.20, Z 1.00 (seen in the side drawings at hip height). On her left side (+X) the hose goes down and forward under her arm towards the belt at X +0.17, Z 1.02.
9.9 Bedroll: under the helmet, across the lower back, a horizontal roll 0.34 long and 0.11 across, centre X 0, Y +0.22, Z 1.06. Cream-tan canvas RGB (0.66, 0.58, 0.45), held by two brown leather straps around it (each 0.02 wide), at X -0.10 and X +0.10.
9.10 A few loops of beige rope (the same rope as 7.1) hanging from the bottom of the helmet over the bedroll: 2 loops, 0.12 long.
9.11 Harness: the chest straps of 4.3 come over the shoulders and hold the helmet: they reach the collar ring of the helmet at its top-left and top-right. Add one horizontal strap around the waist at the back, holding the bedroll.

### Group 10 - Materials pass, triangles, skeleton

10.1 Every object has a material with the colours given above. Leather: roughness 0.6 to 0.7. Cloth: roughness 0.85 to 0.95. Brass: metallic 1.0, roughness 0.3 to 0.4. Glass: transmission or alpha so it looks like glass. No pure black, no pure white.
10.2 Every surface has its outside facing out (recalculate normals). Shade smooth on organic parts (head, hair, hands, cape, rope, body); keep sharp edges only where metal or leather has a real edge (use auto smooth / smooth by angle at 30 degrees).
10.3 No hole in the body and no part floating in the air: every piece touches or sits on the piece that holds it (hands on wrists, pouches on belts, helmet on back, laces on boots).
10.4 Triangles: at most 40,000 for the whole character. Write in the log the count per object. Spend them where they are seen: face and hair about 6,000, hands about 4,000 (2,000 each), cape about 6,000, helmet about 5,000, rope and hoses about 4,000, everything else the rest. If you are above 40,000, lower the number of segments of small round pieces first (rivets, rope, laces), never the hands or the face.
10.5 Skeleton: keep your skeleton if you have one and fix it; build it if it is missing. Bones, with the exact names: Hips (at the hip centre, Z 0.95), Spine (Z 1.10), Chest (Z 1.27), Neck (Z 1.45), Head (Z 1.50 to 1.70); for each side (L = +X, R = -X): Shoulder.L/R (from the neck base to the shoulder joint), UpperArm.L/R (shoulder joint to elbow), LowerArm.L/R (elbow to wrist), Hand.L/R (wrist to the knuckles), UpperLeg.L/R (hip joint to knee), LowerLeg.L/R (knee to ankle), Foot.L/R (ankle to the ball of the foot), Toes.L/R (ball of the foot to the toe tip). The arm bones follow the A pose of 1.4 exactly; the leg bones follow the legs.
10.6 After you moved the body parts, bind again: parent every mesh of the character to the armature with automatic weights; the helmet, hoses, bedroll and back straps follow the Chest bone (weight 1.0 to Chest); the pouches, rope and map tube follow the Hips bone; the bracer follows LowerArm.L. Test it in a step: rotate UpperArm.L by 30 degrees, render "rev_prova_osso" with views fronte and tre_quarti, check that the sleeve, glove and hand follow the arm without tearing, then put the bone back to 0.

## D. Delivery (when it is done or when the hour is over)

D1. Save personaggio.blend (it replaces the round-1 file; the round-1 copy is personaggio_giro1.blend).
D2. Export personaggio.glb (glTF binary, the armature included, +Y up as Blender's exporter does).
D3. Run render_viste("finale_revisione_personaggio").
D4. Complete NOTE-revisione-personaggio.md: start and end time, number of steps, the list of groups 1-10 with "done", "partly" or "not done" for each, triangles in total, number of bones, the one piece (if any) you deleted and rebuilt and why, and what is still different from the reference.
D5. Reply to me in simple Italian: what you changed, what is now better than round 1, what is still missing.

Work on your own until the end without asking me anything, unless something blocks you completely.
