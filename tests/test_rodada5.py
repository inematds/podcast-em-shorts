"""Testes congelados (rodada 5): mão perto do rosto não é rosto. NÃO editar."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_pes import FIX, run  # noqa: E402

MAO = os.path.join(FIX, "mao7.mp4")
MAO_LEG = os.path.join(FIX, "mao7.legendas.json")


class TMao(unittest.TestCase):
    def test_mao_apontando_nao_reprova(self):
        # Caso real: o apresentador aponta para o próprio rosto; a legenda está abaixo do rosto.
        p = run("checar-quadros", MAO, "--legendas", MAO_LEG, "--json")
        r = json.loads(p.stdout)
        self.assertTrue(r["itens"]["rosto_legenda"]["ok"], r["itens"]["rosto_legenda"])
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_legenda_no_rosto_de_verdade_ainda_reprova(self):
        leg = json.load(open(MAO_LEG))
        rosto = leg["rosto_esperado"]
        leg["blocos"] = [dict(b, caixa=list(rosto)) for b in leg["blocos"]]
        f = os.path.join(tempfile.mkdtemp(), "ruim.json")
        json.dump(leg, open(f, "w"))
        p = run("checar-quadros", MAO, "--legendas", f, "--json")
        self.assertEqual(p.returncode, 1)
        self.assertFalse(json.loads(p.stdout)["itens"]["rosto_legenda"]["ok"])

    def test_legenda_logo_abaixo_do_queixo_reprova(self):
        # 10 px abaixo do queixo ainda é "encostar" (margem de 4% da altura).
        leg = json.load(open(MAO_LEG))
        x, y, w, h = leg["rosto_esperado"]
        leg["blocos"] = [dict(b, caixa=[x, y + h + 10, w, 100]) for b in leg["blocos"]]
        f = os.path.join(tempfile.mkdtemp(), "colado.json")
        json.dump(leg, open(f, "w"))
        p = run("checar-quadros", MAO, "--legendas", f, "--json")
        self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main()
