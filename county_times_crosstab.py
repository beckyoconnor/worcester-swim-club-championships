#!/usr/bin/env python3
"""
Create crosstab analysis of county times achievement by age
Breaks down by number of county times: 1-3, 4-10, 11+
"""

import pandas as pd

def main():
    # Load the comparison data
    df = pd.read_csv('county_times_2026/county_times_comparison.csv')
    
    # Use Age_2026 for grouping (county comparison age)
    # But keep Age_2025 for display purposes
    achieved = df[df['Achieved_County_Time'] == 'Yes'].copy()
    ct_per_swimmer = achieved.groupby(['Name', 'Age_2026']).size().reset_index(name='County_Times_Count')
    
    # Get total swimmers by age (using 2026 age for county comparison)
    all_swimmers = df.groupby(['Name', 'Age_2026']).size().reset_index(name='Events')[['Name', 'Age_2026']]
    
    # Merge to get swimmers with 0 county times
    swimmer_stats = all_swimmers.merge(ct_per_swimmer, on=['Name', 'Age_2026'], how='left')
    swimmer_stats['County_Times_Count'] = swimmer_stats['County_Times_Count'].fillna(0).astype(int)
    
    # Categorize county times
    def categorize_ct(count):
        if count == 0:
            return '0 County Times'
        elif count <= 3:
            return '1-3 County Times'
        elif count <= 10:
            return '4-10 County Times'
        else:
            return '11+ County Times'
    
    swimmer_stats['Category'] = swimmer_stats['County_Times_Count'].apply(categorize_ct)
    
    # Create crosstab (using Age_2026 for county comparison)
    crosstab = pd.crosstab(
        swimmer_stats['Age_2026'], 
        swimmer_stats['Category'],
        margins=True,
        margins_name='Total'
    )
    
    # Ensure all columns exist
    for col in ['0 County Times', '1-3 County Times', '4-10 County Times', '11+ County Times']:
        if col not in crosstab.columns:
            crosstab[col] = 0
    
    # Reorder columns
    col_order = ['0 County Times', '1-3 County Times', '4-10 County Times', '11+ County Times', 'Total']
    crosstab = crosstab[[col for col in col_order if col in crosstab.columns]]
    
    # Create percentage crosstab
    crosstab_pct = crosstab.copy()
    for idx in crosstab.index:
        if idx != 'Total':
            total = crosstab.loc[idx, 'Total']
            if total > 0:
                for col in crosstab.columns:
                    if col != 'Total':
                        crosstab_pct.loc[idx, col] = f"{crosstab.loc[idx, col]} ({crosstab.loc[idx, col]/total*100:.1f}%)"
    
    # Save raw counts
    output_counts = 'county_times_2026/county_times_crosstab_counts.csv'
    crosstab.to_csv(output_counts)
    print(f"✓ Saved counts to: {output_counts}")
    
    # Create a combined version with both counts and cumulative percentages
    results = []
    
    for age in crosstab.index:
        if age == 'Total':
            continue
            
        total = crosstab.loc[age, 'Total']
        zero = crosstab.loc[age, '0 County Times']
        one_three = crosstab.loc[age, '1-3 County Times']
        four_ten = crosstab.loc[age, '4-10 County Times']
        eleven_plus = crosstab.loc[age, '11+ County Times']
        
        # Calculate cumulative counts
        one_plus = one_three + four_ten + eleven_plus  # 1+ county times
        four_plus = four_ten + eleven_plus  # 4+ county times
        eleven_plus_count = eleven_plus  # 11+ county times
        
        # Calculate cumulative percentages
        one_plus_pct = (one_plus / total * 100) if total > 0 else 0
        four_plus_pct = (four_plus / total * 100) if total > 0 else 0
        eleven_plus_pct = (eleven_plus_count / total * 100) if total > 0 else 0
        zero_pct = (zero / total * 100) if total > 0 else 0
        
        results.append({
            'Age': age,
            'Total_Swimmers': int(total),
            '0_CT_Count': int(zero),
            '0_CT_Percent': f"{zero_pct:.1f}%",
            '1+_CT_Count': int(one_plus),
            '1+_CT_Percent': f"{one_plus_pct:.1f}%",
            '4+_CT_Count': int(four_plus),
            '4+_CT_Percent': f"{four_plus_pct:.1f}%",
            '11+_CT_Count': int(eleven_plus_count),
            '11+_CT_Percent': f"{eleven_plus_pct:.1f}%"
        })
    
    # Add totals
    total_swimmers = crosstab.loc['Total', 'Total']
    total_zero = crosstab.loc['Total', '0 County Times']
    total_one_three = crosstab.loc['Total', '1-3 County Times']
    total_four_ten = crosstab.loc['Total', '4-10 County Times']
    total_eleven_plus = crosstab.loc['Total', '11+ County Times']
    
    # Calculate cumulative totals
    total_one_plus = total_one_three + total_four_ten + total_eleven_plus
    total_four_plus = total_four_ten + total_eleven_plus
    
    results.append({
        'Age': 'TOTAL',
        'Total_Swimmers': int(total_swimmers),
        '0_CT_Count': int(total_zero),
        '0_CT_Percent': f"{(total_zero/total_swimmers*100):.1f}%",
        '1+_CT_Count': int(total_one_plus),
        '1+_CT_Percent': f"{(total_one_plus/total_swimmers*100):.1f}%",
        '4+_CT_Count': int(total_four_plus),
        '4+_CT_Percent': f"{(total_four_plus/total_swimmers*100):.1f}%",
        '11+_CT_Count': int(total_eleven_plus),
        '11+_CT_Percent': f"{(total_eleven_plus/total_swimmers*100):.1f}%"
    })
    
    df_results = pd.DataFrame(results)
    
    # Save combined version
    output_combined = 'county_times_2026/county_times_crosstab_analysis.csv'
    df_results.to_csv(output_combined, index=False)
    print(f"✓ Saved analysis to: {output_combined}")
    
    # Print summary
    print("\n" + "="*100)
    print("COUNTY TIMES ACHIEVEMENT BREAKDOWN BY AGE (CUMULATIVE)")
    print("Age shown is 2026 age (for county comparison, +1 year from club champs)")
    print("="*100)
    print()
    print(f"{'Age':<5} {'Total':<7} {'0 CT':<15} {'1+ CT':<15} {'4+ CT':<15} {'11+ CT':<15}")
    print(f"{'2026':<5}")
    print("-"*100)
    
    for result in results:
        age = str(result['Age'])
        total = result['Total_Swimmers']
        zero = f"{result['0_CT_Count']} ({result['0_CT_Percent']})"
        one_plus = f"{result['1+_CT_Count']} ({result['1+_CT_Percent']})"
        four_plus = f"{result['4+_CT_Count']} ({result['4+_CT_Percent']})"
        eleven_plus = f"{result['11+_CT_Count']} ({result['11+_CT_Percent']})"
        
        if age == 'TOTAL':
            print("-"*100)
        
        print(f"{age:<5} {total:<7} {zero:<15} {one_plus:<15} {four_plus:<15} {eleven_plus:<15}")
    
    print()

if __name__ == '__main__':
    main()

