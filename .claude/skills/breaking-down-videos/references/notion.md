# Optional: save breakdowns to Notion too

Only when the user has asked for Notion and has the Notion connector on in Claude
(Settings → Connectors → Notion). The markdown file is always saved first; Notion is a copy.

## First time: make the library

Ask the user which Notion page the library should live under. Then create a database called
**Viral Video Library** under it with these properties:

| Property | Type |
|---|---|
| Hook | title |
| Creator | text |
| Link | url |
| Plays · Likes · Comments · Followers | number |
| Outlier x | number |
| Duration (s) | number |
| Posted | date |
| Format | select (the Format list in `hook-types.md`) |
| Hook Type | select (the Hook types in `hook-types.md`) |
| Template | text |
| Framework | text (the whole-video line) |
| Feel | text |
| Psychology | multi-select (lever names from `psychology-levers.md`) |
| Why It Won | text |

Save the database's URL to the skill's `.env` as `NOTION_LIBRARY_URL=<url>` so later runs
find it without asking.

## This library (Navigare): Portuguese

The library already exists: **Biblioteca de Vídeos Virais** (URL in `.env` as
`NOTION_LIBRARY_URL`). Its properties and options are in Portuguese. Write every
breakdown in Brazilian Portuguese (the markdown file and the Notion page body); keep the
hook and any quoted lines word for word in the video's original language.

Map the front matter to these property names:

| Spec field | Notion property |
|---|---|
| Hook | Gancho (title) |
| Creator | Criador |
| Link | Link |
| Plays / Likes / Comments / Followers | Visualizações / Curtidas / Comentários / Seguidores |
| Outlier x | Acima da média (x) |
| Duration (s) | Duração (s) |
| Posted | Publicado em |
| Format | Formato |
| Hook Type | Tipo de gancho |
| Template | Template |
| Framework | Estrutura |
| Feel | Ritmo |
| Psychology | Gatilhos psicológicos |
| Why It Won | Por que funcionou |

Option translations:

- Formato: Talking Head → Rosto na câmera · Silent Text Overlay → Texto sem fala ·
  Voiceover B-Roll → Narração + B-roll · Vlog → Vlog · Skit → Esquete ·
  Demo / Screen → Demonstração / Tela · Listicle → Lista · Rant → Desabafo ·
  Whiteboard → Quadro branco · Ranking → Ranking · Green Screen → Fundo verde ·
  React / Duet → React / Dueto · Other → Outro
- Tipo de gancho: Prediction → Previsão · Experiment → Experimento · How-to → Como fazer ·
  Secret → Segredo · Contrarian → Contrário · Comparison → Comparação · Question → Pergunta ·
  Story → História · POV / Skit → POV / Esquete
- Gatilhos psicológicos: Pattern Interrupt → Quebra de padrão · Curiosity Gap → Lacuna de
  curiosidade · Loss Framing → Medo de perder · Identity Callout → Chamada de identidade ·
  Open Loop → Loop aberto · Re-hook → Re-gancho · Variable Reward → Recompensa variável ·
  Cognitive Ease → Facilidade cognitiva · Vulnerability → Vulnerabilidade · Proof → Prova ·
  Identity Alignment → Alinhamento de identidade · Reciprocity → Reciprocidade ·
  Single Ask → Pedido único · Consistency → Consistência

## Every run

1. Read `NOTION_LIBRARY_URL` from `.env`. Fetch the database to confirm the properties.
2. Search it for a row with the same Link. If one exists, update that page instead of making
   a duplicate.
3. Otherwise create a page: properties from the markdown file's front matter, body = the
   markdown file's body.
4. Fetch the page back and confirm the beat map table and the template rendered. It isn't
   saved until the fetch shows it.

If the Notion tools aren't available, say so in one line and carry on: the markdown file is
the breakdown.
