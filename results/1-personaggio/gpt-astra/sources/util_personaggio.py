import bpy, math, random, os
from mathutils import Vector
from math import sin, cos, pi
BASE = r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro'

def mat(name, color, metal=0, rough=.65):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def mesh(name, verts, faces, material, bone=None, smooth=True):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    if material: me.materials.append(material)
    for f in me.polygons: f.use_smooth=smooth
    if bone: ob['bone']=bone
    ob['character']=True
    return ob

def finish(ob, name, material, bone=None, smooth=True):
    ob.name=name
    if material: ob.data.materials.append(material)
    if ob.type=='MESH':
        for p in ob.data.polygons:p.use_smooth=smooth
    if bone:ob['bone']=bone
    ob['character']=True
    return ob

def uv(name, loc, scale, material, bone=None, seg=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    ob=bpy.context.object; ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(ob,name,material,bone)

def box(name,loc,scale,material,bone=None,bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object; ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(ob,name,material,bone,False)
    if bevel:
        mod=ob.modifiers.new('Bordi consumati','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=ob.modifiers.new('Normali','WEIGHTED_NORMAL'); bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def tube(name, points, radii, material, bone=None, sides=10, caps=True):
    pts=[Vector(p) for p in points]; verts=[]; faces=[]
    for i,p in enumerate(pts):
        tang=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]; tang.normalize()
        axis=Vector((0,1,0))
        if abs(tang.dot(axis))>.95:axis=Vector((1,0,0))
        u=tang.cross(axis).normalized(); v=tang.cross(u).normalized()
        rr=radii[i] if isinstance(radii,list) else radii
        rx,ry=rr if isinstance(rr,tuple) else (rr,rr)
        for j in range(sides):
            a=2*pi*j/sides; verts.append(tuple(p+u*(cos(a)*rx)+v*(sin(a)*ry)))
    for i in range(len(pts)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    if caps:
        faces.append(tuple(reversed(range(sides))))
        faces.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
    return mesh(name,verts,faces,material,bone)

def path(name,pts,radius,material,bone=None,sides=8):
    return tube(name,pts,radius,material,bone,sides)

def rings(name,sections,material,bone=None,n=32):
    # z, center x, center y, radius x, radius y, optional angular ripple
    vv=[]; ff=[]
    for sec in sections:
        z,x,y,rx,ry=sec[:5]; rip=sec[5] if len(sec)>5 else 0
        for j in range(n):
            a=2*pi*j/n; r=1+rip*cos(6*a+z*32)
            vv.append((x+rx*cos(a)*r,y+ry*sin(a)*r,z))
    for i in range(len(sections)-1):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;ff.append((a,b,b+n,a+n))
    ff.extend([tuple(reversed(range(n))),tuple((len(sections)-1)*n+j for j in range(n))])
    return mesh(name,vv,ff,material,bone)

def torus(name,loc,major,minor,material,bone=None,rot=(pi/2,0,0), seg=32, sides=8):
    bpy.ops.mesh.primitive_torus_add(major_segments=seg,minor_segments=sides,location=loc,rotation=rot,major_radius=major,minor_radius=minor)
    return finish(bpy.context.object,name,material,bone)

def cylinder(name,a,b,r,material,bone=None,n=20,r2=None):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=(b-a).length,location=(a+b)/2)
    ob=bpy.context.object; ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return finish(ob,name,material,bone)

def ribbon(name,points,width,material,bone=None,thick=.002):
    pts=[Vector(p) for p in points]; vv=[]
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        u=t.cross(Vector((0,-1,0))).normalized()
        vv.extend([tuple(p-u*width/2),tuple(p+u*width/2)])
    ob=mesh(name,vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(pts)-1)],material,bone)
    if thick:
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Spessore','SOLIDIFY');mod.thickness=thick
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def save():
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'personaggio.blend'))

def tri_count():
    total=0
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and o.get('character'):
            o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
    return total

def materials():
    return {m.name:m for m in bpy.data.materials}
