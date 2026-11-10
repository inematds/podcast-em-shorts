# Dúvidas e limitações observadas

Nenhuma gravação foi barrada nesta rodada. Os testes ficaram congelados;
nenhum limite foi alterado para aprovar a fixture.

- No teste extra `camera-teste` (webcam isolada da própria fixture), YuNet
  confundiu uma mão com um segundo rosto em 16,0 s do corte. O verificador
  manteve `rosto_legenda` reprovado e saída 1. Não se deve aprovar esse
  resultado automaticamente nem trocar a checagem pela caixa prevista.
  A pessoa precisa conferir o quadro e decidir se refaz o enquadramento.
- A margem de cabeça e a detecção são verificações geométricas por amostra;
  não comprovam todos os quadros ou o sentido do conteúdo. A revisão humana
  continua obrigatória, especialmente com várias pessoas ou cortes de cena.
- faster-whisper não está instalado neste ambiente. A importação por JSON
  foi validada; o caminho sem motor retorna 2 com orientação. Transcrição
  real pelo motor opcional não foi medida nesta rodada.
- `novo --forcar` recadastra a mesma mídia; recusa substituir um original
  diferente, preservando `raw/`. Use outro identificador para outra gravação.
