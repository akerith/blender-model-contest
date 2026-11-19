exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Corpetto sagomato'];tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def front(x,z):
    h=tree.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))
    return h[0].y if h[0] else -.083
def reshape_ribbon(ob,points,width,thickness,offset=0):
    points=[Vector(p) for p in points];N=len(points)*2
    assert len(ob.data.vertices)==N*2,(ob.name,len(ob.data.vertices),N*2)
    for v in ob.data.vertices:
        j=(v.index%N)//2;side=1 if v.index%2 else -1;back=v.index//N
        tangent=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized();across=tangent.cross(Vector((0,-1,0))).normalized()
        p=points[j]+across*width*.5*side
        if points[j].y<-.02:p.y=front(p.x,p.z)-offset-thickness*back
        else:p.y+=thickness*back
        v.co=p
    for p in ob.data.polygons:p.use_smooth=False
for s,side in [(-1,'R'),(1,'L')]:
    pts=[(s*.13,.07,1.41),(s*.13,0,1.425),(s*.13,-.065,1.41),(s*.060,-.11,1.325),(0,-.125,1.25),(-s*.11,-.106,1.105),(-s*.15,-.079,1.04)]
    reshape_ribbon(bpy.data.objects['Bretella incrociata '+side],pts,.035,.008,.010 if side=='L' else .002)
    ob=bpy.data.objects['Cucitura bretella '+side]
    for v in ob.data.vertices:
        k=min(4,v.index//5);c=Vector(pts[k+2]);c.x+=s*.011;a=2*pi*(v.index%5)/5
        v.co=(c.x+.00065*cos(a),front(c.x,c.z)-(.019 if side=='L' else .011),c.z+.00065*sin(a))
    for ob in select_prefix('Fibbia pettorale '+side):
        shift(ob,(-s*.014,0,0))
ob=bpy.data.objects['Cintura obliqua']
reshape_ribbon(ob,[(-.17,-.05,.94),(-.11,-.1,.95),(0,-.12,.97),(.11,-.1,.99),(.17,-.04,1.0)],.04,.006,.008)
for ob in select_prefix('Cinturone','REV Cinghia sottoseno'):
    for p in ob.data.polygons:p.use_smooth=False
log('Corrette le estremita delle bretelle e l\'aderenza sul busto mantenendo vertici e facce originali')
finish_group(4)
