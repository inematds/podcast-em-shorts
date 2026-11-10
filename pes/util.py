"""Arquivos locais, validações e metadados compartilhados."""
import json
import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def raiz(a):
    return Path(a.raiz).expanduser().resolve()


def ler(caminho):
    return json.loads(Path(caminho).read_text(encoding='utf-8'))


def salvar(caminho, valor):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + '.tmp')
    temporario.write_text(json.dumps(valor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporario.replace(caminho)


def marca(a):
    return ler(raiz(a) / 'marca/marca.json')


def episodio(a, exigir=True):
    if not re.fullmatch(r'[a-z0-9-]+', a.ep):
        raise ValueError('Episódio deve usar somente letras minúsculas, números e hífen.')
    pasta = raiz(a) / 'episodios' / a.ep
    if exigir and not (pasta / 'ep.json').is_file():
        raise ValueError('Episódio não encontrado: ' + a.ep)
    return pasta


def executar(cmd, timeout=120):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError('Comando falhou: ' + str(cmd[0]) + '\n' + p.stderr[-2400:])
    return p.stdout


def ffprobe(video):
    return json.loads(executar(['ffprobe', '-v', 'error', '-show_streams',
                               '-show_format', '-of', 'json', video]))


def clips(a):
    return ler(episodio(a) / 'clips.json')['clips']


def clip(a, identificador):
    for item in clips(a):
        if item['id'] == identificador:
            return item
    raise ValueError('Clip desconhecido: ' + identificador)


def palavras(a):
    itens = ler(episodio(a) / 'work/palavras.json')
    if not itens:
        raise ValueError('Transcrição vazia.')
    for i, w in enumerate(itens):
        if (w['i'] != i or not str(w['w']).strip() or not 0 <= w['s'] < w['e']
                or (i and w['s'] < itens[i - 1]['s'])):
            raise ValueError('Palavras inválidas no índice ' + str(i))
    return itens


def fim_frase(texto):
    return bool(re.search(r'[.?!]$', texto.strip()))


def cruzam(a, b):
    x, y, w, h = a
    bx, by, bw, bh = b
    return x < bx + bw and bx < x + w and y < by + bh and by < y + h
