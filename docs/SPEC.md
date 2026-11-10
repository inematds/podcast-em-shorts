# SPEC — podcast-em-shorts (contrato para quem implementa)

Kit aberto do INEMA.CLUB: **um episódio longo (podcast, live, entrevista, aula gravada) entra; shorts 9:16 prontos para revisar saem.**
Roda em Linux (e Mac) com Python 3.10+, ffmpeg e OpenCV. Nada é publicado sozinho: o kit só gera, checa e organiza; quem aprova é a pessoa.

## Regras do projeto (não negociáveis)

1. **Implementação original.** Não copiar código, textos, tabelas, números de pesquisa nem nomes de regra de nenhum kit de terceiros. Sem citar fonte, autor ou comunidade de origem em nenhum arquivo.
2. **Nada publica.** Nenhum código chama API de rede social, agendador de posts, banco ou hospedagem na nuvem. `exportar` só copia arquivos aprovados para uma pasta.
3. **Sem chave de API** em lugar nenhum. Tudo local: faster-whisper (opcional) ou importação de um JSON de transcrição pronto.
4. **Valores de marca só em `marca/marca.json`** (cores, fonte, nome, @, duração mín/máx, quantidade de shorts). Nenhuma cor/fonte fixa no código.
5. **Falha é falha.** Checagem que falha sai com código 1 e imprime o motivo. Nunca afrouxar um limite para um exemplo passar.
6. **Não apagar o original** (`episodios/<ep>/raw/`).
7. Textos para o usuário em português simples (CLI, README, mensagens).
8. Fonte: Montserrat (OFL) em `marca/fontes/` com o arquivo de licença OFL.

## Estrutura

```
pes.py                      # CLI único:  python3 pes.py <subcomando> ...
pes/                        # pacote: um módulo por subcomando + util
marca/marca.json            # marca padrão INEMA (ver abaixo)
marca/fontes/               # Montserrat-Black.ttf + OFL.txt
regras/REGRAS.md            # regras do kit (R1..R40 no máximo), cada uma com "Por quê" e "Quem checa"
regras/MINHAS-REGRAS.md     # regras da pessoa, começam em R200 (criado vazio com cabeçalho)
skill/podcast-em-shorts/SKILL.md   # skill para Claude Code / Codex: ordem dos passos e quando parar
episodios/                  # (ignorado no git) um diretório por episódio
exemplos/                   # shorts de exemplo gerados pelo próprio kit + o relatório das checagens
tests/                      # testes congelados (não editar)
requirements.txt            # opencv-python-headless, numpy, pillow; faster-whisper como opcional comentado
```

Episódio: `episodios/<ep>/raw/video.mp4`, `episodios/<ep>/ep.json`, `work/`, `clips/`, `revisao.json`, `aprovados/`.
`<ep>` só `[a-z0-9-]+`. Todo subcomando aceita `--raiz <dir>` (padrão: pasta do pes.py) para achar `episodios/`, `marca/` e `regras/`.

## marca/marca.json (padrão INEMA)

```json
{
  "nome": "INEMA.CLUB", "arroba": "@inema.club",
  "cores": {"fundo": "#0c0c10", "texto": "#FFFFFF", "destaque": "#FACC15", "contorno": "#000000"},
  "fonte": "marca/fontes/Montserrat-Black.ttf",
  "legenda": {"max_palavras": 3, "max_caracteres": 22, "tamanho": 72, "contorno": 8},
  "duracao": {"min": 20, "max": 59},
  "shorts_por_episodio": 3,
  "area_segura": {"topo": 0.10, "base": 0.20, "lados": 0.06},
  "titulo_segundos": 3.0
}
```

## Subcomandos (interfaces que os testes usam — nomes e saídas exatos)

### `novo <ep> --video <arquivo>`
Cria a estrutura e copia (ou faz hardlink) o vídeo em `raw/video.mp4`. Grava `ep.json` `{"ep","video","duracao","largura","altura","fps"}` (ffprobe). Recusa se `<ep>` já existe (saída 1) a não ser com `--forcar`.

### `transcrever <ep> [--modelo large-v3] [--idioma pt] [--de-json <arquivo>]`
Gera `work/palavras.json`: lista `[{"i":0,"w":"Olá,","s":0.12,"e":0.40}, ...]` (i sequencial, s<e, ordem crescente).
`--de-json` importa um JSON de segmentos com `words` (`[{"start","end","text","words":[{"word","start","end"}]}]`, formato do faster-whisper/inemavox) sem precisar de GPU. Sem `--de-json`, usa faster-whisper se instalado; se não, sai 2 com a dica de instalar ou importar.

### `candidatos <ep> [--top 12] [--json]`
Lê `palavras.json`, quebra em frases (pontuação final `. ? !` e pausas > 0,8 s) e monta trechos **contínuos** de frases inteiras com duração entre `duracao.min` e `duracao.max`.
Pontua cada trecho por sinais (heurísticas próprias, em PT; documentar em `regras/REGRAS.md`, sem números de pesquisa de terceiros):
- positivos: `numero` (dígitos ou número por extenso), `voce` (você/seu/sua/teu), `virada` (mas, só que, na verdade, o problema é, ninguém fala, o segredo), `pergunta` (frase com ?), `veredito` (ou seja, resumindo, a lição, no fim das contas, então o que), `nome` (palavra com inicial maiúscula fora do começo de frase), `exemplo` (por exemplo, imagina, olha isso, vou mostrar);
- negativos (alertas): `referencia_atras` (como eu falei, como eu disse, lá atrás, ontem, na live passada), `chamada` (se inscreve, inscreva, link na descrição, comenta aí, deixa o like), `muleta_inicio` (primeira palavra é então/né/tipo/aí/é/bom/e), `sem_fechamento` (última palavra sem pontuação final).
Grava `work/candidatos.json` = lista ordenada por `nota` desc com objetos
`{"id":"c01","ini":<i palavra>,"fim":<i palavra>,"s":<seg>,"e":<seg>,"duracao":<seg>,"nota":<float>,"sinais":[...],"alertas":[...],"texto":"..."}`.
Trechos não se sobrepõem mais que 50% entre si no top. Com `--json` imprime o mesmo JSON no stdout; sem, imprime tabela legível.

### `escolher <ep> <id>[,<id>...] [--titulo "<id>=Título"]...`
Escreve `clips.json` `{"clips":[{"id":"s1","de":"c03","ini":..,"fim":..,"s":..,"e":..,"titulo":"..."}]}` a partir de candidatos (ids s1, s2… na ordem dada). Título padrão = primeiras 5 palavras do trecho, sem pontuação. Ajuste fino: `--ajustar s1=ini:fim` (índices de palavra).

### `gancho --falado "<frase>" --titulo "<título>" [--json]`
Nota de 0 a 10 para a primeira frase falada e para o título, com motivos. Critérios próprios e simples (ex.: falado: tem sujeito concreto, tem número ou "você", não começa com muleta, ≤ 18 palavras; título: ≤ 7 palavras, ≤ 40 caracteres, sem reticências, sem caixa toda baixa, tem palavra forte). Sai 0 se falado ≥ 6 e título ≥ 6; senão 1. `--json` → `{"falado":{"nota","motivos"},"titulo":{"nota","motivos"},"passa":bool}`.

### `layout <ep> [--forcar tela+camera|camera|tela] [--json]`
Amostra ≥ 24 quadros espalhados, detecta rostos com OpenCV **YuNet** (`cv2.FaceDetectorYN`; o modelo `.onnx` é baixado uma vez para `~/.cache/podcast-em-shorts/` com checagem de tamanho/sha256, ou lido de `PES_YUNET`) e decide:
- `tela+camera`: rosto estável (mesma região em ≥ 50% das amostras) e pequeno (caixa < 8% da área) → é webcam sobre tela compartilhada. Grava `camera` (caixa da webcam inteira, estimada em volta do rosto e presa às bordas do quadro) e `tela` (o resto útil do quadro, sem a webcam).
- `camera`: rosto grande → modo rosto; grava a trilha suavizada do centro do rosto por tempo.
- `tela`: sem rosto.
Grava `work/layout.json` `{"modo":..., "camera":[x,y,w,h]|null, "tela":[x,y,w,h]|null, "rosto_medio":[x,y,w,h]|null, "amostras":N, "com_rosto":M}`.

### `render <ep> [<id>...|--todos]`
Para cada clip: `clips/<id>.mp4` 1080x1920, H.264 yuv420p, AAC, 30 fps, duração = `e - s` (± 0,15 s), áudio do trecho original sem dessincronizar.
Layouts:
- `tela+camera`: metade de cima (1080x960) = webcam ampliada com recorte que mantém a cabeça inteira; metade de baixo (1080x960) = tela (escala para caber na largura, fundo = a própria tela desfocada). Faixa de legenda centrada na junção, **fora da caixa do rosto**.
- `camera`: recorte 9:16 seguindo o rosto suavizado (sem tremer: deslocamento máx. por quadro limitado), cabeça inteira dentro do quadro, legenda no terço de baixo acima da área segura.
- `tela`: tela escalada no centro com fundo desfocado; legenda abaixo.
Título do clip no topo nos primeiros `titulo_segundos`, dentro da área segura, nunca sobre o rosto.
Legenda karaokê palavra a palavra: blocos de até `max_palavras` / `max_caracteres`, **uma linha**, palavra falada em `destaque`, contorno; tempos tirados de `palavras.json` (sem atraso > 0,1 s).
Grava ao lado `clips/<id>.legendas.json` = `{"blocos":[{"s","e","texto","caixa":[x,y,w,h]}], "titulo":{"s","e","caixa":[x,y,w,h]}, "rosto_esperado":[x,y,w,h]|null, "layout":"..."}` (caixas em pixels do vídeo final). Render via ffmpeg (filtros + legenda em ASS ou imagens PNG desenhadas com Pillow) — escolha livre, desde que determinístico.

### `checar-quadros <mp4> [--legendas <json>] [--fps 2] [--json]`
Lê o vídeo final a `--fps` quadros por segundo e verifica:
- `resolucao`: 1080x1920; `audio`: tem trilha de áudio e não é silêncio total (volume médio > -50 dB);
- `preto`: nenhum trecho > 0,5 s com quadro quase todo preto; `congelado`: nenhum trecho > 3 s sem mudança de imagem;
- `rosto_legenda`: em nenhum quadro amostrado a caixa de legenda/título ativa (do `--legendas`) cruza a caixa de um rosto detectado (com margem de 4% da altura, e cabelo: estender a caixa do rosto 25% para cima);
- `cabeca_cortada`: rosto detectado encostando na borda do quadro;
- `area_segura`: caixas de legenda/título dentro da área segura da marca.
Imprime uma linha por item e no fim exatamente `QUADROS OK` (saída 0) ou `QUADROS FALHOU: <itens>` (saída 1). `--json` → `{"ok":bool,"itens":{nome:{"ok":bool,"detalhe":str}}}`.

### `checar-conteudo <ep> <id> [--json]`
Verifica o texto do clip: começa no início de uma frase (palavra anterior termina em `. ? !` ou pausa > 0,8 s) e não começa com muleta; termina com pontuação final; sem `chamada` dentro; duração dentro de `duracao`; um trecho só (contínuo). Imprime `CONTEUDO OK` (0) ou `CONTEUDO FALHOU: <itens>` (1).

### `revisao <ep> [--porta 0] [--host 127.0.0.1] [--so-html]`
Página local de revisão: cada short com player, título, nota dos candidatos, resultado das checagens, campo de nota e botões **Aprovar** / **Refazer**. Servidor `http.server` só da biblioteca padrão:
- `GET /` página; `GET /video/<id>.mp4` vídeo (suporta Range); `GET /api/estado` JSON;
- `POST /api/acao` corpo JSON `{"id":"s1","acao":"aprovar"|"refazer","nota":"texto"}` → grava em `episodios/<ep>/revisao.json` `{"<id>":{"status":"aprovado"|"refazer","notas":[{"texto","quando"}]}}` e responde o estado.
Com `--porta 0` escolhe porta livre e imprime `REVISAO http://<host>:<porta>/` na primeira linha (flush). `--so-html` só grava `episodios/<ep>/revisao.html` estático e sai.
Visual: fundo `fundo`, destaque `destaque` da marca, responsivo no celular.

### `regra "<texto>" [--quem quadros|conteudo|olho] [--por-que "<texto>"]`
Acrescenta em `regras/MINHAS-REGRAS.md` a próxima regra livre a partir de **R200** (`## R200 — <texto>` + `Por quê:` + `Quem checa:`), imprime o número (`R200`). Nota da revisão → regra: `regra --da-nota <ep> <id>` usa a última nota do clip como texto.

### `exportar <ep>`
Copia só os clips com `status: aprovado` para `episodios/<ep>/aprovados/` + `<id>.txt` com título, texto falado e sugestão de legenda de post (sem link). Se nenhum aprovado: imprime `NADA APROVADO` e sai 1. Nunca envia nada pela rede.

### `doutor`
Confere ffmpeg/ffprobe, OpenCV com `FaceDetectorYN`, numpy, Pillow, faster-whisper (opcional), fonte, modelo YuNet. Uma linha por item `ok`/`falta` + dica de instalação (Ubuntu e Mac). Sai 0 se o obrigatório está ok.

### `tudo <ep> [--de-json <arquivo>]`
Atalho: transcrever → candidatos → escolher os `shorts_por_episodio` melhores sem alertas → layout → render → checar-quadros → checar-conteudo, e imprime o resumo e o comando da revisão. Para no primeiro erro de infraestrutura; checagem reprovada fica marcada no resumo (não esconde).

## Testes

`python3 -m unittest discover -s tests -v` (congelados; não alterar). Usam `tests/fixtures/live30.mp4` (30 s de uma live com tela + webcam) e `tests/fixtures/live30-segmentos.json` (transcrição com palavras), e geram vídeos sintéticos com ffmpeg para os casos de falha.
