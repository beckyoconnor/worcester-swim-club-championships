# Quick Start Guide

Get started with the Swim Event Extractor in under 2 minutes!

## 1. Install Dependencies

```bash
pip install openpyxl
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## 2. Run the Extractor

### Command Line (Easiest)

```bash
python swim_event_extractor.py "WSC Club Champs 2024.xlsx"
```

That's it! The script will:
- Extract all numbered event sheets
- Validate and clean the data
- Create individual CSV files for each event
- Show a summary of results

### Python Script

Create a file called `extract.py`:

```python
from swim_event_extractor import SwimEventExtractor

extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
extractor.extract_all_events()
```

Run it:
```bash
python extract.py
```

## 3. Output

You'll get CSV files named `event_101.csv`, `event_102.csv`, etc., each containing:

| Event Number | Name | Age | Club | WA Points |
|--------------|------|-----|------|-----------|
| 101 | James Walter | 11 | Worcester | 148 |
| 101 | Tarek Bluck | 14 | Worcester | 410 |

## Advanced Usage

### Create Combined CSV

```python
from swim_event_extractor import SwimEventExtractor

extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
extractor.extract_all_events()
extractor.create_combined_csv('all_events.csv')
```

### Custom Output Directory

```python
extractor = SwimEventExtractor(
    excel_file='WSC Club Champs 2024.xlsx',
    output_dir='./my_output_folder'
)
extractor.extract_all_events()
```

### Analyze Data

```python
extractor = SwimEventExtractor('WSC Club Champs 2024.xlsx')
extractor.load_workbook()

# Get event data
data, event_name = extractor.extract_event_data('101')

print(f"Event: {event_name}")
print(f"Swimmers: {len(data)}")

for swimmer in data:
    print(f"{swimmer['Name']} - {swimmer['WA Points']} points")
```

## Need More Examples?

Check out `example_usage.py` for detailed examples of:
- Filtering by club
- Analyzing statistics
- Top performers
- And more!

## Troubleshooting

**File not found error?**
- Make sure the Excel file is in the current directory
- Or provide the full path: `SwimEventExtractor('/full/path/to/file.xlsx')`

**Import error?**
- Install openpyxl: `pip install openpyxl`

**No data extracted?**
- Check that your Excel file has numbered sheet tabs (101, 102, etc.)
- Check that sheets have columns: Name, AaD, Club, WA Pts

## File Structure

After running, you'll have:
```
worcester_swim_club/
├── swim_event_extractor.py  ← The library
├── requirements.txt          ← Dependencies
├── README.md                 ← Full documentation
├── QUICKSTART.md            ← This file
├── example_usage.py         ← Usage examples
├── WSC Club Champs 2024.xlsx ← Your Excel file
└── event_*.csv              ← Generated CSV files
```

## Next Steps

- Read the full documentation in `README.md`
- Try the examples in `example_usage.py`
- Modify the library for your specific needs

Happy swimming! 🏊‍♂️

