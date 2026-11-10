"""Blocos em uma linha, geometria medida e karaokê ASS por palavra."""
from PIL import ImageFont
from .util import cruzam


def fonte(m, raiz, tamanho):
    return ImageFont.truetype(str(raiz / m['fonte']), tamanho)


def blocos(pal, c, m):
    grupos, grupo = [], []
    cfg = m['legenda']
    for w in pal[c['ini']:c['fim'] + 1]:
        if len(w['w']) > cfg['max_caracteres']:
            raise ValueError('Palavra excede o limite de caracteres: ' + w['w'])
        texto = ' '.join(x['w'] for x in grupo + [w])
        if grupo and (len(grupo) >= cfg['max_palavras'] or len(texto) > cfg['max_caracteres']
                      or w['s'] - grupo[-1]['e'] > .8):
            grupos.append(grupo)
            grupo = []
        grupo.append(w)
    if grupo:
        grupos.append(grupo)
    return grupos


def medir(texto, m, raiz, tamanho, y, max_largura=None):
    margem = m['legenda']['contorno'] + 4
    limite = max_largura or 1080 * (1 - 2 * m['area_segura']['lados'])
    while tamanho > 12:
        f = fonte(m, raiz, tamanho)
        w = f.getlength(texto) + 2 * margem
        if w <= limite:
            break
        tamanho -= 1
    if w > limite:
        raise ValueError('Texto não cabe na área segura.')
    # Métrica tipográfica completa, incluindo contorno e descendentes.
    subida, descida = f.getmetrics()
    h = subida + descida + 2 * margem
    return tamanho, [round((1080 - w) / 2), round(y), round(w), round(h)]


def cor(valor):
    r, g, b = valor.lstrip('#')[0:2], valor.lstrip('#')[2:4], valor.lstrip('#')[4:6]
    return '&H00' + b + g + r + '&'


def tempo(t):
    cent = max(0, round(t * 100))
    return f'{cent // 360000}:{cent // 6000 % 60:02d}:{cent // 100 % 60:02d}.{cent % 100:02d}'


def escapar(texto):
    return texto.replace('\\', '＼').replace('{', '｛').replace('}', '｝').replace('\n', ' ')


def titulo_linhas(texto, m, raiz):
    palavras = texto.split()
    for tam in range(80, 79, -1):
        if fonte(m, raiz, tam).getlength(texto) <= 920:
            return [texto], tam
    for tam in range(80, 79, -1):
        f = fonte(m, raiz, tam)
        opcoes = [(' '.join(palavras[:i]), ' '.join(palavras[i:]))
                  for i in range(1, len(palavras))]
        if opcoes:
            linhas = min(opcoes, key=lambda par: max(f.getlength(t) for t in par))
            if max(f.getlength(t) for t in linhas) <= 920:
                return list(linhas), tam
    raise ValueError('Título não cabe em duas linhas com fonte de 80 px.')


def criar(pal, c, lay, rosto, m, raiz, destino):
    cores = m['cores']
    nome_fonte = fonte(m, raiz, m['legenda']['tamanho']).getname()[0]
    largura_util = 1080 * (1 - 2 * m['area_segura']['lados'])
    y_leg = 1030 if lay == 'tela+camera' else 1370
    eventos, resultado = [], []
    def evento(s, e, texto, caixa, tamanho, estilo='Legenda'):
        if e <= s:
            return
        x, y, w, _ = caixa
        tags = f'{{\\an8\\pos({x + w / 2:.1f},{y + m["legenda"]["contorno"] + 4})\\fs{tamanho}}}'
        eventos.append(f'Dialogue: 0,{tempo(s)},{tempo(e)},{estilo},,0,0,0,,{tags}{texto}')
    for grupo in blocos(pal, c, m):
        texto = ' '.join(w['w'] for w in grupo)
        tam, caixa = medir(texto, m, raiz, m['legenda']['tamanho'], y_leg)
        if lay == 'tela+camera':
            caixa[1] = round(960 + (140-caixa[3])/2)
        if rosto and cruzam(caixa, rosto):
            raise ValueError('Legenda cruza o rosto; reveja o layout.')
        inicio, fim = max(0, grupo[0]['s'] - c['s']), grupo[-1]['e'] - c['s']
        resultado.append({'s': inicio, 'e': fim, 'texto': texto, 'caixa': caixa})
        # Estados explícitos: só a palavra cujo intervalo está ativo é amarela.
        limites = sorted({inicio, fim} | {max(inicio, min(fim, w[k] - c['s']))
                                          for w in grupo for k in ('s', 'e')})
        for s, e in zip(limites, limites[1:]):
            meio = (s + e) / 2 + c['s']
            partes = []
            for w in grupo:
                valor = cores['destaque'] if w['s'] <= meio < w['e'] else cores['texto']
                partes.append('{\\c' + cor(valor) + '}' + escapar(w['w']))
            evento(s, e, ' '.join(partes), caixa, tam)
    linhas, tam = titulo_linhas(c['titulo'], m, raiz)
    f_titulo = fonte(m, raiz, tam)
    passo = max(f_titulo.getbbox(t)[3]-f_titulo.getbbox(t)[1] for t in linhas) + 24
    y = 12 if lay == 'tela+camera' else 192
    medidas = [medir(t, m, raiz, tam, y+i*passo, largura_util)[1]
               for i, t in enumerate(linhas)]
    caixa = [min(b[0] for b in medidas), y, max(b[2] for b in medidas), passo*len(linhas)]
    if rosto and cruzam(caixa, rosto):
        raise ValueError('Título cruza o rosto; reveja o layout.')
    titulo = {'s': 0, 'e': min(m['titulo_segundos'], c['e'] - c['s']),
              'caixa': caixa, 'tamanho': tam, 'linhas': linhas}
    # Maior palavra de conteúdo é a ênfase determinística do título.
    forte = max(c['titulo'].split(), key=len)
    bx, by, bw, bh = caixa
    tags = (f'{{\\an7\\pos({bx-10},{by})\\p1\\bord0\\shad0'
            f'\\c{cor(cores["fundo"])}\\alpha&H55&}}')
    eventos.append(f'Dialogue: 0,0:00:00.00,{tempo(titulo["e"])},Titulo,,0,0,0,,{tags}'
                   f'm 0 0 l {bw+20} 0 l {bw+20} {bh} l 0 {bh}')
    for linha, medida in zip(linhas, medidas):
        texto = ' '.join('{\\c'+cor(cores['destaque'] if w == forte else cores['texto'])+'}'
                         + escapar(w) for w in linha.split())
        evento(0, titulo['e'], texto, medida, tam, 'Titulo')
    cabecalho = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n'
                 'WrapStyle: 2\nScaledBorderAndShadow: yes\n[V4+ Styles]\n'
                 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, '
                 'BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, '
                 'BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
    for estilo in ('Legenda', 'Titulo'):
        cabecalho += (f'Style: {estilo},{nome_fonte},72,{cor(cores["texto"])},'
                      f'{cor(cores["destaque"])},{cor(cores["contorno"])},{cor(cores["fundo"])},'
                      f'-1,0,0,0,100,100,0,0,1,{m["legenda"]["contorno"]},0,8,0,0,0,1\n')
    cabecalho += '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    destino.write_text(cabecalho + '\n'.join(eventos) + '\n', encoding='utf-8')
    return {'blocos': resultado, 'titulo': titulo, 'rosto_esperado': rosto, 'layout': lay}
