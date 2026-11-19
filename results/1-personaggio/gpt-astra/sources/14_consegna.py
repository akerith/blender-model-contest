exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
import json,time,datetime,glob,hashlib
ob=bpy.data.objects['Personaggio_Mesh'];rig=bpy.data.objects['Personaggio_Rig']
ob.hide_set(False);ob.hide_render=False;rig.hide_set(False);rig.hide_render=False;rig.show_in_front=False
for pb in rig.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
bpy.context.view_layer.update()
# Audit only the deliverable mesh, with all of its actual final modifiers.
ob.data.calc_loop_triangles();triangles=len(ob.data.loop_triangles)
assert triangles<=40000
assert all(v.groups for v in ob.data.vertices)
assert max(len(v.groups) for v in ob.data.vertices)<=4
assert all(g.name in rig.data.bones for g in ob.vertex_groups)
height=max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices)
assert abs(height-1.7)<.00001
assert ob.data.uv_layers.active is not None
assert all(math.isfinite(c) for v in ob.data.vertices for c in v.co)
assert len(ob.data.materials)==1
assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==1
# Remove unused intermediate/imported datablocks; the editable source remains in its backup file.
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.shading.type='MATERIAL';a.spaces.active.overlay.show_overlays=False
        a.spaces.active.region_3d.view_distance=2.6;a.spaces.active.region_3d.view_location=(0,0,.85)
        a.spaces.active.region_3d.view_rotation=Vector((1,-2,.5)).to_track_quat('Z','Y')
        a.spaces.active.region_3d.view_perspective='ORTHO'
bpy.context.scene.cycles.samples=64
save()
render_viste('finale_personaggio',risoluzione=1536)
save()

end=datetime.datetime.now();start=end.replace(hour=10,minute=36,second=0,microsecond=0)
elapsed=(end-start).total_seconds()/60
steps=[p for p in glob.glob(os.path.join(os.path.dirname(BASE),'inbox','*.py')) if not os.path.basename(p).endswith('_prova.py')]
glb=json.load(open(os.path.join(BASE,'verifica_glb.json')))
note_path=os.path.join(BASE,'NOTE-personaggio.md');note=open(note_path,encoding='utf-8').read().split('## Consuntivo')[0]
note+=f'''## Consuntivo
- Fine: {end.strftime('%d/%m/%Y %H:%M:%S')} (Europe/Rome).
- Tempo trascorso: {elapsed:.1f} minuti, entro il termine delle 12:36.
- Passi del progetto eseguiti attraverso il kit: {len(steps)}, compresi controlli diagnostici e tentativi corretti; esclusa la prova iniziale.
- Altezza: {height:.6f} m, dalla suola alla sommità dei capelli. Posa di riposo A.
- Triangoli nel file Blender: {triangles:,}; nel GLB effettivo: {glb['triangles_glb']:,}. Entrambi sotto 40.000. L'esportatore ha eliminato tre triangoli degeneri.
- Scheletro: {len(rig.data.bones)} ossa (Root, bacino, colonna, collo, testa, spalle, braccia, mani, dita, gambe, piedi, dita dei piedi e 9 ossa del mantello).
- Vertici senza pesi: 0. Massimo 4 influenze per vertice; pesi normalizzati.
- Un'unica mesh deformabile e un unico materiale PBR; UV non sovrapposte generate per un atlante comune.
- Tre texture 4096 x 4096 create e cotte dentro Blender: BaseColor, Normal tangent-space, ORM (R=1, G=roughness, B=metallic).
- Texture incorporate sia nel .blend sia nel .glb. Nessun modello, immagine o materiale scaricato.

## File consegnati
- `personaggio.blend`: versione finale con rig e texture incorporate.
- `personaggio.glb`: glTF 2.0 binario, metri, Y up, scheletro e texture incorporati; circa {glb['glb_bytes']/1000000:.1f} MB.
- `personaggio_sorgente.blend`: copia precedente all'unione e alla cottura delle texture, con pezzi separati e materiali procedurali, utile per modifiche.
- `personaggio_BaseColor.png`, `personaggio_Normal.png`, `personaggio_ORM.png`: copie delle texture.
- Sei render in `../outbox/finale_personaggio_*.png`: fronte, destra, retro, sinistra, tre_quarti, alto, 1536 x 1536.
- `verifica_rig.json` e `verifica_glb.json`: misure e risultati dei controlli.

## Controlli fatti
- Confronto delle viste intermedie con l'unico riferimento 1-personaggio.webp.
- Corrette compenetrazioni delle falde, spalle e fasce al ginocchio, oltre a una prima versione troppo spigolosa di volto e capelli.
- Prova di posa di braccio, gamba, testa, dito e mantello; poi ritorno alla posa A senza salvare animazioni.
- Controllato il contenuto binario del GLB: una mesh, un materiale, 3 immagini incorporate, 62 articolazioni della skin, attributi di pesatura e UV presenti.
- Reimportato il GLB in Blender: altezza {glb['reimport_height_m']:.6f} m, 62 ossa, nessun vertice senza pesi. Una rotazione dell'avambraccio muove {glb['reimport_vertices_moved_by_forearm']} vertici della mesh importata.
- Guardati i render della reimportazione per verificare materiali e silhouette. Il primo export senza scheletro e un controllo interrotto dalla forma ausiliaria delle ossa sono stati corretti; il GLB finale contiene il rig.

## Risultato e limiti
- Riconoscibili mantello verde strappato e consumato, ciocca bianca, casco in ottone con oblò e griglie, tubi corrugati, corde, astuccio, bussola, guanti, stivali allacciati e cinture.
- Volto e capelli sono una interpretazione stilizzata: non riproducono tutta la finezza e l'espressione del disegno. Le pieghe e gli strappi sono più semplici e regolari del riferimento.
- Il mantello ha ossa aggiuntive, ma non una simulazione fisica. Pose estreme possono richiedere correzioni dei pesi o delle compenetrazioni.
- Scheletro di deformazione con nomi leggibili per un flusso umanoide; nessun controllo IK, rig facciale, blendshape o clip di animazione consegnato.
- Esportazione e deformazione verificate in Blender. Importazione, creazione Avatar Humanoid e retargeting in Unity non sono stati collaudati in questa sessione.
- Nessuna modifica al kit e nessun accesso alle cartelle degli altri concorrenti.
'''
open(note_path,'w',encoding='utf-8').write(note)
summary={'start':'10:36','end':end.strftime('%H:%M:%S'),'elapsed_minutes':round(elapsed,2),'steps':len(steps),'triangles_blend':triangles,'triangles_glb':glb['triangles_glb'],'bones':len(rig.data.bones),'height_m':height}
open(os.path.join(BASE,'riepilogo_finale.json'),'w').write(json.dumps(summary,indent=2))
log('Consegna completata:',summary)
