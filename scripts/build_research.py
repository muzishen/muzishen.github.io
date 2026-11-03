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
ARTICLE_TEMPLATE = (ROOT / '_includes/research-article.html').read_text(encoding='utf-8')


def esc(value):
    return escape(str(value), quote=True)


def article_path(paper, locale):
    return f'/research/{"zh/" if locale == "zh" else ""}{paper["id"]}/'


def author_html(paper, separator=', '):
    return separator.join(f'<span class="author-name">{esc(name)}</span>' for name in paper['author_names'])


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
        introduction_url = esc(article_path(paper, locale))
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
          <h2 id="title-{esc(paper['id'])}"><a href="{introduction_url}">{esc(title)}</a></h2>
          <p class="paper-meta"><span class="paper-authors">{author_html(paper)}</span><span class="paper-date"><time datetime="{esc(paper['date'])}">{esc(shown_date)}</time><span class="separator" aria-hidden="true">·</span>{esc(paper['publication'][locale])}</span></p>
          <p class="paper-summary">{esc(paper['summary'][locale])}</p>
          <div class="paper-links">
            <a class="paper-introduction-link" href="{introduction_url}">{esc(ui['introduction_link'])} <span aria-hidden="true">→</span></a>
            <a href="{paper_url}" target="_blank" rel="noopener noreferrer">{esc(ui['paper_link'])} <span aria-hidden="true">↗</span></a>
            {code_link}
          </div>
        </div>
        <a class="paper-image" href="{introduction_url}" aria-label="{esc(ui['figure_link'].replace('{title}', title))}">
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


def render_article(paper, locale):
    ui = DATA['article_ui'][locale]
    article = paper['article'][locale]
    index_path = '/research/zh/' if locale == 'zh' else '/research/'
    en_path, zh_path = article_path(paper, 'en'), article_path(paper, 'zh')
    page_path = article_path(paper, locale)
    canonical = 'https://muzishen.github.io' + page_path
    title = paper['title'][locale]
    submitted = datetime.strptime(paper['submitted'], '%Y-%m-%d')
    display_date = f'{submitted.year}年{submitted.month}月{submitted.day}日' if locale == 'zh' else f'{submitted.strftime("%B")} {submitted.day}, {submitted.year}'
    values = {key.upper(): esc(value) for key, value in ui.items()}
    values.update({
        'LANG': 'zh-Hans' if locale == 'zh' else 'en',
        'PAGE_TITLE': esc(title + ' | NExT-LFM'),
        'ARTICLE_TITLE': esc(title),
        'DECK': esc(article['deck']),
        'SHORT': esc(article['short']),
        'CANONICAL': canonical,
        'EN_PATH': en_path, 'ZH_PATH': zh_path,
        'EN_URL': 'https://muzishen.github.io' + en_path,
        'ZH_URL': 'https://muzishen.github.io' + zh_path,
        'INDEX_PATH': index_path,
        'OG_LOCALE': 'zh_CN' if locale == 'zh' else 'en_US',
        'EN_CURRENT': ' aria-current="page"' if locale == 'en' else '',
        'ZH_CURRENT': ' aria-current="page"' if locale == 'zh' else '',
        'CATEGORY': esc(DATA['categories'][paper['category']][locale]),
        'AUTHORS': author_html(paper, '<span class="author-separator" aria-hidden="true">·</span>'),
        'DATE_ISO': esc(paper['submitted']), 'DATE_DISPLAY': esc(display_date),
        'PUBLICATION': esc(paper['publication'][locale]),
        'PAPER': esc(paper['paper']), 'PDF': esc(paper['pdf']),
        'IMAGE': esc(paper['image']),
        'FIGURE_ALT': esc(ui['figure_alt'].replace('{title}', title)),
        'CSS_VERSION': sha256((ROOT / 'assets/css/research.css').read_bytes()).hexdigest()[:12],
        'ARTICLE_CSS_VERSION': sha256((ROOT / 'assets/css/research-article.css').read_bytes()).hexdigest()[:12],
    })
    for section in ('motivation', 'evidence', 'takeaway'):
        values[section.upper()] = f'<p>{esc(article[section])}</p>'
    values['METHOD'] = ''.join(f'<li>{esc(step)}</li>' for step in article['method'])
    values['HIGHLIGHTS'] = ''.join(
        '<div class="research-highlight">'
        f'<span class="highlight-value">{esc(item["value"])}</span>'
        f'<span class="highlight-label">{esc(item["label"])}</span></div>'
        for item in article['highlights']
    )
    code_link = f'<a href="{esc(paper["code"])}" target="_blank" rel="noopener noreferrer">{esc(ui["code_label"])}</a>' if paper.get('code') else ''
    values['CODE_META'] = '<span class="separator" aria-hidden="true">·</span>' + code_link if code_link else ''
    values['CODE_RESOURCE'] = code_link
    bibtex = ('@misc{' + paper['id'].replace('-', '_') + ',\n'
              '  title = {' + paper['title']['en'] + '},\n'
              '  author = {' + ' and '.join(paper['authors_bibtex']) + '},\n'
              '  year = {' + str(submitted.year) + '},\n'
              '  eprint = {' + paper['paper'].rstrip('/').split('/')[-1] + '},\n'
              '  archivePrefix = {arXiv},\n'
              '  url = {' + paper['paper'] + '}\n}')
    values['BIBTEX'] = esc(bibtex)
    schema = {'@context': 'https://schema.org', '@type': 'Article',
              'headline': title, 'description': article['deck'],
              'author': [{'@type': 'Person', 'name': name} for name in paper['author_names']],
              'inLanguage': values['LANG'], 'mainEntityOfPage': canonical,
              'image': 'https://muzishen.github.io' + paper['image'], 'isBasedOn': paper['paper']}
    values['SCHEMA'] = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    output = re.sub(r'@@([A-Z_]+)@@', lambda match: values[match.group(1)], ARTICLE_TEMPLATE)
    if '@@' in output:
        raise ValueError('Unresolved article placeholder')
    path = ROOT / page_path.lstrip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding='utf-8')
    print(f'{path.relative_to(ROOT)}: {len(paper["author_names"])} full author names')


if __name__ == '__main__':
    for language in ('en', 'zh'):
        render(language)
        for paper in DATA['papers']:
            render_article(paper, language)
