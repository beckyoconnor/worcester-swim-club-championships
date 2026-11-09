"""
Build the 2026 Club Championship results (run locally after adding new .RES files).

    python build_2026_results.py                 # real 2026 data
    python build_2026_results.py --sample        # 2024 Wychavon example data

Parses the .RES files, keeps Worcester swimmers only, scores them with the 2026
bucket rules and writes small CSVs to <folder>/championship_results/. The
dashboard only reads these CSVs, so it does no parsing or scoring itself.
Commit and push the championship_results folder afterwards.
"""

import argparse
import os
from datetime import datetime

from champs_2026_scoring import build_scoreboard, load_results, mark_counted

BASE_TIMES = 'wa_base_times_scm.csv'
HOME_CLUB = 'Worcester'
FOLDERS = {'real': 'WSC_Club_Champs_2026', 'sample': 'WSC_Club_champs_wychavon'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sample', action='store_true', help='build the example (2024 Wychavon) results')
    args = parser.parse_args()

    base = FOLDERS['sample' if args.sample else 'real']
    df = load_results(os.path.join(base, 'raw_files'), BASE_TIMES)
    if df.empty:
        raise SystemExit(f'No .RES results found in {base}/raw_files')
    df = df[df['Club'] == HOME_CLUB].copy()
    if df.empty:
        raise SystemExit(f'No {HOME_CLUB} swimmers found')
    df = mark_counted(df)
    board = build_scoreboard(df)

    out = os.path.join(base, 'championship_results')
    os.makedirs(out, exist_ok=True)
    df.to_csv(os.path.join(out, 'swims_2026.csv'), index=False)
    board.to_csv(os.path.join(out, 'scoreboard_2026.csv'), index=False)
    with open(os.path.join(out, 'last_updated.txt'), 'w') as f:
        f.write(datetime.now().strftime('%d %b %Y %H:%M'))
    print(f'{len(df)} swims, {len(board)} {HOME_CLUB} swimmers -> {out}/')


if __name__ == '__main__':
    main()
