"""Render determinístico CPU via ffmpeg, com áudio original e ASS temporizado."""
import time
from pathlib import Path
from .util import episodio, ler, marca, palavras, raiz, salvar, executar, clips
from .legenda import criar, titulo_linhas, fonte
from .rostos import proteger_cabeca
from .tela import expressao


def par(n):
    return max(2, int(n) // 2 * 2)


def filtro_corte(caixa):
    x, y, w, h = caixa
    return f'crop={int(w)}:{int(h)}:{int(x)}:{int(y)}'


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


def geometria(lay, c, m, pasta_marca=None):
    modo, face = lay['modo'], lay['rosto_medio']
    rosto = None
    if modo == 'tela+camera':
        x, y, w, h = lay['camera']
        fx, fy, fw, fh = face
        # Inset elimina a moldura. O recorte vertical mantém cabelo e ombros,
        # ampliando sem introduzir pad ou pixels externos à webcam.
        x, y, w, h = x+w*.03, y+h*.03, w*.94, h*.94
        linhas, tam = titulo_linhas(c['titulo'], m, (pasta_marca or Path(__file__).resolve().parents[1]))
        reserva = 0
        if len(linhas) == 2:
            f = fonte(m, (pasta_marca or Path(__file__).resolve().parents[1]), tam)
            reserva = par(32 + 2*(max(f.getbbox(t)[3]-f.getbbox(t)[1] for t in linhas)+24))
        util = 960-reserva
        ch = par(min(h, fh*2.26 if not reserva else util*fh/310))
        cw = par(ch*1080/util)
        cy = max(y, min(y+h-ch, fy-.9*fh))
        cx = max(x, min(x+w-cw, fx+fw/2-cw/2))
        camera = [par(cx), par(cy), cw, ch]
        escala = util/ch
        rosto = [(fx-camera[0])*1080/cw, reserva + (fy-camera[1])*escala,
                 fw*1080/cw, fh*escala]
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
        cima = f'[srccam]{filtro_corte(camera)},scale=1080:{util},eq=brightness=0.04[cima]'
        if reserva:
            # Menos zoom na pessoa para abrir espaço acima da testa. O topo
            # continua preenchido pelo fundo da própria webcam, sem moldura.
            topo = [camera[0], camera[1], cw, par(min(ch*.22, fy-camera[1]-fh*.3))]
            cima = (f'[srccam]split=2[head][person];[head]{filtro_corte(topo)},'
                    f'scale=1080:{reserva},eq=brightness=0.04[headroom];'
                    f'[person]{filtro_corte(camera)},scale=1080:{util},eq=brightness=0.04[personfg];'
                    '[headroom][personfg]vstack=inputs=2[cima]')
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
    grafo, rosto = geometria(lay, c, m, raiz(a))
    ass = pasta / 'work' / (c['id'] + '.ass')
    protegido = proteger_cabeca(rosto, 1920 * .04) if rosto else None
    dados = criar(palavras(a), c, lay['modo'], protegido, m, raiz(a), ass)
    dados['rosto_esperado'] = rosto
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
    salvar(destino.with_suffix('.legendas.json'), dados)
    print('Render:', c['id'], f'({time.monotonic()-inicio:.1f}s)', destino)


def rodar(a):
    pasta = episodio(a)
    lay = ler(pasta / 'work/layout.json')
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
