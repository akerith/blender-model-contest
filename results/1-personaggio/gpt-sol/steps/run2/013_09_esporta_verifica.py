import os,json,struct
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');character.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig

path=os.path.join(WORK,'personaggio.glb')
options=dict(filepath=path,export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_skins=True,export_all_influences=False,export_def_bones=False,export_animations=False,export_morph=False,export_normals=True,export_tangents=True,export_materials='EXPORT',export_image_format='AUTO',export_cameras=False,export_lights=False,export_vertex_color='MATERIAL',export_extras=False)
props={p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
options={k:v for k,v in options.items() if k in props}
log('Opzioni esportazione:',options)
bpy.ops.export_scene.gltf(**options)

raw=open(path,'rb').read();magic,version,total=struct.unpack_from('<III',raw,0)
assert magic==0x46546c67 and version==2 and total==len(raw)
length,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+length].decode('utf-8'))
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert tri<=40000
assert len(doc.get('skins',[]))==1
assert len(doc['skins'][0]['joints'])==53
assert all('uri' not in b for b in doc.get('buffers',[]))
assert all('bufferView' in i for i in doc.get('images',[]))
assert all('JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes'] for m in doc['meshes'] for p in m['primitives'])
log('GLB:',len(raw),'byte;',tri,'triangoli;',len(doc['skins'][0]['joints']),'joints;',len(doc.get('images',[])),'immagini incorporate; nessuna dipendenza esterna.')

before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=path)
imported=[o for o in bpy.data.objects if o not in before]
meshes=[o for o in imported if o.type=='MESH'];arms=[o for o in imported if o.type=='ARMATURE']
assert meshes and len(arms)==1
imp_tri=0;coords=[];unweighted=0
for o in meshes:
    o.data.calc_loop_triangles();imp_tri+=len(o.data.loop_triangles)
    coords.extend(o.matrix_world@v.co for v in o.data.vertices)
    unweighted+=sum(1 for v in o.data.vertices if not any(g.weight>0 for g in v.groups))
height=max(p.z for p in coords)-min(p.z for p in coords)
assert imp_tri==tri
assert abs(height-1.7)<1e-4
assert unweighted==0
assert len(arms[0].data.bones)==53
log('Reimportazione:',imp_tri,'triangoli; altezza',height,'m;',len(arms[0].data.bones),'ossa; vertici non pesati',unweighted)
character.hide_set(True);rig.hide_set(True)
render_viste('09_glb_controllo',viste=['fronte','tre_quarti'])
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
character.hide_set(False);rig.hide_set(False)

report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'))
report['glb']={'byte':len(raw),'triangoli':tri,'joints':len(doc['skins'][0]['joints']),'texture_incorporate':len(doc.get('images',[])),'reimportato':True,'altezza_reimportata':height,'vertici_non_pesati_reimportati':unweighted,'dipendenze_esterne':False}
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
save()
