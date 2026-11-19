import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
setup_materials()

# Reserve a little more of the budget for the iconic hip equipment.
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.name.startswith(('Casco_','Tubo_','Zaino_','Spallaccio_','Regolatore_')):
        o.data.calc_loop_triangles()
        if len(o.data.loop_triangles)>80:
            bpy.context.view_layer.objects.active=o;de=o.modifiers.new('Ottimizzazione_equipaggiamento','DECIMATE');de.ratio=.72;bpy.ops.object.modifier_apply(modifier=de.name)

def ring_at(name,center,direction,radius,mat='brass',r=.0025,n=16,bone='pelvis'):
    c=Vector(center);t=Vector(direction).normalized();a=t.cross(Vector((0,1,0))).normalized()
    if a.length<.01:a=Vector((1,0,0))
    b=t.cross(a).normalized()
    return tube(name,[tuple(c+radius*(a*cos(i*2*pi/n)+b*sin(i*2*pi/n))) for i in range(n)],r,mat,bone,6,True)

# Four uneven loops of heavy hemp rope, hung from an actual belt tie.
for j in range(4):
    pts=[]
    for k in range(32):
        t=k*2*pi/32
        pts.append((-.130+(.039+j*.004)*sin(t),-.132-j*.005-.005*cos(t),.849+(.099+j*.009)*cos(t)))
    tube('Corda_avvolta_'+str(j),pts,.0049,'rope','pelvis',6,True)
for j in range(2):
    pts=[(-.112-j*.012,-.130,1.018),(-.108-j*.012,-.144,.988),(-.115-j*.012,-.149,.952)]
    tube('Legatura_corda_'+str(j),pts,.0045,'rope','pelvis',6)
    circle('Nodo_corda_'+str(j),(-.117,-.153-j*.006,.982),.013,.008,'rope','pelvis',.0035,n=12)
tube('Capo_corda_libero',[(-.114,-.157,.969),(-.094,-.158,.913),(-.104,-.159,.858),(-.095,-.151,.825)],.0036,'rope','pelvis',6)
for j in range(3):
    tube('Corda_sfrangiata_'+str(j),[(-.095,-.151,.825),(-.094+j*.002,-.151,.813-j*.003)],.0008,'rope','pelvis',4)

# Oval leather pouch with flap, belt loop, seam and stud.
ell('Borsa_fianco',(-.153,-.087,.981),(.044,.032,.051),'leather','pelvis',16,10)
ell('Borsa_patella',(-.154,-.113,1.003),(.044,.009,.027),'darkleather','pelvis',16,8)
tube('Borsa_cucitura',[(-.189,-.121,1.009),(-.184,-.123,.989),(-.152,-.125,.978),(-.121,-.123,.991),(-.117,-.12,1.009)],.0012,'stitch','pelvis',5)
ell('Borsa_bottone',(-.153,-.126,.988),(.004,.002,.004),'brass','pelvis',8,6)
strap('Borsa_passante',[(-.152,-.086,1.054),(-.153,-.107,1.025),(-.151,-.121,1.01)],.016,'leatheredge','pelvis')

# Long rolled-map canister, tilted out from the right hip as in the drawing.
a=Vector((.175,-.071,1.003));b=Vector((.213,-.092,.723));axis=(b-a).normalized()
tube('Portamappe_corpo',[tuple(a),tuple(b)],.027,'shirt','pelvis',16)
for j,t in enumerate([.02,.14,.79,.97]):
    p=a.lerp(b,t)
    tube('Portamappe_fascia_'+str(j),[tuple(p-axis*.008),tuple(p+axis*.008)],.029,'brass','pelvis',12)
    ring_at('Portamappe_orlo_'+str(j),p,axis,.029,'brassedge',.0018,16)
tube('Portamappe_coperchio',[tuple(a-axis*.007),tuple(a-axis*.022)],.030,'leather','pelvis',16)
strap('Portamappe_cinghia',[(.115,-.075,1.035),(.173,-.094,.99),(.184,-.112,.948),(.195,-.114,.853)],.016,'leather','pelvis')
for j in range(4):
    p=a.lerp(b,.25+j*.14);ell('Portamappe_rivetto_'+str(j),(p.x,p.y-.028,p.z),(.002,.0014,.002),'brass','pelvis',8,6)

# Compact brass telescope strapped to the opposite thigh.
a=Vector((-.177,-.090,.921));b=Vector((-.204,-.116,.804));axis=(b-a).normalized()
tube('Cannocchiale_fodero',[tuple(a),tuple(b)],.022,'leather','pelvis',14)
for j,t in enumerate([.0,.2,.83,1.]):
    p=a.lerp(b,t);tube('Cannocchiale_anello_'+str(j),[tuple(p-axis*.005),tuple(p+axis*.005)],.024,'brass','pelvis',12)
ring_at('Cannocchiale_lente',b+axis*.006,axis,.018,'iron',.002,14)

# Long ripped fabric strips beside the map case.
for k in range(2):
    verts=[];uv=[]
    for i in range(7):
        t=i/6;x=.129+k*.024+.009*sin(t*4+k);y=-.112+.013*sin(t*3)
        z=1.01-t*(.27+k*.045)
        for s in [-1,1]:
            zz=z+(.011*s if i==6 else 0);verts.append((x+s*(.014-.005*t),y,zz));uv.append(((s+1)/2,1-t))
    o=mesh('Bande_tessuto_strappato_'+str(k),verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(6)],'shirt','pelvis',uv)

# A small hanging brass compass and chain beneath the belt.
tube('Catena_bussola',[(-.041,-.102,1.026),(-.039,-.127,1.002),(-.016,-.139,.976)],.0018,'iron','pelvis',5)
disk('Bussola_pendente',(-.016,-.141,.961),.017,.006,'brass','pelvis',n=16)
disk('Bussola_pendente_quadrante',(-.016,-.146,.961),.012,.002,'shirt','pelvis',n=16)
tube('Bussola_pendente_ago',[(-.023,-.148,.954),(-.010,-.148,.969)],.0012,'iron','pelvis',5)

# Bone-colored shoulder clasp over the folded capelet.
ell('Fermaglio_spalla',(.116,-.093,1.371),(.022,.011,.017),'brass','chest',12,8)
for s in [-1,1]:
    ell('Fermaglio_incavo_'+str(s),(.116+s*.008,-.104,1.374),(.004,.002,.004),'darkleather','chest',8,6)
tube('Fermaglio_catenella',[(.105,-.101,1.36),(.078,-.105,1.344),(.053,-.098,1.358)],.0018,'brass','chest',5)

# Lift the collar towards the jaw, reducing the exposed cylindrical neck.
for o in bpy.context.scene.objects:
    if o.name.startswith(('Colletto_','Bordo_colletto_')):
        for v in o.data.vertices:
            if v.co.z>1.435:v.co.z+=.018*(v.co.z-1.435)/.033
    if o.name=='Foulard_collo':
        for v in o.data.vertices:
            if v.co.z>1.43:v.co.z+=.012

save()
render_viste('06_accessori',viste=['fronte','tre_quarti','retro'])
portrait('06_dettaglio_accessori',center=(0,-.04,.91),scale=.64,loc=(.5,-1.7,1.02))
