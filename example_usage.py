"""
Example Usage of Swim Event Extractor
======================================

This script demonstrates various ways to use the SwimEventExtractor library.
"""

from swim_event_extractor import SwimEventExtractor

def example_basic_usage():
    """Basic usage: Extract all events."""
    print("="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
    results = extractor.extract_all_events()
    
    print(f"\nExtracted {len(results)} events")


def example_custom_output_dir():
    """Extract events to a custom directory."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Output Directory")
    print("="*60)
    
    import os
    
    # Create output directory if it doesn't exist
    output_dir = './swim_events_csv'
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx', output_dir)
    results = extractor.extract_all_events()
    
    print(f"\nCSV files saved to: {output_dir}")


def example_combined_csv():
    """Create a combined CSV with all events."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Combined CSV")
    print("="*60)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
    
    # Extract individual CSVs first
    extractor.extract_all_events(verbose=False)
    
    # Create combined CSV
    combined_file = extractor.create_combined_csv('all_swimmers.csv')
    print(f"\nCombined file created: {combined_file}")


def example_analyze_events():
    """Analyze event data programmatically."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Analyze Event Data")
    print("="*60)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
    extractor.load_workbook()
    
    event_sheets = extractor.get_numbered_sheets()
    
    print(f"\nAnalyzing {len(event_sheets)} events...\n")
    
    total_swimmers = 0
    top_events = []
    
    for sheet_name in event_sheets:
        data, event_name = extractor.extract_event_data(sheet_name)
        swimmer_count = len(data)
        total_swimmers += swimmer_count
        
        top_events.append((sheet_name, event_name, swimmer_count))
    
    # Sort by swimmer count
    top_events.sort(key=lambda x: x[2], reverse=True)
    
    print("Top 5 Events by Participation:")
    print("-" * 60)
    for i, (event_num, event_name, count) in enumerate(top_events[:5], 1):
        # Truncate long event names
        name_display = event_name[:40] + "..." if len(event_name) > 40 else event_name
        print(f"{i}. Event {event_num}: {count} swimmers")
        print(f"   {name_display}")
    
    print(f"\nTotal swimmers across all events: {total_swimmers}")


def example_single_event():
    """Extract and analyze a single event."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Single Event Extraction")
    print("="*60)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
    extractor.load_workbook()
    
    # Extract event 101
    event_number = '101'
    data, event_name = extractor.extract_event_data(event_number)
    
    print(f"\nEvent: {event_name}")
    print(f"Total swimmers: {len(data)}")
    
    if data:
        print(f"\nFirst 5 swimmers:")
        print("-" * 60)
        for swimmer in data[:5]:
            print(f"  {swimmer['Name']:25} Age: {swimmer['Age']:2}  "
                  f"Club: {swimmer['Club']:15}  Points: {swimmer['WA Points']}")
        
        # Calculate statistics
        ages = [s['Age'] for s in data]
        points = [s['WA Points'] for s in data]
        
        print(f"\nStatistics:")
        print(f"  Age range: {min(ages)} - {max(ages)}")
        print(f"  Average age: {sum(ages) / len(ages):.1f}")
        print(f"  WA Points range: {min(points)} - {max(points)}")
        print(f"  Average WA Points: {sum(points) / len(points):.1f}")


def example_filter_by_club():
    """Filter swimmers by club."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Filter by Club")
    print("="*60)
    
    extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
    extractor.load_workbook()
    
    target_club = 'Worcester'
    event_sheets = extractor.get_numbered_sheets()
    
    club_swimmers = []
    
    for sheet_name in event_sheets:
        data, event_name = extractor.extract_event_data(sheet_name)
        for swimmer in data:
            if target_club in swimmer['Club']:
                club_swimmers.append(swimmer)
    
    print(f"\nFound {len(club_swimmers)} swimmers from {target_club}")
    
    # Count unique swimmers
    unique_names = set(s['Name'] for s in club_swimmers)
    print(f"Unique swimmers: {len(unique_names)}")
    
    # Top performers
    club_swimmers.sort(key=lambda x: x['WA Points'], reverse=True)
    
    print(f"\nTop 10 performers from {target_club}:")
    print("-" * 60)
    for i, swimmer in enumerate(club_swimmers[:10], 1):
        print(f"{i:2}. {swimmer['Name']:25} Event {swimmer['Event Number']}  "
              f"Age {swimmer['Age']:2}  {swimmer['WA Points']} pts")


if __name__ == "__main__":
    """Run all examples."""
    
    print("\n" + "="*60)
    print("SWIM EVENT EXTRACTOR - USAGE EXAMPLES")
    print("="*60)
    
    try:
        # Run examples
        example_basic_usage()
        # example_custom_output_dir()  # Uncomment to run
        # example_combined_csv()  # Uncomment to run
        example_analyze_events()
        example_single_event()
        example_filter_by_club()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except FileNotFoundError:
        print("\nError: 'WSC Club Champs 2024.xlsx' not found in current directory")
        print("Please make sure the Excel file is in the same directory as this script.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

