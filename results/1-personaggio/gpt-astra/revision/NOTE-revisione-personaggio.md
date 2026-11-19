# Revisione personaggio - gpt-astra

Inizio: 18 novembre 2026, ore 18:38 (Europe/Rome). Termine: 19:38.
Copie immutabili create prima dell'apertura: personaggio_giro1.blend, personaggio_giro1.glb, NOTE-personaggio_giro1.md.
Sei viste rev_inizio esaminate prima di modificare il modello.
Il modello del primo giro e una mesh unita con atlante: per modificarne i pezzi vengono recuperati i nomi dal proprio file sorgente, senza sostituire la geometria del modello aperto.

Interruzione per limite di utilizzo: 18 novembre alle 19:05, dopo il gruppo 8.
Ripresa: 19 novembre 2026, ore 09:55 (Europe/Rome, inizio prudenziale).
Tempo residuo autorizzato: 33 minuti; termine della ripresa: 10:28.
Alla ripresa Blender era chiuso. Riapertura del salvataggio tramite kit e nuova verifica A2 delle sei viste prima delle modifiche.

## Consuntivo

Fine produzione: 19 novembre 2026, ore 10:14:27 (Europe/Rome). Sei viste definitive esaminate e consegna chiusa alle 10:15, entro il termine autorizzato delle 10:28. Tempo di ripresa utilizzato: circa 20 minuti dei 33 disponibili.
Passi della revisione: 28 file inviati al kit, di cui 27 completati e 1 errore iniziale di codifica prima di qualsiasi modifica. Prima dell'interruzione: 16 passi; alla ripresa: 12 passi, inclusi inventario A2, controlli, correzioni e consegna. Il comando bloccato dal limite di utilizzo alle 19:05 non fu eseguito e non e contato come passo.

| Gruppo | Stato | Intervento e limiti |
| --- | --- | --- |
| 1 - Proporzioni e posa | done | Altezza 1,70 m, piedi distanziati, arti e articolazioni portati alla posa ad A e alle quote principali richieste. |
| 2 - Testa, viso, capelli | partly | Testa e lineamenti rimodellati, occhi e bocca riposizionati, capelli scuri a ciocche e striscia chiara sul lato destro. Il volto e ancora stilizzato, i capelli restano meno naturali del disegno. |
| 3 - Collo e colletti | done | Collo, colletto grigio-blu e collo alto del mantello adattati alle nuove proporzioni. |
| 4 - Torso, cinghie, cinture | partly | Giacca navy, cuciture, falde anteriori e posteriori, incrocio delle cinghie, due cinture, fibbie e medaglione. Alcuni bordi delle cinghie e delle falde rimangono angolosi. |
| 5 - Braccia e mani | partly | Maniche a sbuffo, tre fasce dei guanti, strumento al braccio sinistro, palmi arrotondati e dita articolate. Pollici e transizioni del palmo sono ancora semplificati. |
| 6 - Mantello | done | Mantello allargato, due falde frontali, pieghe, bordo irregolare, fori e spessore reale; teal con striature e fondo sabbia. Tre conchiglie sul lato sinistro. Corretta la compenetrazione della falda posteriore. |
| 7 - Accessori alla vita | partly | Quattro giri di corda, canister orizzontale a destra, custodie verticali a sinistra, panno strappato e tasche. La torsione della corda e presente ma resta grossolana rispetto al riferimento. |
| 8 - Gambe e stivali | done | Pantaloni, ginocchiere bilaterali, fasce chiare, gambali, risvolti, suole, tacchi e otto incroci dei lacci con contatto corretto sugli stivali. |
| 9 - Casco e dorso | partly | Calotta riposizionata e ingrandita, oblo principale con croce, due laterali, 12 rivetti dell'oblo e 16 del collare, cinghie dorsali, due tubi, rotolo e due anelli di corda. Spirale del tubo e sezione del rotolo restano approssimati. |
| 10 - Materiali, budget e scheletro | done | Materiali assegnati, normali ricalcolate, superfici curve levigate, budget rispettato, scheletro esistente adattato e collegamento automatico rifatto. Pesi corretti per gli accessori e per le parti articolate. Prova del braccio a 30 gradi verificata e posa ripristinata. |

## Dati della consegna

- Triangoli effettivi nel GLB e nel progetto: **39.443**, sotto il limite di 40.000. Il primo controllo dopo la decimazione riportava 39.445; il conteggio finale usa la triangolazione effettiva del file esportato, verificata anche dopo reimportazione.
- Ossa: **62**, con tutti i nomi richiesti dal gruppo 10.5. Scheletro originale conservato e corretto.
- Altezza misurata: **1,700000 m**. Unita in metri; export glTF con Y verso l'alto.
- 535 mesh, 31 materiali, massimo 4 influenze per vertice; nessun vertice senza peso.
- Collegamento automatico eseguito con risultato FINISHED, senza vertici scoperti. Successivamente corretti i pesi locali: casco, tubi, rotolo e cinghie dorsali a Chest; accessori della cintura a Hips; bracciale a LowerArm.L.
- UpperArm.L ruotato di 30 gradi: viste fronte e tre_quarti esaminate, manica, guanto e mano seguono senza distacco visibile; osso riportato a zero.
- Riduzione iniziata da rivetti, corde, tubi e lacci, poi dettagli secondari e capelli. **Viso e mani non sono stati decimati.** Conteggi per oggetto in rev_budget.json, nei log e nel controllo finale.
- Texture del mantello BaseColor e Normal a 2048 px, create in Blender, salvate in texture/ e incorporate nel .blend e nel GLB. Il materiale procedurale originale della revisione e conservato come copia nel progetto.
- GLB reimportato in Blender: triangoli, altezza, ossa e pesi verificati; 460 vertici del palmo sinistro si muovono nella prova dell'osso. Verifica effettuata in Blender, non in Unity o in un motore esterno.

Nessun pezzo del personaggio e stato eliminato e ricostruito. La mesh del giro 1 e stata separata per recuperarne i pezzi e quindi deformata. Le sole copie temporanee importate per verificare il GLB sono state rimosse dopo il controllo. Le tre copie giro1 sono rimaste intatte.

## Differenze ancora presenti

Il risultato resta piu stilizzato e meno ricco di microdettagli del riferimento: volto, capelli, pollici, torsione della corda, tubi corrugati, bordi delle cinghie e usura del cuoio richiederebbero ulteriore rifinitura artistica. Le quote principali guidano il modello; le forme dei piccoli accessori sono approssimate. Per la testa sono state seguite le quote assolute del mento e del cranio, che nel testo non coincidono con l'altezza nominale indicata di 0,22 m.

File principali: personaggio.blend e personaggio.glb. Sei render di consegna in ../outbox/finale_revisione_personaggio_*.png. Controlli tecnici: verifica_revisione_rig.json, verifica_revisione_glb.json, verifica_revisione_finale.json. Tutti gli interventi 3D sono stati eseguiti dentro Blender attraverso il kit; nessun download, add-on o generatore esterno.
