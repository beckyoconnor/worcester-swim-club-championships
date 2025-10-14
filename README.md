# Swim Event Data Extractor

A Python library to extract and clean swimming event data from Excel files. Automatically detects numbered event sheets and extracts swimmer information including name, age, club, and WA points.

## Features

- ✅ Automatically detects numbered event sheets (e.g., 101, 102, 201, etc.)
- ✅ Extracts swimmer data: Name, Age, Club, WA Points
- ✅ Validates all data with strict rules (no NaN values allowed)
- ✅ **Removes duplicate entries** automatically within each event
- ✅ **Improved column detection** with multiple header patterns
- ✅ **Auto-creates organized folders** with competition name, date, and filename
- ✅ Creates individual CSV files per event
- ✅ Can create combined CSV with all events
- ✅ Easy to use as a library or command-line tool

## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

Or install openpyxl directly:
```bash
pip install openpyxl
```

## Usage

### Command Line

Extract all events from an Excel file:
```bash
python swim_event_extractor.py "WSC Club Champs 2024.xlsx"
```

Specify a custom output directory:
```bash
python swim_event_extractor.py "WSC Club Champs 2024.xlsx" "./output"
```

### As a Python Library

```python
from swim_event_extractor import SwimEventExtractor

# Create extractor instance (auto-creates folder by default)
extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')

# Extract all events to individual CSV files
# Creates folder like: "WSC_Club_Champs_2024" with all CSVs inside
results = extractor.extract_all_events()

# Create a combined CSV with all events
extractor.create_combined_csv('all_events.csv')

# Get list of numbered event sheets
event_sheets = extractor.get_numbered_sheets()
print(f"Found events: {event_sheets}")

# Disable auto-folder creation if needed
extractor = SwimEventExtractor('file.xlsx', auto_create_folder=False)
```

### Advanced Usage

```python
from swim_event_extractor import SwimEventExtractor

# Custom output directory
extractor = SwimEventExtractor(
    excel_file='WSC Club Champs 2024.xlsx',
    output_dir='./csv_output'
)

# Extract all events
results = extractor.extract_all_events(verbose=True)

# Check results
for event_num, swimmer_count in results.items():
    print(f"Event {event_num}: {swimmer_count} swimmers")

# Extract single event
data, event_name = extractor.extract_event_data('101')
print(f"{event_name}: {len(data)} swimmers")
```

## Data Validation Rules

The extractor applies strict validation rules to ensure clean data:

- **Name**: Must be a valid person's name
  - At least 2 characters
  - Contains letters
  - Not a header row (e.g., "Name", "Place")

- **Age**: Must be a 1 or 2 digit integer
  - Range: 1-99
  - Must be numeric

- **Club**: Must be a valid club name
  - At least 2 characters
  - Non-empty string

- **WA Points**: Must be a 1, 2, or 3 digit integer
  - Range: 1-999
  - Must be numeric

Rows that don't meet these criteria are automatically excluded.

## Output Format

### Individual Event CSV Files

Each event creates a file named `event_XXX.csv` with the following columns:

| Event Number | Name | Age | Club | WA Points |
|--------------|------|-----|------|-----------|
| 101 | James Walter | 11 | Worcester | 148 |
| 101 | Tarek Bluck | 14 | Worcester | 410 |

### Combined CSV File

Optional combined file contains all events in a single CSV with the same format.

## Example Output

```
$ python swim_event_extractor.py "WSC Club Champs 2024.xlsx"

Loading workbook: WSC Club Champs 2024.xlsx

📁 Created output folder:
   Competition: WSC Club Champs 2024
   Date: 2024
   Folder: WSC_Club_Champs_2024

🏊 Found 36 numbered event sheets
📂 Output directory: /path/to/WSC_Club_Champs_2024

✓ event_101.csv: 12 swimmers (EVENT 101 Open/Male 200m Butterfly)
✓ event_102.csv: 32 swimmers (EVENT 102 Female 400m IM)
✓ event_103.csv: 50 swimmers (EVENT 103 Open/Male 400m Freestyle)
...

============================================================
SUMMARY:
  Total events: 36
  Total swimmers: 1541
  CSV files saved to: /path/to/WSC_Club_Champs_2024
============================================================

Create a combined CSV with all events? (y/n): y

Creating combined CSV with all events...
✓ Combined CSV created: /path/to/WSC_Club_Champs_2024/all_events_combined.csv
  Total rows: 1541

✓ Processing complete!
```

### Folder Organization

The library automatically creates a well-organized folder structure:

```
worcester_swim_club/
├── WSC Club Champs 2024.xlsx           # Original Excel file
└── WSC_Club_Champs_2024/               # Auto-created folder
    ├── event_101.csv
    ├── event_102.csv
    ├── event_103.csv
    ├── ...
    └── all_events_combined.csv (optional)
```

The folder name is automatically generated from:
- **Competition name** (extracted from Excel sheets)
- **Date** (extracted from competition name or file modification date)
- **Excel filename** (if different from competition name)

Example folder names:
- `WSC_Club_Champs_2024`
- `Regional_Championships_2024-05-15`
- `Summer_Gala_2024_Results`

## Error Handling

The library handles various edge cases:

- Missing or malformed data is automatically skipped
- Events without valid data create empty CSV files
- Column positions are auto-detected (handles different Excel layouts)
- Graceful handling of missing WA Points or other fields

## Requirements

- Python 3.6+
- openpyxl 3.0.0+

## File Structure

```
worcester_swim_club/
├── swim_event_extractor.py    # Main library
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── WSC Club Champs 2024.xlsx  # Input Excel file
└── event_*.csv                # Generated CSV files
```

## API Reference

### SwimEventExtractor Class

#### `__init__(excel_file: str, output_dir: str = None, auto_create_folder: bool = True)`
Initialize the extractor with an Excel file path and optional output directory.

**Parameters:**
- `excel_file`: Path to the Excel file
- `output_dir`: Custom output directory (overrides auto-folder creation)
- `auto_create_folder`: If True, automatically creates organized folder (default: True)

#### `extract_all_events(verbose: bool = True) -> Dict[str, int]`
Extract all numbered event sheets and save to CSV files. Returns a dictionary mapping event numbers to swimmer counts.

#### `extract_event_data(sheet_name: str) -> Tuple[List[Dict], str]`
Extract data from a single event sheet. Returns tuple of (swimmer data list, event name).

#### `create_combined_csv(output_filename: str = "all_events_combined.csv") -> str`
Create a single CSV file containing all events. Returns the path to the created file.

#### `get_numbered_sheets() -> List[str]`
Get all sheet names that are numeric. Returns sorted list of sheet names.

#### `save_to_csv(data: List[Dict], event_number: str) -> str`
Save event data to a CSV file. Returns the path to the created file.

### Static Validation Methods

- `validate_name(name) -> bool`: Validate person's name
- `validate_age(age) -> Optional[int]`: Validate and convert age
- `validate_club(club) -> Optional[str]`: Validate club name
- `validate_wa_points(points) -> Optional[int]`: Validate and convert WA points

## License

Free to use and modify.

## Support

For issues or questions, please review the code or modify as needed for your specific use case.

