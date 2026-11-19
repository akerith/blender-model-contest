import bpy,os
BASE=r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro'
log('Oggetti:',[(o.name,o.type,o.hide_get(),len(o.data.bones) if o.type=='ARMATURE' else 0) for o in bpy.data.objects])
log('Elementi importati:',[(o.name,o.type) for o in imported])
log('Import disponibili:',[p.identifier for p in bpy.ops.import_scene.gltf.get_rna_type().properties])
# Restore visibility and keep only the original asset after an interrupted check.
for obj in list(bpy.data.objects):
    if obj.name not in ['Personaggio_Rig','Personaggio_Mesh','_gara_Key','_gara_Fill','_gara_Rim']:bpy.data.objects.remove(obj,do_unlink=True)
for name in ['Personaggio_Rig','Personaggio_Mesh']:
    obj=bpy.data.objects[name];obj.hide_set(False);obj.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'personaggio.blend'))
