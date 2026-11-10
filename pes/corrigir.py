"""Correções literais por palavra, preservando índices, tempos e pontuação."""
import re
from .util import episodio, palavras, ler, salvar


def rodar(a):
    pasta, pal = episodio(a), palavras(a)
    inicio = a.de if a.de is not None else 0
    fim = a.ate if a.ate is not None else len(pal) - 1
    if not 0 <= inicio <= fim < len(pal):
        raise ValueError('Índices de correção inválidos (limites inclusivos).')
    trocas = {}
    for item in a.trocar:
        origem, separador, destino = item.partition('=')
        if not separador or not origem or not destino or any(c.isspace() for c in origem + destino):
            raise ValueError('Use --trocar palavra=palavra, sem espaços ou texto vazio.')
        if not origem.isalnum() or not destino.isalnum():
            raise ValueError('A troca deve conter somente a palavra; a pontuação será preservada.')
        if origem in trocas and trocas[origem] != destino:
            raise ValueError('Trocas conflitantes para: ' + origem)
        trocas[origem] = destino
    alterados = set()
    for w in pal[inicio:fim + 1]:
        partes = re.fullmatch(r'([^\w]*)(\w+)([^\w]*)', w['w'])
        if partes and partes[2] in trocas and trocas[partes[2]] != partes[2]:
            w['w'] = partes[1] + trocas[partes[2]] + partes[3]
            alterados.add(w['i'])
    if alterados:
        salvar(pasta / 'work/palavras.json', pal)
        # Uma alteração no texto exige render e aprovação novos dos cortes afetados.
        if (pasta / 'clips.json').exists() and (pasta / 'revisao.json').exists():
            revisao = ler(pasta / 'revisao.json')
            for c in ler(pasta / 'clips.json')['clips']:
                if any(c['ini'] <= i <= c['fim'] for i in alterados):
                    revisao.pop(c['id'], None)
            salvar(pasta / 'revisao.json', revisao)
    print(len(alterados), 'palavras trocadas')
    return 0
