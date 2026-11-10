"""Testes congelados (rodada 6): cabeça encostada no topo da webcam. NÃO editar."""
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_pes import FIX, nova_raiz, run  # noqa: E402

VIDEO = os.path.join(FIX, "cabeca24.mp4")
SEGS = os.path.join(FIX, "cabeca24-segmentos.json")


class TCabecaNoTopo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = nova_raiz()
        run("novo", "c", "--video", VIDEO, raiz=cls.raiz, check=0)
        run("transcrever", "c", "--de-json", SEGS, raiz=cls.raiz, check=0)
        lay = json.loads(run("layout", "c", "--json", raiz=cls.raiz, check=0).stdout)
        cls.cam = lay["camera"]
        pal = json.load(open(os.path.join(cls.raiz, "episodios", "c", "work", "palavras.json")))
        ini = next(i for i in range(1, len(pal)) if re.search(r"[.?!]$", pal[i - 1]["w"]) and pal[i]["w"][0].isupper())
        fim = max(i for i in range(len(pal)) if re.search(r"[.?!]$", pal[i]["w"]))
        run("escolher", "c", "manual", "--ajustar", f"s1={ini}:{fim}", "--titulo", "s1=Pedido claro", raiz=cls.raiz, check=0)
        run("render", "c", "s1", raiz=cls.raiz, check=0)
        d = os.path.join(cls.raiz, "episodios", "c", "clips")
        cls.mp4 = os.path.join(d, "s1.mp4")
        cls.legp = os.path.join(d, "s1.legendas.json")
        cls.leg = json.load(open(cls.legp))

    def test_layout_tela_camera(self):
        self.assertIsNotNone(self.cam)

    def test_recorte_nunca_sai_da_webcam(self):
        rec = self.leg.get("recortes_camera")
        self.assertTrue(rec, "render deve registrar os recortes da webcam usados (recortes_camera)")
        cx, cy, cw, ch = self.cam
        for r in rec:
            x, y, w, h = r["caixa"]
            self.assertGreaterEqual(x, cx - 1, r)
            self.assertGreaterEqual(y, cy - 1, r)
            self.assertLessEqual(x + w, cx + cw + 1, r)
            self.assertLessEqual(y + h, cy + ch + 1, r)
            self.assertGreater(w, 50)
            self.assertGreater(h, 50)

    def test_checagens(self):
        p = run("checar-quadros", self.mp4, "--legendas", self.legp)
        self.assertEqual(p.returncode, 0, p.stdout)


if __name__ == "__main__":
    unittest.main()
