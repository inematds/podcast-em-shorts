# podcast-em-shorts

[![Your livestream becomes shorts](guia/assets/banner-en.jpg)](https://inematds.github.io/podcast-em-shorts/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

podcast-em-shorts is a free Python toolkit that turns a long recording (podcast, livestream, interview, or lesson) into vertical short videos. It reads the transcript, identifies clips that make sense on their own, crops them to 9:16 with the face enlarged and the screen below, writes word-by-word captions, and checks every frame. It’s for people who record a lot and don’t have time to edit. You need a computer with Python and ffmpeg; no account, key, or paid service is required.

## 📖 User guide

Full guide (landing page + step-by-step instructions): **https://inematds.github.io/podcast-em-shorts/guia/en/**

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
.venv/bin/python pes.py exportar minha-live     # copies only the approved clips
```

## Commands

`doutor`, `novo`, `transcrever`, `corrigir`, `palavras`, `candidatos`, `escolher`, `gancho`, `layout`, `render`, `checar-quadros`, `checar-conteudo`, `revisao`, `regra`, `exportar`, `tudo`. Each has `--help`.

To find the indices used for manual selection:

```bash
.venv/bin/python pes.py palavras minha-live --de 540 --ate 600 --busca "liberdade"
.venv/bin/python pes.py escolher minha-live manual --ajustar s1=1239:1255
```

`palavras <ep> [--de <seconds>] [--ate <seconds>] [--busca <text>]`
shows full sentences that overlap the interval (inclusive bounds). Search
ignores case and accents and combines with the time filters; all are optional.
Each line includes the start index, start time, and end index:
`[1239] 09:27.7  AI builds a material paradise.[1246]`.
Indices start at zero, and the `--ajustar` endpoints are inclusive.
`candidatos` also shows `ini` and `fim` in the readable table.

`tudo` prints the review command using the same interpreter that is running
(including the one in the venv), with `pes.py` as a relative path when run from the toolkit root.
`revisao` prints the address and a tip for accessing it from a phone: run it with
`--host 0.0.0.0` and use this computer’s IP address on the same network, keeping the displayed port.

- **The toolkit doesn’t publish anything.** It generates, checks, and organizes; you approve.
- Branding (colors, font, captions, duration, quantity) in `marca/marca.json`.
- Toolkit rules in `regras/REGRAS.md`; your rules, starting at R200, in `regras/MINHAS-REGRAS.md`.
- Skill for Claude Code / Codex in `skill/podcast-em-shorts/`.
- Real examples in `exemplos/` (3 shorts from a 57-minute livestream).
- Tests: `python3 -m unittest discover -s tests -v`.

Technical details: [docs/SPEC.md](docs/SPEC.md) and [docs/IMPLEMENTACAO.md](docs/IMPLEMENTACAO.md).

Montserrat font under the SIL Open Font License (`marca/fontes/OFL.txt`). YuNet face detector (OpenCV Zoo), downloaded on first run.

---

Made by [INEMA.CLUB](https://inema.club) — practical AI, free of charge.