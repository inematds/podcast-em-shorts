---
name: podcast-em-shorts
description: Preparar cortes verticais de um episódio local, verificar imagem e conteúdo e organizar a aprovação humana, sem publicar.
---

# Podcast em shorts

Leia `docs/SPEC.md`, `docs/IMPLEMENTACAO.md` e as regras antes de executar.
O kit usa somente processamento local. Os testes estão congelados.

## Ordem de trabalho

1. Confira as dependências com `python3 pes.py doutor`.
2. Importe com `novo <ep> --video <arquivo>`. Preserve `raw/`.
   `--forcar` permite recadastrar a mesma gravação; outro original exige outro episódio.
3. Prefira a transcrição pronta: `transcrever <ep> --de-json <arquivo>`.
   Sem JSON, o motor opcional faster-whisper roda localmente em CPU.
   Durações zero/negativas e recuos menores que 0,3 s são reparados e contados.
   Leia o aviso de palavras inválidas descartadas, se houver.
4. Leia `candidatos <ep> --json` e seus alertas. Assista ao contexto antes
   de escolher. A nota é uma heurística; não prevê audiência.
5. Use `escolher <ep> c01,c02 --titulo 's1=Título'` para definir trechos
   contínuos. `--ajustar s1=ini:fim` usa índices das palavras originais.
   Confira o gancho com `gancho --falado ... --titulo ...`.
6. Rode `layout <ep>` e confira as caixas. Só force um modo com evidência visual.
7. Gere os cortes com `render <ep> --todos`.
8. Para cada corte, rode `checar-quadros <mp4> --legendas <json>` e
   `checar-conteudo <ep> <id>`. Preserve os relatórios e as reprovações.
9. Abra `revisao <ep>` no endereço local impresso. Assista e ouça cada corte:
   cabelo, boca, legenda, título, tela, sentido, sincronismo e fechamento.
10. Somente a pessoa aprova. `exportar <ep>` copia os aprovados e seus textos
    para `aprovados/`, sem distribuir os arquivos.

Todos os subcomandos aceitam `--raiz <pasta>` para marca, regras e episódios.
`tudo <ep> --de-json <arquivo>` executa os passos automáticos, escolhe até a
quantidade da marca sem alertas e apresenta o resumo e o comando de revisão.
Nunca aprova automaticamente. Um resumo reprovado mantém saída 1.
`revisao --so-html` cria uma página estática; decisões exigem o servidor local.

## Correção de palavras e seleção manual

Antes do render, corrija nomes com:

```bash
python3 pes.py corrigir meu-ep --trocar "Iá=IA" --trocar "Whisper=Wisper"
python3 pes.py corrigir meu-ep --trocar "Iá=IA" --de 1239 --ate 1315
python3 pes.py escolher meu-ep manual --ajustar s1=1239:1315 --titulo "s1=Liberdade e IA"
```

As trocas são literais, sensíveis a maiúsculas e aplicadas uma vez por palavra,
sem encadear substituições. Origem e destino usam letras/números, sem espaços.
`Iá,` vira `IA,`; pontuação, índices e tempos são preservados. `--de`/`--ate`
são índices inclusivos, começando em zero; omitidos, abrangem a transcrição.
O comando imprime a quantidade de palavras alteradas. Gere candidatos de novo
para atualizar seus textos; renderize novamente os cortes afetados. A correção
invalida a aprovação desses cortes, sem alterar títulos escolhidos manualmente.

`manual` dispensa candidatos e exige `--ajustar sN=ini:fim` para cada seleção.
Pode misturar: `escolher meu-ep c01,manual --ajustar s2=1239:1315`.
Uma nova seleção substitui `clips.json` e limpa as decisões de revisão.
A nota usa densidade por frase/10 s, valoriza virada, número e veredito final;
`inicio_meio` sinaliza início minúsculo (conservador mesmo após ponto), e
`depende_tela` sinaliza demonstrativos e excesso de “aqui”/“ó”. Leia os textos;
maiúsculas e pontuação do Whisper não garantem autonomia ou fechamento.

## Quando parar

- Pare no primeiro erro de dependência, arquivo ilegível ou modelo inválido.
- Não substitua uma reprovação por aprovação nem altere os testes congelados.
- Sem palavras temporizadas, não invente tempos para a legenda.
- A webcam inferida exige inspeção: se moldura ou cabeça ficarem cortadas,
  ajuste o enquadramento antes de renderizar novamente.
- Sem aprovação humana registrada, não exporte como aprovado.
- Não instale serviços, use motores remotos ou publique para resolver um erro.
- Reescolher ou renderizar novamente invalida a aprovação do corte alterado.

## Marca e regras pessoais

Use `marca/marca.json`; fonte e licença ficam em `marca/fontes/`.
Leia `regras/REGRAS.md` e `regras/MINHAS-REGRAS.md`.
Uma nota só vira regra quando a pessoa pedir: `regra --da-nota <ep> <id>`.
Preserve motivo e responsável pela checagem; não apresente opinião como teste.
