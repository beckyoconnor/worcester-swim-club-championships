#!/usr/bin/env python3
"""
Streamlit Frontend - Data Ingest + Scoreboard Runner

Allows a user to:
- Select a championship year (creates `WSC_Club_Champs_{YEAR}` if missing)
- Upload an Excel file and extract events via SwimEventExtractor into `cleaned_files/`
- Run the scoreboard process to generate results into `championship_results/`
"""

import os
import io
import time
import datetime as dt
import streamlit as st

from typing import List, Dict

# Local imports
from swim_event_extractor import SwimEventExtractor
from club_championships_scoreboard import (
    get_event_gender_map_from_csvs,
    load_all_events,
    export_all_events_union,
    calculate_championship_scores,
    create_age_groups,
    export_scoreboard,
    export_swimmer_narratives,
)


def list_existing_years(base_dir: str = ".") -> List[int]:
    years: List[int] = []
    try:
        for name in os.listdir(base_dir):
            if not name.startswith("WSC_Club_Champs_"):
                continue
            tail = name.split("_")[-1]
            if tail.isdigit():
                years.append(int(tail))
    except Exception:
        pass
    return sorted(set(years))


def ensure_year_structure(year: int) -> str:
    base_folder = f"WSC_Club_Champs_{year}"
    cleaned = os.path.join(base_folder, "cleaned_files")
    results = os.path.join(base_folder, "championship_results")
    os.makedirs(cleaned, exist_ok=True)
    os.makedirs(results, exist_ok=True)
    return base_folder


def write_uploaded_file(uploaded, target_path: str) -> None:
    with open(target_path, "wb") as f:
        f.write(uploaded.getbuffer())


def ui_header():
    st.set_page_config(page_title="WSC - Ingest & Scoreboard", page_icon="🏊", layout="wide")
    st.title("🏊 Worcester SC - Data Ingest & Scoreboard")
    st.caption("Upload Excel → Extract to cleaned_files → Run Scoreboard → Export results")


def main():
    ui_header()

    # Year selection
    existing_years = list_existing_years(".")
    default_year = dt.datetime.now().year
    col_year, col_info = st.columns([2, 3])
    with col_year:
        year_options = [str(y) for y in existing_years] + ["Custom…"] if existing_years else ["Custom…"]
        selected = st.selectbox("Championship Year", options=year_options, index=min(len(year_options)-1, year_options.index(str(default_year)) if str(default_year) in year_options else len(year_options)-1))
        if selected == "Custom…":
            year = int(st.number_input("Enter Year", min_value=2000, max_value=2100, value=default_year, step=1))
        else:
            year = int(selected)

    base_folder = ensure_year_structure(year)
    with col_info:
        st.info(f"Base folder: `{base_folder}`")

    st.markdown("---")
    st.subheader("1) Upload Excel and Extract Events")

    uploaded = st.file_uploader("Excel file (.xlsx/.xlsm)", type=["xlsx", "xlsm", "xls"], accept_multiple_files=False)
    extract_btn = st.button("Extract events to cleaned_files")

    if extract_btn:
        if not uploaded:
            st.error("Please upload an Excel file first.")
        else:
            try:
                # Persist upload to a temporary timestamped file
                ts = int(time.time())
                excel_filename = f"uploaded_{year}_{ts}.xlsx"
                excel_path = os.path.join(base_folder, excel_filename)
                write_uploaded_file(uploaded, excel_path)

                st.write("Loading workbook and extracting events…")
                extractor = SwimEventExtractor(excel_file=excel_path, output_dir=base_folder, auto_create_folder=False)
                results: Dict[str, int] = extractor.extract_all_events(verbose=False)

                total_events = len(results)
                total_swimmers = sum(results.values())
                st.success(f"✓ Extracted {total_events} events, {total_swimmers} total swimmers → `{base_folder}/cleaned_files`")
                if total_events:
                    # Show a small summary table
                    try:
                        import pandas as pd
                        df_summary = pd.DataFrame(sorted(results.items()), columns=["Event #", "Swimmers"])
                        st.dataframe(df_summary, use_container_width=True, height=300)
                    except Exception:
                        pass
            except Exception as e:
                st.error(f"Extraction failed: {e}")

    st.markdown("---")
    st.subheader("2) Run Scoreboard for Selected Year")
    run_btn = st.button("Run scoreboard and export results")

    if run_btn:
        try:
            st.write("Building event gender map…")
            event_gender_map = get_event_gender_map_from_csvs(base_folder)
            st.write(f"Mapped {len(event_gender_map)} events to gender")

            st.write("Loading all events from cleaned_files…")
            df_all = load_all_events(base_folder)
            st.write(f"Loaded {len(df_all)} rows across {df_all['Event Number'].nunique() if 'Event Number' in df_all.columns else 0} events")

            st.write("Exporting unioned events file (Parquet/CSV)…")
            export_all_events_union(base_folder, df_all)

            st.write("Calculating championship scores…")
            df_champs = calculate_championship_scores(df_all, event_gender_map)
            df_champs = create_age_groups(df_champs)

            st.write("Exporting scoreboards and narratives…")
            export_scoreboard(df_champs, base_folder)
            export_swimmer_narratives(base_folder, df_all, event_gender_map)

            results_dir = os.path.join(base_folder, "championship_results")
            produced = [
                os.path.join(results_dir, "championship_scoreboard_boys.csv"),
                os.path.join(results_dir, "championship_scoreboard_girls.csv"),
                os.path.join(results_dir, "championship_age_group_winners.csv"),
                os.path.join(results_dir, "championship_swimmer_narratives.csv"),
                os.path.join(results_dir, "events_all.parquet"),
            ]

            st.success("✓ Scoreboard complete. Files written under `championship_results/`.")
            for p in produced:
                exists = os.path.exists(p)
                st.write(("✅" if exists else "⚠️"), p)

        except Exception as e:
            st.error(f"Scoreboard run failed: {e}")


if __name__ == "__main__":
    main()



