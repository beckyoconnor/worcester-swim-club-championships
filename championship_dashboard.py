#!/usr/bin/env python3
"""
Club Championships Dashboard - Streamlit App
Interactive dashboard to view championship rankings by age group and gender.
"""

import streamlit as st
import pandas as pd
import os
from typing import Dict

# Compatibility for different Streamlit versions
if hasattr(st, 'cache_data'):
    cache_decorator = st.cache_data
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

# Worcester SC Branding - Custom CSS (matching website colors)
st.markdown("""
<style>
    /* Worcester SC Color Scheme - From Official Website */
    :root {
        --wsc-purple: #2b1f5c;
        --wsc-navy: #1a1444;
        --wsc-green: #7ef542;
        --wsc-dark-green: #5cb82f;
    }
    
    /* Header Styling */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Title Styling - White text */
    h1, h2, h3 {
        color: white !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Hide Sidebar - no longer needed */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Expand main content to full width */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #2b1f5c;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2b1f5c;
        color: white;
        border-radius: 5px;
        border: none;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #7ef542;
    }
    
    /* Mobile Responsive Styles */
    @media screen and (max-width: 768px) {
        /* Reduce padding on mobile */
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Make headers smaller on mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        h4 {
            font-size: 1rem !important;
        }
        
        /* Make metrics stack better on mobile */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        /* Improve dataframe display on mobile */
        .dataframe {
            font-size: 0.75rem !important;
        }
        
        /* Make download buttons full width on mobile */
        .stDownloadButton>button {
            width: 100% !important;
        }
        
        /* Reduce expander padding */
        .streamlit-expanderHeader {
            font-size: 0.9rem !important;
        }
        
        /* Stack columns on mobile for better readability */
        [data-testid="column"] {
            min-width: 100% !important;
        }
    }
    
    /* iPhone specific optimizations */
    @media screen and (max-width: 430px) {
        /* iPhone 14 Pro Max and smaller */
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* Smaller text for tables */
        .dataframe {
            font-size: 0.7rem !important;
        }
        
        /* Adjust metric spacing */
        [data-testid="metric-container"] {
            padding: 0.5rem !important;
        }
    }
        color: #2b1f5c;
    }
    
    /* Download Button - Worcester Green */
    .stDownloadButton>button {
        background-color: #7ef542;
        color: #2b1f5c;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .stDownloadButton>button:hover {
        background-color: #5cb82f;
        color: white;
    }
    
    /* Radio Buttons - Main page (not sidebar) */
    .stRadio > label {
        color: #1a1d5a !important;
        font-weight: 600;
    }
    
    .stRadio label {
        color: #1a1d5a !important;
    }
    
    /* Radio button text */
    .stRadio div[role="radiogroup"] label {
        color: #1a1d5a !important;
    }
    
    /* Selectbox - Main page */
    .stSelectbox > label {
        color: #1a1d5a !important;
        font-weight: 600;
    }
    
    .stSelectbox label {
        color: #1a1d5a !important;
    }
    
    /* Dataframe styling - Worcester Blue/Green headers */
    .dataframe thead tr th,
    .dataframe thead th,
    table thead tr th,
    table thead th,
    [data-testid="stDataFrame"] thead tr th,
    [data-testid="stDataFrame"] thead th {
        background-color: #1a1d5a !important;
        color: #7ef542 !important;
        border-bottom: 2px solid #7ef542 !important;
        font-weight: 700 !important;
        padding: 12px !important;
        text-transform: uppercase !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.5px !important;
    }
    
    .dataframe tbody tr:nth-child(odd) {
        background-color: #f8f9ff !important;
    }
    
    /* Additional table header targeting */
    div[data-testid="stDataFrame"] table thead tr,
    div[data-testid="stDataFrame"] table thead th {
        background-color: #1a1d5a !important;
        color: #7ef542 !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #ffffff !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #e0e7ff !important;
    }
    
    .dataframe {
        border: 2px solid #2b1f5c !important;
    }
    
    /* Info box */
    .stAlert {
        background-color: #f0f4ff;
        border-left: 4px solid #2b1f5c;
    }
    
    /* Replace Streamlit red theme with Worcester green */
    /* Checkbox styling */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        color: white !important;
    }
    
    /* Radio button active state - Worcester green */
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: transparent !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child > div {
        border-color: #1a1d5a !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"][data-checked="true"] > div:first-child > div {
        background-color: #7ef542 !important;
        border-color: #7ef542 !important;
    }
    
    /* Radio button inner circle when selected */
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] > div:first-child {
        background-color: #7ef542 !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] > div:first-child > div {
        background-color: #7ef542 !important;
        border-color: #7ef542 !important;
    }
    
    /* Selectbox dropdown - Worcester colors */
    .stSelectbox [data-baseweb="select"] {
        background-color: white;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #7ef542 !important;
    }
    
    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #7ef542 !important;
        box-shadow: 0 0 0 1px #7ef542 !important;
    }
    
    /* Multi-select tags - Worcester green */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #7ef542 !important;
        color: #2b1f5c !important;
    }
    
    /* Slider - Worcester green */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #7ef542 !important;
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stTickBar"] > div > div {
        background-color: #7ef542 !important;
    }
    
    /* Number input focus - Worcester green */
    .stNumberInput input:focus {
        border-color: #7ef542 !important;
        box-shadow: 0 0 0 1px #7ef542 !important;
    }
    
    /* Text input focus - Worcester green */
    .stTextInput input:focus {
        border-color: #7ef542 !important;
        box-shadow: 0 0 0 1px #7ef542 !important;
    }
    
    /* Text area focus - Worcester green */
    .stTextArea textarea:focus {
        border-color: #7ef542 !important;
        box-shadow: 0 0 0 1px #7ef542 !important;
    }
    
    /* Link color - Worcester green */
    a {
        color: #7ef542 !important;
    }
    
    a:hover {
        color: #5cb82f !important;
    }
    
    /* Progress bar - Worcester green */
    .stProgress > div > div > div > div {
        background-color: #7ef542 !important;
    }
    
    /* Spinner - Worcester green */
    .stSpinner > div {
        border-top-color: #7ef542 !important;
    }
    
    /* Tab selected state - Worcester green */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #7ef542 !important;
        color: #7ef542 !important;
    }
    
    /* File uploader - Worcester colors */
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        border-color: #2b1f5c !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #7ef542 !important;
        background-color: rgba(126, 245, 66, 0.1) !important;
    }
    
    /* Header container background */
    .header-container {
        background-color: #1e3a8a !important;
        padding: 2rem !important;
        border-radius: 10px !important;
        margin-bottom: 2rem !important;
    }
    
    /* Make sure columns in header have blue background */
    .header-container .element-container,
    .header-container [data-testid="column"],
    .header-container > div,
    .header-container .stImage {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


@cache_decorator
def get_swimmer_gender_map(df_all: pd.DataFrame) -> Dict[str, str]:
    """Map swimmer names to gender based on common name patterns."""
    swimmer_gender_map = {}
    
    # Common female name patterns
    female_patterns = [
        'ella', 'emma', 'lucy', 'sophie', 'charlotte', 'olivia', 'amelia', 'isabella', 
        'mia', 'ava', 'grace', 'lily', 'zoe', 'ruby', 'freya', 'chloe', 'millie', 
        'sophia', 'isla', 'poppy', 'rosie', 'maya', 'eva', 'harper', 'layla', 'luna', 
        'piper', 'penelope', 'nora', 'hazel', 'violet', 'aurora', 'savannah', 'audrey', 
        'brooklyn', 'bella', 'claire', 'skylar', 'ellie', 'madison', 'aria', 'anna', 
        'caroline', 'natalie', 'hailey', 'samantha', 'leah', 'riley', 'mila', 'aubrey', 
        'hannah', 'addison', 'eleanor', 'stella', 'paisley', 'allison'
    ]
    
    for name in df_all['Name'].unique():
        name_lower = name.lower()
        if any(pattern in name_lower for pattern in female_patterns):
            swimmer_gender_map[name] = 'Female'
        else:
            swimmer_gender_map[name] = 'Male'
    
    return swimmer_gender_map


@cache_decorator
def get_event_gender_map_from_csvs(folder: str) -> Dict[str, str]:
    """Map event numbers to gender by reading event names from CSV files."""
    import glob
    
    # Look for event files in cleaned_files subfolder
    cleaned_folder = os.path.join(folder, 'cleaned_files')
    if os.path.exists(cleaned_folder):
        search_folder = cleaned_folder
    else:
        search_folder = folder
    
    # Find all event CSV files
    csv_files = glob.glob(os.path.join(search_folder, 'event_*.csv'))
    
    event_gender_map = {}
    
    for csv_file in csv_files:
        try:
            # Extract event number from filename
            filename = os.path.basename(csv_file)
            event_number = filename.replace('event_', '').replace('.csv', '')
            
            # Read first row to get event name
            df = pd.read_csv(csv_file, nrows=1)
            if 'Event Name' in df.columns and len(df) > 0:
                event_name = str(df['Event Name'].iloc[0]).lower()
                
                # Determine gender based on event name
                if 'female' in event_name or 'girl' in event_name:
                    event_gender_map[event_number] = 'Female'
                elif 'male' in event_name or 'open/male' in event_name or 'boy' in event_name:
                    event_gender_map[event_number] = 'Male'
                elif 'open' in event_name:
                    event_gender_map[event_number] = 'Male'
                else:
                    # Default to Male for open events if not specified
                    event_gender_map[event_number] = 'Male'
            else:
                event_gender_map[event_number] = 'Unknown'
                
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue
    
    return event_gender_map


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
def filter_dataframe_memory_efficient(df: pd.DataFrame, gender: str, age: str, view_type: str) -> pd.DataFrame:
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
    
    # Apply view type filter (eligible vs all)
    if view_type == 'Championship Eligible Only':
        filtered_df = filtered_df[filtered_df['Eligible'] == True]
    
    # Sort by total points descending
    filtered_df = filtered_df.sort_values('Total_Points', ascending=False).reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1  # Start ranking from 1
    
    return filtered_df


@cache_decorator
def calculate_all_championship_scores(df_all: pd.DataFrame, event_gender_map: Dict[str, str], 
                                      min_categories: int = 0) -> pd.DataFrame:
    """
    Calculate championship scores for ALL swimmers (no minimum category requirement).
    
    Args:
        df_all: Dataframe with all events
        event_gender_map: Mapping of event numbers to gender
        min_categories: Minimum categories required (0 = show all)
    """
    # Add gender column if it doesn't exist, otherwise use existing one
    if 'Gender' not in df_all.columns:
        df_all['Event Number'] = df_all['Event Number'].astype(str)
        df_all['Gender'] = df_all['Event Number'].map(event_gender_map)
    else:
        # Gender column already exists, just ensure Event Number is string
        df_all['Event Number'] = df_all['Event Number'].astype(str)
    
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
            'Distance_Events': category_counts.get('Distance', 0),
            'Eligible': num_categories >= 5  # Mark if eligible for championship
        })
    
    df = pd.DataFrame(championship_results)
    
    # Create age groups (18+ is Open)
    bins = [0, 10, 12, 14, 16, 17, 100]
    labels = ['9-10', '11-12', '13-14', '15-16', '17', 'Open (18+)']
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    
    return df


def main():
    """Main Streamlit app."""
    
    # Worcester SC Header with Logo - Blue Background
    st.markdown("""
    <style>
    .wsc-header {
        background-color: #1a1d5a;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    .wsc-header-logo {
        flex-shrink: 0;
    }
    .wsc-header-text {
        flex-grow: 1;
    }
    .wsc-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .wsc-header h2 {
        color: white;
        margin: 0.5rem 0 0 0;
        font-size: 1.5rem;
        font-weight: 400;
    }
    .wsc-header p {
        color: #7ef542;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        # Load all data with optimized types
        df_all = load_all_events(events_folder)
        
        # Check if Gender column exists, if not create it from event names
        if 'Gender' not in df_all.columns:
            # Fallback: create gender mapping from event names
            event_gender_map = get_event_gender_map_from_csvs(events_folder)
            df_all['Event Number'] = df_all['Event Number'].astype(str)
            df_all['Gender'] = df_all['Event Number'].map(event_gender_map)
            df_all = df_all[df_all['Gender'] != 'Unknown'].copy()
        else:
            # Gender column exists, create event gender map for backward compatibility
            event_gender_map = df_all.groupby('Event Number')['Gender'].first().to_dict()
        
        # Calculate scores for all swimmers (no minimum)
        df_all_swimmers = calculate_all_championship_scores(df_all, event_gender_map, min_categories=0)
        
        # Also get eligible swimmers (5+ categories) - create view instead of copy
        df_eligible = df_all_swimmers[df_all_swimmers['Eligible'] == True]
        
        # Store filtered data for event rankings (before deleting df_all)
        df_all_with_gender = df_all.copy()
        
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
    st.markdown('<h3 style="color: #1a1d5a;">🔍 Select Filters</h3>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Gender filter
            gender_options = ['Male', 'Female']
            selected_gender = st.selectbox("Gender", gender_options, key='gender_filter')
        
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
            selected_gender, 
            selected_age, 
            'All Swimmers'  # Always show all swimmers
        )
        
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
            # Add CSS for tooltips
            st.markdown("""
            <style>
            .main-tooltip {
                position: relative;
                display: inline-block;
                cursor: help;
            }
            
            .main-tooltip .main-tooltiptext {
                visibility: hidden;
                width: 300px;
                background-color: #2b1f5c;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px 12px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -150px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.875rem;
                font-weight: 500;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            .main-tooltip .main-tooltiptext::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #2b1f5c transparent transparent transparent;
            }
            
            .main-tooltip:hover .main-tooltiptext {
                visibility: visible;
                opacity: 1;
            }
            
            .main-metric-label {
                font-size: 0.875rem;
                color: #64748b;
                font-weight: 600;
                margin-bottom: 0.25rem;
                border-bottom: 1px dotted #2b1f5c;
            }
            
            .main-metric-value {
                font-size: 2rem;
                color: #2b1f5c;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if len(df_display) > 0:
                avg_points = df_display['Total_Points'].mean()
                
                # Dynamic tooltip based on age selection
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
                # Dynamic tooltip for empty data
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
                
                # Dynamic tooltip based on age selection
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
        if selected_gender == 'Male':
            expander_title = f"📊 Boys Rankings - {age_text}"
        elif selected_gender == 'Female':
            expander_title = f"📊 Girls Rankings - {age_text}"
        else:
            expander_title = f"📊 All Rankings - {age_text}"
        
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
                    # Create horizontal bar chart with Altair
                    import altair as alt
                    
                    # Sort by Total Points for better visualization
                    chart_data = df_for_chart.sort_values('Total Points', ascending=False).head(20)  # Show top 20
                    chart_data = chart_data[['Name', 'Total Points']].copy()
                    
                    if len(chart_data) > 0:
                        # Create Altair chart
                        chart = alt.Chart(chart_data).mark_bar(color='#7ef542').encode(
                            x=alt.X('Total Points:Q', 
                                    axis=alt.Axis(labels=False, title='', ticks=False, grid=False)),
                            y=alt.Y('Name:N', 
                                    sort='-x',
                                    axis=alt.Axis(title='')),
                            tooltip=['Name', 'Total Points']
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
                filename = f"rankings_{selected_gender}_age{selected_age}.csv"
                st.download_button(
                    label="📥 Download Rankings as CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
            else:
                st.info("No swimmers found matching the selected filters.")
        
        with st.expander("🔍 Individual Swimmer Details", expanded=True):
            # Individual Swimmer Detail Section
            st.markdown("---")
            st.markdown("### 🔍 Swimmer Event Details")
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
                st.markdown(f"#### {selected_swimmer}")
                
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
                    
                    # Use CSS-based tooltip that works reliably in Streamlit
                    st.markdown(f"""
                    <style>
                    .tooltip {{
                        position: relative;
                        display: inline-block;
                        cursor: help;
                    }}
                    
                    .tooltip .tooltiptext {{
                        visibility: hidden;
                        width: 300px;
                        background-color: #2b1f5c;
                        color: #fff;
                        text-align: center;
                        border-radius: 6px;
                        padding: 8px 12px;
                        position: absolute;
                        z-index: 1;
                        bottom: 125%;
                        left: 50%;
                        margin-left: -150px;
                        opacity: 0;
                        transition: opacity 0.3s;
                        font-size: 0.875rem;
                        font-weight: 500;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    }}
                    
                    .tooltip .tooltiptext::after {{
                        content: "";
                        position: absolute;
                        top: 100%;
                        left: 50%;
                        margin-left: -5px;
                        border-width: 5px;
                        border-style: solid;
                        border-color: #2b1f5c transparent transparent transparent;
                    }}
                    
                    .tooltip:hover .tooltiptext {{
                        visibility: visible;
                        opacity: 1;
                    }}
                    
                    .metric-label {{
                        font-size: 0.875rem;
                        color: #64748b;
                        font-weight: 600;
                        margin-bottom: 0.25rem;
                        border-bottom: 1px dotted #2b1f5c;
                    }}
                    
                    .metric-value {{
                        font-size: 2rem;
                        color: #2b1f5c;
                        font-weight: bold;
                    }}
                    </style>
                    
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
                
                    # Add event gender
                    swimmer_events['Gender'] = swimmer_events['Event Number'].map(event_gender_map)
                
                    # Prepare display dataframe
                    event_display = swimmer_events[['Event Number', 'Event Name', 'Event Category', 'Time', 'WA Points']].copy()
                
                    # Format Time to hh:mm:ss:hs (hundredths of seconds)
                    def format_time(time_val):
                        if pd.isna(time_val) or time_val is None or time_val == '':
                            return '-'
                        
                        time_str = str(time_val).strip()
                        
                        # If already a dash, return as is
                        if time_str == '-':
                            return '-'
                        
                        # Check if time has colons (already formatted)
                        if ':' in time_str:
                            parts = time_str.split(':')
                            if len(parts) == 2:
                                # mm:ss.cs format -> 00:mm:ss:hs
                                mins, secs = parts
                                # Extract hundredths
                                if '.' in secs:
                                    sec_parts = secs.split('.')
                                    ss = sec_parts[0].zfill(2)
                                    hs = sec_parts[1][:2].ljust(2, '0')
                                    return f"00:{mins.zfill(2)}:{ss}:{hs}"
                                else:
                                    return f"00:{mins.zfill(2)}:{secs.zfill(2)}:00"
                            elif len(parts) == 3:
                                # hh:mm:ss format -> hh:mm:ss:hs
                                hours, mins, secs = parts
                                if '.' in secs:
                                    sec_parts = secs.split('.')
                                    ss = sec_parts[0].zfill(2)
                                    hs = sec_parts[1][:2].ljust(2, '0')
                                    return f"{hours.zfill(2)}:{mins.zfill(2)}:{ss}:{hs}"
                                else:
                                    return f"{hours.zfill(2)}:{mins.zfill(2)}:{secs.zfill(2)}:00"
                        else:
                            # Just seconds (e.g., "31.95") -> 00:00:ss:hs
                            try:
                                secs_float = float(time_str)
                                ss = int(secs_float)
                                hs = int((secs_float - ss) * 100)
                                return f"00:00:{str(ss).zfill(2)}:{str(hs).zfill(2)}"
                            except:
                                return time_str
                        
                        return time_str
                    
                    event_display['Time'] = event_display['Time'].apply(format_time)
                
                    event_display = event_display.rename(columns={
                        'Event Number': 'Event #',
                        'Event Name': 'Event',
                        'Event Category': 'Category',
                        'Time': 'Time',
                        'WA Points': 'FINA Points'
                    })
                
                    # Reset index to start from 1
                    event_display.insert(0, 'Rank', range(1, len(event_display) + 1))
                
                    st.markdown(f"**Total Events Competed: {len(swimmer_events)}**")
                
                    # Reset index for cleaner display
                    event_display_clean = event_display.reset_index(drop=True)
                
                    # Display swimmer events using standard dataframe (more reliable)
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
                    
                    # Show category breakdown
                    st.markdown("#### 📊 Category Breakdown")
                    
                    # Calculate statistics for each category
                    category_stats = swimmer_events.groupby('Event Category').agg({
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
                        'Events Count': '📈 Number of Events per Category',
                        'Avg Points': '📊 Average FINA Points per Category',
                        'Best Points': '🏆 Best FINA Points per Category',
                        'Total Points': '🎯 Total FINA Points per Category'
                    }
                    
                    # Create columns for better layout
                    col1, col2 = st.columns(2)
                    
                    for i, (measure, title) in enumerate(measures.items()):
                        # Alternate between columns
                        with col1 if i % 2 == 0 else col2:
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
                            
                            # Add some styling with custom CSS
                            st.markdown("""
                            <style>
                            .category-breakdown-table {
                                margin-bottom: 1rem;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            st.dataframe(formatted_df, use_container_width=True, key=f"category_{measure}")
                else:
                    st.warning(f"No events found for {selected_swimmer}")
            else:
                st.info("No swimmers found matching the selected filters.")
        
        # Event Rankings Section
        with st.expander("🏁 Event Rankings - View All Swimmers by Event", expanded=True):
            st.markdown("### Select an Event to View Rankings")
            
            # Filter events by selected gender first
            df_gender_events = df_all_with_gender[df_all_with_gender['Gender'] == selected_gender].copy()
            
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
                    
                    # Format time
                    def format_time_event(time_val):
                        if pd.isna(time_val) or time_val is None or time_val == '':
                            return '-'
                        time_str = str(time_val).strip()
                        if time_str == '-':
                            return '-'
                        if ':' in time_str:
                            parts = time_str.split(':')
                            if len(parts) == 2:
                                mins, secs = parts
                                if '.' in secs:
                                    sec_parts = secs.split('.')
                                    ss = sec_parts[0].zfill(2)
                                    hs = sec_parts[1][:2].ljust(2, '0')
                                    return f"00:{mins.zfill(2)}:{ss}:{hs}"
                                else:
                                    return f"00:{mins.zfill(2)}:{secs.zfill(2)}:00"
                            elif len(parts) == 3:
                                hours, mins, secs = parts
                                if '.' in secs:
                                    sec_parts = secs.split('.')
                                    ss = sec_parts[0].zfill(2)
                                    hs = sec_parts[1][:2].ljust(2, '0')
                                    return f"{hours.zfill(2)}:{mins.zfill(2)}:{ss}:{hs}"
                                else:
                                    return f"{hours.zfill(2)}:{mins.zfill(2)}:{secs.zfill(2)}:00"
                        else:
                            try:
                                secs_float = float(time_str)
                                ss = int(secs_float)
                                hs = int((secs_float - ss) * 100)
                                return f"00:00:{str(ss).zfill(2)}:{str(hs).zfill(2)}"
                            except:
                                return time_str
                        return time_str
                    
                    event_swimmers['Time'] = event_swimmers['Time'].apply(format_time_event)
                    
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
    
    # FINA Points Explanation
    st.markdown("""
    <style>
    .fina-explanation-container {
        background-color: #f0f4ff;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 5px solid #2b1f5c;
        box-shadow: 0 2px 8px rgba(43, 31, 92, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    

    
    st.markdown("#### What are FINA Points?")
    st.markdown("""
    **FINA Points** (now called **World Aquatics Points**) are a standardized scoring system used worldwide to compare swimming performances across different events, distances, and genders. 
    They provide a fair way to evaluate swimmers regardless of the specific event or distance they compete in.
    
    The system uses a mathematical formula: **P = 1000 × (B/T)³** where B is the base time (typically world record) and T is the swimmer's time.
    
    **Important**: FINA points are calculated against **open (adult) world records**, not age-specific records. This means younger swimmers are compared against adult standards, which is why age progression in FINA points is so significant.
    """)
    
    st.markdown("#### Why Age Matters:")
    st.markdown("As swimmers get older, they typically achieve higher FINA points due to:")
    st.markdown("""
    - **Physical Development:** Increased strength, power, and endurance
    - **Technical Improvement:** Better stroke technique and efficiency
    - **Training Experience:** More years of structured training
    - **Competition Experience:** Better race strategy and mental preparation
    """)
    
    st.markdown("#### What the Charts Show:")
    st.markdown("""
    The charts below show how average FINA points progress with age across different event categories. 
    Each line represents a different type of swimming event, helping you understand which events show the strongest age-related improvements 
    and how Worcester Swimming Club swimmers compare across different age groups.
    """)
    
    st.markdown("#### Sources & Further Reading:")
    st.markdown("""
    - [World Aquatics Official Website](https://www.worldaquatics.com) - Governing body for swimming
    - [Swim England](https://www.swimming.org) - UK swimming governing body
    - [FINA Points Calculator](https://sites.google.com/view/fina-points/home) - Calculate your own points
    - [Understanding FINA Points](https://thebingeful.com/what-are-fina-points-in-swimming/) - Detailed explanation
    """)
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
    st.markdown('#### Average FINA Points by Age and Event Category', unsafe_allow_html=True)
    
    # Create charts for average FINA points by age and event category
    if len(df_all_with_gender) > 0:
        # Calculate average FINA points by age and event category for each gender
        chart_data_male = df_all_with_gender[df_all_with_gender['Gender'] == 'Male'].copy()
        chart_data_female = df_all_with_gender[df_all_with_gender['Gender'] == 'Female'].copy()
        
        # Function to create chart data
        def create_chart_data(data, gender_name):
            if len(data) == 0:
                return None
            
            # Create a copy and cap ages at 18+ for swimmers over 18
            chart_data = data.copy()
            chart_data['Age_Group'] = chart_data['Age'].apply(lambda x: min(x, 18))
            
            # Group by age group and event category, calculate average WA Points
            chart_df = chart_data.groupby(['Age_Group', 'Event Category'])['WA Points'].mean().reset_index()
            chart_df = chart_df.rename(columns={'WA Points': 'Average FINA Points', 'Age_Group': 'Age'})
            
            # Convert age 18 to "18+" for display
            chart_df['Age'] = chart_df['Age'].apply(lambda x: '18+' if x == 18 else str(int(x)))
            
            return chart_df
        
        # Create chart data for both genders
        male_chart_data = create_chart_data(chart_data_male, 'Male')
        female_chart_data = create_chart_data(chart_data_female, 'Female')
        
        # Create charts using Altair
        import altair as alt
        
        # Define color palette for event categories
        category_colors = {
            'Sprint': '#FF6B6B',
            'Free': '#4ECDC4', 
            '100 Form': '#45B7D1',
            '200 Form': '#96CEB4',
            'IM': '#FFEAA7',
            'Distance': '#DDA0DD'
        }
        
        # Create male chart
        if male_chart_data is not None and len(male_chart_data) > 0:
            st.markdown("### Male/Open Swimmers")
            
            male_chart = alt.Chart(male_chart_data).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Age:N', title='Age', sort=['9', '10', '11', '12', '13', '14', '15', '16', '17', '18+']),
                y=alt.Y('Average FINA Points:Q', title='Average FINA Points'),
                color=alt.Color('Event Category:N', 
                              scale=alt.Scale(domain=list(category_colors.keys()), 
                                            range=list(category_colors.values())),
                              title='Event Category'),
                tooltip=['Age:N', 'Event Category:N', 'Average FINA Points:Q']
            ).properties(
                width=600,
                height=400,
                title='Average FINA Points by Age - Male/Open Swimmers'
            ).interactive()
            
            st.altair_chart(male_chart, use_container_width=True)
        
        # Create female chart
        if female_chart_data is not None and len(female_chart_data) > 0:
            st.markdown("###   Female Swimmers")
            
            female_chart = alt.Chart(female_chart_data).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Age:N', title='Age', sort=['9', '10', '11', '12', '13', '14', '15', '16', '17', '18+']),
                y=alt.Y('Average FINA Points:Q', title='Average FINA Points'),
                color=alt.Color('Event Category:N', 
                              scale=alt.Scale(domain=list(category_colors.keys()), 
                                            range=list(category_colors.values())),
                              title='Event Category'),
                tooltip=['Age:N', 'Event Category:N', 'Average FINA Points:Q']
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
                📊 Chart Explanation:
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
    
    # Footer with Worcester SC info
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #f8fafc; border-radius: 10px; margin-top: 2rem;'>
        <p style='color: #1e3a8a; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;'>
            Worcester Swimming Club
        </p>
        <p style='color: #64748b; font-size: 0.9rem; margin: 0.25rem 0;'>
            📧 Contact: <a href='https://worcestersc.co.uk/contact' style='color: #dc2626;'>worcestersc.co.uk/contact</a>
        </p>
        <p style='color: #64748b; font-size: 0.9rem; margin: 0.25rem 0;'>
            🌐 Website: <a href='https://worcestersc.co.uk' style='color: #dc2626;'>worcestersc.co.uk</a>
        </p>
        <p style='color: #94a3b8; font-size: 0.8rem; margin-top: 1rem;'>
            © 2024 Worcester Swimming Club - Club Championships Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()

