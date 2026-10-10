"""Foto → configuração visual aproximada. Nunca produz altura/peso/circunferências."""
import math

def avatar_from_renderer(renderer):
    points=renderer.get('pontos') or {}
    def point(name):
        p=points.get(name)
        if not isinstance(p,dict): return None
        x,y=p.get('x'),p.get('y')
        if not isinstance(x,(int,float)) or not isinstance(y,(int,float)) or not math.isfinite(x+y): return None
        return x,y
    def center(a,b):
        a,b=point(a),point(b)
        return ((a[0]+b[0])/2,(a[1]+b[1])/2) if a and b else None
    shoulders=center('ombro_esquerdo','ombro_direito')
    hips=center('quadril_esquerdo','quadril_direito')
    ankles=center('tornozelo_esquerdo','tornozelo_direito')
    if not renderer.get('pronto') or not all((shoulders,hips,ankles)):
        return {'aplicavel':False,'configuracao':{},'mensagem':'Não foi possível observar as proporções. Use a edição manual ou envie outra foto.'}
    torso=hips[1]-shoulders[1];legs=ankles[1]-hips[1];height=torso+legs
    if torso<=0 or legs<=0 or height<.3:
        return {'aplicavel':False,'configuracao':{},'mensagem':'Pose inadequada. Envie uma foto frontal, em pé e de corpo inteiro.'}
    left,right=point('ombro_esquerdo'),point('ombro_direito')
    width=abs(left[0]-right[0])/height;ratio=torso/height
    return {'aplicavel':True,'configuracao':{'porte_corporal':'estreito' if width<.23 else 'largo' if width>.31 else 'medio',
        'proporcao_tronco':'curto' if ratio<.36 else 'longo' if ratio>.44 else 'media',
        'proporcao_pernas':'longas' if ratio<.36 else 'curtas' if ratio>.44 else 'media'},
        'mensagem':'Proporções visuais aproximadas aplicadas ao seu avatar. Ajuste-as livremente; suas medidas continuam sendo informadas por você.',
        'origem':'landmarks_normalizados','usa_medida_fisica':False,'renderer':'2d'}
