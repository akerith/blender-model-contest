exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
shirt=mat('REV Collo camicia',(.30,.33,.38),rough=.90)
teal=mat('REV Mantello teal',(.22,.34,.31),rough=.92)
seam=mat('REV Orlo teal',(.16,.26,.23),rough=.93)
parts=select_prefix('Fazzoletto piega')
for o in parts:
    transform(o,lambda p:(p.x*1.03,p.y*1.07,1.41+(p.z-1.42826)*(.05/.07174)))
    assign(o,shirt)
rings('REV Colletto camicia continuo',[(1.41,0,0,.061,.054),(1.435,0,0,.059,.054),(1.46,0,0,.057,.051)],shirt,'neck',24)
o=bpy.data.objects['Collo alto verde'];assign(o,teal)
for v in o.data.vertices:
    x,y,z=v.co;t=max(0,min(1,(z-1.4359)/.08259));front=max(0,min(1,-y/.053))
    v.co=(x*.96,y,1.40+t*(.12-.04*front))
o=bpy.data.objects['Bordo colletto'];assign(o,seam)
for v in o.data.vertices:
    x,y,z=v.co;front=max(0,min(1,-y/.053));v.co=(x*.96,y,1.520-.04*front+(z-1.5206)*.11)
log('Colletto camicia 1.41-1.46; collo mantello aperto davanti, 1.40-1.52 dietro e 1.48 agli angoli')
finish_group(3)
