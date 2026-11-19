exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.bvhtree import BVHTree
for s,side in [(-1,'R'),(1,'L')]:
    cape=bpy.data.objects['Mantellina curva '+side]
    tree=BVHTree.FromPolygons(coords(cape),[list(p.vertices) for p in cape.data.polygons])
    for ob in select_prefix('Orlo mantellina '+side,'Cresta mantellina '+side):
        for v in ob.data.vertices:
            co,no,idx,d=tree.find_nearest(v.co)
            if co is not None:v.co=co+no*.0010
    ob=bpy.data.objects['REV Falda frontale mantello '+side];N=19*11
    for v in ob.data.vertices:
        idx=v.index%N;t=(idx//11)/18;u=(idx%11)/10;back=v.index//N
        inner=.15+.03*t;outer=.20+.35*t;v.co.x=s*(inner*(1-u)+outer*u)
        iy=-.08+.12*min(1,t*3);oy=.024+.035*t
        v.co.y=iy*(1-u)+oy*u+.020*sin(u*pi*4+t*.4)*sin(pi*u)+back*.006
log('Orli riportati sulla stoffa; falde aperte 0.30-0.36 m e arretrate ai fianchi per lasciare liberi gli accessori')
finish_group(6)
