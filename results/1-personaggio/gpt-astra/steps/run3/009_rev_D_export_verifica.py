exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
import struct
from mathutils import Quaternion
rig=bpy.data.objects['Personaggio_Rig'];obs=objects()
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
points=[p for o in obs for p in coords(o)]
height=max(p.z for p in points)-min(p.z for p in points)
assert abs(height-1.70)<.002,(height,min(p.z for p in points),max(p.z for p in points))
assert tri_count()<=40000
bpy.ops.object.select_all(action='DESELECT')
for ob in obs:ob.hide_set(False);ob.hide_render=False;ob.select_set(True)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_mainfile()
options=dict(filepath=os.path.join(BASE,'personaggio.glb'),export_format='GLB',use_selection=True,export_yup=True,export_skins=True,export_animations=False,export_cameras=False,export_lights=False,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_apply=False,export_all_influences=False)
available={p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
assert all(k in available for k in options)
bpy.ops.export_scene.gltf(**options)
data=open(os.path.join(BASE,'personaggio.glb'),'rb').read();magic,version,size=struct.unpack_from('<4sII',data,0)
assert magic==b'glTF' and version==2 and size==len(data)
jn,jt=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+jn]);triangles=0;primitives=0
for mm in doc['meshes']:
    for pr in mm['primitives']:
        assert pr.get('mode',4)==4
        triangles+=doc['accessors'][pr['indices']]['count']//3;primitives+=1
        assert 'JOINTS_0' in pr['attributes'] and 'WEIGHTS_0' in pr['attributes']
        assert 'NORMAL' in pr['attributes']
assert triangles<=40000 and triangles==tri_count(),(triangles,tri_count())
assert len(doc['skins'])==1
assert all('bufferView' in im and 'uri' not in im for im in doc.get('images',[]))
report={'glb_bytes':len(data),'triangles_glb':triangles,'triangles_blend':tri_count(),'height_m':height,'bones_blend':len(rig.data.bones),'skin_joints':len(doc['skins'][0]['joints']),'meshes':len(doc['meshes']),'primitives':primitives,'materials':len(doc['materials']),'embedded_images':len(doc.get('images',[])),'y_up_export':True,'all_primitives_skinned':True}
log('Audit binario GLB',report)
open(os.path.join(BASE,'verifica_revisione_glb.json'),'w').write(json.dumps(report,indent=2))

# Import the exported file for an independent visual and skin check.
before=set(bpy.data.objects)
for ob in obs:ob.hide_set(True);ob.hide_render=True
rig.hide_set(True)
bpy.ops.import_scene.gltf(filepath=os.path.join(BASE,'personaggio.glb'),disable_bone_shape=True)
imported=[o for o in bpy.data.objects if o not in before]
imeshes=[o for o in imported if o.type=='MESH'];iarms=[o for o in imported if o.type=='ARMATURE']
assert len(iarms)==1
ia=iarms[0];ipoints=[o.matrix_world@v.co for o in imeshes for v in o.data.vertices]
ih=max(p.z for p in ipoints)-min(p.z for p in ipoints)
itri=sum(sum(len(p.vertices)-2 for p in ob.data.polygons) for ob in imeshes)
assert abs(ih-1.70)<.002 and itri==triangles
assert all(any(g.weight>0 for g in v.groups) for ob in imeshes for v in ob.data.vertices)
render_viste('rev_glb_reimportato',viste=['fronte','retro','tre_quarti'],risoluzione=1100)
hand=next(o for o in imeshes if o.name.startswith('Palmo guanto L'))
dg=bpy.context.evaluated_depsgraph_get();before_pose=[v.co.copy() for v in hand.evaluated_get(dg).data.vertices]
pb=ia.pose.bones['UpperArm.L'];pb.rotation_mode='QUATERNION';axis=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,-1,0));pb.rotation_quaternion=Quaternion(axis,math.radians(30));bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();after_pose=[v.co.copy() for v in hand.evaluated_get(dg).data.vertices]
moved=sum((a-b).length>.001 for a,b in zip(before_pose,after_pose));assert moved>0
pb.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
report.update({'reimport_height_m':ih,'reimport_triangles':itri,'reimport_bones':len(ia.data.bones),'reimport_meshes':len(imeshes),'reimport_unweighted_vertices':0,'reimport_hand_vertices_moved':moved})
open(os.path.join(BASE,'verifica_revisione_glb.json'),'w').write(json.dumps(report,indent=2))
log('Reimportazione verificata',report)
for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
for ob in obs:ob.hide_set(False);ob.hide_render=False
rig.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_mainfile()
