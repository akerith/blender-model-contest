import os
character=bpy.data.objects['Esploratrice_mesh'];rig=bpy.data.objects['Esploratrice_Rig']
log('Normali:',[(round(p.normal.length,4),p.use_smooth) for p in list(character.data.polygons)[:5]])
log('Colori:',[(c.name,c.domain,c.data_type,len(c.data)) for c in character.data.color_attributes])
for slot in character.material_slots:
    m=slot.material;bs=m.node_tree.nodes.get('Principled BSDF')
    base=bs.inputs['Base Color']
    log(m.name,'colore da',[(l.from_node.type,l.from_socket.name) for l in base.links])
render_viste('09b_originale',viste=['fronte'])
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=os.path.join(WORK,'personaggio.glb'))
imported=[o for o in bpy.data.objects if o not in before]
meshes=[o for o in imported if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
character.hide_set(True);rig.hide_set(True)
for obj in meshes:
    for m in obj.data.materials:
        bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for link in list(bs.inputs['Normal'].links):m.node_tree.links.remove(link)
render_viste('09b_senza_normal_map',viste=['fronte'])
for obj in meshes:
    for m in obj.data.materials:
        bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
        bs.inputs['Base Color'].default_value=(.3,.3,.3,1)
render_viste('09b_senza_colori',viste=['fronte'])
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
character.hide_set(False);rig.hide_set(False)
