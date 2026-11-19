exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
from mathutils.noise import noise
import json
M=materials();skin=M['Pelle | ocra desaturata'];hair=M['Capelli | nero caldo']

# Final close-up correction: shallow eyelids blended into the actual head surface.
head=bpy.data.objects['Testa anatomica']
for v in head.data.vertices:
    x,y,z=v.co
    if y<0:v.co.y-=.0025*math.exp(-((abs(x)-.028)/.018)**2-((z-1.555)/.012)**2)*max(0,min(1,-y*18))
tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
def surface(x,z):
    hit=tree.ray_cast(Vector((x,-.25,z)),Vector((0,1,0)))
    return hit[0].y if hit[0] is not None else -.04
for s in [-1,1]:
    for name in ['Occhio ','Ciglia fini ']:
        ob=bpy.data.objects[name+str(s)]
        for v in ob.data.vertices:v.co.y+=.005
    for name in ['Iride ','Pupilla ','Punto luce ']:bpy.data.objects[name+str(s)].location.y+=.005
    ob=bpy.data.objects['Palpebre integrate '+str(s)];N=32;R=4;cx=s*.028;z0=1.556
    for i in range(R+1):
        t=i/R
        for j in range(N):
            a=2*pi*j/N;xi=cx+.014*cos(a);zi=z0+(.0053 if sin(a)>0 else .0036)*sin(a)+s*.001*cos(a)
            xo=cx+.019*cos(a);zo=z0+.009*sin(a)+s*.001*cos(a)
            x=xi*(1-t)+xo*t;z=zi*(1-t)+zo*t
            base=surface(x,z);inner=-.055-.003*abs(sin(a));delta=(surface(xi,zi)-inner)
            y=base-delta*(1-t)**2+.0004*t
            ob.data.vertices[i*N+j].co=(x,y,z)
    old=bpy.data.objects.get('Sopracciglio definitivo '+str(s))
    if old:bpy.data.objects.remove(old,do_unlink=True)
    vv=[]
    for j in range(13):
        t=j/12;x=s*(.011+.035*t);z=1.569+.003*sin(pi*t)-.002*t
        w=.0016*sin(pi*(t*.85+.08))+.0002
        for dz in [-w,w]:vv.append((x,surface(x,z+dz)-.0007,z+dz))
    mesh('Sopracciglio aderente '+str(s),vv,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(12)],hair,'head')

# Bury blunt hair roots in the scalp, and lower their shine.
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name.startswith(('Capelli frangia','Capelli ciocca','Capelli lato','Capelli tempia','Capelli nuca')):
        for i in range(3):
            vs=list(ob.data.vertices)[i*6:(i+1)*6];center=sum((v.co for v in vs),Vector())/6
            normal=Vector((center.x/.076**2,(center.y-.01)/.074**2,(center.z-1.58)/.103**2)).normalized()
            for v in vs:v.co=center+(v.co-center)*[.08,.5,.85][i]-normal*[.006,.003,.0005][i]
for name in ['Capelli | nero caldo','Capelli | riflessi','Ciocca bianca','Ciocca bianca | luce']:
    m=M[name];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.7

# Pigment for the new brow strips.
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.get('character') or ob.data.color_attributes.get('Pigmento'):continue
    attr=ob.data.color_attributes.new(name='Pigmento',type='FLOAT_COLOR',domain='CORNER')
    for poly in ob.data.polygons:
        m=ob.data.materials[poly.material_index];base=m.get('base_pigment',m.diffuse_color[:3])
        for li in poly.loop_indices:attr.data[li].color=(*base,1)

# Normalize all mesh coordinates to metres and exactly 1.70 m, sole to hair.
objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('character')]
points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
zmin=min(p.z for p in points);zmax=max(p.z for p in points);fac=1.7/(zmax-zmin)
for ob in objects:
    matworld=ob.matrix_world.copy()
    for v in ob.data.vertices:
        p=matworld@v.co;v.co=(p.x*fac,p.y*fac,(p.z-zmin)*fac)
    ob.matrix_world=Matrix.Identity(4)
bpy.context.scene['scale_geometry']=fac;bpy.context.scene['original_zmin']=zmin
def P(p):return Vector((p[0]*fac,p[1]*fac,(p[2]-zmin)*fac))

# Human rig with clear Unity humanoid names, individual fingers and cape chains.
bpy.ops.object.select_all(action='DESELECT')
armdata=bpy.data.armatures.new('Scheletro umano');rig=bpy.data.objects.new('Personaggio_Rig',armdata);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,a,b,parent=None,connected=False):
    eb=armdata.edit_bones.new(name);eb.head=P(a);eb.tail=P(b)
    if parent:eb.parent=armdata.edit_bones[parent];eb.use_connect=connected
    eb.roll=0
    return eb
bone('Root',(0,0,0),(0,0,.14))
bone('Hips',(0,0,.87),(0,0,1.02),'Root')
bone('Spine',(0,0,1.02),(0,0,1.17),'Hips',True)
bone('Chest',(0,0,1.17),(0,0,1.29),'Spine',True)
bone('UpperChest',(0,0,1.29),(0,0,1.395),'Chest',True)
bone('Neck',(0,0,1.395),(0,0,1.472),'UpperChest',True)
bone('Head',(0,0,1.472),(0,0,1.65),'Neck',True)
mapping={'pelvis':'Hips','spine':'Spine','chest':'UpperChest','neck':'Neck','head':'Head'}
finger_paths={}
for s,side,label in [(-1,'R','Right'),(1,'L','Left')]:
    bone(label+'Shoulder',(s*.025,0,1.36),(s*.17,0,1.347),'UpperChest')
    bone(label+'UpperArm',(s*.17,0,1.347),(s*.336,0,1.157),label+'Shoulder',True)
    bone(label+'LowerArm',(s*.336,0,1.157),(s*.48,0,1.025),label+'UpperArm',True)
    bone(label+'Hand',(s*.48,0,1.025),(s*.535,0,.978),label+'LowerArm',True)
    bone(label+'UpperLeg',(s*.093,0,.87),(s*.093,0,.526),'Hips')
    bone(label+'LowerLeg',(s*.093,0,.526),(s*.093,.012,.11),label+'UpperLeg',True)
    bone(label+'Foot',(s*.093,.012,.11),(s*.093,-.105,.044),label+'LowerLeg',True)
    bone(label+'Toes',(s*.093,-.105,.044),(s*.093,-.153,.044),label+'Foot',True)
    for a,b in [('clavicle','Shoulder'),('upper_arm','UpperArm'),('forearm','LowerArm'),('hand','Hand'),('thigh','UpperLeg'),('shin','LowerLeg'),('foot','Foot')]:mapping[a+'.'+side]=label+b
    axis=Vector((s*.71,0,-.70));cross=Vector((s*.70,0,.71));center=Vector((s*.53,-.001,.979))
    for k,fname in enumerate(['Little','Ring','Middle','Index']):
        start=center+cross*((k-1.5)*.013);length=[.037,.047,.045,.035][k];end=start+axis*length+Vector((0,-.005,0))
        pp=[start,start.lerp(end,.36),start.lerp(end,.69),end]
        names=[label+fname+x for x in ['Proximal','Intermediate','Distal']]
        for j in range(3):bone(names[j],pp[j],pp[j+1],label+'Hand' if j==0 else names[j-1],j>0)
        finger_paths['Dito %d %s'%(k+1,side)]=(P(start),P(end),names)
    pp=[(s*.487,-.006,1.008),(s*.481,-.016,.987),(s*.485,-.022,.974),(s*.49,-.024,.962)]
    names=[label+'Thumb'+x for x in ['Proximal','Intermediate','Distal']]
    for j in range(3):bone(names[j],pp[j],pp[j+1],label+'Hand' if j==0 else names[j-1],j>0)
    finger_paths['Pollice '+side]=(P(pp[0]),P(pp[-1]),names)
for col,x in [('R',-.17),('C',0),('L',.17)]:
    pp=[(x,.128,1.31),(x*1.16,.143,.95),(x*1.3,.158,.61),(x*1.42,.173,.25)]
    for j in range(3):bone('Cape_'+col+'_'+str(j+1),pp[j],pp[j+1],'UpperChest' if j==0 else 'Cape_'+col+'_'+str(j),j>0)
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True;armdata.display_type='OCTAHEDRAL'

def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def between(z,centers,names):
    if z<=centers[0]:return {names[0]:1}
    if z>=centers[-1]:return {names[-1]:1}
    for i in range(len(centers)-1):
        if centers[i]<=z<=centers[i+1]:
            t=smooth((z-centers[i])/(centers[i+1]-centers[i]));return {names[i]:1-t,names[i+1]:t}
def weights(ob,p):
    tag=ob.get('bone','pelvis');z=p.z/fac+zmin;x=p.x/fac
    if ob.name in finger_paths:
        a,b,names=finger_paths[ob.name];t=(p-a).dot(b-a)/(b-a).length_squared
        return between(t,[.13,.51,.86],names)
    if tag=='TORSO':return between(z,[1.015,1.13,1.25,1.35],['Hips','Spine','Chest','UpperChest'])
    if tag.startswith('ARM.'):
        label='Left' if tag.endswith('L') else 'Right';w=smooth((1.205-z)/.095)
        return {label+'UpperArm':1-w,label+'LowerArm':w}
    if tag.startswith('SHOULDER.'):
        label='Left' if tag.endswith('L') else 'Right';w=smooth((abs(x)-.105)/.13)
        return {label+'Shoulder':1-w,label+'UpperArm':w}
    if tag.startswith('LEG.'):
        label='Left' if tag.endswith('L') else 'Right';w=smooth((.595-z)/.12)
        return {label+'UpperLeg':1-w,label+'LowerLeg':w}
    if tag=='CAPE':
        cols=between(x,[-.17,0,.17],['R','C','L']);out={}
        for col,cw in cols.items():
            ww=between(z,[.36,.72,1.06,1.35],['Cape_'+col+'_3','Cape_'+col+'_2','Cape_'+col+'_1','UpperChest'])
            for key,w in ww.items():out[key]=out.get(key,0)+cw*w
        return out
    if tag.startswith('foot.'):
        label='Left' if tag.endswith('L') else 'Right';w=smooth((z-.095)/.055)
        return {label+'Foot':1-w,label+'LowerLeg':w}
    if tag.startswith('shin.') and ob.name.startswith('Gambale'):
        label='Left' if tag.endswith('L') else 'Right';w=smooth((z-.07)/.09)
        return {label+'Foot':1-w,label+'LowerLeg':w}
    return {mapping.get(tag,'Hips'):1}

for ob in objects:
    for vg in list(ob.vertex_groups):ob.vertex_groups.remove(vg)
    groups={}
    for v in ob.data.vertices:
        ws={k:w for k,w in weights(ob,v.co).items() if w>.0001};ss=sum(ws.values())
        for name,w in ws.items():
            if name not in groups:groups[name]=ob.vertex_groups.new(name=name)
            groups[name].add([v.index],w/ss,'REPLACE')
    ob.parent=rig;mod=ob.modifiers.new('Deformazione scheletro','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False

# Audit before any pose is tried.
unweighted=0;maxinf=0;maxerr=0
for ob in objects:
    for v in ob.data.vertices:
        if not v.groups:unweighted+=1
        maxinf=max(maxinf,len(v.groups));maxerr=max(maxerr,abs(sum(g.weight for g in v.groups)-1))
report={'height_m':1.7,'triangles':tri_count(),'bones':len(armdata.bones),'unweighted_vertices':unweighted,'max_influences':maxinf,'max_weight_sum_error':maxerr}
open(os.path.join(BASE,'verifica_rig.json'),'w').write(json.dumps(report,indent=2))
log('Controllo rig:',report)
save()

# Test deformation without committing an animation or changing the reference rest pose.
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
rig.pose.bones['LeftLowerArm'].rotation_euler.x=.65
rig.pose.bones['RightUpperArm'].rotation_euler.z=-.24
rig.pose.bones['LeftLowerLeg'].rotation_euler.x=.3
rig.pose.bones['Head'].rotation_euler.z=.14
rig.pose.bones['LeftIndexProximal'].rotation_euler.x=.3
rig.pose.bones['Cape_L_2'].rotation_euler.x=.12
bpy.context.view_layer.update()
render_viste('08_test_rig',viste=['fronte','tre_quarti'])
for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
bpy.context.view_layer.update();save()
render_viste('08_riposo',viste=['fronte'])
