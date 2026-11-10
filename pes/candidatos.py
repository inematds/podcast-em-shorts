"""Frases inteiras e sinais editoriais explicáveis; não prevê audiência."""
import json
import re
from .util import episodio, marca, palavras, fim_frase, salvar

MULETAS = {'então', 'né', 'tipo', 'aí', 'é', 'bom', 'e'}
PADROES = {
    'numero': r'\b(?:\d+|um|uma|dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cem|mil)\b',
    'voce': r'\b(?:você|seu|sua|teu)\b',
    'virada': r'\b(?:mas|só que|na verdade|o problema é|ninguém fala|o segredo)\b',
    'pergunta': r'\?',
    'veredito': r'\b(?:ou seja|resumindo|a lição|no fim das contas|portanto)\b',
    'exemplo': r'\b(?:por exemplo|imagina|olha isso|vou mostrar)\b',
}
ALERTAS = {
    'referencia_atras': r'\b(?:como eu falei|como eu disse|lá atrás|ontem|na live passada)\b',
    'depende_tela': (r'\b(?:vocês estão vendo|olha isso aqui|deixa eu (?:ver|abrir)|' 
                     r'clica aqui|essa imagem aqui|vamos dar uma olhada|tá aqui|isso aqui|'
                     r'olha só|(?:queria|quero|vou|posso) mostrar|tenho que dar uma olhada|'
                     r'aqui no chat|mensagens aqui)\b'),
    'chamada': r'\b(?:se inscreve|inscreva|link na descrição|comenta aí|deixa o like)\b',
}


def sinais(texto):
    bons = [k for k, p in PADROES.items() if re.search(p, texto, re.I)]
    ruins = [k for k, p in ALERTAS.items() if re.search(p, texto, re.I)]
    tokens = texto.split()
    if any(w[:1].isupper() and not fim_frase(tokens[i - 1]) for i, w in enumerate(tokens) if i):
        bons.append('nome')
    if len(re.findall(r'\b(?:aqui|ó)\b', texto, re.I)) >= 3 and 'depende_tela' not in ruins:
        ruins.append('depende_tela')
    if tokens[0][:1].islower():
        ruins.append('inicio_meio')
    if tokens[0].lower().strip('.,!?;:') in MULETAS:
        ruins.append('muleta_inicio')
    if not fim_frase(tokens[-1]):
        ruins.append('sem_fechamento')
    return bons, ruins



def pontuar(texto, duracao, bons, ruins):
    # Cada sinal conta no máximo uma vez por frase: repetição não infla a nota.
    frases = [f for f in re.split(r'(?<=[.!?])\s+', texto) if f.strip()]
    pesos = dict(numero=2.5, voce=.7, virada=3.5, pergunta=1., veredito=3., exemplo=1.)
    carga = sum(pesos[k] * sum(bool(re.search(p, f, re.I)) for f in frases)
                for k, p in PADROES.items())
    quantidade = max(len(frases), len(texto.split()) / 15)
    nota = carga / quantidade + carga / max(1, duracao / 10)
    if 'veredito' in bons and re.search(PADROES['veredito'], ' '.join(texto.split()[-18:]), re.I):
        nota += 4
    if 'nome' in bons:
        nota += .5
    descontos = dict(inicio_meio=5, depende_tela=7, referencia_atras=4,
                     chamada=5, muleta_inicio=2, sem_fechamento=4)
    return round(nota - sum(descontos[k] for k in ruins), 3)

def gerar(pal, m, top):
    if top < 1:
        raise ValueError('--top deve ser positivo.')
    frases, inicio = [], 0
    for i, w in enumerate(pal):
        pausa = i + 1 < len(pal) and pal[i + 1]['s'] - w['e'] > .8
        if fim_frase(w['w']) or pausa or i == len(pal) - 1:
            frases.append((inicio, i))
            inicio = i + 1
    possiveis = []
    for j, (ini, _) in enumerate(frases):
        for _, fim in frases[j:]:
            dur = pal[fim]['e'] - pal[ini]['s']
            if dur > m['duracao']['max']:
                break
            if dur < m['duracao']['min']:
                continue
            texto = ' '.join(w['w'] for w in pal[ini:fim + 1])
            bons, ruins = sinais(texto)
            nota = pontuar(texto, dur, bons, ruins)
            possiveis.append(dict(ini=ini, fim=fim, s=pal[ini]['s'], e=pal[fim]['e'],
                                  duracao=dur, nota=float(nota), sinais=bons, alertas=ruins, texto=texto))
    possiveis.sort(key=lambda c: (-c['nota'], c['duracao'], c['ini']))
    escolhidos = []
    for c in possiveis:
        if any(max(0, min(c['e'], b['e']) - max(c['s'], b['s'])) >
               .5 * min(c['duracao'], b['duracao']) + 1e-8 for b in escolhidos):
            continue
        c['id'] = f'c{len(escolhidos) + 1:02d}'
        escolhidos.append(c)
        if len(escolhidos) == top:
            break
    return escolhidos


def rodar(a):
    resultado = gerar(palavras(a), marca(a), a.top)
    salvar(episodio(a) / 'work/candidatos.json', resultado)
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False))
    else:
        for c in resultado:
            print(f"{c['id']}  {c['s']:.2f}–{c['e']:.2f}s  nota {c['nota']:.1f}  "
                  + ', '.join(c['alertas']) + '\n  ' + c['texto'])
        if not resultado:
            print('Nenhum trecho dentro da duração da marca.')
    return 0
