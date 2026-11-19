exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
from mathutils.noise import noise_vector, noise
M=materials();skin=M['Pelle | ocra desaturata'];hair=M['Capelli | nero caldo'];edge=M['Cuoio | bordi'];brass=M['Ottone antico'];thread=M['Filo | canapa'];green=M['Mantello | verde salvia']

# Repair the jacket panels: explicit triangulation avoids an unstable mirrored ngon.
for side,s in [('R',-1),('L',1)]:
    for name in ['Falda giacca '+side,'Profilo falda '+side]:
        ob=bpy.data.objects.get(name)
        if ob:bpy.data.objects.remove(ob,do_unlink=True)
    vv=[(s*.009,-.112,.994),(s*.119,-.096,.989),(s*.016,-.123,.906),(s*.133,-.108,.902),(s*.021,-.127,.806),(s*.116,-.119,.789),(s*.151,-.086,.829)]
    ob=mesh('Falda giacca corretta '+side,vv,[(0,1,3),(0,3,2),(2,3,5),(2,5,4),(3,6,5)],M['Corpetto | petrolio scuro'],'pelvis')
    mod=ob.modifiers.new('Spessore falda','SOLIDIFY');mod.thickness=.003;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    path('Profilo falda corretto '+side,[vv[i] for i in [0,2,4,5,6,1]],.0015,edge,'pelvis',5)
    # Sleeve roots tucked under the shoulder cloth.
    ob=bpy.data.objects['Manica '+side]
    for i,v in enumerate(ob.data.vertices):
        if 20<=i<40:v.co.z-=.018
    # Soft irregular folds, especially above the knees.
    ob=bpy.data.objects['Pantalone '+side]
    for v in ob.data.vertices:
        x,y,z=v.co;a=math.atan2(y,(x-s*.093))
        v.co.x+=.0035*sin(z*95+a*3)*sin(pi*min(1,max(0,(z-.38)/.5)))
        v.co.y+=.004*sin(z*90+a*4)
    # Long tailored seams on the trouser legs.
    path('Couture pantalon '+side,[(s*.15,.002,.81),(s*.158,.004,.71),(s*.155,.001,.62),(s*.146,-.002,.55)],.0011,thread,'LEG.'+side,5)

# Broader asymmetric cape, less regular than a rectangular curtain.
cape=bpy.data.objects['Mantello lungo strappato']
for v in cape.data.vertices:
    x,y,z=v.co;t=max(0,min(1,(1.37-z)/1.15))
    v.co.x*=1+.23*t
    v.co.y+=.014*sin(x*42+t*7)*t+.007*sin(x*77-t*4)*t
    v.co.z+=.025*sin(x*23)*t+.026*x*t
    if z<.52:
        v.co.z+=.02*sin(x*89)+.012*sin(x*177)
# Irregular slit near the lower left side: remove one small set of faces.
import bmesh
bm=bmesh.new();bm.from_mesh(cape.data)
erase=[]
for f in bm.faces:
    c=f.calc_center_median()
    if -.18<c.x<-.14 and .32<c.z<.48:erase.append(f)
bmesh.ops.delete(bm,geom=erase,context='FACES');bm.to_mesh(cape.data);bm.free()

# Stern, less arched brows and subtle lower-eye shading.
for s in [-1,1]:
    ob=bpy.data.objects.get('Sopracciglio '+str(s))
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
    path('Sopracciglio definitivo '+str(s),[(s*.012,-.0625,1.568),(s*.024,-.065,1.570),(s*.036,-.060,1.571),(s*.046,-.051,1.566)],.0022,hair,'head',7)
    # Small loose hair tips break up the rounded bob.
    for k in range(4):
        tube('Punta ribelle %d %d'%(s,k),[(s*.065,.015+k*.009,1.6-k*.012),(s*.086,.015+k*.009,1.58-k*.014),(s*(.093-k*.003),.009+k*.009,1.583-k*.016)],[(.008,.003),(.006,.002),(.0005,.0004)],hair,'head',6)

# Central vest placket, small buttons, articulated shoulder folds.
ribbon('Abbottonatura',[(0,-.078,1.385),(0,-.102,1.29),(0,-.098,1.2),(0,-.083,1.095)],.019,edge,'TORSO',.002)
for j in range(5):
    z=1.34-j*.047;y=-.102 if z<1.32 else -.089
    cylinder('Bottone busto %d'%j,(-.003,y,z),(-.003,y-.003,z),.0032,brass,'TORSO',8)
for s,side in [(-1,'R'),(1,'L')]:
    for k in range(3):
        path('Piega mantellina '+side+str(k),[(s*(.065+k*.027),-.078,1.406-k*.012),(s*(.10+k*.028),-.093,1.371-k*.013),(s*(.14+k*.025),-.086,1.344-k*.014)],.0019,M['Mantello | cuciture'],'clavicle.'+side,6)

# Reduce dense rounded small components. Protect face, thin strips and cape topology.
protected=('Testa','Naso','Occhio','Iride','Pupilla','Punto luce','Palpebra','Labbro','Rima','Mantello lungo','Falda','Mantellina','Collo alto','Corpetto','Manica','Pantalone','Bacino')
reduced=0
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH' or not ob.get('character') or ob.name.startswith(protected):continue
    ob.data.calc_loop_triangles();n=len(ob.data.loop_triangles)
    if n<100:continue
    ratio=.63 if n>300 else .76
    if ob.name.startswith(('Spirale tubo','Toron corde','Boucle corde')):ratio=.58
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Ottimizzazione gioco','DECIMATE');mod.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=mod.name);reduced+=1

# Vertex pigment describes large-scale wear; shader noise supplies the fine grain.
for m in bpy.data.materials:
    if not m.use_nodes:continue
    p=m.node_tree.nodes.get('Principled BSDF')
    if not p:continue
    base=tuple(p.inputs['Base Color'].default_value[:3]);m['base_original']=base
    name=m.name
    if 'Mantello | verde' in name:base=(.055,.112,.088)
    elif 'Corpetto' in name:base=(.037,.067,.063)
    elif 'Pelle' in name:base=(.36,.235,.165)
    elif 'Lino' in name:base=(.245,.21,.164)
    m['base_pigment']=base

for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.get('character'):continue
    attr=ob.data.color_attributes.new(name='Pigmento',type='FLOAT_COLOR',domain='CORNER')
    for poly in ob.data.polygons:
        m=ob.data.materials[poly.material_index];base=Vector(m.get('base_pigment',(.2,.2,.2)))
        for li in poly.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index];p=ob.matrix_world@v.co
            n=noise(p*31)+.5*noise(p*97);c=base*(.91+.22*n)
            if ob.name.startswith(('Mantello lungo','Mantellina','Collo alto')):
                # Bleached irregular stains near lower and outer edges, with dirt in folds.
                stain=noise(p*13+Vector((2,0,3)))+.4*noise(p*38)
                border=max(0,(abs(p.x)-.19)*3)+max(0,(.67-p.z))*.6
                w=max(0,min(.75,(stain-.18+border)*1.1))
                c=c.lerp(Vector((.28,.27,.205)),w)
            elif 'Ottone' in m.name:
                tarnish=max(0,min(.9,(noise(p*52)-.05)*1.5))
                c=c.lerp(Vector((.05,.105,.083)),tarnish)
            elif ob.name=='Testa':
                x,y,z=p
                blush=math.exp(-((abs(x)-.04)/.021)**2-((z-1.523)/.02)**2)*max(0,min(1,-y*18))
                c=c.lerp(Vector((.30,.145,.105)),blush*.38)
                sock=math.exp(-((abs(x)-.027)/.018)**2-((z-1.556)/.017)**2)*max(0,min(1,-y*18))
                c*=1-sock*.20
            attr.data[li].color=(*[max(.001,min(1,x)) for x in c],1)

for m in bpy.data.materials:
    if not m.use_nodes or 'base_pigment' not in m:continue
    nt=m.node_tree;p=nt.nodes.get('Principled BSDF');name=m.name
    col=nt.nodes.new('ShaderNodeVertexColor');col.layer_name='Pigmento'
    tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=90;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.7
    geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],tex.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.57,.57,.57,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(1,1,1,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.65
    nt.links.new(col.outputs['Color'],mix.inputs[1]);nt.links.new(ramp.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
    # Skin, eyes and hair need very little roughness detail.
    if any(k in name for k in ['Occhi','Pupill','Oblo','Ciocca']):continue
    fine=nt.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=650 if any(k in name for k in ['Mantello','Lino','Pantalon','Corpetto']) else 280;fine.inputs['Detail'].default_value=2
    nt.links.new(geo.outputs['Position'],fine.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.0007 if 'Pelle' in name else .0015
    nt.links.new(fine.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
    if 'Ottone' in name:p.inputs['Roughness'].default_value=.49

save();log('Ottimizzati',reduced,'oggetti. Triangoli:',tri_count())
render_viste('05_finitura',viste=['fronte','retro','tre_quarti'],risoluzione=1200)
