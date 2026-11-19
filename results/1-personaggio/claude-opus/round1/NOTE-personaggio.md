# NOTE - personaggio (claude-opus)

Inizio: 00:20 (limite 02:20)

## Piano
Tutto fatto con codice: una piccola libreria (`lib.py`) con una funzione "loft" che crea tubi
a sezione ellittica (anelli con larghezza, profondità davanti e dietro diverse). Con questa costruisco
corpo e vestiti a pezzi, ogni pezzo con il suo materiale.

Ordine:
1. Scheletro umano (Hips, Spine, Chest, Neck, Head, Shoulder/UpperArm/LowerArm/Hand, UpperLeg/LowerLeg/Foot/Toes, L e R) in posa A, alta 1.70 m, rivolta verso -Y.
2. Corpo vestito: busto (gilet scuro, camicia blu), gambe (pantaloni), braccia (maniche chiare arrotolate), guanti con dita, testa, collo.
3. Testa: viso (naso, occhi, sopracciglia, labbra, orecchie), capelli corti spettinati con ciocca bianca.
4. Stivali alti con risvolto e lacci, ginocchiere, bracciali di cuoio.
5. Cinture, cinghie incrociate sul petto, fibbie, borse, cilindri, corde arrotolate sul fianco, strisce di stoffa.
6. Mantello verde strappato (bordo inferiore irregolare, pieghe, colletto alto, parte bassa più chiara e sporca).
7. Elmo da palombaro in ottone sulla schiena (oblò, bulloni, tubi, rotolo sotto).
8. Pesi delle ossa (calcolati per distanza dalle ossa, con limiti per pezzo), unione in un solo mesh, prova di piegatura.
9. Esportazione glb, render finali, note.

Triangoli: ogni pezzo ha un numero fisso di segmenti (8-24 per anello), conto i triangoli a ogni
passo. Obiettivo circa 20-30 mila, sotto il limite di 40 mila. Niente subdivision non controllate.

## Registro passi
- p01 scheletro (21 ossa) + corpo base, posa A
- p02 viso (occhi, sopracciglia, naso, labbra, orecchie) + primi capelli (troppo a punte)
- p03 capelli rifatti: ciocche piatte e ondulate, ciocca bianca davanti a destra
- p04 vestiti: tunica, gilet con bottoni, cinghie incrociate con anello, cinture, borse, astuccio lungo, barattolo d'ottone, corda arrotolata, stracci, ginocchiere, stivali con risvolto/lacci/fibbie, bracciali, maniche arrotolate, quadrante sul polso
- p05 mantello strappato (due volte: la seconda più lungo, più largo in basso, colore più spento)
- p06 elmo da palombaro sulla schiena: oblò con grata, oblò laterali e in alto, bulloni, fasce, tubo ad arco, tubi, spirale, rotolo, corda
- p07 elmo più grande e attaccato alla schiena, mani girate e ingrandite, colori più spenti
- p08 pesi delle ossa (distanza dalle ossa, pezzi rigidi come elmo/borse con peso unico) + unione in un mesh
- p09 prova di piegatura (braccia, gamba, testa, busto): funziona
- p10 ricostruzione completa con miglioramenti (spalle più strette, viso più femminile, corda più grande)
- p08 di nuovo (pesi sul modello ricostruito)
- p11 luci finali, controlli, esportazione glb
- p12 scalato a 1.70 m esatti, glb riesportato e verificato reimportandolo, render finali

## Risultato
Fine: 00:34 (circa 14 minuti di lavoro secondo l'orologio del PC)
Passi eseguiti con il kit: 14 (dal 002 al 015)
Triangoli: 33.440 (limite 40.000)
Ossa: 21 - Hips, Spine, Chest, Neck, Head, Shoulder/UpperArm/LowerArm/Hand L e R, UpperLeg/LowerLeg/Foot/Toes L e R
Altezza: 1.700 m. Un solo mesh "Esploratrice" con 20 materiali, legato allo scheletro (massimo 3 ossa per vertice, nessun vertice senza peso).
File: personaggio.blend, personaggio.glb (1 MB, Y in alto, metri; reimportato e controllato), finale_personaggio_*.png (anche in outbox).
Gli script p01-p12 e lib.py rifanno tutto da zero (p10 + p08 + p11 + p12).

## Cosa manca / cosa non va
- Nessuna texture: solo colori pieni per materiale (niente sporco dipinto, cuciture, venature del cuoio). Il mantello ha 3 toni per la parte bassa sporca invece di una sfumatura.
- Il viso è semplice e un po' squadrato, poco femminile rispetto al disegno; occhi e naso sono forme semplici.
- Il mantello è un unico pezzo rigido legato a busto/bacino: se le gambe si muovono molto, le gambe possono attraversarlo (non c'è simulazione di stoffa).
- I pezzi sono gusci separati uniti in un mesh (non una pelle unica): va bene per un gioco, ma ci sono compenetrazioni nascoste.
- Le dita non hanno ossa proprie (la mano si muove intera).
- Il ginocchio nella prova di posa sembrava piegato all'indietro, ma era il segno della mia rotazione di prova, non un problema dello scheletro.
- Nessuna UV mappata con cura (servirebbe solo per texture future).
- File in più: personaggio_prima_skin.blend (copia di sicurezza prima dell'unione) e personaggio.blend1 (backup automatico di Blender).
