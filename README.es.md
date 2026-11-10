# podcast-em-shorts

[![Tu live se convierte en shorts](guia/assets/banner-es.jpg)](https://inematds.github.io/podcast-em-shorts/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

podcast-em-shorts es un kit gratuito en Python que transforma una grabación larga (podcast, live, entrevista o clase) en videos cortos verticales. Lee la transcripción, señala los fragmentos que se entienden por sí solos, recorta en formato 9:16 con el rostro ampliado y la pantalla abajo, escribe los subtítulos palabra por palabra y revisa cada cuadro. Es para quienes graban mucho y no tienen tiempo para editar. Necesitas una computadora con Python y ffmpeg; no hace falta ninguna cuenta, clave ni servicio de pago.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/podcast-em-shorts/guia/es/**

## Inicio rápido

```bash
git clone https://github.com/inematds/podcast-em-shorts
cd podcast-em-shorts
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt faster-whisper
.venv/bin/python pes.py doutor
.venv/bin/python pes.py novo minha-live --video /caminho/da/live.mp4
.venv/bin/python pes.py tudo minha-live --modelo small --idioma pt
.venv/bin/python pes.py revisao minha-live      # aprueba en la página que se abra
.venv/bin/python pes.py exportar minha-live     # copia solo los aprobados
```

## Comandos

`doutor`, `novo`, `transcrever`, `corrigir`, `palavras`, `candidatos`, `escolher`, `gancho`, `layout`, `render`, `checar-quadros`, `checar-conteudo`, `revisao`, `regra`, `exportar`, `tudo`. Cada uno tiene `--help`.

Para encontrar los índices que se usan en la selección manual:

```bash
.venv/bin/python pes.py palavras minha-live --de 540 --ate 600 --busca "liberdade"
.venv/bin/python pes.py escolher minha-live manual --ajustar s1=1239:1255
```

`palavras <ep> [--de <segundos>] [--ate <segundos>] [--busca <texto>]`
muestra frases completas que se cruzan con el intervalo (límites inclusivos). La búsqueda
ignora mayúsculas y acentos, y se combina con los filtros de tiempo; todos son opcionales.
Cada línea muestra el índice inicial, el tiempo inicial y el índice final:
`[1239] 09:27.7  A IA constrói um paraíso material.[1246]`.
Los índices comienzan en cero y los extremos de `--ajustar` son inclusivos.
`candidatos` también muestra `ini` y `fim` en una tabla fácil de leer.

`tudo` imprime el comando de revisión con el mismo intérprete en ejecución
(incluido el de la venv), con `pes.py` relativo cuando se ejecuta desde la raíz del kit.
`revisao` imprime la dirección y el consejo para acceder desde el celular: ejecútalo con
`--host 0.0.0.0` y usa la IP de esta computadora en la misma red, manteniendo el puerto que se muestra.

- **El kit no publica nada.** Genera, revisa y organiza; tú apruebas.
- Marca (colores, fuente, subtítulos, duración, cantidad) en `marca/marca.json`.
- Reglas del kit en `regras/REGRAS.md`; las tuyas, a partir de R200, en `regras/MINHAS-REGRAS.md`.
- Skill para Claude Code / Codex en `skill/podcast-em-shorts/`.
- Ejemplos reales en `exemplos/` (3 shorts de un live de 57 min).
- Pruebas: `python3 -m unittest discover -s tests -v`.

Detalles técnicos: [docs/SPEC.md](docs/SPEC.md) y [docs/IMPLEMENTACAO.md](docs/IMPLEMENTACAO.md).

Fuente Montserrat bajo la SIL Open Font License (`marca/fontes/OFL.txt`). Detector de rostros YuNet (OpenCV Zoo), descargado en la primera ejecución.

---

Hecho por [INEMA.CLUB](https://inema.club) — IA en la práctica, gratis.