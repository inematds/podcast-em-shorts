"""Testes visuais congelados (rodada 3). NÃO editar para fazer passar."""
import json
import os
import subprocess
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from test_pes import PES, VIDEO, SEGS, nova_raiz, run  # noqa: E402


def quadro(mp4, t):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", mp4, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.uint8).reshape(1920, 1080)


def frac_linhas_pretas(img, y0, y1, limite=10):
    medias = img[y0:y1].mean(axis=1)
    return float((medias < limite).mean())


class TVisual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = nova_raiz()
        run("novo", "v", "--video", VIDEO, raiz=cls.raiz, check=0)
        run("transcrever", "v", "--de-json", SEGS, raiz=cls.raiz, check=0)
        run("layout", "v", raiz=cls.raiz, check=0)
        c = json.loads(run("candidatos", "v", "--top", "1", "--json", raiz=cls.raiz, check=0).stdout)[0]
        run("escolher", "v", c["id"], "--titulo", "s1=Seu glossário de IA", raiz=cls.raiz, check=0)
        run("render", "v", "s1", raiz=cls.raiz, check=0)
        d = os.path.join(cls.raiz, "episodios", "v", "clips")
        cls.mp4 = os.path.join(d, "s1.mp4")
        cls.leg = json.load(open(os.path.join(d, "s1.legendas.json")))
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cls.mp4],
                                   capture_output=True, text=True, check=True).stdout)
        cls.tempos = [round(dur * f, 2) for f in (0.05, 0.3, 0.6, 0.9)]

    def test_webcam_preenche_metade_de_cima(self):
        for t in self.tempos:
            img = quadro(self.mp4, t)
            self.assertLess(frac_linhas_pretas(img, 0, 960), 0.08, f"faixa preta na metade de cima em t={t}")

    def test_rosto_grande_e_inteiro_em_cima(self):
        x, y, w, h = self.leg["rosto_esperado"]
        self.assertGreaterEqual(h, 300, "rosto ampliado de verdade (>= 300 px de altura)")
        self.assertGreaterEqual(y - 0.25 * h, 0, "testa/cabelo dentro do quadro")
        self.assertLessEqual(y + h, 960, "rosto na metade de cima")

    def test_tela_preenche_metade_de_baixo(self):
        for t in self.tempos:
            img = quadro(self.mp4, t)
            self.assertLess(frac_linhas_pretas(img, 960 + 160, 1920, limite=4), 0.20,
                            f"tela pequena demais / faixas vazias embaixo em t={t}")

    def test_titulo_grande(self):
        x, y, w, h = self.leg["titulo"]["caixa"]
        self.assertGreaterEqual(h, 80, "título com letra grande")
        self.assertGreaterEqual(self.leg["titulo"]["e"] - self.leg["titulo"]["s"], 2.5)

    def test_legenda_tamanho(self):
        for b in self.leg["blocos"]:
            self.assertGreaterEqual(b["caixa"][3], 70, f"legenda pequena: {b}")

    def test_checagem_passa(self):
        p = run("checar-quadros", self.mp4, "--legendas",
                os.path.join(self.raiz, "episodios", "v", "clips", "s1.legendas.json"))
        self.assertEqual(p.returncode, 0, p.stdout)


if __name__ == "__main__":
    unittest.main()
