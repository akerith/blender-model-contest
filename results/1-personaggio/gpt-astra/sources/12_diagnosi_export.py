import bpy, os, json
BASE=r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro'
ob=bpy.data.objects['Personaggio_Mesh'];rig=bpy.data.objects['Personaggio_Rig']
log('Parent',ob.parent.name if ob.parent else None,'modificatori',[(m.name,m.type,getattr(m,'object',None).name if getattr(m,'object',None) else None,m.show_viewport,m.show_render) for m in ob.modifiers])
log('Gruppi',len(ob.vertex_groups),[g.name for g in ob.vertex_groups][:20])
log('Vertici senza pesi',sum(not v.groups for v in ob.data.vertices),'ossa',len(rig.data.bones))
log('Selezione',[(o.name,o.type,o.select_get(),o.hide_get()) for o in bpy.context.scene.objects])
data=open(os.path.join(BASE,'personaggio.glb'),'rb').read();import struct
jn=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+jn])
log('GLB mesh attributes',[p['attributes'] for m in doc['meshes'] for p in m['primitives']]);log('GLB skins',doc.get('skins',[]));log('Nodes',[(n.get('name'),n.get('mesh'),n.get('skin')) for n in doc.get('nodes',[])][:12])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'personaggio.blend'))
