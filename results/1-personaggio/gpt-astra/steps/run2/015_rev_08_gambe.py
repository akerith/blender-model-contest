exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
pants=mat('REV Pantaloni',(.22,.19,.16),rough=.92)
boot=mat('REV Stivali',(.30,.18,.10),rough=.66)
sole=mat('REV Suole',(.12,.08,.06),rough=.78)
lace=mat('REV Lacci',(.55,.42,.28),rough=.80)
leather=bpy.data.materials['REV Guanti cuoio'];brass=bpy.data.materials['REV Ottone'];linen=bpy.data.materials['REV Lino crema']
for ob in select_prefix('Pantalone','Bacino pantaloni','Couture pantalon'):assign(ob,pants)
for s,side in [(-1,'R'),(1,'L')]:
    ob=bpy.data.objects['Pantalone '+side]
    for v in ob.data.vertices:
        x,y,z=v.co;cx=s*(.10+.03*max(0,min(1,(.90-z)/.82)));scale=1-.12*math.exp(-((z-.53)/.07)**2)
        v.co.x=cx+(x-cx)*scale
        if y>0 and .45<z<.58:v.co.y+=.005*sin((z-.45)*155)*sin(pi*(z-.45)/.13)
    for k in range(3):
        z=.51+k*.019;cx=s*.115
        path('REV Piega retro ginocchio '+side+str(k),[(cx-.045,.040,z+.008),(cx,.060,z),(cx+.045,.040,z+.005)],.0018,pants,'LEG.'+side,5)
    # Keep the original boot shaft, raise the top to 0.42 m.
    ob=bpy.data.objects['Gambale stivale '+side]
    transform(ob,lambda p:(p.x,p.y,.08+(p.z-.08)*(.34/.3006) if p.z>.08 else p.z));assign(ob,boot)
    for ob in select_prefix('Stivale piede continuo '+side):fit(ob,(s*.13-.05,-.19,.02),(s*.13+.05,.08,.108));assign(ob,boot)
    fit(bpy.data.objects['Suola '+side],(s*.13-.05,-.19,0),(s*.13+.05,.08,.02));assign(bpy.data.objects['Suola '+side],sole)
    fit(bpy.data.objects['Tacco '+side],(s*.13-.044,.022,0),(s*.13+.044,.078,.03));assign(bpy.data.objects['Tacco '+side],sole)
    for ob in select_prefix('Cucitura punta '+side):transform(ob,lambda p:(s*.13+(p.x-s*.13)*.94,-.19+(p.y+.153)*(.27/.221),p.z));assign(ob,lace)
    # Folded cuff and original ankle/top straps.
    rings('REV Risvolto stivale '+side,[(.38,s*.118,.01,.064,.055),(.392,s*.118,.01,.068,.057),(.42,s*.117,.01,.063,.055)],boot,'shin.'+side,24)
    for k,oldz in enumerate([.385,.346,.15]):
        ob=bpy.data.objects['Cinghia stivale '+side+str(oldz)];z=[.38,.35,.09][k];cx=s*(.13-.013*(z/.42));rx=.065 if z>.3 else .049;ry=.057 if z>.3 else .052
        fit(ob,(cx-rx,.01-ry,z-.01),(cx+rx,.01+ry,z+.01));assign(ob,leather)
        for item in select_prefix('Fibbia stivale '+side+str(oldz)):
            a,b=bounds(item);shift(item,(s*(.13+.035)-(a.x+b.x)/2,-.047-(a.y+b.y)/2,z-(a.z+b.z)/2));assign(item,brass)
    # Eight crosses and two rows of nine eyelets.
    for k in range(8):
        z=.10+k*.0375;cx=s*(.13-.013*(z/.42));cy=-.047
        for label,rev in [('a',False),('b',True)]:
            left=(cx-.015,cy,z if not rev else z+.0375);right=(cx+.015,cy,z+.0375 if not rev else z)
            if k<7:
                ob=bpy.data.objects['Laccio X '+label+' '+side+str(k)];a,b=bounds(ob)
                for v in ob.data.vertices:
                    t=(v.co.x-a.x)/(b.x-a.x);p=Vector(left).lerp(Vector(right),t);p.y+=.002*sin((v.index%5)*2*pi/5);v.co=p
                assign(ob,lace)
            else:path('REV Ottavo laccio '+label+side,[left,right],.002,lace,'shin.'+side,6)
        for ss in [-1,1]:
            torus('REV Occhiello '+side+str(k)+' '+str(ss),(cx+ss*.015,cy+.001,z),.0028,.0008,brass,'shin.'+side,seg=8,sides=3)
    for ss in [-1,1]:torus('REV Occhiello finale '+side+str(ss),(s*.117+ss*.015,-.046,.40),.0028,.0008,brass,'shin.'+side,seg=8,sides=3)
    # Cream wraps arranged in three overlapping rings.
    for k in range(3):
        ob=bpy.data.objects['Fascia ginocchio '+side+str(k)];cx=s*.119;z=.40+.016*k
        fit(ob,(cx-.065,-.060,z),(cx+.065,.068,z+.028));assign(ob,linen)
    for z in [.455,.545]:
        rings('REV Cinghia ginocchio '+side+str(z),[(z-.008,s*.115,0,.064,.059),(z+.008,s*.115,0,.064,.059)],leather,'shin.'+side,20)
# Both knees now carry matching round pads.
ob=bpy.data.objects['Ginocchiera cuoio destra'];fit(ob,(-.170,-.080,.445),(-.060,-.055,.555));assign(ob,leather)
ob['bone']='shin.R';copy=ob.copy();copy.data=ob.data.copy();bpy.context.collection.objects.link(copy);copy.name='REV Ginocchiera sinistra';transform(copy,lambda p:(-p.x,p.y,p.z));copy['bone']='shin.L'
for k,ob in enumerate(select_prefix('Rivetto ginocchiera')):
    a=2*pi*k/10;c=Vector((-.115+.046*cos(a),-.080,.50+.046*sin(a)));aa,bb=bounds(ob);shift(ob,c-(aa+bb)/2);assign(ob,brass)
    copy=ob.copy();copy.data=ob.data.copy();bpy.context.collection.objects.link(copy);copy.name='REV Rivetto sinistro '+str(k);transform(copy,lambda p:(-p.x,p.y,p.z));copy['bone']='shin.L'
log('Stivali: piedi 0.27 x 0.10 m, suole 0.02, tacco 0.03, gambale a 0.42; otto incroci e due ginocchiere')
finish_group(8)
