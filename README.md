# Worcester Swimming Club - Club Championships 2025

A complete system for managing swimming event data, calculating championship scores, and displaying interactive rankings for Worcester Swimming Club.

## 🏊 System Overview

This project consists of three main components:

1. **Swim Event Extractor** - Extracts and cleans swimming event data from MeetManager .RES files
2. **Championship Scoreboard** - Calculates championship scores based on club rules
3. **Championship Dashboard** - Interactive Streamlit web app for viewing rankings and analysis

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Component 1: Swim Event Extractor](#component-1-swim-event-extractor)
- [Component 2: Championship Scoreboard](#component-2-championship-scoreboard)
- [Component 3: Championship Dashboard](#component-3-championship-dashboard)
- [Championship Rules](#championship-rules)
- [Data Structure](#data-structure)
- [Troubleshooting](#troubleshooting)

## 🔧 Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- pandas
- streamlit
- altair
- psutil
- pyarrow (for Parquet support)

## 🚀 Quick Start

### Complete Workflow Example

```bash
# 1. Extract events from .RES files
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files --output-dir WSC_Club_Champs_2025

# 2. Calculate championship scores
python club_championships_scoreboard.py

# 3. Launch the dashboard
streamlit run championship_dashboard_2025.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## Component 1: Swim Event Extractor

Extracts and cleans swimming event data from MeetManager .RES text files.

### Features

- ✅ Parses MeetManager .RES format files
- ✅ Extracts swimmer data: Name, Age, Club, Time, WA Points
- ✅ Validates all data with strict rules (no NaN values)
- ✅ Removes duplicate entries automatically
- ✅ Categorizes events (Sprint, Free, 100 Form, 200 Form, IM, Distance)
- ✅ Determines gender from event names
- ✅ Creates individual CSV files per event

### Usage

#### Command Line

Extract all .RES files from a folder:

```bash
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files
```

Specify custom output directory:

```bash
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files --output-dir ./output
```

#### As a Python Library

```python
from swim_event_extractor import SwimEventExtractor

# Create extractor instance
extractor = SwimEventExtractor(output_dir='WSC_Club_Champs_2025')

# Extract all events from .RES files
results = extractor.extract_all_events_from_res('WSC_Club_Champs_2025/raw_files')

# Results show number of swimmers per event
for event_num, swimmer_count in results.items():
    print(f"Event {event_num}: {swimmer_count} swimmers")
```

### Input Format

The extractor expects MeetManager .RES files with this format:

```
EVENT 302 Open/Male 400m Freestyle

Place    Name                Age  Club    Time        WA Points
1.       Lucy PIPER          12   WORM    6:04.09     359
2.       James WALTER        11   WORM    6:15.23     340
```

### Output Format

Creates CSV files in `cleaned_files/` subfolder:

**File:** `event_302.csv`

| Event Number | Event Name | Event Category | Gender | Name | Age | Club | Time | WA Points |
|--------------|------------|----------------|--------|------|-----|------|------|-----------|
| 302 | Open/Male 400m Freestyle | Free | Male/Open | Lucy PIPER | 12 | Worcester | 6:04.09 | 359 |
| 302 | Open/Male 400m Freestyle | Free | Male/Open | James WALTER | 11 | Worcester | 6:15.23 | 340 |

### Event Categories

Events are automatically categorized:

| Category | Events |
|----------|--------|
| **Sprint** | 50m Free, Back, Breast, Fly |
| **Free** | 100m, 200m, 400m Freestyle |
| **100 Form** | 100m Back, Breast, Fly |
| **200 Form** | 200m Back, Breast, Fly |
| **IM** | 100m, 200m, 400m Individual Medley |
| **Distance** | 800m, 1500m |

### Data Validation

The extractor applies strict validation:

- **Name**: Valid person's name, at least 2 characters
- **Age**: Integer 1-99
- **Club**: Non-empty string, at least 2 characters
- **Time**: Valid time format (skips DNC/DNF/DQ)
- **WA Points**: Integer 1-999

### Example Output

```
🏊 Found 8 RES files
📂 Output directory: WSC_Club_Champs_2025/cleaned_files

✓ event_301.csv: 45 swimmers (Open/Male 200m Butterfly)
✓ event_302.csv: 52 swimmers (Female 400m IM)
✓ event_303.csv: 48 swimmers (Open/Male 400m Freestyle)
...

============================================================
SUMMARY:
  Total events: 8
  Total swimmers: 387
  CSV files saved to: WSC_Club_Champs_2025/cleaned_files
============================================================
```

---

## Component 2: Championship Scoreboard

Calculates age group trophies based on Worcester SC championship rules.

### Features

- ✅ Implements club-specific scoring rules
- ✅ Enforces category limits (2 per category for all ages)
- ✅ Calculates top 8 events per swimmer
- ✅ Creates age group categories (9-10, 11-12, 13-14, 15, 16+)
- ✅ Generates detailed scoreboard CSVs
- ✅ Exports age group winners
- ✅ Creates swimmer narratives for dashboard

### Championship Rules

**Scoring System:**
- Top 8 events count toward total score
- Maximum 2 races per category (all ages)
- Winner determined by highest total WA/FINA points

**Categories:** Sprint, Free, 100 Form, 200 Form, IM, Distance

### Usage

#### Command Line

```bash
# Edit the script to set your folder path
python club_championships_scoreboard.py
```

#### Configuration

Edit the `main()` function in the script:

```python
def main():
    # Set your championship folder
    base_folder = 'WSC_Club_Champs_2025'
    
    # Script will automatically:
    # - Read from: base_folder/cleaned_files/*.csv
    # - Write to: base_folder/championship_results/
```

#### As a Python Library

```python
from club_championships_scoreboard import (
    load_all_events,
    get_event_gender_map_from_csvs,
    calculate_championship_scores,
    create_age_groups,
    export_scoreboard
)

# Load event data
df_all = load_all_events('WSC_Club_Champs_2025')

# Get gender mapping
event_gender_map = get_event_gender_map_from_csvs('WSC_Club_Champs_2025')

# Calculate scores
df_champs = calculate_championship_scores(df_all, event_gender_map)

# Create age groups
df_champs = create_age_groups(df_champs)

# Export results
export_scoreboard(df_champs, 'WSC_Club_Champs_2025')
```

### Output Files

The script creates files in `championship_results/` subfolder:

1. **`championship_scoreboard_boys.csv`** - All male/open swimmers ranked by age group
2. **`championship_scoreboard_girls.csv`** - All female swimmers ranked by age group
3. **`championship_age_group_winners.csv`** - Winners of each age group trophy
4. **`championship_swimmer_narratives.csv`** - Detailed breakdown for each swimmer
5. **`events_all.parquet`** - Combined event data (optimized for dashboard)

### Example Output

```
==================================================================================================
🏆 CLUB CHAMPIONSHIPS SCOREBOARD
==================================================================================================

📊 Loading event data...
✓ Mapped 40 events to gender (from CSVs)
✓ Loaded 1,542 total entries from 40 events
✓ Saved unioned events Parquet: WSC_Club_Champs_2025/championship_results/events_all.parquet (1542 rows)

🏊 Calculating championship scores...
Rules:
  • Count up to 8 scoring events total
  • Maximum 2 races per category (all ages)

✓ 247 swimmers eligible for championship

🏊‍♂️ BOYS CHAMPIONSHIP SCOREBOARD
==================================================================================================

🏆 11-12 AGE GROUP
----------------------------------------------------------------------------------------------------
Pos  Name                      Age  Club            Total   Avg    Events  Categories
----------------------------------------------------------------------------------------------------
1    James WALTER              11   Worcester       2847    355.9  8       Sp:2 Fr:2 100F:1 200F:1 IM:2 Dist:0
2    Oliver SMITH              12   Worcester       2654    331.8  8       Sp:2 Fr:2 100F:1 200F:2 IM:1 Dist:0
...

==================================================================================================
📁 EXPORTING RESULTS
==================================================================================================

✓ Saved: WSC_Club_Champs_2025/championship_results/championship_scoreboard_boys.csv (132 boys)
✓ Saved: WSC_Club_Champs_2025/championship_results/championship_scoreboard_girls.csv (115 girls)
✓ Saved: WSC_Club_Champs_2025/championship_results/championship_age_group_winners.csv (10 age group winners)
✓ Saved swimmer narratives: WSC_Club_Champs_2025/championship_results/championship_swimmer_narratives.csv (247 swimmers)

✅ CHAMPIONSHIP SCOREBOARD COMPLETE!
```

---

## Component 3: Championship Dashboard

Interactive Streamlit web application for viewing rankings, swimmer details, and FINA points analysis.

### Features

- ✅ Interactive rankings by age and gender
- ✅ Individual swimmer event breakdowns
- ✅ Event-by-event rankings
- ✅ FINA points progression charts
- ✅ Category performance analysis
- ✅ Downloadable CSV reports
- ✅ Responsive design with Worcester SC branding
- ✅ Memory-optimized for Streamlit Community Cloud

### Usage

#### Local Development

```bash
streamlit run championship_dashboard_2025.py
```

The dashboard will open automatically at `http://localhost:8501`

#### Deployment to Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with:
   - **Main file**: `championship_dashboard_2025.py`
   - **Python version**: 3.9+
   - **Requirements**: `requirements.txt`

### Dashboard Sections

#### 1. Championship Scoreboard

- Filter by gender (Male/Open or Female)
- Filter by age (All or specific age/16+)
- View rankings in table or chart format
- Download rankings as CSV

#### 2. Individual Swimmer Details

- Select any swimmer
- View their total points, age, categories competed
- See all events with included/excluded indicators
- Category breakdown with statistics
- Download individual swimmer reports

#### 3. Event Rankings

- View all swimmers in a specific event
- Sort by WA Points (FINA Points)
- Filter by age and gender
- See times and rankings
- Download event results

#### 4. FINA Points Analysis

- Charts showing FINA points progression by age
- Separate charts for male and female swimmers
- Category-specific trend lines
- Understand age-related performance improvements

### Configuration

Edit the folder path in the script:

```python
def main():
    # Set your championship folder
    events_folder = 'WSC_Club_Champs_2025'
```

### Screenshots

The dashboard includes:
- Worcester SC branding and logo
- Interactive tooltips explaining metrics
- Responsive charts and tables
- Mobile-friendly design
- Export buttons for all data views

---

## 📊 Championship Rules

### Worcester SC Club Championships Format

The championship format encourages swimmers to participate across multiple event types.

#### Event Categories

Competition is spread across **6 categories**:

| Category | Events |
|----------|--------|
| **Sprint** | 50m Free, Back, Breast, and Fly |
| **Free** | 100m, 200m, and 400m Freestyle |
| **100 Form** | 100m Back, Breast, and Fly |
| **200 Form** | 200m Back, Breast, and Fly |
| **IM** | 100m, 200m, and 400m Individual Medley |
| **Distance** | 800m and 1500m |

#### Scoring Rules

Age group trophies are awarded to swimmers who gain the highest collated number of **FINA/WA points** from their **top 8 events** across the 6 categories.

**Category Limits:**
- Maximum of **2 races** counted per category (all ages)

Your **best 8 events** (by WA Points) will count toward your total score, respecting the category limits.

#### Age Groups

Trophies awarded in these age groups:
- 9-10 years
- 11-12 years
- 13-14 years
- 15 years
- 16+ years (Open)

---

## 📁 Data Structure

### Folder Organization

```
WSC_Club_Champs_2025/
├── raw_files/                      # Input: .RES files from MeetManager
│   ├── CC25E301.RES
│   ├── CC25E302.RES
│   └── ...
├── cleaned_files/                  # Output: Cleaned CSV files per event
│   ├── event_301.csv
│   ├── event_302.csv
│   └── ...
└── championship_results/           # Output: Championship calculations
    ├── championship_scoreboard_boys.csv
    ├── championship_scoreboard_girls.csv
    ├── championship_age_group_winners.csv
    ├── championship_swimmer_narratives.csv
    └── events_all.parquet
```

### CSV Column Definitions

#### Event CSVs (`cleaned_files/event_*.csv`)

| Column | Type | Description |
|--------|------|-------------|
| Event Number | string | Event number (e.g., "301") |
| Event Name | string | Full event name with gender |
| Event Category | string | Sprint/Free/100 Form/200 Form/IM/Distance |
| Gender | string | Male/Open or Female |
| Name | string | Swimmer's full name |
| Age | int | Swimmer's age at competition |
| Club | string | Club name |
| Time | string | Swim time (HH:MM:SS.HS format) |
| WA Points | int | World Aquatics (FINA) points |

#### Championship Scoreboard CSVs

| Column | Type | Description |
|--------|------|-------------|
| Age Group | string | Age group category |
| Name | string | Swimmer's name |
| Age | int | Swimmer's age |
| Club | string | Club name |
| Total_Points | int | Sum of top 8 events |
| Average_Points | float | Average points per event |
| Best_Event_Points | int | Highest single event score |
| Events_Count | int | Number of events counted (max 8) |
| Categories_Competed | int | Number of categories competed in |
| Sprint_Events | int | Sprint events counted |
| Free_Events | int | Freestyle events counted |
| Form_100_Events | int | 100 Form events counted |
| Form_200_Events | int | 200 Form events counted |
| IM_Events | int | IM events counted |
| Distance_Events | int | Distance events counted |

---

## 🐛 Troubleshooting

### Common Issues

#### 1. No CSV files found

**Problem**: `No CSV files found in cleaned_files`

**Solution**: Run the event extractor first:
```bash
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files --output-dir WSC_Club_Champs_2025
```

#### 2. Module not found errors

**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Dashboard doesn't load data

**Problem**: Dashboard shows "No data available"

**Solution**: Ensure you've run the scoreboard calculator:
```bash
python club_championships_scoreboard.py
```

#### 4. Memory issues on Streamlit Cloud

**Problem**: Dashboard crashes or runs slowly

**Solution**: The dashboard is optimized for Streamlit Community Cloud (2GB limit):
- Uses Parquet files for efficient loading
- Implements caching
- Uses category data types for memory optimization
- Monitor memory usage in System Information expander

#### 5. Gender mapping issues

**Problem**: Events show as "Unknown" gender

**Solution**: Ensure event names contain gender indicators:
- "Male", "Open", "Open/Male" → Male/Open
- "Female" → Female

Check event names in your .RES files or CSV Event Name column.

### Getting Help

For issues specific to Worcester SC:
- 📧 Email: Contact via [worcestersc.co.uk/contact](https://worcestersc.co.uk/contact)
- 🌐 Website: [worcestersc.co.uk](https://worcestersc.co.uk)

For technical issues:
- Check this README
- Review the code comments
- Verify your data format matches the examples

---

## 🎯 Best Practices

### Data Quality

1. **Verify .RES files** before extraction
   - Check for complete event headers
   - Ensure consistent formatting
   - Remove any corrupted files

2. **Review extracted CSVs** in `cleaned_files/`
   - Spot check swimmer counts
   - Verify event categorization
   - Check gender assignments

3. **Validate championship results**
   - Review age group winners
   - Verify category limits applied correctly
   - Check swimmer narratives for accuracy

### Performance Optimization

1. **Use Parquet files** for large datasets (automatically created)
2. **Clear Streamlit cache** if data changes:
   ```bash
   streamlit cache clear
   ```
3. **Restart dashboard** after updating championship data

### Workflow Tips

1. **Complete workflow in order**:
   - Extract → Calculate → Display
2. **Keep raw files** as backup
3. **Version control** your results CSVs
4. **Export reports** regularly from dashboard

---

## 📄 License

Free to use and modify for Worcester Swimming Club and other swimming clubs.

## 🏊 Credits

Developed for Worcester Swimming Club Championships 2025.

**Worcester Swimming Club**
- 🌐 Website: [worcestersc.co.uk](https://worcestersc.co.uk)
- 📍 Location: Worcester, UK

---

## 🔄 Updates and Maintenance

### Version History

- **2025.1.0** - Initial release
  - Swim Event Extractor (RES format only)
  - Championship Scoreboard calculator
  - Interactive Streamlit dashboard

### Roadmap

Potential future enhancements:
- Real-time data updates during competitions
- Historical comparison across years
- Additional statistical analysis
- Mobile app version
- PDF report generation

---

**Last Updated:** January 2025
