"""Rubrica simples de clareza para fala e título."""
import json
import re
from .candidatos import MULETAS, PADROES


def avaliar(falado, titulo):
    tokens = falado.split()
    primeira = tokens[0].lower().strip('.,;!?') if tokens else ''
    concreto = bool(re.search(r'\b(você|empresa|loja|pessoa|equipe|pedidos|horas|cliente|funcionário|eu|nós)\w*\b', falado, re.I))
    criterios_fala = [
        (bool(tokens) and len(tokens) <= 18, 2, 'Até 18 palavras'),
        (primeira not in MULETAS and bool(tokens), 3, 'Entrada sem muleta'),
        (concreto, 3, 'Sujeito ou objeto concreto'),
        (bool(re.search(PADROES['numero'] + '|' + PADROES['voce'], falado, re.I)), 2, 'Número ou você'),
    ]
    forte = r'\b(\d+|horas|perde|fora|erro|segredo|problema|tempo|como|evite|custa|muda|ganha|nunca)\b'
    criterios_titulo = [
        (0 < len(titulo.split()) <= 7, 2, 'Até 7 palavras'),
        (0 < len(titulo) <= 40, 2, 'Até 40 caracteres'),
        ('...' not in titulo and '…' not in titulo, 2, 'Sem reticências'),
        (not titulo.islower() or bool(re.search(r'\d', titulo)), 2, 'Inicial destacada ou número'),
        (bool(re.search(forte, titulo, re.I)), 2, 'Palavra concreta ou forte'),
    ]
    def nota(criterios):
        return {'nota': sum(p for ok, p, _ in criterios if ok),
                'motivos': [('ok: ' if ok else 'rever: ') + txt for ok, _, txt in criterios]}
    f, t = nota(criterios_fala), nota(criterios_titulo)
    return {'falado': f, 'titulo': t, 'passa': f['nota'] >= 6 and t['nota'] >= 6}


def rodar(a):
    r = avaliar(a.falado, a.titulo)
    if a.json:
        print(json.dumps(r, ensure_ascii=False))
    else:
        for campo in ('falado', 'titulo'):
            print(campo, str(r[campo]['nota']) + '/10:', '; '.join(r[campo]['motivos']))
    return 0 if r['passa'] else 1
