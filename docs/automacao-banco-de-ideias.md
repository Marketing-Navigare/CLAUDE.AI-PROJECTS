# Automação: WhatsApp → Banco de Ideias (Notion)

Fluxo: alguém da equipe vê um Reel ou TikTok bom → **Compartilhar → WhatsApp → número da
Navigare** → o Make cria a linha na fila do Notion → a análise automática do Claude roda
uma vez por dia e preenche tudo, inclusive "Como replicar na Navigare".

- Biblioteca no Notion: https://app.notion.com/p/b024531fde3648d1a741b19040be7340
- Visualizações: 📥 Fila · 💡 Banco de pautas · 🎬 Aprovadas para gravar · ⚠️ Erros

---

## 1. Antes de começar (pré-requisitos)

1. **Um número de WhatsApp dedicado** na **WhatsApp Business Platform (Cloud API)**,
   ligado a um app da Meta (developers.facebook.com → app do tipo Business → produto
   WhatsApp).
   - A Cloud API **não lê grupos comuns**. Cada pessoa manda o link **no privado** para
     esse número. Para a equipe, é igual a mandar para um contato.
   - Use um chip novo, ou confira se o número atual pode usar o modo "coexistência"
     (app WhatsApp Business + API ao mesmo tempo). Um número que já está no WhatsApp
     comum precisa ser migrado.
2. **Conexão do WhatsApp Business Cloud no Make**, com o token permanente (usuário do
   sistema) e o Phone Number ID.
3. **Conexão do Notion no Make**, com a página "Documentos Marketing" (ou a biblioteca)
   compartilhada com a integração do Make.
4. **Lista de números autorizados**: só a equipe pode alimentar o banco.

---

## 2. Cenário no Make: "Banco de Ideias — WhatsApp → Notion"

```
[1 WhatsApp: Watch Events]
   → [2 Filtro: é texto com link do Instagram/TikTok e o número está autorizado]
   → [3 Text parser: extrair os links]  → [4 Iterator: um link por vez]
   → [5 Set variables: link limpo + nota]
   → [6 Notion: Search Objects (Link = link limpo)]
   → Router
       ├─ já existe → [7a WhatsApp: "Esse já está no banco 👍"]
       └─ novo      → [7b Notion: Create a Database Item] → [8 WhatsApp: "✅ Entrou na fila"]
```

### Módulo 1. WhatsApp Business Cloud → Watch Events
Gatilho instantâneo (webhook). Recebe cada mensagem enviada para o número.

### Filtro 2. Mensagem válida
Todas as condições:
- `Messages[].Type` = `text`
- `Messages[].Text.Body` corresponde ao padrão (regex) `instagram\.com|tiktok\.com`
- `Messages[].From` está na lista de números da equipe. Use um Data Store "Equipe"
  (telefone → nome) ou um filtro com os números.

### Módulo 3. Text parser → Match pattern
- Padrão:
  `https?://(?:www\.)?(?:instagram\.com/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)|(?:vm\.|vt\.)?tiktok\.com/[^\s]+)`
- Global match: **Sim** (para o caso de virem vários links na mesma mensagem)
- Texto: `Messages[].Text.Body`

### Módulo 4. Iterator
Um ciclo por link encontrado.

### Módulo 5. Tools → Set multiple variables
- `link_limpo`:
  - Instagram: `https://www.instagram.com/reel/{{3.$1}}/`. Esse formato padronizado evita
    duplicar o mesmo vídeo com `?igsh=...` diferente.
  - TikTok: o link como veio, sem nada depois do `?` (use `split(link; "?")` e pegue o
    primeiro item).
- `nota`: o texto da mensagem sem o link (`replace(Text.Body; link; "")`, com `trim`).
- `quem`: o nome do Data Store "Equipe" ou, se não houver, `Contacts[].Profile.Name`.

### Módulo 6. Notion → Search Objects
- Busca em: Database items, banco **Biblioteca de Vídeos Virais**
- Filtro: `Link` **equals** `link_limpo`
- Limite: 1

### Router
**Rota A (já existe)**, filtro: total de resultados do módulo 6 ≥ 1
- 7a. WhatsApp → Send a Message para `Messages[].From`:
  "Esse vídeo já está no banco 👍 {{URL da página encontrada}}"

**Rota B (novo)**, filtro: total de resultados do módulo 6 = 0
- 7b. Notion → Create a Database Item:

| Propriedade | Valor |
|---|---|
| Gancho | `⏳ Aguardando análise` |
| Link | `link_limpo` |
| Status | `Na fila` |
| Salvo por | `quem` |
| Data salvo | `now` |
| Nota de quem salvou | `nota` |

- 8. WhatsApp → Send a Message:
  "✅ Entrou na fila do Banco de Ideias. A análise sai na próxima rodada (todo dia às [hora])."

> As respostas automáticas são permitidas porque a pessoa escreveu primeiro, dentro da
> janela de 24h da Meta. Não precisa de template aprovado.

### Tratamento de erros
Nos módulos do Notion, adicione o handler **Break**, com 3 tentativas e intervalo de 1 min.
Quedas rápidas do Notion não perdem a mensagem.

---

## 3. Análise automática (Claude)

O Make só organiza a fila. A análise completa (baixar o vídeo, ver quadro a quadro,
transcrição, psicologia, "Como replicar na Navigare") roda numa **sessão agendada do
Claude Code**, uma vez por dia, com a skill `breaking-down-videos` deste repositório:

1. Pega as linhas com Status **Na fila**, as mais antigas primeiro (até 10 por rodada).
2. Analisa uma por uma e preenche **a mesma linha**: todas as colunas, a página completa,
   o curso relacionado e uma sugestão de prioridade. Ao terminar, muda para **Analisado**.
3. Quando não dá para analisar (post privado, carrossel, falha no download), marca
   **Erro** e escreve o motivo.

Para ela rodar sozinha, falta configurar:
- [ ] `SCRAPECREATORS_API_KEY` como variável de ambiente do ambiente na nuvem
- [ ] criar a tarefa agendada (horário a definir)

---

## 4. Rotina da equipe

1. Viu um vídeo bom → **Compartilhar → WhatsApp → Banco de Ideias Navigare**. Se quiser,
   escreva junto para que serviria ("pro workshop de toxina", "gancho bom pra pós").
2. No dia seguinte a análise está no Notion, em **💡 Banco de pautas**.
3. Na reunião de pauta, marque **Aprovado para gravar** no que vai virar conteúdo; o item
   aparece em **🎬 Aprovadas para gravar**.
4. Confira **⚠️ Erros** de vez em quando. Normalmente é post privado ou carrossel de fotos.

## Custos

- Scrape Creators: de 4 a 14 créditos por vídeo. Perfis grandes gastam mais, porque a
  ferramenta busca o histórico do criador.
- Make: cerca de 6 a 8 operações por link recebido.
- WhatsApp Cloud API: responder dentro da janela de 24h aberta pela pessoa não tem custo de
  template.
