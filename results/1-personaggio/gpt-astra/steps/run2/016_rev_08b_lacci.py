exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
for s,side in [(-1,'R'),(1,'L')]:
    meshes=select_prefix('Gambale stivale '+side,'REV Risvolto stivale '+side,'Cinghia stivale '+side)
    vv=[];ff=[]
    for ob in meshes:
        off=len(vv);vv.extend(coords(ob));ff.extend([[i+off for i in p.vertices] for p in ob.data.polygons])
    tree=BVHTree.FromPolygons(vv,ff)
    def yy(x,z):
        hit=tree.ray_cast(Vector((x,-.3,z)),Vector((0,1,0)))
        return hit[0].y-.004 if hit[0] else -.052
    for k in range(8):
        z=.10+k*.0375;cx=s*(.13-.013*(z/.42))
        for label,rev in [('a',False),('b',True)]:
            z0=z if not rev else z+.0375;z1=z+.0375 if not rev else z
            pp=[Vector((cx-.015,yy(cx-.015,z0),z0)),Vector((cx+.015,yy(cx+.015,z1),z1))]
            ob=bpy.data.objects['Laccio X '+label+' '+side+str(k)] if k<7 else bpy.data.objects['REV Ottavo laccio '+label+side]
            sides=len(ob.data.vertices)//2;t=(pp[1]-pp[0]).normalized();u=t.cross(Vector((0,1,0))).normalized();v=t.cross(u).normalized()
            for vert in ob.data.vertices:
                j=vert.index//sides;a=2*pi*(vert.index%sides)/sides;vert.co=pp[j]+.002*(u*cos(a)+v*sin(a))
    for ob in select_prefix('REV Occhiello '+side,'REV Occhiello finale '+side):
        a,b=bounds(ob);c=(a+b)/2;shift(ob,(0,yy(c.x,c.z)-c.y,0))
log('Lacci riportati sulla superficie degli stivali e ripristinata la sezione tonda 4 mm')
finish_group(8)
