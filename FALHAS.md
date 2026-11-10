| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-11-10 | Escolha manual exigia índices sem consulta legível; comando de revisão perdia a venv e faltava dica de rede | adicionar palavras e ini/fim nos candidatos, imprimir sys.executable e caminho relativo na raiz, orientar acesso pelo celular | infra |
| 2026-11-10 | Webcam desfocada no preenchimento mostrava segunda cabeça no topo de s3 | trocar somente o preenchimento por degradê da marca sem pixels da webcam, com transição alfa de 40 px | infra |
| 2026-11-10 | Degradê escurecido abaixo de fundo reprovou a checagem de faixa preta (35/36) | iniciar na cor fundo sem escurecer e clarear suavemente até 115% de luminância | infra |
| 2026-11-10 | Cópia auxiliar de evidências buscou relatório de conteúdo em clips/ | copiar de work/, destino definido por conteudo.py | infra |
| 2026-11-10 | Topo da webcam parecia preto e moldura branca da origem virava fio horizontal ampliado | preencher desde y=0 com webcam desfocada menos escura e retirar somente borda branca contínua confirmada em três quadros | infra |
| 2026-11-10 | Enquadramento pela mediana do episódio colidia com título/legenda quando a cabeça se movia | medir mediana do clip e extremos durante título/legenda a 2 fps, resolver folga com zoom fixo e recorte interno | infra |
| 2026-11-10 | Título invadia os 10% reservados à interface dos apps após afrouxar a marca | restaurar topo 0,10, posicionar título pela marca e reduzir zoom/deslocar webcam dentro da origem | infra |
| 2026-11-10 | faster-whisper 1.2.1 com PyAV 19 recusava metadata_errors ao abrir MP4 | extrair float32 mono 16 kHz com ffmpeg e entregar array numpy ao Whisper; venv real passou | infra |
| 2026-11-10 | Player da revisão vazio e horizontal antes de carregar metadados | fixar aspect-ratio 9/16, gerar JPG no render ou abertura e exibir erro de vídeo | infra |
| 2026-11-10 | Ancorar webcam no topo aproximou a margem do queixo da legenda em s2; título tocava margem em s3 | reservar 16 px inferiores e 16 px extras no cálculo de zoom para título, sem alterar verificadores | infra |
| 2026-11-10 | Faixa da webcam esticada acima da pessoa duplicava a cabeça ao levantá-la | limitar recorte aos quatro lados de camera e preencher folga com webcam desfocada e escurecida; registrar caixa no JSON | infra |
| 2026-11-10 | YuNet confundia mão apontando com face e reprovava legenda livre | validar os cinco pontos e exigir confiança maior nas faces secundárias, preservando margem facial | infra |
| 2026-11-10 | checar-quadros gravava relatório junto a vídeos externos, inclusive fixtures | salvar automaticamente só dentro de episódio e oferecer --salvar explícito | infra |
| 2026-11-10 | Conferência auxiliar da live assumiu objeto, mas o JSON era lista | aceitar lista de segmentos ou objeto com segments na conferência | infra |
| 2026-11-10 | Whisper real com duas palavras de duração zero era recusado | reparar duração e pequenos recuos preservando índices; abrir espaço na próxima palavra quando necessário | infra |
| 2026-11-10 | Candidatos empatavam por presença de sinais e promoviam demonstrações sem contexto | normalizar densidade, limitar bônus final e descontar início solto e dependência da tela | infra |
| 2026-11-10 | Webcam com pad, face pequena e borda de janela; faixa desfocada sob legenda | recorte interno com cover, folga para título e faixa sólida de 140 px | infra |
| 2026-11-10 | Título ampliado colidia com a cabeça em movimento | medir tinta do título, subir o bloco e reduzir zoom com espaço superior em duas linhas | infra |
| 2026-11-10 | Detector removia só parte da barra de tarefas | selecionar a primeira fronteira forte persistente com maioria de colunas uniformes | infra |
| 2026-11-10 | Movimento vertical no modo camera aproximava face da legenda | seguir os dois eixos com velocidade limitada e folga vertical no recorte 9:16 | infra |
| 2026-11-10 | Webcam isolada era inferida como sobreposição e gerava tela de área zero | validar área útil e usar camera quando a estimativa ocupa o quadro inteiro | infra |
| 2026-11-10 | YuNet viu mão junto à legenda como rosto e acusou colisão | reservar mais distância vertical entre webcam e legenda, sem mudar o verificador | infra |
| 2026-11-10 | CLI confundia pes.py com pacote pes sem inicializador | adicionar pes/__init__.py | infra |
