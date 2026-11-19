exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
linen=mat('REV Lino crema',(.82,.76,.64),rough=.93)
leather=mat('REV Guanti cuoio',(.26,.16,.09),rough=.66)
dark=mat('REV Cinghie guanti',(.20,.12,.07),rough=.68)
brass=mat('REV Ottone',(.62,.45,.20),metal=1,rough=.35)
green=mat('REV Quadrante verde',(.25,.55,.35),rough=.18)
handpaths={}
for s,side in [(-1,'R'),(1,'L')]:
    shoulder=Vector((s*.19,0,1.40));elbow=Vector((s*.38,0,1.18));wrist=Vector((s*.54,0,.99));axis=(wrist-elbow).normalized()
    # Original sleeve: same 160 vertices and all original faces, reshaped ring by ring.
    ob=bpy.data.objects['Manica '+side]
    centers=[Vector((s*x,0,z)) for x,z in [(.165,1.408),(.19,1.40),(.225,1.36),(.266,1.313),(.305,1.267),(.342,1.224),(.364,1.198),(.38,1.18)]]
    radii=[.05,.052,.056,.057,.055,.056,.054,.047]
    assert len(ob.data.vertices)==160
    for v in ob.data.vertices:
        k=v.index//20;a=2*pi*(v.index%20)/20;tang=(centers[min(k+1,7)]-centers[max(0,k-1)]).normalized();u=tang.cross(Vector((0,1,0))).normalized()
        v.co=centers[k]+u*cos(a)*radii[k]+Vector((0,sin(a)*radii[k]*.95,0))
    assign(ob,linen)
    for ob in select_prefix('Piega manica '+side):assign(ob,linen)
    for k,t in enumerate([.75,.85,.95]):
        c=shoulder.lerp(elbow,t);ob=torus('REV Risvolto manica '+side+str(k),c,.048,.007,linen,'ARM.'+side,rot=(0,0,0),seg=20,sides=6)
        ob.rotation_euler=(elbow-shoulder).to_track_quat('Z','Y').to_euler()
    # Original leather gauntlet rescaled in its local length and cross-section.
    ob=bpy.data.objects['Guanto avambraccio '+side];pp=coords(ob);ts=[(p-elbow).dot(axis) for p in pp];lo,hi=min(ts),max(ts)
    for v in ob.data.vertices:
        p=v.co;along=(p-elbow).dot(axis);t=(along-lo)/(hi-lo);off=p-elbow-axis*along
        oldradius=.049*(1-t)+.030*t;newradius=.0475*(1-t)+.0375*t
        v.co=elbow+axis*(.04+t*((wrist-elbow).length-.04))+off*(newradius/oldradius)
    assign(ob,leather)
    c=elbow+axis*.043;ob=torus('REV Bordo svasato guanto '+side,c,.0475,.0075,leather,'forearm.'+side,rot=(0,0,0),seg=20,sides=6);ob.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
    for k,dist in enumerate([.048,.138,.235]):
        ob=bpy.data.objects['Cinghia guanto '+side+str(k)];pp=coords(ob);oc=sum(pp,Vector())/len(pp)
        aa=[(p-oc).dot(axis) for p in pp];al,ah=min(aa),max(aa);maxr=max(((p-oc)-axis*(p-oc).dot(axis)).length for p in pp);rad=[.052,.046,.040][k]
        for v in ob.data.vertices:
            off=v.co-oc;a=off.dot(axis);r=off-axis*a;v.co=elbow+axis*dist+axis*((a-(al+ah)/2)*.015/(ah-al))+r*(rad/maxr)
        assign(ob,dark);c=elbow+axis*dist
        frame_buckle('REV Fibbia guanto '+side+str(k),(c.x,-rad-.002,c.z),.015,.014,brass,'forearm.'+side,rad=.0015)
    # Add loops to the existing palm and fingers; no hand is deleted or rebuilt.
    direction=Vector((s*.643,0,-.766)).normalized();normal=Vector((-s*.383,.866,-.321)).normalized();across=direction.cross(normal).normalized()
    oldacross=Vector((s*.766,0,.643)).normalized()
    ob=bpy.data.objects['Palmo guanto '+side]
    pp=coords(ob);oldcenter=sum(pp,Vector())/len(pp);projs=[[ (p-oldcenter).dot(a) for p in pp] for a in [direction,oldacross,Vector((0,1,0))]];ranges=[(min(q),max(q)) for q in projs]
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True);bm.to_mesh(ob.data);bm.free()
    center=wrist+direction*.039
    for v in ob.data.vertices:
        p=v.co-oldcenter;vals=[]
        for a,(low,high) in zip([direction,oldacross,Vector((0,1,0))],ranges):vals.append(max(-1,min(1,2*(p.dot(a)-low)/(high-low)-1)))
        vals=[math.copysign(abs(t)**.55,t) for t in vals]
        v.co=center+direction*(vals[0]*.044)+across*(vals[1]*.040)+normal*(vals[2]*.015)
    assign(ob,leather)
    for k,length in enumerate([.075,.085,.080,.065]):
        ob=bpy.data.objects['Dito %d %s'%(k+1,side)];pp=coords(ob);oldcenter=sum(pp,Vector())/len(pp);ts=[p.dot(direction) for p in pp];tmin,tmax=min(ts),max(ts)
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True);bm.to_mesh(ob.data);bm.free()
        spread=math.radians((k-1.5)*8);forward=direction*cos(spread)+across*sin(spread);base=wrist+direction*.076+across*((k-1.5)*.019)
        pathpoints=[base]
        for j in range(3):pathpoints.append(pathpoints[-1]+(forward*cos(math.radians(j*10))+normal*sin(math.radians(j*10)))*(length/3))
        handpaths[(side,k)]=pathpoints
        for v in ob.data.vertices:
            p=v.co;t=max(0,min(1,(p.dot(direction)-tmin)/(tmax-tmin)));offset=p-oldcenter;radial=offset-direction*offset.dot(direction);angle=math.atan2(radial.y,radial.dot(oldacross));rr=.009*(1-.40*t)
            f=t*3;j=min(2,int(f));c=pathpoints[j].lerp(pathpoints[j+1],f-j)
            v.co=c+across*cos(angle)*rr+normal*sin(angle)*rr
        assign(ob,leather);ob['finger_index']=k
    # Original thumb, two bent phalanges plus its base.
    ob=bpy.data.objects['Pollice '+side];pp=coords(ob);oc=sum(pp,Vector())/len(pp);ax=(pp[-1]-pp[0]).normalized();ts=[p.dot(direction) for p in pp];low,high=min(ts),max(ts)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True);bm.to_mesh(ob.data);bm.free()
    base=wrist+direction*.019-across*.029;td=(direction*cos(.70)-across*sin(.70)).normalized();thumbpts=[base,base+td*.025,base+td*.047+normal*.005,base+td*.061+normal*.014]
    for v in ob.data.vertices:
        p=v.co;t=max(0,min(1,(p.dot(direction)-low)/(high-low)));off=p-oc;angle=math.atan2(off.y,off.dot(oldacross));f=t*3;j=min(2,int(f));c=thumbpts[j].lerp(thumbpts[j+1],f-j);r=.011*(1-.5*t)
        v.co=c+across*cos(angle)*r+normal*sin(angle)*r
    assign(ob,leather);handpaths[(side,4)]=thumbpts
    # Existing knuckle strips moved onto the back of the reshaped palm.
    for k,ob in enumerate(select_prefix('Nocca guanto '+side)):
        a,b=bounds(ob);c=wrist+direction*.065+across*((k-1)*.019)-normal*.015
        shift(ob,c-(a+b)/2);assign(ob,dark)
# Gauge just above the left wrist, with all original dial details kept together.
for ob in select_prefix('Boussole','Aiguille boussole','Graduation boussole'):
    transform(ob,lambda p:(.505+(p.x-.43556)*.83,-.044+(p.y+.039)*.79,1.032+(p.z-1.11497)*.83))
    if ob.name=='Boussole cadran':assign(ob,green)
    elif ob.name.startswith('Boussole'):assign(ob,brass)
    ob['bone']='forearm.L'
for ob in select_prefix('Dito ','Pollice ','Palmo guanto'):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    for p in ob.data.polygons:p.use_smooth=True
open(os.path.join(BASE,'rev_dita.json'),'w').write(json.dumps({str(k):[list(p) for p in pp] for k,pp in handpaths.items()},indent=2))
log('Mani conservate e suddivise; dita 3 segmenti, pollice base piu 2 segmenti; nessuna parte eliminata')
finish_group(5)
hidden=[]
for ob in objects():
    if not (ob.get('bone') in ['hand.L','forearm.L']):hidden.append(ob);ob.hide_set(True);ob.hide_render=True
render_viste('rev_5_mano',viste=['fronte','tre_quarti'])
for ob in hidden:ob.hide_set(False);ob.hide_render=False
bpy.ops.wm.save_mainfile()
