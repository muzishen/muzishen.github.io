#!/usr/bin/env python3
"""Build both static Research pages. Run after editing _data/research.json.

Uses Python's standard library only. The generated pages work on GitHub Pages
without new Jekyll plugins, a server, or client-side translation dependencies.
"""
from datetime import datetime
from html import escape
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / '_data/research.json').read_text(encoding='utf-8'))
TEMPLATE = (ROOT / '_includes/research-page.html').read_text(encoding='utf-8')


def esc(value):
    return escape(str(value), quote=True)


def render(locale):
    ui = DATA['ui'][locale]
    categories = DATA['categories']
    items = DATA['papers']
    values = {key.upper(): esc(value) for key, value in ui.items()}
    values.update({
        'LANG': 'zh-Hans' if locale == 'zh' else 'en',
        'CANONICAL': 'https://muzishen.github.io' + ui['home_research'],
        'OG_LOCALE': 'zh_CN' if locale == 'zh' else 'en_US',
        'OG_ALTERNATE': 'en_US' if locale == 'zh' else 'zh_CN',
        'EN_CURRENT': ' aria-current="page"' if locale == 'en' else '',
        'ZH_CURRENT': ' aria-current="page"' if locale == 'zh' else '',
        'INITIAL_COUNT': esc(ui['count_template'].replace('{count}', str(len(items)))),
        'CSS_VERSION': sha256((ROOT / 'assets/css/research.css').read_bytes()).hexdigest()[:12],
        'JS_VERSION': sha256((ROOT / 'assets/js/research.js').read_bytes()).hexdigest()[:12],
    })
    filters = [('all', ui['all_research'])] + [(key, value[locale]) for key, value in categories.items()]
    values['FILTERS'] = '\n        '.join(
        f'<button class="filter-button" type="button" data-filter="{esc(key)}" '
        f'aria-pressed="{"true" if key == "all" else "false"}">{esc(label)}</button>'
        for key, label in filters
    )
    rows = []
    for index, paper in enumerate(items):
        date = datetime.strptime(paper['date'], '%Y-%m')
        shown_date = f'{date.year}年{date.month}月' if locale == 'zh' else date.strftime('%B %Y')
        paper_url = esc(paper['paper'])
        category = categories[paper['category']][locale]
        code_link = (
            f'<a href="{esc(paper["code"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(ui["code_link"])} <span aria-hidden="true">↗</span></a>'
        ) if paper.get('code') else ''
        title = paper['title'][locale]
        loading = 'eager' if index == 0 else 'lazy'
        rows.append(f'''<article class="research-row" data-category="{esc(paper['category'])}" id="{esc(paper['id'])}" aria-labelledby="title-{esc(paper['id'])}">
        <div class="paper-copy">
          <span class="category-tag">{esc(category)}</span>
          <h2 id="title-{esc(paper['id'])}"><a href="{paper_url}" target="_blank" rel="noopener noreferrer">{esc(title)}</a></h2>
          <p class="paper-meta">{esc(paper['authors'])}<span class="separator" aria-hidden="true">·</span><time datetime="{esc(paper['date'])}">{esc(shown_date)}</time><br>{esc(paper['publication'][locale])}</p>
          <p class="paper-summary">{esc(paper['summary'][locale])}</p>
          <div class="paper-links">
            <a href="{paper_url}" target="_blank" rel="noopener noreferrer">{esc(ui['paper_link'])} <span aria-hidden="true">↗</span></a>
            {code_link}
          </div>
        </div>
        <a class="paper-image" href="{paper_url}" target="_blank" rel="noopener noreferrer" aria-label="{esc(ui['figure_link'].replace('{title}', title))}">
          <img src="{esc(paper['image'])}" width="600" height="400" alt="{esc(ui['figure_alt'].replace('{title}', title))}" loading="{loading}" decoding="async">
        </a>
      </article>''')
    values['PAPERS'] = '\n      '.join(rows)
    output = re.sub(r'@@([A-Z_]+)@@', lambda match: values[match.group(1)], TEMPLATE)
    if '@@' in output:
        raise ValueError('Unresolved template placeholder')
    path = ROOT / ('research/zh/index.html' if locale == 'zh' else 'research/index.html')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding='utf-8')
    print(f'{path.relative_to(ROOT)}: {len(items)} papers, {len(filters)} filters')


if __name__ == '__main__':
    for language in ('en', 'zh'):
        render(language)
