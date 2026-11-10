"""Mede a pessoa no trecho, mantendo o recorte e o zoom fixos no render."""
import cv2
import numpy as np
from .rostos import Detector, mediana


def medir_camera(video, lay, c, segundos_titulo):
    x, y, w, h = lay['camera']
    captura = cv2.VideoCapture(str(video))
    detector = Detector()
    faces, topos, bases = [], [], []
    try:
        for t in np.arange(0, c['e']-c['s'], .5):
            captura.set(cv2.CAP_PROP_POS_MSEC, (c['s']+t)*1000)
            ok, q = captura.read()
            if not ok:
                raise ValueError('Falha ao medir enquadramento da webcam.')
            candidatas = [f for f in detector.detectar(q)
                          if x <= f[0] and y <= f[1]
                          and f[0]+f[2] <= x+w and f[1]+f[3] <= y+h]
            if candidatas:
                face = candidatas[0]
                faces.append(face)
                bases.append(face[1]+face[3])
                if t < segundos_titulo:
                    topos.append(face[1]-.25*face[3])
    finally:
        captura.release()
    if not faces or not topos:
        raise ValueError('Sem rosto suficiente para enquadrar o título com segurança.')
    return dict(lay, rosto_medio=mediana(faces),
                cabelo_min=min(topos), queixo_max=max(bases))
