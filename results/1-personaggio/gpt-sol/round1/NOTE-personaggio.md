# Personaggio — gpt-sol

Inizio: 18 novembre 2026, ore 11:18 (ora locale). Scadenza: 13:18.
Riferimento unico: `riferimenti/1-personaggio.webp`.

## Piano prima della modellazione
1. Proporzioni femminili alte 1,70 m, posa A della vista frontale: corpo vestito, viso, mani e stivali.
2. Mantello verde consumato, colletto rialzato, lembi strappati e pieghe; capelli corti scuri con ciocca chiara.
3. Imbracatura e cintura, guanti, ginocchiere, fibbie, cuciture e lacci; borse, corde e contenitori.
4. Casco da palombaro in ottone sulla schiena, oblò protetto, raccordi, tubi e zaino inferiore.
5. Scheletro umano con dita, pesi dei vertici e prova di deformazione. Controllo altezza, triangoli, materiali e GLB per Unity.

Geometria a sezioni con numero di lati controllato; dettagli piccoli con pochi segmenti, rilievi e texture generate con codice in Blender. Obiettivo 30–38 mila triangoli, limite assoluto 40 mila. Nessuna suddivisione globale. Verifica del conteggio prima della consegna.

Ogni passo importante: salvataggio `personaggio.blend`, render delle viste pertinenti, confronto visivo e correzioni prima di proseguire.

## Consuntivo
Fine: 18/11/2026, ore 11:55:34 (ora locale).
Tempo trascorso: circa 38 minuti, entro la scadenza delle 13:18. L'inizio e stato annotato al minuto.
Esecuzioni del kit per il progetto: 21 (la prova iniziale e esclusa); 3 esecuzioni interrotte per errori di script o controllo, poi corrette. Compresi ripristino, diagnostica e verifiche di esportazione.

### Modello consegnato
- Altezza effettiva: 1.700000 m, suole a quota zero. Unita Blender in metri.
- Posa di riposo A, braccia aperte e inclinate in basso, come fronte e retro del riferimento.
- 37,740 triangoli reali, tutti espliciti; margine di 2,260 sul limite di 40.000.
- 19,730 vertici nella mesh Blender. Una mesh skinned, 23 materiali.
- 53 ossa totali: 50 dello scheletro umano, comprese dita, pollici e root, piu 3 del mantello. Una root di controllo non deformante; 52 ossa deformanti.
- Tutti i vertici hanno pesi; massimo 2 influenze per vertice. Provati gomiti, ginocchio, dita e mantello in posa; poi ripristinata la posa A.
- Corpo vestito, viso, capelli scuri con ciocca chiara, mantello verde con strappi geometrici e usura, colletto, imbracatura, cintura, guanti, quadrante sul bracciale, ginocchiere, stivali con lacci e fibbie.
- Casco in ottone sulla schiena con tre oblo, griglia, rivetti, valvola, tubi corrugati e zaino inferiore. Ai fianchi: corde, borsa, portamappe, cannocchiale e bussola.
- Albedo, normal map e rugosita generate con codice dentro Blender, senza risorse esterne. Texture incorporate nel blend e nel GLB.

### File e verifiche
- `personaggio.blend`: scena modificabile con rig, luci e camera di presentazione. F12 usa la camera inclusa.
- `personaggio.glb`: glTF 2.0 binario, metri, Y up, mesh e scheletro, senza luci/camere o animazioni predefinite; texture incorporate, nessun file esterno necessario.
- GLB reimportato in Blender e controllato: stessi 37,740 triangoli, 53 ossa, altezza 1,70 m, zero vertici senza peso. Materiali controllati tramite render della sola copia importata.
- `verifica_personaggio.json`: conteggi, altezza, struttura delle ossa e controlli del GLB.
- Sei render finali a 1440 x 1440 in `../outbox/finale_personaggio_*.png`, piu i dettagli di viso e casco. Anche i render intermedi e la prova delle deformazioni sono nella outbox.

### Limiti e differenze dal riferimento
- Interpretazione stilizzata: viso e capelli sono piu semplici e meno realistici del disegno; non e una riproduzione fotorealistica.
- Le pieghe fini, l'invecchiamento e alcuni piccoli ornamenti sono semplificati. Gli accessori sono modellati con geometrie separate all'interno della mesh unita.
- Scheletro FK con pesi, senza IK, rig facciale, blendshape o clip di animazione. Il mantello dispone di ossa per animazione secondaria, senza simulazione fisica.
- Non e stato aperto Unity: verifica di esportazione e reimportazione eseguita in Blender, non prova dell'Avatar Humanoid nell'editor Unity.
- Il difetto apparente visto durante il primo confronto del GLB derivava dalla sovrapposizione di originale e copia importata nel render; risolto isolando la copia importata. Rimosse anche facce di area nulla e triangolata esplicitamente la mesh.

Riferimento unico utilizzato: `riferimenti/1-personaggio.webp`. Nessuna modifica al kit, nessuna installazione, nessun download. Tutti i comandi avvia/passo eseguiti fuori dall'ambiente isolato di Codex, nel Blender visibile dell'utente.
