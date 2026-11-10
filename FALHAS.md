| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
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
