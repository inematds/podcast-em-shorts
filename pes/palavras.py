"""Consulta legível da transcrição, preservando índices para escolha manual."""
import math
import unicodedata
from .util import palavras, fim_frase


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.casefold())
                   if unicodedata.category(c) != 'Mn')


def rodar(a):
    for limite in (a.de, a.ate):
        if limite is not None and (not math.isfinite(limite) or limite < 0):
            raise ValueError('--de e --ate devem ser segundos finitos não negativos.')
    if a.de is not None and a.ate is not None and a.de > a.ate:
        raise ValueError('--de não pode ser maior que --ate.')
    pal = palavras(a)
    busca = normalizar(a.busca or '')
    inicio, exibidas = 0, 0
    for i, w in enumerate(pal):
        pausa = i + 1 < len(pal) and pal[i + 1]['s'] - w['e'] > .8
        if not (fim_frase(w['w']) or pausa or i == len(pal) - 1):
            continue
        primeira = pal[inicio]
        texto = ' '.join(p['w'] for p in pal[inicio:i + 1])
        inicio = i + 1
        if ((a.de is not None and w['e'] < a.de)
                or (a.ate is not None and primeira['s'] > a.ate)
                or busca not in normalizar(texto)):
            continue
        decimos = round(primeira['s'] * 10)
        minutos, resto = divmod(decimos, 600)
        print(f"[{primeira['i']}] {minutos:02d}:{resto / 10:04.1f}  {texto}[{w['i']}]")
        exibidas += 1
    if not exibidas:
        print('Nenhuma frase encontrada para os filtros informados.')
    return 0
