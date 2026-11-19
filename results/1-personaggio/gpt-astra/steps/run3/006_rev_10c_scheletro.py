exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils import Quaternion
import ast,time
rig=bpy.data.objects['Personaggio_Rig'];rig.hide_set(False);rig.hide_viewport=False;rig.hide_render=False
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
rig.data.pose_position='POSE'
for side,label in [('L','Left'),('R','Right')]:
    for part in ['Shoulder','UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot','Toes']:
        old=rig.data.bones.get(label+part)
        if old:old.name=part+'.'+side
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
eb=rig.data.edit_bones
for b in eb:b.use_connect=False
def place(name,a,b,parent=None):
    bone=eb[name];bone.head=a;bone.tail=b;bone.roll=0
    if parent:bone.parent=eb[parent]
place('Root',(0,0,0),(0,0,.14));eb['Root'].use_deform=False
place('Hips',(0,0,.95),(0,0,1.10),'Root')
place('Spine',(0,0,1.10),(0,0,1.27),'Hips')
place('Chest',(0,0,1.27),(0,0,1.40),'Spine')
place('UpperChest',(0,0,1.40),(0,0,1.45),'Chest')
place('Neck',(0,0,1.45),(0,0,1.50),'UpperChest')
place('Head',(0,0,1.50),(0,0,1.70),'Neck')
finger_data={ast.literal_eval(k):[Vector(p) for p in ps] for k,ps in json.load(open(os.path.join(BASE,'rev_dita.json'))).items()}
finger_bones={}
for s,side,label in [(-1,'R','Right'),(1,'L','Left')]:
    shoulder=Vector((s*.19,0,1.40));elbow=Vector((s*.38,0,1.18));wrist=Vector((s*.54,0,.99));knuckle=wrist+Vector((s*.643,0,-.766))*.076
    place('Shoulder.'+side,(s*.025,0,1.45),shoulder,'UpperChest')
    place('UpperArm.'+side,shoulder,elbow,'Shoulder.'+side)
    place('LowerArm.'+side,elbow,wrist,'UpperArm.'+side)
    place('Hand.'+side,wrist,knuckle,'LowerArm.'+side)
    place('UpperLeg.'+side,(s*.10,0,.90),(s*.115,0,.49),'Hips')
    place('LowerLeg.'+side,(s*.115,0,.49),(s*.13,0,.08),'UpperLeg.'+side)
    place('Foot.'+side,(s*.13,0,.08),(s*.13,-.13,.04),'LowerLeg.'+side)
    place('Toes.'+side,(s*.13,-.13,.04),(s*.13,-.19,.04),'Foot.'+side)
    for k,fname in enumerate(['Index','Middle','Ring','Little','Thumb']):
        ps=finger_data[(side,k)];names=[label+fname+x for x in ['Proximal','Intermediate','Distal']]
        for j in range(3):place(names[j],ps[j],ps[j+1],'Hand.'+side if j==0 else names[j-1])
        finger_bones[('Pollice '+side) if k==4 else ('Dito '+str(k+1)+' '+side)]=(ps,names)
for side,s in [('R',-1),('C',0),('L',1)]:
    pts=[(s*.15,.12,1.35),(s*.28,.17,.95),(s*.39,.19,.60),(s*.48,.21,.25)]
    for j in range(3):place('Cape_'+side+'_'+str(j+1),pts[j],pts[j+1],'UpperChest' if j==0 else 'Cape_'+side+'_'+str(j))
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True

obs=objects()
for ob in obs:
    ob.hide_set(False);strip_armature(ob)
    for vg in list(ob.vertex_groups):ob.vertex_groups.remove(vg)
bpy.ops.object.select_all(action='DESELECT')
for ob in obs:ob.select_set(True)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
automatic_result=''
try:
    automatic_result=str(bpy.ops.object.parent_set(type='ARMATURE_AUTO'))
except Exception as ex:automatic_result=repr(ex)
log('Parent automatic weights:',automatic_result)
auto_unweighted=sum(not any(g.weight>.00001 for g in v.groups) for ob in obs for v in ob.data.vertices)
log('Vertici senza peso dopo automatico',auto_unweighted)

def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def between(t,centers,names):
    if t<=centers[0]:return {names[0]:1.0}
    if t>=centers[-1]:return {names[-1]:1.0}
    for i in range(len(centers)-1):
        if centers[i]<=t<=centers[i+1]:
            w=smooth((t-centers[i])/(centers[i+1]-centers[i]));return {names[i]:1-w,names[i+1]:w}
def fallback(ob,p):
    tag=ob.get('bone','pelvis');side='R' if tag.endswith('R') else 'L'
    if ob.name in finger_bones:
        pts,names=finger_bones[ob.name];d=pts[-1]-pts[0];t=(p-pts[0]).dot(d)/d.length_squared
        return between(t,[.12,.50,.86],names)
    if tag=='TORSO':return between(p.z,[1.08,1.19,1.34,1.43],['Hips','Spine','Chest','UpperChest'])
    if tag.startswith('ARM.'):
        w=smooth((1.225-p.z)/.085);return {'UpperArm.'+side:1-w,'LowerArm.'+side:w}
    if tag.startswith('SHOULDER.'):
        w=smooth((abs(p.x)-.12)/.15);return {'UpperChest':1-w,'UpperArm.'+side:w}
    if tag.startswith('LEG.'):
        w=smooth((.55-p.z)/.11);return {'UpperLeg.'+side:1-w,'LowerLeg.'+side:w}
    if tag=='CAPE':
        out={};spread=.20+.35*clamp((1.4-p.z)/1.2)
        for col,cw in between(p.x/spread,[-.75,0,.75],['R','C','L']).items():
            for name,w in between(p.z,[.35,.70,1.04,1.36],['Cape_'+col+'_3','Cape_'+col+'_2','Cape_'+col+'_1','UpperChest']).items():out[name]=out.get(name,0)+cw*w
        return out
    if tag.startswith('foot.'):
        return between(-p.y,[.10,.16],['Foot.'+side,'Toes.'+side])
    if tag.startswith('shin.'):
        return between(p.z,[.07,.16],['Foot.'+side,'LowerLeg.'+side])
    mapping={'head':'Head','neck':'Neck','chest':'Chest','pelvis':'Hips','spine':'Spine','hand.'+side:'Hand.'+side,'forearm.'+side:'LowerArm.'+side,'clavicle.'+side:'Shoulder.'+side}
    return {mapping.get(tag,'Hips'):1}

# Automatic heat weights are retained for main torso and legs when local and valid.
# Separate garments, fingers and rigid equipment receive corrected local weights.
kept_auto=0;corrected=0
for ob in obs:
    world=ob.matrix_world.copy()
    oldweights=[]
    for v in ob.data.vertices:oldweights.append({ob.vertex_groups[g.group].name:g.weight for g in v.groups if g.group<len(ob.vertex_groups) and g.weight>.00001})
    for vg in list(ob.vertex_groups):ob.vertex_groups.remove(vg)
    groups={}
    for v in ob.data.vertices:
        p=world@v.co;ws=fallback(ob,p)
        if ob.name in ['Corpetto sagomato','Pantalone L','Pantalone R']:
            allowed={'Hips','Spine','Chest','UpperChest'} if ob.name=='Corpetto sagomato' else {'UpperLeg.'+ob.name[-1],'LowerLeg.'+ob.name[-1],'Hips'}
            automatic={n:w for n,w in oldweights[v.index].items() if n in allowed}
            if sum(automatic.values())>.1:ws=automatic;kept_auto+=1
            else:corrected+=1
        else:corrected+=1
        ws=dict(sorted(((n,w) for n,w in ws.items() if w>.00001),key=lambda t:t[1],reverse=True)[:4]);ss=sum(ws.values())
        for name,w in ws.items():
            if name not in groups:groups[name]=ob.vertex_groups.new(name=name)
            groups[name].add([v.index],w/ss,'REPLACE')
    ob.parent=rig;ob.matrix_parent_inverse=rig.matrix_world.inverted();ob.matrix_world=world
    mods=[m for m in ob.modifiers if m.type=='ARMATURE']
    mod=mods[0] if mods else ob.modifiers.new('Deformazione scheletro','ARMATURE');mod.object=rig
    for extra in mods[1:]:ob.modifiers.remove(extra)

unweighted=0;maxinf=0;maxerr=0
for ob in obs:
    for v in ob.data.vertices:
        valid=[g.weight for g in v.groups if g.weight>.000001]
        unweighted+=not valid;maxinf=max(maxinf,len(valid));maxerr=max(maxerr,abs(sum(valid)-1))
required=['Hips','Spine','Chest','Neck','Head']+[p+'.'+s for s in ['L','R'] for p in ['Shoulder','UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot','Toes']]
assert all(n in rig.data.bones for n in required)
assert unweighted==0 and maxinf<=4 and maxerr<.00001
report={'triangles':tri_count(),'bones':len(rig.data.bones),'unweighted_vertices':unweighted,'max_influences':maxinf,'max_weight_error':maxerr,'automatic_parent_result':automatic_result,'unweighted_after_automatic':auto_unweighted,'automatic_weights_retained_vertices':kept_auto,'corrected_vertices':corrected,'required_bones':required}
open(os.path.join(BASE,'verifica_revisione_rig.json'),'w').write(json.dumps(report,indent=2))
bpy.context.view_layer.update();bpy.ops.wm.save_mainfile();log('Rig revisionato',report)
pb=rig.pose.bones['UpperArm.L'];pb.rotation_mode='QUATERNION'
axis=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,-1,0))
pb.rotation_quaternion=Quaternion(axis,math.radians(30));bpy.context.view_layer.update()
render_viste('rev_prova_osso',viste=['fronte','tre_quarti'])
log('UpperArm.L a 30 gradi: posa di prova da verificare, salvataggio su disco resta in riposo')
