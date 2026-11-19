exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
teal=bpy.data.materials['REV Mantello teal'];nt=teal.node_tree;principled=nt.nodes.get('Principled BSDF');output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
cape=[o for o in objects() if any(m==teal for m in o.data.materials)]
assert cape
backup=teal.copy();backup.name='REV Mantello sorgente procedurale';backup.use_fake_user=True
bpy.ops.object.select_all(action='DESELECT')
for ob in cape:
    ob.select_set(True)
    for uv in list(ob.data.uv_layers):ob.data.uv_layers.remove(uv)
    ob.data.uv_layers.new(name='REV_UV')
bpy.context.view_layer.objects.active=cape[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.012,area_weight=.5,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
texdir=os.path.join(BASE,'texture');os.makedirs(texdir,exist_ok=True)
uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map='REV_UV'
target=nt.nodes.new('ShaderNodeTexImage');target.name='REV Texture cotta';nt.links.new(uvnode.outputs['UV'],target.inputs['Vector'])
for n in nt.nodes:n.select=False
target.select=True;nt.nodes.active=target
color_image=bpy.data.images.new('REV Mantello BaseColor',width=2048,height=2048,alpha=False)
color_image.filepath_raw=os.path.join(texdir,'rev_mantello_BaseColor.png');color_image.file_format='PNG';target.image=color_image
source=principled.inputs['Base Color'].links[0].from_socket
emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(source,emit.inputs['Color']);nt.links.new(emit.outputs[0],output.inputs['Surface'])
sc=bpy.context.scene;sc.render.bake.use_selected_to_active=False;sc.render.bake.use_clear=False;old_samples=sc.cycles.samples;sc.cycles.samples=1
bpy.ops.object.bake(type='EMIT',margin=12,use_clear=False)
color_image.save();color_image.pack()
nt.links.new(principled.outputs['BSDF'],output.inputs['Surface'])
normal_image=bpy.data.images.new('REV Mantello Normal',width=2048,height=2048,alpha=False)
normal_image.colorspace_settings.name='Non-Color';normal_image.filepath_raw=os.path.join(texdir,'rev_mantello_Normal.png');normal_image.file_format='PNG';target.image=normal_image
bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT',margin=12,use_clear=False)
normal_image.save();normal_image.pack()
target.image=color_image;nt.links.new(target.outputs['Color'],principled.inputs['Base Color'])
normal_tex=nt.nodes.new('ShaderNodeTexImage');normal_tex.image=normal_image;nt.links.new(uvnode.outputs['UV'],normal_tex.inputs['Vector'])
normal_map=nt.nodes.new('ShaderNodeNormalMap');normal_map.uv_map='REV_UV';nt.links.new(normal_tex.outputs['Color'],normal_map.inputs['Color']);nt.links.new(normal_map.outputs['Normal'],principled.inputs['Normal'])
nt.nodes.remove(emit);sc.cycles.samples=old_samples
for ob in cape:ob.data.uv_layers[0].active_render=True
log('Bake mantello colore e normale 2048, oggetti',len(cape),'immagini impacchettate; materiale procedurale conservato come copia')
bpy.ops.wm.save_mainfile()
render_viste('rev_10',viste=['fronte','destra','retro','sinistra','tre_quarti','alto'])
