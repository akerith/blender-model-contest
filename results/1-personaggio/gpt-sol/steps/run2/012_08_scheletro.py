import os, json
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))

# Tuck the upper neck inside the jaw, removing the exposed corner seen in portrait.
neck=bpy.data.objects['Collo']
for v in neck.data.vertices:
    v.co.x*=.82;v.co.y*=.88

objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('personaggio')]
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
minz=min(v.co.z for o in objects for v in o.data.vertices)
maxz=max(v.co.z for o in objects for v in o.data.vertices)
factor=1.70/(maxz-minz)
for o in objects:
    for v in o.data.vertices:v.co=Vector((v.co.x*factor,v.co.y*factor,(v.co.z-minz)*factor))
    # A neutral color outside the skin avoids black fallback colors on import.
    if not o.data.color_attributes.get('Carnagione'):
        ca=o.data.color_attributes.new(name='Carnagione',type='FLOAT_COLOR',domain='CORNER')
        for d in ca.data:d.color=(1,1,1,1)

def P(p):return Vector((p[0]*factor,p[1]*factor,(p[2]-minz)*factor))
def Z(z):return (z-minz)*factor

# Three cape bones allow secondary motion without tying the hem to the hips.
for o in objects:
    if o.name=='Mantello_strappato' or o.name.startswith('Bordo_mantello_'):
        weight_z(o,[(Z(.16),'cape.03'),(Z(.50),'cape.03'),(Z(.78),'cape.02'),(Z(1.10),'cape.01'),(Z(1.34),'chest')])
    elif o.name.startswith('Sfilaccio_'):
        o.vertex_groups.clear();o.vertex_groups.new(name='cape.03').add(list(range(len(o.data.vertices))),1,'REPLACE')

armdata=bpy.data.armatures.new('Scheletro_umano')
rig=bpy.data.objects.new('Esploratrice_Rig',armdata);bpy.context.collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
bone_info={}
def bone(name,head,tail,parent=None,deform=True):
    b=armdata.edit_bones.new(name);b.head=P(head);b.tail=P(tail);b.use_deform=deform
    if parent:b.parent=armdata.edit_bones[parent]
    b.align_roll(Vector((0,-1,0)));bone_info[name]={'head':list(head),'tail':list(tail),'parent':parent}
    return b

bone('root',(0,0,minz),(0,0,.15),deform=False)
bone('pelvis',(0,.005,.91),(0,.005,1.04),'root')
bone('spine',(0,.005,1.04),(0,.005,1.18),'pelvis')
bone('chest',(0,.005,1.18),(0,.005,1.365),'spine')
bone('neck',(0,.005,1.365),(0,.003,1.49),'chest')
bone('head',(0,.003,1.49),(0,.008,1.685),'neck')
bone('cape.01',(0,.13,1.345),(0,.14,1.03),'chest')
bone('cape.02',(0,.14,1.03),(0,.15,.68),'cape.01')
bone('cape.03',(0,.15,.68),(0,.16,.25),'cape.02')

for s in [-1,1]:
    side='L' if s==1 else 'R'
    shoulder=Vector((s*.169,0,1.365));elbow=Vector((s*.323,-.006,1.195));wrist=Vector((s*.451,-.021,1.065))
    direction=(wrist-elbow).normalized();palm_end=wrist+direction*.070;across=Vector((s*.71,0,.70))
    bone('clavicle.'+side,(s*.015,0,1.351),shoulder,'chest')
    bone('upper_arm.'+side,shoulder,elbow,'clavicle.'+side)
    bone('forearm.'+side,elbow,wrist,'upper_arm.'+side)
    bone('hand.'+side,wrist,palm_end,'forearm.'+side)
    for f in range(4):
        base=palm_end+across*((f-1.5)*.016);length=[.054,.067,.062,.048][f]
        end=base+direction*length+Vector((0,-.004,-.005));points=[base,base.lerp(end,.44),base.lerp(end,.75),end]
        for j in range(3):
            name='finger%d.%02d.%s'%(f,j+1,side)
            parent='hand.'+side if j==0 else 'finger%d.%02d.%s'%(f,j,side)
            bone(name,points[j],points[j+1],parent)
        obj=bpy.data.objects['Dito_'+side+'_'+str(f)];obj.vertex_groups.clear()
        names=['finger%d.%02d.%s'%(f,j+1,side) for j in range(3)]
        for n in names:obj.vertex_groups.new(name=n)
        axis=P(end)-P(base)
        for v in obj.data.vertices:
            t=(v.co-P(base)).dot(axis)/axis.length_squared
            if t<.25:w=[(names[0],1)]
            elif t<.56:
                q=(t-.25)/.31;w=[(names[0],1-q),(names[1],q)]
            elif t<.7:w=[(names[1],1)]
            elif t<.89:
                q=(t-.7)/.19;w=[(names[1],1-q),(names[2],q)]
            else:w=[(names[2],1)]
            for n,q in w:
                if q>0:obj.vertex_groups[n].add([v.index],q,'REPLACE')
    base=wrist+direction*.025-across*.031;end=base+direction*.042-across*.025+Vector((0,-.012,0));mid=base.lerp(end,.5)
    bone('thumb.01.'+side,base,mid,'hand.'+side);bone('thumb.02.'+side,mid,end,'thumb.01.'+side)
    obj=bpy.data.objects['Pollice_'+side];obj.vertex_groups.clear();obj.vertex_groups.new(name='thumb.01.'+side);obj.vertex_groups.new(name='thumb.02.'+side)
    axis=P(end)-P(base)
    for v in obj.data.vertices:
        t=max(0,min(1,((v.co-P(base)).dot(axis)/axis.length_squared-.3)/.5))
        obj.vertex_groups['thumb.01.'+side].add([v.index],1-t,'REPLACE');obj.vertex_groups['thumb.02.'+side].add([v.index],t,'REPLACE')
    bone('thigh.'+side,(s*.085,.012,.94),(s*.116,-.01,.61),'pelvis')
    bone('shin.'+side,(s*.116,-.01,.61),(s*.12,.010,.14),'thigh.'+side)
    bone('foot.'+side,(s*.12,.010,.14),(s*.12,-.11,.065),'shin.'+side)
    bone('toe.'+side,(s*.12,-.11,.065),(s*.12,-.16,.048),'foot.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True;rig.display_type='WIRE';rig.data.display_type='OCTAHEDRAL'
for n in ['Corpo','Dita','Mantello']:
    if not rig.data.collections.get(n):rig.data.collections.new(n)
for b in rig.data.bones:
    c='Mantello' if b.name.startswith('cape') else ('Dita' if b.name.startswith(('finger','thumb')) else 'Corpo')
    rig.data.collections[c].assign(b)

# Join the components into one skinned game mesh, keeping the material islands and weights.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Giacca_corpo']
bpy.ops.object.join();character=bpy.context.object;character.name='Esploratrice_mesh';character.data.name='Esploratrice_topologia'
character.parent=rig
mod=character.modifiers.new('Scheletro_umano','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False

unknown=[];unweighted=[];maxinf=0
for v in character.data.vertices:
    valid=[g for g in v.groups if g.weight>0 and character.vertex_groups[g.group].name in rig.data.bones]
    invalid=[character.vertex_groups[g.group].name for g in v.groups if g.weight>0 and character.vertex_groups[g.group].name not in rig.data.bones]
    unknown.extend(invalid)
    if not valid:unweighted.append(v.index);continue
    valid=sorted(valid,key=lambda g:g.weight,reverse=True)[:4];total=sum(g.weight for g in valid)
    vals=[(character.vertex_groups[g.group],g.weight/total) for g in valid]
    for group in character.vertex_groups:
        try:group.remove([v.index])
        except RuntimeError:pass
    for group,w in vals:group.add([v.index],w,'REPLACE')
    maxinf=max(maxinf,len(valid))
assert not unweighted, 'Vertici non pesati: '+str(unweighted[:20])
assert not unknown, 'Gruppi senza osso: '+str(set(unknown))

character.data.calc_loop_triangles();tri=len(character.data.loop_triangles)
height=max(v.co.z for v in character.data.vertices)-min(v.co.z for v in character.data.vertices)
assert tri<=40000
assert abs(height-1.7)<1e-5
rig['altezza_metri']=height;rig['triangoli']=tri;rig['ossa']=len(rig.data.bones)
rig['nota']='Scheletro FK umano; tre ossa aggiuntive per il mantello. Riposo in posa A.'
metrics={'triangoli':tri,'vertici':len(character.data.vertices),'ossa':len(rig.data.bones),'altezza_metri':height,'vertici_non_pesati':len(unweighted),'max_influenze':maxinf,'materiali':len(character.data.materials),'normalizzazione':{'fattore':factor,'min_z_originale':minz},'ossa_definizione':bone_info}
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(metrics,indent=2))
log('Controllo rig:',tri,'triangoli;',len(rig.data.bones),'ossa; altezza',height,'m; vertici non pesati',len(unweighted),'; influenze massime',maxinf)
save()
render_viste('08_rig_riposo',viste=['fronte','retro'])

# Deliberately bend elbow, knee, fingers and cape, then restore the required A-pose.
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
rig.pose.bones['forearm.L'].rotation_euler.x=-.75
rig.pose.bones['forearm.R'].rotation_euler.x=.45
rig.pose.bones['thigh.R'].rotation_euler.x=.25
rig.pose.bones['shin.R'].rotation_euler.x=-.55
rig.pose.bones['cape.02'].rotation_euler.x=.12
for pb in rig.pose.bones:
    if pb.name.startswith('finger') and pb.name.endswith('.L'):pb.rotation_euler.x=.38
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();ev=character.evaluated_get(deps);emd=ev.to_mesh()
delta=max((emd.vertices[v.index].co-v.co).length for v in character.data.vertices)
ev.to_mesh_clear();log('Prova deformazione: spostamento massimo dei vertici',round(delta,4),'m')
render_viste('08_prova_rig',viste=['fronte','tre_quarti'])
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
bpy.context.view_layer.update();save()
