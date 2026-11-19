exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
M=materials();skin=M['Pelle | ocra desaturata'];leather=M['Cuoio | bruno'];dark=M['Cuciture e suole']
lip=mat('Labbra | terra rosa',(.30,.16,.125),rough=.73)
shadow=mat('Occhi | ombra calda',(.075,.045,.032),rough=.8)
white=mat('Occhi | avorio',(.50,.48,.40),rough=.35)
iris=mat('Occhi | nocciola verde',(.10,.15,.10),rough=.3)
pupil=mat('Pupille',(.008,.011,.009),rough=.22)
hair=mat('Capelli | nero caldo',(.025,.022,.019),rough=.52)
hair2=mat('Capelli | riflessi',(.055,.047,.036),rough=.57)
silver=mat('Ciocca bianca',(.47,.46,.42),rough=.61)
silver2=mat('Ciocca bianca | luce',(.65,.63,.55),rough=.57)

# Replace the provisional feet with a continuous toe/vamp shape.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('Piede stivale','Punta stivale','Dito ','Pollice')):bpy.data.objects.remove(ob,do_unlink=True)
for s,side in [(-1,'R'),(1,'L')]:
    x=s*.093;vv=[];ff=[];n=20
    for y,w,h,z in [(-.153,.029,.017,.042),(-.14,.047,.025,.047),(-.115,.052,.03,.05),(-.073,.053,.041,.061),(-.025,.049,.061,.077),(.02,.045,.063,.08),(.06,.04,.045,.065)]:
        for j in range(n):
            a=2*pi*j/n;vv.append((x+w*cos(a),y,max(.028,z+h*sin(a))))
    for i in range(6):
        for j in range(n):a=i*n+j;b=i*n+(j+1)%n;ff.append((a,b,b+n,a+n))
    ff.extend([tuple(reversed(range(n))),tuple(6*n+j for j in range(n))])
    mesh('Stivale piede continuo '+side,vv,ff,leather,'foot.'+side)
    # Four fingers emerge side-by-side across the palm, rather than along it.
    axis=Vector((s*.71,0,-.70));cross=Vector((s*.70,0,.71));center=Vector((s*.53,-.001,.979))
    for k in range(4):
        start=center+cross*((k-1.5)*.013)
        length=[.037,.047,.045,.035][k]
        mid=start+axis*length*.55+Vector((0,-.002,0));end=start+axis*length+Vector((0,-.005,0))
        tube('Dito %d %s'%(k+1,side),[start,mid,end],[.0075,.0068,.0045],leather,'hand.'+side,8)
    tube('Pollice '+side,[(s*.49,-.009,1.005),(s*.481,-.02,.98),(s*.49,-.024,.962)],[.011,.009,.0055],leather,'hand.'+side,8)

# Sculpt-like offsets to the base head: cheek planes, eye sockets, chin and muzzle.
head=bpy.data.objects['Testa']
for v in head.data.vertices:
    x,y,z=v.co
    if y<.003:
        front=max(0,min(1,(-y+.003)/.05))
        cheek=.007*math.exp(-((abs(x)-.042)/.025)**2-((z-1.527)/.022)**2)
        socket=.004*math.exp(-((abs(x)-.029)/.017)**2-((z-1.559)/.012)**2)
        muzzle=.008*math.exp(-(x/.025)**2-((z-1.495)/.022)**2)
        v.co.y+=front*(socket-cheek-muzzle)
for s in [-1,1]:
    # Ear with recessed concha and raised helix.
    uv('Orecchio '+str(s),(s*.068,.002,1.538),(.012,.013,.023),skin,'head',16,10)
    uv('Conca orecchio '+str(s),(s*.075,-.009,1.539),(.005,.003,.013),lip,'head',12,8)
    pts=[(s*(.07+.007*sin(t)), -.007-.003*sin(t),1.539+.018*cos(t)) for t in [2*pi*i/20 for i in range(21)]]
    path('Elice orecchio '+str(s),pts,.0023,skin,'head',6)
    # Almond-shaped eye surface, pointed corners and low visible sclera.
    cx=s*.028;z0=1.556
    verts=[(cx,-.064,z0)];N=24
    for j in range(N):
        a=2*pi*j/N;xx=.014*cos(a);zz=(.0055 if sin(a)>0 else .004)*sin(a)
        verts.append((cx+xx,-.0595-.0025*abs(sin(a)),z0+zz+s*.001*cos(a)))
    mesh('Occhio '+str(s),verts,[(0,j+1,(j+1)%N+1) for j in range(N)],white,'head')
    uv('Iride '+str(s),(cx,-.0642,z0),(.0045,.0016,.0047),iris,'head',16,10)
    uv('Pupilla '+str(s),(cx,-.0657,z0),(.0022,.0007,.0027),pupil,'head',12,8)
    uv('Punto luce '+str(s),(cx-.001,-.0662,z0+.0016),(.0007,.0004,.0008),white,'head',8,6)
    upper=[];lower=[]
    for j in range(13):
        a=pi*j/12
        upper.append((cx+.014*cos(a),-.060-.003*sin(a),z0+.0055*sin(a)+s*.001*cos(a)))
        lower.append((cx+.014*cos(a),-.060-.003*sin(a),z0-.004*sin(a)+s*.001*cos(a)))
    path('Palpebra superiore '+str(s),upper,.0019,skin,'head',6)
    path('Ciglia '+str(s),[(x,y-.0013,z-.0005) for x,y,z in upper],.0007,shadow,'head',5)
    path('Palpebra inferiore '+str(s),lower,.0014,skin,'head',6)
    path('Sopracciglio '+str(s),[(s*.012,-.061,1.57),(s*.024,-.064,1.574),(s*.036,-.059,1.573),(s*.045,-.051,1.567)], [.0028,.0032,.0023,.0006] if False else .0024,hair,'head',7)

# Nose bridge and tip, with narrow alae and recessed nostrils.
rings('Naso scolpito',[(1.518,0,-.07,.009,.008),(1.522,0,-.077,.011,.012),(1.528,0,-.081,.009,.014),(1.536,0,-.073,.007,.012),(1.55,0,-.065,.006,.009),(1.568,0,-.059,.004,.004)],skin,'head',16)
for s in [-1,1]:
    uv('Ala naso '+str(s),(s*.009,-.073,1.521),(.0055,.006,.004),skin,'head',12,8)
    uv('Narice '+str(s),(s*.008,-.078,1.518),(.0025,.0014,.0014),shadow,'head',10,6)
path('Filtro naso',[(-.003,-.070,1.515),(-.003,-.071,1.505)],.0012,skin,'head',6)
path('Filtro naso 2',[(.003,-.070,1.515),(.003,-.071,1.505)],.0012,skin,'head',6)
# Lips are fine curved strips with a cupid bow; a closed neutral expression.
xs=[-.018,-.013,-.007,0,.007,.013,.018]
upper=[1.497,1.500,1.503,1.5015,1.503,1.500,1.497]
lower=[1.497,1.4935,1.492,1.4915,1.492,1.4935,1.497]
vv=[]
for x,z in zip(xs,upper):vv.extend([(x,-.068+abs(x)*.2,z),(x,-.072+abs(x)*.2,1.497)])
mesh('Labbro superiore',vv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(6)],lip,'head')
vv=[]
for x,z in zip(xs,lower):vv.extend([(x,-.072+abs(x)*.2,1.497),(x,-.068+abs(x)*.2,z)])
mesh('Labbro inferiore',vv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(6)],lip,'head')
path('Rima labiale',[(x,-.0725+abs(x)*.2,1.497) for x in xs],.00065,shadow,'head',5)

# Hair cap with a high forehead, lower sideburns and a cropped nape.
vv=[];ff=[];N=40;R=12
for i in range(R+1):
    t=i/R
    for j in range(N):
        a=2*pi*j/N; front=max(0,-sin(a)); bottom=1.496+.109*front
        phi=t*math.acos((bottom-1.583)/.099)
        vv.append((.076*sin(phi)*cos(a),.011+.073*sin(phi)*sin(a),1.583+.099*cos(phi)))
for i in range(R):
    for j in range(N):a=i*N+j;b=i*N+(j+1)%N;ff.append((a,b,b+N,a+N))
mesh('Calotta capelli',vv,ff,hair,'head')

def lock(name,points,width,material):
    # Flattened tapered lock, ridge across its centre.
    radii=[(width*(sin(pi*(i+.35)/(len(points)+.2))**.7),width*.28*(1-i/(len(points)+.15))) for i in range(len(points))]
    radii[-1]=(.0005,.0005)
    return tube(name,points,radii,material,'head',8)

random.seed(18)
# Forehead locks sweep from the pale part towards the left temple.
for k in range(10):
    off=(k-4.5)*.006
    pts=[(.023+off,.008,1.675),(.008+off,-.036,1.682),(-.025+off,-.062,1.662),(-.049+off,-.059,1.628),(-.057+off,-.05,1.598),(-.067+off,-.035,1.58+(k%3)*.008)]
    lock('Ciuffo frontale %02d'%k,pts,.011+(k%3)*.002,hair if k%3 else hair2)
    if k%2==0:path('Incisione ciuffo %02d'%k,[(x,y-.002,z+.003) for x,y,z in pts[:-1]],.0009,hair2,'head',5)
# The characteristic white streak curls from the part over the forehead.
for k in range(4):
    off=(k-1.5)*.004
    pts=[(.025+off,-.018,1.682),(.034+off,-.042,1.675),(.025+off,-.064,1.659),(.014+off,-.073,1.646),(.014+off,-.075,1.627),(.024+off,-.071,1.614)]
    lock('Ciocca argento %02d'%k,pts,.006,silver if k%2 else silver2)
# Wisps along each side and the back; asymmetrical tips, not a helmet silhouette.
for s in [-1,1]:
    for k in range(9):
        a=-.75+k*.28
        pts=[]
        for j in range(6):
            t=j/5;ang=a+.5*t
            pts.append((s*(.05+.027*sin(t*pi*.8))*cos(ang),.012+(.065+.012*sin(pi*t))*sin(ang),1.663-.15*t-(k%3)*.012*t))
        lock('Meche laterale %s %02d'%(s,k),pts,.013,hair if k%3 else hair2)
    for k in range(4):
        lock('Basetta %s %02d'%(s,k),[(s*.062,-.026+k*.009,1.605),(s*.078,-.027+k*.01,1.574),(s*.075,-.019+k*.012,1.543),(s*(.079+k*.002),-.009+k*.013,1.521+(k%2)*.01)],.009,hair)
save();log('Volto e capelli; triangoli:',tri_count())
render_viste('02_volto',viste=['fronte','tre_quarti'])
