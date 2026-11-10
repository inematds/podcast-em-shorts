"""Revisão humana local, arquivos com Range e decisões persistentes."""
import html
import json
import mimetypes
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from .util import episodio, clips, ler, salvar, marca


def pagina(a, estatico=False):
    pasta, m = episodio(a), marca(a)
    estado = ler(pasta / 'revisao.json') if (pasta / 'revisao.json').exists() else {}
    candidatos = {c['id']: c for c in ler(pasta / 'work/candidatos.json')}
    secoes = []
    esc = html.escape
    for c in clips(a):
        identificador = c['id']
        testes = []
        for tipo, caminho in [('quadros', pasta / 'clips' / (identificador + '.quadros.json')),
                              ('conteúdo', pasta / 'work' / (identificador + '.conteudo.json'))]:
            if caminho.exists():
                r = ler(caminho)
                resultado = 'OK' if r['ok'] else 'Reprovado'
                testes.append(f'<li>{tipo}: <strong>{resultado}</strong><details><summary>Ver resultados</summary>'
                              f'<pre>{esc(json.dumps(r["itens"], ensure_ascii=False, indent=2))}</pre></details></li>')
            else:
                testes.append(f'<li>{tipo}: ainda não verificado</li>')
        nota = candidatos.get(c['de'], {}).get('nota', 'não disponível')
        st = estado.get(identificador, {})
        notas = ''.join('<li>' + esc(n['texto']) + '</li>' for n in st.get('notas', []))
        video = ('clips/' if estatico else '/video/') + identificador + '.mp4'
        desabilitado = 'disabled' if estatico else ''
        secoes.append(f'''<article id="{identificador}"><video controls preload="metadata" playsinline src="{video}" aria-label="Vídeo {identificador}"></video>
<div class="decisao"><h2>{esc(c['titulo'])}</h2><p>{identificador} · {c['e']-c['s']:.1f} s · Nota do candidato: {nota}</p>
<ul class="checagens">{''.join(testes)}</ul><p class="status" role="status">{esc(st.get('status', 'Aguardando revisão'))}</p>
<label for="nota-{identificador}">O que ficou bom ou precisa mudar?</label><textarea id="nota-{identificador}" rows="3" maxlength="4000"></textarea>
<div class="acoes"><button data-acao="aprovar" {desabilitado}>Aprovar</button><button data-acao="refazer" {desabilitado}>Refazer</button></div>
<details><summary>Notas anteriores</summary><ul class="notas">{notas or '<li>Sem notas.</li>'}</ul></details></div></article>''')
    css = '''*{box-sizing:border-box}body{margin:0;background:var(--fundo);color:var(--texto);font-family:var(--fonte),sans-serif;line-height:1.6}
main{max-width:1080px;margin:auto;padding:40px 24px}h1{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.15}h2{font-size:1.5rem;line-height:1.3}
article{display:grid;grid-template-columns:minmax(220px,340px) minmax(0,1fr);gap:40px;padding:40px 0;border-top:1px solid var(--texto)}
video{width:100%;max-height:74vh;background:var(--contorno)}p{max-width:65ch}.decisao{min-width:0}.checagens{padding-left:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem}
label{display:block;margin-top:24px}textarea{display:block;width:100%;padding:12px;background:var(--fundo);color:var(--texto);border:1px solid var(--texto);font:inherit}
.acoes{display:flex;gap:12px;margin:16px 0 24px}button{padding:12px 24px;min-height:48px;font:inherit;cursor:pointer;border:1px solid var(--texto);color:var(--texto);background:var(--fundo)}
button[data-acao=aprovar]{background:var(--destaque);color:var(--contorno);border-color:var(--destaque)}button:hover{filter:brightness(.85)}button:disabled{opacity:.5;cursor:wait}
:focus-visible{outline:3px solid var(--destaque);outline-offset:4px}.status{color:var(--destaque)}summary{cursor:pointer}details{margin-top:12px}
@media(max-width:640px){main{padding:24px 16px}article{grid-template-columns:1fr;gap:16px}video{max-height:65vh}.acoes button{flex:1;padding:12px}}'''
    cores = ';'.join('--' + k + ':' + v for k, v in m['cores'].items())
    css = ':root{' + cores + ';--fonte:RevisaoMarca}' + css
    fonte_url = 'revisao-fonte.ttf' if estatico else '/fonte.ttf'
    css += f"@font-face{{font-family:RevisaoMarca;src:url('{fonte_url}');font-display:swap}}"
    js = '''document.querySelectorAll('button[data-acao]').forEach(b=>b.onclick=async()=>{
const art=b.closest('article'),status=art.querySelector('.status'),bs=art.querySelectorAll('button');
bs.forEach(x=>x.disabled=true);status.textContent='Salvando decisão…';
try{const r=await fetch('/api/acao',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:art.id,acao:b.dataset.acao,nota:art.querySelector('textarea').value})});
if(!r.ok)throw Error(await r.text());const dados=await r.json();status.textContent=dados[art.id].status;
const lista=art.querySelector('.notas');lista.replaceChildren();dados[art.id].notas.forEach(n=>{const li=document.createElement('li');li.textContent=n.texto;lista.append(li)});art.querySelector('textarea').value='';
}catch(e){status.textContent='Não foi possível salvar. Tente novamente: '+e.message}finally{bs.forEach(x=>x.disabled=false)}});'''
    aviso = 'Visualização estática: abra o servidor de revisão para registrar decisões.' if estatico else 'Assista e ouça o corte inteiro antes de decidir. As checagens não substituem sua revisão.'
    return f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisão · {esc(a.ep)}</title><style>{css}</style><main><h1>Revisão de {esc(a.ep)}</h1><p>{aviso}</p>
{''.join(secoes) or '<p>Nenhum corte escolhido. Use escolher e render antes de revisar.</p>'}</main><script>{'' if estatico else js}</script></html>'''


def rodar(a):
    pasta = episodio(a)
    lista = {c['id'] for c in clips(a)}
    if any(not re.fullmatch(r'[a-zA-Z0-9-]+', c) for c in lista):
        raise ValueError('Identificador de clip inválido.')
    if a.so_html:
        import shutil
        from .util import raiz
        shutil.copy2(raiz(a) / marca(a)['fonte'], pasta / 'revisao-fonte.ttf')
        (pasta / 'revisao.html').write_text(pagina(a, True), encoding='utf-8')
        print('Página gravada:', pasta / 'revisao.html')
        return 0
    trava = threading.Lock()
    class Servidor(ThreadingHTTPServer):
        daemon_threads = True
    class Pedido(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def responder(self, status, dados, tipo='application/json; charset=utf-8'):
            dados = dados.encode('utf-8') if isinstance(dados, str) else dados
            self.send_response(status)
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(dados)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            url = urlsplit(self.path).path
            if url == '/':
                return self.responder(200, pagina(a), 'text/html; charset=utf-8')
            if url == '/api/estado':
                return self.responder(200, json.dumps(ler(pasta / 'revisao.json'), ensure_ascii=False))
            if url == '/fonte.ttf':
                from .util import raiz
                return self.responder(200, (raiz(a) / marca(a)['fonte']).read_bytes(), 'font/ttf')
            nome = url.removeprefix('/video/').removesuffix('.mp4')
            if url != '/video/' + nome + '.mp4' or nome not in lista:
                return self.responder(404, 'Arquivo não encontrado.', 'text/plain; charset=utf-8')
            caminho = pasta / 'clips' / (nome + '.mp4')
            if not caminho.exists():
                return self.responder(404, 'Vídeo ainda não renderizado.', 'text/plain; charset=utf-8')
            total = caminho.stat().st_size
            inicio, fim, status = 0, total - 1, 200
            pedido_range = self.headers.get('Range')
            if pedido_range:
                m = re.fullmatch(r'bytes=(\d*)-(\d*)', pedido_range)
                if not m or not any(m.groups()):
                    return self.invalido_range(total)
                if m[1]:
                    inicio = int(m[1]); fim = min(total-1, int(m[2])) if m[2] else total-1
                else:
                    inicio = max(0, total - int(m[2]))
                if inicio > fim or inicio >= total:
                    return self.invalido_range(total)
                status = 206
            self.send_response(status)
            self.send_header('Content-Type', mimetypes.guess_type(str(caminho))[0] or 'video/mp4')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', str(fim - inicio + 1))
            if status == 206:
                self.send_header('Content-Range', f'bytes {inicio}-{fim}/{total}')
            self.end_headers()
            try:
                with caminho.open('rb') as f:
                    f.seek(inicio)
                    falta = fim - inicio + 1
                    while falta:
                        dados = f.read(min(falta, 65536))
                        if not dados:
                            break
                        self.wfile.write(dados)
                        falta -= len(dados)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def invalido_range(self, total):
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{total}')
            self.send_header('Content-Length', '0')
            self.end_headers()

        def do_POST(self):
            if self.path != '/api/acao':
                return self.responder(404, '{}')
            origem = self.headers.get('Origin')
            if origem and origem != 'http://' + self.headers.get('Host', ''):
                return self.responder(403, 'Origem não permitida.')
            try:
                tamanho = int(self.headers.get('Content-Length', 0))
                if not 0 < tamanho <= 16384:
                    raise ValueError('Corpo ausente ou grande demais.')
                dados = json.loads(self.rfile.read(tamanho))
                identificador, acao, nota = dados['id'], dados['acao'], dados.get('nota', '')
                if identificador not in lista or acao not in ('aprovar', 'refazer'):
                    raise ValueError('Clip ou ação inválidos.')
                if not isinstance(nota, str) or len(nota) > 4000:
                    raise ValueError('Nota inválida.')
                with trava:
                    caminho = pasta / 'revisao.json'
                    estado = ler(caminho) if caminho.exists() else {}
                    item = estado.setdefault(identificador, {'notas': []})
                    item['status'] = 'aprovado' if acao == 'aprovar' else 'refazer'
                    if nota.strip():
                        item['notas'].append({'texto': nota.strip(), 'quando': datetime.now(timezone.utc).isoformat()})
                    salvar(caminho, estado)
                self.responder(200, json.dumps(estado, ensure_ascii=False))
            except (ValueError, KeyError, TypeError) as exc:
                self.responder(400, str(exc), 'text/plain; charset=utf-8')
    with Servidor((a.host, a.porta), Pedido) as servidor:
        print(f'REVISAO http://{a.host}:{servidor.server_port}/', flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0
