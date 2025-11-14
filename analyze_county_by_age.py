#!/usr/bin/env python3
"""
Analyze county times achievement by age
"""

import pandas as pd

def main():
    # Load the comparison data
    df = pd.read_csv('county_times_2026/county_times_comparison.csv')
    
    # Filter only those who achieved county times
    achieved = df[df['Achieved_County_Time'] == 'Yes'].copy()
    
    # Get unique swimmers by age who achieved at least one county time (using 2026 age)
    swimmers_by_age = achieved.groupby('Age_2026')['Name'].nunique().sort_index()
    
    # Get total swimmers by age (who competed) (using 2026 age)
    total_swimmers_by_age = df.groupby('Age_2026')['Name'].nunique().sort_index()
    
    # Get total county times achieved by age (using 2026 age)
    county_times_by_age = achieved.groupby('Age_2026').size().sort_index()
    
    print("="*80)
    print("COUNTY TIMES ACHIEVEMENT BY AGE (2026 Age for County Comparison)")
    print("="*80)
    print()
    print(f"{'Age':<6} {'Swimmers with':<18} {'Total':<12} {'Percentage':<12} {'Total CT'}")
    print(f"{'':6} {'County Times':<18} {'Swimmers':<12} {'':12} {'Achieved'}")
    print("-"*80)
    
    total_with_ct = 0
    total_swimmers = 0
    total_ct_achieved = 0
    
    for age in total_swimmers_by_age.index:
        swimmers_with_ct = swimmers_by_age.get(age, 0)
        total = total_swimmers_by_age[age]
        ct_count = county_times_by_age.get(age, 0)
        percentage = (swimmers_with_ct / total * 100) if total > 0 else 0
        
        print(f"{age:<6} {swimmers_with_ct:<18} {total:<12} {percentage:>6.1f}%      {ct_count}")
        
        total_with_ct += swimmers_with_ct
        total_swimmers += total
        total_ct_achieved += ct_count
    
    print("-"*80)
    overall_percentage = (total_with_ct / total_swimmers * 100) if total_swimmers > 0 else 0
    print(f"{'TOTAL':<6} {total_with_ct:<18} {total_swimmers:<12} {overall_percentage:>6.1f}%      {total_ct_achieved}")
    print()
    
    # Show top performers by age
    print()
    print("="*80)
    print("TOP PERFORMERS BY AGE GROUP (2026 Age)")
    print("="*80)
    
    for age in sorted(achieved['Age_2026'].unique()):
        age_data = achieved[achieved['Age_2026'] == age]
        top_performers = age_data.groupby('Name').size().sort_values(ascending=False).head(3)
        
        print(f"\nAge {age}:")
        for i, (name, count) in enumerate(top_performers.items(), 1):
            print(f"  {i}. {name}: {count} county times")

if __name__ == '__main__':
    main()

