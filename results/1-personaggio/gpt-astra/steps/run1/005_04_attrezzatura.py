exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
M=materials();brass=M['Ottone antico'];leather=M['Cuoio | bruno'];edge=M['Cuoio | bordi'];green=M['Mantello | verde salvia'];dark=M['Cuciture e suole'];thread=M['Filo | canapa']
bronze=mat('Ottone | incavi',(.15,.09,.035),metal=.75,rough=.5)
patina=mat('Ottone | ossido verde',(.065,.135,.115),metal=.5,rough=.65)
glass=mat('Oblo | vetro verde scuro',(.035,.085,.072),metal=.45,rough=.21)
rope=mat('Corda | canapa scura',(.23,.18,.11),rough=.95)
ivory=mat('Strumenti | quadrante',(.43,.40,.28),rough=.6)

# Correct intersections found in the previous views.
for ob in bpy.data.objects:
    if ob.name.startswith('Falda giacca'):
        for v in ob.data.vertices:v.co.y-=.025
    if ob.name.startswith('Profilo falda'):
        for v in ob.data.vertices:v.co.y-=.025
    if ob.name.startswith('Manica '):
        side=-1 if ob.name.endswith('R') else 1
        for i,v in enumerate(ob.data.vertices):
            if i<20:
                center=Vector((side*.145,0,1.35));v.co=center+(v.co-center)*.65;v.co.x-=side*.014;v.co.z-=.012
    if ob.name.startswith('Mantellina spalla'):
        for v in ob.data.vertices:
            v.co.z+=.016;v.co.y-=.009
    if ob.name.startswith(('Bordo spalla','Piega spalla')):
        for v in ob.data.vertices:v.co.z+=.016;v.co.y-=.009

# Diving helmet carried on the back: an ovoid copper-brass shell, not a backpack box.
uv('Casco palombaro | calotta',(0,.167,1.307),(.116,.102,.14),brass,'chest',32,20)
# Vertical reinforcement bands run over the shell.
for s in [-1,1]:
    pts=[]
    for j in range(17):
        a=-1.4+2.8*j/16
        pts.append((s*.074,.168+.078*cos(a),1.307+.124*sin(a)))
    path('Casco nervatura '+str(s),pts,.006,bronze,'chest',8)
    # Shoulder lugs holding the helmet to the harness.
    box('Attacco casco '+str(s),(s*.092,.123,1.416),(.031,.032,.037),bronze,'chest',.003)
    torus('Anello attacco '+str(s),(s*.094,.133,1.425),.012,.003,brass,'chest',seg=16,sides=6)

# Rear viewing port with raised bronze flange, black gasket and gridded green glass.
cylinder('Flangia oblo',(0,.245,1.319),(0,.272,1.319),.074,bronze,'chest',32)
cylinder('Vetro oblo',(0,.271,1.319),(0,.278,1.319),.060,glass,'chest',32)
torus('Oblo guarnizione',(0,.28,1.319),.062,.003,dark,'chest',seg=32,sides=6)
torus('Oblo bordo esterno',(0,.276,1.319),.071,.005,brass,'chest',seg=32,sides=8)
torus('Oblo bordo interno',(0,.282,1.319),.059,.0035,brass,'chest',seg=32,sides=6)
for x in [-.022,.022]:
    h=math.sqrt(.057**2-x*x)
    cylinder('Barra verticale oblo '+str(x),(x,.284,1.319-h),(x,.284,1.319+h),.0026,bronze,'chest',8)
cylinder('Barra orizzontale oblo',(-.059,.284,1.319),(.059,.284,1.319),.0028,brass,'chest',8)
for j in range(10):
    a=2*pi*j/10
    cylinder('Bullone oblo %02d'%j,(.071*cos(a),.279,1.319+.071*sin(a)),(.071*cos(a),.286,1.319+.071*sin(a)),.0034,brass,'chest',6)
    path('Taglio vite oblo %02d'%j,[(.071*cos(a)-.002,.2865,1.319+.071*sin(a)),(.071*cos(a)+.002,.2865,1.319+.071*sin(a))],.00045,bronze,'chest',4)
# Side ports and hinges are visible in profile.
for s in [-1,1]:
    cylinder('Oblo laterale base '+str(s),(s*.1,.167,1.306),(s*.119,.167,1.306),.042,bronze,'chest',24)
    cylinder('Oblo laterale vetro '+str(s),(s*.12,.167,1.306),(s*.122,.167,1.306),.032,glass,'chest',24)
    torus('Oblo laterale bordo '+str(s),(s*.123,.167,1.306),.035,.004,brass,'chest',rot=(0,pi/2,0),seg=24,sides=6)
    cylinder('Griglia laterale '+str(s),(s*.125,.137,1.306),(s*.125,.197,1.306),.0025,brass,'chest',8)
    cylinder('Griglia laterale verticale '+str(s),(s*.125,.167,1.276),(s*.125,.167,1.336),.0025,brass,'chest',8)
    box('Cerniera oblo '+str(s),(s*.085,.251,1.319),(.018,.014,.033),brass,'chest',.002)

# Neck flange at the bottom, valve and corrugated breathing hoses.
ob=torus('Collare casco',(0,.164,1.197),.071,.009,bronze,'chest',rot=(0,0,0),seg=28,sides=8);ob.scale.y=.78
cylinder('Valvola casco',(0,.252,1.212),(0,.278,1.212),.018,bronze,'chest',16)
torus('Volantino valvola',(0,.284,1.212),.017,.003,brass,'chest',seg=20,sides=6)
for a in [0,2*pi/3,4*pi/3]:
    path('Raggio valvola '+str(a),[(0,.284,1.212),(.015*cos(a),.284,1.212+.015*sin(a))],.002,brass,'chest',6)
for s in [-1,1]:
    pts=[]
    for j in range(37):
        t=j/36
        pts.append((s*(.087+.052*sin(pi*t)),.177+.02*sin(2*pi*t),1.203-.19*sin(pi*t*.88)))
    path('Tubo respirazione '+str(s),pts,.012,dark,'chest',10)
    # A helical rib follows the tube without adding dozens of separate toruses.
    rib=[]
    for j in range(181):
        t=j/180;idx=min(35,int(t*36));frac=t*36-idx
        p=Vector(pts[idx]).lerp(Vector(pts[idx+1]),frac)
        tang=(Vector(pts[idx+1])-Vector(pts[idx])).normalized();u=tang.cross(Vector((0,1,0))).normalized();v=tang.cross(u)
        a=2*pi*22*t;rib.append(tuple(p+.012*(u*cos(a)+v*sin(a))))
    path('Spirale tubo '+str(s),rib,.0018,edge,'chest',4)
    cylinder('Raccordo tubo '+str(s),(s*.087,.177,1.203),(s*.087,.177,1.226),.017,bronze,'chest',12)

# Soft pouch directly below the brass shell.
box('Sacca dorsale',(0,.167,1.078),(.155,.075,.125),leather,'spine',.015)
box('Patella sacca dorsale',(0,.213,1.117),(.163,.014,.05),edge,'spine',.009)
for s in [-1,1]:
    box('Chiusura sacca '+str(s),(s*.047,.224,1.075),(.018,.008,.075),leather,'spine',.002)
    cylinder('Bottone sacca '+str(s),(s*.047,.228,1.076),(s*.047,.233,1.076),.005,brass,'spine',10)

# Coiled rope at the right hip, three unequal loops with winding and a knot.
for k in range(3):
    pts=[]
    for j in range(65):
        a=2*pi*j/64
        pts.append((-.12+(.045+k*.009)*cos(a),-.089-.006*k-.007*sin(a*2),.859+(.12+k*.017)*sin(a)))
    path('Boucle corde %d'%k,pts,.0045,rope,'pelvis',8)
    # Fine alternating twist only on one loop: economical detail.
    if k==1:
        fine=[]
        for j in range(161):
            a=2*pi*j/160;p=Vector((-.12+.054*cos(a),-.095-.007*sin(a*2),.859+.137*sin(a)))
            fine.append(tuple(p+Vector((.003*cos(a)*cos(a*35),.003*sin(a*35),.003*sin(a)*cos(a*35)))))
        path('Toron corde',fine,.0012,thread,'pelvis',4)
path('Noeud corde',[(-.153,-.105,1.004),(-.115,-.113,.987),(-.141,-.119,.98),(-.156,-.108,.999),(-.129,-.115,1.009),(-.11,-.12,.987)],.006,rope,'pelvis',8)
path('Bout libre corde',[(-.13,-.112,.99),(-.16,-.125,.918),(-.17,-.125,.85)],.004,rope,'pelvis',8)

# Rolled map case / brass canister along the other thigh, slightly tilted.
a=Vector((.185,-.025,.69));b=Vector((.154,-.022,.982));axis=(b-a).normalized()
cylinder('Etui cartes tube',a,b,.034,edge,'pelvis',20)
for k,t in enumerate([0,.07,.45,.83,1]):
    p=a.lerp(b,t);cylinder('Cerclage etui %d'%k,p-axis*.009,p+axis*.009,.037,brass,'pelvis',20)
for s in [-1,1]:
    path('Nervure etui '+str(s),[tuple(a+Vector((s*.022,-.027,0))),tuple(b+Vector((s*.022,-.027,0)))],.002,bronze,'pelvis',6)
ribbon('Sangle etui',[(.095,-.077,.99),(.147,-.06,.955),(.185,-.052,.81)],.017,leather,'pelvis')

# Compass on left forearm: case, green dial, bezel and needle.
c=Vector((.386,-.039,1.112));cylinder('Boussole boitier',c,c+Vector((0,-.019,0)),.029,bronze,'forearm.L',24)
cylinder('Boussole cadran',c+Vector((0,-.019,0)),c+Vector((0,-.021,0)),.023,patina,'forearm.L',24)
torus('Boussole lunette',c+Vector((0,-.022,0)),.025,.003,brass,'forearm.L',seg=24,sides=6)
mesh('Aiguille boussole',[(c.x-.003,c.y-.023,c.z-.017),(c.x-.005,c.y-.023,c.z+.003),(c.x+.006,c.y-.023,c.z+.018),(c.x+.004,c.y-.023,c.z-.003)],[(0,1,2,3)],ivory,'forearm.L',False)
for j in range(8):
    ang=2*pi*j/8;path('Graduation boussole '+str(j),[(c.x+.018*cos(ang),c.y-.023,c.z+.018*sin(ang)),(c.x+.021*cos(ang),c.y-.023,c.z+.021*sin(ang))],.0008,ivory,'forearm.L',4)

# Pendant and small chest fasteners.
path('Chaine pendentif',[(-.048,-.101,1.01),(-.029,-.119,.963),(-.01,-.112,.99)],.0015,brass,'pelvis',6)
cylinder('Medaille',(-.029,-.119,.954),(-.029,-.124,.954),.015,bronze,'pelvis',20)
torus('Medaille contour',(-.029,-.125,.954),.013,.0018,brass,'pelvis',seg=20,sides=6)
path('Rose medaille',[(-.029,-.127,.943),(-.029,-.127,.965)],.0012,ivory,'pelvis',5)
path('Rose medaille transverse',[(-.04,-.127,.954),(-.018,-.127,.954)],.0012,ivory,'pelvis',5)

save();log('Attrezzatura completa; triangoli:',tri_count())
render_viste('04_attrezzatura',viste=['fronte','retro','destra','tre_quarti'])
