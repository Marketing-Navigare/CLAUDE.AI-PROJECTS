# Workshop de Estética Avançada — Landing Page

Landing page do **Workshop de Estética Avançada** (João Pessoa/PB), realizado pela Navigare.

**Evento:** Estratégias Avançadas em Toxina Botulínica e Bioestimulação para Resultados Personalizados
**Data:** 20 de agosto de 2026, 19h · João Pessoa/PB
**Inscrições:** [Sympla](https://www.sympla.com.br/evento/estrategias-avancadas-em-toxina-botulinica-e-bioestimulacao-para-resultados-personalizados/3527797)

## Estrutura

```
index.html              markup, SEO (meta tags, Open Graph, JSON-LD Event)
assets/css/styles.css   design system completo
assets/js/main.js       menu mobile, scroll suave, reveal, CTA fixo
```

Site estático, sem build e sem dependências. Para visualizar localmente:

```bash
python3 -m http.server 8000
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
