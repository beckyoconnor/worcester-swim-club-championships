"""
2026 Club Championships scoring.

Parses SPORTSYSTEMS results exports (.RES), calculates World Aquatics points
from swim times, and applies the 2026 bucket rules:

  8 & under : 4 buckets - 25m Free / 25m Breast / 25m Back / 25m Fly
  9+        : Sprints (50s) / 100m Form / Freestyle (100, 200) / IM (100, 200, 400)

Only the best score per bucket counts; an empty bucket scores 0.
Age is the "AaD" column in the .RES file, which is age as at 31 December of the
meet year (cross-checked against dates of birth for the 2024 meet).

.RES files are used instead of LENEX (.LEF) because they don't contain dates of
birth or Swim England numbers. Swimmers are identified by name + club.
"""

import glob
import os
import re

import pandas as pd

BUCKETS = ['Bucket 1', 'Bucket 2', 'Bucket 3', 'Bucket 4']

BUCKET_NAMES_U9 = {
    'Bucket 1': '25m Free', 'Bucket 2': '25m Breast',
    'Bucket 3': '25m Back', 'Bucket 4': '25m Fly',
}
BUCKET_NAMES_9PLUS = {
    'Bucket 1': 'Sprints', 'Bucket 2': '100m Form',
    'Bucket 3': 'Freestyle', 'Bucket 4': 'IM',
}

# (distance, stroke) -> bucket
BUCKET_MAP_U9 = {
    (25, 'FREE'): 'Bucket 1', (25, 'BREAST'): 'Bucket 2',
    (25, 'BACK'): 'Bucket 3', (25, 'FLY'): 'Bucket 4',
}
BUCKET_MAP_9PLUS = {
    (50, 'FREE'): 'Bucket 1', (50, 'BREAST'): 'Bucket 1',
    (50, 'FLY'): 'Bucket 1', (50, 'BACK'): 'Bucket 1',
    (100, 'BREAST'): 'Bucket 2', (100, 'FLY'): 'Bucket 2', (100, 'BACK'): 'Bucket 2',
    (100, 'FREE'): 'Bucket 3', (200, 'FREE'): 'Bucket 3',
    (100, 'MEDLEY'): 'Bucket 4', (200, 'MEDLEY'): 'Bucket 4', (400, 'MEDLEY'): 'Bucket 4',
}

STROKE_LABELS = {'FREE': 'Free', 'BACK': 'Back', 'BREAST': 'Breast', 'FLY': 'Fly', 'MEDLEY': 'IM'}
STROKE_WORDS = {'freestyle': 'FREE', 'backstroke': 'BACK', 'breaststroke': 'BREAST',
                'butterfly': 'FLY', 'im': 'MEDLEY', 'medley': 'MEDLEY'}

EVENT_RE = re.compile(r'^EVENT\s+(\d+)\s+(Female|Open/Male|Male|Mixed)\s+(\d+)m\s+(.+?)\s*$', re.I)
AGE_GROUP_RE = re.compile(r'^(FEMALE|OPEN/MALE|MALE)?\s*(.*?)Age Group', re.I)
SESSION_RE = re.compile(r'^Session\s*-\s*(\d+)', re.I)


def bucket_names_for_age(age: int) -> dict:
    return BUCKET_NAMES_U9 if age <= 8 else BUCKET_NAMES_9PLUS


def bucket_for(age: int, distance: int, stroke: str) -> str | None:
    """Return the bucket an event counts towards for this age, or None if it doesn't count."""
    mapping = BUCKET_MAP_U9 if age <= 8 else BUCKET_MAP_9PLUS
    return mapping.get((distance, stroke))


def _time_to_seconds(t: str) -> float | None:
    """.RES times look like '18.72', '2:12.89' or '1:02:12.89'."""
    try:
        parts = [float(p) for p in t.split(':')]
    except (AttributeError, ValueError):
        return None
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return secs if secs > 0 else None


def format_seconds(secs: float) -> str:
    if secs is None or pd.isna(secs):
        return '-'
    m, s = divmod(secs, 60)
    return f"{int(m)}:{s:05.2f}" if m else f"{s:.2f}"


def _tidy_name(name: str) -> str:
    """'Angela O'CONNOR' -> 'Angela O'Connor' (surnames are upper-case in .RES)."""
    return ' '.join(w.title() if w.isupper() and len(w) > 1 else w for w in name.split())


def find_res_files(folder: str) -> list[str]:
    """All .RES files under folder, de-duplicated by file name (exports often contain copies)."""
    files = {}
    for path in sorted(glob.glob(os.path.join(folder, '**', '*.[rR][eE][sS]'), recursive=True)):
        files.setdefault(os.path.basename(path).upper(), path)
    return list(files.values())


def parse_res(path: str) -> pd.DataFrame:
    """One row per individual result in a .RES file.

    Each swimmer appears under their own age group and again under 'Open';
    the duplicate is dropped.
    """
    with open(path, encoding='latin-1') as f:
        lines = f.read().replace('\x00', '').split('\n')

    rows, session, event, section_gender = [], None, None, None
    for line in lines:
        if m := SESSION_RE.match(line.strip()):
            session = m.group(1)
            continue
        if m := EVENT_RE.match(line.strip()):
            num, gender, dist, stroke_txt = m.groups()
            stroke = STROKE_WORDS.get(stroke_txt.strip().lower())
            event = {
                'Session': session, 'Event Number': num,
                'Event Name': f"{gender} {dist}m {stroke_txt.strip()}",
                'Distance': int(dist), 'Stroke': stroke,
                'Event Gender': gender.lower(),
            }
            section_gender = None
            continue
        if 'Age Group' in line:
            m = AGE_GROUP_RE.match(line.strip())
            section_gender = (m.group(1) or '').lower() if m else ''
            continue
        if event is None or line.startswith('Place'):
            continue

        cols = [c.strip() for c in line.split('\t')]
        if len(cols) < 6 or not cols[1] or not cols[2].isdigit():
            continue
        time_txt = cols[5]
        status = time_txt if time_txt.upper() in {'DQ', 'DNS', 'DNF', 'NS', 'DSQ'} else ''

        # Gender comes from the event name, or the age-group heading for 'Mixed' events
        g = event['Event Gender'] if event['Event Gender'] != 'mixed' else section_gender
        gender = 'Female' if g.startswith('female') else ('Male/Open' if g else 'Unknown')

        name = _tidy_name(cols[1])
        rows.append({
            **{k: v for k, v in event.items() if k != 'Event Gender'},
            'Athlete ID': f"{name.lower()}|{cols[3].lower()}",
            'Name': name,
            'Gender': gender,
            'Age': int(cols[2]),
            'Club': cols[3],
            'Swim Time': '' if status else time_txt,
            'Status': status,
            'Source File': os.path.basename(path),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.drop_duplicates(subset=['Event Number', 'Athlete ID']).reset_index(drop=True)


def load_base_times(path: str) -> dict:
    df = pd.read_csv(path)
    return {(r.gender, int(r.distance), r.stroke): float(r.base_time) for r in df.itertuples()}


def load_results(folder: str, base_times_path: str) -> pd.DataFrame:
    """Parse every .RES file and add seconds, WA points and bucket."""
    frames = [parse_res(p) for p in find_res_files(folder)]
    frames = [f for f in frames if len(f)]
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    base = load_base_times(base_times_path)

    df['Seconds'] = df['Swim Time'].map(_time_to_seconds)
    df.loc[df['Status'] != '', 'Seconds'] = None  # DQ / DNS etc. score nothing

    gender_code = {'Female': 'F', 'Male/Open': 'M'}

    def points(r):
        b = base.get((gender_code.get(r['Gender']), r['Distance'], r['Stroke']))
        if b is None or r['Seconds'] is None or pd.isna(r['Seconds']):
            return 0
        return int(1000 * (b / r['Seconds']) ** 3)

    df['WA Points'] = df.apply(points, axis=1)
    df['Bucket'] = df.apply(lambda r: bucket_for(r['Age'], r['Distance'], r['Stroke']), axis=1)
    df['Event'] = df['Distance'].astype(str) + 'm ' + df['Stroke'].map(STROKE_LABELS).fillna(df['Stroke'])
    df['Time'] = df['Seconds'].map(format_seconds)
    df.loc[df['Status'] != '', 'Time'] = df['Status']
    return df


def mark_counted(df: pd.DataFrame) -> pd.DataFrame:
    """Flag the single best-scoring swim per swimmer per bucket."""
    df = df.copy()
    df['Counted'] = False
    eligible = df[df['Bucket'].notna() & (df['WA Points'] > 0)]
    best_idx = eligible.sort_values('WA Points', ascending=False).groupby(['Athlete ID', 'Bucket']).head(1).index
    df.loc[best_idx, 'Counted'] = True
    return df


def build_scoreboard(df: pd.DataFrame) -> pd.DataFrame:
    """One row per swimmer: points per bucket (0 if not swum) and total."""
    if df.empty:
        return pd.DataFrame()
    counted = df[df['Counted']]
    pivot = counted.pivot_table(index='Athlete ID', columns='Bucket', values='WA Points', aggfunc='sum')
    pivot = pivot.reindex(columns=BUCKETS).fillna(0).astype(int)
    best_event = counted.pivot_table(index='Athlete ID', columns='Bucket', values='Event', aggfunc='first')
    best_event = best_event.reindex(columns=BUCKETS)

    info = df.groupby('Athlete ID').agg(Name=('Name', 'first'), Age=('Age', 'max'),
                                        Gender=('Gender', lambda g: g.mode().iat[0]),
                                        Club=('Club', 'first'), Swims=('Event Number', 'count'))
    board = info.join(pivot, how='left').fillna({b: 0 for b in BUCKETS})
    for b in BUCKETS:
        board[b] = board[b].astype(int)
        board[f'{b} Event'] = best_event[b] if b in best_event else None
    board['Total Points'] = board[BUCKETS].sum(axis=1)
    board['Buckets Scored'] = (board[BUCKETS] > 0).sum(axis=1)
    return board.reset_index()
