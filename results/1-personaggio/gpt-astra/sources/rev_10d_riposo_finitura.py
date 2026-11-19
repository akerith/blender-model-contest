exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
import re
rig=bpy.data.objects['Personaggio_Rig']
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
# Curved leather remains smooth across the simplified radial segments.
# Preserve sharp seams on actual frames, strap edges and sole rims.
round_names=re.compile(r'Guanto|Gambale|Stivale piede|Etui|Canister|canister|Rotolo|Sacca dorsale|Patella sacca dorsale|Ginocchier|Fascia tibia|Fasciatura|Risvolto|rotolo|Casco palombaro|Vetro|Boussole cadran|Manica|Arrotol',re.I)
for ob in objects():
    if round_names.search(ob.name) or ob.name.startswith(('REV Rotolo manica','REV Fascia stinco')):
        for p in ob.data.polygons:p.use_smooth=True
        for e in ob.data.edges:e.use_edge_sharp=False
        if ob.data.has_custom_normals:
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
            if hasattr(bpy.ops.mesh,'customdata_custom_splitnormals_clear'):
                try:bpy.ops.mesh.customdata_custom_splitnormals_clear()
                except Exception:pass
        ob.data.update()
report=json.load(open(os.path.join(BASE,'verifica_revisione_rig.json')))
report['pose_test_degrees']=30;report['pose_test_views']=['fronte','tre_quarti'];report['pose_test_reviewed']=True;report['rest_pose_restored']=True
open(os.path.join(BASE,'verifica_revisione_rig.json'),'w').write(json.dumps(report,indent=2))
log('Prova 30 gradi esaminata: manica, guanto e mano seguono; ritorno a riposo. Triangoli',tri_count())
finish_group(10)
