"""Comparação explicável de medidas declaradas. Nunca mede fotografias."""
from app.services.vestibilidade_avatar import gerar_vestibilidade_avatar_v1
from app.services.recomendacao import recomendar_tamanho

# Os dados do catálogo representam largura da peça aberta OU circunferência explícita.
# Não se compara projeção frontal de foto com circunferência corporal.
AXES = {
 'camiseta': [('torax_cm','torax_cm',8),('ombros_cm','ombros_cm',2)],
 'calca': [('cintura_cm','cintura_cm',3),('quadril_cm','quadril_cm',5)],
 'short': [('cintura_cm','cintura_cm',3),('quadril_cm','quadril_cm',5)],
 'saia': [('cintura_cm','cintura_cm',3),('quadril_cm','quadril_cm',5)],
 'vestido': [('torax_cm','torax_cm',6),('cintura_cm','cintura_cm',5),('quadril_cm','quadril_cm',6)],
 'calcado': [('pe_cm','pe_cm',0.8)],
}
LABELS={'torax_cm':'Tórax','cintura_cm':'Cintura','quadril_cm':'Quadril','ombros_cm':'Ombros','pe_cm':'Comprimento do pé'}


def compare(product,variant,profile,preference='padrao'):
    measured=profile.get('medidas',{})
    items=[]
    for size in variant['tamanhos']:
        measures=size.get('medidas') or {}
        reasons=[]; errors=[]; tight=False; snug=False; wide=False
        for body_key,garment_key,target in AXES.get(product['categoria'],[]):
            body=measured.get(body_key); garment=measures.get(garment_key)
            if garment is None and garment_key=='torax_cm' and measures.get('largura_cm'):
                garment=measures['largura_cm']*2
            if body is None or garment is None: continue
            target *= {'justo':0.5,'slim':0.75,'padrao':1,'solto':1.6,'largo':1.95,'oversized':2.3}.get(preference,1)
            if product['categoria']=='camiseta' and body_key=='torax_cm' and variant.get('modelagem')=='oversized': target+=4
            gap=garment-body
            tolerance=0.5 if body_key=='pe_cm' else max(3,target)
            errors.append(abs(gap-target)/tolerance)
            tight |= gap < (0.3 if body_key=='pe_cm' else 0)
            snug |= gap < target * 0.5
            wide |= gap > target + (0.5 if body_key=='pe_cm' else max(2,target*0.3))
            reasons.append(f'{LABELS[body_key]}: peça {garment:g} cm, medida informada {body:g} cm; diferença {gap:+g} cm.')
        status='Sem medidas suficientes'
        if errors: status='Mais justo' if tight or snug else ('Mais amplo' if wide else 'Equilibrado')
        legacy={'id':size['legacy_product_id'],'nome':product['nome'],'categoria':product['categoria'],
                'tamanho':size['label'],'modelagem':variant.get('modelagem'),**measures}
        visual=gerar_vestibilidade_avatar_v1(profile,legacy,size['label'])
        items.append({'size_id':size['id'],'tamanho':size['label'],'medidas':measures,'estoque':size['estoque'],
                      'legacy_product_id':size['legacy_product_id'],'caimento':status,'motivos':reasons,
                      'score':sum(errors)/len(errors) if errors else None,
                      'eixos_comparados':len(errors),'apertado':tight,'visual':visual})
    candidates=[i for i in items if i['score'] is not None and not i['apertado'] and i['estoque']!=0]
    candidates.sort(key=lambda i:(i['apertado'],i['score']))
    recommendation=None
    if candidates:
        best=candidates[0]
        axes=len(AXES.get(product['categoria'],[]))
        complete=best['eixos_comparados']==axes
        recommendation={'tamanho':best['tamanho'],'size_id':best['size_id'],'origem':'medidas_informadas',
                        'confianca':'Moderada' if complete else 'Limitada',
                        'motivos':best['motivos'],'mensagem':'Comparação das medidas informadas com a tabela desta peça. Não é garantia de ajuste.',
                        'alternativa':candidates[1]['tamanho'] if len(candidates)>1 and abs(candidates[1]['score']-best['score'])<0.25 else None}
    # Compatibilidade com a sugestão antiga, claramente aproximada e só para roupas.
    elif not any(i['eixos_comparados'] for i in items) and product['categoria'] not in ('calcado','bone') and profile.get('altura_aproximada_cm') and profile.get('peso_aproximado_kg'):
        available=[i['tamanho'] for i in items if i['estoque']!=0]
        if available:
            suggested=recomendar_tamanho(profile['altura_aproximada_cm'],profile['peso_aproximado_kg'],preferencia_caimento={'slim':'justo','largo':'solto'}.get(preference,preference),grade_tamanhos=available)
            label=suggested.get('tamanho_recomendado') if isinstance(suggested,dict) else suggested
            best=next((i for i in items if i['tamanho']==label),None)
            if best: recommendation={'tamanho':label,'size_id':best['size_id'],'origem':'estimativa_legada','confianca':'Baixa',
                'motivos':['Sugestão inicial baseada em altura e peso informados, sem comparação de circunferências.'],
                'mensagem':'Informe medidas corporais para refinar. O avatar é uma ilustração aproximada.','alternativa':None}
    message='Nenhuma opção em estoque atende às medidas comparadas. Confira a tabela ou outra peça.' if any(i['eixos_comparados'] for i in items) and not recommendation else 'Informe medidas pertinentes à categoria para comparar com a tabela da peça.'
    return {'tamanhos':items,'recomendacao':recommendation,'mensagem':message,'renderer':'2d','simulacao_fisica':False}
