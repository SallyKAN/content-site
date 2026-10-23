#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用内容站渲染器 —— markdown 日报 -> 静态 HTML（Cloudflare Pages 就绪）"""
import os, re, glob, shutil, datetime, html as _html
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")

# ---------------- 源配置：加新专栏只改这里 ----------------
SOURCES = [
    {
        "id": "dev",
        "name": "每日独立开发精选",
        "icon": "🧰",
        "desc": "Hacker News / Product Hunt / Reddit / SomebodyMakeThis 每日精选",
        "pattern": os.path.expanduser("~/clawd/memory/daily-digest-*.md"),
        "date_re": r"daily-digest-(\d{4})-(\d{2})-(\d{2})",
        "date_mode": "ymd",
    },
    {
        "id": "topic",
        "name": "选题日报",
        "icon": "✍️",
        "desc": "AI 热点选题方案与晚间推送",
        "pattern": os.path.expanduser("~/BusinessContent/01-选题管理/[0-9][0-9][0-9][0-9]-*.md"),
        "date_re": r"/(\d{2})(\d{2})-(.+)\.md$",
        "date_mode": "md",
    },
]

CSS = """
:root{--bg:#fafaf9;--fg:#1c1917;--muted:#78716c;--line:#e7e5e4;--card:#fff;--accent:#2563eb;--accent-soft:#eff6ff}
@media(prefers-color-scheme:dark){:root{--bg:#0c0a09;--fg:#e7e5e4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#60a5fa;--accent-soft:#172554}}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;-webkit-text-size-adjust:100%}
.wrap{max-width:760px;margin:0 auto;padding:0 18px}
header{padding:22px 0 14px;border-bottom:1px solid var(--line);margin-bottom:26px}
header a{color:var(--fg);text-decoration:none;font-weight:700;font-size:18px;letter-spacing:-.01em}
nav.sub{margin-top:8px;display:flex;gap:14px;flex-wrap:wrap;font-size:13px}
nav.sub a{color:var(--muted);text-decoration:none;padding:3px 9px;border-radius:999px}
nav.sub a.on{background:var(--accent-soft);color:var(--accent);font-weight:600}
article{padding-bottom:60px}
article h1{font-size:26px;line-height:1.35;margin:6px 0 4px;letter-spacing:-.02em}
.meta{color:var(--muted);font-size:13px;margin-bottom:24px}
article h2{font-size:19px;margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line);letter-spacing:-.01em}
article h3{font-size:16px;margin:24px 0 10px}
article p{margin:12px 0}
article a{color:var(--accent);text-decoration:none;word-break:break-all}
article a:hover{text-decoration:underline}
article ul,article ol{margin:12px 0 12px 22px}
article li{margin:6px 0}
article blockquote{border-left:3px solid var(--accent);background:var(--card);padding:10px 14px;margin:16px 0;color:var(--muted);font-size:14px;border-radius:0 6px 6px 0}
article code{background:var(--card);border:1px solid var(--line);padding:1px 5px;border-radius:4px;font-size:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
article pre{background:var(--card);border:1px solid var(--line);padding:14px;border-radius:8px;overflow-x:auto;margin:16px 0;font-size:13px}
article pre code{border:0;padding:0;background:none}
.tw{overflow-x:auto;margin:16px 0;-webkit-overflow-scrolling:touch}
article table{border-collapse:collapse;width:100%;font-size:14px;min-width:420px}
article th,article td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
article th{background:var(--card);font-weight:600}
article hr{border:0;border-top:1px solid var(--line);margin:28px 0}
article img{max-width:100%;height:auto;border-radius:8px}
.pager{display:flex;justify-content:space-between;gap:12px;margin:36px 0 0;padding-top:20px;border-top:1px solid var(--line);font-size:14px}
.pager a{color:var(--accent);text-decoration:none;max-width:48%}
.pager .r{text-align:right;margin-left:auto}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px 17px;margin:11px 0;text-decoration:none;color:var(--fg);transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.card .d{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.card .t{font-weight:600;margin:5px 0 3px;font-size:15px;line-height:1.5}
.card .p{font-size:13px;color:var(--muted);line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.hub h1{font-size:24px;margin-bottom:8px}
.hubgrid{display:grid;gap:14px;margin:22px 0}
.hubcard{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;text-decoration:none;color:var(--fg);display:block;transition:.15s}
.hubcard:hover{border-color:var(--accent)}
.hubcard .ic{font-size:24px}
.hubcard .n{font-weight:700;margin:9px 0 5px;font-size:17px}
.hubcard .s{color:var(--muted);font-size:13px;line-height:1.6}
.hubcard .c{margin-top:11px;font-size:12px;color:var(--accent);font-weight:600}
#q{width:100%;padding:11px 15px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg);font-size:15px;margin:16px 0;outline:none}
#q:focus{border-color:var(--accent)}
footer{color:var(--muted);font-size:12px;text-align:center;padding:34px 0 40px;border-top:1px solid var(--line);margin-top:40px}
"""

SEARCH_JS = """
<script>
(function(){var q=document.getElementById('q');if(!q)return;
q.addEventListener('input',function(){var v=this.value.trim().toLowerCase();
var cs=document.querySelectorAll('.card');
cs.forEach(function(c){if(!v){c.style.display='';return;}
var t=(c.dataset.s||'').toLowerCase();
c.style.display=t.indexOf(v)>=0?'':'none';});});})();
</script>
"""


def page(title, body, cls="", nav="", extra=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{_html.escape(title)}</title>
<meta name="color-scheme" content="light dark">
<style>{CSS}</style>
</head><body class="{cls}">
<div class="wrap">
<header>
<a href="{{ROOT}}index.html">📚 Snape 的内容站</a>
<nav class="sub">{nav}</nav>
</header>
{body}
<footer>自动生成 · {datetime.date.today().isoformat()}</footer>
</div>{extra}
</body></html>"""


def extract_title(md_text, fallback):
    for line in md_text.split("\n")[:8]:
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def extract_summary(md_text):
    """取正文第一段有实质内容的文字作为摘要"""
    for line in md_text.split("\n"):
        s = line.strip()
        if not s or s.startswith(("#", ">", "---", "|", "!", "-", "*")) or s.startswith("http"):
            continue
        s = re.sub(r"[`*_\[\]]|\(http[^)]*\)", "", s).strip()
        if len(s) > 20:
            return s[:120]
    return ""


URL_RE = re.compile(r'(?<![="\'>])(https?://[^\s<>"\u3000-\u303f\uff00-\uffef)]+)')


def linkify_raw(html_text):
    """把正文里裸露的 URL 转成可点击链接（跳过已有 <a> 标签内的）"""
    parts = re.split(r'(<a\b[^>]*>.*?</a>)', html_text, flags=re.S | re.I)
    out = []
    for seg in parts:
        if re.match(r'<a\b', seg, re.I):
            out.append(seg)          # 已是链接，原样保留
            continue
        def rep(m):
            u = m.group(1).rstrip('.,;:!?)')
            tail = m.group(1)[len(u):]
            return f'<a href="{u}" target="_blank" rel="noopener">{u}</a>{tail}'
        out.append(URL_RE.sub(rep, seg))
    return "".join(out)


def collect(src):
    """收集某个源的所有文件 -> [{date, path, title, summary}]"""
    items = []
    for path in sorted(glob.glob(src["pattern"])):
        name = os.path.basename(path)
        m = re.search(src["date_re"], path)
        if not m:
            continue
        if src["date_mode"] == "ymd":
            y, mo, d = m.group(1), m.group(2), m.group(3)
            date = f"{y}-{mo}-{d}"
            sub = ""
        else:  # mmdd
            mo, d = m.group(1), m.group(2)
            y = "2026"
            date = f"{y}-{mo}-{d}"
            sub = m.group(3)
        try:
            raw = open(path, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        fb = date + (" " + sub if sub else "")
        items.append({
            "date": date, "sub": sub, "path": path,
            "title": extract_title(raw, fb),
            "summary": extract_summary(raw),
            "raw": raw,
            "_upd": sub.endswith("-更新"),
            "_key": (date, re.sub(r"-更新$", "", sub)),
        })

    # --- 合并同日期同主题的「原版」与「-更新」版 ---
    merged = {}
    order = []
    for it in items:
        k = it["_key"]
        if k not in merged:
            merged[k] = it
            order.append(k)
        else:
            keep = merged[k]
            keep["raw"] = merge_two(keep["path"], it["path"])
            keep["sub"] = re.sub(r"-更新$", "", keep["sub"])
            keep["title"] = extract_title(keep["raw"], keep["date"])
            keep["summary"] = extract_summary(keep["raw"])

    items = [merged[k] for k in order]
    items.sort(key=lambda x: (x["date"], x["sub"]), reverse=True)
    return items


def merge_two(p_orig, p_upd):
    """把原版与更新版合并成一个 markdown 文档，保留两版各自独有的内容"""
    import difflib
    a = open(p_orig, encoding="utf-8", errors="ignore").read()
    b = open(p_upd, encoding="utf-8", errors="ignore").read()
    if a.strip() == b.strip():
        return a
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if ratio > 0.9:  # 几乎相同，取更长的
        return a if len(a) >= len(b) else b
    # 主体用较全的那版，另一版作为「更新版补充」附在后面
    main, extra = (a, b) if len(a) >= len(b) else (b, a)
    tag = "更新版补充" if main is a else "原始版本补充"
    main = re.sub(r"^# .*$", "", main, count=1, flags=re.M).strip()
    extra = re.sub(r"^# .*$", "", extra, count=1, flags=re.M).strip()
    return (main + "\n\n---\n\n## 📎 " + tag + "\n\n" + extra).strip()


def render_items(src, items):
    d = os.path.join(OUT, src["id"])
    os.makedirs(d, exist_ok=True)
    md = markdown.Markdown(extensions=["extra", "sane_lists", "nl2br"])
    for i, it in enumerate(items):
        md.reset()
        body = md.convert(it["raw"])
        body = linkify_raw(body)
        body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
        nav_prev = nav_next = ""
        if i + 1 < len(items):  # 更旧
            o = items[i + 1]
            nav_next = f'<a class="l" href="{slug(o)}">← {o["date"]}{" " + o["sub"] if o["sub"] else ""}</a>'
        if i > 0:  # 更新
            o = items[i - 1]
            nav_prev = f'<a class="r" href="{slug(o)}">{o["date"]}{" " + o["sub"] if o["sub"] else ""} →</a>'
        body = (f'<article><div class="meta">{it["date"]}</div>{body}'
                f'<div class="pager">{nav_next}{nav_prev}</div></article>')
        p = page(it["title"], body, nav=sub_nav(src), extra="")
        p = p.replace("{ROOT}", "../")
        open(os.path.join(d, slug(it)), "w", encoding="utf-8").write(p)

    # 专栏列表页
    cards = []
    for it in items:
        label = it["date"] + (" · " + it["sub"] if it["sub"] else "")
        cards.append(
            f'<a class="card" href="{slug(it)}" data-s="{_html.escape(it["title"] + " " + label + " " + it["summary"])}">'
            f'<div class="d">{label}</div><div class="t">{_html.escape(it["title"])}</div>'
            f'<div class="p">{_html.escape(it["summary"])}</div></a>')
    body = (f'<h1>{src["icon"]} {src["name"]}</h1>'
            f'<div class="meta">{src["desc"]} · 共 {len(items)} 篇</div>'
            f'<input id="q" type="search" placeholder="🔍 搜索标题或内容…">'
            f'<div id="list">{"".join(cards) or "<p>暂无内容</p>"}</div>')
    p = page(src["name"], body, nav=sub_nav(src), extra=SEARCH_JS).replace("{ROOT}", "../")
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(p)
    return len(items)


def slug(it):
    return it["date"] + ("-" + it["sub"] if it["sub"] else "") + ".html"


def sub_nav(cur):
    out = ['<a href="/index.html">全部</a>']
    for s in SOURCES:
        on = "on" if s["id"] == cur["id"] else ""
        out.append(f'<a class="{on}" href="/{s["id"]}/index.html">{s["icon"]} {s["name"]}</a>')
    return "".join(out)


def build_hub(all_items):
    cards = []
    for s in SOURCES:
        its = all_items.get(s["id"], [])
        latest = its[0]["date"] if its else "—"
        cards.append(
            f'<a class="hubcard" href="/{s["id"]}/index.html">'
            f'<div class="ic">{s["icon"]}</div>'
            f'<div class="n">{s["name"]}</div>'
            f'<div class="s">{s["desc"]}</div>'
            f'<div class="c">{len(its)} 篇 · 最近 {latest} →</div></a>')
    recent = []
    for s in SOURCES:
        for it in all_items.get(s["id"], [])[:3]:
            label = it["date"] + (" · " + it["sub"] if it["sub"] else "")
            recent.append(
                f'<a class="card" href="/{s["id"]}/{slug(it)}" data-s="{_html.escape(it["title"])}">'
                f'<div class="d">{s["icon"]} {s["name"]} · {label}</div>'
                f'<div class="t">{_html.escape(it["title"])}</div></a>')
    body = (f'<div class="hub"><h1>📚 内容站</h1>'
            f'<div class="meta">每日自动归档</div>'
            f'<div class="hubgrid">{"".join(cards)}</div>'
            f'<h2 style="font-size:18px;margin:28px 0 12px">最近更新</h2>'
            f'{"".join(recent)}</div>')
    p = page("Snape 的内容站", body).replace("{ROOT}", "")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(p)
    # CF Pages 404 回退
    shutil.copy(os.path.join(OUT, "index.html"), os.path.join(OUT, "404.html"))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    all_items = {}
    for src in SOURCES:
        items = collect(src)
        n = render_items(src, items)
        all_items[src["id"]] = items
        print(f"  {src['icon']} {src['name']}: {n} 篇")
    build_hub(all_items)
    print(f"  ✅ 输出目录: {OUT}")


if __name__ == "__main__":
    main()
