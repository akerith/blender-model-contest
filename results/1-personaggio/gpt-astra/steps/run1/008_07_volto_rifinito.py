exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
from mathutils.noise import noise
M=materials();skin=M['Pelle | ocra desaturata'];hair=M['Capelli | nero caldo'];hair2=M['Capelli | riflessi'];silver=M['Ciocca bianca'];silver2=M['Ciocca bianca | luce'];shadow=M['Occhi | ombra calda']
prefixes=('Testa','Naso scolpito','Ala naso','Narice','Filtro naso','Palpebra','Ciglia','Calotta capelli','Ciuffo frontale','Incisione ciuffo','Ciocca argento','Meche laterale','Basetta','Punta ribelle')
for o in list(bpy.data.objects):
    if o.name.startswith(prefixes):bpy.data.objects.remove(o,do_unlink=True)

sections=[(1.446,.018,.022,-.016),(1.46,.035,.04,-.013),(1.481,.051,.052,-.006),(1.511,.065,.061,0),(1.54,.07,.064,.003),(1.575,.068,.063,.006),(1.609,.065,.061,.009),(1.639,.051,.049,.011),(1.66,.018,.018,.011),(1.664,.002,.002,.011)]
def shape(z):
    i=0
    while i<len(sections)-2 and sections[i+1][0]<z:i+=1
    a,b=sections[i],sections[i+1];t=max(0,min(1,(z-a[0])/(b[0]-a[0])))
    # Hermite interpolation smooths the forehead and jaw silhouette.
    p0=sections[max(0,i-1)];p3=sections[min(len(sections)-1,i+2)]
    vals=[]
    for k in [1,2,3]:
        m1=(b[k]-p0[k])/(b[0]-p0[0])*(b[0]-a[0]);m2=(p3[k]-a[k])/(p3[0]-a[0])*(b[0]-a[0])
        vals.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*m2)
    return vals
def face_offset(x,z):
    cheek=.005*math.exp(-((abs(x)-.043)/.023)**2-((z-1.53)/.022)**2)
    socket=-.004*math.exp(-((abs(x)-.027)/.018)**2-((z-1.555)/.012)**2)
    brow=.004*math.exp(-((abs(x)-.026)/.021)**2-((z-1.571)/.009)**2)
    bridge=.017*math.exp(-(x/.008)**2-((z-1.548)/.023)**2)
    tip=.025*math.exp(-(x/.010)**2-((z-1.528)/.009)**2)
    alae=.007*math.exp(-((abs(x)-.009)/.006)**2-((z-1.521)/.005)**2)
    muzzle=.006*math.exp(-(x/.023)**2-((z-1.497)/.016)**2)
    chin=.003*math.exp(-(x/.023)**2-((z-1.469)/.01)**2)
    return cheek+socket+brow+bridge+tip+alae+muzzle+chin
def face_y(x,z):
    rx,ry,cy=shape(z)
    return cy-ry*math.sqrt(max(0,1-(x/rx)**2))-face_offset(x,z)
zs=[1.446,1.451,1.458,1.467,1.478,1.487,1.492,1.497,1.502,1.508,1.514,1.519,1.523,1.527,1.531,1.536,1.542,1.548,1.553,1.558,1.563,1.569,1.576,1.585,1.597,1.609,1.621,1.633,1.644,1.654,1.66,1.664]
vv=[];ff=[];N=64
for z in zs:
    rx,ry,cy=shape(z)
    for j in range(N):
        a=2*pi*j/N;x=rx*cos(a);y=cy+ry*sin(a)
        if sin(a)<0:y-=face_offset(x,z)*(-sin(a))**4
        vv.append((x,y,z))
for i in range(len(zs)-1):
    for j in range(N):a=i*N+j;b=i*N+(j+1)%N;ff.append((a,b,b+N,a+N))
ff.extend([tuple(reversed(range(N))),tuple((len(zs)-1)*N+j for j in range(N))])
mesh('Testa anatomica',vv,ff,skin,'head')

# Replace tubular eyelids by fleshy annular surfaces merging into the cheeks.
for s in [-1,1]:
    cx=s*.028;z0=1.556;vv=[];ff=[];N=32;R=4
    for i in range(R+1):
        t=i/R
        for j in range(N):
            a=2*pi*j/N
            xi=cx+.014*cos(a);zi=z0+(.0053 if sin(a)>0 else .0036)*sin(a)+s*.001*cos(a)
            xo=cx+.022*cos(a);zo=z0+.013*sin(a)+s*.001*cos(a)
            x=xi*(1-t)+xo*t;z=zi*(1-t)+zo*t
            yi=-.06-.003*abs(sin(a));yo=face_y(xo,zo)-.0005
            y=yi*(1-t)+yo*t-.0016*sin(pi*t)
            vv.append((x,y,z))
    for i in range(R):
        for j in range(N):a=i*N+j;b=i*N+(j+1)%N;ff.append((a,b,b+N,a+N))
    mesh('Palpebre integrate '+str(s),vv,ff,skin,'head')
    pp=[]
    for j in range(17):
        a=pi*j/16;pp.append((cx+.014*cos(a),-.0605-.003*sin(a),z0+.0053*sin(a)+s*.001*cos(a)))
    path('Ciglia fini '+str(s),pp,.00055,shadow,'head',5)
    # Recess the iris and reduce the bright white area.
    for prefix in ['Iride','Pupilla','Punto luce']:
        ob=bpy.data.objects[prefix+' '+str(s)]
        ob.scale.x*=.86;ob.scale.z*=.86
    uv('Narice discreta '+str(s),(s*.0085,-.076,1.519),(.0021,.0011,.001),shadow,'head',10,6)
# Remove overly sharp mouth corners; merge the lips gently into the new face surface.
for name in ['Labbro superiore','Labbro inferiore','Rima labiale']:
    ob=bpy.data.objects.get(name)
    if ob:
        for v in ob.data.vertices:
            x,y,z=v.co
            v.co.y=max(y,face_y(x,z)-.0028)

# Smooth hair ribbons with a flattened lens section, following the head normal.
def catmull(points,t):
    f=t*(len(points)-1);i=min(len(points)-2,int(f));u=f-i
    p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[i+1]);p3=Vector(points[min(len(points)-1,i+2)])
    return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
def smooth_lock(name,pts,width,material,segments=13):
    vv=[];ff=[];sides=6
    for i in range(segments):
        t=i/(segments-1);p=catmull(pts,t)
        tang=(catmull(pts,min(1,t+.01))-catmull(pts,max(0,t-.01))).normalized()
        normal=Vector((p.x/.076**2,(p.y-.01)/.074**2,(p.z-1.58)/.103**2)).normalized()
        across=tang.cross(normal).normalized();normal=across.cross(tang).normalized()
        w=width*(.55+.45*sin(pi*t))*(1-t**5)+.0003
        h=.0035*(1-t**3)+.0002
        for j in range(sides):
            a=2*pi*j/sides;vv.append(tuple(p+across*w*cos(a)+normal*h*sin(a)))
    for i in range(segments-1):
        for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;ff.append((a,b,b+sides,a+sides))
    ff.extend([tuple(reversed(range(sides))),tuple((segments-1)*sides+j for j in range(sides))])
    return mesh(name,vv,ff,material,'head')
# Rounded scalp, fully closed at the crown.
vv=[(0,.01,1.677)];ff=[];N=40;R=12
for i in range(1,R+1):
    t=i/R
    for j in range(N):
        a=2*pi*j/N;front=max(0,-sin(a));bottom=1.498+.108*front
        phi=t*math.acos((bottom-1.581)/.096)
        vv.append((.074*sin(phi)*cos(a),.01+.07*sin(phi)*sin(a),1.581+.096*cos(phi)))
for j in range(N):ff.append((0,1+j,1+(j+1)%N))
for i in range(R-1):
    for j in range(N):a=1+i*N+j;b=1+i*N+(j+1)%N;ff.append((a,b,b+N,a+N))
mesh('Capelli base continua',vv,ff,hair,'head')
for k in range(8):
    off=(k-3.5)*.004
    pts=[(.025+off,.01,1.679),(.014+off,-.033,1.673),(-.013+off,-.06,1.65),(-.042+off,-.063,1.617),(-.064+off,-.042,1.588),(-.072+off,-.02,1.575)]
    smooth_lock('Capelli frangia morbida %02d'%k,pts,.010,hair if k%3 else hair2)
for k in range(3):
    off=(k-1)*.003
    pts=[(.027+off,-.012,1.68),(.029+off,-.038,1.672),(.020+off,-.063,1.652),(.012+off,-.071,1.635),(.02+off,-.069,1.614)]
    smooth_lock('Capelli ciocca chiara %02d'%k,pts,.0055,silver if k!=1 else silver2)
for s in [-1,1]:
    for k in range(7):
        a=-.75+k*.29
        pts=[]
        for j in range(5):
            t=j/4;ang=a+.30*t
            pts.append((s*(.053+.025*sin(t*pi*.75))*cos(ang),.011+(.051+.023*sin(t*pi*.7))*sin(ang),1.663-.148*t-(k%3)*.008*t))
        smooth_lock('Capelli lato %d %02d'%(s,k),pts,.012,hair if k%4 else hair2)
    for k in range(3):
        smooth_lock('Capelli tempia %d %d'%(s,k),[(s*.061,-.03+k*.011,1.605),(s*.075,-.032+k*.012,1.573),(s*.073,-.022+k*.014,1.543),(s*.082,-.006+k*.013,1.53+k*.004)],.008,hair,11)
# A few back locks follow the nape instead of ending in aligned vertical blades.
for k in range(6):
    x=(k-2.5)*.017
    smooth_lock('Capelli nuca %d'%k,[(x,.035,1.664),(x*1.2,.069,1.63),(x*1.35,.081,1.578),(x*1.2+.006,.064,1.521),(x*.9,.052,1.493+(k%2)*.008)],.013,hair if k%3 else hair2)

# New pigment attributes; reduce noisy skin and hair micro-bump.
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.get('character') or ob.data.color_attributes.get('Pigmento'):continue
    attr=ob.data.color_attributes.new(name='Pigmento',type='FLOAT_COLOR',domain='CORNER')
    for poly in ob.data.polygons:
        m=ob.data.materials[poly.material_index];base=Vector(m.get('base_pigment',m.diffuse_color[:3]))
        for li in poly.loop_indices:
            p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;c=base*(.97+.06*noise(p*60))
            if 'Testa' in ob.name or 'Palpebre' in ob.name:
                x,y,z=p
                cheek=math.exp(-((abs(x)-.04)/.023)**2-((z-1.526)/.021)**2)*max(0,min(1,-y*18));c=c.lerp(Vector((.33,.18,.135)),cheek*.25)
                socket=math.exp(-((abs(x)-.028)/.017)**2-((z-1.56)/.013)**2)*max(0,min(1,-y*18));c*=1-.15*socket
            attr.data[li].color=(*c,1)
for m in [skin,hair,hair2]:
    for n in m.node_tree.nodes:
        if n.type=='BUMP':n.inputs['Strength'].default_value=.055;n.inputs['Distance'].default_value=.00025
        if n.type=='MIX_RGB':n.inputs[0].default_value=.25
# Reduce eye whites in the stored pigment, avoiding a startled expression.
for ob in bpy.data.objects:
    if ob.name.startswith('Occhio '):
        attr=ob.data.color_attributes.get('Pigmento')
        for d in attr.data:d.color=(.31,.30,.245,1)

# Keep the full character below the contest limit despite the improved facial topology.
if tri_count()>39200:
    candidates=[]
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and ob.get('character') and ob.get('bone')!='head' and not ob.name.startswith(('Mantello','Mantellina','Corpetto','Manica','Pantalone')):
            ob.data.calc_loop_triangles()
            if len(ob.data.loop_triangles)>180:candidates.append(ob)
    for ob in sorted(candidates,key=lambda o:len(o.data.loop_triangles),reverse=True):
        if tri_count()<38900:break
        bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Budget finale','DECIMATE');mod.ratio=.65;bpy.ops.object.modifier_apply(modifier=mod.name)
save();log('Volto continuo e capelli curvi; triangoli:',tri_count())
hidden=[]
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and ob.get('bone')!='head':hidden.append((ob,ob.hide_get(),ob.hide_render));ob.hide_set(True);ob.hide_render=True
render_viste('07_volto_rifinito',viste=['fronte','tre_quarti'],risoluzione=1000)
for ob,h,r in hidden:ob.hide_set(h);ob.hide_render=r
render_viste('07_personaggio',viste=['fronte','tre_quarti'])
save()
