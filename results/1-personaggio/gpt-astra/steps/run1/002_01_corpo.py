exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\util_personaggio.py').read(),'util','exec'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
skin=mat('Pelle | ocra desaturata',(.43,.30,.215),rough=.74)
shirt=mat('Lino | avorio sporco',(.29,.265,.215),rough=.93)
pants=mat('Pantaloni | tela carbone',(.095,.104,.092),rough=.9)
vest=mat('Corpetto | petrolio scuro',(.055,.105,.105),rough=.79)
leather=mat('Cuoio | bruno',(.075,.043,.025),rough=.64)
edge=mat('Cuoio | bordi',(.145,.092,.052),rough=.72)
dark=mat('Cuciture e suole',(.025,.023,.021),rough=.88)
brass=mat('Ottone antico',(.36,.23,.095),metal=.78,rough=.36)
green=mat('Mantello | verde salvia',(.095,.18,.155),rough=.93)

# Anatomical proportions, forward is -Y, total height with hair will be 1.70 m.
rings('Corpetto sagomato',[(.85,0,0,.14,.086),(.91,0,0,.145,.09),(.99,0,0,.13,.085),(1.06,0,0,.108,.073),(1.12,0,0,.112,.078),(1.2,0,-.003,.135,.087),(1.27,0,-.008,.15,.093),(1.32,0,.003,.158,.083),(1.36,0,.006,.158,.068),(1.39,0,.004,.115,.055),(1.405,0,0,.052,.042)],vest,'TORSO',32)
rings('Bacino pantaloni',[(.76,0,.003,.126,.071),(.83,0,0,.145,.083),(.91,0,0,.143,.083),(.96,0,0,.129,.08)],pants,'pelvis',24)
uv('Collo',(0,0,1.431),(.043,.043,.075),skin,'neck')
# A controlled head cage, facial features in the next step.
rings('Testa',[(1.447,0,-.019,.022,.026),(1.46,0,-.016,.042,.044),(1.485,0,-.006,.056,.057),(1.515,0,0,.069,.065),(1.55,0,.003,.071,.065),(1.585,0,.005,.069,.064),(1.62,0,.009,.061,.058),(1.65,0,.011,.042,.041),(1.662,0,.011,.009,.009)],skin,'head',40)
for s,side in [(-1,'R'),(1,'L')]:
    x=s*.093
    rings('Pantalone '+side,[(.38,x,.008,.057,.052,.025),(.44,x,.006,.061,.053,.045),(.49,x,.002,.062,.055,.07),(.53,x,0,.057,.052,.06),(.57,x,0,.061,.06,.07),(.62,x,0,.067,.064,.025),(.71,x,0,.073,.07,.02),(.81,x,0,.074,.07,.01),(.88,x,0,.068,.068)],pants,'LEG.'+side,24)
    # Tall leather boots with shaped ankles and broad cuffs.
    rings('Gambale stivale '+side,[(.055,x,.008,.049,.051),(.11,x,.01,.046,.045),(.18,x,.014,.043,.041),(.25,x,.016,.051,.047),(.33,x,.015,.057,.049),(.39,x,.01,.06,.049),(.415,x,.009,.064,.053)],leather,'shin.'+side,24)
    uv('Piede stivale '+side,(x,-.046,.065),(.055,.112,.053),leather,'foot.'+side,24,12)
    uv('Punta stivale '+side,(x,-.108,.049),(.054,.053,.035),leather,'foot.'+side,20,10)
    ob=box('Suola '+side,(x,-.042,.019),(.112,.218,.026),dark,'foot.'+side,.012)
    box('Tacco '+side,(x,.036,.014),(.087,.064,.028),dark,'foot.'+side,.006)
    # Sleeves with a continuous elbow, then leather gauntlets.
    sleeve=[(s*.145,0,1.35),(s*.181,0,1.339),(s*.215,0,1.301),(s*.255,0,1.253),(s*.29,0,1.205),(s*.324,0,1.169),(s*.345,0,1.148),(s*.365,0,1.128)]
    tube('Manica '+side,sleeve,[(.064,.061),(.069,.063),(.058,.055),(.053,.049),(.05,.046),(.054,.05),(.047,.045),(.042,.041)],shirt,'ARM.'+side,20)
    tube('Guanto avambraccio '+side,[(s*.335,0,1.158),(s*.36,0,1.132),(s*.405,0,1.09),(s*.458,0,1.047),(s*.482,0,1.023)],[(.051,.046),(.049,.044),(.041,.037),(.032,.029),(.03,.025)],leather,'forearm.'+side,20)
    hand=uv('Palmo guanto '+side,(s*.506,-.001,1.003),(.035,.024,.052),leather,'hand.'+side,20,12)
    hand.rotation_euler[1]=s*-.77
    # Four individually modelled fingers, thumb spread towards the torso.
    for k in range(4):
        start=Vector((s*(.512+.012*k),-.003,1.005-.011*k))
        end=start+Vector((s*(.041-.004*abs(k-1)),-.002,-(.044-.003*abs(k-1))))
        mid=start.lerp(end,.55)+Vector((0,-.004,0))
        tube('Dito %d %s'%(k+1,side),[start,mid,end],[.009,.008,.0048],leather,'hand.'+side,8)
    tube('Pollice '+side,[(s*.484,-.004,.998),(s*.482,-.014,.975),(s*.495,-.02,.956)],[.013,.01,.006],leather,'hand.'+side,10)

sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True
sc.world.color=(.15,.15,.15)
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.18,.2,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
sc.view_settings.view_transform='AgX'
for name,loc,power,size,col in [('Key',(-3,-4,5),450,4,(1,.86,.72)),('Fill',(3,-2,2.5),240,3,(.68,.8,1)),('Rim',(1,3,4),550,3,(1,.9,.72))]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='_gara_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_distance=2.6;a.spaces.active.region_3d.view_location=(0,0,.9)
save();log('Corpo base; triangoli:',tri_count())
render_viste('01_corpo',viste=['fronte','tre_quarti'])
