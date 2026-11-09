#!/usr/bin/env python3
"""
Worcester SC Club Championships 2026 - Streamlit dashboard.

Scoring (2026 rules): four event buckets, best WA points score per bucket,
total = sum of the four bucket scores (0 for a bucket not swum).

Data: drop the results exports (.RES) into WSC_Club_Champs_2026/raw_files/.
Until those arrive the app previews using the 2024 Wychavon meet files.
.LEF files are not needed (and are git-ignored) as they contain dates of birth.
"""

import base64
import os

import altair as alt
import pandas as pd
import streamlit as st

from champs_2026_scoring import (
    BUCKETS, BUCKET_NAMES_U9, BUCKET_NAMES_9PLUS, bucket_names_for_age,
    build_scoreboard, find_res_files, load_results, mark_counted,
)

DATA_FOLDER_2026 = 'WSC_Club_Champs_2026/raw_files'
SAMPLE_FOLDER = 'WSC_Club_champs_wychavon/raw_files'
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
</style>""")

# Worcester club colours for the bucket chart (navy, green, blue, light green)
BUCKET_COLOURS = ['#1a1d5a', '#7ef542', '#1e3a8a', '#b7f59a']


@st.cache_data(ttl=3600, max_entries=4)
def get_data(folder: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load_results(folder, BASE_TIMES)
    if df.empty:
        return df, pd.DataFrame()
    df = df[df['Club'] == HOME_CLUB].copy()
    if df.empty:
        return df, pd.DataFrame()
    df = mark_counted(df)
    return df, build_scoreboard(df)


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

using_sample = not find_res_files(DATA_FOLDER_2026)
folder = SAMPLE_FOLDER if using_sample else DATA_FOLDER_2026
if using_sample:
    st.warning(
        f"Showing the 2024 Wychavon results as sample data. Add the 2026 results (.RES) "
        f"files to `{DATA_FOLDER_2026}/` and the app will switch over automatically.",
        title="Preview mode", icon=":material/science:",
    )

df_all, board = get_data(folder)
if board.empty:
    st.error(f"No {HOME_CLUB} results found in `{folder}`.")
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
            y=alt.Y('Name:N', sort=alt.EncodingSortField('Total Points', order='descending'), title=None, axis=alt.Axis(labelOverlap=False, labelLimit=200)),
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
    st.dataframe(
        detail.drop(columns='Status'), hide_index=True,
        column_config={'Counted': st.column_config.CheckboxColumn('Counted'),
                       'Event Number': st.column_config.NumberColumn('Event #', format='%d')},
    )
    st.caption(f"Ages as at 31 December, as shown in the results file. Points use the base times in `{BASE_TIMES}`.")
