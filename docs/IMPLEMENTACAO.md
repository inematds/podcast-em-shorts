# Implementação — rodada 4 — 10/11/2026

Os 27 testes congelados passaram (21 anteriores + 6 da rodada 4). `tests/` não foi
alterado. Sem commit, push, API paga ou cópia de `_referencia`.

## Render e layout preservados da rodada 3

- Webcam preenche 1080×960 com cover, recorte interno de aproximadamente 3%
  e enquadramento fixo pela mediana (sem tremor). Face prevista de 427 px.
  Leve compensação de exposição (+0,04) na webcam escura, sem faixas artificiais.
- Faixa lisa em `fundo`, y=960…1100 (140 px), legenda centralizada, contorno
  preto e apenas a palavra ativa na cor `destaque`. Tela útil de 1080×820.
- Título Montserrat Black de 80 px, uma ou duas linhas, palavra mais longa
  em destaque e fundo da marca semitransparente, durante `titulo_segundos`.
  Em duas linhas, reduz o zoom (face prevista de 310 px), abrindo espaço
  superior com o fundo da própria webcam. A junção desse fundo pode ser visível.
  Topo seguro da marca ajustado para 0,6% para manter o título acima da testa.
- `tela_modo`: `inteira` mantém fundo desfocado e tela inteira; `preencher`
  recorta e preenche, seguindo o centro das diferenças entre 32 amostras,
  suavizado e com velocidade limitada. Sem atividade, o centro para.
  `auto` (padrão) usa o fallback `preencher`; não há OCR de legibilidade.
- Barra inferior detectada por fronteira forte, uniformidade e persistência.
  Neste exemplo, a tela útil passou de 1510×1080 para 1510×1030.
- `pes/tela.py` concentra análise de atividade e interpolação. Os módulos
  de render da rodada 3 têm até 172 linhas. Regras R18/R20/R21/R23/R24 atualizadas.

## Verificações observadas

Exemplo regenerado com “Seu glossário de IA”: `exemplos/live30-s1.mp4`,
`.legendas.json`, `.quadros.json` e `live30-quadro.png`. Duração: 21,28 s.
QUADROS OK: 43 amostras, sem colisão e sem cabeça junto à borda.
Nos 90 quadros iniciais: face mínima de 407,26 px, cabelo acima de y=203,73,
nenhuma colisão com o título. Inspeção visual em quatro momentos do corte.
Título em duas linhas também passou no verificador real. Os três modos de
tela foram executados pelo ffmpeg. Em vídeo sintético, o centro seguiu
atividade à direita (x=400→610) e permaneceu idêntico no trecho estático.

Benchmark de 29,78 s: 4,116 s e 4,159 s, incluindo preparação do ASS.
SHA-256 idêntico nas duas execuções:
`af44b0de77ead4019fb688762a96ecdcd4384eccddaefdc766f2eb1f0014b6c4`.
As heurísticas de webcam/barra e a amostragem de atividade exigem revisão humana.

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

## Saída final dos testes

`python3 -m unittest discover -s tests -v` — código de saída 0.
Abaixo, resultado completo dos 27 casos, omitindo somente os ResourceWarning
sobre arquivos abertos pelos próprios testes congelados.

```text
test_doutor (test_pes.T00Doutor.test_doutor) ... ok
test_a_novo_recusa_repetido (test_pes.T01Fluxo.test_a_novo_recusa_repetido) ... ok
test_b_palavras (test_pes.T01Fluxo.test_b_palavras) ... ok
test_c_candidatos (test_pes.T01Fluxo.test_c_candidatos) ... ok
test_d_layout_tela_camera (test_pes.T01Fluxo.test_d_layout_tela_camera) ... ok
test_e_render_e_checagens (test_pes.T01Fluxo.test_e_render_e_checagens) ... ok
test_f_revisao_e_exportar (test_pes.T01Fluxo.test_f_revisao_e_exportar) ... ok
test_checar_conteudo_meio_da_frase (test_pes.T02Candidatos.test_checar_conteudo_meio_da_frase) ... ok
test_melhor_trecho_e_alertas (test_pes.T02Candidatos.test_melhor_trecho_e_alertas) ... ok
test_bom (test_pes.T03Gancho.test_bom) ... ok
test_ruim (test_pes.T03Gancho.test_ruim) ... ok
test_preto_silencio_e_resolucao (test_pes.T04QuadrosSinteticos.test_preto_silencio_e_resolucao) ... ok
test_numeracao_r200 (test_pes.T05Regras.test_numeracao_r200) ... ok
test_codigo_nao_publica (test_pes.T06SemRede.test_codigo_nao_publica) ... ok
test_marca_sem_cor_fixa_no_codigo (test_pes.T06SemRede.test_marca_sem_cor_fixa_no_codigo) ... ok
test_comeca_no_meio_da_frase (test_rodada4.TEscolha.test_comeca_no_meio_da_frase) ... ok
test_depende_da_tela (test_rodada4.TEscolha.test_depende_da_tela) ... ok
test_nome_nao_dispara_em_inicio_de_frase (test_rodada4.TEscolha.test_nome_nao_dispara_em_inicio_de_frase) ... ok
test_nota_separa_denso_de_vazio (test_rodada4.TEscolha.test_nota_separa_denso_de_vazio) ... ok
test_arquivo_quebrado_recusa (test_rodada4.TTranscricaoReal.test_arquivo_quebrado_recusa) ... ok
test_palavra_com_duracao_zero (test_rodada4.TTranscricaoReal.test_palavra_com_duracao_zero) ... ok
test_checagem_passa (test_visual.TVisual.test_checagem_passa) ... ok
test_legenda_tamanho (test_visual.TVisual.test_legenda_tamanho) ... ok
test_rosto_grande_e_inteiro_em_cima (test_visual.TVisual.test_rosto_grande_e_inteiro_em_cima) ... ok
test_tela_preenche_metade_de_baixo (test_visual.TVisual.test_tela_preenche_metade_de_baixo) ... ok
test_titulo_grande (test_visual.TVisual.test_titulo_grande) ... ok
test_webcam_preenche_metade_de_cima (test_visual.TVisual.test_webcam_preenche_metade_de_cima) ... ok

----------------------------------------------------------------------
Ran 27 tests in 31.782s

OK
```
