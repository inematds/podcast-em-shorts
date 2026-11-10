#!/usr/bin/env python3
"""Entrada única do kit local de cortes verticais."""
import argparse
import importlib
import sys
from pathlib import Path


def parser():
    p = argparse.ArgumentParser(description='Um episódio local em shorts para revisão humana.')
    p.add_argument('--raiz', default=str(Path(__file__).resolve().parent))
    subs = p.add_subparsers(dest='comando', required=True)
    modulos = {'checar-quadros': 'quadros', 'checar-conteudo': 'conteudo', 'regra': 'regras'}
    for nome in ('novo', 'transcrever', 'corrigir', 'palavras', 'candidatos', 'escolher', 'gancho', 'layout',
                 'render', 'checar-quadros', 'checar-conteudo', 'revisao', 'regra',
                 'exportar', 'doutor', 'tudo'):
        s = subs.add_parser(nome)
        s.add_argument('--raiz', default=argparse.SUPPRESS)
        s.set_defaults(modulo=modulos.get(nome, nome))
        if nome not in ('gancho', 'checar-quadros', 'regra', 'doutor'):
            s.add_argument('ep')
        if nome in ('transcrever', 'tudo'):
            s.add_argument('--de-json')
            s.add_argument('--modelo', default='large-v3')
            s.add_argument('--idioma', default='pt')
        if nome == 'corrigir':
            s.add_argument('--trocar', action='append', required=True)
            s.add_argument('--de', type=int)
            s.add_argument('--ate', type=int)
        if nome == 'novo':
            s.add_argument('--video', required=True)
            s.add_argument('--forcar', action='store_true')
        if nome == 'candidatos':
            s.add_argument('--top', type=int, default=12)
        if nome == 'palavras':
            s.add_argument('--de', type=float, help='Início do intervalo em segundos')
            s.add_argument('--ate', type=float, help='Fim do intervalo em segundos')
            s.add_argument('--busca', help='Texto da frase, sem distinguir maiúsculas ou acentos')
        if nome == 'escolher':
            s.add_argument('ids')
            s.add_argument('--titulo', action='append', default=[])
            s.add_argument('--ajustar', action='append', default=[])
        if nome == 'gancho':
            s.add_argument('--falado', required=True)
            s.add_argument('--titulo', required=True)
        if nome == 'layout':
            s.add_argument('--forcar', choices=['tela+camera', 'camera', 'tela'])
        if nome == 'render':
            s.add_argument('ids', nargs='*')
            s.add_argument('--todos', action='store_true')
        if nome == 'checar-quadros':
            s.add_argument('mp4')
            s.add_argument('--legendas')
            s.add_argument('--fps', type=float, default=2)
            s.add_argument('--salvar', metavar='ARQUIVO', help='Destino explícito do relatório JSON')
        if nome == 'checar-conteudo':
            s.add_argument('id')
        if nome == 'revisao':
            s.add_argument('--porta', type=int, default=0)
            s.add_argument('--host', default='127.0.0.1')
            s.add_argument('--so-html', action='store_true')
        if nome == 'regra':
            s.add_argument('texto', nargs='?')
            s.add_argument('--quem', choices=['quadros', 'conteudo', 'olho'], default='olho')
            s.add_argument('--por-que', default='Observação da pessoa revisora.')
            s.add_argument('--da-nota', nargs=2, metavar=('EP', 'ID'))
        if nome in ('candidatos', 'gancho', 'layout', 'checar-quadros', 'checar-conteudo'):
            s.add_argument('--json', action='store_true')
    return p


def main():
    a = parser().parse_args()
    try:
        return importlib.import_module('pes.' + a.modulo).rodar(a) or 0
    except (ValueError, OSError, KeyError, ImportError, RuntimeError) as exc:
        print('ERRO:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
