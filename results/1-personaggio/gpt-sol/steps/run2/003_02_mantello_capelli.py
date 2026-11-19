import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
M={k:bpy.data.materials[n] for k,n in [('skin','01_Pelle'),('lip','02_Labbra'),('shadow','03_Ombra_calda'),('eye','04_Avorio_occhi'),('iris','05_Iride_nocciola'),('black','06_Pupilla'),('hair','07_Capelli_carbone'),('hairlight','08_Ciocca_argento'),('coat','09_Tessuto_giacca'),('cape','10_Mantello_verde'),('capeEdge','11_Tessuto_consumato'),('shirt','12_Tessuto_maniche'),('pants','13_Tessuto_pantaloni'),('leather','14_Cuoio_bruno'),('leatheredge','15_Cuoio_bordi'),('darkleather','16_Cuoio_scuro'),('brass','17_Ottone_antico'),('brassedge','18_Ottone_lucido'),('iron','19_Ferro'),('rope','20_Canapa'),('glass','21_Oblo_verde'),('stitch','22_Filo'),('sole','23_Suola')]}

# Corrections from the first renders: prevent sleeves and trousers piercing outer clothes.
for o in list(bpy.context.scene.objects):
    if o.name.startswith('Guanto_avambraccio'):
        center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
        for v in o.data.vertices:v.co=center+(v.co-center)*1.12
    if o.name.startswith('Falda_giacca'):
        for v in o.data.vertices:v.co.y-=.018
    if o.name.startswith(('Occhio_','Iride_','Pupilla_','Riflesso_occhio_','Palpebra_','Ciglia_')):
        # Narrower eyes, set deeper within the head.
        if o.location.length>.1:
            o.location.y+=.003
            for v in o.data.vertices:v.co.z*=.78
        else:
            for v in o.data.vertices:
                v.co.y+=.003;v.co.z=1.592+(v.co.z-1.592)*.78
    if o.name.startswith('Sopracciglio'):
        for v in o.data.vertices:v.co.z=1.611+(v.co.z-1.611)*.7

# Fuse flesh pieces into a continuous, rounded head rather than intersecting shapes.
parts=[o for o in bpy.context.scene.objects if o.name=='Viso' or o.name=='Naso' or o.name.startswith(('Ala_naso_','Orecchio_'))]
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Viso'];bpy.ops.object.join();head=bpy.context.object
import bmesh
bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(head.data);bm.free()
rem=head.modifiers.new('Unione_anatomica','REMESH');rem.mode='VOXEL';rem.voxel_size=.0018;rem.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=rem.name)
sm=head.modifiers.new('Raccordo_lineamenti','SMOOTH');sm.factor=.8;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
head.data.calc_loop_triangles();ratio=min(1,4200/len(head.data.loop_triangles))
de=head.modifiers.new('Topologia_viso','DECIMATE');de.ratio=ratio;bpy.ops.object.modifier_apply(modifier=de.name)
head.vertex_groups.clear();head.vertex_groups.new(name='head').add(list(range(len(head.data.vertices))),1,'REPLACE')
if not head.data.uv_layers:
    head.data.uv_layers.new(name='UVMap')

# Short, tousled scalp, with an open forehead and low nape.
N=40;R=10;verts=[];uv=[]
for i in range(R+1):
    v=i/R
    for j in range(N):
        t=2*pi*j/N
        edge=1.595+.041*cos(t) if cos(t)>0 else 1.563+.032*cos(t)
        polar=v*pi/2
        z=1.708-(1.708-edge)*(1-cos(polar))
        x=.081*sin(polar)*sin(t);y=.012-.071*sin(polar)*cos(t)
        verts.append((x,y,z));uv.append((j/N,v))
faces=[]
for i in range(R):
    for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
mesh('Capelli_calotta',verts,faces,'hair','head',uv)

def lock(name,points,widths,mat='hair'):
    return loft(name,[(tuple(p),max(.001,w*.36),w) for p,w in zip(points,widths)],mat,'head',sides=8,axis='PATH')

# Irregular swept locks: distinct silhouette, asymmetrical parting and pale forelock.
rng=random.Random(41)
for j in range(20):
    t=2*pi*j/20
    x=.047*sin(t);y=.014-.046*cos(t)
    edge=1.595+.041*cos(t) if cos(t)>0 else 1.563+.032*cos(t)
    points=[(x*.55,y*.6,1.700),(x,y,1.685),(.077*sin(t+.10),.014-.071*cos(t+.1),1.64),(.085*sin(t+.19),.015-.078*cos(t+.19),edge+.005),(.088*sin(t+.35),.016-.080*cos(t+.35),edge-.017-rng.random()*.012)]
    lock('Meche_perimetro_%02d'%j,points,[.006,.013,.015,.010,.0008])
for j in range(8):
    d=j*.006
    pts=[(.025+d*.5,-.012,1.704-j*.001),(.006+d*.7,-.052,1.696-j*.001),(-.026+d*.5,-.075,1.677-j*.002),(-.055+d*.45,-.079,1.651-j*.003),(-.067+d*.4,-.064,1.622-j*.002)]
    lock('Vague_frange_%02d'%j,pts,[.007,.012,.014,.010,.001],'hairlight' if j in [1,2] else 'hair')
for j in range(5):
    pts=[(.028+j*.006,-.012,1.706),(.058+j*.004,-.028,1.687),(.077+j*.002,-.031,1.659),(.078+j*.003,-.015,1.624),(.091+j*.002,.004,1.614)]
    lock('Meche_droite_%02d'%j,pts,[.006,.013,.014,.01,.0007])
# Fine sculpted streaks on prominent locks.
for j in range(6):
    d=j*.007
    tube('Stria_capelli_%02d'%j,[(.027+d*.5,-.022,1.710),(.005+d*.6,-.059,1.698),(-.026+d*.5,-.081,1.674),(-.053+d*.5,-.085,1.646)],.00075,'hairlight' if j==1 else 'leatheredge','head',5)

# Raised collar in separate left/right folded panels, padded neck scarf.
loft('Foulard_collo',[((0,0,1.401),.048,.043),((0,-.002,1.433),.047,.041),((0,0,1.456),.043,.037)],'shirt','neck',sides=24)
for j in range(3):
    tube('Piega_foulard_'+str(j),[(-.034,-.029,1.444-j*.008),(0,-.043,1.43-j*.008),(.034,-.028,1.445-j*.008)],.003,'capeEdge','neck',7)
for s in [-1,1]:
    collar=mesh('Colletto_rialzato_'+str(s),[(s*.027,-.044,1.403),(s*.096,-.048,1.386),(s*.105,.012,1.426),(s*.068,.044,1.468),(s*.035,-.031,1.453)],[(0,1,2,3,4)],'cape','chest')
    mod=collar.modifiers.new('Spessore','SOLIDIFY');mod.thickness=.005;bpy.context.view_layer.objects.active=collar;bpy.ops.object.modifier_apply(modifier=mod.name)
    tube('Bordo_colletto_'+str(s),[(s*.027,-.047,1.403),(s*.035,-.034,1.453),(s*.068,.041,1.468),(s*.105,.009,1.426)],.002,'capeEdge','chest',6)

# Cape has real open tears, a serrated outline and irregular folds, UV-painted wear.
nc=49;nr=20;verts=[];uv=[]
rng=random.Random(9)
hems=[]
for j in range(nc):
    base=.245+.028*cos(j*.8)+rng.uniform(-.045,.045)
    if j in [2,9,15,22,30,39,45]:base-=.060
    if j in [5,12,19,28,35,42]:base+=.09
    hems.append(base)
for i in range(nr):
    v=i/(nr-1)
    for j in range(nc):
        u=j/(nc-1);t=-2.20+u*4.40
        rx=.179+.075*v+.010*sin(v*pi)
        ry=.087+.027*v
        fold=(.006+.011*v)*sin(t*8+v*.8)+.005*sin(t*15-v*3)
        x=(rx+fold)*sin(t)
        y=.021+(ry+fold)*cos(t)+.016*v
        z=(1-v)*(1.381-.040*abs(sin(t)))+v*hems[j]
        verts.append((x,y,z));uv.append((u,1-v))
faces=[]
for i in range(nr-1):
    for j in range(nc-1):
        if i>=nr-4 and (i,j) in {(16,4),(17,4),(17,13),(18,13),(16,20),(17,32),(17,33),(18,40),(16,44)}:continue
        faces.append((i*nc+j,i*nc+j+1,(i+1)*nc+j+1,(i+1)*nc+j))
cape=mesh('Mantello_strappato',verts,faces,'cape',uv=uv)
weight_z(cape,[(.2,'pelvis'),(.93,'pelvis'),(1.12,'spine'),(1.32,'chest')])
# Blender and glTF both display its inside.
M['cape'].use_backface_culling=False

# Dedicated albedo with broad abrasions, woven grain, stains and hairline scratches.
n=1024;yy,xx=np.mgrid[0:n,0:n];u=xx/(n-1);v=yy/(n-1);rngnp=np.random.default_rng(15)
cloud=np.zeros((n,n))
for k in range(1,14):cloud+=np.sin(u*k*9+rngnp.random()*6)*np.cos(v*k*6+rngnp.random()*6)/(k*2)
noise=rngnp.random((n,n));fade=np.clip((.27-v)/.24,0,1)*.65
wear=np.zeros((n,n))
for k in range(38):
    cx=rngnp.random();cy=rngnp.random()*.55
    wx=rngnp.uniform(.008,.045);wy=rngnp.uniform(.015,.12)
    wear+=np.exp(-((u-cx)/wx)**2-((v-cy)/wy)**2)*rngnp.uniform(.2,.8)
wear=np.clip(wear*.7+fade,0,.83)
rgba=np.ones((n,n,4),np.float32)
for c,(base,faded) in enumerate(zip((.065,.135,.112),(.28,.286,.219))):
    rgba[:,:,c]=np.clip(base*(.82+.13*noise+.15*cloud)*(1-wear)+faded*wear,0,1)
# Sparse scratches follow wandering hand-drawn lines.
for k in range(40):
    startx=rngnp.uniform(.05,.95);starty=rngnp.uniform(.05,.7)
    for q in range(rngnp.integers(18,90)):
        px=int((startx+q*.0004+.003*sin(q*.13))*n);py=int((starty+q*.0009)*n)
        if 1<px<n-2 and 1<py<n-2:rgba[py:py+2,px:px+2,:3]=(.24,.28,.226)
im=bpy.data.images.new('Mantello_usura_dipinta',width=n,height=n);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=os.path.join(TEX,'mantello_usura.png');im.file_format='PNG';im.save();im.pack()
M['cape'].node_tree.nodes['Usura generata'].image=im
# Frayed threads on silhouette and holes: sparse, thin and asymmetric.
for j in range(1,nc-1,2):
    p=Vector(verts[(nr-1)*nc+j]);tube('Sfilaccio_%02d'%j,[tuple(p),tuple(p+Vector((.003*sin(j),.001,-.012-.008*(j%3))))],.0008,'capeEdge','pelvis',4)
for j in [0,nc-1]:
    tube('Bordo_mantello_'+str(j),[verts[i*nc+j] for i in range(nr)],.0015,'capeEdge','chest',5)

# Short capelets hide shoulder joins and drape across upper arms.
for s in [-1,1]:
    vs=[(s*.055,-.059,1.407),(s*.129,-.087,1.378),(s*.196,-.054,1.352),(s*.227,-.026,1.292),(s*.162,-.066,1.313),(s*.113,-.093,1.343)]
    o=mesh('Mantellina_spalla_'+str(s),vs,[(0,1,5),(1,2,4,5),(2,3,4)],'cape','chest')
    so=o.modifiers.new('Spessore','SOLIDIFY');so.thickness=.004;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=so.name)
    tube('Orlo_mantellina_'+str(s),[vs[0],vs[1],vs[2],vs[3],vs[4],vs[5]],.002,'capeEdge','chest',6)

save()
render_viste('02_mantello',viste=['fronte','retro','tre_quarti'])
portrait('02_viso',scale=.36,center=(0,0,1.57),loc=(.13,-1.5,1.62))
