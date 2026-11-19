import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
setup_materials()

def smooth_path(points,per=5):
    p=[Vector(v) for v in points];out=[]
    for i in range(len(p)-1):
        a=p[max(0,i-1)];b=p[i];c=p[i+1];d=p[min(i+2,len(p)-1)]
        for j in range(per):
            t=j/per
            v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            out.append(tuple(v))
    return out+[tuple(p[-1])]

def disk(name,center,radius,depth,mat,bone='chest',axis='Y',n=24):
    c=Vector(center);verts=[];uv=[]
    a=Vector((1,0,0)) if axis!='X' else Vector((0,1,0))
    b=Vector((0,0,1)) if axis!='Z' else Vector((0,1,0))
    normal=a.cross(b)
    for k in [-1,1]:
        for i in range(n):
            t=i*2*pi/n;verts.append(tuple(c+a*(radius*cos(t))+b*(radius*sin(t))+normal*depth*k/2));uv.append((.5+.48*cos(t),.5+.48*sin(t)))
    faces=[tuple(range(n-1,-1,-1)),tuple(n+i for i in range(n))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    return mesh(name,verts,faces,mat,bone,uv)

# The helmet is mounted on the upper back, above a small leather pack.
ell('Casco_calotta_ottone',(0,.169,1.335),(.129,.104,.158),'brass','chest',32,20)
loft('Casco_collare_inferiore',[((0,.166,1.19),.079,.066),((0,.167,1.213),.093,.079),((0,.168,1.23),.100,.087)],'brass','chest',sides=24)
circle('Casco_orlo_inferiore',(0,.166,1.207),.093,.079,'brassedge','chest',.004,'XY',28)

# Rear window: recessed dark glass, thick annular case, bolts and protective bars.
disk('Casco_oblo_sede',(0,.271,1.347),.081,.016,'darkleather',n=32)
disk('Casco_oblo_vetro',(0,.283,1.347),.067,.006,'glass',n=32)
circle('Casco_oblo_cornice',(0,.286,1.347),.076,.076,'brassedge','chest',.006,n=36)
circle('Casco_oblo_guarnizione',(0,.288,1.347),.066,.066,'iron','chest',.0023,n=28)
for i in range(8):
    t=i*pi/4
    ell('Casco_bullone_oblo_'+str(i),(.076*cos(t),.294,1.347+.076*sin(t)),(.004,.003,.004),'brass','chest',8,6)
for x in [-.026,.026]:
    h=(.064**2-x*x)**.5
    tube('Casco_griglia_verticale_'+str(x),[(x,.296,1.347-h),(x,.299,1.347),(x,.296,1.347+h)],.003,'brass','chest',6)
tube('Casco_griglia_orizzontale',[(-.065,.296,1.347),(0,.300,1.347),(.065,.296,1.347)],.003,'brass','chest',6)

# Small side windows with four fasteners each.
for s in [-1,1]:
    disk('Casco_oblo_laterale_'+str(s),(s*.126,.167,1.35),.038,.010,'glass',axis='X',n=20)
    circle('Casco_cornice_laterale_'+str(s),(s*.133,.167,1.35),.041,.041,'brassedge','chest',.004,'YZ',24)
    for k in range(4):
        t=k*pi/2
        ell('Casco_vite_laterale_'+str(s)+str(k),(s*.138,.167+.043*cos(t),1.35+.043*sin(t)),(.0025,.003,.003),'iron','chest',8,6)
    tube('Casco_barra_laterale_'+str(s),[(s*.139,.131,1.35),(s*.141,.203,1.35)],.0025,'brass','chest',6)

# Raised plate seams curved over the hammered shell.
for s in [-1,1]:
    pts=[]
    for k in range(17):
        t=-pi*.43+k*pi*.86/16
        pts.append((s*.105*cos(t),.174+.064*cos(t),1.335+.158*sin(t)))
    tube('Casco_nervatura_'+str(s),pts,.003,'brassedge','chest',6)
    for k in range(5):
        t=-1+k*.5
        ell('Casco_ribattino_'+str(s)+str(k),(s*.110*cos(t),.178+.065*cos(t),1.335+.155*sin(t)),(.003,.003,.003),'iron','chest',8,6)
loft('Casco_valvola_superiore',[((0,.17,1.477),.025,.024),((0,.17,1.504),.025,.024),((0,.17,1.507),.019,.019),((0,.17,1.529),.019,.019)],'brass','chest',sides=16)
circle('Casco_valvola_orlo',(0,.17,1.526),.021,.021,'brassedge','chest',.003,'XY',20)
cube('Casco_fermo_valvola',(0,.17,1.537),(.042,.018,.014),'iron','chest',.003)
for s in [-1,1]:
    cube('Casco_aggancio_'+str(s),(s*.098,.204,1.25),(.031,.026,.032),'brass','chest',.003)
    disk('Casco_raccordo_'+str(s),(s*.099,.228,1.249),.017,.019,'iron',n=12)

# Short hoses with alternating diameters: corrugation is actual exported geometry.
hoses=[
 [(-.099,.24,1.249),(-.150,.22,1.205),(-.159,.15,1.145),(-.132,.15,1.095),(-.091,.185,1.10)],
 [(.099,.24,1.249),(.150,.225,1.19),(.165,.17,1.107),(.141,.148,1.065),(.096,.178,1.09)],
 [(.119,.168,1.28),(.173,.105,1.22),(.188,.05,1.125),(.178,-.019,1.025)]
]
for j,points in enumerate(hoses):
    pts=smooth_path(points,9)
    radii=[.0095 if k%2==0 else .0115 for k in range(len(pts))]
    tube('Tubo_corrugato_'+str(j),pts,.010,'darkleather','chest',8,radii=radii)
    for end in [0,-1]:
        p=Vector(pts[end]);q=Vector(pts[1] if end==0 else pts[-2]);direction=(q-p).normalized()
        tube('Tubo_raccordo_'+str(j)+str(end),[tuple(p-direction*.006),tuple(p+direction*.011)],.014,'brass','chest',10)

# Backpack visible beneath the helmet, with stitched flap and two belts.
cube('Zaino_inferiore',(0,.155,1.095),(.166,.082,.152),'leather','spine',.014)
flap=mesh('Zaino_patella',[(-.089,.199,1.166),(.089,.199,1.166),(.084,.209,1.092),(.030,.216,1.063),(-.040,.216,1.068),(-.087,.210,1.098)],[(0,1,2,3,4,5)],'darkleather','spine',smooth=False)
tube('Zaino_cucitura',[(-.082,.215,1.157),(-.080,.216,1.10),(-.037,.221,1.076),(.030,.221,1.071),(.078,.215,1.098),(.082,.210,1.157)],.0013,'stitch','spine',5)
for s in [-1,1]:
    strap('Zaino_cinghia_'+str(s),[(s*.051,.211,1.177),(s*.051,.222,1.12),(s*.050,.226,1.054),(s*.048,.210,1.028)],.017,'leatheredge','spine')
    # Buckle made directly in the rear-facing plane.
    tube('Zaino_fibbia_'+str(s),[(s*.051-.011,.229,1.08),(s*.051+.011,.229,1.08),(s*.051+.011,.229,1.105),(s*.051-.011,.229,1.105)],.002,'brass','spine',6,True)
    strap('Spallaccio_zaino_'+str(s),[(s*.11,.066,1.40),(s*.105,.11,1.32),(s*.10,.13,1.22),(s*.07,.16,1.16)],.023,'leather','chest')

# Small side pressure valve on the backpack.
disk('Regolatore_zaino',(-.10,.16,1.10),.028,.017,'iron','spine',axis='X',n=16)
circle('Regolatore_bordo',(-.111,.16,1.10),.025,.025,'brass','spine',.003,'YZ',20)

save()
render_viste('05_casco',viste=['retro','destra','tre_quarti'])
portrait('05_dettaglio_casco',center=(0,.18,1.30),scale=.52,loc=(.50,1.7,1.45))
