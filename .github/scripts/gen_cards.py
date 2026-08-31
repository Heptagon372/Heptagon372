#!/usr/bin/env python3
"""
Self-hosted GitHub stat cards for the Heptagon372 profile README.

Renders three SVGs into ./assets:
  stats.svg  — headline numbers + heptagon rank ring
  langs.svg  — top languages, stacked bar + legend
  graph.svg  — 12-month contribution area chart

Why this exists: the public github-readme-stats / trophy / activity-graph
instances go down or get quota-paused. This runs on a schedule in the repo's
own Action, so the cards are always up and always on-brand.

Usage:
  GH_TOKEN=... GH_USER=Heptagon372 python gen_cards.py
  python gen_cards.py --mock          # render with sample data, no network
  python gen_cards.py --pending       # neutral "not run yet" cards, no network
"""

import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone

# ----------------------------------------------------------------- palette --
BG = "#0D0718"
STROKE = "#2E1A47"
V_DEEP = "#5B21B6"
V_MID = "#7C3AED"
V_BRIGHT = "#A855F7"
V_LIGHT = "#C4B5FD"
FUCHSIA = "#E879F9"
DIM = "#7E6BA0"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "assets")
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, ".fonts"))
ORB = os.path.join(FONT_DIR, "Orbitron.ttf")
JBM = os.path.join(FONT_DIR, "JetBrainsMono.ttf")

# --------------------------------------------------------------- text→path --
from fontTools.ttLib import TTFont            # noqa: E402
from fontTools.varLib import instancer        # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen   # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402
from fontTools.misc.transform import Transform      # noqa: E402

_CACHE = {}


def _font(path, wght):
    key = (path, wght)
    if key not in _CACHE:
        f = TTFont(path)
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        _CACHE[key] = f
    return _CACHE[key]


def text_path(font_path, text, wght, size, ls=0.0):
    """Baseline at y=0, starts at x=0. Returns (path_d, advance_width)."""
    f = _font(font_path, wght)
    upem = f["head"].unitsPerEm
    scale = size / upem
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    parts, x = [], 0.0
    for ch in str(text):
        gname = cmap.get(ord(ch)) or ".notdef"
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        gs[gname].draw(TransformPen(pen, Transform(scale, 0, 0, -scale, x, 0)))
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += hmtx[gname][0] * scale + ls
    if text:
        x -= ls
    return " ".join(parts), x


def txt(font, s, wght, size, x, y, fill, ls=0.0, anchor="start", opacity=None):
    d, w = text_path(font, s, wght, size, ls)
    if anchor == "end":
        x -= w
    elif anchor == "middle":
        x -= w / 2
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<g transform="translate({x:.2f},{y:.2f})"><path d="{d}" fill="{fill}"{op}/></g>', w


def heptagon_pts(cx, cy, r, rot=-90):
    return " ".join(
        f"{cx + r*math.cos(math.radians(rot + i*360/7)):.2f},"
        f"{cy + r*math.sin(math.radians(rot + i*360/7)):.2f}"
        for i in range(7)
    )


def heptagon_d(cx, cy, r, rot=-90):
    pts = [
        (cx + r * math.cos(math.radians(rot + i * 360 / 7)),
         cy + r * math.sin(math.radians(rot + i * 360 / 7)))
        for i in range(7)
    ]
    d = f"M{pts[0][0]:.2f} {pts[0][1]:.2f}"
    for p in pts[1:]:
        d += f"L{p[0]:.2f} {p[1]:.2f}"
    return d + "Z", 2 * r * math.sin(math.pi / 7) * 7  # path, perimeter


def human(n):
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 10_000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return f"{n:,}"


def card_shell(w, h, uid):
    return (
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="13" fill="{BG}"/>'
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="13" fill="url(#wash{uid})"/>'
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="13" fill="none" '
        f'stroke="{STROKE}"/>'
    )


def defs_common(uid, wash_cx="0.85", wash_cy="0.1"):
    return f'''<defs>
  <radialGradient id="wash{uid}" cx="{wash_cx}" cy="{wash_cy}" r="0.9">
    <stop offset="0%" stop-color="{V_MID}" stop-opacity="0.22"/>
    <stop offset="100%" stop-color="{V_MID}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="ttl{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FFFFFF"/><stop offset="100%" stop-color="{V_LIGHT}"/>
  </linearGradient>
  <linearGradient id="ring{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{FUCHSIA}"/><stop offset="100%" stop-color="{V_MID}"/>
  </linearGradient>
  <linearGradient id="area{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{V_BRIGHT}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{V_BRIGHT}" stop-opacity="0.02"/>
  </linearGradient>
  <linearGradient id="line{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{V_MID}"/><stop offset="55%" stop-color="{V_BRIGHT}"/>
    <stop offset="100%" stop-color="{FUCHSIA}"/>
  </linearGradient>
  <filter id="gl{uid}" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="4"/>
  </filter>
</defs>'''


def card_title(uid, title, sub, x=22, y=36):
    o = []
    p, w = txt(ORB, title, 700, 15, x, y, f"url(#ttl{uid})", ls=1.6)
    g, _ = txt(ORB, title, 700, 15, x, y, V_BRIGHT, ls=1.6, opacity=0.45)
    o.append(f'<g filter="url(#gl{uid})">{g}</g>')
    o.append(p)
    if sub:
        s, _ = txt(JBM, sub, 400, 11, x + w + 10, y, DIM)
        o.append(s)
    return "".join(o)


# ------------------------------------------------------------------ github --
GQL = "https://api.github.com/graphql"

Q_MAIN = """
query($login:String!) {
  user(login:$login) {
    login name createdAt
    followers { totalCount }
    pullRequests(states:MERGED) { totalCount }
    issues { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                 orderBy:{field:STARGAZERS, direction:DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first:12, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

Q_YEAR = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def gql(query, variables, token):
    req = urllib.request.Request(
        GQL,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "heptagon-profile-cards",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        body = json.loads(r.read().decode())
    if "errors" in body:
        raise RuntimeError(json.dumps(body["errors"])[:400])
    return body["data"]


def fetch(user, token):
    main = gql(Q_MAIN, {"login": user}, token)["user"]
    created = datetime.fromisoformat(main["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    stars = sum(n["stargazerCount"] for n in main["repositories"]["nodes"])

    langs = {}
    for n in main["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            nm = e["node"]["name"]
            if nm not in langs:
                langs[nm] = {"size": 0, "color": e["node"]["color"] or "#8B5CF6"}
            langs[nm]["size"] += e["size"]

    commits = prs = issues = contrib_repos = 0
    calendar = []          # (date, count) for the trailing 12 months
    all_days = {}          # date -> count, every year since the account was created
    for year in range(created.year, now.year + 1):
        frm = max(created, datetime(year, 1, 1, tzinfo=timezone.utc))
        to = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        if frm >= to:
            continue
        c = gql(Q_YEAR, {"login": user, "from": frm.isoformat(), "to": to.isoformat()},
                token)["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        prs += c["totalPullRequestContributions"]
        issues += c["totalIssueContributions"]
        contrib_repos = max(contrib_repos, c["totalRepositoriesWithContributedCommits"])
        for wk in c["contributionCalendar"]["weeks"]:
            for dd in wk["contributionDays"]:
                if dd["date"][:4] == str(year):
                    all_days[dd["date"]] = dd["contributionCount"]

    cal = gql(Q_YEAR, {"login": user,
                       "from": datetime(now.year - 1, now.month, min(now.day, 28),
                                        tzinfo=timezone.utc).isoformat(),
                       "to": now.isoformat()},
              token)["user"]["contributionsCollection"]["contributionCalendar"]
    for wk in cal["weeks"]:
        for d in wk["contributionDays"]:
            calendar.append((d["date"], d["contributionCount"]))

    return {
        "user": main["login"],
        "name": main["name"] or main["login"],
        "stars": stars,
        "commits": commits,
        "prs": max(prs, main["pullRequests"]["totalCount"]),
        "issues": max(issues, main["issues"]["totalCount"]),
        "repos": main["repositories"]["totalCount"],
        "contributed": contrib_repos,
        "followers": main["followers"]["totalCount"],
        "year_total": cal["totalContributions"],
        "langs": langs,
        "calendar": calendar,
        "streak": streaks(all_days),
    }


def streaks(days):
    """days: {'YYYY-MM-DD': count}. Returns totals plus current/longest streaks."""
    from datetime import date, timedelta
    if not days:
        today = datetime.now(timezone.utc).date().isoformat()
        return {"total": 0, "since": today,
                "current": 0, "current_from": today, "current_to": today,
                "longest": 0, "longest_from": today, "longest_to": today}

    keys = sorted(days)
    start = date.fromisoformat(keys[0])
    end = date.fromisoformat(keys[-1])

    best = cur = 0
    best_end = cur_end = None
    d = start
    while d <= end:
        if days.get(d.isoformat(), 0) > 0:
            cur += 1
            cur_end = d
            if cur > best:
                best, best_end = cur, cur_end
        else:
            cur, cur_end = 0, None
        d += timedelta(days=1)

    # a streak stays alive while today still has time left on the clock
    today = datetime.now(timezone.utc).date()
    if cur and cur_end and (today - cur_end).days > 1:
        cur, cur_end = 0, None
    if cur == 0:
        cur_from = cur_to = today
    else:
        cur_to = cur_end
        cur_from = cur_end - timedelta(days=cur - 1)

    if best and best_end:
        best_from, best_to = best_end - timedelta(days=best - 1), best_end
    else:
        best_from = best_to = today

    return {
        "total": sum(days.values()),
        "since": start.isoformat(),
        "current": cur,
        "current_from": cur_from.isoformat(), "current_to": cur_to.isoformat(),
        "longest": best,
        "longest_from": best_from.isoformat(), "longest_to": best_to.isoformat(),
    }


def mock():
    import random
    random.seed(7)
    now = datetime.now(timezone.utc)
    cal = []
    for i in range(371):
        d = now.timestamp() - (370 - i) * 86400
        base = 0 if random.random() < 0.28 else random.randint(1, 9)
        if random.random() < 0.06:
            base += random.randint(6, 20)
        cal.append((datetime.fromtimestamp(d, timezone.utc).strftime("%Y-%m-%d"), base))
    return {
        "user": "Heptagon372", "name": "Yoon Seungho",
        "stars": 34, "commits": 1487, "prs": 62, "issues": 28,
        "repos": 10, "contributed": 9, "followers": 1,
        "year_total": sum(c for _, c in cal),
        "streak": streaks({ds: c for ds, c in cal}),
        "langs": {
            "TypeScript": {"size": 512000, "color": "#3178c6"},
            "Python": {"size": 388000, "color": "#3572A5"},
            "JavaScript": {"size": 141000, "color": "#f1e05a"},
            "CSS": {"size": 96000, "color": "#663399"},
            "HTML": {"size": 58000, "color": "#e34c26"},
            "Shell": {"size": 21000, "color": "#89e051"},
            "PLpgSQL": {"size": 12000, "color": "#336790"},
        },
        "calendar": cal,
    }


# ------------------------------------------------------------------- cards --
def fmt(d, n):
    """Cards committed before the first Action run must not show invented numbers."""
    return "—" if d.get("pending") else human(n)


NOTE = "awaiting first Action run"


def pending():
    """Neutral placeholders, committed so the repo never ships fabricated stats.
    The scheduled workflow overwrites these on its first run."""
    return {
        "user": os.environ.get("GH_USER", "Heptagon372"), "name": "",
        "stars": 0, "commits": 0, "prs": 0, "issues": 0, "repos": 0,
        "contributed": 0, "followers": 0, "year_total": 0,
        "langs": {}, "calendar": [], "pending": True,
        "streak": {"total": 0, "since": "", "current": 0, "current_from": "",
                   "current_to": "", "longest": 0, "longest_from": "",
                   "longest_to": ""},
    }


def rank_of(d):
    """Small, transparent score → letter + ring fill fraction."""
    score = (
        min(d["commits"] / 2000, 1) * 0.42
        + min(d["prs"] / 120, 1) * 0.16
        + min(d["issues"] / 100, 1) * 0.10
        + min(d["stars"] / 200, 1) * 0.18
        + min(d["contributed"] / 30, 1) * 0.08
        + min(d["followers"] / 100, 1) * 0.06
    )
    for cut, letter in ((0.88, "S"), (0.72, "A+"), (0.56, "A"),
                        (0.40, "B+"), (0.24, "B"), (0.0, "C")):
        if score >= cut:
            return letter, max(score, 0.08)
    return "C", 0.08


def card_stats(d):
    W, H = 500, 212
    uid = "s"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" fill="none" role="img" aria-label="GitHub stats for {d["user"]}">',
         defs_common(uid), card_shell(W, H, uid),
         card_title(uid, "GITHUB STATS", f"@{d['user']}")]

    rows = [
        ("Total Stars Earned", d["stars"]),
        ("Total Commits", d["commits"]),
        ("Total PRs", d["prs"]),
        ("Total Issues", d["issues"]),
        ("Contributed To", d["contributed"]),
        ("Followers", d["followers"]),
    ]
    y = 66
    for i, (label, val) in enumerate(rows):
        o.append(f'<polygon points="{heptagon_pts(28, y - 4, 4.5)}" fill="none" '
                 f'stroke="{FUCHSIA}" stroke-opacity="0.85" stroke-width="1.2"/>')
        p, _ = txt(JBM, label, 400, 12, 42, y, V_LIGHT, opacity=0.9)
        o.append(p)
        v, _ = txt(ORB, fmt(d, val), 700, 13, 336, y, FUCHSIA, anchor="end", ls=0.5)
        o.append(v)
        if i < len(rows) - 1:
            o.append(f'<path d="M42 {y+7}H336" stroke="{STROKE}" stroke-opacity="0.8" '
                     f'stroke-dasharray="1 5"/>')
        y += 23

    # heptagon rank ring
    letter, frac = ("—", 0.0) if d.get("pending") else rank_of(d)
    cx, cy, r = 412, 118, 52
    dpath, perim = heptagon_d(cx, cy, r)
    o.append(f'<path d="{dpath}" fill="none" stroke="{STROKE}" stroke-width="7" '
             f'stroke-linejoin="round"/>')
    o.append(f'<path d="{dpath}" fill="none" stroke="url(#ring{uid})" stroke-width="7" '
             f'stroke-linejoin="round" stroke-linecap="round" '
             f'stroke-dasharray="{perim*frac:.1f} {perim:.1f}" opacity="0.55" '
             f'filter="url(#gl{uid})"/>')
    o.append(f'<path d="{dpath}" fill="none" stroke="url(#ring{uid})" stroke-width="4.5" '
             f'stroke-linejoin="round" stroke-linecap="round" '
             f'stroke-dasharray="{perim*frac:.1f} {perim:.1f}">'
             f'<animate attributeName="stroke-dashoffset" from="{perim:.1f}" to="0" '
             f'dur="1.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.3 1" '
             f'keyTimes="0;1" values="{perim:.1f};0"/></path>')
    p, _ = txt(ORB, letter, 800, 34, cx, cy + 6, "url(#ttl" + uid + ")", anchor="middle", ls=1)
    g, _ = txt(ORB, letter, 800, 34, cx, cy + 6, V_BRIGHT, anchor="middle", ls=1, opacity=0.5)
    o.append(f'<g filter="url(#gl{uid})">{g}</g>')
    o.append(p)
    lp, _ = txt(JBM, "RANK", 500, 9, cx, cy + 24, DIM, anchor="middle", ls=1.6)
    o.append(lp)

    stamp = (NOTE if d.get("pending")
             else datetime.now(timezone.utc).strftime("updated %Y-%m-%d"))
    sp, _ = txt(JBM, stamp, 400, 9, W - 20, H - 14, DIM, anchor="end")
    o.append(sp)
    o.append("</svg>")
    return "\n".join(o)


def card_langs(d, top=7):
    W, H = 380, 212
    uid = "l"
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1]["size"])[:top]
    total = sum(v["size"] for _, v in items) or 1

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" fill="none" role="img" aria-label="Top languages">',
         defs_common(uid, "0.1", "0.05"), card_shell(W, H, uid),
         card_title(uid, "TOP LANGUAGES", None)]

    # stacked bar
    bx, by, bw, bh = 22, 56, W - 44, 11
    o.append(f'<clipPath id="barclip"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
             f'rx="{bh/2}"/></clipPath>')
    o.append(f'<g clip-path="url(#barclip)">')
    x = bx
    for name, v in items:
        seg = bw * v["size"] / total
        o.append(f'<rect x="{x:.2f}" y="{by}" width="{seg+0.7:.2f}" height="{bh}" '
                 f'fill="{v["color"]}"/>')
        x += seg
    o.append(f'<rect x="{x:.2f}" y="{by}" width="{max(bx+bw-x,0):.2f}" height="{bh}" '
             f'fill="{STROKE}"/>')
    o.append('</g>')
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh/2}" fill="none" '
             f'stroke="{BG}" stroke-opacity="0.6"/>')

    if not items:
        note, _ = txt(JBM, NOTE, 400, 11, W / 2, 108, DIM, anchor="middle")
        o.append(note)
        o.append("</svg>")
        return "\n".join(o)

    # legend, two columns
    col_x = [22, 200]
    y0 = 96
    for i, (name, v) in enumerate(items):
        cx_ = col_x[i % 2]
        yy = y0 + (i // 2) * 25
        o.append(f'<circle cx="{cx_+5}" cy="{yy-4}" r="5" fill="{v["color"]}"/>')
        nm = name if len(name) <= 13 else name[:12] + "…"
        p, _ = txt(JBM, nm, 500, 11.5, cx_ + 17, yy, V_LIGHT, opacity=0.92)
        o.append(p)
        pct = 100 * v["size"] / total
        pp, _ = txt(ORB, f"{pct:.1f}%", 600, 10.5, cx_ + 156, yy, FUCHSIA, anchor="end")
        o.append(pp)

    o.append("</svg>")
    return "\n".join(o)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def pretty_date(iso):
    y, m, dd = iso.split("-")
    return f"{MONTHS[int(m)-1]} {int(dd)}, {y}"


def card_streak(d):
    W, H = 900, 190
    uid = "k"
    s = d["streak"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" fill="none" role="img" aria-label="Contribution streak">',
         defs_common(uid, "0.5", "0.0"), card_shell(W, H, uid)]

    # dividers
    for x in (300, 600):
        o.append(f'<path d="M{x} 34V{H-34}" stroke="{V_MID}" stroke-opacity="0.45" stroke-dasharray="2 6"/>')

    def panel(cx, big, label, sub):
        g = []
        p, _ = txt(ORB, big, 800, 31, cx, 92, FUCHSIA, anchor="middle", ls=1)
        gl, _ = txt(ORB, big, 800, 31, cx, 92, V_BRIGHT, anchor="middle", ls=1, opacity=0.45)
        g.append(f'<g filter="url(#gl{uid})">{gl}</g>')
        g.append(p)
        lp, _ = txt(JBM, label, 600, 12, cx, 120, V_LIGHT, anchor="middle", opacity=0.92)
        g.append(lp)
        sp, _ = txt(JBM, sub, 400, 9.5, cx, 140, DIM, anchor="middle")
        g.append(sp)
        return "".join(g)

    # left — total contributions
    o.append(panel(150, fmt(d, s["total"]), "Total Contributions",
                   NOTE if d.get("pending") else f'{pretty_date(s["since"])} — Present'))

    # centre — current streak, inside a heptagon ring with a flame
    cx, cy, r = 450, 78, 50
    dpath, perim = heptagon_d(cx, cy, r)
    o.append(f'<path d="{dpath}" fill="none" stroke="{STROKE}" stroke-width="6" '
             f'stroke-linejoin="round"/>')
    o.append(f'<path d="{dpath}" fill="none" stroke="url(#ring{uid})" stroke-width="6" '
             f'stroke-linejoin="round" opacity="0.45" filter="url(#gl{uid})"/>')
    o.append(f'<path d="{dpath}" fill="none" stroke="url(#ring{uid})" stroke-width="3" '
             f'stroke-linejoin="round" stroke-dasharray="{perim:.1f}">'
             f'<animate attributeName="stroke-dashoffset" values="{perim:.1f};0" dur="1.6s" '
             f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.3 1" keyTimes="0;1"/>'
             f'</path>')
    # flame sitting on the top vertex
    flame = ("M1.5 -17 C 1.5 -10.5 8 -7.5 8.6 -0.5 C 9.3 7.5 4.5 14 -0.8 14 "
             "C -6.6 14 -10.2 8.2 -9.4 1.8 C -8.7 -2.8 -5.2 -4.2 -4.6 -9 "
             "C -2.2 -6.2 -0.4 -10.4 1.5 -17 Z")
    inner = ("M1 -6.5 C 1 -3 4.2 -1.6 4.4 2 C 4.7 6.6 2.2 9.8 -0.5 9.8 "
             "C -3.6 9.8 -5.4 7 -5 3.6 C -4.6 1.2 -2.6 0.4 -2.2 -2.2 "
             "C -1.1 -0.8 -0.2 -3.2 1 -6.5 Z")
    o.append(f'<g transform="translate({cx},{cy-r})">'
             f'<circle r="17" fill="{BG}"/>'
             f'<path d="{flame}" fill="{FUCHSIA}" opacity="0.30" filter="url(#gl{uid})"/>'
             f'<path d="{flame}" fill="url(#ring{uid})"/>'
             f'<path d="{inner}" fill="#FFE8FF" opacity="0.85">'
             f'<animate attributeName="opacity" values="0.55;0.95;0.55" dur="2.2s" '
             f'repeatCount="indefinite"/></path></g>')
    cur = fmt(d, s["current"])
    np_, _ = txt(ORB, cur, 800, 30, cx, cy + 12, "#FFFFFF", anchor="middle", ls=1)
    ng, _ = txt(ORB, cur, 800, 30, cx, cy + 12, V_BRIGHT, anchor="middle",
                ls=1, opacity=0.55)
    o.append(f'<g filter="url(#gl{uid})">{ng}</g>')
    o.append(np_)
    lp, _ = txt(JBM, "Current Streak", 600, 12, cx, 148, V_LIGHT, anchor="middle", opacity=0.92)
    o.append(lp)
    if d.get("pending"):
        rng = NOTE
    elif s["current"]:
        rng = f'{pretty_date(s["current_from"])} — {pretty_date(s["current_to"])}'
    else:
        rng = "no active streak"
    sp, _ = txt(JBM, rng, 400, 9.5, cx, 166, DIM, anchor="middle")
    o.append(sp)

    # right — longest streak
    o.append(panel(750, fmt(d, s["longest"]), "Longest Streak",
                   NOTE if d.get("pending") else
                   (f'{pretty_date(s["longest_from"])} — {pretty_date(s["longest_to"])}'
                    if s["longest"] else "—")))

    o.append("</svg>")
    return "\n".join(o)


def card_graph(d):
    W, H = 900, 250
    uid = "g"
    cal = d["calendar"]
    if not cal:
        today = datetime.now(timezone.utc)
        cal = [((today.replace(day=1)).strftime("%Y-%m-%d"), 0)] * 14

    # weekly buckets keep the line readable
    weeks = [cal[i:i + 7] for i in range(0, len(cal), 7)]
    series = [(w[0][0], sum(c for _, c in w)) for w in weeks if w]
    vals = [v for _, v in series]
    vmax = max(max(vals), 1)

    pad_l, pad_r, pad_t, pad_b = 46, 22, 74, 44
    pw, ph = W - pad_l - pad_r, H - pad_t - pad_b

    def px(i):
        return pad_l + (pw * i / max(len(series) - 1, 1))

    def py(v):
        return pad_t + ph - (ph * v / vmax)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" fill="none" role="img" aria-label="Contribution activity">',
         defs_common(uid, "0.5", "0.0"), card_shell(W, H, uid),
         card_title(uid, "CONTRIBUTION ACTIVITY", "// last 12 months, weekly")]

    tot, _ = txt(ORB, fmt(d, d["year_total"]), 800, 20, W - 22, 40, FUCHSIA,
                 anchor="end", ls=0.5)
    o.append(tot)
    tl, _ = txt(JBM, "contributions", 400, 10, W - 22, 54, DIM, anchor="end")
    o.append(tl)

    if d.get("pending"):
        note, _ = txt(JBM, NOTE, 400, 11, W / 2, pad_t + ph / 2, DIM, anchor="middle")
        o.append(note)
        o.append("</svg>")
        return "\n".join(o)

    # gridlines
    for k in range(4):
        gy = pad_t + ph * k / 3
        o.append(f'<path d="M{pad_l} {gy:.1f}H{pad_l+pw}" stroke="{STROKE}" '
                 f'stroke-opacity="0.9" stroke-dasharray="2 6"/>')
        lab, _ = txt(JBM, human(round(vmax * (3 - k) / 3)), 400, 9,
                     pad_l - 8, gy + 3, DIM, anchor="end")
        o.append(lab)

    pts = [(px(i), py(v)) for i, (_, v) in enumerate(series)]
    line = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.2f} {pad_t+ph} L{pts[0][0]:.2f} {pad_t+ph} Z"
    o.append(f'<path d="{area}" fill="url(#area{uid})"/>')
    o.append(f'<path d="{line}" stroke="url(#line{uid})" stroke-width="4" fill="none" '
             f'stroke-linejoin="round" stroke-linecap="round" opacity="0.5" '
             f'filter="url(#gl{uid})"/>')
    o.append(f'<path d="{line}" stroke="url(#line{uid})" stroke-width="2.2" fill="none" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')

    # peak marker
    pi = vals.index(max(vals))
    o.append(f'<circle cx="{pts[pi][0]:.2f}" cy="{pts[pi][1]:.2f}" r="8" fill="{FUCHSIA}" '
             f'opacity="0.25" filter="url(#gl{uid})"/>')
    o.append(f'<circle cx="{pts[pi][0]:.2f}" cy="{pts[pi][1]:.2f}" r="3.6" fill="{FUCHSIA}" '
             f'stroke="{BG}" stroke-width="1.5"><animate attributeName="r" '
             f'values="3.2;5;3.2" dur="2.6s" repeatCount="indefinite"/></circle>')

    # month ticks — first week of each month, dropped when it would crowd its neighbour
    seen, last_x = set(), -1e9
    for i, (ds, _) in enumerate(series):
        m = int(ds[5:7])
        if m in seen:
            continue
        seen.add(m)
        x = px(i)
        if x - last_x < 46 or x > pad_l + pw - 14:
            continue
        last_x = x
        lab, _ = txt(JBM, MONTHS[m - 1], 400, 9.5, x, H - 20, DIM, anchor="middle")
        o.append(lab)
        o.append(f'<path d="M{x:.2f} {pad_t+ph}v5" stroke="{STROKE}"/>')

    o.append("</svg>")
    return "\n".join(o)


# -------------------------------------------------------------------- main --
def main():
    if "--pending" in sys.argv:
        d = pending()
    elif "--mock" in sys.argv:
        d = mock()
    else:
        token = os.environ.get("GH_TOKEN")
        user = os.environ.get("GH_USER")
        if not token or not user:
            sys.exit("GH_TOKEN and GH_USER are required (or pass --mock)")
        d = fetch(user, token)

    os.makedirs(ASSETS, exist_ok=True)
    for name, svg in (("stats.svg", card_stats(d)),
                      ("langs.svg", card_langs(d)),
                      ("streak.svg", card_streak(d)),
                      ("graph.svg", card_graph(d))):
        with open(os.path.join(ASSETS, name), "w") as f:
            f.write(svg)
        print(f"wrote assets/{name}  ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
