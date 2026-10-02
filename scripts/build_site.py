"""Build events.ics + index.html for the Eastern Denmark events feed.
Input: rows.json = list of dicts with keys url, Event, date:Date:start, date:Date:end,
Venue, City, Organiser, Website, Description, Date note, Listing.
Usage: python3 build_site.py rows.json BASE_URL outdir
Only events whose end (or start) date is today or later are written.
"""
import json, sys, os, html, datetime as dt, urllib.parse as u

rows, base, out = json.load(open(sys.argv[1])), sys.argv[2].rstrip("/"), sys.argv[3]
os.makedirs(out, exist_ok=True)
today = dt.date.today()
CAL = "Eastern Denmark Business Events"

def esc(s): return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def fold(line):
    b = line.encode("utf-8"); parts = []
    while len(b) > 75:
        cut = 75 if not parts else 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        parts.append(b[:cut].decode()); b = b[cut:]
    parts.append(b.decode())
    return "\r\n ".join(parts)

evs = []
for r in rows:
    s = r.get("date:Date:start")
    if not s: continue
    s = dt.date.fromisoformat(s[:10]); e = dt.date.fromisoformat((r.get("date:Date:end") or r["date:Date:start"])[:10])
    if e < today: continue
    evs.append((s, e, r))
evs.sort(key=lambda x: x[0])

stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Copenhagen Capacity//Eastern Denmark Events//EN",
     "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:" + CAL, "X-WR-TIMEZONE:Europe/Copenhagen",
     "X-WR-CALDESC:Verified business events in Copenhagen and Eastern Denmark",
     "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
for s, e, r in evs:
    uid = r["url"].rstrip("/").split("/")[-1].split("?")[0] + "@eastern-denmark-events"
    desc = "\n".join(x for x in [r.get("Description"), r.get("Date note"), "Organiser: " + (r.get("Organiser") or ""), "Meet CopCap: " + ((r.get("Meet CopCap") or "").strip() or "CopCap"), r.get("Website")] if x)
    L += ["BEGIN:VEVENT", "UID:" + uid, "DTSTAMP:" + stamp,
          "DTSTART;VALUE=DATE:" + s.strftime("%Y%m%d"), "DTEND;VALUE=DATE:" + (e + dt.timedelta(days=1)).strftime("%Y%m%d"),
          "SUMMARY:" + esc(r["Event"]), "LOCATION:" + esc(r.get("Venue")), "DESCRIPTION:" + esc(desc),
          "URL:" + (r.get("Website") or ""), "TRANSP:TRANSPARENT", "END:VEVENT"]
L.append("END:VCALENDAR")
open(os.path.join(out, "events.ics"), "w", newline="").write("\r\n".join(fold(x) for x in L) + "\r\n")

ics = base + "/events.ics"; host = ics.split("://", 1)[1]
links = {
    "Outlook (work / Microsoft 365)": "https://outlook.office.com/calendar/0/addfromweb?" + u.urlencode({"url": ics, "name": CAL}),
    "Outlook.com": "https://outlook.live.com/calendar/0/addfromweb?" + u.urlencode({"url": ics, "name": CAL}),
    "Google Calendar": "https://calendar.google.com/calendar/r?" + u.urlencode({"cid": "webcal://" + host}),
    "Apple Calendar": "webcal://" + host,
}
def fmt(s, e):
    if s == e: return s.strftime("%-d %b %Y")
    if s.year == e.year and s.month == e.month: return f"{s.day}–{e.strftime('%-d %b %Y')}"
    return f"{s.strftime('%-d %b')} – {e.strftime('%-d %b %Y')}"
def meet(r): return (r.get("Meet CopCap") or "").strip() or "CopCap"
def country(r): return (r.get("Country") or "").strip() or "Denmark"
items = "".join(
    f'<tr data-country="{html.escape(country(r))}"><td class="d" data-l="Date"><time>{fmt(s, e)}</time></td>'
    f'<td class="ev" data-l="Event"><a href="{html.escape(r.get("Website") or "#")}" rel="noopener">{html.escape(r["Event"])}</a>'
    f'<span>{html.escape(r.get("Venue") or "")}</span>'
    + (f'<em>{html.escape(r["Date note"])}</em>' if r.get("Date note") else "") + "</td>"
    f'<td class="c" data-l="Country">{html.escape(country(r))}</td>'
    f'<td class="m" data-l="Meet CopCap">{html.escape(meet(r))}</td></tr>'
    for s, e, r in evs) or '<tr><td colspan="4">No upcoming events listed yet.</td></tr>'
countries = sorted({country(r) for _, _, r in evs} | {"Denmark"}, key=lambda c: (c != "Denmark", c == "Online", c))
opts = "".join(f'<option value="{html.escape(c)}"{" selected" if c == "Denmark" else ""}>{html.escape(c)}</option>' for c in countries) + '<option value="">All countries</option>'
btns = "".join(f'<a class="btn" href="{html.escape(v)}">{k}</a>' for k, v in links.items())
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{CAL}</title><link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@500;600&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#090446;--teal:#2B757C;--bg:#fff;--fg:#1b1b2f;--muted:#5d6070;--line:#e4e6ee;--card:#f6f7fb}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d0c1f;--fg:#ecedf5;--muted:#a3a6ba;--line:#26264a;--card:#15143a;--navy:#c9c8ff;--teal:#5fb3ba}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Montserrat,system-ui,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:40px 16px 64px}}h1,h2{{font-family:'IBM Plex Serif',Georgia,serif;color:var(--navy);line-height:1.2}}
h1{{font-size:2rem;margin:0 0 8px}}h2{{font-size:1.25rem;margin:40px 0 12px}}p{{color:var(--muted);margin:0 0 16px}}
.btns{{display:flex;flex-wrap:wrap;gap:8px}}.btn{{background:var(--teal);color:#fff;text-decoration:none;padding:10px 14px;border-radius:8px;font-weight:600;font-size:.9rem}}
.copy{{display:flex;gap:8px;margin-top:12px}}.copy input{{flex:1;min-width:0;padding:9px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit;font-size:.85rem}}
.copy button{{padding:9px 14px;border:1px solid var(--teal);background:none;color:var(--teal);border-radius:8px;font:inherit;font-weight:600;cursor:pointer}}
table{{width:100%;border-collapse:collapse}}th{{text-align:left;font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:600;padding:0 12px 8px 0;border-bottom:2px solid var(--line)}}
td{{vertical-align:top;padding:14px 12px 14px 0;border-top:1px solid var(--line)}}td.d{{width:140px;white-space:nowrap}}td.m{{width:170px;font-size:.88rem}}td.c{{width:110px;font-size:.88rem}}tr[hidden]{{display:none}}
.filter{{display:flex;align-items:center;gap:10px;margin:0 0 14px;font-size:.88rem}}.filter label{{font-weight:600}}.filter select{{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}}#cn{{color:var(--muted)}}
time{{font-weight:600;color:var(--teal);font-size:.9rem}}td a{{color:var(--fg);font-weight:600;text-decoration:none}}td a:hover{{text-decoration:underline}}
td span,td em{{display:block;color:var(--muted);font-size:.88rem}}p.note{{font-size:.85rem;border-left:3px solid var(--teal);padding-left:10px}}footer{{margin-top:40px;font-size:.8rem;color:var(--muted)}}
@media (max-width:600px){{thead{{display:none}}table,tbody,tr,td{{display:block;width:auto}}tr{{border-top:1px solid var(--line);padding:12px 0}}td{{border:0;padding:2px 0}}td.d,td.m,td.c{{width:auto}}td.m::before,td.c::before{{content:attr(data-l) ": ";color:var(--muted)}}tr[hidden]{{display:none}}}}
</style></head><body><main>
<h1>{CAL}</h1>
<p>Upcoming conferences and business events in Copenhagen and Eastern Denmark, curated by Copenhagen Capacity. Every listing is checked against the organiser's own website; please confirm details with the organiser before you travel.</p>
<p class="note">This events calendar is maintained by Copenhagen Capacity through its Copenhagen Synergy AI.</p>
<h2>Upcoming events</h2>
<div class="filter"><label for="cf">Country</label><select id="cf">{opts}</select><span id="cn"></span></div>
<table><thead><tr><th>Date</th><th>Event</th><th>Country</th><th>Meet CopCap</th></tr></thead><tbody>{items}</tbody></table>
<p id="none" hidden>No upcoming events in this country yet.</p>
<script>
(function(){{var sel=document.getElementById('cf'),rows=[].slice.call(document.querySelectorAll('tbody tr[data-country]')),cn=document.getElementById('cn'),none=document.getElementById('none');
function apply(){{var v=sel.value,n=0;rows.forEach(function(r){{var show=!v||r.getAttribute('data-country')===v;r.hidden=!show;if(show)n++;}});cn.textContent=n+(n===1?' event':' events');none.hidden=n>0;}}
sel.addEventListener('change',apply);apply();}})();
</script>
<h2>Add to my calendar</h2>
<p>Subscribe once and new events appear in your calendar automatically.</p>
<div class="btns">{btns}</div>
<div class="copy"><input id="u" readonly value="{html.escape(ics)}" aria-label="Calendar feed URL"><button onclick="navigator.clipboard.writeText(document.getElementById('u').value);this.textContent='Copied'">Copy link</button></div>
<footer>Last updated {today.strftime('%-d %B %Y')}. Copenhagen Capacity · Havneholmen 29, DK-1561 Copenhagen V · <a href="https://www.copcap.com" style="color:inherit">copcap.com</a></footer>
</main></body></html>"""
open(os.path.join(out, "index.html"), "w").write(page)
print(f"{len(evs)} upcoming events written")
