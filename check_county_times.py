#!/usr/bin/env python3
"""
Check which swimmers achieved county qualifying times
Compares all swimmer performances against WCSA 2026 standards
"""

import pandas as pd
import re
from datetime import datetime

def time_to_seconds(time_str):
    """Convert time string to seconds for comparison"""
    if pd.isna(time_str):
        return float('inf')
    
    time_str = str(time_str).strip()
    
    # Handle HH:MM:SS.HH format (e.g., 00:02:31.75)
    match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{2})', time_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        hundredths = int(match.group(4))
        return hours * 3600 + minutes * 60 + seconds + hundredths / 100
    
    # Handle MM:SS.HH format (e.g., 02:31.75)
    match = re.match(r'(\d+):(\d{2})\.(\d{2})', time_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        hundredths = int(match.group(3))
        return minutes * 60 + seconds + hundredths / 100
    
    # Handle SS.HH format (e.g., 31.75)
    match = re.match(r'(\d+)\.(\d{2})', time_str)
    if match:
        seconds = int(match.group(1))
        hundredths = int(match.group(2))
        return seconds + hundredths / 100
    
    return float('inf')

def seconds_to_time(seconds):
    """Convert seconds back to time string"""
    if seconds == float('inf') or pd.isna(seconds):
        return ""
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    
    if minutes > 0:
        return f"{minutes}:{secs:05.2f}"
    else:
        return f"{secs:.2f}"

def normalize_event_name(event_name):
    """Normalize event names for matching"""
    # Remove gender prefixes
    event_name = re.sub(r'^(Open/Male|Open/Female|Female|Male)\s+', '', event_name, flags=re.IGNORECASE)
    
    # Standardize event names
    replacements = {
        'Freestyle': 'Free',
        'Backstroke': 'Back',
        'Breaststroke': 'Breast',
        'Butterfly': 'Fly',
        'Individual Medley': 'IM',
    }
    
    for old, new in replacements.items():
        event_name = event_name.replace(old, new)
    
    return event_name.strip()

def get_age_group(age):
    """Convert age to county age group"""
    age = int(age)
    if age <= 11:
        return '10/11'
    elif age == 12:
        return '12'
    elif age == 13:
        return '13'
    elif age == 14:
        return '14'
    elif age == 15:
        return '15'
    elif age == 16:
        return '16'
    else:
        return '17+'

def get_gender_from_event(event_name):
    """Extract gender from event name"""
    event_lower = event_name.lower()
    if 'female' in event_lower:
        return 'Female'
    elif 'male' in event_lower or 'open' in event_lower:
        return 'Male'
    return None

def main():
    # Load swimmer events data
    print("Loading swimmer data...")
    events_file = 'WSC_Club_Champs_2025/championship_results/events_all.parquet'
    df_events = pd.read_parquet(events_file)
    
    print(f"✓ Loaded {len(df_events)} swimmer performances")
    
    # Load county qualifying times
    print("\nLoading county qualifying times...")
    county_file = 'county_times_2026/county_qualifying_times_2026.csv'
    df_county = pd.read_csv(county_file)
    
    print(f"✓ Loaded {len(df_county)} county qualifying standards")
    
    # Prepare data
    results = []
    
    print("\nAnalyzing performances...")
    
    for idx, row in df_events.iterrows():
        swimmer_name = row['Name']
        event_name_full = row['Event Name']
        swimmer_time = row['Time']
        swimmer_age_2025 = row['Age']
        
        # Age up by 1 year since county times are based on age as of Dec 31, 2026
        # Club champs were in 2025, so swimmers will be 1 year older
        swimmer_age_2026 = swimmer_age_2025 + 1
        
        # Get gender from event name
        gender = get_gender_from_event(event_name_full)
        if not gender:
            continue
        
        # Normalize event name for matching
        event_normalized = normalize_event_name(event_name_full)
        
        # Get age group based on 2026 age
        age_group = get_age_group(swimmer_age_2026)
        
        # Find matching county standard
        county_match = df_county[
            (df_county['EVENT'] == event_normalized) &
            (df_county['GENDER'] == gender) &
            (df_county['AGE'] == age_group)
        ]
        
        if county_match.empty:
            # No county standard for this event/age/gender
            results.append({
                'Name': swimmer_name,
                'Age_2025': swimmer_age_2025,
                'Age_2026': swimmer_age_2026,
                'Gender': gender,
                'Event': event_normalized,
                'Swimmer_Time': swimmer_time,
                'County_Standard': 'N/A',
                'Achieved_County_Time': 'N/A',
                'Time_Difference': 'N/A',
                'Percentage_Difference': 'N/A',
                'Status': 'No standard'
            })
        else:
            county_time = county_match.iloc[0]['TIME']
            
            # Convert times to seconds for comparison
            swimmer_seconds = time_to_seconds(swimmer_time)
            county_seconds = time_to_seconds(county_time)
            
            # Check if achieved (swimmer time must be <= county time)
            achieved = swimmer_seconds <= county_seconds
            
            # Calculate difference (positive = faster than standard, negative = slower)
            diff_seconds = county_seconds - swimmer_seconds
            diff_str = seconds_to_time(abs(diff_seconds))
            
            # Calculate percentage difference
            if county_seconds > 0:
                percent_diff = (diff_seconds / county_seconds) * 100
            else:
                percent_diff = 0
            
            if achieved:
                status = f"✓ Faster by {diff_str}"
                percent_str = f"+{percent_diff:.2f}%"
            else:
                status = f"✗ Slower by {diff_str}"
                percent_str = f"-{abs(percent_diff):.2f}%"
            
            results.append({
                'Name': swimmer_name,
                'Age_2025': swimmer_age_2025,
                'Age_2026': swimmer_age_2026,
                'Gender': gender,
                'Event': event_normalized,
                'Swimmer_Time': swimmer_time,
                'County_Standard': county_time,
                'Achieved_County_Time': 'Yes' if achieved else 'No',
                'Time_Difference': diff_str,
                'Percentage_Difference': percent_str,
                'Status': status
            })
    
    # Create results DataFrame
    df_results = pd.DataFrame(results)
    
    # Sort by name, then event
    df_results = df_results.sort_values(['Name', 'Event'])
    
    # Save to CSV
    output_file = 'county_times_2026/county_times_comparison.csv'
    df_results.to_csv(output_file, index=False)
    
    print(f"\n✓ Analysis complete!")
    print(f"✓ Saved to: {output_file}")
    
    # Summary statistics
    achieved = df_results[df_results['Achieved_County_Time'] == 'Yes']
    print(f"\n" + "="*80)
    print("SUMMARY (County times based on age as of Dec 31, 2026)")
    print("="*80)
    print(f"Total performances analyzed: {len(df_results)}")
    print(f"County times achieved: {len(achieved)}")
    print(f"Percentage achieved: {len(achieved)/len(df_results)*100:.1f}%")
    
    # By swimmer
    swimmers_with_county = achieved['Name'].nunique()
    total_swimmers = df_results['Name'].nunique()
    print(f"\nSwimmers with at least one county time: {swimmers_with_county}/{total_swimmers}")
    
    # Top performers (most county times)
    print("\nTop performers by county times achieved:")
    top_performers = achieved.groupby('Name').size().sort_values(ascending=False).head(10)
    for i, (name, count) in enumerate(top_performers.items(), 1):
        print(f"  {i}. {name}: {count} county times")
    
    # Display sample
    print(f"\nFirst 20 results (Age_2025 = club champs age, Age_2026 = county comparison age):")
    print(df_results.head(20).to_string(index=False))

if __name__ == '__main__':
    main()

