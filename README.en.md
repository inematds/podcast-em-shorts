# podcast-em-shorts

[![Your livestream becomes shorts](guia/assets/banner-en.jpg)](https://inematds.github.io/podcast-em-shorts/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

podcast-em-shorts is a free Python toolkit that turns a long recording (podcast, livestream, interview, or class) into short vertical videos. It reads the transcript, identifies segments that make sense on their own, crops them to 9:16 with the face enlarged and the screen below, writes word-by-word captions, and checks every frame. It’s for people who record a lot and don’t have time to edit. You need a computer with Python and ffmpeg; no account, key, or paid service is required.

## 📖 User guide

Complete guide (landing page + step-by-step instructions): **https://inematds.github.io/podcast-em-shorts/guia/en/**

## Quick start

```bash
git clone https://github.com/inematds/podcast-em-shorts
cd podcast-em-shorts
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt faster-whisper
.venv/bin/python pes.py doutor
.venv/bin/python pes.py novo minha-live --video /caminho/da/live.mp4
.venv/bin/python pes.py tudo minha-live --modelo small --idioma pt
.venv/bin/python pes.py revisao minha-live      # approve on the page that opens
.venv/bin/python pes.py exportar minha-live     # copy only the approved ones
```

Commands: `doutor`, `novo`, `transcrever`, `corrigir`, `candidatos`, `escolher`, `gancho`, `layout`, `render`, `checar-quadros`, `checar-conteudo`, `revisao`, `regra`, `exportar`, `tudo`. Each has `--help`.

- **Nothing is published by the toolkit.** It generates, checks, and organizes; you approve.
- Branding (colors, font, captions, duration, quantity) in `marca/marca.json`.
- Toolkit rules in `regras/REGRAS.md`; your rules, starting at R200, in `regras/MINHAS-REGRAS.md`.
- Skill for Claude Code / Codex in `skill/podcast-em-shorts/`.
- Real examples in `exemplos/` (3 shorts from a 57-minute livestream).
- Tests: `python3 -m unittest discover -s tests -v`.

Technical details: [docs/SPEC.md](docs/SPEC.md) and [docs/IMPLEMENTACAO.md](docs/IMPLEMENTACAO.md).

Montserrat font under the SIL Open Font License (`marca/fontes/OFL.txt`). YuNet face detector (OpenCV Zoo), downloaded on first run.

---

Made by [INEMA.CLUB](https://inema.club) — AI in practice, free.