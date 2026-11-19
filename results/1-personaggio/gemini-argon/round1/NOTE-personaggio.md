# NOTE - Progetto 1: Personaggio (Esploratrice)

- **Concorrente**: `gemini-argon`
- **Ora di inizio**: `13:29`
- **Ora di fine**: `14:10`
- **Tempo impiegato**: `41 minuti` (su 2 ore disponibili)
- **Numero di passi eseguiti**: `8` passi per il progetto personaggio (`003`–`010` nella sessione Blender, `10` totali inclusi i 2 passi della prova preliminare)
- **Altezza finale**: `1.7000 m` (da `Z = 0.0000 m` sotto le suole a `Z = 1.7000 m` sulla cima dei capelli)
- **Conteggio triangoli finale**: `36.434` triangoli (limite massimo: `40.000` triangoli)
- **Numero di ossa dello scheletro (`Armature`)**: `21` ossa (`pelvis`, `spine`, `chest`, `neck`, `head`, `shoulder.L/R`, `upper_arm.L/R`, `forearm.L/R`, `hand.L/R`, `thigh.L/R`, `shin.L/R`, `foot.L/R`, `toe.L/R`), vincolate alla mesh unica `Personaggio` con pesi normalizzati pronti per Unity.

## Riepilogo dei passi svolti

1. **`passo1_corpo_base.py` / `passo1b_fix_volto_e_mani.py`**:
   - Configurazione di EEVEE e studio di illuminazione a tre luci (`Luce_Key`, `Luce_Fill`, `Luce_Back`) con fondo morbido.
   - Modellazione del corpo in posa "A" (altezza `1.70 m`): volto femminile scolpito, occhi con iride e pupilla, sopracciglia, capelli corti mossi a ciocche con la ciocca bianca anteriore sinistra, giacca blu-ardesia con nervature sul petto e falde sui fianchi, camicia interna beige, pantaloni con pieghe, ginocchiera corazzata sul ginocchio destro, fasce alle gambe, stivali alti con stringhe incrociate e guanti lunghi con cinque dita separate.
2. **`passo2_mantella_e_cinture.py`**:
   - Creazione della mantella verde a doppio strato (con spessore reale `Solidify` per evitare problemi di backface culling in Unity), colletto alto, spallacci drappeggiati, pieghe verticali, fori e lembo inferiore strappato a punte irregolari, con texture procedurale che sfuma dal verde muschio al fango/ocra sul fondo.
   - Aggiunta dei cirripedi/conchiglie sulla spalla sinistra, cinghie incrociate sul petto con fibbie in ottone, doppia cintura in vita con medaglione rotondo chiaro e lembi di stoffa logora sui fianchi.
3. **`passo3_casco_e_accessori.py` / `passo4_rifinitura_dettagli.py`**:
   - Modellazione del casco da palombaro in ottone dietro le spalle con grande oblò posteriore e due oblò laterali dotati di vetro verdastro, griglie incrociate bombate e bulloni, più valvole superiori e tubi corrugati.
   - Aggiunta della sacca arrotolata sotto il casco con cinghie e tubi curvi pendenti, della corda arrotolata a 5 spire e borraccia sul fianco destro, dell'astuccio cilindrico lungo in pergamena con ghiere in ottone sul fianco sinistro, e della bussola/manometro da polso con quadrante verde luminoso sull'avambraccio sinistro.
4. **`passo5_scheletro_e_ottimizzazione.py`**:
   - Ottimizzazione selettiva dei poligoni fino a `36.434` triangoli, unione in un'unica mesh `Personaggio` con UV e materiali PBR impacchettati, creazione dell'`Armature` umanoide a 21 ossa con pesi vertice continui ed esportazione di `personaggio.blend`, `personaggio.glb` e dei 6 render `finale_personaggio_*.png`.

## Cosa è venuto bene e cosa manca / è semplificato

- **Cosa è venuto bene**:
  - La silhouette generale in posa "A" e la corrispondenza con le viste del riferimento (fronte, retro e profili).
  - Il casco da palombaro in ottone sulla schiena (con oblò posteriore e laterali a griglia, bulloni, tubi e sacca arrotolata inferiore).
  - La mantella verde strappata a doppio strato con texture organica usurata/fangosa sul fondo, strappi e fori passanti.
  - Il corredo di accessori (corda a spire e borraccia a destra, astuccio cilindrico a sinistra, bussola da polso verde sull'avambraccio sinistro, stivali allacciati e ginocchiera destra).
  - La pulizia tecnica per Unity: un'unica mesh `Personaggio` di `36.434` triangoli associata a uno scheletro umanoide di `21` ossa con texture impacchettate nel `.glb`.
- **Cosa è semplificato o perfettibile**:
  - I lineamenti del volto e le ciocche dei capelli hanno uno stile leggermente stilizzato/geometrico rispetto al disegno pittorico 2D.
  - Le micro-incisioni sul quadrante dello strumento da polso e i nodi minuti delle corde sono rappresentati tramite geometria semplificata per restare comodamente sotto il budget di 40.000 triangoli.
