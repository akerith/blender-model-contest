# NOTE - personaggio (qwen-max)

- Inizio: 23:45 (2026-11-17). Scadenza: 01:45.
- Riferimento: solo `riferimenti/1-personaggio.webp`.

## Piano
Parti da costruire, in ordine:
1. Scheletro umano (bacino, colonna, collo, testa, clavicol/braccia/mani, gambe/piedi L/R) in posa A (braccia ~20° aperte verso il basso). Altezza totale 1,70 m.
2. Corpo unico (bacino, torso, collo, testa, braccia, gambe) da primitive unite + remesh voxel + decimate; materiali per zona (pelle, tunica scura, maniche beige, pantaloni marroni).
3. Testa: capelli con ciuffo bianco, occhi, sopracciglia, naso, bocca. Mani con guanti scuri, bracciali di cuoio, gauge ottone sul polso sinistro.
4. Stivali alti con lacci e ginocchiere, cintura con tasche, corda arrotolata, contenitore cilindrico, cinghie incrociate sul petto, fibbia e chiusura del mantello.
5. Mantello verde strappato (fuori verde, dentro beige) fatto come griglia parametrica attorno alle spalle, orlo frastagliato.
6. Zaino-casco da palombaro in ottone: oblò con vetro e griglia, valvole, tubi verso il petto.
7. Skin: pesi automatici sul corpo, gruppi rigidi per accessorio (osso giusto per parte); tutto unito in una mesh con modificatore Armature. Prova di posa e reset.
8. Correzioni guardando i render (fronte/retro per la posa, lati per i volumi).
9. Export personaggio.glb (metri, Y su), render finale, note.

## Budget triangoli (max 40.000)
Corpo ~7.000, mantello ~3.000, casco+tubi ~2.000, stivali ~1.000, cintura/corda ~600, testa/mani ~800, resto ~500 → totale previsto ~15.000. Controllo il conteggio a ogni passo e decimo se serve.

## Risultato finale
- Fine: 23:57 (2026-11-17). Tempo impiegato: ~12 minuti.
- Passi eseguiti: 11 (uno con errore non bloccante, recuperato nel passo dopo).
- Triangoli: 13.392 (limite 40.000). Ossa: 19. Altezza: 1,70 m esatti. Posa A.
- Scheletro: pelvis, spine, chest, neck, head + clavicle/upper_arm/forearm/hand L/R + thigh/shin/foot L/R.
- Skin: pesi automatici sul corpo, gruppi rigidi per accessori; prova di posa: la mano si muove di 0,42 m ruotando il braccio di 45°, poi riportata a riposo.
- Consegne: personaggio.blend, personaggio.glb (~918 KB, metri, Y su, skin inclusa), render finale_personaggio_* (6 viste) in outbox.

## Cosa manca / non è riuscito
- Dita non separate: guanti a muffola, mani molto blocchettose.
- Viso stilizzato (occhi/naso/bocca geometrici), niente texture dipinte: solo colori a nodi.
- Mantello rigido sul petto: niente simulazione cloth, non si muove con le gambe.
- Amuleti/ciondoli piccoli del riferimento omessi; lacci degli stivali semplificati ad anelli.
- Il ciuffo bianco sembra una toppa rettangolare più che una ciocca.