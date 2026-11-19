exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
skin=mat('REV Pelle',(.85,.68,.58),rough=.68)
hairmat=mat('REV Capelli',(.10,.08,.07),rough=.78)
silver=mat('REV Ciocca bianca',(.80,.80,.78),rough=.73)
lip=mat('REV Labbra',(.47,.27,.22),rough=.73)
iris=mat('REV Iride bruna',(.09,.045,.019),rough=.27)
shadow=mat('REV Ombra calda',(.065,.035,.025),rough=.8)
white=mat('REV Sclera',(.68,.65,.58),rough=.32)
def face_z(z):
    pts=[(1.475,1.475),(1.51755,1.505),(1.553,1.540),(1.585,1.585),(1.66,1.66)]
    for (a,b),(c,d) in zip(pts,pts[1:]):
        if a<=z<=c:return b+(d-b)*(z-a)/(c-a)
    return z
for o in objects():
    if o.get('bone')!='head' or o.name.startswith('Capelli'):continue
    transform(o,lambda p:(p.x,p.y*.93,face_z(p.z)))
    if o.name.startswith(('Testa','Orecchio','Elice','Palpebre')):assign(o,skin)
    elif o.name.startswith('Iride'):assign(o,iris)
    elif o.name.startswith('Occhio'):assign(o,white)
    elif o.name.startswith('Labbro'):assign(o,lip)
    elif not o.name.startswith('Punto luce'):assign(o,shadow)
    if o.name.startswith(('Occhio','Iride','Pupilla','Punto luce','Ciglia','Palpebre','Sopracciglio')):
        s=-1 if o.name.endswith('-1') else 1;shift(o,(s*.00254,0,0))
head=bpy.data.objects['Testa anatomica']
# Reduce only the nose's projection; retain all facial topology.
for v in head.data.vertices:
    x,y,z=v.co
    v.co.y+=.011*math.exp(-(x/.013)**2-((z-1.542)/.016)**2)*max(0,min(1,-y*15))
tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
def surf(x,z):
    hit=tree.ray_cast(Vector((x,-.3,z)),Vector((0,1,0)))
    return hit[0].y if hit[0] else -.07
for o in select_prefix('Sopracciglio'):
    s=-1 if o.name.endswith('-1') else 1
    for v in o.data.vertices:
        x=v.co.x;t=max(0,min(1,(abs(x)-.014)/.037));z=1.595+.004*t
        v.co.z=z+(.0013 if v.index%2 else -.0013);v.co.y=surf(x,v.co.z)-.0012
    assign(o,hairmat)
for o in select_prefix('Labbro','Rima labiale'):
    transform(o,lambda p:(p.x*1.16,p.y,p.z))
    for v in o.data.vertices:v.co.y=surf(v.co.x,v.co.z)-(.0012 if o.name=='Rima labiale' else .0015)
# Thicker, irregular wavy locks: deform the original clumps, including their tips.
locks=select_prefix('Capelli')
for oi,o in enumerate(locks):
    assign(o,silver if 'chiara' in o.name else hairmat)
    if 'base continua' in o.name:
        transform(o,lambda p:(p.x*1.08,p.y*1.04,p.z))
        continue
    if 'chiara' in o.name:
        transform(o,lambda p:(-p.x*1.13-.005,p.y,p.z-.001))
        continue
    for v in o.data.vertices:
        x,y,z=v.co;t=max(0,min(1,(1.685-z)/.18))
        phase=oi*.92
        v.co.x=x*(1.06+.07*sin(t*pi))+(.0045*sin(t*9+phase)*sin(pi*t))
        v.co.y=y+.005*sin(t*10+phase)*sin(pi*t)
        if 'frangia' not in o.name:v.co.z-=.015*t+.004*sin(phase)*t
    # Inflate each original six-sided cross section, keep buried roots small.
    if len(o.data.vertices)%6==0:
        for k in range(len(o.data.vertices)//6):
            vs=list(o.data.vertices)[k*6:(k+1)*6];c=sum((v.co for v in vs),Vector())/6
            for v in vs:v.co=c+(v.co-c)*(1.18 if k>1 else 1.0)
# Add short flyaways and a continuation of the white group over the crown.
for s in [-1,1]:
    for k in range(5):
        z=1.62-.020*k;y=.009+.013*k
        tube('REV Ciuffo mosso %d %d'%(s,k),[(s*.068,y,z+.038),(s*.088,y-.006,z+.013),(s*(.092+(k%2)*.006),y+.007,z+.02),(s*.087,y+.015,z-.007)],[(.012,.005),(.014,.006),(.008,.004),(.0008,.0005)],hairmat,'head',6)
for k in range(2):
    x=-.026-k*.010
    tube('REV Ciocca bianca corona '+str(k),[(x,-.035,1.681),(x-.007,.0,1.696-k*.002),(x-.012,.038,1.678),(x-.017,.071,1.65)],[(.009,.004),(.009,.004),(.008,.004),(.001,.001)],silver,'head',8)
for o in select_prefix('Capelli','REV Ciuffo','REV Ciocca'):
    for v in o.data.vertices:v.co.z=min(1.70,v.co.z)
fit(bpy.data.objects['Collo'],(-.055,-.055,1.45),(.055,.055,1.49));assign(bpy.data.objects['Collo'],skin)
log('Ciocche separate',len(select_prefix('Capelli'))-1+12,'occhi centro X +/-0.0325 Z 1.585, bocca Z 1.505')
finish_group(2)
# Additional close-up, same fixed cameras, only temporary visibility changes.
hidden=[]
for o in objects():
    if o.get('bone')!='head':hidden.append(o);o.hide_set(True);o.hide_render=True
render_viste('rev_2_volto',viste=['fronte','tre_quarti'],risoluzione=1000)
for o in hidden:o.hide_set(False);o.hide_render=False
bpy.ops.wm.save_mainfile()
