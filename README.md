# Eastern Denmark Business Events — calendar feed

Public, verified calendar of business events in Copenhagen and Eastern Denmark, curated by Copenhagen Capacity.

- Landing page: https://copenhagensynergy.github.io/copcap-events/
- Subscribe (iCal): https://copenhagensynergy.github.io/copcap-events/events.ics

Source of truth is the Notion database "Eastern Denmark Business Events". A weekly scheduled task regenerates `events.ics` and `index.html` with `scripts/build_site.py`; do not edit those two files by hand.

## Embedding on another website

- One-line embed (auto-height): `<div class="copcap-events"></div><script src="https://copenhagensynergy.github.io/copcap-events/embed.js" async></script>`
- Plain iframe: `https://copenhagensynergy.github.io/copcap-events/?embed=1` (fixed height).
- Options (as `data-*` on the div, or URL parameters on the iframe): `country` (`""` = all), `sort` (`date`, `event`, `organiser`, `sector`, `team`, `country`, `meet`; prefix `-` for descending, e.g. `sort=-date`), `subscribe=0`, `theme=light|dark|auto`, `bg=transparent`.
- Demo: https://copenhagensynergy.github.io/copcap-events/embed-demo.html
- Embed mode lives in `scripts/build_site.py` (generated page) and `embed.js` (hand-maintained loader). The page reports its height to the host with `postMessage({type:"copcap-events:resize", id, height})`; `embed.js` only accepts it from the copenhagensynergy.github.io origin.
