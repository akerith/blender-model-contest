import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
setup_materials()
counts=[]
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o.get('personaggio'):
        o.data.calc_loop_triangles();counts.append((len(o.data.loop_triangles),o.name))
log('Oggetti piu densi:',sorted(counts,reverse=True)[:25])

# Preserve deformation rings and silhouette on the principal meshes; simplify
# the numerous round trims and hardware more aggressively.
for o in list(bpy.context.scene.objects):
    if o.type!='MESH' or not o.get('personaggio'):continue
    o.data.calc_loop_triangles();n=len(o.data.loop_triangles)
    if o.name.startswith('Mantello_'):ratio=.80
    elif o.name=='Viso':ratio=.77
    elif o.name.startswith(('Meche_','Vague_','Capelli_')):ratio=.61
    elif o.name.startswith(('Manica_','Giacca_','Pantalone_','Guanto_palmo','Dito_','Pollice_')):ratio=.85
    elif o.name.startswith(('Occhio_','Iride_','Pupilla_','Riflesso_','Palpebra_','Labbro_','Naso','Narice_')):ratio=.7
    elif n<40:continue
    else:ratio=.54
    if n<80:ratio=max(.7,ratio)
    bpy.context.view_layer.objects.active=o
    de=o.modifiers.new('Budget_gioco','DECIMATE');de.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=de.name)

# Make the hips and upper thighs a little fuller and less mannequin-like.
for o in bpy.context.scene.objects:
    if o.name.startswith('Pantalone_'):
        s=1 if o.name.endswith('L') else -1
        for v in o.data.vertices:
            f=1+.10*exp(-((v.co.z-.85)/.13)**2)
            v.co.x=s*.108+(v.co.x-s*.108)*f
            v.co.y=.008+(v.co.y-.008)*f

save()
render_viste('04_budget',viste=['fronte','tre_quarti'])
