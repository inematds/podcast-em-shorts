"""Importa palavras temporizadas ou transcreve com motor local opcional."""
import math
from .util import episodio, ler, salvar


def normalizar(segmentos):
    if not isinstance(segmentos, list):
        raise ValueError('Transcrição deve conter uma lista de segmentos.')
    brutas = []
    for segmento in segmentos:
        if not isinstance(segmento, dict) or not isinstance(segmento.get('words'), list):
            raise ValueError('Cada segmento deve conter words com tempos por palavra.')
        brutas.extend(segmento['words'])
    validas, invalidas = [], 0
    for w in brutas:
        try:
            texto = w['word'].strip()
            s, e = float(w['start']), float(w['end'])
            if not texto or not math.isfinite(s) or not math.isfinite(e) or s < 0:
                raise ValueError()
            if e < s - .3 or (validas and validas[-1]['s'] - s >= .3 - 1e-9):
                raise ValueError()
            validas.append(dict(w=texto, s=s, e=e))
        except (KeyError, TypeError, ValueError, AttributeError):
            invalidas += 1
    if not validas or invalidas > len(brutas) / 2:
        raise ValueError('Transcrição sem palavras ou com maioria inválida.')
    corrigidas, out, piso = 0, [], 0.
    for i, w in enumerate(validas):
        s, e = w['s'], w['e']
        s = max(s, piso, out[-1]['s'] if out else 0.)
        piso = 0.
        if e <= s:
            proximo = validas[i + 1]['s'] if i + 1 < len(validas) else math.inf
            e = min(s + .02, proximo) if proximo > s else s + .02
            # Tempos coincidentes: abre espaço e desloca a próxima palavra.
            piso = e
        corrigidas += (s != w['s'] or e != w['e'])
        out.append(dict(i=len(out), w=w['w'], s=s, e=e))
    return out, corrigidas, invalidas


def rodar(a):
    pasta = episodio(a)
    if a.de_json:
        segmentos = ler(a.de_json)
        if isinstance(segmentos, dict):
            segmentos = segmentos.get('segments')
    else:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print('Falta faster-whisper: pip install faster-whisper; ou use --de-json arquivo.json.')
            return 2
        motor = WhisperModel(a.modelo, device='cpu', compute_type='int8')
        segs, _ = motor.transcribe(str(pasta / 'raw/video.mp4'), language=a.idioma,
                                  word_timestamps=True)
        segmentos = [{'words': [{'word': w.word, 'start': w.start, 'end': w.end}
                                for w in (s.words or [])]} for s in segs]
    out, corrigidas, invalidas = normalizar(segmentos)
    salvar(pasta / 'work/palavras.json', out)
    print('Transcrição:', len(out), 'palavras')
    print(corrigidas, 'palavras corrigidas')
    if invalidas:
        print(invalidas, 'palavras inválidas descartadas')
    return 0
