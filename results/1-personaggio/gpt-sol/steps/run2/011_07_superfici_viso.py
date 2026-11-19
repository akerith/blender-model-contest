import os
exec(compile(open(os.path.join(os.path.dirname(OUTBOX),'lavoro','personaggio_lib.py'),encoding='utf-8').read(),'personaggio_lib.py','exec'))
setup_materials()

# Replace protruding eyeballs with shallow almond-shaped sclerae, finer eyelids.
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('Occhio_','Iride_','Pupilla_','Riflesso_occhio_','Palpebra_','Ciglia_','Sopracciglio_')):
        bpy.data.objects.remove(o,do_unlink=True)
for s in [-1,1]:
    cx=s*.0305;verts=[];uv=[];nx=15;ny=5
    for i in range(nx):
        t=i/(nx-1);x=cx+(t-.5)*.037
        upper=1.592+.0048*sin(t*pi)+s*(x-cx)*.035
        lower=1.592-.0036*sin(t*pi)+s*(x-cx)*.035
        for j in range(ny):
            q=j/(ny-1);z=lower*(1-q)+upper*q
            y=-.0595+.006*(abs(t-.5)*2)**1.6+.0013*(abs(q-.5)*2)**2
            verts.append((x,y,z));uv.append((t,q))
    mesh('Occhio_anatomico_'+str(s),verts,[(i*ny+j,(i+1)*ny+j,(i+1)*ny+j+1,i*ny+j+1) for i in range(nx-1) for j in range(ny-1)],'eye','head',uv)
    ell('Iride_rifinita_'+str(s),(cx,-.0604,1.592),(.0051,.001,.0049),'iris','head',16,8)
    ell('Pupilla_rifinita_'+str(s),(cx,-.0615,1.592),(.0023,.0005,.0031),'black','head',12,6)
    ell('Riflesso_rifinito_'+str(s),(cx-.0012,-.0622,1.594),(.001,.0004,.001),'eye','head',8,6)
    for upper in [True,False]:
        pts=[]
        for i in range(11):
            t=i/10;x=cx+(t-.5)*.037
            z=1.592+(.0048 if upper else -.0036)*sin(t*pi)+s*(x-cx)*.035
            y=-.0582+.006*(abs(t-.5)*2)**1.6
            pts.append((x,y,z))
        tube(('Palpebra_sup_' if upper else 'Palpebra_inf_')+str(s),pts,.0016 if upper else .0011,'skin','head',6)
        if upper:tube('Ciglia_fini_'+str(s),[(x,y-.0007,z-.0007) for x,y,z in pts],.00065,'hair','head',5)
    tube('Sopracciglio_rifinito_'+str(s),[(s*.012,-.060,1.606),(s*.025,-.061,1.610),(s*.040,-.057,1.609),(s*.052,-.048,1.605)],.0024,'hair','head',6,radii=[.0022,.0026,.0021,.0007])

# A slightly narrower, softer jaw and lip line.
o=bpy.data.objects['Viso']
for v in o.data.vertices:
    if v.co.z<1.547:
        v.co.x*=1-.09*exp(-((v.co.z-1.516)/.025)**2)
for o in bpy.context.scene.objects:
    if o.name.startswith(('Labbro_','Rima_labbra')):
        for v in o.data.vertices:
            v.co.x*=.92;v.co.z=1.543+(v.co.z-1.543)*.82
    if o.name.startswith('Cavita_orecchio_'):
        for v in o.data.vertices:v.co*=.74

# Subtle vertex-painted complexion: warm cheeks, under-eye tone, no external images.
for o in bpy.context.scene.objects:
    if o.type!='MESH' or M['skin'] not in list(o.data.materials):continue
    attr=o.data.color_attributes.get('Carnagione') or o.data.color_attributes.new(name='Carnagione',type='FLOAT_COLOR',domain='CORNER')
    for loop in o.data.loops:
        p=o.matrix_world@o.data.vertices[loop.vertex_index].co
        cheek=exp(-((abs(p.x)-.042)/.027)**2-((p.z-1.564)/.02)**2)*max(0,min(1,(-p.y-.015)*25))
        eye=exp(-((abs(p.x)-.032)/.021)**2-((p.z-1.582)/.007)**2)*max(0,min(1,(-p.y-.02)*30))
        brow=exp(-((abs(p.x)-.032)/.026)**2-((p.z-1.609)/.009)**2)*max(0,min(1,(-p.y-.03)*35))
        base=np.array((.48,.285,.19))*(1-.13*eye-.055*brow)
        base=base*(1-.16*cheek)+np.array((.48,.21,.15))*.16*cheek
        attr.data[loop.index].color=(*base,1)
bs=M['skin'].node_tree.nodes.get('Principled BSDF')
vc=M['skin'].node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Carnagione'
M['skin'].node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])

def write_texture(name,arr,srgb=False):
    h,w=arr.shape[:2];rgba=np.ones((h,w,4),np.float32)
    rgb=np.clip(arr,0,1)
    if srgb:rgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055)
    rgba[:,:,:3]=rgb
    tmp=bpy.data.images.new(name+'_buffer',width=w,height=h);tmp.colorspace_settings.name='Non-Color';tmp.pixels.foreach_set(rgba.ravel())
    path=os.path.join(TEX,name+'.png');tmp.filepath_raw=path;tmp.file_format='PNG';tmp.save();bpy.data.images.remove(tmp)
    im=bpy.data.images.load(path,check_existing=False);im.name=name;im.colorspace_settings.name='sRGB' if srgb else 'Non-Color';im.pack();return im

# Export-safe texture nodes. Diffuse PNG files are explicitly encoded in sRGB;
# tangent-space normal maps remain linear data, for matching Blender/glTF shading.
for key,m in M.items():
    node=m.node_tree.nodes.get('Usura generata')
    if not node:continue
    im=node.image;w,h=im.size;data=np.empty(w*h*4,np.float32);im.pixels.foreach_get(data);rgb=data.reshape(h,w,4)[:,:,:3].copy()
    rng=np.random.default_rng(100+sum(map(ord,key)));yy,xx=np.mgrid[0:h,0:w]
    u=xx/w;v=yy/h;grain=rng.random((h,w))
    if key in ['brass','brassedge','iron']:
        cloud=np.sin(u*32+np.sin(v*14))*np.cos(v*28)+.5*np.sin(u*96+v*49)
        patina=np.clip((cloud-.45)*.25,0,.19)
        rgb=rgb*(1-patina[:,:,None])+np.array((.035,.095,.073))*patina[:,:,None]
        # Fine engraving-like scratches and small dark pits.
        for k in range(65):
            x0=rng.integers(0,w);y0=rng.integers(0,h);length=rng.integers(3,25)
            for q in range(length):
                x=(x0+q)%w;y=(y0+q//5)%h
                rgb[y,x,:]*=1.18 if k%3 else .55
        height=grain*.28+.09*cloud
    elif key in ['leather','leatheredge','darkleather','sole']:
        crease=np.sin(u*62+np.sin(v*37)*1.3)*np.sin(v*46+np.sin(u*42))
        height=grain*.35+crease*.12
        rgb*=((.94+.12*grain+.05*crease)[:,:,None])
        for k in range(22):
            x0=rng.integers(0,w);y0=rng.integers(0,h)
            for q in range(rng.integers(3,15)):
                x=(x0+q)%w;y=(y0+q//3)%h;rgb[y,x,:]=rgb[y,x,:]*.68+np.array((.24,.15,.078))*.32
    elif key=='rope':
        height=.4*np.sin((u*8+v*48)*2*pi)+grain*.1
        rgb*=((.91+.12*np.sin((u*8+v*48)*2*pi))[:,:,None])
    elif key in ['hair','hairlight']:
        height=.22*np.sin(u*72*pi+np.sin(v*8))+.08*grain
        rgb*=((.9+.15*np.sin(u*72*pi+np.sin(v*8)))[:,:,None])
    else:
        height=(.18*np.cos(xx*pi)+.18*np.cos(yy*pi)+.10*grain)
    node.image=write_texture(m.name+'_albedo_sRGB',rgb,True)
    # Central differences with a mild amplitude; highlights show the weave without bumps.
    dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.7
    dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.7
    normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
    nim=write_texture(m.name+'_normal',normal*.5+.5)
    tn=m.node_tree.nodes.new('ShaderNodeTexImage');tn.name='Normal texture glTF';tn.image=nim
    nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.32 if key not in ['rope','hair','hairlight'] else .7
    m.node_tree.links.new(tn.outputs['Color'],nm.inputs['Color'])
    m.node_tree.links.new(nm.outputs['Normal'],m.node_tree.nodes['Principled BSDF'].inputs['Normal'])
    # Use a neutral linear roughness with a separate packed texture where it helps.
    if key in ['brass','brassedge','iron','leather','darkleather']:
        rough=m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value
        rm=np.ones((h,w,3),np.float32);rm[:,:,0]=1;rm[:,:,1]=np.clip(rough+(grain-.5)*.12,.1,1);rm[:,:,2]=m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value
        ri=write_texture(m.name+'_ORM',rm)
        rt=m.node_tree.nodes.new('ShaderNodeTexImage');rt.image=ri
        sep=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(rt.outputs['Color'],sep.inputs['Color'])
        bs=m.node_tree.nodes['Principled BSDF'];m.node_tree.links.new(sep.outputs['Green'],bs.inputs['Roughness']);m.node_tree.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])

# Repair circular UV seams so that the final wrap segment does not stretch an atlas.
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.data.uv_layers:continue
    layer=o.data.uv_layers.active
    for p in o.data.polygons:
        vals=[layer.data[i].uv.x for i in p.loop_indices]
        if max(vals)-min(vals)>.7 and min(vals)>=0 and max(vals)<=1:
            for i in p.loop_indices:
                if layer.data[i].uv.x<.3:layer.data[i].uv.x+=1

save()
render_viste('07_superfici',viste=['fronte','retro','tre_quarti'])
portrait('07_viso',scale=.33,center=(0,0,1.584),loc=(.04,-1.5,1.60))
portrait('07_casco',center=(0,.18,1.30),scale=.52,loc=(.50,1.7,1.45))
