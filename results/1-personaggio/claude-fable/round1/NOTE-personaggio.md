# NOTE - personaggio (claude-fable)

- Ora di inizio: **00:38** (limite 02:38)
- Ora di fine: **01:03**
- Tempo usato: **circa 25 minuti** su 2 ore

## Piano (scritto prima di modellare)
Tutto fatto con codice (lib.py = funzioni comuni, poi un file per ogni passo).
Il personaggio guarda verso -Y, alto 1.70 m, posa ad "A" come nelle viste fronte/retro.

Ordine dei pezzi:
1. scena (luci), scheletro, busto (tunica), gambe, stivali
2. braccia, guanti/mani, testa, viso, capelli
3. mantello verde strappato + colletto
4. elmo da palombaro sulla schiena, rotolo, tubi
5. cinture, cinghie incrociate, corde, borse, cilindri, stracci, ginocchiera
6. ritocchi dopo il confronto con il disegno, texture fatte con codice
7. pesi dello scheletro (calcolati per ogni pezzo), prova di posa, esporta glb, render finali

Triangoli (limite 40.000): ogni pezzo e' fatto di "tubi" a pochi lati (6-24 lati),
niente suddivisioni; conto i triangoli a ogni passo. Obiettivo 25-35 mila.

## Risultato
- **Triangoli: 26.532** (limite 40.000)
- **Ossa: 34**: Hips, Spine, Chest, Neck, Head; per ogni lato Shoulder, UpperArm, LowerArm, Hand,
  5 dita (un osso per dito), UpperLeg, LowerLeg, Foot, Toes; piu' 3 ossa per il mantello (Cape1-3).
  Nomi in stile Unity (Left.../Right...).
- **Una sola mesh** ("Personaggio") legata allo scheletro; tutti i vertici hanno pesi (0 senza peso).
- **Altezza: 1.700 m**, piedi a quota 0, guarda verso -Y in Blender (in avanti in Unity dopo l'esportazione Y-su).
- **Materiali: 21**, 14 texture fatte con codice (numpy): mantello 512 px con macchie di fango e segni chiari,
  le altre 256 px ripetibili (cuoio, lino, ottone con patina verde, ecc.). Nessun file preso da fuori.
- Facce a un solo lato (backface culling attivo): ho controllato con i render che non ci siano facce girate.
  Il mantello e il colletto hanno uno strato interno, quindi si vedono anche da dentro.
- File glb: 2,6 MB, 1 mesh, 1 skin con 34 ossa (controllato leggendo il file).

## Passi
- File di passo: 7 (p01 ... p07) + lib.py. Ogni file si puo' rieseguire da solo.
- Passi eseguiti in Blender in tutto: 82 (molti sono ricostruzioni complete p01->p07 dopo una correzione).
- Per rifare tutto da zero: eseguire in ordine p01, p02, p03, p04, p05, p06, p07.

## Correzioni fatte guardando i render
- capelli: prima erano punte che coprivano il viso, rifatti a ciocche grosse con la ciocca bianca
- mantello: aggiunti i lembi davanti sopra le spalle, pieghe, orlo strappato, tagli
- la texture del mantello non si vedeva (mappa UV non attiva): corretto
- facce girate nel mantello e nelle barrette (lacci, sopracciglia): corrette
- mani: prima col pollice in giu', ora palmi in avanti e pollice in alto
- viso: mento piu' corto, occhi a meta' testa
- altezza: era 1.734 m, portata a 1.700 m

## Cosa manca o non e' venuto bene
- Il viso e' semplice e stilizzato (occhi, naso e labbra sono pezzi appoggiati), non somiglia molto al disegno.
- Lo stile e' "low poly" a colori puliti: manca il tratto disegnato e molti piccoli dettagli (cuciture, fibbie fini, lacci del corpetto).
- I pezzi sono volumi che si compenetrano (non un'unica pelle chiusa): va bene per un gioco, ma non e' una mesh "a tenuta".
- 21 materiali sono tanti per un gioco: si potrebbero unire in un atlante.
- Le texture ripetibili usano una proiezione piatta semplice: da vicino si vedono giunte.
- Dita: un solo osso per dito. Niente ossa per viso, corde e oggetti appesi (seguono rigidamente bacino o petto,
  quindi in animazioni forti possono entrare nelle gambe).
- Mantello: 3 ossa sulla schiena; i lembi sulle spalle seguono le braccia ma possono compenetrarsi alzando molto le braccia.
- Proporzioni delle braccia: un po' piu' lunghe che nel disegno (li' sono molto corte) per avere uno scheletro credibile.
- Non provato dentro Unity: ho solo controllato il contenuto del file glb e una posa di prova in Blender.
