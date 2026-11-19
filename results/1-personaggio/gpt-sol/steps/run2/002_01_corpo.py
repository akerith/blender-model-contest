exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
setup_materials();studio()
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1

# Torso shaped by tailored sections, slightly lifted breast and narrow natural waist.
body=loft('Giacca_corpo',[
 ((0,.005,.94),.145,.090),((0,.005,.99),.132,.085),((0,.005,1.055),.112,.077),
 ((0,.005,1.115),.108,.077),((0,.005,1.18),.126,.088),((0,-.004,1.235),.145,.108),
 ((0,.002,1.285),.153,.095),((0,.008,1.33),.166,.077),((0,.009,1.365),.174,.067),
 ((0,.008,1.39),.123,.058),((0,0,1.414),.052,.045)],'coat',sides=32)
weight_z(body,[(.94,'pelvis'),(1.08,'spine'),(1.23,'chest')])
neck=loft('Collo', [((0,.006,1.38),.044,.039),((0,.004,1.44),.039,.034),((0,.003,1.49),.041,.036),((0,0,1.515),.048,.042)],'skin',bone='neck',sides=24)

# Fitted split tunic tails.
for s in [-1,1]:
    side='L' if s==1 else 'R'
    panel=mesh('Falda_giacca_'+side,[(s*.012,-.091,1.01),(s*.135,-.065,1.01),(s*.168,-.08,.86),(s*.064,-.119,.84),(s*.012,-.112,.89)],[(0,1,2,3,4)],'coat','pelvis')
    mod=panel.modifiers.new('Spessore','SOLIDIFY');mod.thickness=.004;bpy.context.view_layer.objects.active=panel;bpy.ops.object.modifier_apply(modifier=mod.name)
    tube('Bordo_falda_'+side,[(s*.012,-.095,1.01),(s*.012,-.116,.89),(s*.064,-.123,.84),(s*.168,-.084,.86)],.002,'leatheredge','pelvis',6)
    # Trousers in natural separated stance.
    leg=loft('Pantalone_'+side,[
      ((s*.085,.012,.99),.087,.082),((s*.099,.008,.94),.085,.089),((s*.108,.01,.86),.082,.087),
      ((s*.112,.012,.77),.073,.075),((s*.115,-.002,.68),.060,.061),((s*.116,-.013,.61),.058,.059),
      ((s*.117,-.010,.56),.059,.059),((s*.119,.006,.49),.054,.057),((s*.12,.013,.42),.049,.049),
      ((s*.12,.009,.36),.045,.043)],'pants',sides=24)
    weight_z(leg,[(.42,'shin.'+side),(.56,'shin.'+side),(.64,'thigh.'+side),(.9,'thigh.'+side),(.99,'pelvis')])
    # Tall boots, sculpted ankles and projecting toes.
    boot=loft('Stivale_'+side,[
      ((s*.12,-.042,.038),.055,.116),((s*.12,-.045,.060),.055,.118),((s*.12,-.042,.087),.054,.105),
      ((s*.12,-.009,.12),.046,.063),((s*.12,.010,.18),.039,.043),((s*.12,.014,.25),.041,.047),
      ((s*.12,.009,.34),.047,.050),((s*.119,.005,.425),.055,.055)],'darkleather',sides=24)
    weight_z(boot,[(.07,'foot.'+side),(.14,'foot.'+side),(.22,'shin.'+side),(.43,'shin.'+side)])
    sole=loft('Suola_'+side,[((s*.12,-.044,.014),.057,.119),((s*.12,-.044,.035),.059,.122),((s*.12,-.044,.048),.057,.12)],'sole','foot.'+side,sides=24)
    # Leather front shaft and toe cap seam.
    strap('Linguetta_stivale_'+side,[(s*.12,-.039,.155),(s*.12,-.040,.24),(s*.12,-.047,.34),(s*.119,-.054,.415)],.055,'leather','shin.'+side)
    circle('Bordo_stivale_'+side,(s*.119,.005,.425),.056,.056,'leatheredge','shin.'+side,.004,'XY')
    tube('Cucitura_punta_'+side,[(s*.12-.045,-.11,.063),(s*.12-.03,-.145,.064),(s*.12,-.159,.065),(s*.12+.03,-.145,.064),(s*.12+.045,-.11,.063)],.0014,'stitch','foot.'+side,6)
    for j in range(7):
        z=.18+j*.031;y=-.044-(z-.18)*.035
        tube('Laccio_'+side+'_'+str(j),[(s*.12-.022,y,z),(s*.12+.022,y-.003,z+.024),(s*.12+.021,y,z+.031)],.0017,'rope','shin.'+side,6)
        tube('Laccio_inc_'+side+'_'+str(j),[(s*.12+.022,y,z),(s*.12-.022,y-.003,z+.024)],.0017,'rope','shin.'+side,6)
    # A-pose sleeves with several intermediate deformation rings.
    shoulder=Vector((s*.169,0,1.365));elbow=Vector((s*.323,-.006,1.195));wrist=Vector((s*.451,-.021,1.065))
    sections=[]
    for i,(t,rx,ry) in enumerate([(0,.055,.061),(.15,.058,.061),(.35,.052,.054),(.54,.044,.047),(.63,.043,.044),(.76,.040,.042),(1,.032,.033)]):
        if t<.56:p=shoulder.lerp(elbow,t/.56)
        else:p=elbow.lerp(wrist,(t-.56)/.44)
        sections.append((tuple(p),rx,ry))
    sleeve=loft('Manica_'+side,sections,'shirt',sides=20,axis='PATH')
    weight_z(sleeve,[(1.065,'forearm.'+side),(1.18,'forearm.'+side),(1.235,'upper_arm.'+side),(1.37,'upper_arm.'+side)])
    # Forearm glove cuff, articulated palm and five fingers.
    c1=elbow.lerp(wrist,.37);c2=wrist.lerp(elbow,.06)
    cuff=loft('Guanto_avambraccio_'+side,[(tuple(c1),.044,.047),(tuple(c1.lerp(c2,.12)),.045,.049),(tuple(c1.lerp(c2,.6)),.036,.038),(tuple(c2),.033,.035)],'leather','forearm.'+side,sides=20,axis='PATH')
    direction=(wrist-elbow).normalized(); palm_end=wrist+direction*.070
    palm=loft('Guanto_palmo_'+side,[(tuple(wrist),.027,.030),(tuple(wrist.lerp(palm_end,.42)),.025,.037),(tuple(palm_end),.019,.032)],'darkleather','hand.'+side,sides=16,axis='PATH')
    across=Vector((s*.71,0,.70))
    for f in range(4):
        base=palm_end+across*((f-1.5)*.016)
        length=[.054,.067,.062,.048][f]
        end=base+direction*length+Vector((0,-.004,-.005))
        finger=loft('Dito_'+side+'_'+str(f),[(tuple(base),.008,.0085),(tuple(base.lerp(end,.44)),.008,.008),(tuple(base.lerp(end,.75)),.0067,.0067),(tuple(end),.0035,.004)],'darkleather',sides=10,axis='PATH')
        finger.vertex_groups.new(name='finger%d.01.%s'%(f,side)).add(list(range(len(finger.data.vertices))),1,'REPLACE')
    thumbbase=wrist+direction*.025-across*.031
    thumbend=thumbbase+direction*.042-across*.025+Vector((0,-.012,0))
    loft('Pollice_'+side,[(tuple(thumbbase),.011,.011),(tuple(thumbbase.lerp(thumbend,.5)),.010,.010),(tuple(thumbend),.005,.005)],'darkleather','thumb.01.'+side,sides=10,axis='PATH')

# Anatomical head: section widths follow jaw, cheeks, temples and forehead.
head_sections=[(1.49,.022,.025,.0),(1.505,.041,.043,-.003),(1.525,.055,.053,-.001),(1.55,.064,.061,.002),(1.575,.073,.066,.006),(1.60,.075,.065,.009),(1.62,.074,.062,.010),(1.645,.068,.059,.012),(1.666,.055,.048,.013),(1.681,.032,.029,.014),(1.685,.005,.006,.014)]
verts=[];uv=[];n=48
for k,(z,rx,ry,cy) in enumerate(head_sections):
    for j in range(n):
        t=2*pi*j/n;x=rx*sin(t);y=cy-ry*cos(t)
        # hollow temples, cheek planes and eyelid sockets integrated in the face
        if cos(t)>0:
            y+=.009*exp(-((abs(x)-.032)/.021)**2-((z-1.593)/.018)**2)
            y-=.006*exp(-((abs(x)-.042)/.022)**2-((z-1.565)/.015)**2)
        verts.append((x,y,z));uv.append((j/n,k/(len(head_sections)-1)))
faces=[]
for k in range(len(head_sections)-1):
    for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
faces += [tuple(range(n-1,-1,-1)),tuple((len(head_sections)-1)*n+j for j in range(n))]
mesh('Viso',verts,faces,'skin','head',uv)
for s in [-1,1]:
    ell('Orecchio_'+str(s),(s*.074,.004,1.57),(.014,.012,.026),'skin','head',16,10)
    ell('Cavita_orecchio_'+str(s),(s*.080,-.005,1.57),(.005,.005,.014),'shadow','head',12,8)
    # eyes are fitted into sockets, with flesh upper and lower rims.
    ell('Occhio_'+str(s),(s*.0305,-.0545,1.592),(.020,.0095,.0082),'eye','head',20,12)
    ell('Iride_'+str(s),(s*.0305,-.0632,1.592),(.0068,.0017,.0070),'iris','head',16,10)
    ell('Pupilla_'+str(s),(s*.0305,-.0648,1.592),(.0032,.001,.0042),'black','head',12,8)
    ell('Riflesso_occhio_'+str(s),(s*.0305-.0018,-.0658,1.5945),(.0015,.0007,.0015),'eye','head',8,6)
    pts=[(s*(.012+i*.006),-.061-.002*sin(i*pi/6),1.591+.008*sin(i*pi/6)) for i in range(7)]
    tube('Palpebra_superiore_'+str(s),pts,.0025,'skin','head',8)
    tube('Ciglia_'+str(s),[(x,y-.001,z-.001) for x,y,z in pts],.0012,'hair','head',6)
    pts=[(s*(.012+i*.006),-.060,1.591-.0055*sin(i*pi/6)) for i in range(7)]
    tube('Palpebra_inferiore_'+str(s),pts,.0019,'skin','head',8)
    tube('Sopracciglio_'+str(s),[(s*.012,-.060,1.610),(s*.025,-.061,1.613),(s*.040,-.057,1.611),(s*.051,-.049,1.606)],.0034,'hair','head',8,radii=[.003,.0036,.003,.0014])
# Nose bridge, tapered tip, nostrils and restrained mouth.
loft('Naso', [((0,-.056,1.613),.007,.005),((0,-.063,1.594),.0075,.009),((0,-.077,1.573),.009,.012),((0,-.077,1.566),.012,.009),((0,-.069,1.562),.010,.005)],'skin','head',sides=16)
for s in [-1,1]:
    ell('Ala_naso_'+str(s),(s*.009,-.070,1.565),(.0065,.008,.0055),'skin','head',12,8)
    ell('Narice_'+str(s),(s*.0075,-.076,1.562),(.003,.002,.0017),'shadow','head',10,6)
tube('Labbro_superiore',[(-.022,-.057,1.544),(-.010,-.064,1.548),(0,-.066,1.546),(.010,-.064,1.548),(.022,-.057,1.544)],.0026,'lip','head',8)
tube('Labbro_inferiore',[(-.020,-.058,1.542),(-.009,-.064,1.540),(0,-.065,1.5395),(.009,-.064,1.540),(.020,-.058,1.542)],.003,'lip','head',8)
tube('Rima_labbra',[(-.020,-.060,1.543),(-.009,-.066,1.544),(0,-.067,1.543),(.009,-.066,1.544),(.020,-.060,1.543)],.0009,'shadow','head',6)

save()
render_viste('01_corpo',viste=['fronte','destra','tre_quarti'])
portrait('01_viso',scale=.31,center=(0,0,1.575),loc=(.10,-1.5,1.60))
