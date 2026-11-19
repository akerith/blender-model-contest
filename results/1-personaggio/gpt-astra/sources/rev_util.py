exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py',encoding='utf-8').read(),'util','exec'))
from mathutils import Matrix
import json, bmesh, datetime

_base_mat=mat
def mat(name,color,metal=0,rough=.65):
    if name.startswith('REV '):
        linear=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in color)
        m=_base_mat(name,linear,metal,rough);m['RGB_sRGB']=list(color)
        return m
    return _base_mat(name,color,metal,rough)

def objects():
    return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('character')]
def coords(o): return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(o):
    p=coords(o)
    return Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])
def transform(o,fn):
    mw=o.matrix_world.copy(); inv=mw.inverted()
    for v in o.data.vertices:v.co=inv@Vector(fn(mw@v.co))
    o.data.update()
def select_prefix(*prefix): return [o for o in objects() if o.name.startswith(prefix)]
def assign(o,m):
    o.data.materials.clear();o.data.materials.append(m)
    for p in o.data.polygons:p.material_index=0
def fit(o,lo,hi):
    a,b=bounds(o);lo,hi=Vector(lo),Vector(hi)
    transform(o,lambda p: [lo[i]+(p[i]-a[i])*(hi[i]-lo[i])/max(1e-8,b[i]-a[i]) for i in range(3)])
def shift(o,d):transform(o,lambda p:p+Vector(d))
def finish_group(i):
    bpy.context.view_layer.update()
    bpy.ops.wm.save_mainfile()
    log('Gruppo',i,'triangoli',tri_count(),'ore',datetime.datetime.now().strftime('%H:%M:%S'))
    render_viste('rev_'+str(i))
def worldmesh(o):
    mw=o.matrix_world.copy()
    for v in o.data.vertices:v.co=mw@v.co
    o.matrix_world=Matrix.Identity(4)
def strip_armature(o):
    for mod in list(o.modifiers):
        if mod.type=='ARMATURE':o.modifiers.remove(mod)
    mw=o.matrix_world.copy();o.parent=None;o.matrix_world=mw

def deform_path(o,old,new,cross_scale=1):
    old=[Vector(p) for p in old];new=[Vector(p) for p in new]
    def change(p):
        best=None
        for i in range(len(old)-1):
            a,b=old[i:i+2];ab=b-a;t=max(0,min(1,(p-a).dot(ab)/ab.length_squared));c=a+ab*t;d=(p-c).length_squared
            if best is None or d<best[0]:best=(d,i,t,c)
        _,i,t,c=best;rot=(old[i+1]-old[i]).rotation_difference(new[i+1]-new[i])
        return new[i].lerp(new[i+1],t)+rot@(p-c)*cross_scale
    transform(o,change)

def frame_buckle(name,center,w,h,material,bone,rad=.0025):
    x,y,z=center
    path(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2),(x-w/2,y,z-h/2)],rad,material,bone,6)
    path(name+' pin',[(x,y-.001,z-h/2),(x,y-.002,z+h*.25)],rad*.55,material,bone,5)

