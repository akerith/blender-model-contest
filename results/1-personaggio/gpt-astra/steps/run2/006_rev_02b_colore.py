exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
for name,col,rough in [('REV Pelle',(.85,.68,.58),.68),('REV Capelli',(.10,.08,.07),.78),('REV Ciocca bianca',(.80,.80,.78),.73),('REV Labbra',(.47,.27,.22),.73),('REV Iride bruna',(.09,.045,.019),.27),('REV Ombra calda',(.065,.035,.025),.8),('REV Sclera',(.68,.65,.58),.32)]:mat(name,col,rough=rough)
# Recalculate smooth normals after the lock deformation.
for o in select_prefix('Capelli','REV Ciuffo','REV Ciocca','Testa','Palpebre'):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=True
log('Colori interpretati come RGB sRGB e convertiti in lineare per lo shader Blender')
finish_group(2)
hidden=[]
for o in objects():
    if o.get('bone')!='head':hidden.append(o);o.hide_set(True);o.hide_render=True
render_viste('rev_2_volto',viste=['fronte','tre_quarti'],risoluzione=1000)
for o in hidden:o.hide_set(False);o.hide_render=False
bpy.ops.wm.save_mainfile()
