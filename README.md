# Workshop de Estética Avançada com Ênfase em Injetáveis — Landing Page

Landing page de captação do **Workshop de Estética Avançada com Ênfase em Injetáveis**,
realizado pela Navigare em João Pessoa/PB.

**Tema:** Associação de Recursos Estéticos para Potencialização de Resultados
**Data:** 20 de agosto de 2026, a partir das 19h
**Local:** Av. Cabo Branco, 4550 – Cabo Branco, João Pessoa/PB – CEP 58045-010
**Ministrantes:** Drª Cecília Luane e Drª Carol Alves

## Estrutura

```
index.html                        markup, SEO (meta tags, Open Graph, JSON-LD EducationEvent)
assets/css/styles.css             design system completo
assets/js/main.js                 contagem regressiva, reveals, parallax, CTAs e rastreamento
assets/img/                       fotografias das ministrantes

workshop-estetica-avancada.html   versão de arquivo único (gerada)
build-single.py                   gera a versão de arquivo único
```

Site estático, sem dependências nem build obrigatório. Para visualizar localmente:

```bash
python3 -m http.server 8000
```

## Seções

1. **Hero** — título editorial, informações do evento, selo de vagas limitadas, CTA e
   composição fotográfica das duas ministrantes.
2. **O que você vai aprender** — seis tópicos numerados em losangos dourados.
3. **Quem serão as mentoras** — dois cards de mesma altura e mesmo peso visual.
4. **Contagem regressiva** — contador funcional até 20/08/2026 19h (`America/Fortaleza`).
5. **CTA final** — recapitulação das informações e botão de inscrição.

A página não tem cabeçalho nem rodapé: abre direto no hero e encerra no CTA final.
Os CTAs se repetem no hero, aprendizados, mentoras, contagem e encerramento, mais uma
barra fixa que aparece no mobile depois do hero.

## ⚠️ Antes de publicar

### 1. Fotografia

A página inteira usa **um único arquivo** — a composição recortada com as duas
ministrantes, em PNG com fundo transparente:

```
assets/img/ministrantes.png    (~636 × 1210)
```

Ele alimenta três lugares: a composição do hero, o enquadramento fechado do
encerramento e os dois cards das mentoras (cada card mostra um recorte diferente
do mesmo arquivo). Enquanto o arquivo não existir, a página exibe
`ministrantes-placeholder.svg` na mesma paleta.

**Se as proporções do arquivo final forem diferentes**, ajuste o recorte dos cards
direto no `index.html` — são três números por card, em fração da imagem:

```html
<!-- Drª Cecília Luane — figura em primeiro plano, de verde -->
<div class="mentor-photo mentor-photo--crop" style="--rx:.40; --ry:.28; --rw:.53">

<!-- Drª Carol Alves — figura ao fundo, de branco -->
<div class="mentor-photo mentor-photo--crop" style="--rx:.07; --ry:0; --rw:.53">
```

| Variável | Significado |
|---|---|
| `--rx` | borda esquerda da região, em fração da largura |
| `--ry` | borda superior da região, em fração da altura |
| `--rw` | largura da região, em fração da largura |

A altura visível decorre da proporção do card. O `--rw` é igual nos dois para que as
duas apareçam na mesma escala. Como as ministrantes se sobrepõem na composição, o card
da Drª Cecília mostra uma faixa estreita da colega na borda esquerda — aumentar `--rx`
reduz essa faixa, ao custo de descentralizar o rosto.

Se um dia houver retratos individuais em alta resolução, o resultado nos cards fica
mais nítido: troque o `src` das duas imagens da seção de mentoras e remova a classe
`mentor-photo--crop` junto com o `style` do recorte.

### 2. Pendências menores

- **Imagem social** — gerar `assets/img/og-workshop.jpg` (1200×630) e conferir a URL
  canônica em `index.html`.
- **Logotipo da Navigare** — não aparece mais na página, que hoje não tem cabeçalho nem
  rodapé. Se a marca precisar aparecer, o lugar natural é o topo do hero.
- **Aviso de LGPD e links legais** — saíram junto com o rodapé. Se a inscrição passar a
  coletar dados nesta página, eles precisam voltar.

## Inscrição

Os seis CTAs abrem, em nova aba, o evento no Sympla:

```
https://www.sympla.com.br/evento/associacao-de-recursos-esteticos-para-potencializacao-de-resultados/3493821
```

O endereço aparece no `href` de cada botão (funciona sem JavaScript), no schema
`EducationEvent` e na constante `LINK_INSCRICAO` de `assets/js/main.js`, que reescreve
todos os CTAs de uma vez caso o link mude.

## Conversão e analytics

O bloco de tags no `<head>` do `index.html` está pronto e comentado — basta inserir os
IDs e descomentar:

- Google Tag Manager (`GTM-XXXXXXX`)
- Google Analytics 4 (`G-XXXXXXXXXX`)
- Meta Pixel (`SEU_PIXEL_ID`)

Cada clique em CTA já dispara automaticamente:

| Destino | Evento |
|---|---|
| `dataLayer` | `cta_click` com `cta_location` |
| `gtag` | `cta_click`, categoria `inscricao` |
| `fbq` | `Lead` com `source` |

O `cta_location` identifica a origem do clique: `hero`, `aprendizados`, `mentoras`,
`contagem`, `final` ou `barra-mobile`.

Não há formulário na página: a inscrição acontece na plataforma externa.

## Versão de arquivo único

`workshop-estetica-avancada.html` é a mesma página com CSS, JS e imagens embutidos —
abre com dois cliques e pode ser hospedada sozinha, sem estrutura de pastas.

É um arquivo **gerado**: edite sempre `index.html`, `styles.css`, `main.js` e as imagens,
e depois regenere com:

```bash
python3 build-single.py
```

## Identidade

| Token | Cor | Uso |
|---|---|---|
| `--ivory` | `#F4E5D3` | fundo principal marfim |
| `--cream` | `#EED8BE` | fundo secundário creme |
| `--beige` | `#D2AD82` | bege médio, fundo externo |
| `--gold` | `#A76B28` | dourado envelhecido, detalhes |
| `--caramel` | `#B9782E` | botões e números |
| `--brown` | `#4A2D1B` | títulos e áreas de contraste |
| `--ink` | `#211914` | texto principal |
| `--ink-2` | `#6D5545` | texto secundário |
| `--warm-white` | `#FFF9F1` | branco quente |

Tipografia: **Cormorant Garamond** (títulos) e **Inter** (textos), via Google Fonts.
Elemento recorrente da identidade: o **losango dourado** — em números, marcadores,
divisores e decorações flutuantes.

## Validação

Layout conferido em 1920, 1440, 1366, 1280, 768, 420, 390 e 375 px: sem rolagem
horizontal, com o CTA do hero acima da dobra em todas as resoluções de desktop e
notebook. Animações respeitam `prefers-reduced-motion`.
