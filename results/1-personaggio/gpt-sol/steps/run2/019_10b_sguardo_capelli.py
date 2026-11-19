import os,bmesh
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'))
factor=report['normalizzazione']['fattore'];minz=report['normalizzazione']['min_z_originale']
def P(p):return Vector((p[0]*factor,p[1]*factor,(p[2]-minz)*factor))
def Z(z):return (z-minz)*factor

# Increase the almond opening slightly so the iris sits fully inside the eyelids.
bm=bmesh.new();bm.from_mesh(character.data);seen=set();changed=0
for start in bm.verts:
    if start in seen:continue
    group=[];stack=[start];seen.add(start)
    while stack:
        v=stack.pop();group.append(v)
        for e in v.link_edges:
            q=e.other_vert(v)
            if q not in seen:seen.add(q);stack.append(q)
    mn=Vector([min(v.co[k] for v in group) for k in range(3)]);mx=Vector([max(v.co[k] for v in group) for k in range(3)])
    mats={character.data.materials[f.material_index].name for v in group for f in v.link_faces}
    if mn.z>Z(1.580) and mx.z<Z(1.603) and mx.y<-.043*factor and .025*factor<mx.x-mn.x<.050*factor and mats.issubset({'01_Pelle','04_Avorio_occhi','07_Capelli_carbone'}):
        for v in group:v.co.z=Z(1.592)+(v.co.z-Z(1.592))*1.32
        changed+=1
bm.normal_update();bm.to_mesh(character.data);bm.free();character.data.update()
log('Isole palpebre e sclera rifinite:',changed)

# A few curled, tapered wisps soften the hair silhouette around the ears.
new=[]
for s in [-1,1]:
    for j in range(3):
        dy=j*.022
        pts=[(s*.059,-.018+dy,1.676-j*.010),(s*.080,-.036+dy,1.654-j*.014),(s*.086,-.047+dy,1.625-j*.016),(s*.096,-.040+dy,1.613-j*.017),(s*.099,-.027+dy,1.623-j*.018)]
        pts=smooth_path(pts,3)
        sec=[]
        for i,p in enumerate(pts):
            t=i/(len(pts)-1);w=.0095*sin(pi*(.12+.87*t))
            sec.append((tuple(P(p)),max(.0006,w*.33),max(.0007,w)))
        o=loft('Riccio_tempia_'+str(s)+str(j),sec,'hair','head',sides=8,axis='PATH')
        ca=o.data.color_attributes.new(name='Carnagione',type='FLOAT_COLOR',domain='CORNER')
        for d in ca.data:d.color=(1,1,1,1)
        new.append(o)
bpy.ops.object.select_all(action='DESELECT');character.select_set(True)
for o in new:o.select_set(True)
bpy.context.view_layer.objects.active=character;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(character.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.normal_update();bm.to_mesh(character.data);bm.free();character.data.update()
character.data.calc_loop_triangles();tri=len(character.data.loop_triangles);assert tri<=40000
rig['triangoli']=tri;report['triangoli']=tri;report['vertici']=len(character.data.vertices)
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
save()
portrait('10b_viso',scale=.35,center=(0,0,Z(1.59)),loc=(.04,-1.5,Z(1.62)))
render_viste('10b_rifinitura',viste=['fronte','tre_quarti'])
