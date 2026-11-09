#!/usr/bin/env python3
"""
Worcester SC Club Championships 2026 - Streamlit dashboard.

Scoring (2026 rules): four event buckets, best WA points score per bucket,
total = sum of the four bucket scores (0 for a bucket not swum).

Data: add .RES files to WSC_Club_Champs_2026/raw_files/, then run
`python build_2026_results.py` - the app only reads the precomputed CSVs.
Until those arrive the app previews using the 2024 Wychavon meet files.
.LEF files are not needed (and are git-ignored) as they contain dates of birth.
"""

import base64
import html
import os

import altair as alt
import pandas as pd
import streamlit as st

from champs_2026_scoring import (
    BUCKETS, BUCKET_NAMES_U9, BUCKET_NAMES_9PLUS, bucket_names_for_age,
)

# Precomputed by build_2026_results.py - the app only reads these small CSVs
DATA_FOLDER_2026 = 'WSC_Club_Champs_2026/championship_results'
SAMPLE_FOLDER = 'WSC_Club_champs_wychavon/championship_results'
BASE_TIMES = 'wa_base_times_scm.csv'
HOME_CLUB = 'Worcester'  # club short name as it appears in .RES files
AGE_RULE_TEXT = "31 December of the championship year (the age shown in the results file)"

st.set_page_config(page_title="Worcester SC - Club Championships 2026", page_icon="🏊", layout="wide")

# Same club branding as the 2025 dashboard (fonts, header, expanders, buttons, tooltips)
if os.path.exists('styles.css'):
    with open('styles.css') as f:
        st.html(f"<style>{f.read()}</style>")
# styles.css sets all markdown to body size, which shrinks st.metric values; restore the 2025 metric look
st.html("""<style>
[data-testid="stMetricValue"], [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] p {
  font-size: 2rem !important; line-height: 1.2 !important; color: #2b1f5c !important; font-weight: 700 !important;
}
/* Phones: smaller club header so results start higher up the screen */
@media (max-width: 768px) {
  .wsc-header { padding: 1rem !important; gap: 0.9rem !important; margin-bottom: 1rem !important; }
  .wsc-header-logo img { width: 64px !important; }
  .wsc-header-text h1 { font-size: 1.35rem !important; line-height: 1.2 !important; }
  .wsc-header-text h2 { font-size: 0.95rem !important; margin-top: 0.25rem !important; }
  .wsc-header-text p { font-size: 0.8rem !important; margin-top: 0.25rem !important; }
  [data-testid="stMetricValue"], [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] p {
    font-size: 1.5rem !important;
  }
}
</style>""")

# Worcester club colours for the bucket chart (navy, green, blue, light green)
BUCKET_COLOURS = ['#1a1d5a', '#7ef542', '#1e3a8a', '#b7f59a']


def _read(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    text_cols = df.select_dtypes(exclude=['number', 'bool']).columns
    df[text_cols] = df[text_cols].fillna('')
    return df


# One shared copy for all visitors; max_entries=1 keeps only the current results in memory
@st.cache_data(ttl=3600, max_entries=1)
def get_data(folder: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    return _read(os.path.join(folder, 'swims_2026.csv')), _read(os.path.join(folder, 'scoreboard_2026.csv'))


def age_label(age: int) -> str:
    return '8 & under' if age <= 8 else ('16+' if age >= 16 else str(age))


# ---------- Header ----------
logo_html = "<div style='font-size: 4rem;'>🏊</div>"
if os.path.exists('cropped-WSC_Blue.jpg'):
    with open('cropped-WSC_Blue.jpg', 'rb') as img:
        logo_b64 = base64.b64encode(img.read()).decode()
    logo_html = (f'<img src="data:image/jpeg;base64,{logo_b64}" width="150" '
                 'style="display: block; border-radius: 5px;">')
st.html(f"""
<div class="wsc-header">
    <div class="wsc-header-logo">{logo_html}</div>
    <div class="wsc-header-text">
        <h1>Worcester Swimming Club</h1>
        <h2>Club Championships Dashboard 2026</h2>
        <p>Interactive Rankings &amp; Competition Analysis</p>
    </div>
</div>
""")

using_sample = not os.path.exists(os.path.join(DATA_FOLDER_2026, 'scoreboard_2026.csv'))
folder = SAMPLE_FOLDER if using_sample else DATA_FOLDER_2026
if using_sample:
    st.caption(
        ":material/info: Showing example results from a previous meet so you can see how the new 2026 "
        "scoring works. The 2026 Club Championship results will appear here once they're published."
    )

df_all, board = get_data(folder)
if board.empty:
    st.error("Results are not available yet.")
    st.stop()

with st.expander("Championship rules and scoring", icon=":material/rule:"):
    left, right = st.columns(2)
    with left:
        st.markdown("**8 years & under**")
        st.table(pd.DataFrame({'Bucket': BUCKETS, 'Events': list(BUCKET_NAMES_U9.values())}).set_index('Bucket'))
    with right:
        st.markdown("**9 years +**")
        st.table(pd.DataFrame({
            'Bucket': BUCKETS,
            'Group': list(BUCKET_NAMES_9PLUS.values()),
            'Events': ['50m Free, Breast, Fly, Back', '100m Breast, Fly, Back', '100m Free, 200m Free',
                       '100 IM, 200 IM, 400 IM'],
        }).set_index('Bucket'))
    st.markdown(
        f"- Age calculated as at **{AGE_RULE_TEXT}**\n"
        "- Points: World Aquatics (FINA) points calculated from swim times: `1000 × (base time / swim time)³`\n"
        "- Only your **best score in each bucket** counts; total = sum of the four buckets\n"
        "- No swim in a bucket scores **0** for that bucket\n"
        "- Events outside the four buckets (e.g. 200m form, 400 free) do not count\n"
        f"- Only {HOME_CLUB} SC swimmers are included"
    )

    st.markdown("**What is a base time?**")
    st.markdown(
        "Every event has a **base time**: a benchmark set by World Aquatics from the short-course "
        "(25m pool) **world record**, separately for girls and boys. Your points show how close "
        "your time is to that benchmark:\n"
        "- Swim the base time and you score **1000 points** (world-record pace)\n"
        "- The slower you are compared with the base time, the fewer points you get\n"
        "- The formula cubes the ratio, so points drop quickly. Twice the base time scores 125 points.\n\n"
        "Because every event has its own base time, points let us fairly compare **different strokes "
        "and distances**. A good 100m IM and a good 50m Breast earn similar points, even though the times "
        "are very different. That's what lets the four buckets add up to a fair total."
    )
    ex = pd.read_csv(BASE_TIMES).query("gender == 'F' and distance == 50 and stroke == 'FREE'")['base_time'].iat[0]
    st.markdown(
        f"*Example:* the girls' 50m Free base time is **{ex:.2f}s**. A girl swimming **{ex * 1.5:.2f}s** "
        f"(one and a half times the base time) scores 1000 × ({ex:.2f} / {ex * 1.5:.2f})³ = "
        f"**{int(1000 * (1 / 1.5) ** 3)} points**."
    )

    st.markdown("**How 25m swims are scored (8 & under)**")
    bt = pd.read_csv(BASE_TIMES)
    bt25 = bt[bt['distance'] == 25].pivot(index='stroke', columns='gender', values='base_time')
    bt25 = bt25.reindex(['FREE', 'BREAST', 'BACK', 'FLY']).rename(
        index={'FREE': '25m Free', 'BREAST': '25m Breast', 'BACK': '25m Back', 'FLY': '25m Fly'},
        columns={'F': 'Girls base time (s)', 'M': 'Boys base time (s)'})
    bt25.index.name = 'Event'
    st.markdown(
        "World Aquatics does not publish base times for 25m events, so the club uses **half the "
        "short-course 50m base time** for the same stroke. Points then use the same formula as every "
        "other event: `1000 × (base time / swim time)³`."
    )
    st.table(bt25[['Girls base time (s)', 'Boys base time (s)']])
    ex_base = float(bt25.loc['25m Back', 'Boys base time (s)'])
    ex_time = 23.88
    st.markdown(
        f"*Example:* a boy swimming 25m Back in **{ex_time}s** scores "
        f"1000 × ({ex_base} / {ex_time})³ = **{int(1000 * (ex_base / ex_time) ** 3)} points**."
    )
    st.caption(
        "Base times are elite-level, so young swimmers' 25m scores are typically well under 400 points. That's "
        "expected and fair within the 8 & under group, since everyone is scored the same way and "
        "8 & unders are only ranked against each other."
    )

# ---------- Filters ----------
board['Age Group'] = board['Age'].map(age_label)
age_order = ['8 & under'] + [str(a) for a in range(9, 16)] + ['16+']
age_options = [a for a in age_order if a in set(board['Age Group'])]
f1, f2 = st.columns([2, 3])
with f1:
    gender = st.segmented_control("Gender", ['Female', 'Male/Open'], default='Female', key='gender')
with f2:
    age_group = st.selectbox("Age group", age_options, key='age_group')

view = board[(board['Gender'] == (gender or 'Female')) & (board['Age Group'] == age_group)]
view = view.sort_values(['Total Points', 'Buckets Scored'], ascending=False).reset_index(drop=True)
# Everyone in the age group stays available for the swimmer breakdown; only scorers are ranked
all_in_group = view
view = view[view['Total Points'] > 0].reset_index(drop=True)
view.insert(0, 'Rank', view.index + 1)
unranked = all_in_group[all_in_group['Total Points'] == 0]

names = bucket_names_for_age(0 if age_group == '8 & under' else 9)
bucket_cols = {b: f"{b.replace('Bucket ', 'B')} {names[b]}" for b in BUCKETS}

# ---------- KPIs ----------
with st.container(horizontal=True):
    st.metric("Swimmers", len(view), border=True)
    st.metric("Leader", view['Name'].iloc[0] if len(view) else '-', border=True)
    st.metric("Top score", int(view['Total Points'].max()) if len(view) else 0, border=True)
    n_all_four = int((view['Buckets Scored'] == 4).sum())
    leader_all_four = len(view) > 0 and view['Buckets Scored'].iloc[0] == 4
    st.metric("Leader has all four buckets", "✓" if leader_all_four else "✗", border=True,
              delta=f"{n_all_four} of {len(view)} swimmers have all four", delta_color='off', delta_arrow='off')

st.subheader(f"{gender or 'Female'} rankings: age {age_group}")

if view.empty:
    st.info("No swimmers have scored points in this age group yet.")
else:
    tab_chart, tab_table = st.tabs([":material/bar_chart: Points chart", ":material/table: Leaderboard"])

    with tab_chart:
        chart_df = view.head(25).melt(id_vars=['Name', 'Total Points'], value_vars=BUCKETS,
                                      var_name='Bucket', value_name='Points')
        chart_df['Bucket'] = chart_df['Bucket'].map(bucket_cols)
        bars = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X('sum(Points):Q', title='WA points'),
            y=alt.Y('Name:N', sort=alt.EncodingSortField('Total Points', order='descending'), title=None, axis=alt.Axis(labelOverlap=False, labelLimit=110)),
            color=alt.Color('Bucket:N', legend=alt.Legend(orient='bottom', title=None),
                            scale=alt.Scale(domain=list(bucket_cols.values()), range=BUCKET_COLOURS)),
            order=alt.Order('Bucket:N'),
            tooltip=['Name', 'Bucket', 'Points', 'Total Points'],
        ).properties(height=max(300, 28 * view.head(25)['Name'].nunique()))
        st.altair_chart(bars)

    with tab_table:
        table = view[['Rank', 'Name', 'Age'] + BUCKETS + ['Total Points', 'Buckets Scored']].rename(columns=bucket_cols)
        st.dataframe(
            table, hide_index=True, height=min(600, 38 * (len(table) + 1)),
            column_config={
                'Total Points': st.column_config.ProgressColumn(
                    'Total points', format='%d', min_value=0, max_value=int(view['Total Points'].max()) or 1),
                'Buckets Scored': st.column_config.NumberColumn('Buckets', format='%d / 4'),
            },
        )
        st.download_button(":material/download: Download rankings CSV", table.to_csv(index=False).encode(),
                           file_name=f"rankings_2026_{(gender or 'Female').replace('/', '_')}_{age_group}.csv",
                           mime="text/csv")

if len(unranked):
    st.caption(
        f"Not ranked (no points yet): {', '.join(unranked['Name'])}. Their swims were either "
        "disqualified or not in a scoring bucket for their age. See the swimmer breakdown below."
    )

# ---------- Swimmer detail ----------
st.subheader("Swimmer breakdown")
pick = st.selectbox("Swimmer", all_in_group['Name'].tolist(), index=None, placeholder="Choose a swimmer")
if pick:
    row = all_in_group[all_in_group['Name'] == pick].iloc[0]
    swims = df_all[df_all['Athlete ID'] == row['Athlete ID']].sort_values('WA Points', ascending=False)

    def bucket_note(b):
        if row[b]:
            return row[f'{b} Event']
        tried = swims[swims['Bucket'] == b]
        return 'DQ' if len(tried) and (tried['Status'] != '').all() else 'not swum'

    with st.container(horizontal=True):
        st.metric("Total points", int(row['Total Points']), border=True)
        for b in BUCKETS:
            st.metric(bucket_cols[b], int(row[b]), border=True,
                      delta=bucket_note(b), delta_color='off', delta_arrow='off')

    detail = swims[['Counted', 'Event Number', 'Event', 'Bucket', 'Time', 'WA Points', 'Status']].copy()
    detail['Event Number'] = pd.to_numeric(detail['Event Number'], errors='coerce')
    detail['Note'] = ''
    detail.loc[detail['Status'] != '', 'Note'] = 'Disqualified, no points'
    detail.loc[(detail['Status'] == '') & detail['Bucket'].isna(), 'Note'] = (
        'Points shown for info only: not a scoring event at this age')
    detail.loc[(detail['Status'] == '') & detail['Bucket'].notna() & ~detail['Counted'], 'Note'] = (
        'Better score in this bucket already counted')
    detail['Bucket'] = detail['Bucket'].map(bucket_cols).fillna('Not a scoring event')

    # Branded breakdown table (navy header, counted swims highlighted in club green)
    def row_class(r):
        if r['Counted']:
            return 'counted'
        if r['Status']:
            return 'dq'
        return 'info' if r['Bucket'] == 'Not a scoring event' else ''

    body = ''.join(
        f"<tr class='{row_class(r)}'>"
        f"<td class='tick'>{'✓' if r['Counted'] else ''}</td>"
        f"<td class='num hide-sm'>{'' if pd.isna(r['Event Number']) else int(r['Event Number'])}</td>"
        f"<td>{html.escape(str(r['Event']))}</td><td class='hide-sm'>{html.escape(str(r['Bucket']))}</td>"
        f"<td class='num'>{html.escape(str(r['Time']))}</td><td class='num pts'>{int(r['WA Points'])}</td>"
        f"<td class='note'>{html.escape(r['Note'])}</td></tr>"
        for _, r in detail.iterrows()
    )
    st.html(f"""
<style>
.wsc-swims {{ width: 100%; border-collapse: separate; border-spacing: 0; font-family: 'Inter', sans-serif;
  font-size: 0.92rem; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(26,29,90,0.12); }}
.wsc-swims th {{ background: #1a1d5a; color: #fff; text-align: left; padding: 0.6rem 0.75rem; font-weight: 600; }}
.wsc-swims th.num, .wsc-swims td.num {{ text-align: right; }}
.wsc-swims td {{ padding: 0.55rem 0.75rem; border-bottom: 1px solid #e5e7eb; color: #2b2b2b; }}
.wsc-swims tr:last-child td {{ border-bottom: none; }}
.wsc-swims tr.counted td {{ background: #eefbe5; }}
.wsc-swims tr.counted td:first-child {{ border-left: 4px solid #7ef542; }}
.wsc-swims td.tick {{ color: #3a9a12; font-weight: 700; text-align: center; width: 3rem; }}
.wsc-swims td.pts {{ font-weight: 700; color: #2b1f5c; }}
.wsc-swims tr.dq td {{ color: #b42318; }}
.wsc-swims tr.info td {{ color: #6b7280; }}
.wsc-swims td.note {{ font-size: 0.82rem; color: #64748b; }}
.wsc-swims-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
@media (max-width: 640px) {{
  .wsc-swims {{ font-size: 0.82rem; }}
  .wsc-swims th, .wsc-swims td {{ padding: 0.45rem 0.4rem; }}
  .wsc-swims .hide-sm {{ display: none; }}
  .wsc-swims td.tick {{ width: 1.6rem; }}
  .wsc-swims td.note {{ font-size: 0.72rem; }}
}}
</style>
<div class="wsc-swims-wrap"><table class="wsc-swims">
  <thead><tr><th>✓</th><th class="num hide-sm">Event #</th><th>Event</th><th class="hide-sm">Bucket</th>
  <th class="num">Time</th><th class="num">Points</th><th>Note</th></tr></thead>
  <tbody>{body}</tbody>
</table></div>""")
    st.caption(f"Ages as at 31 December, as shown in the results file. Points use the base times in `{BASE_TIMES}`.")
