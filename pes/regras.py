"""Transforma uma instrução explícita ou última nota em regra pessoal."""
import re
from types import SimpleNamespace
from .util import raiz, episodio, ler


def rodar(a):
    texto = a.texto
    if a.da_nota:
        ep, identificador = a.da_nota
        pasta = episodio(SimpleNamespace(ep=ep, raiz=a.raiz))
        estado = ler(pasta / 'revisao.json')
        notas = estado.get(identificador, {}).get('notas', [])
        if not notas:
            raise ValueError('Este clip não tem nota de revisão.')
        texto = notas[-1]['texto']
    if not texto or not texto.strip():
        raise ValueError('Informe o texto da regra ou --da-nota EP ID.')
    caminho = raiz(a) / 'regras/MINHAS-REGRAS.md'
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conteudo = caminho.read_text(encoding='utf-8') if caminho.exists() else ''
    usados = [int(x) for x in re.findall(r'^## R(\d+)\b', conteudo, re.M)]
    numero = max([199] + usados) + 1
    texto = ' '.join(texto.split())
    motivo = ' '.join(a.por_que.split())
    with caminho.open('a', encoding='utf-8') as f:
        if not caminho.exists() or not conteudo:
            f.write('# Minhas regras\n')
        f.write(f'\n## R{numero} — {texto}\nPor quê: {motivo}\nQuem checa: {a.quem}\n')
    print('R' + str(numero))
    return 0
