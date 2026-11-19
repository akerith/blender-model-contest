import os,bmesh
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
factor=report['normalizzazione']['fattore'];minz=report['normalizzazione']['min_z_originale']
def P(p):return Vector((p[0]*factor,p[1]*factor,(p[2]-minz)*factor))

# Find only the old shoulder capelet islands; do not alter the main cape or collar.
bm=bmesh.new();bm.from_mesh(character.data);bm.verts.ensure_lookup_table()
seen=set();remove=[]
for start in bm.verts:
    if start in seen:continue
    group=[];stack=[start];seen.add(start)
    while stack:
        v=stack.pop();group.append(v)
        for e in v.link_edges:
            q=e.other_vert(v)
            if q not in seen:seen.add(q);stack.append(q)
    mn=Vector([min(v.co[k] for v in group) for k in range(3)]);mx=Vector([max(v.co[k] for v in group) for k in range(3)])
    materials={character.data.materials[f.material_index].name for v in group for f in v.link_faces}
    zlo=(1.275-minz)*factor;zhi=(1.417-minz)*factor
    if mn.z>zlo and mx.z<zhi and max(abs(mn.x),abs(mx.x))>.205*factor and mx.y<.015*factor and materials.issubset({'10_Mantello_verde','11_Tessuto_consumato'}):
        remove.extend(group)
log('Vertici rimossi dalle vecchie mantelline:',len(remove))
if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
bm.to_mesh(character.data);bm.free();character.data.update()

new=[]
for s in [-1,1]:
    side='L' if s==1 else 'R';verts=[];uv=[];nu=13;nv=6
    for i in range(nu):
        u=i/(nu-1)
        x=.052+.184*u
        # High attachment at collar, then a curved drape over the upper arm.
        upper=1.409-.054*u-.052*u*u
        lower=1.366-.025*u-.049*u*u+.004*sin(u*20)
        for j in range(nv):
            v=j/(nv-1)
            z=upper*(1-v)+lower*v+.004*sin(u*12+v*4)*sin(v*pi)
            y=-.047-.026*sin(u*pi)-.033*sin(v*pi/2)+.027*u*u
            xw=x+.004*sin(v*pi)*sin(u*8)
            verts.append(tuple(P((s*xw,y,z))));uv.append((.15+.68*u,.72+.20*(1-v)))
    faces=[]
    for i in range(nu-1):
        for j in range(nv-1):
            if i==nu-3 and j==nv-2:continue
            faces.append((i*nv+j,(i+1)*nv+j,(i+1)*nv+j+1,i*nv+j+1))
    o=mesh('Mantellina_morbida_'+side,verts,faces,'cape',uv=uv);new.append(o)
    o.vertex_groups.new(name='chest');o.vertex_groups.new(name='upper_arm.'+side)
    for v in o.data.vertices:
        x=abs(v.co.x)/factor;t=max(0,min(.65,(x-.13)/.15))
        o.vertex_groups['chest'].add([v.index],1-t,'REPLACE')
        if t:o.vertex_groups['upper_arm.'+side].add([v.index],t,'REPLACE')
    # Fine bound edge along the front, with a couple of frayed fibers.
    pts=[verts[i*nv+nv-1] for i in range(nu)]
    edge=tube('Orlo_mantellina_morbida_'+side,pts,.0011,'capeEdge','chest',5);new.append(edge)
    for j in [8,11]:
        p=Vector(pts[j]);o=tube('Filo_spalla_'+side+str(j),[tuple(p),tuple(p+P((0,0,minz-.006)))],.0006,'capeEdge','chest',4);new.append(o)
    for o in new:
        if not o.data.color_attributes.get('Carnagione'):
            ca=o.data.color_attributes.new(name='Carnagione',type='FLOAT_COLOR',domain='CORNER')
            for d in ca.data:d.color=(1,1,1,1)

bpy.ops.object.select_all(action='DESELECT');character.select_set(True)
for o in new:o.select_set(True)
bpy.context.view_layer.objects.active=character;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(character.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(character.data);bm.free();character.data.update()
character.data.calc_loop_triangles();tri=len(character.data.loop_triangles);assert tri<40000
rig['triangoli']=tri
report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'));report['triangoli']=tri;report['vertici']=len(character.data.vertices)
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
save()
render_viste('10_spalle',viste=['fronte','tre_quarti'])
portrait('10_dettaglio_spalle',scale=.67,center=(0,0,1.38),loc=(.2,-1.5,1.47))
