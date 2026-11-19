import os,json,glob,datetime
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
character.hide_render=False;rig.hide_render=False;character.hide_set(False);rig.hide_set(False)
bpy.context.view_layer.update()
sc=bpy.context.scene;sc.cycles.samples=64;sc.cycles.use_denoising=True
save()
render_viste('finale_personaggio',risoluzione=1440)
portrait('finale_personaggio_dettaglio_viso',scale=.37,center=(0,0,1.57),loc=(.08,-1.5,1.60))
portrait('finale_personaggio_dettaglio_casco',center=(0,.18,1.30),scale=.52,loc=(.50,1.7,1.45))
sc.camera=bpy.data.objects['Presentazione'];sc.render.resolution_x=sc.render.resolution_y=1440
sc.render.filepath=os.path.join(OUTBOX,'presentazione_personaggio.png')
bpy.ops.object.select_all(action='DESELECT');character.select_set(True);bpy.context.view_layer.objects.active=character
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
save()

report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'))
character.data.calc_loop_triangles();tri=len(character.data.loop_triangles)
assert tri==report['glb']['triangoli'] and tri<=40000
assert len(rig.data.bones)==53
height=max(v.co.z for v in character.data.vertices)-min(v.co.z for v in character.data.vertices)
assert abs(height-1.70)<1e-5
assert all(any(g.weight>0 for g in v.groups) for v in character.data.vertices)
assert all(os.path.isfile(os.path.join(OUTBOX,'finale_personaggio_'+v+'.png')) for v in ['fronte','destra','retro','sinistra','tre_quarti','alto'])

now=datetime.datetime.now();start=now.replace(hour=11,minute=18,second=0,microsecond=0)
minutes=(now-start).total_seconds()/60
inbox=os.path.join(os.path.dirname(OUTBOX),'inbox')
steps=[p for p in glob.glob(os.path.join(inbox,'*.py')) if not os.path.basename(p).endswith('_prova.py')]
errors=[]
for p in steps:
    lf=os.path.join(OUTBOX,os.path.splitext(os.path.basename(p))[0]+'.log')
    if os.path.isfile(lf) and open(lf,encoding='utf-8').read().startswith('ERROR'):errors.append(os.path.basename(p))

notes_path=os.path.join(WORK,'NOTE-personaggio.md')
old=open(notes_path,encoding='utf-8').read().split('## Consuntivo')[0]
text=f'''## Consuntivo
Fine: {now.strftime('%d/%m/%Y, ore %H:%M:%S')} (ora locale).
Tempo trascorso: circa {minutes:.0f} minuti, entro la scadenza delle 13:18. L'inizio e stato annotato al minuto.
Esecuzioni del kit per il progetto: {len(steps)} (la prova iniziale e esclusa); {len(errors)} esecuzioni interrotte per errori di script o controllo, poi corrette. Compresi ripristino, diagnostica e verifiche di esportazione.

### Modello consegnato
- Altezza effettiva: {height:.6f} m, suole a quota zero. Unita Blender in metri.
- Posa di riposo A, braccia aperte e inclinate in basso, come fronte e retro del riferimento.
- {tri:,} triangoli reali, tutti espliciti; margine di {40000-tri:,} sul limite di 40.000.
- {len(character.data.vertices):,} vertici nella mesh Blender. Una mesh skinned, {len(character.data.materials)} materiali.
- 53 ossa totali: 50 dello scheletro umano, comprese dita, pollici e root, piu 3 del mantello. Una root di controllo non deformante; 52 ossa deformanti.
- Tutti i vertici hanno pesi; massimo 2 influenze per vertice. Provati gomiti, ginocchio, dita e mantello in posa; poi ripristinata la posa A.
- Corpo vestito, viso, capelli scuri con ciocca chiara, mantello verde con strappi geometrici e usura, colletto, imbracatura, cintura, guanti, quadrante sul bracciale, ginocchiere, stivali con lacci e fibbie.
- Casco in ottone sulla schiena con tre oblo, griglia, rivetti, valvola, tubi corrugati e zaino inferiore. Ai fianchi: corde, borsa, portamappe, cannocchiale e bussola.
- Albedo, normal map e rugosita generate con codice dentro Blender, senza risorse esterne. Texture incorporate nel blend e nel GLB.

### File e verifiche
- `personaggio.blend`: scena modificabile con rig, luci e camera di presentazione. F12 usa la camera inclusa.
- `personaggio.glb`: glTF 2.0 binario, metri, Y up, mesh e scheletro, senza luci/camere o animazioni predefinite; texture incorporate, nessun file esterno necessario.
- GLB reimportato in Blender e controllato: stessi {tri:,} triangoli, 53 ossa, altezza 1,70 m, zero vertici senza peso. Materiali controllati tramite render della sola copia importata.
- `verifica_personaggio.json`: conteggi, altezza, struttura delle ossa e controlli del GLB.
- Sei render finali a 1440 x 1440 in `../outbox/finale_personaggio_*.png`, piu i dettagli di viso e casco. Anche i render intermedi e la prova delle deformazioni sono nella outbox.

### Limiti e differenze dal riferimento
- Interpretazione stilizzata: viso e capelli sono piu semplici e meno realistici del disegno; non e una riproduzione fotorealistica.
- Le pieghe fini, l'invecchiamento e alcuni piccoli ornamenti sono semplificati. Gli accessori sono modellati con geometrie separate all'interno della mesh unita.
- Scheletro FK con pesi, senza IK, rig facciale, blendshape o clip di animazione. Il mantello dispone di ossa per animazione secondaria, senza simulazione fisica.
- Non e stato aperto Unity: verifica di esportazione e reimportazione eseguita in Blender, non prova dell'Avatar Humanoid nell'editor Unity.
- Il difetto apparente visto durante il primo confronto del GLB derivava dalla sovrapposizione di originale e copia importata nel render; risolto isolando la copia importata. Rimosse anche facce di area nulla e triangolata esplicitamente la mesh.

Riferimento unico utilizzato: `riferimenti/1-personaggio.webp`. Nessuna modifica al kit, nessuna installazione, nessun download. Tutti i comandi avvia/passo eseguiti fuori dall'ambiente isolato di Codex, nel Blender visibile dell'utente.
'''
open(notes_path,'w',encoding='utf-8').write(old+text)
report['fine_locale']=now.isoformat(timespec='seconds');report['minuti_trascorsi']=round(minutes,1);report['passi_kit_progetto']=len(steps);report['passi_interrotti']=errors
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
log('CONSEGNA:',tri,'triangoli;',len(rig.data.bones),'ossa;',height,'m;',len(steps),'esecuzioni del kit; fine',now.strftime('%H:%M:%S'))
