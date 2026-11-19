# Personaggio — gpt-astra

Inizio: 18 novembre 2026, ore 10:36 (Europe/Rome).
Scadenza: ore 12:36. Riferimento unico: riferimenti/1-personaggio.webp.

## Piano prima della modellazione
1. Proporzioni di una donna alta 1,70 m, posa A; corpo vestito, pantaloni, maniche, guanti e stivali.
2. Volto, capelli corti scuri e ciocca bianca; colletto e dettagli dell'abbigliamento.
3. Mantello verde strappato, cuciture, cinture, fibbie, tasche e protezioni.
4. Casco da palombaro in ottone sulla schiena, vetri, raccordi, tubi, corde e strumenti.
5. Scheletro umano con pesi, controllo di una posa di prova e ritorno alla posa A.
6. Verifica di scala, triangoli e pesi; esportazione GLB e sei viste finali.

Budget previsto: corpo/vestiti 10.000 triangoli; testa/capelli 8.000; mantello 4.000; attrezzatura 12.000; margine 6.000. Superfici a sezioni controllate, dettagli piccoli con pochi lati, nessuna suddivisione non applicata. Conteggio effettivo prima dell'esportazione: massimo 40.000 triangoli.

Ogni passo viene eseguito attraverso il kit fuori dall'ambiente isolato e salva personaggio.blend. Render intermedi controllati prima di procedere.

## Consuntivo
- Fine: 18/11/2026 11:03:49 (Europe/Rome).
- Tempo trascorso: 27.8 minuti, entro il termine delle 12:36.
- Passi del progetto eseguiti attraverso il kit: 16, compresi controlli diagnostici e tentativi corretti; esclusa la prova iniziale.
- Altezza: 1.700000 m, dalla suola alla sommità dei capelli. Posa di riposo A.
- Triangoli nel file Blender: 39,012; nel GLB effettivo: 39,012. Entrambi sotto 40.000. L'esportatore ha eliminato tre triangoli degeneri.
- Scheletro: 62 ossa (Root, bacino, colonna, collo, testa, spalle, braccia, mani, dita, gambe, piedi, dita dei piedi e 9 ossa del mantello).
- Vertici senza pesi: 0. Massimo 4 influenze per vertice; pesi normalizzati.
- Un'unica mesh deformabile e un unico materiale PBR; UV non sovrapposte generate per un atlante comune.
- Tre texture 4096 x 4096 create e cotte dentro Blender: BaseColor, Normal tangent-space, ORM (R=1, G=roughness, B=metallic).
- Texture incorporate sia nel .blend sia nel .glb. Nessun modello, immagine o materiale scaricato.

## File consegnati
- `personaggio.blend`: versione finale con rig e texture incorporate.
- `personaggio.glb`: glTF 2.0 binario, metri, Y up, scheletro e texture incorporati; circa 26.6 MB.
- `personaggio_sorgente.blend`: copia precedente all'unione e alla cottura delle texture, con pezzi separati e materiali procedurali, utile per modifiche.
- `personaggio_BaseColor.png`, `personaggio_Normal.png`, `personaggio_ORM.png`: copie delle texture.
- Sei render in `../outbox/finale_personaggio_*.png`: fronte, destra, retro, sinistra, tre_quarti, alto, 1536 x 1536.
- `verifica_rig.json` e `verifica_glb.json`: misure e risultati dei controlli.

## Controlli fatti
- Confronto delle viste intermedie con l'unico riferimento 1-personaggio.webp.
- Corrette compenetrazioni delle falde, spalle e fasce al ginocchio, oltre a una prima versione troppo spigolosa di volto e capelli.
- Prova di posa di braccio, gamba, testa, dito e mantello; poi ritorno alla posa A senza salvare animazioni.
- Controllato il contenuto binario del GLB: una mesh, un materiale, 3 immagini incorporate, 62 articolazioni della skin, attributi di pesatura e UV presenti.
- Reimportato il GLB in Blender: altezza 1.700000 m, 62 ossa, nessun vertice senza pesi. Una rotazione dell'avambraccio muove 1516 vertici della mesh importata.
- Guardati i render della reimportazione per verificare materiali e silhouette. Il primo export senza scheletro e un controllo interrotto dalla forma ausiliaria delle ossa sono stati corretti; il GLB finale contiene il rig.

## Risultato e limiti
- Riconoscibili mantello verde strappato e consumato, ciocca bianca, casco in ottone con oblò e griglie, tubi corrugati, corde, astuccio, bussola, guanti, stivali allacciati e cinture.
- Volto e capelli sono una interpretazione stilizzata: non riproducono tutta la finezza e l'espressione del disegno. Le pieghe e gli strappi sono più semplici e regolari del riferimento.
- Il mantello ha ossa aggiuntive, ma non una simulazione fisica. Pose estreme possono richiedere correzioni dei pesi o delle compenetrazioni.
- Scheletro di deformazione con nomi leggibili per un flusso umanoide; nessun controllo IK, rig facciale, blendshape o clip di animazione consegnato.
- Esportazione e deformazione verificate in Blender. Importazione, creazione Avatar Humanoid e retargeting in Unity non sono stati collaudati in questa sessione.
- Nessuna modifica al kit e nessun accesso alle cartelle degli altri concorrenti.
