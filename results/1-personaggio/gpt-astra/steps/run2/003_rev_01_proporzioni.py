exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.kdtree import KDTree
from collections import Counter
original=bpy.data.objects['Personaggio_Mesh'];atlas=original.data.materials[0]
# Read our own saved source only to recover semantic identities. The geometry
# being revised remains the actual round-one delivered mesh throughout.
with bpy.data.libraries.load(os.path.join(BASE,'personaggio_sorgente.blend'),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if not n.startswith('_gara') and n!='Personaggio_Rig']
sources=[o for o in dst.objects if o and o.type=='MESH']
tree=KDTree(sum(len(o.data.vertices) for o in sources));labels=[];metadata=[]
idx=0
for si,o in enumerate(sources):
    metadata.append({'name':o.name,'bone':o.get('bone',''),'materials':[m.name for m in o.data.materials]})
    for v in o.data.vertices:
        tree.insert(o.matrix_world@v.co,idx);labels.append(si);idx+=1
tree.balance();vlabels=[];error=0
for v in original.data.vertices:
    co,i,d=tree.find(original.matrix_world@v.co);vlabels.append(labels[i]);error=max(error,d)
assert error<.0001, error
original.data.materials.clear()
for si,md in enumerate(metadata):
    m=bpy.data.materials.new('REV_ID_'+str(si));m['source_id']=si;original.data.materials.append(m)
for p in original.data.polygons:p.material_index=Counter(vlabels[i] for i in p.vertices).most_common(1)[0][0]
for o in sources:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');original.select_set(True);bpy.context.view_layer.objects.active=original
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
for o in list(bpy.context.selected_objects):
    if o.type!='MESH':continue
    mid=o.data.materials[o.data.polygons[0].material_index]['source_id'];md=metadata[mid]
    o.name=md['name'];o['bone']=md['bone'];o['original_materials']=';'.join(md['materials']);o['character']=True
    assign(o,atlas);strip_armature(o);worldmesh(o)
log('Separati pezzi esistenti',len(objects()),'scarto identificazione',error,'triangoli conservati',tri_count())
fac=bpy.context.scene.get('scale_geometry',1);zmin=bpy.context.scene.get('original_zmin',0)
def raw(p):return Vector((p.x/fac,p.y/fac,p.z/fac+zmin))
def interp(t,pairs):
    if t<=pairs[0][0]:return pairs[0][1]+t-pairs[0][0]
    if t>=pairs[-1][0]:return pairs[-1][1]+t-pairs[-1][0]
    for (a,b),(c,d) in zip(pairs,pairs[1:]):
        if a<=t<=c:return b+(d-b)*(t-a)/(c-a)
def torso(p):
    x,y,z=raw(p);nz=interp(z,[(.79,.80),(.87,.90),(1.035,1.09),(1.20,1.27),(1.35,1.40),(1.405,1.45)])
    sx=interp(z,[(.85,1.17),(1.06,1.25),(1.27,1.07),(1.36,1.02)])
    return (x*sx,y*1.14,nz)
def armmap(p,s):
    p=raw(p);a=Vector((s*.17,0,1.347));b=Vector((s*.336,0,1.157));c=Vector((s*.48,0,1.025))
    na=Vector((s*.19,0,1.4));nb=Vector((s*.38,0,1.18));nc=Vector((s*.54,0,.99))
    if s*p.x<=.336:oa,ob,nn,ne=a,b,na,nb
    else:oa,ob,nn,ne=b,c,nb,nc
    axis=(ob-oa).normalized();newaxis=(ne-nn).normalized();t=(p-oa).dot(axis)/(ob-oa).length
    off=p-(oa+(ob-oa)*t);rot=axis.rotation_difference(newaxis)
    if s*p.x>.48:
        # Lengthen the existing palm and articulated fingers along the same axis.
        oldaxis=(c-b).normalized();newaxis=Vector((s*.66,0,.86))-nc;newaxis.normalize()
        d=p-c;along=d.dot(oldaxis);cross=d-oldaxis*along
        return nc+newaxis*(along*1.65)+oldaxis.rotation_difference(newaxis)@cross*1.18
    return nn+(ne-nn)*t+rot@off
for o in objects():
    n=o.name;tag=o.get('bone','')
    if tag=='head':
        def hm(p):
            x,y,z=raw(p)
            return (x*1.07,y*1.24,interp(z,[(1.446,1.475),(1.50,1.52),(1.556,1.585),(1.664,1.66),(1.687,1.70)]))
        transform(o,hm)
    elif tag.startswith(('ARM.','forearm.','hand.')) or n.startswith(('Dito ','Pollice ','Nocca guanto')):
        transform(o,lambda p,s=(-1 if tag.endswith('R') or n.endswith('R') else 1):armmap(p,s))
    elif tag.startswith(('LEG.','shin.','foot.')):
        s=-1 if tag.endswith('R') else 1
        def lm(p,s=s):
            x,y,z=raw(p);t=max(0,min(1,(.90-z)/.82));cx=s*(.10+.03*t)
            return (cx+(x-s*.093),y,interp(z,[(0,0),(.11,.08),(.526,.49),(.87,.90)]))
        transform(o,lm)
    elif n=='Collo':fit(o,(-.055,-.055,1.45),(.055,.055,1.49))
    elif tag=='TORSO' or n.startswith(('Corpetto','Bacino','Falda','Profilo falda','Cintur','Bordo cintura','Fibbia cintura','Lingua cintura','Foro cintura')):transform(o,torso)
    elif n.startswith(('Mantellina','Orlo mantellina','Cresta mantellina','Sprone','Collo alto','Bordo colletto','Fazzoletto')):
        transform(o,lambda p:(p.x*1.08,p.y,p.z+.035))
# Accurate body widths at the controlling rings without changing topology.
o=bpy.data.objects['Corpetto sagomato']
for v in o.data.vertices:
    z=v.co.z
    if 1.06<z<1.16:v.co.x*=1.02
# Sole floor and exact hair top.
hair=[o for o in objects() if o.get('bone')=='head' and o.name.startswith('Capelli')]
hairmax=max(p.z for o in hair for p in coords(o))
for o in hair:transform(o,lambda p:(p.x,p.y,1.60+(p.z-1.60)*(.10/(hairmax-1.60))))
rig=bpy.data.objects['Personaggio_Rig'];rig.hide_set(True)
bpy.context.scene.cycles.samples=24
report=[{'name':o.name,'bone':o.get('bone'),'bounds':[list(x) for x in bounds(o)],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in objects()]
open(os.path.join(BASE,'rev_parti.json'),'w',encoding='utf-8').write(json.dumps(report,indent=2))
finish_group(1)
