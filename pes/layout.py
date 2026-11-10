"""Amostragem distribuída, classificação e estimativa geométrica da webcam."""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from .rostos import Detector, mediana
from .tela import analisar_tela


def retangulo_inteiro(x, y, w, h, largura, altura):
    x0, y0 = max(0, int(x)), max(0, int(y))
    x1, y1 = min(largura, int(np.ceil(x + w))), min(altura, int(np.ceil(y + h)))
    return [x0, y0, max(1, x1 - x0), max(1, y1 - y0)]


def estimar_camera(face, largura, altura):
    """Reserva cabeça e ombros; webcams sobrepostas normalmente ancoram num canto.

    É uma estimativa, não uma segmentação: uma captura com moldura incomum
    precisa ser inspecionada antes de renderizar.
    """
    x, y, w, h = face
    cx, cy = x + w / 2, y + h / 2
    cw, ch = max(5.8 * w, 4.8 * h), max(3.5 * w, 2.75 * h)
    esquerda = 0 if cx < largura / 2 else max(0, largura - cw)
    topo = 0 if cy < altura / 2 else max(0, altura - ch)
    return retangulo_inteiro(esquerda, topo, cw, ch, largura, altura)


def tela_sem_camera(camera, largura, altura):
    x, y, w, h = camera
    opcoes = [[0, 0, largura, y], [0, y + h, largura, altura - y - h],
              [0, 0, x, altura], [x + w, 0, largura - x - w, altura]]
    return max(opcoes, key=lambda b: b[2] * b[3])


def analisar(video, forcar=None, quantidade=32):
    if quantidade < 24:
        raise ValueError('Amostragem exige pelo menos 24 quadros.')
    captura = cv2.VideoCapture(str(video))
    if not captura.isOpened():
        raise ValueError('Não foi possível abrir o vídeo.')
    largura = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = captura.get(cv2.CAP_PROP_FPS)
    if total < 24 or fps <= 0:
        captura.release()
        raise ValueError('Vídeo curto demais ou sem taxa de quadros válida.')
    detector = Detector()
    observacoes, amostras = [], 0
    try:
        for indice in np.linspace(0, total - 1, min(quantidade, total), dtype=int):
            captura.set(cv2.CAP_PROP_POS_FRAMES, int(indice))
            ok, quadro = captura.read()
            if not ok:
                raise ValueError('Falha ao decodificar amostra ' + str(indice))
            amostras += 1
            faces = detector.detectar(quadro)
            if faces:
                observacoes.append({'t': float(indice / fps), 'caixa': faces[0]})
    finally:
        captura.release()
    rosto = mediana([o['caixa'] for o in observacoes]) if observacoes else None
    camera, tela, trilha = None, [0, 0, largura, altura], []
    estaveis = []
    if rosto:
        cx, cy = rosto[0] + rosto[2] / 2, rosto[1] + rosto[3] / 2
        estaveis = [o for o in observacoes
                    if abs(o['caixa'][0] + o['caixa'][2] / 2 - cx) < largura * 0.10
                    and abs(o['caixa'][1] + o['caixa'][3] / 2 - cy) < altura * 0.10]
    pequeno = rosto is not None and rosto[2] * rosto[3] < largura * altura * 0.08
    modo = ('tela+camera' if pequeno and len(estaveis) >= amostras * 0.5
            else 'camera' if rosto else 'tela')
    if forcar:
        if forcar not in ('tela+camera', 'camera', 'tela'):
            raise ValueError('Modo de layout inválido.')
        if forcar != 'tela' and not rosto:
            raise ValueError('Nenhum rosto detectado para o layout solicitado.')
        modo = forcar
    if modo == 'tela+camera':
        camera = estimar_camera(rosto, largura, altura)
        tela = tela_sem_camera(camera, largura, altura)
        if tela[2] <= 0 or tela[3] <= 0:
            if forcar == 'tela+camera':
                raise ValueError('Webcam ocupa todo o quadro; não sobra tela. Use --forcar camera.')
            modo, camera, tela = 'camera', None, None
    trilha_tela = []
    if tela and modo in ('tela', 'tela+camera'):
        tela, trilha_tela = analisar_tela(video, tela, quantidade)
    if modo == 'camera':
        tela = None
        anterior = None
        for obs in observacoes:
            x, y, w, h = obs['caixa']
            atual = np.array([x + w / 2, y + h / 2])
            if anterior is not None:
                atual = anterior + np.clip((atual - anterior) * 0.3, -largura * 0.025, largura * 0.025)
            trilha.append({'t': obs['t'], 'centro': atual.tolist()})
            anterior = atual
    return {'modo': modo, 'camera': camera, 'tela': tela, 'rosto_medio': rosto,
            'amostras': amostras, 'com_rosto': len(observacoes), 'trilha': trilha,
            'largura': largura, 'altura': altura, 'trilha_tela': trilha_tela}


def rodar(a):
    import re
    if not re.fullmatch(r'[a-z0-9-]+', a.ep):
        raise ValueError('Identificador de episódio inválido.')
    ep = Path(a.raiz) / 'episodios' / a.ep
    resultado = analisar(ep / 'raw/video.mp4', a.forcar)
    destino = ep / 'work/layout.json'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print('Layout:', resultado['modo'], '— rostos em', resultado['com_rosto'],
              'de', resultado['amostras'], 'amostras')
    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Analisar o enquadramento de um episódio local.')
    p.add_argument('ep')
    p.add_argument('--raiz', default=str(Path(__file__).resolve().parents[1]))
    p.add_argument('--forcar', choices=['tela+camera', 'camera', 'tela'])
    p.add_argument('--json', action='store_true')
    raise SystemExit(rodar(p.parse_args()))
