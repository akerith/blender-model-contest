# NOTE REVISIONE - personaggio (qwen-max)

- Inizio: 15:02 (2026-11-18). Fine: 15:58. Scadenza: 16:02 (1 ora).
- Giro 1 conservato intatto in: personaggio_giro1.blend / personaggio_giro1.glb / NOTE-personaggio_giro1.md.
- Riferimento: riferimenti/1-personaggio.webp (pose dei disegni 1 e 4).
- Passi eseguiti in questa sessione: 24 (inclusi diagnostici e correzioni).

## Stato alla partenza (rev_inizio)
- Unica mesh "Personaggio" 13.392 tri, 19 ossa, altezza 1,70.
- Difetti: braccia ~67° sotto orizzonte invece di 50°, mani a scatola fluttuanti, mantello corto (orlo ~0,80), casco piccolo con tubi verso il petto, capelli a calotta liscia con toppa bianca sul lato sbagliato, viso minimale, cintura sul bacino, stivali a blocchi con lacci ad anelli.

## Gruppi 1-10
1. Proporzioni e posa: done.mesh separata in 49 pezzi; braccia ruotate a 50° sotto orizzonte (gomito ±0,38/1,18, polso ±0,54/0,99); gambe leggermente a V (piedi ±0,13); vita stretta, bacino allargato; cavallo 0,86; testa a uovo 0,15×0,19, cranio 1,66.
2. Testa, viso, capelli: done. Occhi 1,585 distanti 0,065, sopracciglia inclinate, naso a cuneo 1,58-1,53, bocca 1,505 larga 0,045, orecchie; capelli = calotta + 60 ciuffi (lati fino a 1,50, nuca 1,48, ciuffi sulla fronte); ciuffo bianco sul lato DESTRO (-X) dalla riga verso dietro.
3. Collo, colletti: done. Colletto camicia grigio-blu 1,41-1,46; colletto alto del mantello aperto davanti, 1,52 dietro / 1,48 agli angoli.
4. Torso: done. 5 cuciture verticali; gonna tunica davanti/dietro fino a 0,80 con orlo irregolare; bandoliere incrociate a nastro (petto → spalle → schiena fino al casco) con fibbie 0,03; fascia petto 1,20; cintura principale 1,06-1,12 con fibbia 0,07×0,05 e perno; cintura bacino obliqua; medaglione 0,04 a 0,99.
5. Braccia: done. Maniche cream gonfie con 3 rolli; guanti cuoio con bordo svasato e 3 cinghie + fibbie; bracciale-gauge ottone 0,055 con vetro verde sul polso sinistro; mani ricostruite (palmo bevellato + 4 dita da 3 segmenti a 10 lati + pollice), palmi verso il basso/indietro.
6. Mantello: done. Rimappato la griglia esistente: campana larga 1,10 in basso, orlo 0,20 dietro / 0,25 davanti, pannelli frontali aperti (gap ~0,35), 6+ pieghe verticali, orlo strappato con punte 0,05-0,18 e buchi; spessore reale; materiale teal con striature chiare e fade sabbia negli ultimi 0,25 m; 3 conchiglie bianche sulla clavicola sinistra.
7. Corda, tasche, custodie: done. 4 loops ovali 0,16×0,10 sul fianco destro fino a 0,72, each con trecciolo a spirale (non tubo liscio); canister cuoio+ottone quasi orizzontale a (-0,24, 0,90); tasca rotonda con patta; tubo mappe 0,45 + tubo sottile 0,35 a sinistra con tappi ottone e cinghie; tela strappata 0,98-0,62; 3 tasche piccole sulla cintura.
8. Gambe e stivali: done. Pantaloni grigio-marrone con pieghe dietro il ginocchio; ginocchiere 0,11 con fasce sopra/sotto; fasce polpaccio a 3 anelli 0,40-0,46; stivali: fusto fino a 0,42 con risvolto, suola 0,02 + tacco 0,03, 16 occhielli e 8 lacci incrociati per stivale, cinturini caviglia e cima con fibbie.
9. Casco e zaino: done. Casco 0,32×0,30, centro (0, 0,25, 1,30), sopra il mantello; collare 0,30; oblò posteriore 0,13 con vetro, griglia a croce e 12 rivetti; 2 oblò laterali; 16 rivetti sul collare; 2 bande rilevate; tubi costolati: destro a spirale piatta 0,12 a (-0,12, 0,20, 1,00), sinistro sotto il braccio alla cintura; bedroll 0,34×0,11 a (0, 0,22, 1,06) con 2 cinghie; 2 loops di corda dal casco; harness posteriore + cintura schiena.
10. Materiali, triangoli, scheletro, skin: done. Colori/roughness da specifica (cuoio 0,6-0,7, stoffa 0,85-0,95, ottone metal 1 rough 0,35, vetri alpha); normali ricalcolate fuori; smooth sugli organici, smooth-by-angle 30° sul resto; 35.456 tri totali (log per oggetto nel passo 020); 21 ossa con i nomi esatti (Hips…Toes.L/R); rebind: pesi automatici su corpo/mantello/stivali, gruppi rigidi per accessori (casco/tubi/bedroll/harness → Chest, tasche/corda/tubi → Hips, gauge → LowerArm.L); pesi braccio rimossi dal mantello dopo la prova.

## Prova osso (10.6)
- UpperArm.L ruotato di 30°: render rev_prova_osso (fronte, tre_quarti): manica, guanto e mano seguono senza strappi; osso riportato a 0.

## Pezzo eliminato e ricostruito (uno solo, regola A3)
- Mano.L e Mano.R: erano scatole chiuse (muffole) senza dita, non correggibili con move/scale; ricostruite con palmo, 4 dita a 3 segmenti e pollice. Tutto il resto è stato modificato/aggiunto, mai cancellato.

## Consegna
- personaggio.blend salvato; personaggio.glb riscritto (2.089.468 byte, armatura inclusa, +Y up).
- Render finale_revisione_personaggio_* (6 viste) in outbox.
- Triangoli: 35.456 / 40.000. Ossa: 21. Altezza: 1,698 m (punte capelli comprimite a 1,70).

## Cosa resta diverso dal riferimento
- Capelli più "a punte" che ondulati: i ciuffi sono coni piegati, non ciocche morbide.
- Viso stilizzato e texture solo a nodi: niente pittura digitale (GIMP/Krita non usati).
- Striature del mantello più larghe e chiare del riferimento; fade sabbia ok.
- In vista laterale la spirale del tubo e parte del canister restano nascoste dai pannelli laterali del mantello (posizione da specifica rispettata).
- Bandoliere e harness sono nastri semplici, niente fibbie dettagliate sul retro.
- Gonna della tunica più corta del riferimento; niente simulazione cloth.
