"""Render determinístico CPU via ffmpeg, com áudio original e ASS temporizado."""
import time
import math
from pathlib import Path
from .util import episodio, ler, marca, palavras, raiz, salvar, executar, clips
from .legenda import criar, titulo_linhas, fonte
from .rostos import proteger_cabeca
from .tela import expressao
from .miniatura import gerar as gerar_miniatura


def par(n):
    return max(2, int(n) // 2 * 2)


def filtro_corte(caixa):
    x, y, w, h = caixa
    return f'crop={int(w)}:{int(h)}:{int(x)}:{int(y)}'


def sem_moldura(video, lay, c):
    """Retira só borda branca contínua confirmada em três quadros da webcam."""
    import cv2
    import numpy as np
    x, y, w, h = map(int, lay['camera'])
    captura, quadros = cv2.VideoCapture(str(video)), []
    try:
        for fracao in (0, .5, .9):
            captura.set(cv2.CAP_PROP_POS_MSEC, (c['s']+fracao*(c['e']-c['s']))*1000)
            ok, q = captura.read()
            if not ok:
                raise ValueError('Falha ao conferir moldura da webcam.')
            quadros.append(q[y:y+h, x:x+w])
    finally:
        captura.release()
    cortes = []
    for eixo, inverso in ((0, False), (0, True), (1, False), (1, True)):
        linhas = [np.moveaxis(q, eixo, 0)[::(-1 if inverso else 1)] for q in quadros]
        n = 0
        while n < min(6, len(linhas[0])//4) and all(
                (a[n].min(axis=1) > 200).mean() >= .98 for a in linhas):
            n += 1
        cortes.append(n)
    topo, base, esquerda, direita = cortes
    return dict(lay, camera=[x+esquerda, y+topo, w-esquerda-direita, h-topo-base])


def tela(caixa, altura, prefixo, reserva=0, rodape=0):
    _, _, w, h = caixa
    escala = min(1080 / w, (altura - reserva - rodape) / h)
    fw, fh = par(w * escala), par(h * escala)
    return (f'[src{prefixo}]{filtro_corte(caixa)},split=2[{prefixo}a][{prefixo}b];'
            f'[{prefixo}a]scale=144:128,boxblur=12:2,scale=1080:{altura}[{prefixo}bg];'
            f'[{prefixo}b]scale={fw}:{fh}[{prefixo}fg];'
            f'[{prefixo}bg][{prefixo}fg]overlay=(W-w)/2:{reserva}+(H-{reserva}-{rodape}-h)/2[{prefixo}]')


def pan(lay, c, largura_crop, eixo=0, folga=0, total=None, alvo=None):
    """Interpola centros suavizados com velocidade limitada em pixels de origem."""
    dimensao = lay['largura'] if eixo == 0 else lay['altura']
    maximo = (total or dimensao) - largura_crop
    alvo = largura_crop / 2 if alvo is None else alvo
    pontos, anterior = [], None
    for obs in lay.get('trilha', []):
        t = obs['t'] - c['s']
        x = max(0, min(maximo, obs['centro'][eixo] + folga - alvo))
        if anterior:
            limite = dimensao * .06 * max(.001, t - anterior[0])
            x = max(anterior[1] - limite, min(anterior[1] + limite, x))
        pontos.append((t, x))
        anterior = (t, x)
    if not pontos:
        f = lay['rosto_medio']
        return str(max(0, min(maximo, f[eixo] + f[eixo + 2] / 2 + folga - alvo)))
    expr = f'{pontos[-1][1]:.3f}'
    for (t0, x0), (t1, x1) in reversed(list(zip(pontos, pontos[1:]))):
        reta = f'({x0:.3f}+({x1-x0:.3f})*clip((t-({t0:.6f}))/{t1-t0:.6f},0,1))'
        expr = f'if(lt(t,{t1:.6f}),{reta},{expr})'
    return expr


def recorte_camera(lay, c, m, pasta_marca):
    """Uma caixa fixa e inteira dentro da webcam, inclusive após arredondar."""
    x, y, w, h = lay['camera']
    fx, fy, fw, fh = lay['rosto_medio']
    # Após limpar a moldura, preservar o topo: o cabelo pode chegar até ele.
    x0, y0 = math.ceil(x / 2) * 2, math.ceil(y / 2) * 2
    x1, y1 = int((x+w) // 2) * 2, int((y+h) // 2) * 2
    if x1-x0 < 2 or y1-y0 < 2:
        raise ValueError('Webcam pequena demais para recorte seguro.')
    linhas, tam = titulo_linhas(c['titulo'], m, pasta_marca)
    f = fonte(m, pasta_marca, tam)
    passo = max(f.getbbox(t)[3]-f.getbbox(t)[1] for t in linhas)+8
    fim_titulo = math.ceil(1920*m['area_segura']['topo']) + passo*len(linhas)
    # Face >= 300 px, título acima do cabelo com a mesma margem do checker.
    # Reduzir o recorte inferior permite deslocar a pessoa sem sair da webcam.
    escala = 302/fh
    cabelo = lay.get('cabelo_min', fy-.25*fh)-y0
    queixo = lay.get('queixo_max', fy+fh)-y0
    minimo_y = max(0, fim_titulo+1920*.04+10-cabelo*escala)
    maximo_y = 974-1920*.04-2-queixo*escala
    if minimo_y > maximo_y:
        raise ValueError(f'Sem enquadramento seguro: y mínimo {minimo_y:.1f} > '
                         f'máximo {maximo_y:.1f}; título termina em {fim_titulo}px.')
    dy = math.ceil((minimo_y+maximo_y)/2)
    ch = par(min(y1-y0, (944-dy)/escala))
    cw = min(x1-x0, par(1080/escala))
    if ch < fy-y0+fh or cw < fw:
        raise ValueError('Webcam sem espaço para título seguro e cabeça inteira; ajuste a gravação.')
    # Ancorar no topo preserva o cabelo mesmo quando a pessoa se levanta.
    cy = y0
    cx = max(x0, min(x1-cw, int((fx+fw/2-cw/2) // 2)*2))
    dw, dh = par(cw*escala), par(ch*escala)
    # A folga inferior mantém o queixo protegido longe da faixa de legenda.
    return [cx, cy, cw, ch], [dw, dh, (1080-dw)//2, dy]


def geometria(lay, c, m, pasta_marca=None):
    modo, face = lay['modo'], lay['rosto_medio']
    rosto = None
    if modo == 'tela+camera':
        camera, (dw, dh, dx, dy) = recorte_camera(
            lay, c, m, pasta_marca or Path(__file__).resolve().parents[1])
        fx, fy, fw, fh = face
        cx, cy, cw, ch = camera
        rosto = [dx+(fx-cx)*dw/cw, dy+(fy-cy)*dh/ch, fw*dw/cw, fh*dh/ch]
        tm = m.get('tela_modo', 'auto')
        if tm not in ('auto', 'inteira', 'preencher'):
            raise ValueError('tela_modo deve ser auto, inteira ou preencher.')
        fundo = m['cores']['fundo']
        if tm == 'inteira':
            baixo = tela(lay['tela'], 820, 'baixo')
        else:
            _, _, tw, th = lay['tela']
            crop_h = par(min(th, tw*820/1080))
            crop_w = par(crop_h*1080/820)
            ex = expressao(lay.get('trilha_tela', []), c['s'], 0, crop_w, tw)
            ey = expressao(lay.get('trilha_tela', []), c['s'], 1, crop_h, th)
            baixo = (f'[srcbaixo]{filtro_corte(lay["tela"])},'
                     f"crop={crop_w}:{crop_h}:x='{ex}':y='{ey}',scale=1080:820[baixo]")
        # Folga sem imagem: degradê da marca, sem silhuetas da webcam.
        # Se há imagem desde y=0, preservá-la opaca; senão, mesclar em 40 px.
        transicao = (",format=yuva420p,geq=lum='lum(X,Y)':cb='cb(X,Y)':"
                     "cr='cr(X,Y)':a='255*clip(Y/40,0,1)'" if dy > 0 else '')
        cima = (f'color=c={fundo}:s=1080x960:r=30,'
                "geq=lum='lum(X,Y)*(1+0.15*Y/H)':cb='cb(X,Y)':cr='cr(X,Y)'[cambg];"
                f'[srccam]{filtro_corte(camera)},scale={dw}:{dh},eq=brightness=0.04'
                f'{transicao}[personfg];'
                f'[cambg][personfg]overlay={dx}:{dy}[cima]')
        grafo = (f'[0:v]split=2[srccam][srcbaixo];' + cima + ';'
                 + baixo + ';[cima]pad=1080:1100:0:0:color=' + fundo + '[faixa];'
                 '[faixa][baixo]vstack=inputs=2[base]')
    elif modo == 'tela':
        grafo = '[0:v]null[srcinteiro];' + tela(lay['tela'], 1920, 'inteiro', rodape=500) + ';[inteiro]null[base]'
    else:
        largura, altura = lay['largura'], lay['altura']
        # Recorte 9:16 com folga vertical para cabeça, título e legenda.
        folga = par(altura * .15)
        total_h = altura + 2 * folga
        crop_w = par(total_h * 9 / 16)
        fx, fy, fw, fh = face
        if crop_w < fw * 1.5:
            raise ValueError('Rosto grande demais para recorte seguro; ajuste a gravação.')
        pad_w = max(largura, crop_w)
        deslocamento = (pad_w - largura) // 2
        expr = pan(lay, c, crop_w) if crop_w <= largura else '0'
        pad_y = par(altura * .4)
        pad_h = altura + 2 * pad_y
        alvo_y = 880 * total_h / 1920
        expr_y = pan(lay, c, total_h, eixo=1, folga=pad_y, total=pad_h, alvo=alvo_y)
        grafo = (f'[0:v]pad={pad_w}:{pad_h}:{deslocamento}:{pad_y}:color={m["cores"]["fundo"]},'
                 f"crop={crop_w}:{total_h}:x='{expr}':y='{expr_y}',scale=1080:1920[base]")
        mx = max(0, min(largura - crop_w, fx + fw / 2 - crop_w / 2))
        rosto = [(fx+deslocamento-mx)*1080/crop_w, 880 - fh*1920/total_h/2,
                 fw*1080/crop_w, fh*1920/total_h]
    return grafo, [round(v, 2) for v in rosto] if rosto else None


def renderizar(a, c, lay):
    pasta, m = episodio(a), marca(a)
    if lay['modo'] == 'tela+camera':
        from .enquadramento import medir_camera
        lay = sem_moldura(pasta / 'raw/video.mp4', lay, c)
        lay = medir_camera(pasta / 'raw/video.mp4', lay, c, m['titulo_segundos'])
    grafo, rosto = geometria(lay, c, m, raiz(a))
    ass = pasta / 'work' / (c['id'] + '.ass')
    protegido = proteger_cabeca(rosto, 1920 * .04) if rosto else None
    dados = criar(palavras(a), c, lay['modo'], protegido, m, raiz(a), ass)
    dados['rosto_esperado'] = rosto
    if lay['modo'] == 'tela+camera':
        camera, _ = recorte_camera(lay, c, m, raiz(a))
        dados['recortes_camera'] = [{'t': 0.0, 'caixa': camera}]
    destino = pasta / 'clips' / (c['id'] + '.mp4')
    destino.parent.mkdir(parents=True, exist_ok=True)
    # Caminhos de filtros usam escapes próprios, separados dos argumentos do processo.
    def caminho(p):
        return str(p).replace('\\', '\\\\').replace(':', '\\:').replace("'", "'\\''")
    grafo += f";[base]setsar=1,ass=filename='{caminho(ass)}':fontsdir='{caminho(raiz(a) / 'marca/fontes')}'[out]"
    temporario = destino.with_suffix('.tmp.mp4')
    inicio = time.monotonic()
    executar(['ffmpeg', '-v', 'error', '-y', '-threads', '2', '-ss', str(c['s']),
              '-i', pasta / 'raw/video.mp4', '-t', str(c['e'] - c['s']),
              '-filter_complex_threads', '2', '-filter_complex', grafo,
              '-map', '[out]', '-map', '0:a:0', '-r', '30', '-c:v', 'libx264',
              '-preset', 'ultrafast', '-crf', '20', '-threads', '2', '-pix_fmt', 'yuv420p',
              '-c:a', 'aac', '-b:a', '160k', '-map_metadata', '-1', '-fflags', '+bitexact',
              '-flags:v', '+bitexact', '-flags:a', '+bitexact', '-movflags', '+faststart', temporario], timeout=120)
    temporario.replace(destino)
    gerar_miniatura(destino, forcar=True)
    salvar(destino.with_suffix('.legendas.json'), dados)
    print('Render:', c['id'], f'({time.monotonic()-inicio:.1f}s)', destino)


def rodar(a):
    pasta = episodio(a)
    caminho_layout = pasta / 'work/layout.json'
    if not caminho_layout.exists():
        from .layout import analisar
        salvar(caminho_layout, analisar(pasta / 'raw/video.mp4'))
    lay = ler(caminho_layout)
    lista = clips(a)
    ids = set(a.ids)
    if not a.todos and not ids:
        raise ValueError('Informe os ids ou --todos.')
    if ids - {c['id'] for c in lista}:
        raise ValueError('Clip desconhecido: ' + ', '.join(sorted(ids - {c['id'] for c in lista})))
    estado = ler(pasta / 'revisao.json') if (pasta / 'revisao.json').exists() else {}
    for c in lista:
        if a.todos or c['id'] in ids:
            renderizar(a, c, lay)
            estado.pop(c['id'], None)
            for tipo in ('quadros', 'conteudo'):
                (pasta / 'work' / (c['id'] + '.' + tipo + '.json')).unlink(missing_ok=True)
    salvar(pasta / 'revisao.json', estado)
    return 0
