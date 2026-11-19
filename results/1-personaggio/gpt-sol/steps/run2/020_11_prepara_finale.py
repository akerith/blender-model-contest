import os,bmesh,json
from mathutils import Euler
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']

# The last portrait showed the added curls were too regular; keep the earlier,
# shorter swept silhouette, together with the improved eyelid opening.
bm=bmesh.new();bm.from_mesh(character.data);seen=set();remove=[]
for start in bm.verts:
    if start in seen:continue
    group=[];stack=[start];seen.add(start)
    while stack:
        v=stack.pop();group.append(v)
        for e in v.link_edges:
            q=e.other_vert(v)
            if q not in seen:seen.add(q);stack.append(q)
    materials={character.data.materials[f.material_index].name for v in group for f in v.link_faces}
    if len(group)==104 and materials=={'07_Capelli_carbone'}:
        remove.extend(group)
log('Rimossi i ricci aggiuntivi troppo regolari:',len(remove),'vertici')
if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
bm.normal_update();bm.to_mesh(character.data);bm.free();character.data.update()
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
bpy.context.view_layer.update()

character.data.calc_loop_triangles();tri=len(character.data.loop_triangles)
assert tri<=40000
assert all(any(g.weight>0 for g in v.groups) for v in character.data.vertices)
rig['triangoli']=tri
report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'));report['triangoli']=tri;report['vertici']=len(character.data.vertices)
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))

# A permanent presentation camera makes F12 work in the delivered .blend as well.
sc=bpy.context.scene
if not bpy.data.objects.get('Presentazione'):
    cd=bpy.data.cameras.new('Presentazione');cd.type='ORTHO';cd.ortho_scale=2.10
    cam=bpy.data.objects.new('Presentazione',cd);sc.collection.objects.link(cam)
else:cam=bpy.data.objects['Presentazione']
cam.location=(2.6,-4.1,2.5);cam.rotation_euler=(Vector((0,0,.87))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
sc.render.resolution_x=sc.render.resolution_y=1440;sc.render.resolution_percentage=100
sc.cycles.samples=64;sc.cycles.use_denoising=True
sc.render.filepath=os.path.join(OUTBOX,'presentazione_personaggio.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.shading.use_scene_lights=False;space.shading.use_scene_world=False
            space.overlay.show_overlays=False;space.region_3d.view_location=(0,0,.86);space.region_3d.view_distance=2.65
            space.region_3d.view_rotation=Euler((math.radians(76),0,math.radians(19)),'XYZ').to_quaternion();space.region_3d.view_perspective='ORTHO'
bpy.ops.object.select_all(action='DESELECT');character.select_set(True);bpy.context.view_layer.objects.active=character
bpy.data.orphans_purge(do_recursive=True)
save()
render_viste('11_controllo_finale',viste=['fronte','tre_quarti'],risoluzione=1200)
