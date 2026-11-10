"""Recorte de tela guiado por diferenças, sem movimento quando não há atividade."""
import cv2
import numpy as np


def analisar_tela(video, caixa, quantidade=32):
    cap = cv2.VideoCapture(str(video))
    total, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS)
    x, y, w, h = caixa
    original_h = h
    amostras = []
    try:
        for i in np.linspace(0, total - 1, min(quantidade, total), dtype=int):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
            ok, q = cap.read()
            if not ok:
                raise ValueError('Falha ao amostrar atividade da tela.')
            mini = cv2.resize(q[y:y+h, x:x+w], (320, 240))
            amostras.append((float(i / fps), mini))
    finally:
        cap.release()
    # Barra inferior: faixa persistente, uniforme na maioria das colunas,
    # com uma fronteira horizontal forte. Não confundir fundo escuro com barra.
    pilha = np.asarray([q for _, q in amostras], dtype=float)
    med = np.median(pilha, axis=0)
    candidatos = []
    for linha in range(216, 237):
        abaixo = med[linha:]
        uniforme = np.mean(np.std(abaixo, axis=0).mean(axis=1) < 12)
        borda = np.mean(np.abs(med[linha] - med[linha-1]))
        estavel = np.mean(np.std(pilha[:, linha:], axis=0)) < 8
        if uniforme > .5 and borda > 30 and estavel:
            candidatos.append((borda, linha))
    if candidatos:
        h = int(h * min(linha for _, linha in candidatos) / 240)
    caixa = [x, y, w, h]
    anterior, centro, trilha, ultimo_t = None, np.array([w/2, h/2]), [], 0
    for t, mini in amostras:
        gray = cv2.cvtColor(mini, cv2.COLOR_BGR2GRAY)[:max(1, round(240*h/original_h)), :]
        # A atividade é medida na área útil; ruído de compressão é descartado.
        gray = cv2.resize(gray, (320, 240))
        if anterior is not None:
            dif = cv2.absdiff(gray, anterior).astype(float)
            dif[dif < 18] = 0
            if np.count_nonzero(dif) > dif.size * .003:
                yy, xx = np.indices(dif.shape)
                alvo = np.array([(xx*dif).sum()/dif.sum()*w/320,
                                 (yy*dif).sum()/dif.sum()*h/240])
                delta = (alvo-centro) * .22
                limite = min(w, h) * .035 * (t-ultimo_t)
                if np.linalg.norm(alvo-centro) > min(w, h)*.035:
                    centro += np.clip(delta, -limite, limite)
        trilha.append({'t': t, 'centro': centro.tolist()})
        anterior, ultimo_t = gray, t
    return caixa, trilha


def expressao(trilha, inicio, eixo, tamanho, total):
    pontos = [(p['t']-inicio, max(0, min(total-tamanho, p['centro'][eixo]-tamanho/2)))
              for p in trilha]
    if not pontos:
        return str(max(0, (total-tamanho)/2))
    expr = f'{pontos[-1][1]:.4f}'
    for (t0, v0), (t1, v1) in reversed(list(zip(pontos, pontos[1:]))):
        expr = (f'if(lt(t,{t1:.6f}),({v0:.4f}+({v1-v0:.4f})*'
                f'clip((t-({t0:.6f}))/{t1-t0:.6f},0,1)),{expr})')
    return expr
