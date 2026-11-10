# Regras do podcast-em-shorts

Estas regras são critérios de construção e revisão. Uma nota de texto não
prevê audiência e não substitui assistir ao corte. A revisão humana decide.

## R1 — Preserve a gravação recebida
Por quê: o episódio original permite refazer qualquer corte sem perda.
Quem checa: importação e pessoa revisora.

## R2 — Corte uma passagem contínua
Por quê: remover palavras no meio pode mudar o sentido da fala.
Quem checa: conteúdo.

## R3 — Comece numa fronteira de frase
Por quê: o público precisa entender a entrada sem ouvir a frase anterior.
Quem checa: conteúdo, por pontuação ou pausa superior a 0,8 segundo.

## R4 — Termine uma ideia
Por quê: um corte com final interrompido promete uma resposta que não entrega.
Quem checa: conteúdo e pessoa revisora.

## R5 — A duração vem da marca
Por quê: um exemplo não autoriza mudar os limites para aprová-lo.
Quem checa: candidatos e conteúdo.

## R6 — Prefira afirmações verificáveis
Por quê: números, inclusive por extenso, dão algo concreto para avaliar.
Quem checa: candidatos, sinal `numero`; pessoa revisora confere a afirmação.

## R7 — Observe a conexão com quem escuta
Por quê: você, seu, sua e teu podem tornar explícita a utilidade da ideia.
Quem checa: candidatos, sinal `voce`.

## R8 — Reconheça uma mudança de raciocínio
Por quê: mas, só que, na verdade, o problema é, ninguém fala e o segredo
podem introduzir uma descoberta; o contexto confirma se ela existe.
Quem checa: candidatos, sinal `virada`; pessoa revisora.

## R9 — Perguntas precisam de resposta
Por quê: a interrogação abre uma expectativa que o restante do corte deve cumprir.
Quem checa: candidatos, sinal `pergunta`; pessoa revisora.

## R10 — Procure uma conclusão compreensível
Por quê: ou seja, resumindo, a lição, no fim das contas e então o que
costumam explicitar o resultado de um raciocínio.
Quem checa: candidatos, sinal `veredito`.

## R11 — Nomes próprios são pistas frágeis
Por quê: uma inicial maiúscula fora do início da frase pode indicar uma
entidade concreta, mas também pode ser apenas erro de transcrição.
Quem checa: candidatos, sinal `nome`; pessoa revisora.

## R12 — Valorize demonstrações
Por quê: por exemplo, imagina, olha isso e vou mostrar podem levar a uma
situação observável, mais fácil de compreender que uma promessa genérica.
Quem checa: candidatos, sinal `exemplo`; pessoa revisora.

## R13 — Marque dependência de contexto
Por quê: como eu falei, como eu disse, lá atrás, ontem e na live passada
podem exigir informação ausente do corte.
Quem checa: candidatos, alerta `referencia_atras`; pessoa revisora.

## R14 — Separe a ideia dos pedidos de interação
Por quê: se inscreve, inscreva, link na descrição, comenta aí e deixa o like
consomem tempo sem concluir o assunto.
Quem checa: candidatos, alerta `chamada`; conteúdo.

## R15 — Revise entradas hesitantes
Por quê: então, né, tipo, aí, é, bom e e podem ser restos de uma frase
anterior quando aparecem como primeira palavra.
Quem checa: candidatos, alerta `muleta_inicio`; conteúdo e pessoa revisora.

## R16 — Não esconda a falta de fechamento
Por quê: ausência de ponto, interrogação ou exclamação no fim exige revisão.
Quem checa: candidatos, alerta `sem_fechamento`; conteúdo.

## R17 — Ofereça opções realmente diferentes
Por quê: trechos com mais da metade do menor trecho em comum repetem a escolha.
Quem checa: seleção de candidatos, pela interseção temporal.

## R18 — Preserve cabeça e ombros na webcam
Por quê: ampliar só a face perde cabelo, testa e contexto da expressão.
Quem checa: render preenche 1080×960 com recorte interno de cerca de 3%,
face com pelo menos 300 px, cabeça e ombros visíveis; quadros e pessoa revisora.
Todo recorte deve ficar dentro dos quatro lados de `camera`, inclusive após
arredondar. Se faltar espaço acima da cabeça, encostar no topo da webcam
ou reduzir o zoom. Não repetir, espelhar ou esticar faixas da imagem para
inventar espaço. Áreas descobertas recebem a webcam inteira desfocada e
escurecida, preservando a proporção da pessoa. Registrar em `recortes_camera`
do `<id>.legendas.json` o tempo relativo ao clip e a caixa `[x,y,w,h]` em
pixels da origem, por mudança de recorte (uma entrada em t=0 se for fixo).
A checagem `cabeca_cortada` permanece integral, mesmo no limite da origem.

## R19 — Detecte rostos de verdade
Por quê: a posição prevista no layout não comprova onde a pessoa está em cada quadro.
Quem checa: quadros, com YuNet; pessoa revisora.

## R20 — Reserve espaço para a leitura
Por quê: legenda ou título sobre a face atrapalham expressão e leitura.
Quem checa: quadros, com margem de 4% da altura e extensão superior de 25% da face.
Título Montserrat Black de pelo menos 80 px, até duas linhas, acima da testa,
com fundo semitransparente e palavra forte em destaque durante `titulo_segundos`.
Se precisar de duas linhas, reduzir o zoom e abrir espaço acima da cabeça
com fundo desfocado e escurecido da webcam; reservar também folga para o
movimento, sem copiar uma faixa com cabelo para cima da pessoa.

## R21 — Uma linha de legenda por vez
Por quê: linhas acumuladas escondem a tela e tornam incerta a palavra atual.
Quem checa: render e pessoa revisora. Na divisão tela+camera, a legenda fica
centralizada numa faixa lisa de 140 px na cor `fundo`, sem degradê.

## R22 — Destaque só a palavra falada
Por quê: o destaque deve acompanhar o áudio sem antecipar a próxima palavra.
Quem checa: render pelos tempos importados; pessoa revisora ouvindo.

## R23 — Escolha entre tela inteira e recorte legível
Por quê: telas largas podem ficar pequenas demais na metade inferior.
Quem checa: `tela_modo` da marca: `inteira` preserva a tela sobre fundo desfocado;
`preencher` cobre os 1080×820 úteis com recorte que acompanha diferenças entre
quadros, centro suavizado, velocidade limitada e parada sem atividade.
`auto` usa `preencher` quando a legibilidade é incerta (fallback desta versão).
Remover barra inferior uniforme e persistente quando detectável.
Pessoa revisora confere controles e textos cortados.

## R24 — Respeite as áreas seguras
Por quê: controles do player podem cobrir texto nas bordas.
Quem checa: quadros, com os limites da marca. Topo de 10% (192 px),
laterais de 6% e base de 20%. O enquadramento deve abrir espaço acima
do cabelo para o título com fonte mínima de 80 px; nunca reduzir o limite.

## R25 — Verifique imagem, movimento e áudio
Por quê: um arquivo existente pode conter silêncio, tela preta ou imagem parada.
Quem checa: quadros; pessoa revisora ouve o corte completo.

## R26 — Uma decisão humana libera a exportação
Por quê: qualidade de conteúdo e sentido não se resumem a verificações automáticas.
Quem checa: revisão e exportação; nada é publicado automaticamente.

## R27 — Falha deve permanecer visível
Por quê: afrouxar uma checagem oculta o problema e produz aprovação enganosa.
Quem checa: comandos retornam erro e explicação; pessoa revisora.

## R28 — Mude a marca num único lugar
Por quê: fonte, cores e limites dispersos deixam versões inconsistentes.
Quem checa: implementação e revisão do arquivo de marca.

## R29 — Transforme observações recorrentes em critérios
Por quê: uma nota específica pode prevenir repetição do mesmo problema.
Quem checa: pessoa revisora, acrescentando regras pessoais a partir de R200.

## R30 — Confira a integridade do detector
Por quê: um download truncado ou outro modelo não deve passar por YuNet válido.
Quem checa: detector confere tamanho e SHA-256, inclusive com PES_YUNET.

## R31 — Valide a anatomia antes de proteger uma face
Por quê: uma mão junto ao rosto pode produzir caixa facial no YuNet; ampliar
o espaço da legenda não corrige essa identificação falsa.
Quem checa: detector exige os cinco pontos finitos próximos da caixa, olhos
aproximadamente horizontais (desnível até metade da distância horizontal),
distância horizontal entre olhos de 20% a 80% da largura, olhos acima do nariz
e nariz acima dos cantos da boca, com separação vertical mínima de 2% da altura.
Nariz e centro da boca ficam entre os olhos, com tolerância lateral de 15%/20%
da distância entre eles; olhos até boca ocupam de 12% a 65% da altura.
A face principal é a válida de maior pontuação (mínimo 0,65); secundárias
exigem 0,80 e contam desde a primeira aparição, sem espera por estabilidade.
Quadros mantém a proteção R20 inteira, inclusive abaixo do queixo.

## R32 — Grave relatórios apenas no destino autorizado
Por quê: conferir um vídeo externo não deve criar arquivos junto à entrada.
Quem checa: `checar-quadros` salva automaticamente junto ao vídeo somente sob
`<raiz>/episodios/<episódio>/` com `ep.json`; `--salvar <arquivo>` escolhe um
destino explícito, inclusive para vídeos externos. A saída da CLI permanece disponível.

### Como a nota dos candidatos é calculada

Cada sinal positivo distinto vale 2 pontos; cada alerta distinto desconta
4 pontos. A presença de número ou de você/seu/sua/teu nas primeiras 15
palavras acrescenta 1 ponto. Em empate, o trecho mais curto vem primeiro;
persistindo o empate, vem o menor índice inicial. O top descarta um trecho
quando a interseção ultrapassa metade da duração do menor dos dois.
Esses pesos são escolhas editoriais locais, não estimativas de audiência.

O gancho falado recebe até 10 pontos: até 18 palavras (2), entrada sem
muleta (3), sujeito ou objeto concreto (3), número ou você (2). O título
recebe 2 pontos por critério: até 7 palavras, até 40 caracteres, ausência de
reticências, inicial destacada ou número, palavra concreta ou forte.
Cada parte precisa de pelo menos 6. A pessoa confere sentido e fidelidade.
