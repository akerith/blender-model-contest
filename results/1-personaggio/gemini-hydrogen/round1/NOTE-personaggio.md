# NOTE - personaggio

- **Ora di inizio**: 14:26
- **Limite**: 2 ore (fino alle 16:26), max 40.000 triangoli, altezza 1,70 m, posa A, scheletro umano collegato per Unity.

## Piano di lavoro
1. **Base e Armatura (`01_base_armatura.py`)**: pulizia scena, luci di studio, scheletro umano completo (`Pelvis`, `Spine`, `Chest`, `Neck`, `Head`, braccia, mani, gambe, piedi), testa, volto, capelli corti scuri con ciocca bianca e corpo base alto 1,70 m in posa A.
2. **Abiti, Guanti e Stivali (`02_abiti_stivali.py`)**: tunica/giacca blu-grigia a strati, maniche beige, pantaloni, ginocchiera destra, stivali alti allacciati, guanti con risvolto e bussola da polso sul braccio sinistro.
3. **Mantello Verde Strappato (`03_mantello.py`)**: mantello con colletto alto, drappeggio sulle spalle e sulla schiena con bordo inferiore frastagliato/strappato e conchiglie sul petto.
4. **Casco da Palombaro, Zaino e Tubi (`04_casco_zaino.py`)**: casco sferico in ottone sulla schiena con oblò a croce, bulloni, sacco arrotolato sottostante e tubi flessibili di collegamento.
5. **Cinture e Accessori (`05_cintura_accessori.py`)**: cinghie incrociate sul torace, cintura con fibbia e ciondolo, corda arrotolata sul fianco destro, borraccia/tasche a destra e tubo portamappe sul fianco sinistro.
6. **Materiali, Skinning e Verifica (`06_skinning_verifica.py`)**: materiali PBR procedurali / texture generate da codice, collegamento di tutte le mesh all'armatura (automatic weights + pesi rigidi per gli accessori), controllo triangoli (< 40.000) e altezza (1,70 m).
7. **Esportazione Finale (`07_export_finale.py`)**: salvataggio `personaggio.blend`, esportazione `personaggio.glb` (Unity, metri, Y-up) e `render_viste("finale_personaggio")`.

## Risultato finale
- **Ora di fine**: 14:39 (durata effettiva: ~13 minuti)
- **Numero di passi**: 16 passi dedicati al personaggio (`002`–`017`, dopo il passo di prova `001`)
- **Triangoli totali**: 11.610 (limite: 40.000)
- **Altezza**: 1,702 m (da Z = 0,000 a Z = 1,702)
- **Ossa dell'armatura**: 21 ossa (`Pelvis`, `Spine`, `Chest`, `Neck`, `Head`, `Shoulder_L/R`, `UpperArm_L/R`, `Forearm_L/R`, `Hand_L/R`, `Thigh_L/R`, `Shin_L/R`, `Foot_L/R`, `Toe_L/R`), collegate alle mesh (pesi morbidi per corpo/abiti/mantello e pesi rigidi per testa e accessori).
- **File consegnati**:
  - `personaggio.blend`
  - `personaggio.glb` (999,4 KB, Y-up, metri, con armatura e skinning per Unity)
  - Render finali `finale_personaggio_*.png` in `outbox/`
- **Note / Cosa manca o migliorabile**:
  - Le dita delle mani sono modellate in un blocco unico (guanto con pollice separato) senza ossa individuali per ogni falange.
  - Il mantello e la tunica usano nodi procedurali Blender (`ShaderNodeTexNoise`) per le macchie del tessuto nei render; nell'esportazione `.glb` per Unity vengono mantenuti i colori base e i parametri PBR Principled BSDF.
