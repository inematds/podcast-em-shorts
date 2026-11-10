"""Miniatura local do short, compartilhada pelo render e pela revisão."""
from pathlib import Path
from tempfile import TemporaryDirectory
from .util import executar


def gerar(video, forcar=False):
    video = Path(video)
    jpg = video.with_suffix('.jpg')
    if not video.is_file() or (jpg.is_file() and not forcar):
        return jpg
    with TemporaryDirectory(dir=video.parent) as tmp:
        quadro = Path(tmp) / 'quadro.jpg'
        # Cortes com menos de um segundo ainda precisam de um poster.
        for segundo in ('1', '0'):
            executar(['ffmpeg', '-v', 'error', '-y', '-threads', '2', '-ss', segundo,
                      '-i', video, '-frames:v', '1', '-vf', 'scale=360:-2',
                      '-threads', '2', '-q:v', '2', quadro], timeout=20)
            if quadro.is_file() and quadro.stat().st_size:
                quadro.replace(jpg)
                return jpg
    raise RuntimeError('Não foi possível gerar miniatura: ' + str(video))
