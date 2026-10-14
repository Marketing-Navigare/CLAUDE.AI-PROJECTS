"""Gera index.html do reel El Niño x Portos a partir do corte (assets/aroll.mp4)
e das palavras transcritas do corte (assets/words-raw.json)."""
import json, random, html

DUR = 59.9
VIDEO_END = 58.99

# ---------- legendas ----------
raw = json.load(open("assets/words-raw.json"))["chunks"]
FIX = {"A": "Há", "Nino": "Niño", "Do": "No", "leitain,": "laytime,",
       "demorragem,": "demurrage,", "POIS,": "pós", "Navigari.": "Navigare.",
       "Navigari": "Navigare", "Rodovia,": "rodovia,", "Ferrovia,": "ferrovia,"}
words = []
i = 0
while i < len(raw):
    t = raw[i]["text"].strip(); a, b = raw[i]["timestamp"]
    if t == "95" and raw[i + 1]["text"].strip() == "%":
        words.append(["95%", a, raw[i + 1]["timestamp"][1]]); i += 2; continue
    if t in ("El", "força") and i + 1 < len(raw):
        nxt = FIX.get(raw[i + 1]["text"].strip(), raw[i + 1]["text"].strip())
        words.append([t + "\u00a0" + nxt, a, raw[i + 1]["timestamp"][1]]); i += 2; continue
    if t == "ele":  # muleta de fala
        i += 1; continue
    if t == "a" and i + 1 < len(raw) and raw[i + 1]["text"].strip() == "pena":
        words.append(["apenas", a, raw[i + 1]["timestamp"][1]]); i += 2; continue
    words.append([FIX.get(t, t), a, b]); i += 1

HL = {"95%", "El\u00a0Niño", "força\u00a0maior.", "isolada.", "tempo.", "cheias", "interromper", "norte,",
      "navegabilidade.", "clima.", "custo.", "laytime,", "demurrage,", "seguro,",
      "maior.", "jurídico.", "integrada", "Navigare.", "Navigare", "turma.",
      "rodovia,", "ferrovia,", "rios,", "armazéns", "terminais.", "atrasa,", "esperar."}

# blocos de legenda definidos à mão (≤ 6 palavras, sem quebrar expressões)
SIZES = [2, 4, 3, 2, 3, 5, 5, 5, 3, 5, 4, 2, 4, 1, 1, 1, 3, 3, 5, 3, 4, 5, 3, 3, 3, 4, 4, 4, 4, 5, 3,
         4, 4, 5, 4, 5, 1, 1, 1, 2, 3, 4, 2, 3, 4, 3, 4, 3, 3, 2, 4, 5]
assert sum(SIZES) == len(words), (sum(SIZES), len(words))
groups, k = [], 0
for n in SIZES:
    groups.append(words[k:k + n]); k += n
# "El Niño" nunca separado
cap_html, cap_js = [], []
for g_i, g in enumerate(groups):
    start = round(g[0][1] - 0.05, 2) if g_i else 0.0
    end = groups[g_i + 1][0][1] - 0.05 if g_i + 1 < len(groups) else VIDEO_END
    end = min(end, g[-1][2] + 0.7)
    dur = round(end - start, 2)
    spans = "".join(
        f'<span class="w{" hl" if w[0] in HL else ""}" id="w{g_i}_{j}">{html.escape(w[0])}</span> '
        for j, w in enumerate(g))
    cap_html.append(f'<div id="cap{g_i}" class="clip cap" data-start="{start}" data-duration="{dur}" '
                    f'data-track-index="9"><div class="cap-in" id="capin{g_i}">{spans.strip()}</div></div>')
    cap_js.append(f'tl.fromTo("#capin{g_i}",{{scale:0.86,opacity:0,y:18}},{{scale:1,opacity:1,y:0,duration:0.16,ease:"back.out(2.2)"}},{start});')
    for j, w in enumerate(g):
        cap_js.append(f'tl.fromTo("#w{g_i}_{j}",{{opacity:0.55}},{{opacity:1,duration:0.08}},{round(w[1],2)});')
        cap_js.append(f'tl.fromTo("#w{g_i}_{j}",{{scale:1}},{{scale:1.12,duration:0.09,yoyo:true,repeat:1,ease:"power2.out"}},{round(w[1],2)});')

# ---------- câmera (punch-ins por corte) ----------
FACES = [(0, .64, .44), (5.22, .61, .42), (8.34, .55, .43), (10.94, .55, .37), (20.10, .54, .33),
         (21.06, .56, .35), (23.03, .56, .35), (26.25, .51, .51), (27.17, .50, .50), (31.22, .50, .43),
         (33.95, .50, .40), (36.28, .51, .39), (38.78, .50, .39), (45.15, .52, .39), (49.68, .53, .41),
         (56.47, .53, .46)]
CAM = [(0, 1.85, .44), (5.22, 1.30, .40), (8.34, 1.55, .40), (10.12, 1.95, .40), (10.94, 1.35, .40),
       (19.95, 1.60, .40), (20.10, 1.25, .40), (24.90, 1.70, .40), (26.25, 2.00, .42), (31.15, 1.35, .40),
       (33.52, 1.80, .40), (33.95, 1.20, .47), (36.28, 1.25, .47), (38.78, 1.50, .40), (45.15, 1.20, .47),
       (48.98, 1.45, .47), (49.68, 1.30, .40), (52.60, 1.20, .50), (56.47, 1.45, .50)]

def face_at(t):
    f = FACES[0]
    for x in FACES:
        if x[0] <= t + 1e-6: f = x
    return f[1], f[2]

def cam_xy(S, fx, fy, ty, tx=.5):
    lim = (S - 1) / 2
    cx = max(-lim, min(lim, tx - .5 - (fx - .5) * S))
    cy = max(-lim, min(lim, ty - .5 - (fy - .5) * S))
    return round(cx * 1080, 1), round(cy * 1920, 1)

cam_js = []
for n, (t0, S, ty) in enumerate(CAM):
    t1 = CAM[n + 1][0] if n + 1 < len(CAM) else VIDEO_END
    fx, fy = face_at(t0)
    x0, y0 = cam_xy(S, fx, fy, ty)
    S1 = S * 1.035
    x1, y1 = cam_xy(S1, fx, fy, ty)
    cam_js.append(f'tl.fromTo("#cam",{{scale:{S},x:{x0},y:{y0}}},{{scale:{S1:.3f},x:{x1},y:{y1},duration:{t1 - t0:.2f},ease:"none",immediateRender:false}},{t0});')

# ---------- chuva determinística ----------
rnd = random.Random(7)
rain = "".join(
    f'<i class="drop" style="left:{rnd.randint(0, 1060)}px;top:{rnd.randint(-300, 1150)}px;height:{rnd.randint(50, 110)}px;opacity:{rnd.uniform(.25, .7):.2f}"></i>'
    for _ in range(70))

tpl = open("index.template").read()
out = (tpl.replace("{{DUR}}", str(DUR)).replace("{{VIDEO_END}}", str(VIDEO_END))
       .replace("{{CAPTIONS}}", "\n      ".join(cap_html))
       .replace("{{CAP_JS}}", "\n      ".join(cap_js))
       .replace("{{CAM_JS}}", "\n      ".join(cam_js))
       .replace("{{RAIN}}", rain))
open("index.html", "w").write(out)
print(len(groups), "grupos de legenda")
for g in groups: print(f"{g[0][1]:6.2f}", " ".join(w[0] for w in g))
