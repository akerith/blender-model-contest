exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
navy=mat('REV Giacca navy',(.13,.16,.22),rough=.90)
leather=mat('REV Pelle cinture',(.36,.22,.12),rough=.65)
brass=mat('REV Ottone',(.62,.45,.20),metal=1,rough=.35)
seam=mat('REV Cucitura navy',(.08,.105,.15),rough=.94)
for o in select_prefix('Corpetto','Falda giacca','Profilo falda','Abbottonatura'):assign(o,navy)
headbody=bpy.data.objects['Corpetto sagomato']
tree=BVHTree.FromPolygons([v.co for v in headbody.data.vertices],[list(p.vertices) for p in headbody.data.polygons])
def front(x,z):
    h=tree.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))
    return h[0].y if h[0] else -.083
fac=bpy.context.scene['scale_geometry'];zmin=bpy.context.scene['original_zmin']
def oldtor(p):return torso(Vector((p[0]*fac,p[1]*fac,(p[2]-zmin)*fac)))
for s,side in [(-1,'R'),(1,'L')]:
    old=[oldtor(p) for p in [(s*.112,.064,1.36),(s*.12,.015,1.387),(s*.108,-.065,1.364),(s*.068,-.095,1.29),(s*.018,-.101,1.207),(-s*.07,-.083,1.112),(-s*.088,-.071,1.065)]]
    new=[(s*.13,.07,1.41),(s*.13,0,1.425),(s*.13,-.065,1.41),(s*.070,-.11,1.325),(0,-.125,1.25),(-s*.10,-.106,1.105),(-s*.15,-.079,1.04)]
    o=bpy.data.objects['Bretella incrociata '+side];deform_path(o,old,new,1.46);assign(o,leather)
    for v in o.data.vertices:
        if v.co.y<-.035:v.co.y=front(v.co.x,v.co.z)-(.009 if side=='L' else .005)
    st=bpy.data.objects['Cucitura bretella '+side];deform_path(st,old,new,1.46)
    for v in st.data.vertices:v.co.y=front(v.co.x,v.co.z)-(.011 if side=='L' else .007)
    for o in select_prefix('Fibbia pettorale '+side):
        a,b=bounds(o);c=(a+b)/2;shift(o,(s*.055-c.x,-.124-c.y,1.30-c.z));assign(o,brass)
    # Existing rear harness now reaches the future helmet ring.
    o=bpy.data.objects['Bretella dorsale '+side]
    oldb=[oldtor(p) for p in [(s*.112,.071,1.36),(s*.097,.091,1.25),(s*.07,.091,1.11)]]
    deform_path(o,oldb,[(s*.13,.07,1.41),(s*.145,.15,1.28),(s*.13,.23,1.145)],1.46);assign(o,leather);o['bone']='chest'
    for o in select_prefix('Falda giacca corretta '+side,'Profilo falda corretto '+side):
        a,b=bounds(o)
        transform(o,lambda p:(p.x*1.09,p.y,1.06-(b.z-p.z)*(.26/(b.z-a.z))))
    # Continue the skirt behind the body with copies of the two original panels.
    src=bpy.data.objects['Falda giacca corretta '+side];ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob);ob.name='REV Falda posteriore '+side
    transform(ob,lambda p:(p.x,-p.y*.88,p.z));assign(ob,navy)
# Six tailored seams; four new seams supplement the original pair.
for o in select_prefix('Cucitura corpetto'):assign(o,seam)
for x in [-.11,-.033,.033,.11]:
    pts=[]
    for j in range(9):
        z=1.09+j*.036;xx=x*(1+.12*sin(j*pi/8));pts.append((xx,front(xx,z)-.0007,z))
    path('REV Cucitura verticale '+str(x),pts,.0011,seam,'TORSO',5)
# Main belt 60 mm tall and 6 mm beyond the waist.
o=bpy.data.objects['Cinturone'];fit(o,(-.147,-.102,1.06),(.147,.102,1.12));assign(o,leather)
for n,z in [('Bordo cintura superiore',1.119),('Bordo cintura inferiore',1.061)]:
    o=bpy.data.objects[n];fit(o,(-.148,-.103,z-.0015),(.148,.103,z+.0015));assign(o,leather)
o=bpy.data.objects['Fibbia cintura'];fit(o,(-.035,-.112,1.065),(.035,-.106,1.115));assign(o,brass)
o=bpy.data.objects['Fibbia cintura ardiglione'];fit(o,(-.002,-.114,1.066),(.002,-.110,1.103));assign(o,brass)
for o in select_prefix('Lingua cintura','Foro cintura'):
    a,b=bounds(o);shift(o,(0,-.012,1.09-(a.z+b.z)/2));assign(o,leather)
# Horizontal strap under the chest.
rings('REV Cinghia sottoseno',[(1.185,0,0,.151,.104),(1.215,0,0,.155,.109)],leather,'TORSO',40)
# Correct the direction and width of the existing lower diagonal belt.
o=bpy.data.objects['Cintura obliqua']
oldhip=[oldtor(p) for p in [(-.132,-.05,.98),(-.085,-.09,.967),(0,-.103,.948),(.09,-.09,.927),(.145,-.025,.93)]]
deform_path(o,oldhip,[(-.17,-.05,.94),(-.11,-.1,.95),(0,-.12,.97),(.11,-.1,.99),(.17,-.04,1.0)],1.6)
assign(o,leather)
for o in select_prefix('Medaille','Rose medaille'):
    transform(o,lambda p:((p.x+.029*fac)*1.32,(p.y+.125*fac)*1.1-.136,(p.z-(.954-zmin)*fac)*1.32+.99));assign(o,brass)
o=bpy.data.objects['Chaine pendentif'];fit(o,(-.013,-.135,1.01),(.013,-.129,1.055));assign(o,leather)
log('Cinghie 35 mm; cinturone 1.06-1.12; cintura inferiore sale sul lato sinistro; medaglione centrato 0.99')
finish_group(4)
