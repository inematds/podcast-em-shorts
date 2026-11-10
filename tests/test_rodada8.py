"""Testes congelados (rodada 8): área segura do topo e transcrição sem PyAV. NÃO editar."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_pes import REPO, SEGS, VIDEO, nova_raiz, run  # noqa: E402


class TAreaSegura(unittest.TestCase):
    def test_marca_topo_10_por_cento(self):
        m = json.load(open(os.path.join(REPO, "marca", "marca.json")))
        self.assertGreaterEqual(m["area_segura"]["topo"], 0.10)
        self.assertGreaterEqual(m["area_segura"]["base"], 0.20)

    def test_titulo_fora_da_faixa_do_app(self):
        raiz = nova_raiz()
        run("novo", "a", "--video", VIDEO, raiz=raiz, check=0)
        run("transcrever", "a", "--de-json", SEGS, raiz=raiz, check=0)
        c = json.loads(run("candidatos", "a", "--top", "1", "--json", raiz=raiz, check=0).stdout)[0]
        run("escolher", "a", c["id"], "--titulo", "s1=Seu glossário de IA para usar hoje", raiz=raiz, check=0)
        run("render", "a", "s1", raiz=raiz, check=0)
        d = os.path.join(raiz, "episodios", "a", "clips")
        leg = json.load(open(os.path.join(d, "s1.legendas.json")))
        x, y, w, h = leg["titulo"]["caixa"]
        self.assertGreaterEqual(y, 192, "título começa abaixo dos 10% do topo")
        self.assertGreaterEqual(h, 80)
        rx, ry, rw, rh = leg["rosto_esperado"]
        self.assertLessEqual(y + h, ry - 0.25 * rh + 1, "título acima da testa/cabelo")
        p = run("checar-quadros", os.path.join(d, "s1.mp4"), "--legendas", os.path.join(d, "s1.legendas.json"))
        self.assertEqual(p.returncode, 0, p.stdout)


class TSemPyAV(unittest.TestCase):
    def test_transcrever_nao_depende_de_pyav(self):
        src = open(os.path.join(REPO, "pes", "transcrever.py"), encoding="utf-8").read()
        self.assertNotIn("import av", src)
        self.assertRegex(src, r"ffmpeg", "áudio extraído com ffmpeg antes do Whisper")


if __name__ == "__main__":
    unittest.main()
