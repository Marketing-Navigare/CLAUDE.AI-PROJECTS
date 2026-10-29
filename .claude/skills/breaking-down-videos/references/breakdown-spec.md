# Breakdown spec

The file every breakdown writes, in this order. Each analysis section is a full paragraph of
evidence, never a bullet list of labels.

## Evidence rules

- Quote the creator word for word, in double quotes, every time a line is named. Never
  paraphrase a hook.
- Every claim about what's on screen cites a timestamp from the watch pass (`0:04`). A claim
  with no frame behind it doesn't go in.
- Numbers come from `video.json` only. If a field is null, write "not available", never estimate.
- Name a lever only with the line or frame that pulls it. "Curiosity gap" alone is a label;
  "Curiosity gap: opened by 'Most people don't know this' at 0:03, closed at 0:41" is analysis.
- The template must work for anyone: no creator-specific nouns left in it, every specific
  swapped for a bracket that says what kind of thing goes there.

---

## File skeleton

```markdown
---
hook: "<text hook, or the spoken first line if there's no text card>"
creator: "@<handle>"
platform: <instagram | tiktok>
link: <link>
posted: <YYYY-MM-DD>
plays: <n>
likes: <n>
comments: <n>
followers: <n>
outlier: <rolling_multiple>x
duration_s: <n>
format: <Format>
hook_type: <Hook type>
template: "<Template name>"
feel: "<section 10 one-liner>"
replicate: "<one-line version of the Como replicar section: the best pauta + who films it + CTA>"
---

# <Template name>: @<handle>

**<plays> plays · <outlier>x their usual · <posted>**  [watch it](<link>)

## Why it won
<one paragraph: the single biggest reason, then the two or three that back it up>

## Script template: <Template name>
<template beats, see below>

### Language rules
<one paragraph>

**Whole video in one line:** <framework mad-lib>

## Como replicar na Navigare
<see "Como replicar na Navigare" below>

## Beat map
<beat map table>

## Analysis
### 1. The hook
### 2. The promise
### 3. Who it's for
### 4. Structure
### 5. Psychology
### 6. The language
### 7. The ending
### 8. Why people share it
### 9. One-line summary
### 10. Feel
### 11. Visual and format
### 12. Hook type

## Transcript
<word for word, from video.json>

## Caption
<word for word, from video.json>
```

The beat map sits above the analysis because it's the part you reuse first when writing.

---

## Sections 1–9

1. **The hook.** Spoken hook and text hook (cover or first on-screen card) quoted separately,
   then how they work together. Name the lever and why it stops this audience in particular.
2. **The promise.** What the viewer believes they'll walk away with, practical or identity,
   and the second it's made.
3. **Who it's for.** Who it speaks to, their frustration, their fear, and the line that makes
   them feel personally named.
4. **Structure.** The chain of beats joined with `→`, each tension point, every re-hook quoted,
   and where the payoff is held back.
5. **Psychology.** Use the names in `psychology-levers.md`. Cover only the levers this video
   actually pulls, each with its line or frame and timestamp.
6. **The language.** Sentence length, tone, connectors, the nouns that make it concrete, the
   stickiest lines.
7. **The ending.** The CTA quoted, the feeling the viewer leaves with, explicit or implicit
   ask, and what the comments-to-likes ratio says about which action it was built for
   (a high ratio = built for comments, like a keyword CTA; a low one = built for saves and shares).
8. **Why people share it.** Why someone sends it, what sending it says about the sender, why
   it gets saved.
9. **One-line summary.** One sentence. The same idea as Why it won, compressed.

## Beat map + sections 10–12

**Beat map**, one row per beat, from the watch pass:

    | Time | Beat | Said (word for word) | On screen | Job |
    |---|---|---|---|---|
    | 0:00–0:03 | Hook | "Your AI is the world's most convincing yes man." | Creator to camera, text card YES MAN | Stop the scroll with a flaw the viewer has felt |

Beat names match the chain in section 4. The Job column says what the beat does for the
viewer's attention, not what it's about.

10. **Feel.** Delivery energy (calm / conversational / urgent / hyped), pace in words per
    second (transcript word count ÷ duration, one decimal), cut rate ("a cut every N seconds",
    from `scene_cuts` in the watch output, checked against the frames), music (see SKILL.md
    Step 2, never guessed), tone, and where it's filmed (desk, studio, out in the world, screen
    only). One paragraph, then a one-liner like
    `Calm, 3.1 w/s, cut every 2.4s, desk, no music, insider-confident`.
11. **Visual and format.** Per beat: visual, movement and layout, using the labels in
    `hook-types.md`. Then the one Format for the whole video.
12. **Hook type.** One type from `hook-types.md` (add `+ scroll-stop` if one is layered on),
    the spoken hook word for word, and the hook as a fill-in-the-blank with [X]/[Y] brackets.

---

## The template

Name it like a move, two to five words: "The Hidden Setting Reveal", "The Confessed Mistake".
One line per beat:

```
**<Beat name>:** [<what goes here, written the way the creator would say it, with
[brackets] for every specific>]
```

Every beat in the beat map gets a template line, in order, including re-hooks and the CTA.
Then `### Language rules`: one paragraph on person (you / I), sentence length, which nouns
must be specific, the connectors to say out loud, and how the CTA keyword is chosen.

The whole-video line joins the beats with `→`:
`[Flaw claim about tool] → [proof it agrees with anything] → [the prompt that flips it] → [result] → comment [WORD]`.

---

## Como replicar na Navigare

The one section written for Navigare's own marketing, so it is the only place Navigare
specifics go (the template above stays generic). Navigare sells pós-graduação courses and
workshops to health and aesthetics professionals (estética avançada, toxina botulínica,
bioestimuladores, harmonização, and other specialisations) in several Brazilian cities.
If the `copy-navigare` skill is available, follow its voice. Write it in Brazilian
Portuguese, in this order:

1. **Vale a pena replicar?** One or two sentences: does this structure fit Navigare's
   audience and goals, and which funnel stage it serves (alcance / autoridade / captação de
   leads / inscrição). If it doesn't fit, say why and stop the section there.
2. **3 pautas prontas.** Three concrete topics for Navigare, each with the template's hook
   filled in word for word (in Portuguese, ready to say on camera) and one line on the payoff.
   Use real course themes, never invented facts, numbers, results or testimonials; put
   [brackets] where a real figure or case has to come from the team.
3. **Roteiro preenchido.** The best of the three, written out beat by beat on the template's
   beats, with the same timings as the beat map.
4. **Quem grava e como.** Who should be on camera (professor/a, coordenador/a, aluna/o,
   especialista convidado/a), where to film, and what to copy from the Feel and Visual
   sections (pace, cut rate, text cards, B-roll to shoot).
5. **CTA para a Navigare.** The ask adapted to Navigare's goal for this pauta (comment a
   keyword for a DM, link na bio, WhatsApp, inscrição no curso/workshop), and the keyword.
6. **Cuidados.** What to avoid for this audience: promises of results, before/after photos
   and other claims health-profession councils restrict in advertising; anything in the
   original that doesn't transfer to an education brand.

---

## Edge cases

- **Song or trend-sound audio.** Lyrics aren't the creator's words. The transcript keeps only
  what the creator says and writes `[song lyrics omitted: <track>]` where they ran. If the
  creator says nothing, write "No speech; the words are on screen" and transcribe the
  on-screen text in order instead.
- **AI transcript over music.** Stock phrases with no frame behind them ("Thanks for
  watching!", "Subscribe", "you") are the transcriber making things up over music. Leave them
  out and note it once.
- **Silent text-overlay videos.** Hook delivery is `Overlay`, the spoken hook is "not
  available (no speech)", and the hook analysis is about the text card. Words per second uses
  on-screen words ÷ duration and says so (`2.1 on-screen w/s`).
- **Cut counting.** `scene_cuts` can miss jump cuts against the same background and can
  count a fast camera move as a cut. Check it against the frames. If the count is an estimate,
  write "about".
- **Multiple against the current median.** When `multiple_basis` starts with "current
  median", the post is older than the catalogue reaches, and the multiple compares it
  to the creator's 12 newest posts. Say "Nx vs their current average" wherever the number appears.
- **No words at all.** No speech and no text card: the hook is the opening action, described
  in a few plain words, and section 1 is about that first frame.
- **Someone else says the hook.** A podcast guest or a stitched clip: quote it as theirs, say
  who in section 1, and use Format `React / Duet` when the creator reacts to the clip.

---

## Self-check before saving

- [ ] Spoken hook quoted exactly as the transcript has it
- [ ] Every on-screen claim has a timestamp
- [ ] Every lever named has its line or frame
- [ ] Beat map rows = template beats = section 4 chain, same names, same order
- [ ] Template has zero creator-specific nouns left
- [ ] Feel line has a w/s number and a cut-rate number
- [ ] Numbers match `video.json`; nulls written as "not available"
- [ ] No song lyrics or transcript filler presented as the creator's words
- [ ] Como replicar na Navigare has 3 pautas with hooks written out, a filled roteiro and a
      CTA, and invents no figures, results or testimonials
