exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
rig=bpy.data.objects['Personaggio_Rig']
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
for ob in objects():ob.hide_set(False);ob.hide_render=False
rig.hide_set(False)
bpy.context.view_layer.update()
rows=[]
for ob in sorted(objects(),key=lambda o:o.name):
    ob.data.calc_loop_triangles();rows.append({'name':ob.name,'triangles':len(ob.data.loop_triangles),'bounds':[list(p) for p in bounds(ob)]})
points=[p for ob in objects() for p in coords(ob)]
assert tri_count()<=40000
height=max(p.z for p in points)-min(p.z for p in points)
assert abs(height-1.70)<.002
for ob in objects():
    assert ob.parent==rig
    assert len(ob.data.materials)>0
    assert all(any(g.weight>.000001 for g in v.groups) for v in ob.data.vertices)
bpy.context.scene.cycles.samples=48
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.overlay.show_overlays=False;space.shading.type='MATERIAL'
            space.region_3d.view_location=(0,0,.85);space.region_3d.view_distance=2.8
            space.region_3d.view_rotation=Vector((-1.6,3.4,-1.1)).to_track_quat('-Z','Y')
            space.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_mainfile()
render_viste('finale_revisione_personaggio',risoluzione=1536)
report={'contestant':'gpt-astra','resume_start':'2026-11-19 09:55 Europe/Rome','resume_deadline':'2026-11-19 10:28 Europe/Rome','finished':datetime.datetime.now().isoformat(timespec='seconds'),'triangles':tri_count(),'bones':len(rig.data.bones),'height_m':height,'mesh_objects':len(objects()),'rest_pose':True,'all_meshes_bound':True,'all_meshes_materials':True,'objects':rows}
open(os.path.join(BASE,'verifica_revisione_finale.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
log('CONSEGNA', {k:v for k,v in report.items() if k!='objects'})
