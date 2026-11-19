exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
from mathutils.noise import noise
M=materials();green=M['Mantello | verde salvia'];seam=M['Mantello | cuciture'];thread=M['Filo | canapa'];leather=M['Cuoio | bruno'];dark=M['Cuciture e suole'];brass=M['Ottone antico'];ivory=M['Strumenti | quadrante']

# Replace flat shoulder pieces with cloth curved over the actual shoulder volume.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('Mantellina spalla','Bordo spalla','Piega spalla','Piega mantellina')):bpy.data.objects.remove(ob,do_unlink=True)
for s,side in [(-1,'R'),(1,'L')]:
    pts=[Vector((s*.075,0,1.385)),Vector((s*.124,0,1.36)),Vector((s*.17,0,1.325)),Vector((s*.207,0,1.289))]
    rad=[.049,.078,.078,.069];vv=[];ff=[];N=18
    for i,c in enumerate(pts):
        tang=(pts[min(i+1,3)]-pts[max(i-1,0)]).normalized();u=tang.cross(Vector((0,1,0))).normalized()
        if u.z<0:u=-u
        v=Vector((0,1,0))
        for j in range(N+1):
            a=-pi*.54+pi*1.08*j/N;p=c+rad[i]*(cos(a)*u+sin(a)*v)
            if i==3:p.z+=.004*sin(j*1.9)
            vv.append(tuple(p))
    for i in range(3):
        for j in range(N):a=i*(N+1)+j;ff.append((a,a+1,a+N+2,a+N+1))
    ob=mesh('Mantellina curva '+side,vv,ff,green,'SHOULDER.'+side)
    mod=ob.modifiers.new('Fodera mantellina','SOLIDIFY');mod.thickness=.0025;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    path('Orlo mantellina '+side,vv[-(N+1):],.0018,seam,'SHOULDER.'+side,6)
    # Add folds along the cloth surface, slightly irregular and discontinuous.
    for j in [4,9,14]:
        pp=[tuple(Vector(vv[i*(N+1)+j])+Vector((0,-.001,.001))) for i in range(1,4)]
        path('Cresta mantellina '+side+str(j),pp,.0013,seam,'SHOULDER.'+side,5)

# Cover the rear gap at the cape's neck, with a curved shoulder-to-shoulder yoke.
vv=[];N=24
for k in range(3):
    for j in range(N+1):
        x=-.175+.35*j/N;t=k/2
        vv.append((x,.065+.05*t+.014*cos(x*16),1.391-.062*t-.018*abs(x)/.175))
ff=[]
for k in range(2):
    for j in range(N):a=k*(N+1)+j;ff.append((a,a+1,a+N+2,a+N+1))
mesh('Sprone dorsale mantello',vv,ff,green,'chest')

# Knee wraps now clear all folds of the trouser mesh.
for ob in bpy.data.objects:
    if ob.name.startswith('Fascia ginocchio'):
        s=-1 if ' R' in ob.name else 1
        for v in ob.data.vertices:
            v.co.x=s*.093+(v.co.x-s*.093)*1.17
            v.co.y=.005+(v.co.y-.005)*1.18

# A worn bone clasp on the shoulder, as in the reference.
uv('Fermaglio osso cranio',(.117,-.077,1.384),(.014,.008,.017),ivory,'clavicle.L',14,10)
for s in [-1,1]:
    uv('Cavita fermaglio '+str(s),(.117+s*.005,-.084,1.386),(.0035,.0018,.004),dark,'clavicle.L',10,6)
box('Fermaglio mascella',(.117,-.079,1.368),(.016,.01,.008),ivory,'clavicle.L',.002)
for k in range(3):path('Dente fermaglio '+str(k),[(.112+k*.005,-.085,1.37),(.112+k*.005,-.085,1.365)],.0007,dark,'clavicle.L',4)
path('Legaccio fermaglio',[(.103,-.078,1.394),(.132,-.077,1.4),(.139,-.074,1.38)],.0023,thread,'clavicle.L',6)

# Additional weathered cape damage is laid on the actual surface, not on a flat plane.
cape=bpy.data.objects['Mantello lungo strappato']
def back_y(x,z):
    # nearest weighted surface interpolation, restricted to visible rear vertices
    near=sorted([( (v.co.x-x)**2+(v.co.z-z)**2,v.co.y) for v in cape.data.vertices],key=lambda a:a[0])[:4]
    ww=[1/max(.000001,d) for d,y in near]
    return sum(w*p[1] for w,p in zip(ww,near))/sum(ww)+.002
random.seed(35)
for k in range(14):
    x=random.uniform(-.23,.23);z=random.uniform(.44,1.13);pp=[]
    for j in range(5):
        xx=x+(j-2)*.008+random.uniform(-.003,.003);zz=z+j*.009+random.uniform(-.004,.004)
        pp.append((xx,back_y(xx,zz),zz))
    path('Abrasion mantello %02d'%k,pp,.0009 if k%2 else .0014,seam,'CAPE',4)
    if k in [2,7,11]:
        for j in range(3):
            x1,y1,z1=pp[j+1]
            path('Rammendo %d %d'%(k,j),[(x1-.004,y1+.0007,z1+.002),(x1+.004,y1+.0007,z1-.004)],.0008,thread,'CAPE',4)

# Populate the same pigment layer on new pieces so they use the established shaders.
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.get('character') or ob.data.color_attributes.get('Pigmento'):continue
    attr=ob.data.color_attributes.new(name='Pigmento',type='FLOAT_COLOR',domain='CORNER')
    for poly in ob.data.polygons:
        m=ob.data.materials[poly.material_index];base=Vector(m.get('base_pigment',m.diffuse_color[:3]))
        for li in poly.loop_indices:
            p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;c=base*(.9+.17*noise(p*34))
            attr.data[li].color=(*c,1)

save();log('Correzioni controllate; triangoli:',tri_count())
render_viste('06_correzioni',viste=['fronte','retro'])
# Dedicated close-up of the head, still made with the kit's fixed-view renderer.
hidden=[]
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and ob.get('bone')!='head':
        hidden.append((ob,ob.hide_get(),ob.hide_render));ob.hide_set(True);ob.hide_render=True
render_viste('06_dettaglio_volto',viste=['fronte','tre_quarti'],risoluzione=1000)
for ob,h,r in hidden:ob.hide_set(h);ob.hide_render=r
save()
