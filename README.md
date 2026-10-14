# Workshop de Estética Avançada — Landing Page

Landing page do **Workshop de Estética Avançada** (João Pessoa/PB), realizado pela Navigare.

**Evento:** Estratégias Avançadas em Toxina Botulínica e Bioestimulação para Resultados Personalizados
**Data:** 20 de agosto de 2026, 19h · João Pessoa/PB
**Inscrições:** [Sympla](https://www.sympla.com.br/evento/estrategias-avancadas-em-toxina-botulinica-e-bioestimulacao-para-resultados-personalizados/3527797)

## Estrutura

```
index.html                        markup, SEO (meta tags, Open Graph, JSON-LD Event)
assets/css/styles.css             design system completo
assets/js/main.js                 menu mobile, scroll suave, reveal, CTA fixo

workshop-estetica-avancada.html   versão de arquivo único (gerada)
build-single.py                   gera a versão de arquivo único
```

Site estático, sem dependências. Para visualizar localmente:

```bash
python3 -m http.server 8000
```

## Versão de arquivo único

`workshop-estetica-avancada.html` é a mesma página com CSS e JS embutidos —
abre com dois cliques e pode ser hospedada sozinha, sem estrutura de pastas.

É um arquivo **gerado**: edite sempre `index.html`, `styles.css` e `main.js`,
e depois regenere com:

```bash
python3 build-single.py
```

## Identidade

| Token | Cor | Uso |
|---|---|---|
| `--bg` | `#F2E6D8` | fundo claro |
| `--secondary` | `#BF9B7A` | elementos secundários |
| `--accent` | `#8C5B3E` | destaques e botões |
| `--dark` | `#593E2E` | fundos escuros e textos |

Tipografia: **Cormorant Garamond** (títulos) e **Inter** (textos), via Google Fonts.

## Pendências de conteúdo

Substituir antes da publicação definitiva:

- Logotipo da Navigare — hoje é um monograma tipográfico (`.logo-mark` / `.logo-word`).
- Fotos das ministrantes — hoje são avatares com iniciais (`.mentor-avatar`).
- Endereço completo do local — a página informa que será enviado após a inscrição.

## Vídeos (HyperFrames)

`videos/` é um projeto [HyperFrames](https://github.com/heygen-com/hyperframes):
vídeos escritos em HTML/CSS/GSAP e renderizados em MP4 (formato vertical 1080×1920,
para Reels/Stories). Requer Node.js 22+ e FFmpeg.

```bash
cd videos
npm run dev      # preview no navegador
npm run check    # valida a composição
npm run render   # gera o MP4 em renders/
```

As skills do HyperFrames para o Claude Code ficam em `.claude/skills/` (comece por
`/hyperframes`). Exemplo de pedido: *"Usando /hyperframes, crie um vídeo de 15s
divulgando o Workshop de Estética Avançada a partir da landing page."*

O GSAP é servido localmente (`videos/assets/vendor/gsap.min.js`) em vez de CDN,
para que o render funcione mesmo em ambientes com rede restrita.
