#!/usr/bin/env python3
"""
Analyze championship data to find the strongest swimmers in each category by age group.
"""

import pandas as pd
import re
from collections import defaultdict

def extract_category_points(included_text):
    """Extract points per category from the IncludedShort column."""
    category_points = {
        'Sprint': 0,
        'Free': 0,
        '100 Form': 0,
        '200 Form': 0,
        'IM': 0,
        'Distance': 0
    }
    
    if pd.isna(included_text):
        return category_points
    
    # Pattern to match category names and their events with points
    patterns = {
        'Sprint': r'Sprint \([^)]+?(\d+) pts[^)]*\)',
        'Free': r'Free \([^)]+?(\d+) pts[^)]*\)',
        '100 Form': r'100 Form \([^)]+?(\d+) pts[^)]*\)',
        '200 Form': r'200 Form \([^)]+?(\d+) pts[^)]*\)',
        'IM': r'IM \([^)]+?(\d+) pts[^)]*\)',
        'Distance': r'Distance \([^)]+?(\d+) pts[^)]*\)'
    }
    
    for category, pattern in patterns.items():
        matches = re.findall(pattern, included_text)
        if matches:
            # Sum all points found for this category
            category_points[category] = sum(int(pts) for pts in matches)
    
    return category_points

def main():
    # Load the swimmer narratives
    df = pd.read_csv('WSC_Club_Champs_2025/championship_results/championship_swimmer_narratives.csv')
    
    # Extract category points for each swimmer
    category_data = []
    for _, row in df.iterrows():
        cat_points = extract_category_points(row['IncludedShort'])
        entry = {
            'Name': row['Name'],
            'Age': row['Age'],
            'Gender': row['Gender'],
            'Total_Points': row['Total_Points'],
            **cat_points
        }
        category_data.append(entry)
    
    df_categories = pd.DataFrame(category_data)
    
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

