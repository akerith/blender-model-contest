exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from collections import Counter
counts=Counter();rows=[]
for o in objects():
    o.data.calc_loop_triangles();n=len(o.data.loop_triangles)
    counts[o.get('bone','NONE')]+=n
    rows.append({'name':o.name,'bone':o.get('bone',''),'triangles':n,'materials':[m.name for m in o.data.materials if m],'original_materials':o.get('original_materials',''),'bounds':[list(x) for x in bounds(o)]})
log('Totale pre ottimizzazione',tri_count(),'per zona',dict(counts))
log('Ossa esistenti',[b.name for b in bpy.data.objects['Personaggio_Rig'].data.bones])
open(os.path.join(BASE,'rev_audit10.json'),'w',encoding='utf-8').write(json.dumps(rows,indent=2))
