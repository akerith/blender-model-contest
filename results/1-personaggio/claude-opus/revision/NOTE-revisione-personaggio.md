# NOTE - revisione personaggio (claude-opus)

Inizio: 16:19 (limite 17:19)
Fine: 16:55 (circa 36 minuti)
Passi eseguiti con il kit: 18 (dal 001 al 018, file `r00` ... `r11b` in questa cartella; libreria `rev_lib.py`)

Copie del giro 1, non toccate: `personaggio_giro1.blend`, `personaggio_giro1.glb`, `NOTE-personaggio_giro1.md`.

## Come ho lavorato
Ho aperto `personaggio.blend` del giro 1 (un solo mesh unito "Esploratrice" + scheletro). L'ho diviso nei suoi
391 pezzi e li ho raggruppati in oggetti con un nome (Testa, Capelli, Busto, Cinghie, Mantello, Elmo, ...).
Poi ho cambiato i pezzi che c'erano (spostati, ruotati, scalati, rimodellati) e ho aggiunto i pezzi mancanti.
Niente scena svuotata, niente personaggio rifatto da zero.

## Registro passi
- 001 r00_inizio: elenco oggetti + render `rev_inizio`
- 002 r01_gruppo1: divisione in pezzi + nuove proporzioni (ogni vertice spostato con i suoi pesi: braccia/gambe/testa con movimenti rigidi, busto con un campo che lo rimodella). Il passo si e' fermato all'ultima parte (scheletro) per un errore di contesto
- 003 r01b_ossa: scheletro sulle nuove articolazioni, render `rev_1`
- 004 r02_testa, 005 r02b_testa_fix: viso, colori, capelli (render `rev_2`)
- 006 r03_collo: collo, colletto camicia, colletto alto del mantello (render `rev_3`)
- 007 r04_busto: giacca, gonna della tunica, cinghie, cinture, medaglione (render `rev_4`)
- 008 r05_braccia, 009 r05b_braccia_fix: maniche, guanti lunghi, quadrante, mani (render `rev_5`)
- 010 r06_mantello: mantello (il pezzo rifatto), mantellina, conchiglie (render `rev_6`)
- 011 r07_cintura: corda, barattolo, borsa tonda, portamappe, stoffa, borsette (render `rev_7`)
- 012 r08_gambe: pantaloni, ginocchiere, fasce, stivali (render `rev_8`)
- 013 r09_elmo: elmo, tubi, rotolo, corde, imbracatura (render `rev_9`)
- 014 r10_materiali_ossa, 015 r10b_pesi_fix, 016 r10c_mantello_fianchi: materiali, normali, triangoli, pesi, prova osso (render `rev_10`, `rev_prova_osso`)
- 017 r11_consegna, 018 r11b_glb: salvataggio, glb, render `finale_revisione_personaggio`

## Gruppi
| Gruppo | Stato | Note |
|---|---|---|
| 1 Proporzioni e posa | fatto | altezza 1.699; posa A: braccio a 45° + avambraccio a 55° (piega 10°); gomito (0.395, 1.195), polso (0.538, 0.990), punta dito medio circa (0.647, 0.846); braccia a Y=0; spalle 0.40, petto 0.32x0.21 a 1.27, vita 0.27 a 1.08, fianchi 0.34; stivali a X ±0.13 |
| 2 Testa, viso, capelli | fatto | occhi a 1.585 distanti 0.065, sopracciglia inclinate verso il naso, naso 1.58-1.53, bocca dritta a 1.505, orecchie 1.55-1.59; capelli 0.205 larghi, cima a 1.70, 44 ciuffi spessi nuovi + 107 ciocche del giro 1 ingrossate; ciocca bianca sul suo lato destro |
| 3 Collo e colletti | fatto | collo 0.11; colletto camicia grigio-blu 1.41-1.46; colletto alto verde 1.415 → 1.52 dietro / 1.48 davanti, aperto davanti |
| 4 Busto | fatto | giacca blu notte; 4 cuciture nuove + 2 bordi del giro 1 = 6 linee; gonna 1.06-0.80, larga 0.41, aperta ai fianchi, orlo irregolare; 2 cinghie incrociate a 1.24 con fibbie quadrate a 1.30; cinghia sotto il petto a 1.20; cintura 1.06-1.12 con fibbia (cornice + ardiglione); cintura bassa inclinata 1.00 → 0.94; medaglione 0.04 a 0.99 con cordino |
| 5 Braccia | fatto | maniche crema gonfie con 3 anelli + rotolo sopra il gomito; guanti 0.075 → 0.095 con polsino svasato; 3 cinghie scure con fibbiette; quadrante verde sul polso sinistro; mani: palmo 0.085x0.08x0.03, 4 dita da 3 segmenti (0.075/0.085/0.08/0.065), aperte e piegate, pollice con base, 16 lati per dito |
| 6 Mantello | fatto | ricostruito (vedi sotto); colore verde con striature, fondo color sabbia con macchie (colori nei vertici, quindi anche nel glb); mantellina con punte; pannelli davanti; largo 1.14 in basso; 9 pieghe verticali; orlo a brandelli irregolari (punte 0.05-0.18) con buchi; spessore 0.007; 3 conchiglie a (0.12, 1.37) |
| 7 Attrezzi in vita | fatto | corda: 4 anelli ovali 0.10x0.16 con un secondo filo a spirale (corda ritorta) fino a 0.69; barattolo ottone/cuoio quasi orizzontale a (-0.24, -0.03, 0.90); borsa tonda con patta; portamappe 0.45 (0.98 → 0.53) con tappi e 2 cinghie + tubo sottile 0.35; stoffa crema 0.98 → 0.62; 3 borsette ai lati e dietro |
| 8 Gambe e stivali | fatto | pantaloni grigio-marroni con 3 pieghe dietro il ginocchio; ginocchiere tonde 0.11 a 0.50 con cinghie; 3 fasce crema 0.40-0.46; gambale fino a 0.42 (0.09 → 0.12) con risvolto; 8 lacci incrociati + 2 file di occhielli 0.03; cinghie con fibbia a 0.09 e 0.38; piede 0.27 (punta -0.19, tallone +0.08), suola scura 0.02, tacco 0.03 |
| 9 Elmo e zaino | fatto | elmo 0.32x0.30, da 1.13 a 1.48; oblo' dietro con griglia e vetro trasparente; oblo' laterali piccoli; 12 rivetti intorno all'oblo' + 16 sul collare; 2 fasce verticali; tubi corrugati (destro → spirale piatta 0.12, sinistro → cintura); rotolo 0.34x0.11 a (0, 0.22, 1.06) con 2 cinghie; 2 anelli di corda; cinghie spalle → elmo + cinghia orizzontale sul rotolo |
| 10 Materiali, triangoli, scheletro | fatto | 32 materiali, niente nero o bianco puro; normali ricalcolate; tutto liscio, spigoli a 30° sui pezzi di metallo/cuoio; 39.377 triangoli; 21 ossa con i nomi giusti; pesi automatici + pesi fissi (elmo/tubi/rotolo/cinghie dietro → Chest, borse/corda/portamappe → Hips, quadrante → LowerArm.L); prova UpperArm.L +30°: manica, guanto e mano seguono, osso rimesso a 0 |

## Numeri finali
- Triangoli: 39.377 (limite 40.000). Mani 2.248 ciascuna, testa 1.576 + capelli 3.897, mantello 5.868 + mantellina 888, elmo 4.674, corda + tubi + corde elmo 3.848.
- Per stare sotto 40.000 ho ridotto i segmenti (Decimate) di ciocche dei capelli, corda, fasce, mantellina, corde dell'elmo ed elmo (85%); mai mani o viso.
- Ossa: 21. Oggetti mesh: 52, tutti legati allo scheletro (massimo 4 ossa per vertice, nessun vertice senza peso).
- glb: `personaggio.glb` (1,6 MB), Y in alto, metri, con scheletro; reimportato e controllato: 52 mesh con pelle, 21 ossa, 39.377 triangoli.

## Il pezzo rifatto
Il mantello lungo. Quello del giro 1 era una campana chiusa con orlo a zig-zag regolare, senza pannelli davanti, e con lo
spessore gia' applicato: non si poteva rimodellare nella forma chiesta (pannelli davanti, svasato a campana, brandelli
irregolari). L'ho rifatto con lo stesso metodo (griglia + spessore), poi rigenerato una volta (passo 016) per aprirlo
all'altezza dei fianchi.

## Cosa e' diverso dal riferimento / cosa non va
- Colori: ho letto i valori RGB della scheda come colori dello schermo (sRGB) e li ho convertiti nei valori lineari di Blender (es. giacca 0.13, 0.16, 0.22 → 0.015, 0.022, 0.040). Con i numeri messi tali e quali la giacca "blu notte" usciva grigio chiaro e la pelle quasi bianca. Nel campo Base Color di Blender si vedono quindi numeri piu' bassi.
- Elmo un po' piu' indietro: centro a Y 0.275 invece di 0.25, se no il davanti dell'elmo entra nella schiena e nel mantello (il petto profondo 0.21 arriva gia' a Y +0.10). Spirale del tubo a X -0.195 invece di -0.12, se no entra nel rotolo.
- Mantello: tra i pannelli davanti, all'altezza dei fianchi, l'apertura e' di circa 0.59 (non 0.30-0.40), cosi' corda, barattolo e portamappe stanno davanti al mantello come nel disegno; in basso l'apertura e' 0.34. Il mantello e la mantellina sono pezzi rigidi legati al busto (niente simulazione di stoffa): se il braccio si alza molto passa dentro la mantellina, e con passi lunghi le gambe possono entrare nel mantello.
- Viso semplice (forme base), un po' lungo e poco femminile; mani con dita sottili e palmo squadrato.
- Capelli: i ciuffi sono un po' piatti e spigolosi dopo la riduzione dei triangoli; da dietro la ciocca bianca si vede poco.
- Niente texture dipinte (non ho usato GIMP/Krita/Inkscape): striature, sporco e macchie del mantello sono colori nei vertici; cuoio e metallo sono colori pieni.
- Restano alcuni dettagli del giro 1 non chiesti: bottoni della giacca, bordi scuri davanti, fermaglio al collo, oblo' in cima all'elmo, valvola e tubo ad arco.
- Un intoppo: dividere il mesh in pezzi ha cambiato l'ordine dei vertici in alcuni pezzi, e la prima versione di manica, guanto e quadrante e' uscita rotta. Li ho ripresi dal backup automatico del salvataggio del gruppo 4 (`personaggio_rev_g4.blend`) e li ho rimodellati con un metodo che non dipende dall'ordine.
- File in piu' in questa cartella: `personaggio_rev_g4.blend` (copia di sicurezza del gruppo 4), `personaggio.blend1` (backup automatico di Blender).
