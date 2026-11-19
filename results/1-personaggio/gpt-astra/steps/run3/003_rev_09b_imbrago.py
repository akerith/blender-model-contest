exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
leather=bpy.data.materials['REV Pelle cinture']
for s in [-1,1]:
    ribbon('REV Cinghia dorsale casco '+str(s),[(s*.13,-.035,1.415),(s*.13,.04,1.445),(s*.13,.105,1.435),(s*.14,.14,1.385),(s*.145,.148,1.24),(s*.14,.16,1.15)],.035,leather,'chest',.008)
for name in ['Casco palombaro | calotta','Sacca dorsale','Patella sacca dorsale']:
    ob=bpy.data.objects[name]
    for p in ob.data.polygons:p.use_smooth=True
log('Cinghie dorsali collegate dal torace al collare del casco; superfici del rotolo levigate')
finish_group(9)
