exec(compile(open(r'C:\Users\USER\gara-modelli\concorrenti\gpt-astra\lavoro\rev_util.py',encoding='utf-8').read(),'rev_util','exec'))
o=bpy.data.objects['Bacino pantaloni']
fit(o,(-.17,-.11,.86),(.17,.11,1.04))
log('Corretto il cavallo a Z 0.86; piedi centrati X +/-0.13; spalla/gomito/polso 1.40/1.18/0.99')
finish_group(1)
