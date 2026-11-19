import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
# Re-use the palette kept in the live step namespace.

# Soften the swept locks without a global high-poly subdivision.
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('Meche_','Vague_frange_')):
        bpy.context.view_layer.objects.active=o
        sm=o.modifiers.new('Ciocche_morbide','SUBSURF');sm.levels=1;sm.render_levels=1
        bpy.ops.object.modifier_apply(modifier=sm.name)
        de=o.modifiers.new('Ciocche_ottimizzate','DECIMATE');de.ratio=.45;bpy.ops.object.modifier_apply(modifier=de.name)
    if o.name.startswith('Stria_capelli_'):
        bpy.data.objects.remove(o,do_unlink=True)
    if o.name.startswith('Falda_giacca'):
        for p in o.data.polygons:p.use_smooth=False

def band_path(name,center,tangent,rx,ry,mat,bone,thickness=.003):
    t=Vector(tangent).normalized();a=Vector((0,1,0));b=t.cross(a).normalized();c=Vector(center)
    pts=[tuple(c+a*rx*cos(i*2*pi/20)+b*ry*sin(i*2*pi/20)) for i in range(20)]
    return tube(name,pts,thickness,mat,bone,6,True)

def buckle(name,c,w,h,bone='pelvis',mat='brass'):
    x,y,z=c
    tube(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],.0025,mat,bone,6,True)
    tube(name+'_ardiglione',[(x,y-.001,z),(x+w*.42,y-.002,z)],.0016,mat,bone,6)

# Curved shoulder and bunching sleeve folds, replacing the straight cylinders.
for s in [-1,1]:
    side='L' if s==1 else 'R';old=bpy.data.objects.get('Manica_'+side)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    shoulder=Vector((s*.154,0,1.357));elbow=Vector((s*.323,-.006,1.195));wrist=Vector((s*.451,-.021,1.065))
    specs=[(0,.032),(.06,.047),(.13,.057),(.22,.056),(.29,.051),(.35,.053),(.39,.046),(.43,.050),(.47,.043),(.50,.047),(.55,.042),(.60,.044),(.65,.037),(.70,.039),(.78,.033),(.9,.029),(1,.026)]
    sec=[]
    for t,r in specs:
        p=shoulder.lerp(elbow,t/.56) if t<=.56 else elbow.lerp(wrist,(t-.56)/.44)
        sec.append((tuple(p),r,r*1.07))
    sleeve=loft('Manica_'+side,sec,'shirt',sides=20,axis='PATH')
    for v in sleeve.data.vertices:
        v.co.y+=.0015*sin(v.co.z*175+v.co.x*50)
    weight_z(sleeve,[(1.065,'forearm.'+side),(1.18,'forearm.'+side),(1.235,'upper_arm.'+side),(1.37,'upper_arm.'+side)])
    for j,t in enumerate([.38,.45,.52]):
        p=shoulder.lerp(elbow,t/.56)
        band_path('Pieghe_manica_'+side+str(j),p,elbow-shoulder,.048-j*.002,.047-j*.002,'shirt','upper_arm.'+side,.0032)
    # Leg straps and kneepad shaped on the front of the bent knee.
    for j,z in enumerate([.405,.31]):
        loft('Fascia_stivale_'+side+str(j),[((s*.12,.006,z-.011),.057 if j==0 else .049,.056),((s*.12,.006,z+.011),.057 if j==0 else .049,.056)],'leather','shin.'+side,sides=20)
        buckle('Fibbia_stivale_'+side+str(j),(s*.145,-.045,z),.022,.020,'shin.'+side)
    for j,z in enumerate([.54,.66]):
        loft('Cinghia_ginocchio_'+side+str(j),[((s*.116,-.006,z-.009),.061,.064),((s*.116,-.006,z+.009),.061,.064)],'leather','shin.'+side if j==0 else 'thigh.'+side,sides=20)
    pad=ell('Ginocchiera_'+side,(s*.116,-.071,.601),(.051,.019,.062),'leather','shin.'+side,20,12)
    circle('Ribattitura_ginocchiera_'+side,(s*.116,-.088,.601),.043,.053,'leatheredge','shin.'+side,.002)
    for j in range(6):
        a=j*2*pi/6;ell('Rivetto_ginocchio_'+side+str(j),(s*.116+.039*cos(a),-.092,.601+.048*sin(a)),(.003,.0018,.003),'brass','shin.'+side,8,6)
    # Cloth gathered above kneepads and around boot tops.
    for j,z in enumerate([.698,.715,.46,.447]):
        x=s*.116;rx=.060 if z>.6 else .051;ry=.064 if z>.6 else .054
        pts=[(x+rx*cos(t),.006+ry*sin(t),z+.004*sin(t*2+j)) for t in [k*pi/10 for k in range(21)]]
        tube('Piega_pantalone_'+side+str(j),pts,.003,'pants','thigh.'+side if z>.6 else 'shin.'+side,6)
    # Long boot side seam and ankle straps.
    tube('Cucitura_stivale_'+side,[(s*.17,-.005,.10),(s*.16,-.004,.22),(s*.17,-.002,.39)],.0013,'stitch','shin.'+side,5)
    strap('Cinghia_caviglia_'+side,[(s*.165,-.045,.12),(s*.12,-.067,.14),(s*.075,-.045,.12)],.020,'leather','foot.'+side)
    # Three independent bands around the glove bracer.
    for j,t in enumerate([.43,.69,.91]):
        p=elbow.lerp(wrist,t);r=.048 if j==0 else (.041 if j==1 else .036)
        band_path('Fascia_bracciale_'+side+str(j),p,wrist-elbow,r,r,'darkleather','forearm.'+side,.004)
        ell('Bottone_bracciale_'+side+str(j),(p.x,p.y-r-.002,p.z),(.005,.0025,.005),'brass','forearm.'+side,10,6)
    # Back of glove with fingers' knuckle stitching.
    direction=(wrist-elbow).normalized();across=Vector((s*.71,0,.70));center=wrist+direction*.044
    ell('Rinforzo_dorso_guanto_'+side,(center.x,-.051,center.z),(.025,.006,.024),'leather','hand.'+side,16,10)
    for f in range(4):
        p=center+across*(f-1.5)*.013
        tube('Cucitura_guanto_'+side+str(f),[(p.x,-.057,p.z),(p.x+direction.x*.022,-.057,p.z+direction.z*.022)],.0011,'leatheredge','hand.'+side,5)

# Broad belt and hanging leather end, with two polished metal frames.
belt=loft('Cintura_vita',[((0,.002,1.014),.137,.094),((0,.002,1.052),.133,.093)],'leather','pelvis',sides=32)
for z in [1.018,1.048]:circle('Cucitura_cintura_'+str(z),(0,.002,z),.136,.095,'leatheredge','pelvis',.0016,'XY',32)
buckle('Fibbia_cintura',(-.012,-.096,1.033),.048,.034)
strap('Cintura_linguetta',[(.013,-.101,1.035),(.092,-.089,1.03),(.13,-.070,1.014),(.132,-.071,.975)],.024,'leather','pelvis')
for j in range(4):ell('Foro_cintura_'+str(j),(.043+j*.012,-.101+j*.0025,1.032),(.0016,.001,.0018),'black','pelvis',8,6)

# Crossing load-bearing harness, with visible edge seams.
harnesses=[
 [(-.13,-.067,1.373),(-.096,-.100,1.322),(-.043,-.115,1.245),(.017,-.095,1.16),(.088,-.084,1.055)],
 [(.129,-.068,1.374),(.09,-.103,1.326),(.027,-.117,1.25),(-.044,-.094,1.159),(-.101,-.078,1.055)]
]
for j,pts in enumerate(harnesses):
    strap('Imbracatura_incrociata_'+str(j),pts,.025,'leather','chest',.004)
    for sign in [-1,1]:
        tube('Cucitura_imbracatura_'+str(j)+str(sign),[(x+sign*.008,y-.003,z) for x,y,z in pts],.0009,'stitch','chest',5)
    p=pts[1];buckle('Regolatore_spalla_'+str(j),(p[0],p[1]-.006,p[2]),.031,.027,'chest')
for s in [-1,1]:
    strap('Cinghia_verticale_'+str(s),[(s*.084,-.081,1.065),(s*.075,-.089,1.14),(s*.072,-.111,1.227)],.015,'darkleather','spine')

# Jacket seams, central fastening and a worn, folded lapel.
for s in [-1,1]:
    tube('Cucitura_principessa_'+str(s),[(s*.089,-.063,1.07),(s*.085,-.057,1.13),(s*.097,-.071,1.18),(s*.105,-.082,1.23)],.0011,'leatheredge','spine',5)
    mesh('Risvolto_giacca_'+str(s),[(s*.008,-.086,1.35),(s*.051,-.091,1.377),(s*.068,-.102,1.31),(s*.026,-.120,1.259)],[(0,1,2,3)],'darkleather','chest',smooth=False)
for j in range(4):
    z=1.09+j*.039;ell('Chiusura_giacca_'+str(j),(.013,-.083-(z-1.09)*.16,z),(.0035,.002,.0035),'brass','spine',10,6)

# Compass/pressure gauge on left forearm: asymmetry visible in the reference.
c=Vector((.386,-.055,1.135))
ell('Quadrante_bracciale_corpo',c,(.029,.013,.029),'brass','forearm.L',24,12)
circle('Quadrante_bracciale_bordo',(c.x,c.y-.013,c.z),.025,.025,'brassedge','forearm.L',.003,n=24)
ell('Quadrante_bracciale_vetro',(c.x,c.y-.015,c.z),(.022,.002,.022),'glass','forearm.L',20,10)
for i in range(8):
    t=i*2*pi/8;tube('Tacca_quadrante_'+str(i),[(c.x+.017*cos(t),c.y-.018,c.z+.017*sin(t)),(c.x+.021*cos(t),c.y-.018,c.z+.021*sin(t))],.0008,'brassedge','forearm.L',4)
tube('Lancetta_quadrante',[(c.x-.009,c.y-.019,c.z-.008),(c.x+.011,c.y-.019,c.z+.013)],.001,'brassedge','forearm.L',5)

save()
render_viste('03_abiti',viste=['fronte','tre_quarti','destra'])
portrait('03_viso',scale=.38,center=(0,0,1.56),loc=(.13,-1.5,1.62))
