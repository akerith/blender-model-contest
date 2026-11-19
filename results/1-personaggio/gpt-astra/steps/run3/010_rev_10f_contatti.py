exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
ob=bpy.data.objects['Mantello lungo strappato']
# Let the middle fold clear the rear tunic. Translate both cloth surfaces
# by the same local offset, retaining thickness and the existing topology.
old=[v.co.copy() for v in ob.data.vertices]
tree=BVHTree.FromPolygons(old,[list(p.vertices) for p in ob.data.polygons])
changed=0
for v in ob.data.vertices:
    p=v.co.copy()
    if abs(p.x)<.23 and .76<p.z<1.12:
        hit=tree.ray_cast(Vector((p.x,.65,p.z)),Vector((0,-1,0)))
        if hit[0] is not None:
            edge=min(1,max(0,(.23-abs(p.x))/.035),max(0,(p.z-.76)/.04),max(0,(1.12-p.z)/.04))
            amount=max(0,.153-hit[0].y)*edge
            if amount>0:v.co.y+=amount;changed+=1
ob.data.update()
# Preserve the folded skirt, sitting inside the cape and outside the trousers.
for skirt in select_prefix('REV Falda posteriore'):
    for v in skirt.data.vertices:
        if v.co.y>.115:v.co.y=.115+(v.co.y-.115)*.12
    skirt.data.update()
log('Contatto tunica/mantello corretto, vertici mantello spostati',changed,'triangoli invariati',tri_count())
finish_group(10)
