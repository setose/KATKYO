#!/usr/bin/env python3
"""index.html をフォルダ構成から自動生成するスクリプト。

使い方:
    python build_index.py

新しい教材(.htmlファイル)を追加・削除・リネームしたら、このスクリプトを
実行するだけで index.html が最新の状態に更新されます。index.html を
手動で編集する必要はありません。
"""
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent

# トップレベルの教科フォルダの表示順。ここに無い教科フォルダが増えたら
# 自動的に末尾（五十音順）に追加されます。
SUBJECT_ORDER = ["中学数学", "高校数学", "高校物理", "高校古文"]

EXCLUDE_DIRS = {".git", ".github"}


def extract_title(html_path: Path) -> str:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<title>(.*?)</title>", text, re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return html_path.stem


def collect_subjects():
    subjects = {}
    for entry in ROOT.iterdir():
        if not entry.is_dir() or entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        html_files = sorted(entry.rglob("*.html"))
        if not html_files:
            continue
        cards = []
        for f in html_files:
            rel = f.relative_to(ROOT)
            sub_rel = f.relative_to(entry)
            folder_parts = sub_rel.parts[:-1]  # 教科フォルダより下の階層
            cards.append({
                "href": str(rel).replace("\\", "/"),
                "title": extract_title(f),
                "folder": "・".join(folder_parts) if folder_parts else None,
            })
        subjects[entry.name] = cards
    return subjects


def ordered_subject_names(subjects):
    known = [s for s in SUBJECT_ORDER if s in subjects]
    rest = sorted(s for s in subjects if s not in SUBJECT_ORDER)
    return known + rest


def render_card(card: dict) -> str:
    folder_html = f'\n        <span class="folder">{card["folder"]}</span>' if card["folder"] else ""
    return (
        f'      <a class="card" href="{card["href"]}">\n'
        f'        <span class="title">{card["title"]}</span>{folder_html}\n'
        f'      </a>'
    )


def render_section(name: str, cards: list) -> str:
    cards_html = "\n".join(render_card(c) for c in cards)
    return (
        f'  <section class="subject">\n'
        f'    <h2>{name}</h2>\n'
        f'    <div class="card-grid">\n'
        f'{cards_html}\n'
        f'    </div>\n'
        f'  </section>'
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>家庭教師 学習教材まとめ</title>
<style>
  :root {{
    --bg: #f5f6fa;
    --card-bg: #ffffff;
    --text: #2d3142;
    --muted: #6b7280;
    --accent: #3b82f6;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}
  header {{
    padding: 2.5rem 1.5rem 1.5rem;
    text-align: center;
  }}
  header h1 {{
    margin: 0 0 0.5rem;
    font-size: 1.8rem;
  }}
  header p {{
    margin: 0;
    color: var(--muted);
    font-size: 0.95rem;
  }}
  main {{
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1.5rem 3rem;
  }}
  section.subject {{
    margin-bottom: 2rem;
  }}
  section.subject h2 {{
    font-size: 1.2rem;
    border-left: 5px solid var(--accent);
    padding-left: 0.75rem;
    margin-bottom: 0.9rem;
  }}
  .card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 0.75rem;
  }}
  .card {{
    display: block;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 0.6rem;
    padding: 0.9rem 1rem;
    text-decoration: none;
    color: var(--text);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
  }}
  .card:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
  }}
  .card .title {{
    font-weight: 600;
    font-size: 0.95rem;
  }}
  .card .folder {{
    display: block;
    margin-top: 0.35rem;
    font-size: 0.75rem;
    color: var(--muted);
  }}
  footer {{
    text-align: center;
    color: var(--muted);
    font-size: 0.8rem;
    padding-bottom: 2rem;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #1a1b1e;
      --card-bg: #232428;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --border: #34353a;
    }}
  }}
</style>
</head>
<body>
<header>
  <h1>家庭教師 学習教材まとめ</h1>
  <p>中学・高校の数学、物理、古文の解説ページ集</p>
</header>
<main>

{sections}

</main>
<footer>
  KATKYO &mdash; 家庭教師用学習教材アーカイブ
</footer>
</body>
</html>
"""


def main():
    subjects = collect_subjects()
    names = ordered_subject_names(subjects)
    sections = "\n\n".join(render_section(name, subjects[name]) for name in names)
    html = TEMPLATE.format(sections=sections)
    out_path = ROOT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    total = sum(len(v) for v in subjects.values())
    print(f"index.html を更新しました（{len(names)}教科 / {total}ファイル）")


if __name__ == "__main__":
    main()
