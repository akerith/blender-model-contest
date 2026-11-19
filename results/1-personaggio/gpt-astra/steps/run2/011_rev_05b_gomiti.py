exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
skin=bpy.data.materials['REV Pelle'];leather=bpy.data.materials['REV Guanti cuoio']
for s,side in [(-1,'R'),(1,'L')]:
    elbow=Vector((s*.38,0,1.18));wrist=Vector((s*.54,0,.99));d=(wrist-elbow).normalized()
    tube('REV Avambraccio scoperto '+side,[elbow-d*.015,elbow+d*.025,elbow+d*.065],[.038,.039,.037],skin,'forearm.'+side,20)
    # Restore a round cross-section to the existing flattened thumb.
    ob=bpy.data.objects['Pollice '+side]
    direction=Vector((s*.643,0,-.766)).normalized();normal=Vector((-s*.383,.866,-.321)).normalized();across=direction.cross(normal).normalized()
    td=(direction*cos(.70)-across*sin(.70)).normalized();tc=td.cross(normal).normalized()
    pp=coords(ob);origin=sum(pp,Vector())/len(pp);axes=[td,tc,normal];vals=[[(p-origin).dot(ax) for p in pp] for ax in axes];limits=[(min(q),max(q)) for q in vals]
    base=wrist+direction*.020-across*.031
    for v in ob.data.vertices:
        p=v.co-origin;t=max(0,min(1,(p.dot(td)-limits[0][0])/(limits[0][1]-limits[0][0])))
        a=2*(p.dot(tc)-limits[1][0])/(limits[1][1]-limits[1][0])-1;b=2*(p.dot(normal)-limits[2][0])/(limits[2][1]-limits[2][0])-1
        v.co=base+td*(.061*t)+normal*(.010*t*t)+tc*(.012*a*(1-.3*t))+normal*(.011*b*(1-.3*t))
    for p in ob.data.polygons:p.use_smooth=True
log('Aggiunta la porzione anatomica scoperta tra manica e guanto; chiusa la discontinuita ai gomiti')
finish_group(5)
