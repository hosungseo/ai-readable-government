#!/usr/bin/env python3
import argparse
import json
import math
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

WORKSPACE = Path('/Users/seohoseong/.openclaw/workspace')
APP_ROOT = WORKSPACE / 'ai-readable-government'
PRESS_ROOT = WORKSPACE / 'gov-press-md'
GAZETTE_ROOT = WORKSPACE / 'gov-gazette-md'
PAGE_SIZE = 100


def parse_front_matter(text: str) -> dict:
    meta = {}
    if not text.startswith('---'):
        return meta
    parts = text.split('---', 2)
    if len(parts) < 3:
        return meta
    for line in parts[1].splitlines():
        if ': ' not in line:
            continue
        k, v = line.split(': ', 1)
        meta[k.strip()] = v.strip().strip('"')
    return meta


def normalize_date(value: str) -> str:
    if not value:
        return ''
    if re.match(r'^\d{4}\.\d{2}\.\d{2}$', value):
        return value.replace('.', '-')
    if re.match(r'^\d{2}/\d{2}/\d{4}', value):
        mm, dd, yyyy = value.split(' ')[0].split('/')
        return f'{yyyy}-{mm}-{dd}'
    return value


def iterate_days(start_day: str, end_day: str):
    start = date.fromisoformat(start_day)
    end = date.fromisoformat(end_day)
    current = start
    while current <= end:
        yield current.isoformat()
        current += timedelta(days=1)


def safe_id(layer: str, day: str, filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r'[^0-9A-Za-z가-힣_-]+', '-', stem)
    return f'{layer}-{day}-{stem}'


def detail_rel_path(layer: str, doc_id: str) -> str:
    return f'docs/details/{layer}/{doc_id}.json'


def summary_fields(item: dict) -> dict:
    return {
        'id': item['id'],
        'layer': item['layer'],
        'title': item['title'],
        'institution': item['institution'],
        'date': item['date'],
        'docType': item['docType'],
        'excerpt': item.get('excerpt', ''),
        'detailPath': item['detailPath'],
    }


def build_press_for_day(day: str, limit_per_day: int) -> list:
    day_dir = PRESS_ROOT / 'data' / day[:4] / day[:7] / day
    if not day_dir.exists():
        return []
    items = []
    for md in sorted(day_dir.glob('*.md')):
        if md.name == 'README.md':
            continue
        text = md.read_text(encoding='utf-8', errors='ignore')
        meta = parse_front_matter(text)
        excerpt = ''
        m = re.search(r'## 본문\n+([\s\S]*?)(\n## |\Z)', text)
        if m:
            body = m.group(1)
            lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.startswith('<')]
            excerpt = ' '.join(lines[:4])[:220]
        doc_id = safe_id('press', day, md.name)
        detail_path = detail_rel_path('press', doc_id)
        items.append({
            'id': doc_id,
            'detailPath': detail_path,
            'layer': 'press',
            'file': md.name,
            'title': meta.get('title', ''),
            'institution': meta.get('ministry', ''),
            'ministry': meta.get('ministry', ''),
            'date': normalize_date(meta.get('approve_date', '')) or day,
            'approveDate': meta.get('approve_date', ''),
            'docType': meta.get('grouping_code', ''),
            'groupingCode': meta.get('grouping_code', ''),
            'newsItemId': meta.get('news_item_id', ''),
            'originalUrl': meta.get('original_url', ''),
            'source': meta.get('source', ''),
            'excerpt': excerpt,
            'path': str(md.relative_to(PRESS_ROOT)),
        })
        if limit_per_day and len(items) >= limit_per_day:
            break
    return items


def extract_meta_lines(text: str) -> dict:
    meta = {}
    for line in text.splitlines()[:40]:
        if ': ' in line and not line.startswith('#') and not line.startswith('- '):
            k, v = line.split(': ', 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta


def build_gazette_for_day(day: str, limit_per_day: int) -> list:
    meta_dir = GAZETTE_ROOT / 'data' / day[:4] / day[:7] / day
    final_dir = GAZETTE_ROOT / 'readable-final' / day
    raw_dir = GAZETTE_ROOT / 'opendataloader-output' / day
    if not meta_dir.exists():
        return []
    items = []
    for md in sorted(meta_dir.glob('*.md')):
        if md.name == 'README.md':
            continue
        text = md.read_text(encoding='utf-8', errors='ignore')
        meta = extract_meta_lines(text)
        final = final_dir / md.name
        raw = raw_dir / md.name
        excerpt = ''
        if final.exists():
            ftxt = final.read_text(encoding='utf-8', errors='ignore')
            lines = [
                ln.strip() for ln in ftxt.splitlines()
                if ln.strip()
                and not ln.startswith('---')
                and not ln.startswith('title:')
                and not ln.startswith('publisher:')
                and not ln.startswith('date:')
                and not ln.startswith('source_')
                and not ln.startswith('postprocess:')
                and not ln.startswith('# ')
                and not ln.startswith('- 발행')
                and not ln.startswith('- 원문 PDF:')
                and not ln.startswith('## ')
            ]
            excerpt = ' '.join(lines[:3])[:220]
        doc_id = safe_id('gazette', day, md.name)
        detail_path = detail_rel_path('gazette', doc_id)
        items.append({
            'id': doc_id,
            'detailPath': detail_path,
            'layer': 'gazette',
            'file': md.name,
            'title': meta.get('title', ''),
            'institution': meta.get('publisher', ''),
            'publisher': meta.get('publisher', ''),
            'date': normalize_date(meta.get('date', '')) or day,
            'docType': meta.get('form_type', ''),
            'formType': meta.get('form_type', ''),
            'basisLaw': meta.get('basis_law', ''),
            'pdfUrl': meta.get('pdf_url', ''),
            'hasRaw': raw.exists(),
            'hasReadable': final.exists(),
            'excerpt': excerpt,
            'metaPath': str(md.relative_to(GAZETTE_ROOT)),
            'rawPath': str(raw.relative_to(GAZETTE_ROOT)) if raw.exists() else '',
            'readablePath': str(final.relative_to(GAZETTE_ROOT)) if final.exists() else '',
        })
        if limit_per_day and len(items) >= limit_per_day:
            break
    return items


def group_by_date(*datasets):
    bucket = defaultdict(list)
    for dataset in datasets:
        for item in dataset:
            bucket[item.get('date', 'unknown')].append({'id': item['id'], 'layer': item['layer'], 'institution': item['institution']})
    result = []
    for day in sorted(bucket.keys()):
        items = bucket[day]
        result.append({
            'date': day,
            'total': len(items),
            'pressCount': sum(1 for x in items if x['layer'] == 'press'),
            'gazetteCount': sum(1 for x in items if x['layer'] == 'gazette'),
            'itemRefs': items,
        })
    return result


def group_by_institution(*datasets):
    bucket = defaultdict(list)
    for dataset in datasets:
        for item in dataset:
            name = item.get('institution') or 'Unknown'
            bucket[name].append({'id': item['id'], 'layer': item['layer'], 'date': item['date']})
    result = []
    for name in sorted(bucket.keys()):
        items = bucket[name]
        result.append({
            'institution': name,
            'total': len(items),
            'pressCount': sum(1 for x in items if x['layer'] == 'press'),
            'gazetteCount': sum(1 for x in items if x['layer'] == 'gazette'),
            'itemRefs': items,
        })
    return result


def write_details(items: list, docs_dir: Path):
    for item in items:
        rel = Path(item['detailPath'].replace('docs/', '', 1))
        path = docs_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')


def write_paged_list(layer: str, items: list, docs_dir: Path):
    page_dir = docs_dir / 'pages' / layer
    page_dir.mkdir(parents=True, exist_ok=True)
    summaries = [summary_fields(x) for x in items]
    total_pages = max(1, math.ceil(len(summaries) / PAGE_SIZE))
    for i in range(total_pages):
        chunk = summaries[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]
        payload = {
            'layer': layer,
            'page': i + 1,
            'pageSize': PAGE_SIZE,
            'totalItems': len(summaries),
            'totalPages': total_pages,
            'items': chunk,
        }
        (page_dir / f'page-{i + 1:03d}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return total_pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day', default='2026-04-01')
    parser.add_argument('--start-day')
    parser.add_argument('--end-day')
    parser.add_argument('--press-limit', type=int, default=8)
    parser.add_argument('--gazette-limit', type=int, default=6)
    parser.add_argument('--press-limit-per-day', type=int)
    parser.add_argument('--gazette-limit-per-day', type=int)
    args = parser.parse_args()

    start_day = args.start_day or args.day
    end_day = args.end_day or args.day
    press_limit = args.press_limit_per_day if args.press_limit_per_day is not None else args.press_limit
    gazette_limit = args.gazette_limit_per_day if args.gazette_limit_per_day is not None else args.gazette_limit

    docs_dir = APP_ROOT / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)

    press = []
    gazette = []
    for day in iterate_days(start_day, end_day):
        press.extend(build_press_for_day(day, press_limit))
        gazette.extend(build_gazette_for_day(day, gazette_limit))

    write_details(press, docs_dir)
    write_details(gazette, docs_dir)
    press_pages = write_paged_list('press', press, docs_dir)
    gazette_pages = write_paged_list('gazette', gazette, docs_dir)

    by_date = group_by_date(press, gazette)
    by_institution = group_by_institution(press, gazette)

    overview = {
        'generatedForDay': start_day if start_day == end_day else None,
        'generatedForRange': {'start': start_day, 'end': end_day},
        'coverage': {
            'pressSampleCount': len(press),
            'gazetteSampleCount': len(gazette),
            'dateGroupCount': len(by_date),
            'institutionGroupCount': len(by_institution),
        },
        'lists': {
            'press': {'pageSize': PAGE_SIZE, 'totalItems': len(press), 'totalPages': press_pages, 'firstPage': 'docs/pages/press/page-001.json'},
            'gazette': {'pageSize': PAGE_SIZE, 'totalItems': len(gazette), 'totalPages': gazette_pages, 'firstPage': 'docs/pages/gazette/page-001.json'},
        },
        'byDate': by_date,
        'byInstitution': by_institution,
    }

    (docs_dir / 'by-date.json').write_text(json.dumps(by_date, ensure_ascii=False, indent=2), encoding='utf-8')
    (docs_dir / 'by-institution.json').write_text(json.dumps(by_institution, ensure_ascii=False, indent=2), encoding='utf-8')
    (docs_dir / 'index-data.json').write_text(json.dumps(overview, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote press={len(press)} gazette={len(gazette)} dates={len(by_date)} institutions={len(by_institution)} range={start_day}..{end_day}')


if __name__ == '__main__':
    main()
