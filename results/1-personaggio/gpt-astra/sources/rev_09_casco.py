exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
brass=mat('REV Ottone',(.62,.45,.20),metal=1,rough=.35)
edge=mat('REV Ottone giunti',(.35,.24,.10),metal=1,rough=.38)
glass=mat('REV Vetro casco',(.55,.70,.65),rough=.13)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.55;p.inputs['IOR'].default_value=1.45
canvas=mat('REV Tela rotolo',(.66,.58,.45),rough=.91)
rubber=mat('REV Tubi scuri',(.20,.15,.10),rough=.68)
leather=bpy.data.materials['REV Pelle cinture'];rope=bpy.data.materials['REV Corda canapa']
fac=bpy.context.scene['scale_geometry'];zmin=bpy.context.scene['original_zmin']
def initial(p):return Vector((p[0]*fac,p[1]*fac,(p[2]-zmin)*fac))
def helm(p):
    p=Vector((p.x/fac,p.y/fac,p.z/fac+zmin));return Vector((p.x*(.32/.232),.25+(p.y-.167)*(.30/.204),1.30+(p.z-1.307)*(.34/.28)))
prefix=('Casco','Attacco casco','Anello attacco','Flangia oblo','Vetro oblo','Oblo ','Barra ','Bullone oblo','Taglio vite oblo','Griglia laterale','Cerniera oblo','Collare casco','Valvola casco','Volantino valvola','Raggio valvola')
for ob in select_prefix(*prefix):
    transform(ob,helm);assign(ob,glass if 'vetro' in ob.name.lower() else brass);ob['bone']='chest'
ob=bpy.data.objects['Casco palombaro | calotta'];fit(ob,(-.16,.10,1.13),(.16,.40,1.47))
for v in ob.data.vertices:
    if v.co.z<1.145:v.co.z=1.145
    if v.co.y<.14:v.co.y=.14+(v.co.y-.14)*.25
assign(ob,brass)
fit(bpy.data.objects['Flangia oblo'],(-.085,.389,1.215),(.085,.414,1.385));assign(bpy.data.objects['Flangia oblo'],edge)
fit(bpy.data.objects['Vetro oblo'],(-.065,.413,1.235),(.065,.419,1.365))
for name,r,y,thick in [('Oblo guarnizione',.066,.418,.003),('Oblo bordo esterno',.085,.418,.010),('Oblo bordo interno',.067,.422,.005)]:
    ob=bpy.data.objects[name];fit(ob,(-r,y-thick/2,1.30-r),(r,y+thick/2,1.30+r));assign(ob,edge if 'guarnizione' in name else brass)
fit(bpy.data.objects['Barra verticale oblo -0.022'],(-.004,.420,1.235),(.004,.428,1.365))
fit(bpy.data.objects['Barra orizzontale oblo'],(-.065,.420,1.296),(.065,.428,1.304))
# The extra original grille bar becomes the frame's latch, retaining its geometry.
fit(bpy.data.objects['Barra verticale oblo 0.022'],(.081,.416,1.283),(.089,.424,1.317))
for j in range(12):
    a=2*pi*j/12;c=Vector((.076*cos(a),.424,1.30+.076*sin(a)))
    if j<10:
        ob=bpy.data.objects['Bullone oblo %02d'%j];fit(ob,c-Vector((.004,.002,.004)),c+Vector((.004,.002,.004)))
        slit=bpy.data.objects['Taglio vite oblo %02d'%j];fit(slit,c+Vector((-.002,.002,-.0006)),c+Vector((.002,.003,.0006)));assign(slit,edge)
    else:uv('REV Rivetto oblo '+str(j),c,(.004,.0025,.004),brass,'chest',8,4)
for s in [-1,1]:
    lo,hi=sorted([s*.146,s*.172]);fit(bpy.data.objects['Oblo laterale base '+str(s)],(lo,.205,1.255),(hi,.295,1.345))
    lo,hi=sorted([s*.173,s*.179]);fit(bpy.data.objects['Oblo laterale vetro '+str(s)],(lo,.215,1.265),(hi,.285,1.335))
    lo,hi=sorted([s*.172,s*.182]);fit(bpy.data.objects['Oblo laterale bordo '+str(s)],(lo,.207,1.257),(hi,.293,1.343))
    lo,hi=sorted([s*.18,s*.184]);fit(bpy.data.objects['Griglia laterale '+str(s)],(lo,.215,1.297),(hi,.285,1.303));fit(bpy.data.objects['Griglia laterale verticale '+str(s)],(lo,.247,1.265),(hi,.253,1.335))
ob=bpy.data.objects['Collare casco'];fit(ob,(-.15,.10,1.13),(.15,.40,1.16));assign(ob,edge)
for j in range(16):
    a=2*pi*j/16;uv('REV Rivetto collare '+str(j),(.141*cos(a),.25+.141*sin(a),1.158),(.004,.004,.003),brass,'chest',8,4)
# Reroute both original corrugated hoses, preserving their mesh and spiral ribs.
for s in [-1,1]:
    old=[];new=[]
    for j in range(37):
        t=j/36;old.append(initial((s*(.087+.052*sin(pi*t)),.177+.02*sin(2*pi*t),1.203-.19*sin(pi*t*.88))))
        if s<0:
            if t<.35:
                u=t/.35;new.append((-.12-.06*u,.25-.05*u,1.16-.16*u))
            else:
                u=(t-.35)/.65;a=pi+3*pi*u;r=.06-.044*u;new.append((-.12+r*cos(a),.20,1.00+r*sin(a)))
        else:
            # Cubic route forward beneath the upper arm, ending on the belt.
            a=Vector((.12,.25,1.16));b=Vector((.20,.23,1.08));c=Vector((.22,.06,1.02));d=Vector((.17,-.015,1.02));new.append(tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d))
    for name in ['Tubo respirazione '+str(s),'Spirale tubo '+str(s)]:
        ob=bpy.data.objects[name];deform_path(ob,old,new,1.25);assign(ob,rubber if name.startswith('Tubo') else leather);ob['bone']='chest'
    ob=bpy.data.objects['Raccordo tubo '+str(s)];c=Vector(new[0]);fit(ob,c-Vector((.018,.018,.008)),c+Vector((.018,.018,.018)));assign(ob,edge)
# Reshape the original back bag as the cylindrical canvas bedroll.
ob=bpy.data.objects['Sacca dorsale'];a,b=bounds(ob);center=(a+b)/2;half=(b-a)/2
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True);bm.to_mesh(ob.data);bm.free()
for v in ob.data.vertices:
    q=Vector([(v.co[i]-center[i])/half[i] for i in range(3)]);r=max(1,math.sqrt(q.y*q.y+q.z*q.z));v.co=(q.x*.17,.22+.055*q.y/r,1.06+.055*q.z/r)
assign(ob,canvas);ob['bone']='chest'
ob=bpy.data.objects['Patella sacca dorsale'];a,b=bounds(ob)
for v in ob.data.vertices:
    x,y,z=v.co;t=(z-a.z)/(b.z-a.z);angle=(t-.5)*2.2;v.co=(x*.34/(b.x-a.x),.22+.056*cos(angle),1.06+.056*sin(angle))
assign(ob,canvas);ob['bone']='chest'
for s in [-1,1]:
    cylinder('REV Sangle rotolo '+str(s),(s*.10-.010,.22,1.06),(s*.10+.010,.22,1.06),.058,leather,'chest',20)
    ob=bpy.data.objects['Chiusura sacca '+str(s)];fit(ob,(s*.10-.012,.276,1.040),(s*.10+.012,.284,1.080));assign(ob,leather);ob['bone']='chest'
    ob=bpy.data.objects['Bottone sacca '+str(s)];fit(ob,(s*.10-.004,.284,1.056),(s*.10+.004,.288,1.064));assign(ob,brass);ob['bone']='chest'
    pts=[(s*.055+.032*cos(2*pi*j/32),.29,1.08+.06*sin(2*pi*j/32)) for j in range(33)]
    path('REV Corda sotto casco '+str(s),pts,.0045,rope,'chest',6)
ribbon('REV Imbrago rotolo',[(-.17,.11,1.09),(-.13,.17,1.06),(0,.166,1.06),(.13,.17,1.06),(.17,.11,1.09)],.025,leather,'chest',.006)
log('Casco 0.32 x 0.30, centro 0/0.25/1.30; oblo posteriore 0.13 e croce; 12+16 rivetti; due tubi e rotolo 0.34 x 0.11')
finish_group(9)
