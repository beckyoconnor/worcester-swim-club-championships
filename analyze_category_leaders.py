#!/usr/bin/env python3
"""
Analyze championship data to find the strongest swimmers in each category by age group.
Uses the scoreboard data directly instead of parsing narrative text.
"""

import pandas as pd

def main():
    # Load the scoreboard data (has Distance_Events column)
    df_boys = pd.read_csv('WSC_Club_Champs_2025/championship_results/championship_scoreboard_boys.csv')
    df_girls = pd.read_csv('WSC_Club_Champs_2025/championship_results/championship_scoreboard_girls.csv')
    
    # Load all events to calculate category totals
    df_all = pd.read_parquet('WSC_Club_Champs_2025/championship_results/events_all.parquet')
    
    # For each swimmer, calculate total points per category
    def calculate_category_points(swimmer_name, age, gender):
        swimmer_events = df_all[
            (df_all['Name'] == swimmer_name) & 
            (df_all['Age'] == age) & 
            (df_all['Gender'] == gender)
        ]
        
        category_points = {}
        for category in ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']:
            cat_events = swimmer_events[swimmer_events['Event Category'] == category]
            # Sum all points for this category (top 2 events are already counted in championship)
            category_points[category] = cat_events['WA Points'].sum()
        
        return category_points
    
    # Combine boys and girls data
    df_boys['Gender'] = 'Male/Open'
    df_girls['Gender'] = 'Female'
    df_all_swimmers = pd.concat([df_boys, df_girls], ignore_index=True)
    
    # Calculate category points for each swimmer
    swimmer_categories = []
    for _, swimmer in df_all_swimmers.iterrows():
        cat_points = calculate_category_points(swimmer['Name'], swimmer['Age'], swimmer['Gender'])
        entry = {
            'Name': swimmer['Name'],
            'Age': swimmer['Age'],
            'Gender': swimmer['Gender'],
            **cat_points
        }
        swimmer_categories.append(entry)
    
    df_categories = pd.DataFrame(swimmer_categories)
    
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
    output.append("## 🏅 Category Leaders by Age Group\n")
    output.append("*Top scorer in each category for each age group*\n")
    
    categories = ['Sprint', 'Free', '100 Form', '200 Form', 'IM', 'Distance']
    
    for age_label, ages in age_groups.items():
        df_age = df_categories[df_categories['Age'].isin(ages)]
        
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
            output.append("\n| Category | Leader | Points |\n")
            output.append("|----------|--------|--------|\n")
            
            for category in categories:
                # Find swimmer with most points in this category
                if df_gender[category].max() > 0:
                    top_swimmer = df_gender.loc[df_gender[category].idxmax()]
                    output.append(f"| **{category}** | {top_swimmer['Name']} | {int(top_swimmer[category])} |\n")
                else:
                    output.append(f"| **{category}** | — | 0 |\n")
    
    return '\n'.join(output)

if __name__ == '__main__':
    result = main()
    
    # Save to file
    with open('WSC_Club_Champs_2025/category_leaders_by_age.md', 'w') as f:
        f.write(result)
    
    print(result)
    print("\n✅ Analysis saved to: WSC_Club_Champs_2025/category_leaders_by_age.md")
