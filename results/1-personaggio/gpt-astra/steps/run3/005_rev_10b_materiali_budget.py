exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
import re
from collections import Counter
brass=mat('REV Ottone',(.62,.45,.20),metal=1,rough=.35)
hemp=mat('REV Corda canapa',(.70,.62,.47),rough=.90)
seam=mat('REV Cuciture mantello',(.20,.29,.25),rough=.92)
ivory=mat('REV Occhio avorio',(.82,.80,.73),rough=.36)
dial=mat('REV Segni quadrante',(.72,.67,.48),metal=.4,rough=.4)
for ob in objects():
    if not ob.data.materials:assign(ob,bpy.data.materials['REV Pelle cinture'])
    if not ob.data.materials[0].name.startswith('REV '):
        original=ob.get('original_materials','')
        if 'Ottone' in original:assign(ob,brass)
        elif 'canapa' in original:assign(ob,hemp)
        elif 'cuciture' in original:assign(ob,seam)
        elif 'Occhi' in original:assign(ob,ivory)
        elif 'quadrante' in original:assign(ob,dial)
    # Procedural geometry retains all original pieces. No face/hand decimation.
    strip_armature(ob);worldmesh(ob)
    for ca in list(ob.data.color_attributes):ob.data.color_attributes.remove(ca)

def ntri(o):o.data.calc_loop_triangles();return len(o.data.loop_triangles)
def protected(o):
    return o.get('bone','').startswith('hand.') or o.name.startswith(('Dito ','Pollice ','Palmo ','Nocca guanto')) or (o.get('bone')=='head' and not o.name.startswith(('Capelli','REV Ciocca')))
keep={o.name:ntri(o) for o in objects() if protected(o)}
reductions=[]
def reduce(o,ratio):
    before=ntri(o)
    if before<32 or protected(o):return
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Budget triangoli revisione','DECIMATE');mod.ratio=max(24/before,ratio);mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    reductions.append((o.name,before,ntri(o)))

# First simplify small round parts as required, before any larger surface.
small=re.compile(r'rivett|bullon|vite|corda|corde|toron|lacci|laccio|tubo|spirale|occhiell|bottone|borchia',re.I)
small_done=set()
for ob in objects():
    if small.search(ob.name) and not protected(ob):reduce(ob,.48);small_done.add(ob.name)
log('Dopo piccoli elementi',tri_count())
if tri_count()>39500:
    for ob in objects():
        if ob.name in small_done or protected(ob):continue
        if ob.get('bone')=='CAPE':ratio=.85
        elif ob.name.startswith(('Capelli','REV Ciocca')):ratio=.62
        elif ob.name in ['Casco palombaro | calotta','Corpetto sagomato','Pantalone R','Pantalone L']:ratio=.80
        else:ratio=.56
        reduce(ob,ratio)
        if tri_count()<=39500:break
if tri_count()>39500:
    for ob in sorted(objects(),key=ntri,reverse=True):
        if protected(ob):continue
        reduce(ob,.75)
        if tri_count()<=39500:break
assert tri_count()<=40000,tri_count()
assert all(ntri(bpy.data.objects[name])==n for name,n in keep.items()),'Face or hands changed'

# Repair outward orientation; organic surfaces smooth, real hard edges at 30 degrees.
for ob in objects():
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    organic=ob.get('bone')=='head' or ob.get('bone','').startswith('hand.') or ob.get('bone')=='CAPE' or bool(re.search(r'Manica|Pantalone|Corda|corde|Toron|Tubo|Spirale|Mantell',ob.name))
    for f in bm.faces:f.smooth=True
    for e in bm.edges:
        e.smooth=organic or (e.is_manifold and e.calc_face_angle(0)<math.radians(30))
    bm.to_mesh(ob.data);bm.free();ob.data.update()
rows=[]
for ob in sorted(objects(),key=lambda o:o.name):
    n=ntri(ob);rows.append({'name':ob.name,'triangles':n});log('Triangoli',ob.name,n)
open(os.path.join(BASE,'rev_budget.json'),'w',encoding='utf-8').write(json.dumps({'total':tri_count(),'protected_before_after':keep,'reductions':reductions,'objects':rows},indent=2))
log('Budget verificato',tri_count(),'nessuna riduzione di viso o mani')
finish_group(10)
