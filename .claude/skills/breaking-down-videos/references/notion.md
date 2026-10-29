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
