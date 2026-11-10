"""Verifica fronteiras, continuidade, duração e chamadas no texto selecionado."""
import json
from .util import palavras, clip, marca, episodio, fim_frase, salvar
from .candidatos import sinais


def verificar(a, c):
    pal, m = palavras(a), marca(a)
    ini, fim = c['ini'], c['fim']
    if not 0 <= ini <= fim < len(pal):
        return {'indices': False}
    trecho = pal[ini:fim + 1]
    _, alertas = sinais(' '.join(w['w'] for w in trecho))
    fronteira = ini == 0 or fim_frase(pal[ini - 1]['w']) or pal[ini]['s'] - pal[ini - 1]['e'] > .8
    return {
        'inicio_frase': fronteira,
        'sem_muleta': 'muleta_inicio' not in alertas,
        'fechamento': fim_frase(trecho[-1]['w']),
        'sem_chamada': 'chamada' not in alertas,
        'duracao': m['duracao']['min'] <= c['e'] - c['s'] <= m['duracao']['max'],
        'continuo': (abs(c['s'] - trecho[0]['s']) < .01
                     and abs(c['e'] - trecho[-1]['e']) < .01
                     and [w['i'] for w in trecho] == list(range(ini, fim + 1))),
    }


def rodar(a):
    itens = verificar(a, clip(a, a.id))
    resultado = {'ok': all(itens.values()), 'itens': itens}
    salvar(episodio(a) / 'work' / (a.id + '.conteudo.json'), resultado)
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False))
    elif resultado['ok']:
        print('CONTEUDO OK')
    else:
        print('CONTEUDO FALHOU: ' + ', '.join(k for k, v in itens.items() if not v))
    return 0 if resultado['ok'] else 1
