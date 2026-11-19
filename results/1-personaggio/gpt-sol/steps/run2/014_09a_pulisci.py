import os, bmesh
log('Diagnosi reimportazione:', 'triangoli GLB',tri,'triangoli reimportati',imp_tri,'altezza',height)
for obj in imported:
    if obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
character.hide_set(False);rig.hide_set(False)
bm=bmesh.new();bm.from_mesh(character.data)
before_faces=len(bm.faces);before_vertices=len(bm.verts)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
bmesh.ops.dissolve_degenerate(bm,dist=.0000001,edges=list(bm.edges))
bad=[f for f in bm.faces if f.calc_area()<1e-13]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
isolated=[v for v in bm.verts if not v.link_faces]
if isolated:bmesh.ops.delete(bm,geom=isolated,context='VERTS')
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
bm.to_mesh(character.data);bm.free();character.data.update()
character.data.calc_loop_triangles();tri=len(character.data.loop_triangles)
log('Pulizia:',before_vertices,'->',len(character.data.vertices),'vertici;',tri,'triangoli espliciti; eliminate le facce di area nulla.')
assert all(len(p.vertices)==3 for p in character.data.polygons)
assert all(p.area>1e-13 for p in character.data.polygons)
assert all(any(g.weight>0 for g in v.groups) for v in character.data.vertices)
rig['triangoli']=tri
report=json.load(open(os.path.join(WORK,'verifica_personaggio.json'),encoding='utf-8'));report['triangoli']=tri;report['vertici']=len(character.data.vertices)
open(os.path.join(WORK,'verifica_personaggio.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
save()
