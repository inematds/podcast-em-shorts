"""Cópia local exclusivamente de cortes aprovados pela pessoa revisora."""
import shutil
import re
from .util import episodio, ler, clips, palavras


def rodar(a):
    pasta = episodio(a)
    estado = ler(pasta / 'revisao.json') if (pasta / 'revisao.json').exists() else {}
    aprovados = [c for c in clips(a) if estado.get(c['id'], {}).get('status') == 'aprovado']
    if not aprovados:
        print('NADA APROVADO')
        return 1
    pal = palavras(a)
    destino = pasta / 'aprovados'
    destino.mkdir(parents=True, exist_ok=True)
    for c in aprovados:
        origem = pasta / 'clips' / (c['id'] + '.mp4')
        if not origem.exists():
            raise ValueError('Clip aprovado sem vídeo: ' + c['id'])
        texto = ' '.join(w['w'] for w in pal[c['ini']:c['fim'] + 1])
        sugestao = re.sub(r'(?:https?://|www\.)\S+', '', c['titulo'] + '\n' + texto).strip()
        shutil.copy2(origem, destino / origem.name)
        (destino / (c['id'] + '.txt')).write_text(
            c['titulo'] + '\n\nTexto falado:\n' + texto + '\n\nSugestão de legenda de post:\n'
            + sugestao + '\n', encoding='utf-8')
        print('Exportado:', c['id'], destino)
    return 0
