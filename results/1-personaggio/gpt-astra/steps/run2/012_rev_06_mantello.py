exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
from mathutils.kdtree import KDTree
teal=mat('REV Mantello teal',(.22,.34,.31),rough=.92)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def color(c):return (*[linear(x) for x in c],1)
nt=teal.node_tree;p=nt.nodes.get('Principled BSDF')
geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
stretch=nt.nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(42,20,2.5);nt.links.new(geo.outputs['Position'],stretch.inputs[0])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=3;nt.links.new(stretch.outputs[0],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=color((.22,.34,.31));ramp.color_ramp.elements[1].position=.80;ramp.color_ramp.elements[1].color=color((.40,.52,.48));nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
fade=nt.nodes.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.22;fade.inputs['From Max'].default_value=.50;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;fade.clamp=True;nt.links.new(xyz.outputs['Z'],fade.inputs['Value'])
stain=nt.nodes.new('ShaderNodeTexNoise');stain.inputs['Scale'].default_value=22;stain.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],stain.inputs['Vector'])
sand=nt.nodes.new('ShaderNodeValToRGB');sand.color_ramp.elements[0].position=.28;sand.color_ramp.elements[0].color=color((.32,.25,.16));sand.color_ramp.elements[1].position=.62;sand.color_ramp.elements[1].color=color((.62,.55,.43));nt.links.new(stain.outputs['Fac'],sand.inputs[0])
mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(fade.outputs[0],mix.inputs[0]);nt.links.new(ramp.outputs[0],mix.inputs[1]);nt.links.new(sand.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.001;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
o=bpy.data.objects['Mantello lungo strappato'];before=[v.co.copy() for v in o.data.vertices];kd=KDTree(len(before))
for i,v in enumerate(before):kd.insert(v,i)
kd.balance();pairs={}
for i,v in enumerate(before):
    near=[(d,j) for co,j,d in kd.find_range(v,.004) if j!=i and d>.00001]
    if near:pairs[i]=min(near)[1]
def cape_map(p):
    x,y,z=p;t=max(0,min(1,(1.38729-z)/1.22360));u=max(-1,min(1,x/(.187+.146*t)))
    return Vector((u*(.20+.35*t),y+.030*sin(6*pi*(u+1)+t*.4)*t**.6,1.40-(1.38729-z)*(1.20/1.22360)))
after=[cape_map(p) for p in before]
for v in o.data.vertices:
    p=after[v.index]
    if v.index in pairs:p=(p+after[pairs[v.index]])*.5+(p-after[pairs[v.index]])*1.8
    v.co=p
assign(o,teal)
# Move the existing abrasion meshes with their supporting cape.
for ob in select_prefix('Abrasion mantello','Rammendo'):transform(ob,cape_map)
# Add the two missing front panels, attached along the existing cape sides.
random.seed(82)
for s,side in [(-1,'R'),(1,'L')]:
    C=10;R=18;hem=[.25+random.uniform(-.015,.07)+(0.085 if j in [2,5,8] else 0) for j in range(C+1)];verts=[];faces=[]
    for i in range(R+1):
        t=i/R
        for j in range(C+1):
            u=j/C;inner=.105+.075*t;outer=.20+.35*t
            x=s*(inner*(1-u)+outer*u);y=-.087*(1-u)+(.024+.035*t)*u+.022*sin(u*pi*4+t*.4)*sin(pi*u)
            z=(1-t)*(1.40-.025*(1-u))+t*hem[j];verts.append((x,y,z))
    for i in range(R):
        for j in range(C):
            if (i,j) in {(16,2),(16,7),(17,7)}:continue
            a=i*(C+1)+j;faces.append((a,a+1,a+C+2,a+C+1))
    ob=mesh('REV Falda frontale mantello '+side,verts,faces,teal,'CAPE')
    mod=ob.modifiers.new('Spessore 6 mm','SOLIDIFY');mod.thickness=.006;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Enlarge the existing shoulder cape over the tops of the upper arms.
    ob=bpy.data.objects['Mantellina curva '+side];N=19;cent=[Vector((s*x,0,z)) for x,z in [(.08,1.43),(.15,1.40),(.235,1.33),(.30,1.25)]];rads=[.049,.078,.075,.060]
    assert len(ob.data.vertices)==152
    for v in ob.data.vertices:
        j=v.index%(N*4);row=j//N;col=j%N;back=v.index//(N*4);a=-pi*.54+pi*1.08*col/(N-1)
        tang=(cent[min(row+1,3)]-cent[max(row-1,0)]).normalized();u=tang.cross(Vector((0,1,0))).normalized()
        if u.z<0:u=-u
        p=cent[row]+(rads[row]+back*.006)*(cos(a)*u+sin(a)*Vector((0,1,0)))
        if row==3:p.z+=.010*sin(col*2.3)+.006*sin(col*4.1)
        v.co=p
    assign(ob,teal)
    # Keep the original edge and seam pieces seated on the enlarged yoke.
    for ob in select_prefix('Orlo mantellina '+side,'Cresta mantellina '+side):
        transform(ob,lambda p:(p.x*1.23,p.y,1.44+(p.z-1.44)*1.50));assign(ob,teal)
ob=bpy.data.objects['Sprone dorsale mantello'];fit(ob,(-.21,.07,1.20),(.21,.14,1.43));assign(ob,teal)
# Rework the old clasp as part of the three-shell cluster.
ivory=mat('REV Conchiglie',(.88,.85,.78),rough=.66)
for ob in select_prefix('Fermaglio','Cavita fermaglio','Dente fermaglio','Legaccio fermaglio'):
    shift(ob,(.003,-.025,-.025));assign(ob,ivory)
o=bpy.data.objects['Fermaglio osso cranio'];fit(o,(.101,-.115,1.358),(.124,-.105,1.382))
o=bpy.data.objects['Fermaglio mascella'];fit(o,(.122,-.116,1.358),(.145,-.107,1.380))
uv('REV Terza conchiglia',(.120,-.112,1.392),(.011,.006,.013),ivory,'clavicle.L',12,8)
for k,c in enumerate([(.112,1.370),(.134,1.370),(.120,1.392)]):
    for j in range(5):
        a=(j-2)*.28;path('REV Costa conchiglia %d %d'%(k,j),[(c[0],-.118,c[1]-.009),(c[0]+.010*sin(a),-.119,c[1]+.010*cos(a))],.0008,ivory,'clavicle.L',4)
for ob in select_prefix('Mantello','Mantellina','REV Falda frontale'):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
log('Mantello allargato a circa 1.10 m, sei onde grandi, due falde frontali con apertura 0.36 m, spessore 6 mm e strappi conservati')
finish_group(6)
