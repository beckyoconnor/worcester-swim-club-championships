#!/usr/bin/env python3
"""
Extract county qualifying times from PDF
Outputs: EVENT, TIME, AGE, GENDER
"""

import re
import pandas as pd
import pdfplumber

def parse_county_times(pdf_path):
    """Parse the county qualifying times PDF"""
    
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]  # Single page PDF
        text = page.extract_text()
        lines = text.split('\n')
        
        # Define age groups
        male_ages = ['10/11', '12', '13', '14', '15', '16', '17+']
        female_ages = ['10/11', '12', '13', '14', '15', '16', '17+']
        
        for line in lines:
            line = line.strip()
            if not line or 'yrs EVENT' in line or 'Age groups' in line or 'qualifying' in line:
                continue
            
            # Parse lines with times and event names
            # Format: time1 time2 time3 time4 time5 time6 time7 EVENT_NAME time1 time2 time3 time4 time5 time6 time7
            
            # Extract event name (look for common patterns)
            event_match = re.search(r'\d{2}:\d{2}\.\d{2}\s+(\d+m\s+\w+(?:\s+\w+)?)\s+\d{2}:\d{2}\.\d{2}', line)
            if not event_match:
                # Try other patterns
                event_match = re.search(r'(\d+m\s+(?:Free|Breast|Fly|Back|IM))\s+\d{2}:\d{2}\.\d{2}', line)
            
            if event_match:
                event_name = event_match.group(1).strip()
                
                # Extract all times from the line
                times = re.findall(r'\d{2}:\d{2}\.\d{2}', line)
                
                # Split into male and female times
                # Male times come before the event name, female after
                event_pos = line.find(event_name)
                line_before_event = line[:event_pos]
                line_after_event = line[event_pos + len(event_name):]
                
                male_times = re.findall(r'\d{2}:\d{2}\.\d{2}', line_before_event)
                female_times = re.findall(r'\d{2}:\d{2}\.\d{2}', line_after_event)
                
                # Add male times
                for i, time in enumerate(male_times):
                    if i < len(male_ages):
                        results.append({
                            'EVENT': event_name,
                            'TIME': time,
                            'AGE': male_ages[i],
                            'GENDER': 'Male'
                        })
                
                # Add female times
                for i, time in enumerate(female_times):
                    if i < len(female_ages):
                        results.append({
                            'EVENT': event_name,
                            'TIME': time,
                            'AGE': female_ages[i],
                            'GENDER': 'Female'
                        })
    
    return results

def main():
    pdf_path = 'county_times_2026/County Qualifying Times 2026.pdf'
    
    print(f"Extracting data from {pdf_path}...")
    
    results = parse_county_times(pdf_path)
    
    if results:
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Sort by event, gender, and age
        df = df.sort_values(['EVENT', 'GENDER', 'AGE'])
        
        # Save to CSV
        output_file = 'county_times_2026/county_qualifying_times_2026.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n✓ Extracted {len(results)} qualifying times")
        print(f"✓ Saved to: {output_file}")
        
        # Display summary
        print(f"\nSummary:")
        print(f"  Total rows: {len(df)}")
        print(f"  Unique events: {df['EVENT'].nunique()}")
        print(f"  Events: {sorted(df['EVENT'].unique())}")
        print(f"  Ages: {sorted(df['AGE'].unique())}")
        print(f"  Genders: {df['GENDER'].unique().tolist()}")
        
        # Display first 20 rows
        print("\nFirst 20 rows:")
        print(df.head(20).to_string(index=False))
    else:
        print("⚠️ No data extracted. Please check the PDF format.")

if __name__ == '__main__':
    main()
