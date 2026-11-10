# Implementação — rodada 10 — 10/11/2026

Rodada 10 elimina o vulto no preenchimento da webcam; as demais seções registram as rodadas anteriores.
`tests/` permanece congelado nesta rodada.
Sem commit, push, API paga ou cópia de `_referencia`.

## Preenchimento sem silhueta (rodada 10)

O preenchimento desfocado da rodada 9 ainda mostrava um vulto da cabeça
no topo de s3 a partir de aproximadamente 10 s. `pes/render.py` substitui
essa camada por uma fonte `color` de 1080×960 com `cores.fundo` da marca
(`#0c0c10`), sem receber nenhum pixel da webcam. O degradê vertical mantém
a crominância e varia a luminância de 100% no topo a 115% na base,
sem escurecer a cor da marca até parecer uma faixa preta.

Quando o recorte nítido começa abaixo de y=0, sua opacidade cresce
linearmente de 0 a 100% nos primeiros **40 px** (`clip(Y/40,0,1)`),
mesclando a imagem ao degradê. Quando começa em y=0, permanece opaco
desde o topo. Permanecem o recorte fixo dentro da webcam limpa, a
remoção confirmada de moldura, o zoom mínimo, a proteção de cabelo/queixo,
o título em y=192 e as faixas de legenda e tela. Os verificadores não mudaram.

## Validação real da rodada 10

`python3 pes.py render ia-superinteligente --todos` — saída 0;
s1 55,6 s, s2 41,8 s e s3 52,8 s de render. Os três MP4 e suas
miniaturas foram regenerados. Executados `checar-quadros <mp4> --legendas
<legendas.json>` e `checar-conteudo ia-superinteligente <id>` para cada
clip: seis saídas 0, **QUADROS OK / CONTEUDO OK**.

| clip | rostos/amostras | colisões / cabeças cortadas | título y | quadros/conteúdo |
|---|---|---|---:|---|
| s1 | 66/67 | 0 / 0 | 192 | OK / OK |
| s2 | 51/52 | 0 / 0 | 192 | OK / OK |
| s3 | 71/71 | 0 / 0 | 192 | OK / OK |

Inspeção visual dos três clips a 0,5, 12 e 20 s: topo liso, sem vulto,
transição suave para a webcam e título acima da cabeça. Em y=0…59,
as nove amostras têm desvio horizontal máximo **0,0 por canal** e a
mesma média BGR **16/11/11** após compressão: nenhuma silhueta variável.
O fundo continua independente da imagem por construção do grafo.

A primeira execução da suíte detectou o degradê inicialmente escurecido
como faixa preta (35/36). A correção foi preservar a luminância da cor
`fundo` no topo e clarear para baixo, sem alterar testes ou verificadores.
Execução final `python3 -m unittest discover -s tests -v` — saída 0,
**36/36 testes**, 152,867 s. Permanecem os `ResourceWarning` já existentes.
Todos os arquivos de `tests/`, exceto caches de execução, foram comparados
por SHA-256 antes/depois: idênticos.

Evidências em `/home/nmaldaner/projetos/output/podcast-em-shorts/rodada10/`:
`quadros.jpg`, quadros individuais, `inspecao.json`, hashes iniciais,
logs do render, das seis checagens e das duas execuções da suíte.
Falhas e correções mínimas registradas em `FALHAS.md`.
Sem commit, push ou chamada de API nesta rodada.

## Webcam desde y=0 e origem do fio (rodada 9)

A área segura de 10% restringe **texto**, não imagem. A webcam preenche
1080×960 desde y=0, com a pessoa no recorte seguro e o espaço restante
preenchido pela própria webcam desfocada/escurecida. O título permanece
em y=192, acima do cabelo, sobre o fundo semitransparente da marca.

O fio vinha da moldura **na mídia original**, não do ASS: a caixa
`[1520,850,400,230]` incluía duas linhas brancas em y=850–851.
Em s1 a 568,16 s da origem, 100% dos pixels dessas linhas tinham todos
os canais acima de 200; em y=852 essa proporção era zero. A ampliação
do recorte deslocado verticalmente transformava essa borda no fio visível.
A moldura inferior em y=1078–1079 também é retirada. A caixa limpa
fica `[1520,852,400,226]` em s1/s2 e `[1520,850,400,228]` em s3:
sem borda clara no topo do s3, esses pixels são preservados.

`sem_moldura` confirma bordas claras contínuas em três quadros (início,
50% e 90% do clip): pelo menos 98% da linha/coluna com todos os canais
acima de 200. Retira no máximo seis pixels por lado, somente a partir
da borda; sem confirmação, preserva o topo e o cabelo. A caixa resultante
continua inteiramente dentro da webcam original. A medição da cabeça e
o recorte fixo usam essa caixa limpa, assim como o fundo desfocado.

O fundo agora é sempre composto desde y=0: redução para 270×240,
`boxblur=6:2`, ampliação para 1080×960 e canais multiplicados por 0,85.
O preenchimento anterior (54×48, blur 12 e fator 0,65) apagava a textura
e fazia o topo parecer uma faixa preta. Não há espelho, repetição de
bordas nem pixels da tela usados no preenchimento. Mantidos zoom com
face mínima de 300 px, cabeça inteira, recorte interno, faixa de legenda
y=960…1100 e tela y=1100…1920. `pes/render.py`: 232 linhas.

A pendência `mao7` está resolvida: o usuário regenerou a fixture a partir
do render novo, trecho 7–14 s do s1. Não houve alteração em `tests/`
nesta rodada nem exceção nos verificadores.

## Área segura e enquadramento (rodada 8)

`marca/marca.json`: topo restaurado para **0,10**, base preservada em **0,20**.
Título começa em `ceil(1920 × topo)` = **192 px**, Montserrat Black **80 px**.
Duas linhas usam altura da tinta + 8 px por linha, sem reduzir a fonte.
A geometria reserva também cabelo (25% da face) e margem de 76,8 px.

`pes/enquadramento.py` mede a mediana da face do próprio clip a 2 fps,
o cabelo mais alto enquanto o título está ativo e o queixo mais baixo
durante todo o corte. `pes/render.py` resolve a faixa vertical permitida
entre título e legenda com folga adicional de 10 px acima e 2 px abaixo,
além da margem obrigatória de 76,8 px em ambos os lados. O zoom
alvo é 302 px de face, com arredondamento que preserva o mínimo de 300 px.
Se a faixa não existe, falha com os dois limites numéricos, sem afrouxar regras.

O recorte fica fixo por clip, ancorado no topo da webcam e limitado aos
quatro lados de `layout.camera`; também cabe nos 1080×960 de destino.
A folga usa a webcam inteira muito desfocada e escurecida. Não há faixa de
cabelo esticada, espelho ou pixels buscados fora da webcam. As caixas da
origem continuam registradas em `recortes_camera`. Se `layout.json` estiver
ausente, `render` faz a análise local antes de enquadrar.

## Falso rosto da mão e destino dos relatórios

`pes/rostos.py` valida os cinco pontos do YuNet antes de devolver caixas:
olhos aproximadamente horizontais, distância entre olhos proporcional à caixa,
nariz entre olhos e boca, pontos próximos da caixa e valores finitos.
A face válida de maior confiança tem mínimo 0,65; secundárias exigem 0,80.
Limites e tolerâncias constam na R31. Não há espera por trilha temporal:
uma segunda face válida já recebe proteção na primeira amostra.
A margem R20 continua em 4% da altura, com extensão superior de 25% da face.
Limite: a heurística favorece faces frontais ou moderadamente inclinadas;
perfis e inclinações acentuadas continuam exigindo revisão humana.

Antes da correção, `mao7` tinha 10 colisões falsas: a mão recebia 0,68–0,75,
com olhos muito próximos e nariz lateral. Depois: 14 rostos em 14 amostras,
zero colisões. Legenda sobre o rosto real e 10 px abaixo do queixo continuam
reprovando nos testes congelados. Em conferência adicional, duplicar o quadro
lado a lado preservou as duas faces verdadeiras detectadas.

`checar-quadros` grava automaticamente apenas sob `<raiz>/episodios/<ep>/`
com `ep.json`. Fora disso, imprime o resultado sem gravar; `--salvar <arquivo>`
escolhe o destino explicitamente (R32). Verificado com `mao7` e destino em
`/tmp/pes-rodada5-explicito.json`; nenhum `.quadros.json` ficou em `tests/`.
O relatório criado pela execução inicial do código antigo foi removido.

Comandos reais executados com `--legendas` correspondente:
`python3 pes.py checar-quadros episodios/ia-superinteligente/clips/s1.mp4 --legendas episodios/ia-superinteligente/clips/s1.legendas.json`
e o mesmo para `s2`: ambos retornaram código 0 e `QUADROS OK`.
s1: 67 rostos em 67 amostras; s2: 52 em 52. Zero colisões e cortes de cabeça.

## Layout preservado

Webcam nos 1080×960 superiores; faixa lisa de legenda em y=960…1100;
tela nos 1080×820 inferiores. `tela_modo` aceita `inteira`, `preencher`
e `auto`; este usa `preencher`. A atividade da tela é suavizada e limitada
em velocidade; não há OCR. A heurística de barra de tarefas e os verificadores
de rosto/cabeça não foram alterados na rodada 8.

## Transcrição local sem decodificação PyAV (rodada 8)

O ffmpeg extrai mono a **16 kHz**, PCM **float32** little-endian via pipe.
Um array numpy é passado a `WhisperModel.transcribe`, preservando
`word_timestamps=True`. Não se passa caminho ao motor, evitando `decode_audio`
e o erro de `metadata_errors` do PyAV. Áudio vazio/não finito é recusado.
Extração tem timeout de 600 s; o array ocupa aproximadamente 230 MB por hora.

Executado o comando solicitado, usando o Python em:
`/tmp/claude-1000/-home-nmaldaner-projetos-wifi/fb945502-587a-450b-9f0c-b7630503c8ea/scratchpad/venv/bin/python`
com `pes.py transcrever fw --modelo small --idioma pt --raiz`
`/tmp/claude-1000/-home-nmaldaner-projetos-wifi/fb945502-587a-450b-9f0c-b7630503c8ea/scratchpad/raiz-fw`.

Ambiente: faster-whisper **1.2.1**, PyAV **19.0.2**, numpy **2.5.4**.
`ctranslate2.get_cuda_device_count()` = **0**; usado CPU, `compute_type=int8`.
Saída real, código 0: `Transcrição: 70 palavras`, `0 palavras corrigidas`.

| palavra | início (s) | fim (s) |
|---|---:|---:|
| É, | 0,00 | 0,08 |
| tipo | 0,22 | 0,38 |
| um | 0,38 | 0,62 |
| dicionário, | 0,62 | 1,82 |
| que | 2,46 | 2,92 |
| nem | 2,92 | 3,12 |
| no | 3,12 | 3,26 |
| meu | 3,26 | 3,42 |
| caso, | 3,42 | 3,92 |

## Transcrição imperfeita

`transcrever --de-json` aceita lista de segmentos ou objeto com `segments`.
Recuos de início menores que 0,3 s são ajustados à ordem anterior. Duração
zero/negativa reparável recebe fim = início + 0,02 s, limitado ao próximo
início quando há espaço. Se os inícios coincidem, desloca também a palavra
seguinte para abrir espaço. Cada palavra alterada é contada uma única vez.
Entradas irrecuperáveis (texto vazio, tempos não finitos/negativos ou recuos
maiores) são descartadas com aviso; sem palavras ou com maioria inválida,
recusa antes de sobrescrever `work/palavras.json`.

Execução real:

```text
python3 pes.py transcrever ia-superinteligente --de-json /home/nmaldaner/projetos/output/podcast-em-shorts/ep/tr/transcript.json
Transcrição: 6443 palavras
4 palavras corrigidas
```

As duas durações zero estão nos índices 1127 e 6129; as seguintes (1128 e
6130) também mudaram para abrir espaço. Conferidos todos os textos e índices,
ordem dos inícios, durações positivas e limite da próxima palavra: OK.
Nenhuma palavra descartada. O JSON original foi preservado.

## Correção e escolha manual

```bash
python3 pes.py corrigir ia-superinteligente --trocar "Iá=IA"
python3 pes.py corrigir ia-superinteligente --trocar "Iá=IA" --trocar "IAs=IAs" --de 1239 --ate 1315
python3 pes.py escolher ia-superinteligente manual --ajustar s1=1239:1315 --titulo "s1=Liberdade e IA"
```

Exemplos documentados; não aplicados ao texto da live usado no ranking abaixo.
`corrigir` troca palavras literais com distinção de maiúsculas; origem/destino
contêm letras/números, sem espaços. Preserva pontuação colada (`Iá,` → `IA,`),
índices e tempos. Não encadeia trocas: cada palavra usa seu texto original.
`--de` e `--ate` são inclusivos e começam em zero; omitidos, usam os extremos.
Imprime `N palavras trocadas`; erro de argumento não altera o arquivo.
Invalida a aprovação dos cortes afetados, sem mudar os títulos. Regere os
candidatos para atualizar seus textos e renderize novamente antes da revisão.

A origem `manual` dispensa `work/candidatos.json` e exige o ajuste de cada sN.
Aceita `manual,manual` ou `c01,manual --ajustar s2=1239:1315` com candidatos
existentes. Uma nova seleção substitui `clips.json` e limpa `revisao.json`.
Verificação pela CLI em episódio temporário: pontuação, limites inclusivos,
metadados intactos, aprovação invalidada, dois cortes manuais e rejeição de
índices/trocas inválidos passaram. Nenhum arquivo em `tests/` foi alterado.

## Nota e leitura editorial da live

Janelas seguem frases/pause de mais de 0,8 s, nunca cortam palavras e preferem
início maiúsculo por desconto de `inicio_meio` nas alternativas minúsculas.
O alerta é conservador mesmo após ponto; cobre também falta de pontuação
na palavra anterior. `depende_tela` cobre as expressões pedidas, variantes
demonstrativas e três ou mais “aqui”/“ó”. Nome ignora início do trecho e
maiúsculas após ponto; é apenas um sinal fraco (+0,5).

Cada sinal conta no máximo uma vez por frase. Pesos: número 2,5; virada 3,5;
veredito 3; exemplo/pergunta 1; você 0,7. A carga ponderada é dividida pelo
número de frases e pelo tempo em unidades de 10 s; os dois valores são somados.
A quantidade de frases tem piso de palavras/15 para não premiar ausência de
pontuação. Veredito nas últimas 18 palavras soma 4. Alertas descontam:
início no meio 5, depende da tela 7, referência anterior 4, chamada 5,
muleta inicial 2 e falta de fechamento 4. “Então o que…?” não é veredito.
A nota tem três casas no JSON e uma na CLI. Mantida a restrição de sobreposição.

Executado `python3 pes.py candidatos ia-superinteligente --top 12` após a
reimportação; lidos os 12 textos completos. Top 5 com nota exata do JSON:

| id | início (s) | duração (s) | nota | alertas | 12 primeiras palavras |
|---|---:|---:|---:|---|---|
| c01 | 386.16 | 22.08 | 11.280 | nenhum | Ótimo, só que um projeto de cada vez você vai ser muito |
| c02 | 567.66 | 20.68 | 10.466 | nenhum | A Iá constrói um paraíso material, com saúde, conforto, abundância, mas a |
| c03 | 2403.46 | 48.28 | 10.210 | nenhum | Quando chegou naquilo, você salva como um MD. Certo? Beleza. Depois, o |
| c04 | 2907.74 | 32.82 | 9.486 | nenhum | Por exemplo, hoje eu acertei um bug. Não era um bug, mas |
| c05 | 2444.50 | 24.18 | 8.441 | nenhum | Ou seja, você vai dando o nome e você vai descrevendo o |

A faixa dos 12 primeiros agora vai de 11.280 a 7.436. c01 contrapõe
trabalho serial à metáfora do maestro; c02 contrapõe conforto à liberdade;
c03 explica glossários com exemplos e conclusão; c04 explica handoff e dá
um número concreto; c05 retoma glossários. A densidade separa esses trechos
do preenchimento sintético nos testes congelados (diferença mínima de 2).

Limites observados na leitura: c03 começa com referência vaga (“naquilo”);
c04/c05 contêm nomes possivelmente errados (“Session Handbook”, “Kumanos”);
c07 ainda começa com “Ajuda” e relato de mensagens, dependente de contexto.
Os alertas não detectam toda dependência semântica ou erro do Whisper.
O top é uma lista para revisão, sem aprovação ou garantia de autonomia.

## Validação real da rodada 9

`python3 pes.py render ia-superinteligente --todos` — saída 0:
s1 32,2 s; s2 29,7 s; s3 26,3 s (tempos do render, sem medição inicial).
Executados `checar-quadros` com `.legendas.json` correspondente e
`checar-conteudo ia-superinteligente <id>` para os três clips: seis
saídas 0, `QUADROS OK` / `CONTEUDO OK`. Sem alteração dos verificadores.

| clip | face prevista (px) | título y / fim y | rostos/amostras | colisões / cabeças cortadas | quadros/conteúdo |
|---|---:|---|---|---|---|
| s1 | 301,68 | 192 / 344 | 67/67 | 0 / 0 | OK / OK |
| s2 | 301,13 | 192 / 376 | 52/52 | 0 / 0 | OK / OK |
| s3 | 301,47 | 192 / 374 | 71/71 | 0 / 0 | OK / OK |

Conferência adicional percorreu **todos os 2.828 quadros** em ordem:
997 do s1, 769 do s2 e 1.062 do s3. Na faixa y=0…189, médias mínimas
de cinza de 16,42 / 14,18 / 11,85 e desvios mínimos de 8,32 / 7,62 /
7,01: há textura, sem faixa uniforme preta. Nenhuma linha na metade
superior teve 98% de pixels acima de 200; máximos de 23,70% / 22,96% /
16,94%, sem o fio claro contínuo. Esses indicadores verificam a falha
visual específica; não substituem detecção de rostos ou revisão humana.
Inspeção da folha de quadros de cada clip a 0,5, 7 e 14 s: topo com
webcam desfocada, sem moldura branca, título acima da cabeça.

Evidências locais em `/home/nmaldaner/projetos/output/podcast-em-shorts/rodada9/`:
`quadros.jpg`, `inspecao.json`, logs do render, das seis checagens e da suíte.

`python3 -m unittest discover -s tests -v` — **saída 0, 36/36 testes**,
135,235 s. `ResourceWarning` de arquivos abertos pelos testes permanece;
não impede a aprovação. Inclui `mao7` regenerada pelo usuário (7–14 s
do s1). Todos os arquivos de `tests/`, exceto caches de execução, foram
comparados por SHA-256 antes/depois e permaneceram idênticos.
Sem commit, push ou chamada de API nesta rodada.
