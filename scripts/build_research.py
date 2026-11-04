#!/usr/bin/env python3
"""Build both static Research pages. Run after editing _data/research.json.

Uses Python's standard library only. The generated pages work on GitHub Pages
without new Jekyll plugins, a server, or client-side translation dependencies.
"""
from datetime import datetime
from html import escape
from hashlib import sha256
from math import ceil
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


def author_html(paper):
    return f'<strong class="author-name">{esc(paper["author_names"][0])}</strong>'


def reading_minutes(paper, locale):
    """Estimate the introduction at 200 words/350 Han characters per minute.

    Includes the article's figure captions and 20 seconds to inspect each
    source figure. Bibliography, bylines, and related articles are excluded.
    """
    article = paper['article'][locale]
    texts = []
    for section in ('deck', 'thesis', 'short', 'motivation', 'method', 'evidence', 'takeaway'):
        value = article[section]
        texts.extend(value if isinstance(value, list) else [value])
    texts.extend(f'{h["value"]} {h["label"]}' for h in article['highlights'])
    for figure in paper['figures']:
        texts.extend((figure['title'][locale], figure['explanation'][locale]))
    text = ' '.join(texts)
    words = len(re.findall(r"[A-Za-z0-9]+(?:['’\u2010-\u2015-][A-Za-z0-9]+)*", text))
    han = len(re.findall(r'[\u3400-\u9fff]', text))
    return max(1, ceil(words / 200 + han / 350 + len(paper['figures']) / 3))


def reading_time_html(paper, locale):
    minutes = reading_minutes(paper, locale)
    label = f'约 {minutes} 分钟阅读' if locale == 'zh' else f'{minutes}-minute read'
    hint = '预计阅读时长，含图表浏览。' if locale == 'zh' else 'Estimated reading time, including figures.'
    return f'<span class="reading-time" data-reading-minutes="{minutes}" title="{esc(hint)}">{esc(label)}</span>'


def contact_author_html(paper, locale):
    ui = DATA['article_ui'][locale]
    name = paper['author_names'][0]
    contact = paper.get('contact', {})
    email = contact.get('email')
    detail = (
        f'<a class="author-email" href="{esc("mailto:" + email)}">{esc(email)} <span aria-hidden="true">↗</span></a>'
        if email else f'<span class="author-email-pending">{esc(ui["contact_pending"])}</span>'
    )
    return ('<div class="author-contact" role="group" aria-label="' + esc(ui['contact_author']) + '">'
            '<div><span class="contact-author-label">' + esc(ui['contact_author']) + '</span>'
            '<strong class="author-name">' + esc(name) + '</strong></div>' + detail + '</div>')


def paragraphs(value):
    return ''.join(f'<p>{esc(p)}</p>' for p in (value if isinstance(value, list) else [value]))


def source_figure(paper, index, locale):
    item = paper['figures'][index]
    ui = DATA['article_ui'][locale]
    label = ('表' if item['kind'] == 'table' else '图') + str(item['number']) if locale == 'zh' else item['kind'].title() + ' ' + str(item['number'])
    title = item['title'][locale]
    return f'''<figure class="source-figure">
          <a class="figure-zoom" href="{esc(item['path'])}" target="_blank" rel="noopener noreferrer" data-figure-src="{esc(item['path'])}" data-figure-title="{esc(label + ' · ' + title)}" aria-label="{esc(ui['figure_zoom'] + ': ' + title)}">
            <img src="{esc(item['path'])}" width="{item['width']}" height="{item['height']}" alt="{esc(label + ' · ' + title + '. ' + item['explanation'][locale])}" loading="lazy" decoding="async">
            <span class="figure-open-icon" aria-hidden="true">⤢</span>
          </a>
          <figcaption><span class="figure-label">{esc(label)} / {'第' + str(item['page']) + '页' if locale == 'zh' else 'p. ' + str(item['page'])}</span>
            <h3>{esc(title)}</h3><p>{esc(item['explanation'][locale])}</p>
            <a href="{esc(item['source'])}" target="_blank" rel="noopener noreferrer">{esc(ui['figure_source'])} <span aria-hidden="true">↗</span></a>
          </figcaption>
        </figure>'''


def related_research(paper, locale):
    lookup = {p['id']: p for p in DATA['papers']}
    rows = []
    for slug in paper['related']:
        p = lookup[slug]
        date = datetime.strptime(p['submitted'], '%Y-%m-%d')
        shown_date = f'{date.year}年{date.month}月{date.day}日' if locale == 'zh' else f'{date.strftime("%B")} {date.day}, {date.year}'
        rows.append(f'''<a class="related-row" href="{esc(article_path(p, locale))}">
          <div class="related-copy"><h3>{esc(p['title'][locale])}</h3><div class="related-meta"><time datetime="{esc(p['submitted'])}">{esc(shown_date)}</time><span aria-hidden="true">·</span>{reading_time_html(p, locale)}</div></div>
          <p class="related-authors">{author_html(p)}</p><span class="related-arrow" aria-hidden="true">→</span>
        </a>''')
    return '\n'.join(rows)


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
        'INITIAL_COUNT': esc(ui['count_template'].replace('{count}', str(sum(p['category'] == DATA['default_category'] for p in items)))),
        'CSS_VERSION': sha256((ROOT / 'assets/css/research.css').read_bytes()).hexdigest()[:12],
        'CONTACT_CSS_VERSION': sha256((ROOT / 'assets/css/research-contact.css').read_bytes()).hexdigest()[:12],
        'JS_VERSION': sha256((ROOT / 'assets/js/research.js').read_bytes()).hexdigest()[:12],
    })
    values['TEAM_CONTACTS'] = '\n          '.join(
        '<li class="contact-team-member">'
        '<h3 class="contact-team-name"><span lang="en">' + esc(member['name_en']) + '</span> '
        '<span class="contact-team-chinese" lang="zh-Hans">(' + esc(member['name_zh']) + ')</span></h3>'
        '<a class="contact-team-email" href="' + esc('mailto:' + member['email']) + '">'
        + esc(member['email']) + ' <span aria-hidden="true">↗</span></a></li>'
        for member in DATA['team_contacts']
    )
    filters = [(key, value[locale]) for key, value in categories.items()]
    values['FILTERS'] = '\n        '.join(
        f'<button class="filter-button" type="button" data-filter="{esc(key)}" '
        f'aria-pressed="{"true" if key == DATA["default_category"] else "false"}">{esc(label)}</button>'
        for key, label in filters
    )
    rows = []
    for index, paper in enumerate(items):
        date = datetime.strptime(paper['date'], '%Y-%m')
        shown_date = f'{date.year}年{date.month}月' if locale == 'zh' else date.strftime('%B %Y')
        paper_url = esc(paper['paper'])
        introduction_url = esc(article_path(paper, locale))
        category = categories[paper['category']][locale]
        topic_tag = '' if paper['topic'][locale] == category else f'<span class="paper-topic">{esc(paper["topic"][locale])}</span>'
        code_link = (
            f'<a href="{esc(paper["code"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(ui["code_link"])} <span aria-hidden="true">↗</span></a>'
        ) if paper.get('code') else ''
        title = paper['title'][locale]
        loading = 'eager' if index == 0 else 'lazy'
        rows.append(f'''<article class="research-row" data-category="{esc(paper['category'])}" id="{esc(paper['id'])}" aria-labelledby="title-{esc(paper['id'])}">
        <div class="paper-copy">
          <span class="category-tag">{esc(category)}</span>{topic_tag}
          <h2 id="title-{esc(paper['id'])}"><a href="{introduction_url}">{esc(title)}</a></h2>
          <p class="paper-meta"><span class="paper-authors">{author_html(paper)}</span><span class="paper-date"><time datetime="{esc(paper['date'])}">{esc(shown_date)}</time><span class="separator" aria-hidden="true">·</span>{esc(paper['publication'][locale])}<span class="separator" aria-hidden="true">·</span>{reading_time_html(paper, locale)}</span></p>
          <p class="paper-summary">{esc(paper['summary'][locale])}</p>
          <div class="paper-links">
            <a class="paper-introduction-link" href="{introduction_url}">{esc(ui['introduction_link'])} <span aria-hidden="true">→</span></a>
            <a href="{paper_url}" target="_blank" rel="noopener noreferrer">{esc(ui['paper_link'])} <span aria-hidden="true">↗</span></a>
            {code_link}
          </div>
        </div>
        <a class="paper-image" href="{introduction_url}" aria-label="{esc(ui['figure_link'].replace('{title}', title))}">
          <img src="{esc(paper['cover'])}" width="1280" height="853" alt="{esc(ui['figure_alt'].replace('{title}', title))}" loading="{loading}" decoding="async">
        </a>
      </article>''')
    values['PAPERS'] = '\n      '.join(rows)
    output = re.sub(r'@@([A-Z_0-9]+)@@', lambda match: values[match.group(1)], TEMPLATE)
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
    if paper['category'] == 'applied':
        index_path += '?topic=applied'
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
        'SHORT': paragraphs(article['short']),
        'THESIS': esc(article['thesis']),
        'CANONICAL': canonical,
        'EN_PATH': en_path, 'ZH_PATH': zh_path,
        'EN_URL': 'https://muzishen.github.io' + en_path,
        'ZH_URL': 'https://muzishen.github.io' + zh_path,
        'INDEX_PATH': index_path,
        'OG_LOCALE': 'zh_CN' if locale == 'zh' else 'en_US',
        'EN_CURRENT': ' aria-current="page"' if locale == 'en' else '',
        'ZH_CURRENT': ' aria-current="page"' if locale == 'zh' else '',
        'CATEGORY': esc(DATA['categories'][paper['category']][locale]),
        'TOPIC': esc(paper['topic'][locale]),
        'TOPIC_KICKER': (esc(paper['topic'][locale]) + ' / ') if paper['topic'][locale] != DATA['categories'][paper['category']][locale] else '',
        'AUTHORS': author_html(paper),
        'READING_TIME': reading_time_html(paper, locale),
        'AUTHOR_CONTACT': contact_author_html(paper, locale),
        'DATE_ISO': esc(paper['submitted']), 'DATE_DISPLAY': esc(display_date),
        'PUBLICATION': esc(paper['publication'][locale]),
        'PAPER': esc(paper['paper']), 'PDF': esc(paper['pdf']),
        'IMAGE': esc(paper['cover']),
        'FIGURE_ALT': esc(ui['concept_label'] + ': ' + title),
        'CSS_VERSION': sha256((ROOT / 'assets/css/research.css').read_bytes()).hexdigest()[:12],
        'ARTICLE_CSS_VERSION': sha256((ROOT / 'assets/css/research-article.css').read_bytes()).hexdigest()[:12],
        'ARTICLE_JS_VERSION': sha256((ROOT / 'assets/js/research-article.js').read_bytes()).hexdigest()[:12],
        'RELATED': related_research(paper, locale),
    })
    for section in ('motivation', 'evidence', 'takeaway'):
        values[section.upper()] = paragraphs(article[section])
    for index in range(3):
        values['SOURCE_FIGURE_' + str(index + 1)] = source_figure(paper, index, locale)
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
              'image': 'https://muzishen.github.io' + paper['cover'], 'isBasedOn': paper['paper'],
              'timeRequired': f'PT{reading_minutes(paper, locale)}M'}
    values['SCHEMA'] = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    output = re.sub(r'@@([A-Z_0-9]+)@@', lambda match: values[match.group(1)], ARTICLE_TEMPLATE)
    if '@@' in output:
        raise ValueError('Unresolved article placeholder')
    path = ROOT / page_path.lstrip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding='utf-8')
    print(f'{path.relative_to(ROOT)}: first author, {reading_minutes(paper, locale)}-minute read')


if __name__ == '__main__':
    for language in ('en', 'zh'):
        render(language)
        for paper in DATA['papers']:
            render_article(paper, language)
