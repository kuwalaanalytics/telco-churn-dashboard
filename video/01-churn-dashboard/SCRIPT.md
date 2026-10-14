# Voice sheet: churn dashboard explainer (v4)

Length 40.5 seconds. Every spoken line is on screen word for word, so the video
also works with the sound off.

Each scene runs in the same order: the picture moves in and settles, there is a
short pause, then the line types while nothing else moves. Start speaking when
the line starts typing, not when the picture appears.

Reading pace is about 2.5 words a second. The whole script is about 60 words
when read aloud.

| # | Picture moves | Line types (speak) | Scene ends | Say | On screen |
|---|---|---|---|---|---|
| 1 | from 0.0 | 0.0 | 3.0 | Which customers are about to leave you? | The question, large and alone, on screen from the first frame. "leave" is orange and gets underlined |
| 2 | 3.0 to 4.7 | 5.0 to 6.7 | 7.3 | This dashboard shows you. | The real dashboard rises in, pans down past the filters, key figures and charts, and stops. "Demo on public IBM sample data" shows below |
| 3 | 7.3 to 8.3 | 8.6 to 11.0 | 11.65 | 1 in 4 customers left in one month. | Four people and the real Churn Rate card (26.5%) arrive together. The fourth person turns orange: "3 stayed", "1 left" |
| 4 | 11.7 to 12.1 | 12.4 to 14.0 | 15.55 | $139,000 a month, gone. | The real Monthly Revenue at Risk card ($139,131) lands. The music drops away under this scene |
| 5 | 15.6 to 16.5 | 16.85 to 19.4 | 19.95 | Month to month customers leave most. | The real Churn Rate by Contract chart, then a ring on the month to month bar and the tag "43% leave" |
| 6 | 20.0 to 20.9 | 21.25 to 23.2 | 23.8 | New customers leave fastest. | The real Churn Rate by Tenure Band chart, then a ring on the first point and the tag "53% in the first 6 months" |
| 7 | 23.85 to 25.5 | 25.9 to 27.8 | 28.4 | It ranks who to call first. | The top at risk customers list. Four rows land in rank order, then row 1 is ringed and tagged "Call first" |
| 8 | 28.45 to 30.8 | 31.15 to 33.6 | 34.2 | The top 20% holds half the leavers. | 100 dots, one for each 1% of customers. The top 20% by risk score is boxed, the leavers turn orange, tagged "51% of leavers" |
| 9 | (none) | 34.35 to 36.7 | 37.5 | Do you know who is about to leave? | The ask, typed large and alone |
| 10 | 37.55 to 39.25 | (no voice) | 40.5 | | End card, top to bottom: the full logo (bulb and "Kuwala Analytics"), the LinkedIn, Facebook and Instagram icons, "Contact us for your data needs", and "Demo on public IBM sample data" in small text |

Line 4 types quickly but needs about 3 seconds to say. Say it as "one thirty
nine thousand dollars a month, gone"; the scene holds until 15.55 to give you
room.

## Recording the voice in CapCut

1. Import `renders/churn-dashboard-v4.mp4` and mute its own sound.
2. Add `assets/audio/music.wav` and `assets/audio/sfx.wav`, both starting at zero.
3. Record your voice over the picture, starting each line when it starts typing.
4. Lower the music 8 to 10 dB under your voice. Leave the effects at full level.
5. Export at 1080 by 1920, 60 frames a second.

## Post caption and pinned comment

The video no longer shows the web address, so put it in the post:

> Do you know who is about to leave? See the live dashboard:
> https://kuwalaanalytics.github.io/telecom-churn-retention-analysis/

## Where the figures come from

Every figure is from the public IBM Telco sample dataset (7,043 customers), as
shown on the dashboard and stored in `data/clean/findings.json`.

| On screen | Exact figure |
|---|---|
| 1 in 4 customers left | Churn rate 26.5% (1,869 of 7,043) |
| $139,000 a month | $139,131 monthly revenue at risk |
| 43% leave | Month to month churn 42.7% |
| 53% in the first 6 months | Churn in months 0 to 6 is 52.9% |
| Risk scores 94.7, 94.2, 94.0, 93.6 | The four highest scoring current customers |
| 51% of leavers | The top 20% by risk score held 51% of all leavers in a back test |

In the dot picture, 26 of the 100 dots are orange (26.5% churn) and 13 of those
sit in the top 20 (half of the leavers).

## Changing the timing

Every time lives in the `timing` block near the bottom of `index.html`. The
clip windows (`data-start`, `data-duration`) must match its `ends`. After a
change, run `npm run audio` so the sound follows, then render.

## Credits

The LinkedIn, Facebook and Instagram icons are from Font Awesome Free 6.7.2
(https://fontawesome.com), licensed CC BY 4.0. The licence note is kept inside
each file in `assets/icons/`.

## Versions

- v1 (28.6 s): first cut. Lines typed while pictures were still moving. Ended on the dashboard address.
- v2 (40.5 s): pictures settle before each line types; end card changed to contact details and social icons.
- v3 (40.5 s): the data disclosure shows with the dashboard and on the end card only, instead of under every scene.
- v4 (40.5 s): end card reordered to full logo, social icons, contact line, then the data note. Logo background cleaned of JPEG noise.
