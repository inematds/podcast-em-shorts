# Podcast em shorts

Kit local e aberto do INEMA.CLUB: episódio longo → cortes verticais com
legendas por palavra → checagem → revisão humana → cópia dos aprovados.

Python 3.10+, ffmpeg/ffprobe e `pip install -r requirements.txt`.
O faster-whisper é opcional; uma transcrição JSON com palavras basta.

```bash
python3 pes.py doutor
python3 pes.py novo minha-live --video /caminho/video.mp4
python3 pes.py tudo minha-live --de-json /caminho/segmentos.json
python3 pes.py revisao minha-live
# Depois de aprovar os cortes na página:
python3 pes.py exportar minha-live
```

Para escolher manualmente, use `candidatos`, `escolher`, `layout` e `render`.
Cada comando aceita `--raiz /pasta` e possui ajuda com `--help`.
Cores, fonte, limites e quantidade ficam em `marca/marca.json`.
O YuNet usa cache local verificado; `PES_YUNET` indica outro caminho para o
mesmo modelo. Na ausência do cache, o download público ocorre uma vez.

Veja [o exemplo](exemplos/live30-s1.mp4), [o contrato](docs/SPEC.md),
[as medições e verificações](docs/IMPLEMENTACAO.md) e
[as limitações observadas](docs/DUVIDAS.md). Nenhum comando publica conteúdo.
