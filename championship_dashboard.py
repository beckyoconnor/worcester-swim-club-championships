#!/usr/bin/env python3
"""
Club Championships Dashboard - Streamlit App
Interactive dashboard to view championship rankings by age group and gender.
"""

import streamlit as st
import pandas as pd
import os
import psutil
from typing import Dict

# Compatibility for different Streamlit versions
if hasattr(st, 'cache_data'):
    # Add conservative defaults for cache: 1 entry and 1-hour TTL
    def cache_decorator(func=None, *, max_entries=1, ttl=3600):
        return st.cache_data(func, max_entries=max_entries, ttl=ttl) if func else (lambda f: st.cache_data(f, max_entries=max_entries, ttl=ttl))
else:
    cache_decorator = st.cache

# Memory optimization settings
MEMORY_OPTIMIZATION = True


# Page configuration
st.set_page_config(
    page_title="Worcester SC - Club Championships",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global stylesheet injection
try:
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass


@cache_decorator
def load_all_events(folder: str) -> pd.DataFrame:
    """Load all event CSV files into a single dataframe with memory optimization."""
    # Look for event files in cleaned_files subfolder
    cleaned_folder = os.path.join(folder, 'cleaned_files')
    if os.path.exists(cleaned_folder):
        search_folder = cleaned_folder
    else:
        search_folder = folder
    
    csv_files = [f for f in os.listdir(search_folder) if f.startswith('event_') and f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {search_folder}")
        return pd.DataFrame()
    
    dfs = []
    for csv_file in csv_files:
        file_path = os.path.join(search_folder, csv_file)
        try:
            # Load with optimized data types for memory efficiency
            df = pd.read_csv(file_path, dtype={
                'Event Number': 'category',  # Use category for repeated values
                'Event Name': 'category',    # Use category for repeated values
                'Event Category': 'category', # Use category for repeated values
                'Name': 'object',            # Use object for names
                'Age': 'int8',              # Use smallest int type
                'Club': 'category',          # Use category for repeated values
                'Time': 'object',           # Keep as object for time format
                'WA Points': 'int16'        # Use int16 instead of int64
            })
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    if not dfs:
        return pd.DataFrame()
    
    # Concatenate and optimize memory usage
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Additional memory optimizations
    if MEMORY_OPTIMIZATION:
        # Convert string columns to category where beneficial
        for col in combined_df.columns:
            if combined_df[col].dtype == 'object':
                # Convert to category if it has many repeated values
                if combined_df[col].nunique() / len(combined_df) < 0.5:
                    combined_df[col] = combined_df[col].astype('category')
    
    return combined_df


@cache_decorator
def get_event_gender_map_from_csvs(folder: str) -> Dict[str, str]:
    """Build a mapping of event number -> gender by inspecting event CSV names.

    This is used as a fallback when input data lacks a Gender column.
    """
    import glob

    # Prefer cleaned_files subfolder if present
    cleaned_folder = os.path.join(folder, 'cleaned_files')
    search_folder = cleaned_folder if os.path.exists(cleaned_folder) else folder

    csv_files = glob.glob(os.path.join(search_folder, 'event_*.csv'))

    event_gender_map: Dict[str, str] = {}

    for csv_file in csv_files:
        try:
            # Extract event number from filename like event_101.csv
            basename = os.path.basename(csv_file)
            event_number = os.path.splitext(basename)[0].split('_')[-1]

            df = pd.read_csv(csv_file)
            if 'Event Name' in df.columns and len(df) > 0:
                event_name = str(df['Event Name'].iloc[0]).lower()

                if 'female' in event_name or 'girl' in event_name:
                    event_gender_map[event_number] = 'Female'
                elif 'male' in event_name or 'open/male' in event_name or 'boy' in event_name:
                    event_gender_map[event_number] = 'Male'
                elif 'open' in event_name:
                    # Treat open as Male for championship grouping
                    event_gender_map[event_number] = 'Male'
                else:
                    # Default if unspecified
                    event_gender_map[event_number] = 'Male'
            else:
                event_gender_map[event_number] = 'Unknown'
        except Exception:
            # On any error, mark unknown and continue
            event_gender_map[event_number] = 'Unknown'

    return event_gender_map


@cache_decorator
def filter_dataframe_memory_efficient(df: pd.DataFrame, gender: str, age: str) -> pd.DataFrame:
    """Memory-efficient filtering of dataframe."""
    # Start with a copy to avoid modifying original
    filtered_df = df.copy()
    
    # Apply gender filter
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    
    # Apply age filter
    if age != 'All':
        if age == '18+':
            filtered_df = filtered_df[filtered_df['Age'] >= 18]
        else:
            filtered_df = filtered_df[filtered_df['Age'] == int(age)]
    
    # Sort by total points descending
    filtered_df = filtered_df.sort_values('Total_Points', ascending=False).reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1  # Start ranking from 1
    
    return filtered_df


@cache_decorator
def calculate_all_championship_scores(df_all: pd.DataFrame, 
                                      min_categories: int = 0) -> pd.DataFrame:
    """
    Calculate championship scores for ALL swimmers (no minimum category requirement).
    
    Args:
        df_all: Dataframe with all events
        min_categories: Minimum categories required (0 = show all)
    """
    # Ensure Event Number is string and Gender column exists
    df_all['Event Number'] = df_all['Event Number'].astype(str)
    if 'Gender' not in df_all.columns:
        df_all['Gender'] = 'Unknown'
    
    # Remove Unknown gender entries
    df_all = df_all[df_all['Gender'] != 'Unknown'].copy()
    
    championship_results = []
    
    # Group by swimmer name
    for name, swimmer_events in df_all.groupby('Name'):
        # Get swimmer info
        age = swimmer_events['Age'].iloc[0]
        club = swimmer_events['Club'].iloc[0]
        # Use the most common gender across all events for this swimmer
        gender_counts = swimmer_events['Gender'].value_counts()
        if len(gender_counts) > 0:
            # Get the most frequent gender
            most_frequent_gender = gender_counts.index[0]
            most_frequent_count = gender_counts.iloc[0]
            
            # If there's a tie, use the gender from the event with highest WA Points
            if len(gender_counts) > 1 and gender_counts.iloc[1] == most_frequent_count:
                # Tie - use gender from best performance
                best_event = swimmer_events.loc[swimmer_events['WA Points'].idxmax()]
                gender = best_event['Gender']
            else:
                gender = most_frequent_gender
        else:
            gender = swimmer_events['Gender'].iloc[0]
        
        # Determine max races per category based on age
        max_per_category = 3 if age < 12 else 2
        
        # Sort by WA Points descending
        swimmer_events_sorted = swimmer_events.sort_values('WA Points', ascending=False)
        
        # For each category, take top N races
        category_events = {}
        for category in ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']:
            cat_events = swimmer_events_sorted[swimmer_events_sorted['Event Category'] == category]
            # Remove duplicates - keep only best score per unique event
            cat_events = cat_events.drop_duplicates(subset=['Event Number'], keep='first')
            # Take top N for this category
            top_n = cat_events.head(max_per_category)
            if len(top_n) > 0:
                category_events[category] = top_n
        
        # Count categories
        num_categories = len(category_events)
        
        # Apply minimum category filter
        if num_categories < min_categories:
            continue
        
        # Combine all category events and take top 8
        if category_events:
            all_category_events = pd.concat(category_events.values(), ignore_index=True)
            top_8_events = all_category_events.nlargest(8, 'WA Points')
        else:
            continue
        
        # Calculate totals
        total_points = top_8_events['WA Points'].sum()
        avg_points = top_8_events['WA Points'].mean()
        best_event_points = top_8_events['WA Points'].max()
        num_events = len(top_8_events)
        
        # Count events per category
        category_counts = top_8_events['Event Category'].value_counts().to_dict()
        
        championship_results.append({
            'Name': name,
            'Age': age,
            'Gender': gender,
            'Club': club,
            'Total_Points': total_points,
            'Average_Points': avg_points,
            'Best_Event_Points': best_event_points,
            'Events_Count': num_events,
            'Categories_Competed': num_categories,
            'Sprint_Events': category_counts.get('Sprint', 0),
            'Free_Events': category_counts.get('Free', 0),
            'Form_100_Events': category_counts.get('100 Form', 0),
            'Form_200_Events': category_counts.get('200 Form', 0),
            'IM_Events': category_counts.get('IM', 0),
            'Distance_Events': category_counts.get('Distance', 0)
        })
    
    df = pd.DataFrame(championship_results)
    
    # Create age groups (18+ is Open)
    bins = [0, 10, 12, 14, 16, 17, 100]
    labels = ['9-10', '11-12', '13-14', '15-16', '17', 'Open (18+)']
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    
    return df


@cache_decorator
def build_swimmer_narratives(df_all: pd.DataFrame) -> pd.DataFrame:
    """Build per-swimmer narratives describing included/excluded events.

    Returns a dataframe with columns:
      Name, Age, Gender, Total_Points, Narrative
    """
    if len(df_all) == 0:
        return pd.DataFrame(columns=['Name', 'Age', 'Gender', 'Total_Points', 'Narrative'])

    results = []
    for swimmer_name, swimmer_events in df_all.groupby('Name'):
        swimmer_events = swimmer_events.sort_values('WA Points', ascending=False).copy()
        age = int(swimmer_events['Age'].iloc[0])
        gender = swimmer_events['Gender'].iloc[0]

        # Category limit and selection
        limit_per_category = 3 if age < 12 else 2
        categories = ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']
        selected_rows = []
        excluded_due_to_limit = []

        # Ensure one best per Event Number
        swimmer_events = swimmer_events.drop_duplicates(subset=['Event Number'], keep='first')

        for cat in categories:
            cat_df = swimmer_events[swimmer_events['Event Category'] == cat]
            if len(cat_df) == 0:
                continue
            top_cat = cat_df.head(limit_per_category)
            selected_rows.append(top_cat)
            if len(cat_df) > len(top_cat):
                over_limit = cat_df.iloc[len(top_cat):]
                excluded_due_to_limit.extend(
                    [f"{row['Event Name']} ({int(row['WA Points'])} pts)" for _, row in over_limit.iterrows()]
                )

        included_numbers = []
        if selected_rows:
            all_candidates = pd.concat(selected_rows, ignore_index=True)
            top8 = all_candidates.nlargest(8, 'WA Points')
            included_numbers = top8['Event Number'].astype(str).tolist()
        else:
            top8 = pd.DataFrame(columns=swimmer_events.columns)

        # Included/Excluded lists
        included_by_cat = {}
        for _, row in top8.iterrows():
            cat = row['Event Category']
            included_by_cat.setdefault(cat, []).append(f"{row['Event Name']} – {int(row['WA Points'])} pts")

        excluded_other = []
        for _, row in swimmer_events.iterrows():
            if str(row['Event Number']) not in included_numbers:
                excluded_other.append(f"{row['Event Name']} – {int(row['WA Points'])} pts")

        total_points = int(top8['WA Points'].sum()) if len(top8) else 0
        avg_points = float(top8['WA Points'].mean()) if len(top8) else 0.0
        best_points = int(top8['WA Points'].max()) if len(top8) else 0

        # Helpers for natural language joins
        def _join(items, max_items=3):
            items = [i for i in items if i]
            if not items:
                return ""
            if len(items) > max_items:
                shown = items[:max_items]
                return ", ".join(shown) + f" and {len(items)-max_items} more"
            if len(items) == 1:
                return items[0]
            return ", ".join(items[:-1]) + f" and {items[-1]}"

        # Compose narrative (natural language)
        included_parts = []
        for cat in categories:
            if cat in included_by_cat:
                included_parts.append(f"{cat} (" + _join(included_by_cat[cat], max_items=2) + ")")
        included_sentence = _join(included_parts, max_items=4) if included_parts else "no events yet counted"

        reason_bits = []
        if excluded_due_to_limit:
            reason_bits.append("some races exceeded the per‑category limit: " + _join(excluded_due_to_limit, max_items=3))
        if excluded_other:
            reason_bits.append("others were just outside the swimmer’s top eight: " + _join(excluded_other, max_items=3))
        reasons_sentence = ("; ".join(reason_bits) + ".") if reason_bits else "All eligible races are currently counted."

        narrative = (
            f"{total_points} points from the top eight races (average {avg_points:.1f}, best {best_points}). "
            f"Included: {included_sentence}. {reasons_sentence}"
        )

        results.append({
            'Name': swimmer_name,
            'Age': age,
            'Gender': gender,
            'Total_Points': total_points,
            'Narrative': narrative,
            'IncludedShort': included_sentence,
        })

    df_narr = pd.DataFrame(results)
    return df_narr


@cache_decorator
def load_precomputed_scoreboard(base_folder: str) -> pd.DataFrame | None:
    """Load precomputed championship scoreboard (boys+girls) if available.

    Expects CSVs under `<base_folder>/championship_results/` as written by
    `club_championships_scoreboard.export_scoreboard()`.
    Returns a dataframe matching the columns used by the dashboard, or None.
    """
    try:
        results_dir = os.path.join(base_folder, 'championship_results')
        boys_csv = os.path.join(results_dir, 'championship_scoreboard_boys.csv')
        girls_csv = os.path.join(results_dir, 'championship_scoreboard_girls.csv')
        if not (os.path.exists(boys_csv) and os.path.exists(girls_csv)):
            return None
        df_boys = pd.read_csv(boys_csv)
        df_girls = pd.read_csv(girls_csv)
        df_boys['Gender'] = 'Male'
        df_girls['Gender'] = 'Female'
        df = pd.concat([df_boys, df_girls], ignore_index=True)
        # Ensure required columns exist and types are consistent
        expected_cols = [
            'Name', 'Age', 'Gender', 'Club', 'Total_Points', 'Average_Points',
            'Best_Event_Points', 'Events_Count', 'Categories_Competed',
            'Sprint_Events', 'Free_Events', 'Form_100_Events', 'Form_200_Events',
            'IM_Events', 'Distance_Events'
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0 if 'Events' in col or 'Points' in col else ''
        # Order columns (not strictly necessary, but helps consistency)
        df = df[expected_cols + [c for c in df.columns if c not in expected_cols]]
        return df
    except Exception:
        return None


@cache_decorator
def load_swimmer_narratives_csv(base_folder: str) -> pd.DataFrame | None:
    """Load prebuilt swimmer narratives if present."""
    try:
        csv_path = os.path.join(base_folder, 'championship_results', 'championship_swimmer_narratives.csv')
        if not os.path.exists(csv_path):
            return None
        return pd.read_csv(csv_path)
    except Exception:
        return None


@cache_decorator
def load_events_prefer_union(base_folder: str) -> pd.DataFrame:
    """Load all events, preferring a single union file if present.

    Order of preference:
      1) championship_results/events_all.parquet (fastest)
      2) championship_results/events_all.csv
      3) Fall back to concatenating cleaned_files/event_*.csv
    """
    # Require Parquet (preferred); fall back to per-file loader only if missing
    results_dir = os.path.join(base_folder, 'championship_results')
    pq_path = os.path.join(results_dir, 'events_all.parquet')
    if os.path.exists(pq_path):
        try:
            return pd.read_parquet(pq_path)
        except Exception:
            pass
    # Fallback to per-file loader
    return load_all_events(base_folder)
def main():
    """Main Streamlit app."""
    
    # Worcester SC Header with Logo - styles now in styles.css
    
    # Create header using pure HTML
    header_html = """
    <div class="wsc-header">
        <div class="wsc-header-logo">
            <img src="data:image/jpeg;base64,{}" width="150" style="display: block; border-radius: 5px;">
        </div>
        <div class="wsc-header-text">
            <h1>Worcester Swimming Club</h1>
            <h2>Club Championships Dashboard 2024</h2>
            <p>Interactive Rankings & Competition Analysis</p>
        </div>
    </div>
    """
    
    # Load and encode the logo
    import base64
    try:
        with open("cropped-WSC_Blue.jpg", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        st.markdown(header_html.format(img_base64), unsafe_allow_html=True)
    except:
        # Fallback without logo
        header_html_no_logo = """
        <div class="wsc-header">
            <div class="wsc-header-logo">
                <div style='font-size: 4rem;'>🏊</div>
            </div>
            <div class="wsc-header-text">
                <h1>Worcester Swimming Club</h1>
                <h2>Club Championships Dashboard 2024</h2>
                <p>Interactive Rankings & Competition Analysis</p>
            </div>
        </div>
        """
        st.markdown(header_html_no_logo, unsafe_allow_html=True)
    
    # Configuration
    events_folder = 'WSC_Club_Champs_2024'
    
    # Check if events folder exists
    if not os.path.exists(events_folder):
        st.error(f"❌ Events folder not found: {events_folder}")
        return
    
    # Load data with memory optimization
    with st.spinner("Loading championship data..."):
        # Load all data (prefer union file for performance)
        df_all = load_events_prefer_union(events_folder)
        
        # Ensure Gender column exists; derive from event CSVs if needed
        if 'Gender' not in df_all.columns:
            df_all['Event Number'] = df_all['Event Number'].astype(str)
            event_gender_map = get_event_gender_map_from_csvs(events_folder)
            df_all['Gender'] = df_all['Event Number'].map(event_gender_map)
            df_all = df_all[df_all['Gender'] != 'Unknown'].copy()
        else:
            # Ensure Event Number is string for consistency
            df_all['Event Number'] = df_all['Event Number'].astype(str)
        
        # Reuse the same dataframe (read-only below) to avoid extra memory copy
        df_all_with_gender = df_all
        
        # Always compute scores for ALL swimmers (no minimum) so counts aren't limited to eligible only
        # Precomputed CSVs contain only championship-eligible swimmers; that undercounts.
        df_precomputed = load_precomputed_scoreboard(events_folder)
        df_all_swimmers = calculate_all_championship_scores(df_all, min_categories=0)

        # Try to load prebuilt narratives; if missing, build on the fly
        df_narratives = load_swimmer_narratives_csv(events_folder)
        if df_narratives is None or len(df_narratives) == 0:
            df_narratives = build_swimmer_narratives(df_all)
        
        # Memory cleanup - remove intermediate variables
        del df_all
        if MEMORY_OPTIMIZATION:
            import gc
            gc.collect()
    
    # Display memory usage info (optional)
    if MEMORY_OPTIMIZATION:
        import psutil
        memory_usage = psutil.virtual_memory()
        st.sidebar.markdown(f"**Memory Usage:** {memory_usage.percent:.1f}%")
        st.sidebar.markdown(f"**Available:** {memory_usage.available / (1024**3):.1f} GB")
    
    # Championship Rules Expander
    with st.expander("📋 Championship Rules & Scoring", expanded=False):
        st.markdown("""
        ### Worcester Swimming Club Championships
        
        Our Club Championships are held every year and they usually take place over a number of sessions. 
        All swimmers are encouraged to enter, although younger swimmers may only do so at the discretion of their coaches. 
        All strokes and distances are swum, but you can only enter certain events dependent upon your age.
        
        #### Age Group Cups
        Age Group Cups are awarded to the best swimmer in an age group.
        
        #### Championship Format
        This year the format has changed in order to try and encourage swimmers to participate in a larger pool of events. 
        Competition is spread across **6 categories**:
        
        | Category | Events |
        |----------|--------|
        | **Sprint** | 50m Free, Back, Breast, and Fly |
        | **Free** | 100m, 200m, and 400m Freestyle |
        | **100 Form** | 100m Back, Breast, and Fly |
        | **200 Form** | 200m Back, Breast, and Fly |
        | **IM** | 100m, 200m, and 400m Individual Medley |
        | **Distance** | 800m and 1500m |
        
        #### Scoring Rules
        Age group trophies will be awarded to the swimmer who gains the highest collated number of **FINA/WA points**, 
        from their **top 8 events** across the 6 categories.
        
        **Category Limits:**
        - **Under 12s**: Maximum of **3 races** counted per category
        - **12 and over**: Maximum of **2 races** counted per category
        
        Your **best 8 events** (by WA Points) will count toward your total score, respecting the category limits based on your age.
        """)
    
    # Filters in main page using form
    # Use stylesheet-driven headings
    st.markdown('<h3 class="wsc-h3">Championship Scoreboard</h3>', unsafe_allow_html=True)
    st.markdown('Select Age and Gender then Retrieve Data', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Gender filter (UI shows 'Male/Open' but data uses 'Male')
            gender_options = ['Male/Open', 'Female']
            selected_gender = st.selectbox("Gender", gender_options, key='gender_filter')
            gender_filter_value = 'Male' if selected_gender == 'Male/Open' else 'Female'
        
        with col2:
            # Get all ages from all swimmers for initial display, group 18+ together
            all_ages = sorted(df_all_swimmers['Age'].unique().tolist())
            # Create age options with 18+ grouping
            age_options = ['All']
            for age in all_ages:
                if age < 18:
                    age_options.append(str(age))
                elif age >= 18 and '18+' not in age_options:
                    age_options.append('18+')
            selected_age = st.selectbox("Age", age_options, key='age_filter')
        
        with col3:
            # Submit button
            st.write("")  # Spacing
            submit_button = 'yes'
    
    # Only run analysis if button is pressed
    if submit_button:
        # Use memory-efficient filtering
        df_display = filter_dataframe_memory_efficient(
            df_all_swimmers, 
            gender_filter_value, 
            selected_age
        )
        
        # Global tooltip styles now provided by styles.css
        
        # Display summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="main-tooltip">
                <div class="main-metric-label">Total Swimmers</div>
                <div class="main-metric-value">{len(df_display)}</div>
                <span class="main-tooltiptext">Total number of swimmers in the current filtered view</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if len(df_display) > 0:
                avg_points = df_display['Total_Points'].mean()
                if selected_age == 'All':
                    avg_tooltip_text = "Average total points across all swimmers. Based on top 8 races per swimmer with category limits: max 3 races per category (under 12) and max 2 races per category (12 and over)."
                elif selected_age == '18+':
                    avg_tooltip_text = "Average total points for 18+ swimmers. Based on top 8 races per swimmer with max 2 races per category (12 and over)."
                else:
                    age_int = int(selected_age)
                    category_limit = 3 if age_int < 12 else 2
                    age_text = "under 12" if age_int < 12 else "12 and over"
                    avg_tooltip_text = f"Average total points for age {selected_age} swimmers. Based on top 8 races per swimmer with max {category_limit} races per category ({age_text})."
                st.markdown(f"""
                <div class="main-tooltip">
                    <div class="main-metric-label">Average Total Points</div>
                    <div class="main-metric-value">{avg_points:.0f}</div>
                    <span class="main-tooltiptext">{avg_tooltip_text}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                if selected_age == 'All':
                    empty_tooltip_text = "Average total points across all swimmers. Based on top 8 races per swimmer with category limits: max 3 races per category (under 12) and max 2 races per category (12 and over)."
                elif selected_age == '18+':
                    empty_tooltip_text = "Average total points for 18+ swimmers. Based on top 8 races per swimmer with max 2 races per category (12 and over)."
                else:
                    age_int = int(selected_age)
                    category_limit = 3 if age_int < 12 else 2
                    age_text = "under 12" if age_int < 12 else "12 and over"
                    empty_tooltip_text = f"Average total points for age {selected_age} swimmers. Based on top 8 races per swimmer with max {category_limit} races per category ({age_text})."
                st.markdown(f"""
                <div class="main-tooltip">
                    <div class="main-metric-label">Average Total Points</div>
                    <div class="main-metric-value">0</div>
                    <span class="main-tooltiptext">{empty_tooltip_text}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if len(df_display) > 0:
                highest_score = df_display['Total_Points'].max()
                if selected_age == 'All':
                    highest_tooltip_text = "Highest total points achieved by any swimmer. Based on their top 8 races with category limits: max 3 races per category (under 12) and max 2 races per category (12 and over)."
                elif selected_age == '18+':
                    highest_tooltip_text = "Highest total points for 18+ swimmers. Based on their top 8 races with max 2 races per category (12 and over)."
                else:
                    age_int = int(selected_age)
                    category_limit = 3 if age_int < 12 else 2
                    age_text = "under 12" if age_int < 12 else "12 and over"
                    highest_tooltip_text = f"Highest total points for age {selected_age} swimmers. Based on their top 8 races with max {category_limit} races per category ({age_text})."
                st.markdown(f"""
                <div class="main-tooltip">
                    <div class="main-metric-label">Highest Score</div>
                    <div class="main-metric-value">{highest_score:.0f}</div>
                    <span class="main-tooltiptext">{highest_tooltip_text}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Dynamic tooltip for empty data
                if selected_age == 'All':
                    empty_highest_tooltip_text = "Highest total points achieved by any swimmer. Based on their top 8 races with category limits: max 3 races per category (under 12) and max 2 races per category (12 and over)."
                elif selected_age == '18+':
                    empty_highest_tooltip_text = "Highest total points for 18+ swimmers. Based on their top 8 races with max 2 races per category (12 and over)."
                else:
                    age_int = int(selected_age)
                    category_limit = 3 if age_int < 12 else 2
                    age_text = "under 12" if age_int < 12 else "12 and over"
                    empty_highest_tooltip_text = f"Highest total points for age {selected_age} swimmers. Based on their top 8 races with max {category_limit} races per category ({age_text})."
                
                st.markdown(f"""
                <div class="main-tooltip">
                    <div class="main-metric-label">Highest Score</div>
                    <div class="main-metric-value">0</div>
                    <span class="main-tooltiptext">{empty_highest_tooltip_text}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Display championship title
        st.markdown("---")
        age_text = f"Age {selected_age}" if selected_age != 'All' else 'All Ages'
        
        # Wrap rankings in an expander
        if gender_filter_value == 'Male':
            expander_title = f"Male/Open Rankings - {age_text}"
        elif gender_filter_value == 'Female':
            expander_title = f"Female Rankings - {age_text}"
        else:
            expander_title = f"All Rankings - {age_text}"
        
        with st.expander(expander_title, expanded=True):
            # Display rankings table
            if len(df_display) > 0:
                # Prepare display dataframe
                df_show = df_display.copy()
                df_show['Rank'] = df_show.index
            
                # Select columns to display (removed Eligible and Categories)
                display_columns = [
                    'Rank', 'Name', 'Age', 
                    'Total_Points', 'Average_Points', 'Events_Count', 
                    'Sprint_Events', 'Free_Events', 'Form_100_Events', 
                    'Form_200_Events', 'IM_Events', 'Distance_Events'
                ]
            
                # Rename columns for display
                column_names = {
                    'Rank': 'Rank',
                    'Name': 'Name',
                    'Age': 'Age',
                    'Total_Points': 'Total Points',
                    'Average_Points': 'Avg Points',
                    'Events_Count': 'Events',
                    'Sprint_Events': 'Sprint',
                    'Free_Events': 'Free',
                    'Form_100_Events': '100 Form',
                    'Form_200_Events': '200 Form',
                    'IM_Events': 'IM',
                    'Distance_Events': 'Distance'
                }
        
                df_show_renamed = df_show[display_columns].rename(columns=column_names)
        
                # Keep numeric version for chart
                df_for_chart = df_show_renamed.copy()
                df_for_chart['Total Points'] = df_display['Total_Points'].values
                
                # Format numbers for table display
                df_show_renamed['Total Points'] = df_show_renamed['Total Points'].apply(lambda x: f"{x:.0f}")
                df_show_renamed['Avg Points'] = df_show_renamed['Avg Points'].apply(lambda x: f"{x:.1f}")
            
                # Create tabs for chart and table (chart first)
                tab1, tab2 = st.tabs(["📈 Points Chart", "📊 Data Table"])
                
                with tab1:
                    # Join narratives for tooltips (prefer IncludedShort -> compact included events list)
                    try:
                        cols = ['Name']
                        if 'IncludedShort' in df_narratives.columns:
                            cols.append('IncludedShort')
                        if 'Narrative' in df_narratives.columns:
                            cols.append('Narrative')
                        df_with_narr = df_for_chart.merge(df_narratives[cols].drop_duplicates('Name'), on='Name', how='left')
                    except Exception:
                        df_with_narr = df_for_chart.copy()

                    # Create horizontal bar chart with Altair
                    import altair as alt
                    
                    # Sort by Total Points for better visualization
                    chart_data = df_with_narr.sort_values('Total Points', ascending=False).head(20)
                    # Prefer compact included list if available; fallback to Narrative; else blank
                    if 'IncludedShort' in df_with_narr.columns:
                        chart_data['Included'] = df_with_narr['IncludedShort'].fillna('')
                    elif 'Narrative' in df_with_narr.columns:
                        chart_data['Included'] = df_with_narr['Narrative'].fillna('')
                    else:
                        chart_data['Included'] = ''
                    chart_data = chart_data[['Name', 'Total Points', 'Included']].copy()
                    
                    if len(chart_data) > 0:
                        # Create Altair chart
                        chart = alt.Chart(chart_data).mark_bar(color='#7ef542').encode(
                            x=alt.X('Total Points:Q', 
                                    axis=alt.Axis(labels=False, title='', ticks=False, grid=False)),
                            y=alt.Y('Name:N', 
                                    sort='-x',
                                    axis=alt.Axis(title='')),
                            tooltip=[alt.Tooltip('Name:N', title='Swimmer'),
                                     alt.Tooltip('Total Points:Q', title='Total Points', format='.0f'),
                                     alt.Tooltip('Included:N', title='Included Events')]
                        ).properties(
                            title='Top Swimmers by Total Points',
                            height=max(400, len(chart_data) * 30)
                        )
                        
                        # Add text labels at the end of bars
                        text = chart.mark_text(
                            align='left',
                            baseline='middle',
                            dx=3,
                            color='#1a1d5a',  # Worcester blue
                            fontSize=12
                        ).encode(
                            text=alt.Text('Total Points:Q', format='.0f')
                        )
                        
                        # Combine bar and text
                        final_chart = (chart + text).configure_view(
                            strokeWidth=0
                        ).configure_axis(
                            labelFontSize=10
                        )
                        
                        st.altair_chart(final_chart, use_container_width=True)
                    else:
                        st.info("No data available for chart")
            
                with tab2:
                    # Display table using standard Streamlit dataframe (more reliable)
                    st.dataframe(df_show_renamed, height=600, use_container_width=True)
                
                # Download button
                csv = df_show_renamed.to_csv(index=False).encode('utf-8')
                filename = f"rankings_{selected_gender.replace('/', '_')}_age{selected_age}.csv"
                st.download_button(
                    label="📥 Download Rankings as CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
            else:
                st.info("No swimmers found matching the selected filters.")
        
        with st.expander("Individual Swimmer Details", expanded=True):
            # Individual Swimmer Detail Section
            st.markdown("---")
            st.markdown('<h3 class="wsc-h3">Swimmer Event Details</h3>', unsafe_allow_html=True)
            st.markdown("Select a swimmer to view their individual event breakdown:")
        
            # Create a dropdown with swimmer names
            swimmer_names = sorted(df_display['Name'].unique().tolist())
            selected_swimmer = st.selectbox(
                "Choose a swimmer:",
                options=[''] + swimmer_names,
                index=0
            )
        
            if selected_swimmer:
                # Get swimmer's info
                swimmer_info = df_display[df_display['Name'] == selected_swimmer].iloc[0]
            
                # Display swimmer summary
                st.markdown(f'<h4 class="wsc-h4">{selected_swimmer}</h4>', unsafe_allow_html=True)
                
                # First row of metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Age", swimmer_info['Age'])
                with col_b:
                    # Determine category limit based on age
                    category_limit = 3 if swimmer_info['Age'] < 12 else 2
                    age_text = "under 12" if swimmer_info['Age'] < 12 else "12 and over"
                    
                    # Create tooltip content for Total Points
                    total_tooltip_text = f"Total points from top 8 races across all categories. Maximum {category_limit} races per category ({age_text})."
                    
                    # Tooltip markup only (styles in styles.css)
                    st.markdown(f"""
                    <div class="tooltip">
                        <div class="metric-label">Total Points</div>
                        <div class="metric-value">{swimmer_info['Total_Points']:.0f}</div>
                        <span class="tooltiptext">{total_tooltip_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    st.metric("Categories Competed", swimmer_info['Categories_Competed'])
                
                # Second row of metrics with tooltips
                col_d, col_e, col_f = st.columns(3)
                with col_d:
                    # Average Points tooltip
                    avg_tooltip_text = f"Average FINA points per race from top 8 races. Calculated as total points ÷ number of races counted."
                    
                    st.markdown(f"""
                    <div class="tooltip">
                        <div class="metric-label">Average Points</div>
                        <div class="metric-value">{swimmer_info['Average_Points']:.1f}</div>
                        <span class="tooltiptext">{avg_tooltip_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_e:
                    # Best Event Points tooltip
                    best_tooltip_text = f"Highest FINA points achieved in a single race from the top 8 races counted towards championship total."
                    
                    st.markdown(f"""
                    <div class="tooltip">
                        <div class="metric-label">Best Event Points</div>
                        <div class="metric-value">{swimmer_info['Best_Event_Points']:.0f}</div>
                        <span class="tooltiptext">{best_tooltip_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_f:
                    st.metric("Events Counted", swimmer_info['Events_Count'])
            
                # Get all events for this swimmer
                swimmer_events = df_all_with_gender[df_all_with_gender['Name'] == selected_swimmer].copy()
            
                if len(swimmer_events) > 0:
                    # Sort by WA Points descending
                    swimmer_events = swimmer_events.sort_values('WA Points', ascending=False)
                
                    # Ensure gender column exists (it should already be present)
                    if 'Gender' not in swimmer_events.columns:
                        swimmer_events['Gender'] = 'Unknown'
                
                    # Determine which events are INCLUDED in championship scoring for this swimmer
                    limit_per_category = 3 if swimmer_info['Age'] < 12 else 2
                    categories_for_scoring = ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']
                    selected_per_cat = []
                    for cat in categories_for_scoring:
                        cat_events = swimmer_events[swimmer_events['Event Category'] == cat]
                        if len(cat_events) == 0:
                            continue
                        cat_events = cat_events.drop_duplicates(subset=['Event Number'], keep='first')
                        top_cat = cat_events.head(limit_per_category)
                        if len(top_cat) > 0:
                            selected_per_cat.append(top_cat)
                    included_event_numbers = set()
                    if len(selected_per_cat) > 0:
                        all_candidates = pd.concat(selected_per_cat, ignore_index=True)
                        top8 = all_candidates.nlargest(8, 'WA Points')
                        included_event_numbers = set(top8['Event Number'].astype(str).tolist())
                
                    # Prepare display dataframe
                    event_display = swimmer_events[['Event Number', 'Event Name', 'Event Category', 'Time', 'WA Points']].copy()
                    event_display['Included'] = event_display['Event Number'].astype(str).apply(lambda x: '✅' if x in included_event_numbers else '')
                
                    # Format Time to hh:mm:ss.hh (hundredths of seconds)
                    def format_time(time_val):
                        if pd.isna(time_val) or time_val is None or time_val == '':
                            return '-'
                        s = str(time_val).strip()
                        if s == '-':
                            return '-'
                        # If already normalized (HH:MM:SS.HS), keep as-is
                        import re
                        if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{2}$", s):
                            return s
                        # HH:MM:SS(.HS)? -> HH:MM:SS.HS
                        m = re.match(r"^(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d{1,2}))?$", s)
                        if m:
                            hh = int(m.group(1)); mm = int(m.group(2)); ss = int(m.group(3)); hs = int(m.group(4)) if m.group(4) else 0
                            return f"{hh:02d}:{mm:02d}:{ss:02d}.{hs:02d}"
                        # MM:SS(.HS)? -> 00:MM:SS.HS
                        m = re.match(r"^(\d{1,2}):(\d{1,2})(?:\.(\d{1,2}))?$", s)
                        if m:
                            mm = int(m.group(1)); ss = int(m.group(2)); hs = int(m.group(3)) if m.group(3) else 0
                            return f"00:{mm:02d}:{ss:02d}.{hs:02d}"
                        # SS.HS -> 00:00:SS.HS
                        m = re.match(r"^(\d{1,2})\.(\d{1,2})$", s)
                        if m:
                            ss = int(m.group(1)); hs = int(m.group(2))
                            return f"00:00:{ss:02d}.{hs:02d}"
                        # Seconds only -> 00:00:SS.00
                        if re.match(r"^\d+$", s):
                            ss = int(s)
                            return f"00:00:{ss:02d}.00"
                        # Seconds with decimals -> 00:00:SS.HS
                        if re.match(r"^\d+\.\d+$", s):
                            parts = s.split('.')
                            ss = int(parts[0]); hs = int(parts[1])
                            return f"00:00:{ss:02d}.{hs:02d}"
                        return s
                    
                    event_display['Time'] = event_display['Time'].apply(format_time)
                    # Ensure any lingering microsecond-style values are trimmed to 2 decimals
                    try:
                        event_display['Time'] = event_display['Time'].astype(str).str.replace(
                            r'^(\d{2}:\d{2}:\d{2})\.(\d{2}).*$', r'\1.\2', regex=True
                        )
                    except Exception:
                        pass
                
                    event_display = event_display.rename(columns={
                        'Event Number': 'Event #',
                        'Event Name': 'Event',
                        'Event Category': 'Category',
                        'Time': 'Time',
                        'WA Points': 'FINA Points'
                    })
                
                    # Reorder columns and remove numeric rank
                    event_display = event_display[['Included', 'Event #', 'Event', 'Category', 'Time', 'FINA Points']]
                
                    st.markdown(f"**Total Events Competed: {len(swimmer_events)}**")
                
                    # Reset index for cleaner display
                    event_display_clean = event_display.reset_index(drop=True)
                
                    # Conditional highlight: lightly highlight included rows
                    def _highlight_row(row: pd.Series):
                        return ['background-color: #e8f7ee' if row.get('Included', '') == '✅' else '' for _ in row]
                    try:
                        styled = event_display_clean.style.apply(_highlight_row, axis=1)
                        st.dataframe(styled, height=400, use_container_width=True)
                    except Exception:
                        st.dataframe(event_display_clean, height=400, use_container_width=True)
                    
                    # Download button for swimmer's events
                    csv_swimmer = event_display_clean.to_csv(index=False).encode('utf-8')
                    swimmer_filename = f"{selected_swimmer.replace(' ', '_')}_events.csv"
                    st.download_button(
                        label=f"📥 Download {selected_swimmer}'s Events",
                        data=csv_swimmer,
                        file_name=swimmer_filename,
                        mime="text/csv"
                    )
                    
                    # Show category breakdown (larger heading)
                    st.markdown('<h3 class="wsc-h3">Category Breakdown</h3>', unsafe_allow_html=True)

                    st.markdown(' View number of included events counted by event category (only those used in scoring)')

                    # Interactive category chips with hover details
                    chip_html_parts = ["<div class='cat-chip-wrap'>"]
                    for cat in ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']:
                        cat_df = swimmer_events[swimmer_events['Event Category'] == cat].copy()
                        if len(cat_df) == 0:
                            continue
                        # Best per event number, sorted by points
                        cat_df = cat_df.drop_duplicates(subset=['Event Number'], keep='first')
                        cat_df = cat_df.sort_values('WA Points', ascending=False)
                        # mark included with star
                        def label_row(r):
                            included = str(r['Event Number']) in included_event_numbers
                            dot = "<span class='cat-dot'></span>" if included else ""
                            return f"{dot}{int(r['Event Number'])} - {r['Event Name']} ({int(r['WA Points'])} pts)"
                        items = [label_row(r) for _, r in cat_df.iterrows()]
                        tooltip_items = ''.join([f"<div class='cat-tooltip-item'>• {it}</div>" for it in items])
                        chip_html_parts.append(
                            f"<div class='cat-chip'>{cat}<div class='cat-tooltip'><div class='cat-tooltip-title'>{cat} events</div>{tooltip_items}<div class='cat-tooltip-note'><span class='cat-dot'></span> indicates events included in scoring</div></div></div>"
                        )
                    chip_html_parts.append("</div>")
                    st.markdown(''.join(chip_html_parts), unsafe_allow_html=True)
                    
                    # Filter to only INCLUDED events for category stats
                    swimmer_events_included = swimmer_events.copy()
                    swimmer_events_included['__included'] = swimmer_events_included['Event Number'].astype(str).apply(
                        lambda x: x in included_event_numbers
                    )
                    swimmer_events_included = swimmer_events_included[swimmer_events_included['__included']]
                    
                    # Calculate statistics for each category (only included events)
                    category_stats = swimmer_events_included.groupby('Event Category').agg({
                        'Event Number': 'count',
                        'WA Points': ['mean', 'max', 'sum']
                    }).round(1)
                    
                    # Flatten multi-level columns
                    category_stats.columns = ['Events Count', 'Avg Points', 'Best Points', 'Total Points']
                    
                    # Transpose so categories are columns
                    category_stats_T = category_stats.T
                    
                    # Fill any missing values with 0 to ensure consistency
                    category_stats_T = category_stats_T.fillna(0)
                    
                    # Create separate dataframes for each measure with better formatting
                    measures = {
                        'Events Count': 'Number of Events per Category',
                        'Avg Points': 'Average FINA Points per Category',
                        'Best Points': 'Best FINA Points per Category',
                        'Total Points': 'Total FINA Points per Category'
                    }
                    
                    # Create columns for better layout
                    col1, col2 = st.columns(2)
                    
                    for i, (measure, title) in enumerate(measures.items()):
                        # Alternate between columns
                        with (col1 if i % 2 == 0 else col2):
                            st.markdown(f"**{title}**")
                            # Create dataframe with proper formatting
                            measure_df = pd.DataFrame([category_stats_T.loc[measure]])
                            # Set better index name
                            if 'Count' in measure:
                                measure_df.index = ['Events']
                                # Format as integers and ensure no None values
                                formatted_df = measure_df.astype(int)
                            else:
                                measure_df.index = ['Points']
                                # Format as floats with 1 decimal place and ensure no None values
                                formatted_df = measure_df.round(1)
                            # Ensure all values are properly formatted (replace any remaining None with 0)
                            formatted_df = formatted_df.fillna(0)
                            # Styling provided by styles.css (.category-breakdown-table)
                            st.dataframe(formatted_df, use_container_width=True, key=f"category_{measure}")
                else:
                    st.warning(f"No events found for {selected_swimmer}")
            else:
                st.info("No swimmers found matching the selected filters.")
        
        # Event Rankings Section
        with st.expander("🏁 Event Rankings - View All Swimmers by Event", expanded=True):
            st.markdown('<h3 class="wsc-h3">Select an Event to View Rankings</h3>', unsafe_allow_html=True)
            
            # Filter events by selected gender first
            df_gender_events = df_all_with_gender[df_all_with_gender['Gender'] == gender_filter_value].copy()
            
            # Get unique events for the selected gender
            event_options = df_gender_events[['Event Number', 'Event Name']].drop_duplicates().sort_values('Event Number')
            event_list = [f"{row['Event Number']} - {row['Event Name']}" for _, row in event_options.iterrows()]
            
            selected_event = st.selectbox(
                "Choose an event:",
                options=event_list,
                key="event_selector"
            )
            
            if selected_event:
                # Extract event number
                event_num = selected_event.split(' - ')[0].strip()
                
                # Get all swimmers for this event from the selected gender
                event_swimmers = df_gender_events[df_gender_events['Event Number'].astype(str) == event_num].copy()
                
                # Apply age filter if not 'All'
                if selected_age != 'All':
                    if selected_age == '18+':
                        event_swimmers = event_swimmers[event_swimmers['Age'] >= 18]
                    else:
                        event_swimmers = event_swimmers[event_swimmers['Age'] == int(selected_age)]
                
                if len(event_swimmers) > 0:
                    # Sort by WA Points descending (best performance first)
                    event_swimmers = event_swimmers.sort_values('WA Points', ascending=False)
                    
                    # Add rank
                    event_swimmers['Rank'] = range(1, len(event_swimmers) + 1)
                    
                    # Format time for rankings to hh:mm:ss.hh
                    def format_time_event(time_val):
                        if pd.isna(time_val) or time_val is None or time_val == '':
                            return '-'
                        s = str(time_val).strip()
                        if s == '-':
                            return '-'
                        import re
                        if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{2}$", s):
                            return s
                        m = re.match(r"^(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d{1,2}))?$", s)
                        if m:
                            hh = int(m.group(1)); mm = int(m.group(2)); ss = int(m.group(3)); hs = int(m.group(4)) if m.group(4) else 0
                            return f"{hh:02d}:{mm:02d}:{ss:02d}.{hs:02d}"
                        m = re.match(r"^(\d{1,2}):(\d{1,2})(?:\.(\d{1,2}))?$", s)
                        if m:
                            mm = int(m.group(1)); ss = int(m.group(2)); hs = int(m.group(3)) if m.group(3) else 0
                            return f"00:{mm:02d}:{ss:02d}.{hs:02d}"
                        m = re.match(r"^(\d{1,2})\.(\d{1,2})$", s)
                        if m:
                            ss = int(m.group(1)); hs = int(m.group(2))
                            return f"00:00:{ss:02d}.{hs:02d}"
                        if re.match(r"^\d+$", s):
                            ss = int(s)
                            return f"00:00:{ss:02d}.00"
                        if re.match(r"^\d+\.\d+$", s):
                            parts = s.split('.')
                            ss = int(parts[0]); hs = int(parts[1])
                            return f"00:00:{ss:02d}.{hs:02d}"
                        return s
                    
                    event_swimmers['Time'] = event_swimmers['Time'].apply(format_time_event)
                    # Enforce 2-decimal display even if upstream produced microseconds
                    try:
                        event_swimmers['Time'] = event_swimmers['Time'].astype(str).str.replace(
                            r'^(\d{2}:\d{2}:\d{2})\.(\d{2}).*$', r'\1.\2', regex=True
                        )
                    except Exception:
                        pass
                    
                    # Display event information
                    st.markdown(f"**Event:** {selected_event}")
                    st.markdown(f"**Category:** {event_swimmers['Event Category'].iloc[0]}")
                    st.markdown(f"**Total Swimmers:** {len(event_swimmers)}")
                    
                    # Prepare display dataframe
                    event_display = event_swimmers[['Rank', 'Name', 'Age', 'Time', 'WA Points']].copy()
                    event_display.columns = ['Rank', 'Name', 'Age', 'Time', 'FINA Points']
                    
                    # Display table
                    st.dataframe(event_display, height=400, use_container_width=True)
                    
                    # Download button
                    csv_event = event_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download Event {event_num} Rankings",
                        data=csv_event,
                        file_name=f"event_{event_num}_rankings.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"No data found for this event.")
    
    # FINA Points Analysis Charts
    st.markdown("---")
    
    # FINA Points Explanation (styles in styles.css -> .fina-explanation-container)
    

    
    st.markdown('<h3 class="wsc-h3">What are FINA Points?</wsc-h4>', unsafe_allow_html=True)
    st.markdown("""
    **FINA Points** (now called **World Aquatics Points**) are a standardized scoring system used worldwide to compare swimming performances across different events, distances, and genders. 
    They provide a fair way to evaluate swimmers regardless of the specific event or distance they compete in.
    
    The system uses a mathematical formula: **P = 1000 × (B/T)³** where B is the base time (typically world record) and T is the swimmer's time.
    
    **Important**: FINA points are calculated against **open (adult) world records**, not age-specific records. This means younger swimmers are compared against adult standards, which is why age progression in FINA points is so significant.
    """)
    
    st.markdown('<h4 class="wsc-h4">Why Age Matters:</h4>', unsafe_allow_html=True)
    st.markdown("As swimmers get older, they typically achieve higher FINA points due to:")
    st.markdown("""
    - **Physical Development:** Increased strength, power, and endurance
    - **Technical Improvement:** Better stroke technique and efficiency
    - **Training Experience:** More years of structured training
    - **Competition Experience:** Better race strategy and mental preparation
    """)
    
    st.markdown('<h4 class="wsc-h4">What the Charts Show:</h4>', unsafe_allow_html=True)
    st.markdown("""
    The charts below show how average FINA points progress with age across different event categories. 
    Each line represents a different type of swimming event, helping you understand which events show the strongest age-related improvements 
    and how Worcester Swimming Club swimmers compare across different age groups.
    """)
    
    st.markdown('<wsc-h4>Sources & Further Reading:</wsc-h4>', unsafe_allow_html=True)
    st.markdown("""
    - [World Aquatics Official Website](https://www.worldaquatics.com) - Governing body for swimming
    - [Swim England](https://www.swimming.org) - UK swimming governing body
    - [FINA Points Calculator](https://sites.google.com/view/fina-points/home) - Calculate your own points
    - [Understanding FINA Points](https://thebingeful.com/what-are-fina-points-in-swimming/) - Detailed explanation
    """)
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<h4 class="wsc-h4">Average FINA Points by Age and Event Category</h4>', unsafe_allow_html=True)
    
    # Create charts for average FINA points by age and event category
    if len(df_all_with_gender) > 0:
        # Calculate average FINA points by age and event category for each gender
        chart_data_male = df_all_with_gender[df_all_with_gender['Gender'] == 'Male/Open'].copy()
        chart_data_female = df_all_with_gender[df_all_with_gender['Gender'] == 'Female'].copy()
        
        # Function to create chart data
        def create_chart_data(data, gender_name):
            if len(data) == 0:
                return None
            
            # Create a copy and cap ages at 18+ for swimmers over 18
            chart_data = data.copy()
            chart_data['Age_Group'] = chart_data['Age'].apply(lambda x: min(x, 18))
            
            # Group by age group and event category, calculate average WA Points
            grouped = chart_data.groupby(['Age_Group', 'Event Category'])
            chart_df = grouped['WA Points'].mean().reset_index()
            chart_df = chart_df.rename(columns={'WA Points': 'Average FINA Points', 'Age_Group': 'Age'})

            # Find min/max average event within each (Age_Group, Event Category)
            # Compute per-event (Event Name) averages first
            per_event = chart_data.groupby(['Age_Group', 'Event Category', 'Event Name'])['WA Points'].mean().reset_index()
            # Robustly pick max/min using groupby + head after sorting (works even for single groups)
            max_ev = (
                per_event
                .sort_values(['Age_Group', 'Event Category', 'WA Points'], ascending=[True, True, False])
                .groupby(['Age_Group', 'Event Category'], as_index=False)
                .head(1)
                [['Age_Group', 'Event Category', 'Event Name', 'WA Points']]
                .rename(columns={'Event Name': 'Max Event', 'WA Points': 'Max Event Avg'})
            )
            min_ev = (
                per_event
                .sort_values(['Age_Group', 'Event Category', 'WA Points'], ascending=[True, True, True])
                .groupby(['Age_Group', 'Event Category'], as_index=False)
                .head(1)
                [['Age_Group', 'Event Category', 'Event Name', 'WA Points']]
                .rename(columns={'Event Name': 'Min Event', 'WA Points': 'Min Event Avg'})
            )

            # Merge onto chart_df
            chart_df = chart_df.merge(max_ev, how='left', left_on=['Age','Event Category'], right_on=['Age_Group','Event Category'])
            chart_df = chart_df.merge(min_ev, how='left', left_on=['Age','Event Category'], right_on=['Age_Group','Event Category'])
            chart_df = chart_df.drop(columns=['Age_Group_x','Age_Group_y'])
            
            # Convert age 18 to "18+" for display
            chart_df['Age'] = chart_df['Age'].apply(lambda x: '18+' if x == 18 else str(int(x)))
            
            return chart_df
        
        # Create chart data for both genders
        male_chart_data = create_chart_data(chart_data_male, 'Male')
        female_chart_data = create_chart_data(chart_data_female, 'Female')
        
        # Create charts using Altair
        import altair as alt
        
        # Define color palette for event categories (Worcester SC palette)
        category_colors = {
            'Sprint': '#7ef542',     # Worcester green
            'Free': '#1a1d5a',       # Club navy
            '100 Form': '#2b1f5c',   # Worcester indigo/purple
            '200 Form': '#5cb82f',   # Darker club green
            'IM': '#1e3a8a',         # Worcester blue
            'Distance': '#25408f'    # Deep blue variant for contrast
        }
        
        # Create male chart
        if male_chart_data is not None and len(male_chart_data) > 0:
            st.markdown('<h3 class="wsc-h3">Male/Open Swimmers</h3>', unsafe_allow_html=True)
            
            male_chart = alt.Chart(male_chart_data).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Age:N', title='Age', sort=['9', '10', '11', '12', '13', '14', '15', '16', '17', '18+']),
                y=alt.Y('Average FINA Points:Q', title='Average FINA Points'),
                color=alt.Color('Event Category:N', 
                              scale=alt.Scale(domain=list(category_colors.keys()), 
                                            range=list(category_colors.values())),
                              title='Event Category'),
                tooltip=[
                    alt.Tooltip('Age:N', title='Age'),
                    alt.Tooltip('Event Category:N', title='Event Category'),
                    alt.Tooltip('Average FINA Points:Q', title='Average FINA Points', format='.1f'),
                    alt.Tooltip('Max Event:N', title='Top Avg Event'),
                    alt.Tooltip('Max Event Avg:Q', title='Top Avg Points', format='.1f'),
                    alt.Tooltip('Min Event:N', title='Lowest Avg Event'),
                    alt.Tooltip('Min Event Avg:Q', title='Lowest Avg Points', format='.1f')
                ]
            ).properties(
                width=600,
                height=400,
                title='Average FINA Points by Age - Male/Open Swimmers'
            ).interactive()
            
            st.altair_chart(male_chart, use_container_width=True)
        
        # Create female chart
        if female_chart_data is not None and len(female_chart_data) > 0:
            st.markdown('<h3 class="wsc-h3">Female Swimmers</h3>', unsafe_allow_html=True)
            
            female_chart = alt.Chart(female_chart_data).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Age:N', title='Age', sort=['9', '10', '11', '12', '13', '14', '15', '16', '17', '18+']),
                y=alt.Y('Average FINA Points:Q', title='Average FINA Points'),
                color=alt.Color('Event Category:N', 
                              scale=alt.Scale(domain=list(category_colors.keys()), 
                                            range=list(category_colors.values())),
                              title='Event Category'),
                tooltip=[
                    alt.Tooltip('Age:N', title='Age'),
                    alt.Tooltip('Event Category:N', title='Event Category'),
                    alt.Tooltip('Average FINA Points:Q', title='Average FINA Points', format='.1f'),
                    alt.Tooltip('Max Event:N', title='Top Avg Event'),
                    alt.Tooltip('Max Event Avg:Q', title='Top Avg Points', format='.1f'),
                    alt.Tooltip('Min Event:N', title='Lowest Avg Event'),
                    alt.Tooltip('Min Event Avg:Q', title='Lowest Avg Points', format='.1f')
                ]
            ).properties(
                width=600,
                height=400,
                title='Average FINA Points by Age - Female Swimmers'
            ).interactive()
            
            st.altair_chart(female_chart, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
            <p style='color: #1a1d5a; font-weight: 600; margin-bottom: 0.5rem;'>
                Chart Explanation:
            </p>
            <ul style='color: #64748b; margin: 0; padding-left: 1.5rem;'>
                <li>Each line represents a different event category (Sprint, Free, 100 Form, 200 Form, IM, Distance)</li>
                <li>X-axis shows swimmer age, Y-axis shows average FINA points achieved</li>
                <li>Points on each line show the average FINA points for swimmers of that age in that event category</li>
                <li>Hover over points to see exact values</li>
                <li>Generally, older swimmers tend to achieve higher FINA points due to physical development and experience</li>
            </ul>
    </div>
    """, unsafe_allow_html=True)
    else:
        st.info("No data available for FINA points analysis charts.")
    
    # Championship rules
    st.markdown("---")
    
    # Footer with Worcester SC info - styled via stylesheet
    st.markdown("""
    <div class='wsc-footer'>
        <h4>Worcester Swimming Club</h4>
        <p>📧 Contact: <a href='https://worcestersc.co.uk/contact'>worcestersc.co.uk/contact</a></p>
        <p>🌐 Website: <a href='https://worcestersc.co.uk'>worcestersc.co.uk</a></p>
        <p style='margin-top: 1rem;'>© 2024 Worcester Swimming Club - Club Championships Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Memory usage monitoring (for Streamlit Community Cloud) - moved to bottom
    with st.expander("🔧 System Information", expanded=False):
        try:
            # Get process memory usage (more accurate for containers)
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024**2)
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Count active processes (rough estimate of concurrent users)
            streamlit_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'streamlit' in proc.info['name'].lower():
                        streamlit_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Streamlit Community Cloud has ~2GB RAM limit
            cloud_limit_gb = 2.0
            cloud_limit_mb = cloud_limit_gb * 1024
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("App Memory Used", f"{process_memory_mb:.0f} MB", f"{(process_memory_mb/cloud_limit_mb)*100:.1f}%")
            with col2:
                st.metric("Cloud Limit", f"{cloud_limit_gb:.0f} GB")
            with col3:
                st.metric("CPU Usage", f"{cpu_percent:.1f}%")
            with col4:
                st.metric("Active Sessions", f"{streamlit_processes}")
            
            # Memory warning based on actual cloud limits
            memory_percent = (process_memory_mb / cloud_limit_mb) * 100
            if memory_percent > 80:
                st.warning("⚠️ High memory usage detected! Consider restarting the app.")
            elif memory_percent > 60:
                st.info("ℹ️ Moderate memory usage")
            else:
                st.success("✅ Memory usage is normal")
            
            # Concurrency warning
            if streamlit_processes > 5:
                st.warning(f"⚠️ {streamlit_processes} active sessions detected. High concurrency may impact performance.")
            elif streamlit_processes > 2:
                st.info(f"ℹ️ {streamlit_processes} active sessions. Monitor memory usage.")
            
            # Additional info
            st.caption("💡 Streamlit Community Cloud provides ~2GB RAM. Each concurrent user increases memory usage. Restart the app if memory usage gets too high.")
                
        except Exception as e:
            st.error(f"Could not retrieve system info: {e}")

if __name__ == '__main__':
    main()

