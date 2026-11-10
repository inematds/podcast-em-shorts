"""Testes congelados do podcast-em-shorts. NÃO editar para fazer passar: conserte o código.

Rodar: python3 -m unittest discover -s tests -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PES = os.path.join(REPO, "pes.py")
FIX = os.path.join(REPO, "tests", "fixtures")
VIDEO = os.path.join(FIX, "live30.mp4")
SEGS = os.path.join(FIX, "live30-segmentos.json")


def run(*args, raiz=None, check=None, timeout=900):
    cmd = [sys.executable, PES, *args]
    if raiz:
        cmd += ["--raiz", raiz]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if check is not None and p.returncode != check:
        raise AssertionError(f"{cmd} saiu {p.returncode} (esperado {check})\nOUT:{p.stdout[-3000:]}\nERR:{p.stderr[-3000:]}")
    return p


def nova_raiz():
    d = tempfile.mkdtemp(prefix="pes-teste-")
    shutil.copytree(os.path.join(REPO, "marca"), os.path.join(d, "marca"))
    os.makedirs(os.path.join(d, "regras"))
    for f in ("REGRAS.md", "MINHAS-REGRAS.md"):
        shutil.copy(os.path.join(REPO, "regras", f), os.path.join(d, "regras", f))
    return d


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def palavras_sinteticas(frases, passo=0.32, pausa=0.9):
    """Lista de palavras com tempos a partir de frases (cada frase = string)."""
    out, t, i = [], 0.5, 0
    for f in frases:
        for w in f.split():
            out.append({"i": i, "w": w, "s": round(t, 3), "e": round(t + passo - 0.04, 3)})
            t += passo
            i += 1
        t += pausa
    return out


def caixas_cruzam(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


class T00Doutor(unittest.TestCase):
    def test_doutor(self):
        p = run("doutor", check=0)
        self.assertIn("ffmpeg", p.stdout.lower())


class T01Fluxo(unittest.TestCase):
    """Fluxo real na live de 30 s: novo → transcrever → candidatos → escolher → layout → render → checagens."""

    @classmethod
    def setUpClass(cls):
        cls.raiz = nova_raiz()
        cls.ep = "live30"
        run("novo", cls.ep, "--video", VIDEO, raiz=cls.raiz, check=0)
        run("transcrever", cls.ep, "--de-json", SEGS, raiz=cls.raiz, check=0)
        cls.epdir = os.path.join(cls.raiz, "episodios", cls.ep)

    def test_a_novo_recusa_repetido(self):
        p = run("novo", self.ep, "--video", VIDEO, raiz=self.raiz)
        self.assertEqual(p.returncode, 1)
        ep = json.load(open(os.path.join(self.epdir, "ep.json")))
        self.assertEqual((ep["largura"], ep["altura"]), (1920, 1080))
        self.assertAlmostEqual(ep["duracao"], 30, delta=1.0)

    def test_b_palavras(self):
        pal = json.load(open(os.path.join(self.epdir, "work", "palavras.json")))
        segs = json.load(open(SEGS))
        n = sum(len(s["words"]) for s in segs)
        self.assertEqual(len(pal), n)
        for k, w in enumerate(pal):
            self.assertEqual(w["i"], k)
            self.assertLess(w["s"], w["e"])
            if k:
                self.assertGreaterEqual(w["s"], pal[k - 1]["s"])

    def test_c_candidatos(self):
        p = run("candidatos", self.ep, "--top", "5", "--json", raiz=self.raiz, check=0)
        cands = json.loads(p.stdout)
        self.assertGreaterEqual(len(cands), 1)
        pal = json.load(open(os.path.join(self.epdir, "work", "palavras.json")))
        notas = [c["nota"] for c in cands]
        self.assertEqual(notas, sorted(notas, reverse=True))
        for c in cands:
            self.assertGreaterEqual(c["duracao"], 20 - 0.01)
            self.assertLessEqual(c["duracao"], 59 + 0.01)
            self.assertAlmostEqual(c["s"], pal[c["ini"]]["s"], delta=0.01)
            self.assertAlmostEqual(c["e"], pal[c["fim"]]["e"], delta=0.01)
            texto = " ".join(w["w"] for w in pal[c["ini"]:c["fim"] + 1])
            self.assertEqual(re.sub(r"\s+", " ", c["texto"]).strip(), texto.strip())
            self.assertTrue(re.search(r"[.?!]$", pal[c["fim"]]["w"]), "trecho deve terminar em fim de frase")
        self.assertTrue(os.path.exists(os.path.join(self.epdir, "work", "candidatos.json")))

    def test_d_layout_tela_camera(self):
        p = run("layout", self.ep, "--json", raiz=self.raiz, check=0)
        lay = json.loads(p.stdout)
        self.assertEqual(lay["modo"], "tela+camera")
        x, y, w, h = lay["camera"]
        self.assertGreater(x + w / 2, 1920 * 0.6, "webcam fica à direita")
        self.assertGreater(y + h / 2, 1080 * 0.5, "webcam fica embaixo")
        self.assertGreaterEqual(lay["amostras"], 24)

    def test_e_render_e_checagens(self):
        run("layout", self.ep, raiz=self.raiz, check=0)
        cands = json.loads(run("candidatos", self.ep, "--top", "3", "--json", raiz=self.raiz, check=0).stdout)
        run("escolher", self.ep, cands[0]["id"], "--titulo", "s1=Teste do kit", raiz=self.raiz, check=0)
        clips = json.load(open(os.path.join(self.epdir, "clips.json")))["clips"]
        self.assertEqual(clips[0]["id"], "s1")
        self.assertEqual(clips[0]["titulo"], "Teste do kit")
        run("render", self.ep, "s1", raiz=self.raiz, check=0)
        mp4 = os.path.join(self.epdir, "clips", "s1.mp4")
        info = probe(mp4)
        v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
        self.assertEqual((v["width"], v["height"]), (1080, 1920))
        self.assertTrue(any(s["codec_type"] == "audio" for s in info["streams"]))
        self.assertAlmostEqual(float(info["format"]["duration"]), clips[0]["e"] - clips[0]["s"], delta=0.2)
        leg = json.load(open(os.path.join(self.epdir, "clips", "s1.legendas.json")))
        self.assertEqual(leg["layout"], "tela+camera")
        self.assertGreater(len(leg["blocos"]), 5)
        for b in leg["blocos"]:
            self.assertLessEqual(len(b["texto"]), 22 + 2)
            self.assertLessEqual(len(b["texto"].split()), 3)
            if leg["rosto_esperado"]:
                self.assertFalse(caixas_cruzam(b["caixa"], leg["rosto_esperado"]), f"legenda sobre o rosto: {b}")
        p = run("checar-quadros", mp4, "--legendas", os.path.join(self.epdir, "clips", "s1.legendas.json"))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("QUADROS OK", p.stdout)
        p = run("checar-conteudo", self.ep, "s1", raiz=self.raiz)
        self.assertIn(p.returncode, (0, 1))
        self.assertTrue(re.search(r"CONTEUDO (OK|FALHOU)", p.stdout))

        # legenda colocada de propósito em cima do rosto → tem que reprovar
        rosto = leg["rosto_esperado"]
        self.assertIsNotNone(rosto)
        ruim = dict(leg)
        ruim["blocos"] = [{"s": b["s"], "e": b["e"], "texto": b["texto"], "caixa": list(rosto)} for b in leg["blocos"]]
        ruim_path = os.path.join(self.epdir, "clips", "ruim.legendas.json")
        json.dump(ruim, open(ruim_path, "w"))
        p = run("checar-quadros", mp4, "--legendas", ruim_path, "--json")
        self.assertEqual(p.returncode, 1)
        res = json.loads(p.stdout)
        self.assertFalse(res["ok"])
        self.assertFalse(res["itens"]["rosto_legenda"]["ok"])

    def test_f_revisao_e_exportar(self):
        if not os.path.exists(os.path.join(self.epdir, "clips", "s1.mp4")):
            self.test_e_render_e_checagens()
        p = run("exportar", self.ep, raiz=self.raiz)
        self.assertEqual(p.returncode, 1)
        self.assertIn("NADA APROVADO", p.stdout)
        proc = subprocess.Popen([sys.executable, PES, "revisao", self.ep, "--porta", "0", "--raiz", self.raiz],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            linha = proc.stdout.readline()
            m = re.search(r"REVISAO (http://\S+)", linha)
            self.assertTrue(m, linha)
            base = m.group(1).rstrip("/")
            html = urllib.request.urlopen(base + "/", timeout=10).read().decode()
            self.assertIn("s1", html)
            r = urllib.request.Request(base + "/video/s1.mp4", headers={"Range": "bytes=0-99"})
            resp = urllib.request.urlopen(r, timeout=10)
            self.assertEqual(resp.status, 206)
            self.assertEqual(len(resp.read()), 100)
            body = json.dumps({"id": "s1", "acao": "aprovar", "nota": "ficou bom"}).encode()
            r = urllib.request.Request(base + "/api/acao", data=body, method="POST",
                                       headers={"Content-Type": "application/json"})
            urllib.request.urlopen(r, timeout=10).read()
            est = json.load(open(os.path.join(self.epdir, "revisao.json")))
            self.assertEqual(est["s1"]["status"], "aprovado")
            self.assertEqual(est["s1"]["notas"][-1]["texto"], "ficou bom")
        finally:
            proc.terminate()
            proc.wait(timeout=10)
        run("exportar", self.ep, raiz=self.raiz, check=0)
        self.assertTrue(os.path.exists(os.path.join(self.epdir, "aprovados", "s1.mp4")))
        self.assertTrue(os.path.exists(os.path.join(self.epdir, "aprovados", "s1.txt")))
        run("revisao", self.ep, "--so-html", raiz=self.raiz, check=0)
        self.assertTrue(os.path.exists(os.path.join(self.epdir, "revisao.html")))


class T02Candidatos(unittest.TestCase):
    """Heurísticas em texto sintético (sem vídeo)."""

    def setUp(self):
        self.raiz = nova_raiz()
        ep = os.path.join(self.raiz, "episodios", "sint")
        os.makedirs(os.path.join(ep, "work"))
        os.makedirs(os.path.join(ep, "raw"))
        json.dump({"ep": "sint", "video": "raw/video.mp4", "duracao": 400, "largura": 1920, "altura": 1080, "fps": 30},
                  open(os.path.join(ep, "ep.json"), "w"))
        bom = [
            "Você sabia que noventa por cento das empresas ainda faz isso à mão?",
            "Mas na verdade o problema não é a ferramenta.",
            "O problema é que ninguém mede o tempo que perde toda semana.",
            "Por exemplo, uma loja com três funcionários gasta doze horas só copiando pedidos.",
            "Imagina isso no fim do mês, são quase cinquenta horas jogadas fora.",
            "Ou seja, a primeira coisa é medir antes de automatizar.",
        ]
        ruim = [
            "Então, como eu falei lá atrás, isso aí é aquela coisa.",
            "E aí a gente vai vendo como fica, né, e vai indo.",
            "Se inscreve no canal e deixa o like que ajuda muito.",
            "Tipo, é isso aí, vai ficando e a gente vai seguindo do jeito que dá.",
            "Comenta aí embaixo o que você achou e link na descrição.",
            "E aí depois a gente volta nisso em outro momento com mais calma.",
        ]
        enchimento = ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 4
        pal = palavras_sinteticas(enchimento + ruim + enchimento + bom + enchimento)
        json.dump(pal, open(os.path.join(ep, "work", "palavras.json"), "w"))
        self.pal = pal

    def test_melhor_trecho_e_alertas(self):
        p = run("candidatos", "sint", "--top", "6", "--json", raiz=self.raiz, check=0)
        cands = json.loads(p.stdout)
        top = cands[0]
        self.assertIn("noventa", top["texto"].lower() + " ".join(c["texto"].lower() for c in cands[:1]))
        for s in ("numero", "virada", "voce"):
            self.assertIn(s, top["sinais"])
        ruins = [c for c in cands if "inscreve" in c["texto"].lower() or "comenta aí" in c["texto"].lower()]
        for c in ruins:
            self.assertIn("chamada", c["alertas"])
            self.assertLess(c["nota"], top["nota"])
        for i, a in enumerate(cands):
            for b in cands[i + 1:]:
                inter = max(0, min(a["e"], b["e"]) - max(a["s"], b["s"]))
                self.assertLessEqual(inter, 0.5 * min(a["duracao"], b["duracao"]) + 0.01)

    def test_checar_conteudo_meio_da_frase(self):
        ep = os.path.join(self.raiz, "episodios", "sint")
        # começa na 3ª palavra de uma frase "boa" e termina sem fechamento
        i0 = next(w["i"] for w in self.pal if w["w"] == "noventa")
        i1 = next(w["i"] for w in self.pal if w["w"] == "funcionários")
        clip = {"id": "x1", "de": "manual", "ini": i0, "fim": i1, "s": self.pal[i0]["s"], "e": self.pal[i1]["e"], "titulo": "x"}
        j0 = next(w["i"] for w in self.pal if w["w"] == "Você")
        j1 = next(w["i"] for w in self.pal if w["w"] == "automatizar.")
        bom = {"id": "x2", "de": "manual", "ini": j0, "fim": j1, "s": self.pal[j0]["s"], "e": self.pal[j1]["e"], "titulo": "y"}
        json.dump({"clips": [clip, bom]}, open(os.path.join(ep, "clips.json"), "w"))
        p = run("checar-conteudo", "sint", "x1", raiz=self.raiz)
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("CONTEUDO FALHOU", p.stdout)
        p = run("checar-conteudo", "sint", "x2", raiz=self.raiz)
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("CONTEUDO OK", p.stdout)


class T03Gancho(unittest.TestCase):
    def test_bom(self):
        p = run("gancho", "--falado", "Você perde doze horas por semana copiando pedidos à mão.",
                "--titulo", "12 horas jogadas fora", "--json", check=0)
        self.assertTrue(json.loads(p.stdout)["passa"])

    def test_ruim(self):
        p = run("gancho", "--falado", "Então, né, tipo assim, é aquela coisa que a gente estava falando antes e tal",
                "--titulo", "uma coisa que eu queria falar sobre aquilo...", "--json")
        self.assertEqual(p.returncode, 1)
        r = json.loads(p.stdout)
        self.assertFalse(r["passa"])
        self.assertLess(r["falado"]["nota"], 6)
        self.assertLess(r["titulo"]["nota"], 6)


class T04QuadrosSinteticos(unittest.TestCase):
    def test_preto_silencio_e_resolucao(self):
        d = tempfile.mkdtemp()
        preto = os.path.join(d, "preto.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=4:r=30",
                        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "4", "-shortest",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", preto], check=True)
        p = run("checar-quadros", preto, "--json")
        self.assertEqual(p.returncode, 1)
        r = json.loads(p.stdout)
        self.assertFalse(r["itens"]["preto"]["ok"])
        self.assertFalse(r["itens"]["audio"]["ok"])
        deitado = os.path.join(d, "deitado.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1920x1080:d=3:r=30",
                        "-f", "lavfi", "-i", "sine=f=440:r=48000", "-t", "3", "-shortest",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", deitado], check=True)
        p = run("checar-quadros", deitado)
        self.assertEqual(p.returncode, 1)
        self.assertIn("QUADROS FALHOU", p.stdout)
        self.assertIn("resolucao", p.stdout)


class T05Regras(unittest.TestCase):
    def test_numeracao_r200(self):
        raiz = nova_raiz()
        a = run("regra", "Legenda nunca em cima do microfone", "--quem", "olho", "--por-que", "tampa a boca",
                raiz=raiz, check=0)
        b = run("regra", "Título com no máximo 5 palavras", "--quem", "conteudo", raiz=raiz, check=0)
        self.assertIn("R200", a.stdout)
        self.assertIn("R201", b.stdout)
        txt = open(os.path.join(raiz, "regras", "MINHAS-REGRAS.md")).read()
        self.assertIn("## R200 — Legenda nunca em cima do microfone", txt)
        self.assertIn("## R201 — Título com no máximo 5 palavras", txt)


class T06SemRede(unittest.TestCase):
    def test_codigo_nao_publica(self):
        proibidos = re.compile(r"buffer\.com|blotato|supabase|vercel|api\.instagram|graph\.facebook|"
                               r"youtube/v3|tiktokapis|requests\.post|api_key|apikey", re.I)
        achados = []
        for raiz, _, arqs in os.walk(os.path.join(REPO, "pes")):
            for a in arqs:
                if a.endswith(".py"):
                    t = open(os.path.join(raiz, a), encoding="utf-8").read()
                    for m in proibidos.finditer(t):
                        achados.append(f"{a}: {m.group(0)}")
        t = open(PES, encoding="utf-8").read()
        achados += [f"pes.py: {m.group(0)}" for m in proibidos.finditer(t)]
        self.assertEqual(achados, [])

    def test_marca_sem_cor_fixa_no_codigo(self):
        achados = []
        for raiz, _, arqs in os.walk(os.path.join(REPO, "pes")):
            for a in arqs:
                if a.endswith(".py"):
                    t = open(os.path.join(raiz, a), encoding="utf-8").read()
                    for m in re.finditer(r"#[0-9A-Fa-f]{6}\b", t):
                        achados.append(f"{a}: {m.group(0)}")
        self.assertEqual(achados, [], "cores só em marca/marca.json")


if __name__ == "__main__":
    unittest.main()
