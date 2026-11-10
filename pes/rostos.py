"""YuNet em CPU: download público verificado e detecção em pixels da origem."""

import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path

import cv2
import numpy as np


MODELO = 'face_detection_yunet_2023mar.onnx'
SHA256 = '8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4'
TAMANHO = 232589
URL = ('https://media.githubusercontent.com/media/opencv/opencv_zoo/'
       'main/models/face_detection_yunet/' + MODELO)


def conferir(caminho):
    """Recusa inclusive caminhos sobrescritos que não sejam o modelo esperado."""
    caminho = Path(caminho)
    if caminho.stat().st_size != TAMANHO:
        raise ValueError('Tamanho incorreto do modelo YuNet: ' + str(caminho))
    resumo = hashlib.sha256(caminho.read_bytes()).hexdigest()
    if resumo != SHA256:
        raise ValueError('SHA-256 incorreto do modelo YuNet: ' + str(caminho))
    return caminho


def caminho_modelo(baixar=True):
    """Só baixa na ausência do cache; arquivo corrompido exige intervenção."""
    alternativo = os.environ.get('PES_YUNET')
    if alternativo:
        return conferir(Path(alternativo).expanduser())
    destino = Path.home() / '.cache' / 'podcast-em-shorts' / MODELO
    if destino.exists():
        return conferir(destino)
    if not baixar:
        raise FileNotFoundError('YuNet ausente. Execute layout para baixar o modelo público.')
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with urllib.request.urlopen(URL, timeout=30) as resposta:
            # Um teto também impede salvar uma resposta inesperadamente grande.
            dados = resposta.read(TAMANHO + 1)
        with tempfile.NamedTemporaryFile(dir=destino.parent, suffix='.onnx', delete=False) as f:
            temporario = Path(f.name)
            f.write(dados)
        conferir(temporario)
        temporario.replace(destino)
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()
    return destino


def geometria_valida(face):
    """Confere os cinco pontos YuNet na escala original da detecção.

    Tolera inclinação moderada e assimetria; não depende da posição no vídeo.
    A caixa sozinha não distingue uma mão de uma face.
    """
    if len(face) != 15 or not np.isfinite(face).all():
        return False
    x, y, w, h = face[:4]
    if w <= 0 or h <= 0:
        return False
    pontos = np.asarray(face[4:14]).reshape(5, 2)
    if (np.any(pontos < [x - .1 * w, y - .1 * h])
            or np.any(pontos > [x + 1.1 * w, y + 1.1 * h])):
        return False
    esquerdo, direito = sorted(pontos[:2], key=lambda p: p[0])
    nariz = pontos[2]
    boca = pontos[3:].mean(axis=0)
    distancia = direito[0] - esquerdo[0]
    olhos_y = (esquerdo[1] + direito[1]) / 2
    return bool(
        .2 * w <= distancia <= .8 * w
        and abs(direito[1] - esquerdo[1]) <= .5 * distancia
        and max(esquerdo[1], direito[1]) + .02 * h < nariz[1]
        and nariz[1] + .02 * h < min(pontos[3:, 1])
        and esquerdo[0] - .15 * distancia <= nariz[0] <= direito[0] + .15 * distancia
        and esquerdo[0] - .2 * distancia <= boca[0] <= direito[0] + .2 * distancia
        and .12 * h <= boca[1] - olhos_y <= .65 * h)


class Detector:
    """Reduz a imagem sem perder a webcam e devolve todas as faces confiáveis."""

    def __init__(self, tamanho_maximo=1920):
        cv2.setNumThreads(2)
        self.tamanho_maximo = tamanho_maximo
        self.rede = cv2.FaceDetectorYN.create(
            str(caminho_modelo()), '', (320, 320), 0.65, 0.3, 5000,
            cv2.dnn.DNN_BACKEND_OPENCV, cv2.dnn.DNN_TARGET_CPU)

    def detectar(self, quadro):
        altura, largura = quadro.shape[:2]
        escala = min(1.0, self.tamanho_maximo / max(altura, largura))
        if escala < 1:
            quadro = cv2.resize(quadro, (round(largura * escala), round(altura * escala)))
        self.rede.setInputSize((quadro.shape[1], quadro.shape[0]))
        _, faces = self.rede.detect(quadro)
        if faces is None:
            return []
        # A face principal é a de maior confiança com anatomia plausível.
        # Secundárias exigem confiança maior, mas não precisam esperar uma trilha:
        # um segundo rosto real deve ser protegido desde a primeira aparição.
        faces = sorted((f for f in faces if geometria_valida(f) and f[14] >= .65),
                       key=lambda f: -float(f[14]))
        caixas = []
        for i, face in enumerate(faces):
            if i and face[14] < .8:
                continue
            x, y, w, h = (face[:4] / escala).tolist()
            x0, y0 = max(0.0, x), max(0.0, y)
            x1, y1 = min(float(largura), x + w), min(float(altura), y + h)
            if x1 > x0 and y1 > y0:
                caixas.append([x0, y0, x1 - x0, y1 - y0])
        return sorted(caixas, key=lambda b: (-b[2] * b[3], b[0], b[1]))


def proteger_cabeca(caixa, margem_altura):
    """Folga superior para cabelo, mais a margem exigida na checagem."""
    x, y, w, h = caixa
    return [x - margem_altura, y - 0.25 * h - margem_altura,
            w + 2 * margem_altura, 1.25 * h + 2 * margem_altura]


def mediana(caixas):
    return np.median(np.asarray(caixas, dtype=float), axis=0).tolist()
