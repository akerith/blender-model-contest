exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
M=materials();green=M['Mantello | verde salvia'];vest=M['Corpetto | petrolio scuro'];shirt=M['Lino | avorio sporco'];leather=M['Cuoio | bruno'];edge=M['Cuoio | bordi'];dark=M['Cuciture e suole'];brass=M['Ottone antico']
thread=mat('Filo | canapa',(.34,.29,.19),rough=.95)
seam=mat('Mantello | cuciture',(.15,.235,.19),rough=.98)
clothlight=mat('Tessuto | usura',(.24,.255,.205),rough=.96)

# Broad torn cape, folded in cross-section and split in several places at the hem.
random.seed(42);cols=44;rows=16
hem=[]
for j in range(cols+1):
    u=j/cols*2-1
    z=.23+.09*abs(u)+.027*sin(j*2.5)+random.uniform(-.035,.035)
    if j in (5,6,18,19,31,39):z+=.11
    hem.append(z)

def cape_point(u,t):
    jj=max(0,min(cols,int((u+1)*cols/2)))
    width=.184+.078*t+.015*sin(t*pi)
    x=width*sin(u*pi/2)+.008*sin(t*5+u*8)*t
    y=.018+.104*cos(u*pi/2)+t*.045+.012*sin(u*6*pi+t*2)*(t+.2)
    z=1.37*(1-t)+hem[jj]*t
    return (x,y,z)
vv=[cape_point(j/cols*2-1,i/rows) for i in range(rows+1) for j in range(cols+1)]
ff=[]
holes={(13,9),(14,9),(14,10),(12,36),(13,36),(15,24),(14,3)}
for i in range(rows):
    for j in range(cols):
        if (i,j) in holes:continue
        a=i*(cols+1)+j;ff.append((a,a+1,a+cols+2,a+cols+1))
cape=mesh('Mantello lungo strappato',vv,ff,green,'CAPE')
cape.data.materials.append(clothlight)
# The pale eroded edge has a deliberately irregular boundary.
for p in cape.data.polygons:
    c=p.center
    # polygon.center is updated below; use vertex coordinates directly.
    center=sum((cape.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    if center.z < .31+.065*sin(center.x*44)+.055*sin(center.x*91):p.material_index=1
mod=cape.modifiers.new('Tessuto doppia faccia','SOLIDIFY');mod.thickness=.0018
bpy.context.view_layer.objects.active=cape;bpy.ops.object.modifier_apply(modifier=mod.name)
# Cape shoulder yoke, shaped around the neck and across the sleeve roots.
for s,side in [(-1,'R'),(1,'L')]:
    vv=[(s*.045,-.032,1.408),(s*.10,-.067,1.413),(s*.17,-.067,1.369),(s*.217,-.048,1.318),(s*.24,-.025,1.277),(s*.178,-.079,1.295),(s*.12,-.097,1.32),(s*.075,-.074,1.355),
        (s*.10,.047,1.412),(s*.18,.06,1.36),(s*.23,.046,1.288)]
    ff=[(0,1,7),(1,2,6,7),(2,3,5,6),(3,4,5),(0,8,9,2,1),(2,9,10,4,3)]
    ob=mesh('Mantellina spalla '+side,vv,ff,green,'clavicle.'+side)
    mod=ob.modifiers.new('Orlo','SOLIDIFY');mod.thickness=.003;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    path('Bordo spalla '+side,[vv[i] for i in [7,6,5,4]],.0024,seam,'clavicle.'+side,6)
    path('Piega spalla '+side,[(s*.085,-.076,1.374),(s*.14,-.085,1.348),(s*.19,-.067,1.325)],.0018,seam,'clavicle.'+side,6)

# High, open collar. An irregular rim is much closer to the reference than a torus.
N=22;vv=[]
for i in range(3):
    for j in range(N+1):
        a=-2.35+4.7*j/N;t=i/2
        vv.append(((.055+.039*t)*sin(a),(.047+.025*t)*cos(a),1.391+.065*t+.009*cos(a)))
ff=[]
for i in range(2):
    for j in range(N):a=i*(N+1)+j;ff.append((a,a+1,a+N+2,a+N+1))
ob=mesh('Collo alto verde',vv,ff,green,'chest');mod=ob.modifiers.new('Fodera','SOLIDIFY');mod.thickness=.003;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
path('Bordo colletto',vv[2*(N+1):],.0025,seam,'chest',6)
# Wrinkled scarf in the open front of the collar.
for k in range(4):
    pts=[(-.043,-.038,1.438-k*.012),(-.023,-.054,1.425-k*.012),(0,-.06,1.419-k*.012),(.023,-.054,1.427-k*.012),(.043,-.035,1.441-k*.012)]
    ribbon('Fazzoletto piega %d'%k,pts,.014,shirt,'neck')

# Split jacket skirts remove the blocky pelvis silhouette.
for s,side in [(-1,'R'),(1,'L')]:
    vv=[(s*.008,-.087,.985),(s*.112,-.072,.981),(s*.148,-.063,.833),(s*.106,-.091,.792),(s*.018,-.102,.817),(s*.014,-.096,.91),(s*.12,-.091,.901)]
    ob=mesh('Falda giacca '+side,vv,[(0,1,6,5),(5,6,2,3,4)],vest,'pelvis')
    mod=ob.modifiers.new('Spessore','SOLIDIFY');mod.thickness=.003;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    path('Profilo falda '+side,[vv[i] for i in [0,5,4,3,2]],.002,edge,'pelvis',6)
    # Shaped vertical seams make the vest read as tailored panels.
    path('Cucitura corpetto '+side,[(s*.055,-.077,1.1),(s*.065,-.089,1.2),(s*.082,-.083,1.29),(s*.093,-.064,1.35)],.0016,edge,'TORSO',6)

# Belt as an actual elliptical band, with central rectangular buckle and tongue.
def belt(name,z,rx,ry,width,material,bone='pelvis'):
    return rings(name,[(z-width/2,0,0,rx,ry),(z+width/2,0,0,rx,ry)],material,bone,40)
belt('Cinturone',1.035,.119,.086,.045,leather)
belt('Bordo cintura superiore',1.057,.12,.087,.003,edge)
belt('Bordo cintura inferiore',1.013,.121,.087,.003,edge)
def buckle(name,center,w,h,bone):
    x,y,z=center
    path(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2),(x-w/2,y,z-h/2)],.003,brass,bone,6)
    path(name+' ardiglione',[(x,y-.001,z-h/2),(x,y-.002,z+h*.2)],.0018,brass,bone,6)
buckle('Fibbia cintura',(0,-.094,1.035),.046,.035,'pelvis')
box('Lingua cintura',(.047,-.091,1.035),(.046,.006,.03),edge,'pelvis',.002)
for k in range(3):uv('Foro cintura %d'%k,(.034+k*.012,-.095,1.035),(.0015,.0007,.0016),dark,'pelvis',8,6)

# Crossed shoulder harness, with separate rear straps beneath the helmet.
for s,side in [(-1,'R'),(1,'L')]:
    points=[(s*.112,.064,1.36),(s*.12,.015,1.387),(s*.108,-.065,1.364),(s*.068,-.095,1.29),(s*.018,-.101,1.207),(-s*.07,-.083,1.112),(-s*.088,-.071,1.065)]
    ribbon('Bretella incrociata '+side,points,.024,leather,'TORSO',.003)
    path('Cucitura bretella '+side,[(x+s*.008,y-.002,z) for x,y,z in points[2:]],.0009,thread,'TORSO',5)
    buckle('Fibbia pettorale '+side,(s*.069,-.104,1.29),.027,.031,'chest')
    ribbon('Bretella dorsale '+side,[(s*.112,.071,1.36),(s*.097,.091,1.25),(s*.07,.091,1.11)],.024,leather,'TORSO')

# Loose lower belt, leather pouches, rivets and buttons.
ribbon('Cintura obliqua',[(-.132,-.05,.98),(-.085,-.09,.967),(0,-.103,.948),(.09,-.09,.927),(.145,-.025,.93)],.025,edge,'pelvis')
for s,side in [(-1,'R'),(1,'L')]:
    x=s*.135
    box('Tasca cintura '+side,(x,-.052,.957),(.063,.047,.074),leather,'pelvis',.009)
    box('Patella tasca '+side,(x,-.079,.979),(.067,.01,.032),edge,'pelvis',.006)
    uv('Bottone tasca '+side,(x,-.086,.974),(.004,.0018,.004),brass,'pelvis',10,6)
    # Bands, boot lacing, shin seams and toe seam.
    for z in [.385,.346,.15]:
        ob=rings('Cinghia stivale '+side+str(z),[(z-.012,s*.093,.012,.062 if z>.3 else .048,.053 if z>.3 else .048),(z+.012,s*.093,.012,.062 if z>.3 else .048,.053 if z>.3 else .048)],edge,'shin.'+side,24)
        buckle('Fibbia stivale '+side+str(z),(s*.126,-.034,z),.016,.018,'shin.'+side)
    path('Cucitura stivale '+side,[(s*.093-.029,-.031,.12),(s*.093-.033,-.035,.23),(s*.093-.036,-.037,.32)],.0013,thread,'shin.'+side,5)
    path('Cucitura stivale esterna '+side,[(s*.093+.029,-.031,.12),(s*.093+.033,-.035,.23),(s*.093+.036,-.037,.32)],.0013,thread,'shin.'+side,5)
    for k in range(7):
        z=.18+k*.021;cy=-.032-(z-.18)*.035
        path('Laccio X a '+side+str(k),[(s*.093-.019,cy,z),(s*.093+.019,cy-.004,z+.018)],.0016,edge,'shin.'+side,5)
        path('Laccio X b '+side+str(k),[(s*.093+.019,cy,z),(s*.093-.019,cy-.004,z+.018)],.0016,edge,'shin.'+side,5)
    path('Cucitura punta '+side,[(s*.093-.047,-.108,.061),(s*.093-.029,-.119,.077),(s*.093,-.122,.08),(s*.093+.029,-.119,.077),(s*.093+.047,-.108,.061)],.0014,edge,'foot.'+side,6)
    # Sleeve seams and wrinkles crossing the arm axis.
    for k in range(4):
        cx=s*(.246+k*.018);zz=1.266-k*.021
        path('Piega manica '+side+str(k),[(cx-s*.021,-.029,zz-.018),(cx,-.048,zz),(cx+s*.021,-.031,zz+.019)],.0035,shirt,'ARM.'+side,7)
    for k in range(3):
        c=Vector((s*(.365+.035*k),0,1.13-.031*k));d=Vector((s*.75,0,-.66))
        tube('Cinghia guanto '+side+str(k),[c-d*.008,c+d*.008],[.046-.007*k,.046-.007*k],edge,'forearm.'+side,16)
    for k in range(3):
        path('Nocca guanto '+side+str(k),[(s*(.50+k*.01),-.024,1.015-k*.009),(s*(.521+k*.01),-.025,.997-k*.009)],.0015,edge,'hand.'+side,5)

# Asymmetric knee armour and cloth wraps.
uv('Ginocchiera cuoio destra',(-.093,-.05,.532),(.057,.024,.07),leather,'shin.R',20,12)
for j in range(10):
    a=2*pi*j/10
    uv('Rivetto ginocchiera %d'%j,(-.093+.047*cos(a),-.065,.532+.055*sin(a)),(.0025,.002,.0025),brass,'shin.R',8,6)
for s,side in [(-1,'R'),(1,'L')]:
    for k in range(3):
        rings('Fascia ginocchio '+side+str(k),[(.433+k*.015,s*.093,.005,.062,.055),(.445+k*.015,s*.093,.005,.063,.055)],shirt,'shin.'+side,24)
save();log('Abiti, mantello e finiture; triangoli:',tri_count())
render_viste('03_abiti',viste=['fronte','retro','tre_quarti'])
