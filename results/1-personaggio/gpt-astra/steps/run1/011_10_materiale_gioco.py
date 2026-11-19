exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
exec(compile(open(os.path.join(BASE,'bake_util.py')).read(),'bake_util','exec'))
normal=bake_map('personaggio_Normal','NORMAL')
orm=bake_map('personaggio_ORM','ORM')
base=bpy.data.images['personaggio_BaseColor']
ob=bpy.data.objects['Personaggio_Mesh']
m=bpy.data.materials.new('Personaggio | PBR atlas 4K');m.use_nodes=True
nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.location=(280,100)
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=base;tex.label='Colore dipinto e usura';tex.location=(-500,330);nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
tex2=nt.nodes.new('ShaderNodeTexImage');tex2.image=orm;tex2.label='R:1 G:Roughness B:Metallic';tex2.location=(-500,-20)
sep=nt.nodes.new('ShaderNodeSeparateColor');sep.location=(-180,-20);nt.links.new(tex2.outputs['Color'],sep.inputs[0]);nt.links.new(sep.outputs['Green'],p.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],p.inputs['Metallic'])
tex3=nt.nodes.new('ShaderNodeTexImage');tex3.image=normal;tex3.location=(-500,-350)
norm=nt.nodes.new('ShaderNodeNormalMap');norm.location=(-100,-280);norm.inputs['Strength'].default_value=1;nt.links.new(tex3.outputs['Color'],norm.inputs['Color']);nt.links.new(norm.outputs['Normal'],p.inputs['Normal'])
ob.data.materials.clear();ob.data.materials.append(m)
for poly in ob.data.polygons:poly.material_index=0
# The pigment is already baked into the atlas, so do not multiply it again in glTF.
for attr in list(ob.data.color_attributes):ob.data.color_attributes.remove(attr)
bpy.context.scene.cycles.samples=48
save();log('Materiale unico PBR con colore, normali e metallicita/rugosita a 4096 px')
render_viste('10_materiale_gioco',viste=['fronte','retro','tre_quarti'],risoluzione=1200)
progress('atlas_complete')
