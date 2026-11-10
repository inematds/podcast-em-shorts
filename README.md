# podcast-em-shorts

[![Sua live vira shorts](guia/assets/banner.jpg)](https://inematds.github.io/podcast-em-shorts/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O podcast-em-shorts é um kit gratuito, em Python, que transforma uma gravação longa (podcast, live, entrevista ou aula) em vídeos curtos verticais. Ele lê a transcrição, aponta os trechos que se entendem sozinhos, corta em 9:16 com o rosto ampliado e a tela embaixo, escreve a legenda palavra a palavra e confere cada quadro. Serve para quem grava muito e não tem tempo de editar. Você precisa de um computador com Python e ffmpeg; nenhuma conta, chave ou serviço pago.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/podcast-em-shorts/guia/**

## Começo rápido

```bash
git clone https://github.com/inematds/podcast-em-shorts
cd podcast-em-shorts
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt faster-whisper
.venv/bin/python pes.py doutor
.venv/bin/python pes.py novo minha-live --video /caminho/da/live.mp4
.venv/bin/python pes.py tudo minha-live --modelo small --idioma pt
.venv/bin/python pes.py revisao minha-live      # aprove na página que abrir
.venv/bin/python pes.py exportar minha-live     # copia só os aprovados
```

Comandos: `doutor`, `novo`, `transcrever`, `corrigir`, `candidatos`, `escolher`, `gancho`, `layout`, `render`, `checar-quadros`, `checar-conteudo`, `revisao`, `regra`, `exportar`, `tudo`. Cada um tem `--help`.

- **Nada é publicado pelo kit.** Ele gera, checa e organiza; você aprova.
- Marca (cores, fonte, legenda, duração, quantidade) em `marca/marca.json`.
- Regras do kit em `regras/REGRAS.md`; as suas, a partir da R200, em `regras/MINHAS-REGRAS.md`.
- Skill para Claude Code / Codex em `skill/podcast-em-shorts/`.
- Exemplos reais em `exemplos/` (3 shorts de uma live de 57 min).
- Testes: `python3 -m unittest discover -s tests -v`.

Detalhes técnicos: [docs/SPEC.md](docs/SPEC.md) e [docs/IMPLEMENTACAO.md](docs/IMPLEMENTACAO.md).

Fonte Montserrat sob a SIL Open Font License (`marca/fontes/OFL.txt`). Detector de rosto YuNet (OpenCV Zoo), baixado na primeira execução.

---

Feito pelo [INEMA.CLUB](https://inema.club) — IA na prática, de graça.
