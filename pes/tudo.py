"""Pipeline local com reprovações explícitas e parada em erro de infraestrutura."""
from types import SimpleNamespace
from . import transcrever, candidatos, escolher, layout, render, quadros, conteudo
from .util import episodio, marca, ler, salvar, clips


def rodar(a):
    pasta = episodio(a)
    def argumentos(**kw):
        return SimpleNamespace(**(vars(a) | kw))
    rc = transcrever.rodar(a)
    if rc:
        return rc
    candidatos.rodar(argumentos(top=12, json=False))
    lista = ler(pasta / 'work/candidatos.json')
    bons = [c for c in lista if not c['alertas']][:marca(a)['shorts_por_episodio']]
    if not bons:
        raise ValueError('Nenhum candidato sem alertas. Revise os trechos manualmente.')
    escolher.rodar(argumentos(ids=','.join(c['id'] for c in bons), titulo=[], ajustar=[]))
    layout.rodar(argumentos(forcar=None, json=False))
    render.rodar(argumentos(ids=[], todos=True))
    resumo = []
    for c in clips(a):
        mp4 = pasta / 'clips' / (c['id'] + '.mp4')
        q = quadros.verificar(argumentos(mp4=str(mp4), legendas=str(mp4.with_suffix('.legendas.json')), fps=2))
        salvar(mp4.with_suffix('.quadros.json'), q)
        itens = conteudo.verificar(a, c)
        co = {'ok': all(itens.values()), 'itens': itens}
        salvar(pasta / 'work' / (c['id'] + '.conteudo.json'), co)
        resumo.append({'id': c['id'], 'quadros': q, 'conteudo': co})
        print(c['id'] + ': quadros ' + ('OK' if q['ok'] else 'REPROVADO')
              + '; conteúdo ' + ('OK' if co['ok'] else 'REPROVADO'))
    salvar(pasta / 'work/resumo.json', resumo)
    import shlex
    from .util import RAIZ
    print('Revisão: python3 ' + shlex.quote(str(RAIZ / 'pes.py')) + ' revisao ' + a.ep
          + ' --raiz ' + shlex.quote(str(a.raiz)))
    return 0 if all(r['quadros']['ok'] and r['conteudo']['ok'] for r in resumo) else 1
