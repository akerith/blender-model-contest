exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
import json, struct, time
rig=bpy.data.objects['Personaggio_Rig'];ob=bpy.data.objects['Personaggio_Mesh']
for item in [rig,ob]:
    item.hide_set(False);item.hide_viewport=False;item.hide_render=False
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=ob
options=dict(filepath=os.path.join(BASE,'personaggio.glb'),export_format='GLB',use_selection=True,export_yup=True,export_skins=True,export_animations=False,export_cameras=False,export_lights=False,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_apply=False,export_all_influences=False)
available={p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
missing=[k for k in options if k not in available]
if missing:raise RuntimeError('Opzioni export non supportate: '+str(missing))
bpy.ops.export_scene.gltf(**options)
log('GLB esportato; dimensioni:',ob.dimensions[:])

# Inspect the actual GLB structure, not just the source scene.
data=open(os.path.join(BASE,'personaggio.glb'),'rb').read();magic,version,size=struct.unpack_from('<4sII',data,0)
assert magic==b'glTF' and version==2 and size==len(data)
jn,jt=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+jn]);triangles=0
for mm in doc['meshes']:
    for pr in mm['primitives']:
        assert pr.get('mode',4)==4
        triangles+=doc['accessors'][pr['indices']]['count']//3
        assert 'JOINTS_0' in pr['attributes'] and 'WEIGHTS_0' in pr['attributes']
        assert 'TEXCOORD_0' in pr['attributes'] and 'NORMAL' in pr['attributes']
assert triangles<=40000
assert len(doc['skins'])==1
assert all('uri' not in im for im in doc['images'])
report={'glb_bytes':len(data),'triangles_glb':triangles,'meshes':len(doc['meshes']),'materials':len(doc['materials']),'embedded_images':len(doc['images']),'skin_joints':len(doc['skins'][0]['joints']),'y_up':True,'animations':len(doc.get('animations',[]))}
log('Audit GLB:',report)

# Round-trip import into a temporary collection, render it, then restore the source.
before=set(bpy.data.objects);ob.hide_set(True);ob.hide_render=True;rig.hide_set(True)
bpy.ops.import_scene.gltf(filepath=os.path.join(BASE,'personaggio.glb'))
imported=[o for o in bpy.data.objects if o not in before]
imeshes=[o for o in imported if o.type=='MESH'];iarms=[o for o in imported if o.type=='ARMATURE']
assert len(imeshes)==1 and len(iarms)==1
io=imeshes[0];ia=iarms[0];io.data.calc_loop_triangles()
pts=[io.matrix_world@v.co for v in io.data.vertices];height=max(p.z for p in pts)-min(p.z for p in pts)
assert abs(height-1.7)<.0001
assert len(io.data.loop_triangles)==triangles
assert all(v.groups for v in io.data.vertices)
report.update({'reimport_height_m':height,'reimport_bones':len(ia.data.bones),'reimport_vertices':len(io.data.vertices),'reimport_unweighted_vertices':sum(not v.groups for v in io.data.vertices)})
render_viste('11_glb_reimportato',viste=['tre_quarti','retro'],risoluzione=1200)
# A short independent deformation check on the imported skin.
pb=ia.pose.bones.get('LeftLowerArm')
if pb:
    dg=bpy.context.evaluated_depsgraph_get();rest=[v.co.copy() for v in io.evaluated_get(dg).data.vertices]
    pb.rotation_mode='XYZ';pb.rotation_euler.x=.4;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();posed=[v.co.copy() for v in io.evaluated_get(dg).data.vertices]
    moved=sum((a-b).length>.00001 for a,b in zip(rest,posed));assert moved>0;report['reimport_vertices_moved_by_forearm']=moved
    pb.rotation_euler=(0,0,0)
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
ob.hide_set(False);ob.hide_render=False;rig.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
open(os.path.join(BASE,'verifica_glb.json'),'w').write(json.dumps(report,indent=2))
save();log('Verifica di reimportazione:',report)
