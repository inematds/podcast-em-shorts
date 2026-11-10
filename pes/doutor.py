"""Diagnóstico de dependências obrigatórias e opcionais."""
import importlib
import shutil
from .util import marca, raiz


def rodar(a):
    tudo = True
    dica = 'Ubuntu: sudo apt install ffmpeg; Mac: brew install ffmpeg'
    for nome in ('ffmpeg', 'ffprobe'):
        ok = bool(shutil.which(nome))
        print(('ok' if ok else 'falta'), nome, '' if ok else dica)
        tudo &= ok
    for nome, pacote, atributo, opcional in (
            ('OpenCV YuNet', 'cv2', 'FaceDetectorYN', False),
            ('numpy', 'numpy', None, False), ('Pillow', 'PIL', None, False),
            ('faster-whisper (opcional)', 'faster_whisper', None, True)):
        try:
            m = importlib.import_module(pacote)
            ok = atributo is None or hasattr(m, atributo)
        except ImportError:
            ok = False
        print(('ok' if ok else 'falta'), nome,
              '' if ok else '— pip install -r requirements.txt; opcional: pip install faster-whisper')
        tudo &= ok or opcional
    try:
        from PIL import ImageFont
        fonte = raiz(a) / marca(a)['fonte']
        ImageFont.truetype(str(fonte), 32)
        print('ok fonte', fonte.name)
    except (OSError, ValueError) as exc:
        print('falta fonte — restaure marca/fontes/:', exc)
        tudo = False
    try:
        from .rostos import Detector
        Detector()
        print('ok modelo YuNet (integridade e carregamento)')
    except (OSError, ValueError, RuntimeError) as exc:
        print('falta YuNet — configure PES_YUNET com o modelo verificado:', exc)
        tudo = False
    return 0 if tudo else 1
