#!/usr/bin/env python3
"""
Streamlit Frontend - Data Ingest + Scoreboard Runner

Allows a user to:
- Select a championship year (creates `WSC_Club_Champs_{YEAR}` if missing)
- Upload .RES files and extract events via SwimEventExtractor into `cleaned_files/`
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
    raw_files = os.path.join(base_folder, "raw_files")
    cleaned = os.path.join(base_folder, "cleaned_files")
    results = os.path.join(base_folder, "championship_results")
    os.makedirs(raw_files, exist_ok=True)
    os.makedirs(cleaned, exist_ok=True)
    os.makedirs(results, exist_ok=True)
    return base_folder


def write_uploaded_file(uploaded, target_path: str) -> None:
    with open(target_path, "wb") as f:
        f.write(uploaded.getbuffer())


def ui_header():
    st.set_page_config(page_title="WSC - Ingest & Scoreboard", page_icon="🏊", layout="wide")
    
    # Load custom CSS
    try:
        with open("styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass
    
    # Worcester SC Header with Logo
    import base64
    header_html = """
    <div class="wsc-header">
        <div class="wsc-header-logo">
            <img src="data:image/jpeg;base64,{}" style="display: block; border-radius: 5px; width: 150px; max-width: 100%;">
        </div>
        <div class="wsc-header-text">
            <h1>Worcester Swimming Club</h1>
            <h2>Data Ingest & Scoreboard</h2>
            <p>Upload .RES files → Extract → Calculate → Export Results</p>
        </div>
    </div>
    """
    
    try:
        with open("cropped-WSC_Blue.jpg", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        st.markdown(header_html.format(img_base64), unsafe_allow_html=True)
    except:
        # Fallback without logo
        header_html_no_logo = """
        <div class="wsc-header">
            <div class="wsc-header-logo">
                <div style='font-size: clamp(2.5rem, 5vw, 4rem);'>🏊</div>
            </div>
            <div class="wsc-header-text">
                <h1>Worcester Swimming Club</h1>
                <h2>Data Ingest & Scoreboard</h2>
                <p>Upload .RES files → Extract → Calculate → Export Results</p>
            </div>
        </div>
        """
        st.markdown(header_html_no_logo, unsafe_allow_html=True)


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
    st.subheader("1) Upload .RES Files and Extract Events")

    uploaded_files = st.file_uploader(
        "MeetManager .RES files", 
        type=["RES", "res"], 
        accept_multiple_files=True,
        help="Upload one or more .RES files from MeetManager"
    )
    extract_btn = st.button("Extract events to cleaned_files")

    if extract_btn:
        if not uploaded_files:
            st.error("Please upload at least one .RES file first.")
        else:
            try:
                # Save uploaded .RES files to raw_files folder
                raw_files_dir = os.path.join(base_folder, "raw_files")
                os.makedirs(raw_files_dir, exist_ok=True)
                
                st.write(f"Saving {len(uploaded_files)} .RES file(s) to raw_files…")
                for uploaded_file in uploaded_files:
                    target_path = os.path.join(raw_files_dir, uploaded_file.name)
                    if os.path.exists(target_path):
                        st.warning(f"  ⚠️ {uploaded_file.name} already exists - overwriting")
                    write_uploaded_file(uploaded_file, target_path)
                    st.write(f"  ✓ {uploaded_file.name}")

                st.write("Extracting events from .RES files…")
                extractor = SwimEventExtractor(output_dir=base_folder)
                results: Dict[str, int] = extractor.extract_all_events_from_res(raw_files_dir, verbose=False)

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
    
    st.markdown("---")
    st.subheader("3) Preview Existing Data")
    
    tab1, tab2 = st.tabs(["📊 Cleaned Event Files", "🏆 Championship Results"])
    
    with tab1:
        st.markdown("**Preview extracted event data from cleaned_files/**")
        
        cleaned_dir = os.path.join(base_folder, "cleaned_files")
        if os.path.exists(cleaned_dir):
            csv_files = sorted([f for f in os.listdir(cleaned_dir) if f.startswith("event_") and f.endswith(".csv")])
            
            if csv_files:
                selected_event = st.selectbox(
                    "Select event to preview:",
                    options=csv_files,
                    format_func=lambda x: x.replace("event_", "Event ").replace(".csv", "")
                )
                
                if selected_event:
                    try:
                        import pandas as pd
                        event_path = os.path.join(cleaned_dir, selected_event)
                        df = pd.read_csv(event_path)
                        
                        st.write(f"**{selected_event}** - {len(df)} swimmers")
                        if len(df) > 0 and 'Event Name' in df.columns:
                            st.caption(f"Event: {df['Event Name'].iloc[0]}")
                        
                        st.dataframe(df, use_container_width=True, height=400)
                        
                        # Download button
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download {selected_event}",
                            data=csv,
                            file_name=selected_event,
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error loading {selected_event}: {e}")
            else:
                st.info("No cleaned event files found. Extract events first.")
        else:
            st.info("No cleaned_files folder found. Extract events first.")
    
    with tab2:
        st.markdown("**Preview championship scoreboard results**")
        
        results_dir = os.path.join(base_folder, "championship_results")
        
        if os.path.exists(results_dir):
            result_files = {
                "Boys Scoreboard": "championship_scoreboard_boys.csv",
                "Girls Scoreboard": "championship_scoreboard_girls.csv",
                "Age Group Winners": "championship_age_group_winners.csv",
                "Swimmer Narratives": "championship_swimmer_narratives.csv"
            }
            
            available_files = {name: file for name, file in result_files.items() 
                             if os.path.exists(os.path.join(results_dir, file))}
            
            if available_files:
                selected_result = st.selectbox(
                    "Select result to preview:",
                    options=list(available_files.keys())
                )
                
                if selected_result:
                    try:
                        import pandas as pd
                        result_path = os.path.join(results_dir, available_files[selected_result])
                        df = pd.read_csv(result_path)
                        
                        st.write(f"**{selected_result}** - {len(df)} rows")
                        st.dataframe(df, use_container_width=True, height=400)
                        
                        # Download button
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download {selected_result}",
                            data=csv,
                            file_name=available_files[selected_result],
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error loading {selected_result}: {e}")
            else:
                st.info("No championship results found. Run scoreboard first.")
        else:
            st.info("No championship_results folder found. Run scoreboard first.")


if __name__ == "__main__":
    main()



