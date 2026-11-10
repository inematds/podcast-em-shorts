"""Importação preservando o original, inclusive ao refazer o cadastro."""
import shutil
from fractions import Fraction
from pathlib import Path
from .util import episodio, ffprobe, salvar


def rodar(a):
    pasta = episodio(a, exigir=False)
    origem = Path(a.video).expanduser().resolve()
    if pasta.exists() and not a.forcar:
        raise ValueError('Episódio já existe; use --forcar para atualizar o cadastro.')
    destino = pasta / 'raw/video.mp4'
    if destino.exists() and destino.resolve() != origem:
        # Forçar nunca substitui a gravação: apenas recadastra a mesma mídia.
        import hashlib
        def resumo(p):
            h = hashlib.sha256()
            with p.open('rb') as f:
                for bloco in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(bloco)
            return h.digest()
        if resumo(destino) != resumo(origem):
            raise ValueError('O original é diferente. Use outro nome de episódio para preservá-lo.')
    info = ffprobe(origem)
    video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    if video is None:
        raise ValueError('Arquivo sem vídeo.')
    for nome in ('raw', 'work', 'clips', 'aprovados'):
        (pasta / nome).mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copy2(origem, destino)
    salvar(pasta / 'ep.json', {'ep': a.ep, 'video': 'raw/video.mp4',
           'duracao': float(info['format']['duration']), 'largura': video['width'],
           'altura': video['height'], 'fps': float(Fraction(video['avg_frame_rate']))})
    if not (pasta / 'revisao.json').exists():
        salvar(pasta / 'revisao.json', {})
    print('Episódio importado:', a.ep)
    return 0
