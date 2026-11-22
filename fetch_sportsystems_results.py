"""
Download published SPORTSYSTEMS web results and save them as .RES-style files,
for use before the official results exports arrive.

    python3 fetch_sportsystems_results.py
    python3 fetch_sportsystems_results.py --url <meet index.htm> --out <folder>

Writes one file per session to <out>/web_results/, in the same tab-separated
layout as the official .RES exports, so build_2026_results.py reads them as-is.
Delete web_results/ once the official .RES files are in raw_files/.
"""

import argparse
import os
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

DEFAULT_URL = 'https://results.swimworcestercounty.org/events/wychavon_invitational/2026/index.htm'
DEFAULT_OUT = 'WSC_Club_Champs_2026/raw_files'


class _Cells(HTMLParser):
    """Collect page content as a flat list of ('h3', text), ('row', [cells]) and ('a', href, text)."""

    def __init__(self):
        super().__init__()
        self.items, self._row, self._cell, self._h3, self._href = [], None, None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self._row = []
        elif tag == 'td' and self._row is not None:
            self._cell = ''
        elif tag == 'h3':
            self._h3 = ''
        elif tag == 'a':
            self._href = dict(attrs).get('href')

    def handle_endtag(self, tag):
        if tag == 'td' and self._cell is not None:
            self._row.append(' '.join(self._cell.split()))
            self._cell = None
        elif tag == 'tr' and self._row is not None:
            self.items.append(('row', self._row))
            self._row = None
        elif tag == 'h3' and self._h3 is not None:
            self.items.append(('h3', ' '.join(self._h3.split())))
            self._h3 = None
        elif tag == 'a':
            self._href = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data
        if self._h3 is not None:
            self._h3 += data
        if self._href and data.strip():
            self.items.append(('a', self._href, data.strip()))


def _get(url: str) -> list:
    with urllib.request.urlopen(url, timeout=30) as r:
        parser = _Cells()
        parser.feed(r.read().decode('utf-8', errors='replace'))
        return parser.items


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default=DEFAULT_URL)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    # The event list lives in the left frame (before.htm) of the frameset index page
    menu_url = urljoin(args.url, 'before.htm')
    with urllib.request.urlopen(menu_url, timeout=30) as r:
        menu_html = r.read().decode('utf-8', errors='replace')
    text = re.sub(r'<[^>]+>', '\n', menu_html)

    sessions, session, events = {}, None, {}
    for line in (l.strip() for l in text.split('\n')):
        # Heading runs into the date, e.g. "Session 121/11/26" = session 1 on 21/11/26
        if m := re.match(r'^Session\s*(\d)', line):
            session = int(m.group(1))
        elif m := re.match(r'^(\d+)\s+(Female|Open/Male|Male|Mixed)\s+(\d+m\s+.+)$', line, re.I):
            events[int(m.group(1))] = (session, f"EVENT {m.group(1)} {m.group(2)} {m.group(3)}")
    result_links = re.findall(r'href="(R[A-Z0-9]+H(\d+)\.HTM)"', menu_html, re.I)

    out_dir = os.path.join(args.out, 'web_results')
    os.makedirs(out_dir, exist_ok=True)
    lines_by_session, n_rows = {}, 0
    for href, num in result_links:
        num = int(num)
        sess, header = events.get(num, (None, None))
        if header is None:
            continue
        out = lines_by_session.setdefault(sess, [f"Session - {sess:02d}", ''])
        out += [header, '']
        for item in _get(urljoin(menu_url, href)):
            if item[0] == 'h3' and 'Age Group' in item[1]:
                out.append(item[1])
            elif item[0] == 'row':
                cells = item[1]
                # Result rows: place, name, AaD, club, blank, time ... (split rows have no age)
                if len(cells) >= 6 and cells[1] and cells[2].isdigit():
                    out.append('\t'.join(cells[:6]))
                    n_rows += 1
        out.append('')

    for sess, lines in sorted(lines_by_session.items()):
        path = os.path.join(out_dir, f"WEB_Session{sess:02d}.RES")
        with open(path, 'w', encoding='latin-1', errors='replace') as f:
            f.write('\n'.join(lines))
    print(f"{len(result_links)} events in {len(lines_by_session)} sessions, {n_rows} result rows -> {out_dir}/")


if __name__ == '__main__':
    main()
