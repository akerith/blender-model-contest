# Results - project 1, the character

Measurements only. The blind judging of quality has not happened yet.

Limits set by the rules: 40,000 triangles, a human skeleton bound to the mesh, height 1.70 m, 2 hours for round 1 and 1 hour for the revision.

## Round 1 (17-18 November 2026, medium reasoning effort)

| Contestant | Time used | Triangles | Bones | Tokens in total | of which read from cache | written by the model | Cost at list price |
|---|---|---|---|---|---|---|---|
| qwen-max | 12 min | 13,392 | 19 | 2,910,064 | 2,599,877 | 82,947 | ~$1.54 |
| claude-opus | 14 min | 33,440 | 21 | 5,947,887 | 5,709,569 | 80,528 | ~$3.54 |
| claude-fable | 24 min | 26,532 | 34 | 7,408,649 | 7,069,842 | 117,150 | ~$8.32 |
| gpt-astra | 28 min | 39,012 | 62 | 5,468,524 | 5,309,952 | 57,441 | ~$9.19 |
| gpt-sol | 38 min | 37,740 | 53 | 7,191,294 | 6,852,224 | 73,001 | ~$1.95 |
| gemini-argon | ~31 min | 36,434 | 21 | 1,853,741 | 1,286,412 | 78,871 | ~$3.79 |
| gemini-hydrogen | 13 min | 11,610 | 21 | 3,553,287 | 3,328,331 | 56,146 | ~$1.17 |

The token and cost figures cover the whole session: the setup test plus the project.

## Revision round (18-19 November 2026, highest reasoning effort of each program)

| Contestant | Time used | Triangles | Bones | Tokens in total | of which read from cache | written by the model | Cost at list price |
|---|---|---|---|---|---|---|---|
| qwen-max | 56 min | 35,456 | 21 | 10,090,878 | 9,505,953 | 217,706 | ~$4.50 |
| claude-opus | 36 min | 39,377 | 21 | 20,301,069 | 19,693,154 | 239,916 | ~$10.58 |
| claude-fable | 54 min | 36,944 | 21 | 12,729,676 | 12,086,207 | 312,928 | ~$18.24 |
| gpt-astra | 48 min | 39,443 | 62 | 10,173,301 | 9,565,696 | 77,926 | ~$18.77 |
| gemini-argon | 48 min | 36,632 | 21 | 17,221,798 | 16,073,668 | 208,711 | ~$11.15 |
| gemini-hydrogen | 21 min | 39,244 | 21 | 14,481,919 | 13,173,405 | 205,889 | ~$5.17 |
| gpt-sol | in progress | | | | | | |

## Notes on single runs

- **qwen-max, round 1:** the provider's default effort is high, so this run was at high, not medium. It stopped by itself after 12 minutes of its 2 hours.
- **qwen-max, revision:** started at high for about two minutes of reading, then set to xhigh. In its last step it changed the scene lighting.
- **claude-fable, revision:** 24 of the 54 minutes were reasoning before the first step. Time is counted from the launch. The owner stopped the session after the delivery, so the revision notes file is incomplete; triangles and bones come from the terminal output. It also brightened the render background.
- **gpt-astra and gpt-sol, round 1:** at the start, Blender opened inside the program's sandbox and was invisible to the kit. Solved with one technical message; that time is not counted. Later prompts carry the same technical paragraph for everyone.
- **gpt-astra, revision:** stopped at minute 27 by the 5-hour usage limit of the subscription and resumed the next morning with the remaining 33 minutes; the clock was stopped in between. The first 27 minutes ran at xhigh, the rest at max. It reached 54,964 triangles mid-way and delivered 39,443 after decimation.
- **gemini-argon, round 1:** about 12 minutes spent waiting for the owner's approvals were removed from the time. Only the working session is counted, not four failed starts caused by the program's sandbox.
- **gemini-argon, revision:** ran at high, the highest level the program offers for this model. It rebuilt the head, the one piece it could not fix.
- **gemini-hydrogen, revision:** ran at xhigh, its highest level.

## How cost is computed

Cost is what the same session would cost on the pay-as-you-go API at list price. It is not what was paid: the runs used subscriptions. Prices in dollars per million tokens:

| Model | Input | Cache write | Cache read | Output | Source |
|---|---|---|---|---|---|
| Qwen 4 Max | 1.50 | - | 0.30 (estimate: 20% of input) | 4.50 | vendor price list |
| Claude Opus 5.5 | 4.00 | 5.00 | 0.20 | 20.00 | vendor price list, 3 Nov 2026 |
| Claude Fable 5.2 | 8.00 | 10.00 | 0.20 | 40.00 | vendor price list, 3 Nov 2026 |
| GPT 6 Astra | 10.00 | 12.50 | 1.00 | 50.00 | third-party listing sites, Oct-Nov 2026 |
| GPT 6.1 Sol | 2.00 | 2.50 | 0.10 | 10.00 | third-party listing sites, Oct-Nov 2026 |
| Gemini 4 Argon | 4.00 | - | 0.20 | 20.00 | third-party listing sites, Nov 2026 (full price; half until 30 Nov) |
| Gemini 4 Hydrogen | 1.50 | - | 0.15 (estimate: 10% of input) | 7.50 | third-party listing sites, Nov 2026 |

Not counted: the small service model Qwen Code uses (about 25,000 tokens), and the automatic reviewer models that approve commands in Codex and in Claude Code's automatic mode (their prices are not public).

Tokens are read from each program's own local usage records.
