exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils import Quaternion
rope=mat('REV Corda canapa',(.70,.62,.47),rough=.91)
leather=mat('REV Pelle cinture',(.36,.22,.12),rough=.65)
brass=mat('REV Ottone',(.62,.45,.20),metal=1,rough=.35)
linen=bpy.data.materials['REV Lino crema']
fac=bpy.context.scene['scale_geometry'];zmin=bpy.context.scene['original_zmin']
def initial(p):return Vector((p[0]*fac,p[1]*fac,(p[2]-zmin)*fac))
# A fourth loop is copied from our existing rope, then all four are reshaped.
src=bpy.data.objects['Boucle corde 2'];ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob);ob.name='REV Quarto giro corda'
for k in range(4):
    oldk=min(k,2);ob=bpy.data.objects['Boucle corde '+str(k)] if k<3 else bpy.data.objects['REV Quarto giro corda']
    oc=initial((-.12,-.089-.006*oldk,.859));rx=(.045+.009*oldk)*fac;rz=(.12+.017*oldk)*fac
    for v in ob.data.vertices:
        p=v.co;a=math.atan2((p.z-oc.z)/rz,(p.x-oc.x)/rx)
        oldc=initial((-.12+(.045+.009*oldk)*cos(a),-.089-.006*oldk-.007*sin(2*a),.859+(.12+.017*oldk)*sin(a)))
        oldtan=Vector((-rx*sin(a),-.014*fac*cos(2*a),rz*cos(a))).normalized();newtan=Vector((-.05*sin(a),0,.08*cos(a))).normalized();rot=oldtan.rotation_difference(newtan)
        offset=rot@(p-oldc);offset=Quaternion(newtan,a*13)@offset
        newc=Vector((-.17+.05*cos(a)-k*.006,-.046+k*.005,.84-.020*k+.08*sin(a)))
        v.co=newc+offset*1.58
    assign(ob,rope);ob['bone']='pelvis'
# Original twisted detail follows the second loop; no smooth-only cord bundle.
old=[initial((-.12+.054*cos(2*pi*j/64),-.095-.007*sin(4*pi*j/64),.859+.137*sin(2*pi*j/64))) for j in range(65)]
new=[(-.176+.05*cos(2*pi*j/64),-.041,.82+.08*sin(2*pi*j/64)) for j in range(65)]
ob=bpy.data.objects['Toron corde'];deform_path(ob,old,new,1.6);assign(ob,rope)
for ob in select_prefix('Noeud corde','Bout libre corde'):
    transform(ob,lambda p:(p.x-.04,p.y+.055,p.z-.02));assign(ob,rope)
# Short suspension reaches the low belt.
path('REV Attacco corda',[(-.17,-.04,.98),(-.184,-.05,.947),(-.182,-.045,.91)],.007,rope,'pelvis',8)
# Almost-horizontal canister, with brass caps and two hoops.
a=Vector((-.34,-.03,.89));b=Vector((-.14,-.03,.91));d=(b-a).normalized()
cylinder('REV Barilotto cuoio',a,b,.035,leather,'pelvis',20)
for k,t in enumerate([0,.25,.75,1]):
    c=a.lerp(b,t);length=.014 if k in [0,3] else .008
    cylinder('REV Cerchio barilotto '+str(k),c-d*length/2,c+d*length/2,.0365,brass,'pelvis',20)
ribbon('REV Attacco barilotto',[(-.16,-.04,.955),(-.20,-.06,.94),(-.24,-.06,.90)],.022,leather,'pelvis',.006)
# Turn the original right belt pouch into the specified oval purse.
o=bpy.data.objects['Tasca cintura R'];a,b=bounds(o);c=(a+b)/2;half=(b-a)/2
for v in o.data.vertices:
    q=Vector([(v.co[i]-c[i])/half[i] for i in range(3)]);q=q.lerp(q.normalized(),.70);v.co=(-.20+q.x*.052,-.04+q.y*.035,.99+q.z*.046)
fit(o,(-.245,-.07,.95),(-.155,-.01,1.03));assign(o,leather)
o=bpy.data.objects['Patella tasca R'];fit(o,(-.239,-.079,.997),(-.161,-.069,1.028));assign(o,leather)
o=bpy.data.objects['Bottone tasca R'];fit(o,(-.204,-.082,1.006),(-.196,-.078,1.014));assign(o,brass)
# Straighten and lengthen the original map case and its existing hardware.
oa=Vector((.185,-.025,.69));ob=Vector((.154,-.022,.982));od=(ob-oa).normalized();nd=Vector((0,0,1));rot=od.rotation_difference(nd);na=Vector((.22,-.02,.55));nb=Vector((.22,-.02,.96))
for o in select_prefix('Etui cartes','Cerclage etui','Nervure etui'):
    def mp(p):
        p=Vector((p.x/fac,p.y/fac,p.z/fac+zmin));t=(p-oa).dot(od)/(ob-oa).length;off=p-(oa+(ob-oa)*t)
        return na.lerp(nb,t)+rot@off*1.10
    transform(o,mp);assign(o,brass if o.name.startswith(('Cerclage etui 0','Cerclage etui 4')) else leather)
for k,lo,hi in [(0,.53,.57),(4,.94,.98)]:fit(bpy.data.objects['Cerclage etui '+str(k)],(.1825,-.0575,lo),(.2575,.0175,hi))
o=bpy.data.objects['Sangle etui'];fit(o,(.14,-.067,.81),(.24,-.045,1.01));assign(o,leather)
cylinder('REV Etui fin',(.285,-.005,.61),(.285,-.005,.96),.025,leather,'pelvis',16)
for z in [.61,.96]:cylinder('REV Capuchon etui fin '+str(z),(.285,-.005,z-.012),(.285,-.005,z+.012),.027,brass,'pelvis',16)
ribbon('REV Bride double etui',[(.17,-.025,1.00),(.22,-.045,.98),(.285,-.030,.955)],.020,leather,'pelvis',.005)
# Torn hanging cloth tucked between the map tube and the left thigh.
vv=[];ff=[];N=6;R=12
for i in range(R+1):
    t=i/R
    for j in range(N+1):
        x=.155+j*.07/N;z=.98-.36*t+(t**8)*(.025*sin(j*2.6));vv.append((x,-.049+.007*sin(t*13+j*.7),z))
for i in range(R):
    for j in range(N):a=i*(N+1)+j;ff.append((a,a+1,a+N+2,a+N+1))
o=mesh('REV Laccio stoffa strappato',vv,ff,linen,'pelvis');mod=o.modifiers.new('Stoffa doppia','SOLIDIFY');mod.thickness=.003;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
# Three small additional belt pockets: existing left pouch plus two rear pockets.
for name,lo,hi in [('Tasca cintura L',(.145,.015,1.00),(.205,.045,1.05)),('Patella tasca L',(.145,.010,1.035),(.205,.017,1.055)),('Bottone tasca L',(.171,.007,1.037),(.179,.011,1.045))]:
    o=bpy.data.objects[name];fit(o,lo,hi);assign(o,brass if name.startswith('Bottone') else leather)
for s in [-1,1]:
    box('REV Tasca posteriore '+str(s),(s*.075,.125,1.055),(.06,.03,.05),leather,'pelvis',.005)
    box('REV Patella posteriore '+str(s),(s*.075,.144,1.07),(.061,.007,.026),leather,'pelvis',.003)
    uv('REV Bottone posteriore '+str(s),(s*.075,.149,1.069),(.003,.002,.003),brass,'pelvis',8,6)
log('Quattro giri di corda ritorta; barilotto e borsa destri; astucci sinistri 0.45 e 0.35 m; stoffa strappata e tre tasche')
finish_group(7)
