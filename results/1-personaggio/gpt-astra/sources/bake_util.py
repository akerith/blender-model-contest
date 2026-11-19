import bpy, os, json, time
BASE=r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro'
def progress(stage):
    open(os.path.join(BASE,'stato_texture.json'),'w').write(json.dumps({'phase':stage,'time':time.strftime('%H:%M:%S')}))

def bake_map(name,kind):
    ob=bpy.data.objects['Personaggio_Mesh']
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    im=bpy.data.images.new(name,width=4096,height=4096,alpha=False,float_buffer=False)
    if kind!='COLOR':im.colorspace_settings.name='Non-Color'
    mats=list(ob.data.materials);saved=[];created=[]
    for m in mats:
        nt=m.node_tree;p=nt.nodes.get('Principled BSDF');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        image_node=nt.nodes.new('ShaderNodeTexImage');image_node.image=im;image_node.name='BAKE_TARGET';nt.nodes.active=image_node;created.append((nt,image_node))
        if kind in ['COLOR','ORM']:
            original=out.inputs['Surface'].links[0].from_socket
            em=nt.nodes.new('ShaderNodeEmission');created.append((nt,em));em.inputs['Strength'].default_value=1
            if kind=='COLOR':
                inp=p.inputs['Base Color']
                if inp.is_linked:nt.links.new(inp.links[0].from_socket,em.inputs['Color'])
                else:em.inputs['Color'].default_value=inp.default_value
            else:
                em.inputs['Color'].default_value=(1,p.inputs['Roughness'].default_value,p.inputs['Metallic'].default_value,1)
            nt.links.new(em.outputs[0],out.inputs['Surface']);saved.append((nt,out,original))
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=8
    sc.render.bake.use_clear=True;sc.render.bake.margin=12
    progress('baking_'+kind)
    try:
        if kind=='NORMAL':bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT')
        else:bpy.ops.object.bake(type='EMIT')
        im.filepath_raw=os.path.join(BASE,name+'.png');im.file_format='PNG';im.save();im.pack()
    finally:
        for nt,out,original in saved:nt.links.new(original,out.inputs['Surface'])
        for nt,n in created:nt.nodes.remove(n)
    progress('done_'+kind)
    return im
