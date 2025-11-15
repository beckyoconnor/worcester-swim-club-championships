#!/usr/bin/env python3
"""
Analyze championship data to find the strongest swimmers in each stroke by age group.
Groups by stroke discipline: Freestyle, Backstroke, Breaststroke, Butterfly
"""

import pandas as pd

def categorize_by_stroke(event_name):
    """Determine stroke from event name."""
    event_lower = event_name.lower()
    
    if 'freestyle' in event_lower or 'free' in event_lower:
        return 'Freestyle'
    elif 'backstroke' in event_lower or 'back' in event_lower:
        return 'Backstroke'
    elif 'breaststroke' in event_lower or 'breast' in event_lower:
        return 'Breaststroke'
    elif 'butterfly' in event_lower or 'fly' in event_lower:
        return 'Butterfly'
    elif 'im' in event_lower or 'medley' in event_lower:
        return None  # IM not included in stroke analysis
    else:
        return None

def main():
    # Load the scoreboard data
    df_boys = pd.read_csv('WSC_Club_Champs_2025/championship_results/championship_scoreboard_boys.csv')
    df_girls = pd.read_csv('WSC_Club_Champs_2025/championship_results/championship_scoreboard_girls.csv')
    
    # Load all events to calculate stroke totals
    df_all = pd.read_parquet('WSC_Club_Champs_2025/championship_results/events_all.parquet')
    
    # Add stroke column
    df_all['Stroke'] = df_all['Event Name'].apply(categorize_by_stroke)
    
    # Remove IM events
    df_all = df_all[df_all['Stroke'].notna()]
    
    # For each swimmer, calculate average points per stroke
    def calculate_stroke_points(swimmer_name, age, gender):
        swimmer_events = df_all[
            (df_all['Name'] == swimmer_name) & 
            (df_all['Age'] == age) & 
            (df_all['Gender'] == gender)
        ]
        
        stroke_points = {}
        for stroke in ['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly']:
            stroke_events = swimmer_events[swimmer_events['Stroke'] == stroke]
            # Calculate average points for this stroke
            if len(stroke_events) > 0:
                stroke_points[stroke] = stroke_events['WA Points'].mean()
            else:
                stroke_points[stroke] = 0
        
        return stroke_points
    
    # Combine boys and girls data
    df_boys['Gender'] = 'Male/Open'
    df_girls['Gender'] = 'Female'
    df_all_swimmers = pd.concat([df_boys, df_girls], ignore_index=True)
    
    # Calculate stroke points for each swimmer
    swimmer_strokes = []
    for _, swimmer in df_all_swimmers.iterrows():
        stroke_pts = calculate_stroke_points(swimmer['Name'], swimmer['Age'], swimmer['Gender'])
        entry = {
            'Name': swimmer['Name'],
            'Age': swimmer['Age'],
            'Gender': swimmer['Gender'],
            **stroke_pts
        }
        swimmer_strokes.append(entry)
    
    df_strokes = pd.DataFrame(swimmer_strokes)
    
    # Define age groups
    age_groups = {
        '9': [9],
        '10': [10],
        '11': [11],
        '12': [12],
        '13': [13],
        '14': [14],
        '15': [15],
        '16+': list(range(16, 100))
    }
    
    # Create output for markdown
    output = []
    output.append("## 🏊 Stroke Specialists by Age Group\n")
    output.append("*Highest average points per stroke (Freestyle, Backstroke, Breaststroke, Butterfly)*\n")
    
    strokes = ['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly']
    
    for age_label, ages in age_groups.items():
        df_age = df_strokes[df_strokes['Age'].isin(ages)]
        
        if df_age.empty:
            continue
        
        output.append(f"\n### Age {age_label}\n")
        
        # Split by gender
        for gender in ['Male/Open', 'Female']:
            df_gender = df_age[df_age['Gender'] == gender]
            
            if df_gender.empty:
                continue
            
            gender_label = "Boys" if gender == 'Male/Open' else "Girls"
            output.append(f"\n#### {gender_label}\n")
            output.append("\n| Stroke | Leader | Avg Points |\n")
            output.append("|--------|--------|------------|\n")
            
            for stroke in strokes:
                # Find swimmer with highest average points in this stroke
                if df_gender[stroke].max() > 0:
                    top_swimmer = df_gender.loc[df_gender[stroke].idxmax()]
                    # Format with one decimal place
                    output.append(f"| **{stroke}** | {top_swimmer['Name']} | {top_swimmer[stroke]:.1f} |\n")
                else:
                    output.append(f"| **{stroke}** | — | 0 |\n")
    
    return '\n'.join(output)

if __name__ == '__main__':
    result = main()
    
    # Save to file
    with open('WSC_Club_Champs_2025/stroke_specialists_by_age.md', 'w') as f:
        f.write(result)
    
    print(result)
    print("\n✅ Analysis saved to: WSC_Club_Champs_2025/stroke_specialists_by_age.md")

