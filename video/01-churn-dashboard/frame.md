# Kuwala Analytics video frame

The brand rules for every Kuwala Analytics video. Values were taken from the
logo file and the churn dashboard, not from memory.

## Canvas

- Portrait, 1080 by 1920, 60 frames a second.
- Safe area: nothing important in the top 150 pixels, the right 140 or the
  bottom 400. Content sits between x 80 and x 940, centred on x 510.

## Colour

Each colour has one meaning and keeps it everywhere, including in text.

| Name | Code | Meaning |
|---|---|---|
| Ink | `#081838` | Text and outlines. Sampled from the logo lines |
| Stay blue | `#2F4B8F` | Customers who stay, and neutral data. The dashboard's bar colour |
| Leave orange | `#E8590C` | Customers who leave, revenue lost, risk. The dashboard's alert colour |
| Glow yellow | `#F8E878` | The Kuwala brand only: the typing cursor and brand highlights. Sampled from the logo bulb |
| Page | `#F2F4F8` | Background |
| Card | `#FFFFFF` | Cards and panels |
| Muted | `#5B6577` | Small labels |

The logo keeps its own colours and is never recoloured. It always sits on white.

## Type

- One font: Inter, weights 500, 600, 700 and 800, shipped in `assets/fonts`.
- Opening and closing questions: 140 pixels, weight 800.
- Typed lines: 84 pixels, weight 700.
- Labels: never smaller than 28 pixels.
- Sentence case. No exclamation marks, no emoji, no dashes.

## Shape

- Cards: white, corner radius 28 to 44, soft shadow `0 18px 50px rgba(8,24,56,.14)`.
- Chips and tags: fully rounded.

## Motion

- Things rise 40 to 60 pixels into place while fading in, over 0.4 seconds, ease `power3.out`.
- Lines are typed letter by letter at 14 letters a second with a visible cursor.
- One thing moves at a time. The picture finishes moving, then a pause of about
  0.35 seconds, then the line types while nothing else moves. Rings and tags land
  before the line, not during it. (Owner feedback on v1, 14 October 2026.)
- The layout of a line is fixed before typing starts, so centred text never jumps.
- A line holds about half a second after it finishes, then the scene moves on.
- No bounces, no spins, no flashing.

## Do

- Show the real dashboard: real screenshots and real figures.
- Disclose the data: "Demo on public IBM sample data" shows with the first data
  scene (the dashboard) and again on the end card. (Owner's choice, 14 October 2026.)
- Colour the words that mean leaving in leave orange.
- End on one question, then the end card, top to bottom: the full logo (bulb and
  wordmark), the LinkedIn, Facebook and Instagram icons, "Contact us for your data
  needs", and the small data note. No dividers. Web addresses go in the post
  caption, not the video. (Owner's layout, 14 October 2026.)

## Do not

- Do not show a number that is not on the dashboard or in `data/clean/findings.json`.
- Do not use stock photos, faces or an AI voice.
- Do not recolour the logo or place it on a coloured background.
- Do not put more than one new thing on screen at a time.
