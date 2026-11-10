# Dúvidas e limitações observadas

Rodada 9: limites preservados; nenhum arquivo em `tests/` alterado nesta rodada.

- No teste extra `camera-teste` (webcam isolada da própria fixture), YuNet
  confundiu uma mão com um segundo rosto em 16,0 s do corte. O verificador
  manteve `rosto_legenda` reprovado e saída 1. Não se deve aprovar esse
  resultado automaticamente nem trocar a checagem pela caixa prevista.
  A pessoa precisa conferir o quadro e decidir se refaz o enquadramento.
- A margem de cabeça e a detecção são verificações geométricas por amostra;
  não comprovam todos os quadros ou o sentido do conteúdo. A revisão humana
  continua obrigatória, especialmente com várias pessoas ou cortes de cena.
- Transcrição local validada no venv indicado: faster-whisper 1.2.1 + PyAV
  19.0.2, CPU/int8, 70 palavras. ffmpeg entrega numpy float32 a 16 kHz;
  o decodificador PyAV não participa da leitura do áudio.
- `novo --forcar` recadastra a mesma mídia; recusa substituir um original
  diferente, preservando `raw/`. Use outro identificador para outra gravação.
- Legenda fixa na junção (y≈974) no modo tela+camera: quando a pessoa abaixa
  muito a cabeça, o queixo pode chegar a menos de 4% da altura da legenda e o
  `checar-quadros` reprova `rosto_legenda` (visto em 10/11 num trecho escolhido
  pelo `tudo` na live de 57 min). Caso limítrofe: não se reproduz com o mesmo
  trecho recomprimido. Hoje a saída é a pessoa trocar o trecho ou ajustar o
  corte; melhoria futura: mover a legenda conforme o rosto de cada trecho.
