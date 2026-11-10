"""Testes congelados (rodada 4): transcrição real imperfeita e escolha de trechos. NÃO editar."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_pes import VIDEO, nova_raiz, palavras_sinteticas, run  # noqa: E402


def ep_sintetico(raiz, nome, frases):
    ep = os.path.join(raiz, "episodios", nome)
    os.makedirs(os.path.join(ep, "work"))
    os.makedirs(os.path.join(ep, "raw"))
    json.dump({"ep": nome, "video": "raw/video.mp4", "duracao": 900, "largura": 1920, "altura": 1080, "fps": 30},
              open(os.path.join(ep, "ep.json"), "w"))
    pal = palavras_sinteticas(frases)
    json.dump(pal, open(os.path.join(ep, "work", "palavras.json"), "w"))
    return pal


class TTranscricaoReal(unittest.TestCase):
    def test_palavra_com_duracao_zero(self):
        raiz = nova_raiz()
        run("novo", "z", "--video", VIDEO, raiz=raiz, check=0)
        segs = [{"start": 0.0, "end": 3.0, "text": "Olá a todos, um teste aqui.",
                 "words": [{"word": "Olá", "start": 0.0, "end": 0.4}, {"word": "a", "start": 0.4, "end": 0.5},
                           {"word": "todos,", "start": 0.5, "end": 0.9}, {"word": "um", "start": 1.0, "end": 1.0},
                           {"word": "teste", "start": 1.0, "end": 1.4}, {"word": "aqui.", "start": 1.38, "end": 1.8}]}]
        f = os.path.join(tempfile.mkdtemp(), "segs.json")
        json.dump(segs, open(f, "w"))
        p = run("transcrever", "z", "--de-json", f, raiz=raiz, check=0)
        self.assertRegex(p.stdout, r"corrigid")
        pal = json.load(open(os.path.join(raiz, "episodios", "z", "work", "palavras.json")))
        self.assertEqual(len(pal), 6)
        for k, w in enumerate(pal):
            self.assertLess(w["s"], w["e"])
            if k:
                self.assertGreaterEqual(w["s"], pal[k - 1]["s"])

    def test_arquivo_quebrado_recusa(self):
        raiz = nova_raiz()
        run("novo", "q", "--video", VIDEO, raiz=raiz, check=0)
        f = os.path.join(tempfile.mkdtemp(), "vazio.json")
        json.dump([{"start": 0, "end": 1, "text": "", "words": []}], open(f, "w"))
        p = run("transcrever", "q", "--de-json", f, raiz=raiz)
        self.assertNotEqual(p.returncode, 0)


class TEscolha(unittest.TestCase):
    def setUp(self):
        self.raiz = nova_raiz()

    def test_comeca_no_meio_da_frase(self):
        # Whisper às vezes não pontua: frase anterior sem ponto, próxima começa minúscula.
        frases = ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 3 + [
            "e aí ficou tudo meio solto sem ponto nenhum aqui",
            "mas ou seja você perde doze horas por semana copiando pedidos à mão.",
            "Na verdade o problema é que ninguém mede esse tempo.",
            "Por exemplo, uma loja com três pessoas joga fora cinquenta horas por mês.",
            "Ou seja, meça antes de automatizar.",
        ] + ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 3
        ep_sintetico(self.raiz, "m", frases)
        cands = json.loads(run("candidatos", "m", "--top", "8", "--json", raiz=self.raiz, check=0).stdout)
        for c in cands:
            primeira = c["texto"].split()[0]
            if primeira[0].islower():
                self.assertIn("inicio_meio", c["alertas"], c)

    def test_depende_da_tela(self):
        frases = ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 2 + [
            "Ó, vocês estão vendo aqui essa imagem aqui, deixa eu ver.",
            "Olha isso aqui na tela, vamos dar uma olhada nessa parte aqui embaixo.",
            "Então clica aqui e depois aqui, e aqui aparece isso aqui.",
            "Deixa eu abrir de novo, ó, tá aqui, essa aqui é a outra coisa.",
        ] + ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 2
        ep_sintetico(self.raiz, "t", frases)
        cands = json.loads(run("candidatos", "t", "--top", "5", "--json", raiz=self.raiz, check=0).stdout)
        alvo = [c for c in cands if "vocês estão vendo" in c["texto"] or "clica aqui" in c["texto"]]
        self.assertTrue(alvo)
        for c in alvo:
            self.assertIn("depende_tela", c["alertas"], c)

    def test_nota_separa_denso_de_vazio(self):
        vazio = ["A gente foi conversando sobre várias coisas da semana e tal."] * 7
        denso = [
            "Você sabia que noventa por cento das lojas ainda copia pedido à mão?",
            "Mas na verdade o problema não é a ferramenta.",
            "O problema é que ninguém mede as doze horas perdidas por semana.",
            "Por exemplo, três pessoas jogam fora cinquenta horas por mês.",
            "Ou seja, meça antes de automatizar.",
        ]
        ep_sintetico(self.raiz, "d", vazio + ["Hoje tem uma conversa bem tranquila com todo mundo aqui."] + denso + vazio)
        cands = json.loads(run("candidatos", "d", "--top", "6", "--json", raiz=self.raiz, check=0).stdout)
        notas = sorted((c["nota"] for c in cands), reverse=True)
        self.assertIn("noventa", cands[0]["texto"])
        vazios = [c for c in cands if "noventa" not in c["texto"] and "doze" not in c["texto"]]
        self.assertTrue(vazios, "deve haver candidatos sem o trecho denso para comparar")
        self.assertGreaterEqual(cands[0]["nota"] - max(c["nota"] for c in vazios), 2.0, notas)

    def test_nome_nao_dispara_em_inicio_de_frase(self):
        frases = ["Hoje a conversa segue com outros temas da semana e alguns recados rápidos."] * 8
        ep_sintetico(self.raiz, "n", frases)
        cands = json.loads(run("candidatos", "n", "--top", "3", "--json", raiz=self.raiz, check=0).stdout)
        for c in cands:
            self.assertNotIn("nome", c["sinais"])


if __name__ == "__main__":
    unittest.main()
