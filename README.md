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

CTAs repetidos no cabeçalho, hero, aprendizados, mentoras, contagem, encerramento e em
uma barra fixa que aparece no mobile após o hero.

## ⚠️ Antes de publicar

### 1. Link de inscrição

Todos os botões apontam para a seção final enquanto o link não é definido.
Edite **uma única linha** em `assets/js/main.js`:

```js
var LINK_INSCRICAO = "https://www.sympla.com.br/...";
```

Ao preencher, os oito CTAs passam a abrir esse endereço em nova aba
(`target="_blank" rel="noopener noreferrer"`).

### 2. Fotografias das ministrantes

Coloque os arquivos exatamente com estes nomes:

```
assets/img/cecilia-luane.webp
assets/img/carol-alves.webp
```

Enquanto não existirem, a página exibe automaticamente um retrato-placeholder
(`retrato-cecilia.svg` / `retrato-carol.svg`) na mesma paleta — nenhuma alteração de
código é necessária ao substituí-los.

Recomendações: retrato vertical (proporção 3:4), rosto no terço superior, fundo neutro
ou recortado, exportado em WebP com largura mínima de 1200 px. As duas fotos devem ter
enquadramento e tratamento equivalentes — nenhuma ministrante deve parecer mais
importante que a outra.

### 3. Pendências menores

- **Imagem social** — gerar `assets/img/og-workshop.jpg` (1200×630) e conferir a URL
  canônica em `index.html`.
- **Logotipo da Navigare** — hoje é um monograma tipográfico (`.logo-mark` / `.logo-word`).
- **Links do rodapé** — Política de Privacidade, Termos de Uso e Instagram apontam para
  caminhos genéricos.

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

O `cta_location` identifica a origem do clique: `header`, `hero`, `aprendizados`,
`mentoras`, `contagem`, `final`, `rodape` ou `barra-mobile`.

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
