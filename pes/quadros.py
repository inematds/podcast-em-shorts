"""Inspeção audiovisual por amostragem e detecção real de rostos YuNet."""
import json
import math
import re
import subprocess
from pathlib import Path
import cv2
import numpy as np
from .rostos import Detector, proteger_cabeca
from .util import ffprobe, ler, marca, cruzam, salvar, raiz


def verificar(a):
    if not math.isfinite(a.fps) or not 0 < a.fps <= 30:
        raise ValueError('--fps deve estar entre zero (exclusivo) e 30.')
    info, m = ffprobe(a.mp4), marca(a)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    largura, altura = v['width'], v['height']
    itens = {}
    def item(nome, ok, detalhe):
        itens[nome] = {'ok': bool(ok), 'detalhe': detalhe}
    item('resolucao', (largura, altura) == (1080, 1920), f'{largura}x{altura}; esperado 1080x1920')
    audio = any(s['codec_type'] == 'audio' for s in info['streams'])
    media = float('-inf')
    if audio:
        p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(a.mp4),
                            '-vn', '-af', 'volumedetect', '-f', 'null', '-'],
                           capture_output=True, text=True, timeout=120)
        if p.returncode:
            raise RuntimeError('Não foi possível medir áudio: ' + p.stderr[-1000:])
        achado = re.search(r'mean_volume:\s*(-?\d+(?:\.\d+)?|-?inf) dB', p.stderr)
        if achado:
            media = float(achado.group(1))
    item('audio', audio and media > -50, f'Volume médio {media:.1f} dB; mínimo exclusivo -50 dB')
    dados = ler(a.legendas) if a.legendas else {'blocos': [], 'titulo': None}
    caixas = dados.get('blocos', []) + ([dados['titulo']] if dados.get('titulo') else [])
    seg = m['area_segura']
    fora = [b for b in caixas if (b['caixa'][0] < largura * seg['lados']
            or b['caixa'][1] < altura * seg['topo']
            or b['caixa'][0] + b['caixa'][2] > largura * (1-seg['lados'])
            or b['caixa'][1] + b['caixa'][3] > altura * (1-seg['base']))]
    item('area_segura', not fora, f'{len(fora)} caixas fora da área segura')
    detector = Detector()
    captura = cv2.VideoCapture(str(a.mp4))
    if not captura.isOpened():
        raise ValueError('Vídeo ilegível.')
    fps = captura.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise ValueError('Vídeo sem fps válido.')
    passo = max(1, round(fps / a.fps))
    delta = passo / fps
    preto_inicio = gelo_inicio = None
    preto_max = gelo_max = 0
    anterior, colisoes, cortes, amostras, rostos = None, [], [], 0, 0
    indice = 0
    try:
        while True:
            ok = captura.grab()
            if not ok:
                break
            if indice % passo:
                indice += 1
                continue
            ok, q = captura.retrieve()
            if not ok:
                raise ValueError('Falha ao decodificar quadro ' + str(indice))
            t = indice / fps
            indice += 1
            amostras += 1
            mini = cv2.resize(cv2.cvtColor(q, cv2.COLOR_BGR2GRAY), (180, 320))
            escuro = np.mean(mini < 20) > .98
            if escuro:
                if preto_inicio is None:
                    preto_inicio = t
                preto_max = max(preto_max, t - preto_inicio + delta)
            else:
                preto_inicio = None
            parado = anterior is not None and np.mean(cv2.absdiff(mini, anterior)) < .12
            if parado:
                if gelo_inicio is None:
                    gelo_inicio = t - delta
                gelo_max = max(gelo_max, t - gelo_inicio)
            else:
                gelo_inicio = None
            anterior = mini
            faces = detector.detectar(q)
            rostos += len(faces)
            ativos = [b['caixa'] for b in caixas if b['s'] <= t < b['e']]
            for face in faces:
                x, y, w, h = face
                protegida = proteger_cabeca(face, altura * .04)
                if any(cruzam(protegida, b) for b in ativos):
                    colisoes.append(round(t, 3))
                if x <= 2 or y - h * .25 <= 2 or x + w >= largura - 2 or y + h >= altura - 2:
                    cortes.append(round(t, 3))
    finally:
        captura.release()
    if not amostras:
        raise ValueError('Nenhum quadro decodificado.')
    item('preto', preto_max <= .5, f'Maior trecho quase preto: {preto_max:.2f}s')
    item('congelado', gelo_max <= 3, f'Maior trecho sem mudança: {gelo_max:.2f}s')
    item('rosto_legenda', not colisoes, f'{len(colisoes)} colisões; {rostos} rostos em {amostras} amostras; tempos {colisoes[:8]}')
    item('cabeca_cortada', not cortes, f'{len(cortes)} rostos junto à borda; tempos {cortes[:8]}')
    return {'ok': all(i['ok'] for i in itens.values()), 'itens': itens}


def rodar(a):
    resultado = verificar(a)
    destino = getattr(a, 'salvar', None)
    if destino is None:
        video = Path(a.mp4).resolve()
        episodios = raiz(a) / 'episodios'
        if video.is_relative_to(episodios):
            relativo = video.relative_to(episodios)
            if len(relativo.parts) >= 2 and (episodios / relativo.parts[0] / 'ep.json').is_file():
                destino = video.with_suffix('.quadros.json')
    if destino is not None:
        salvar(destino, resultado)
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False))
    else:
        for nome, r in resultado['itens'].items():
            print(nome + ':', 'ok' if r['ok'] else 'falhou', '—', r['detalhe'])
        print('QUADROS OK' if resultado['ok'] else 'QUADROS FALHOU: ' +
              ', '.join(k for k, v in resultado['itens'].items() if not v['ok']))
    return 0 if resultado['ok'] else 1
