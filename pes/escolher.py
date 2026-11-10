"""Seleção explícita e ajuste contínuo por índices de palavra."""
import re
from .util import episodio, ler, salvar, palavras


def pares(itens):
    out = {}
    for item in itens:
        if '=' not in item:
            raise ValueError('Use id=valor: ' + item)
        chave, valor = item.split('=', 1)
        out[chave] = valor
    return out


def rodar(a):
    pasta = episodio(a)
    arquivo = pasta / 'work/candidatos.json'
    candidatos = {c['id']: c for c in ler(arquivo)} if arquivo.exists() else {}
    pal = palavras(a)
    titulos, ajustes = pares(a.titulo), pares(a.ajustar)
    out = []
    for n, origem in enumerate(a.ids.split(','), 1):
        identificador = 's' + str(n)
        if origem == 'manual':
            if identificador not in ajustes:
                raise ValueError('Escolha manual exige --ajustar ' + identificador + '=ini:fim.')
            ini, fim = 0, 0
        else:
            if origem not in candidatos:
                raise ValueError('Candidato desconhecido: ' + origem)
            c = candidatos[origem]
            ini, fim = c['ini'], c['fim']
        if identificador in ajustes:
            ini, fim = map(int, ajustes[identificador].split(':'))
        if not 0 <= ini <= fim < len(pal):
            raise ValueError('Índices de ajuste inválidos.')
        padrao = ' '.join(re.sub(r'[^\w\s-]', '', w['w']) for w in pal[ini:fim + 1][:5])
        titulo = titulos.get(identificador, padrao).strip()
        if not titulo:
            raise ValueError('Título vazio.')
        out.append(dict(id=identificador, de=origem, ini=ini, fim=fim,
                        s=pal[ini]['s'], e=pal[fim]['e'], titulo=titulo))
    validos = {c['id'] for c in out}
    if (set(titulos) | set(ajustes)) - validos:
        raise ValueError('Título ou ajuste cita clip que não foi escolhido.')
    salvar(pasta / 'clips.json', {'clips': out})
    # Uma seleção nova exige uma decisão humana nova, mesmo reutilizando s1.
    salvar(pasta / 'revisao.json', {})
    print('Escolhidos:', ', '.join(c['id'] for c in out))
    return 0
