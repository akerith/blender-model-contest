exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
exec(compile(open(os.path.join(BASE,'bake_util.py')).read(),'bake_util','exec'))
rig=bpy.data.objects['Personaggio_Rig']
# Correct the finger labels to match their spatial order next to the thumb.
rename={}
for side in ['Left','Right']:
    for old,new in [('Little','Index'),('Ring','Middle'),('Middle','Ring'),('Index','Little')]:
        for part in ['Proximal','Intermediate','Distal']:rename[side+old+part]=side+new+part
objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('character')]
for ob in objects:
    for g in ob.vertex_groups:
        if g.name in rename:g.name='temp_'+g.name
for old in rename:rig.data.bones[old].name='temp_'+old
for ob in objects:
    for g in ob.vertex_groups:
        if g.name.startswith('temp_'):g.name=rename[g.name[5:]]
for old,new in rename.items():rig.data.bones['temp_'+old].name=new

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'personaggio_sorgente.blend'))
# One skinned game mesh, one shared UV atlas, no extra render-only geometry.
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Corpetto sagomato'];bpy.ops.object.join()
ob=bpy.context.object;ob.name='Personaggio_Mesh';ob['character']=True;ob.parent=rig
# Triangulate before baking to keep tangent-space normals consistent after export.
mod=ob.modifiers.new('Triangoli finali','TRIANGULATE');mod.quad_method='BEAUTY';mod.ngon_method='BEAUTY';bpy.ops.object.modifier_apply(modifier=mod.name)
progress('UV_unwrap')
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.002,area_weight=.15)
bpy.ops.object.mode_set(mode='OBJECT');ob.data.uv_layers.active.name='UV_Atlas'
save()
bake_map('personaggio_BaseColor','COLOR')
save();log('UV e colore 4096 preparati. Triangoli:',tri_count())
progress('color_complete')
