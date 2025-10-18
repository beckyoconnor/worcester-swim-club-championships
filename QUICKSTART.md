# Quick Start Guide - Worcester SC Club Championships

Get your championship dashboard running in under 5 minutes!

## 🚀 Complete Workflow Overview

This system has 3 main components:

1. **Extract** - Process .RES files from MeetManager → Clean CSV files
2. **Calculate** - Compute championship scores → Result CSVs
3. **Display** - Launch interactive dashboard → View rankings

Let's get started! 🏊

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data processing
- `streamlit` - Dashboard framework
- `altair` - Visualization
- `pyarrow` - Fast Parquet file reading
- `psutil` - System monitoring

**Note**: No Excel libraries needed! We only process .RES files.

---

## Step 2: Prepare Your Data

Place your MeetManager .RES files in the raw files folder:

```
WSC_Club_Champs_2025/
└── raw_files/
    ├── CC25E301.RES
    ├── CC25E302.RES
    ├── CC25E303.RES
    └── ...
```

---

## Step 3: Extract Events from .RES Files

Run the extractor to convert .RES files to clean CSVs:

```bash
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files --output-dir WSC_Club_Champs_2025
```

**What it does:**
- ✅ Parses all .RES files
- ✅ Validates swimmer data (name, age, club, time, WA points)
- ✅ Categorizes events (Sprint, Free, 100 Form, 200 Form, IM, Distance)
- ✅ Determines gender from event names
- ✅ Creates CSV files in `cleaned_files/` folder

**Output:**
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

## Step 4: Calculate Championship Scores

Run the scoreboard calculator to compute championship results:

```bash
python club_championships_scoreboard.py
```

**What it does:**
- ✅ Loads all event CSVs
- ✅ Applies championship rules (max events per category by age)
- ✅ Calculates top 8 events for each swimmer
- ✅ Creates age group rankings
- ✅ Generates result files

**Output files created in `championship_results/`:**
- `championship_scoreboard_boys.csv` - Boys rankings
- `championship_scoreboard_girls.csv` - Girls rankings  
- `championship_age_group_winners.csv` - Trophy winners
- `championship_swimmer_narratives.csv` - Detailed breakdowns
- `events_all.parquet` - Combined events (for fast dashboard loading)

---

## Step 5: Launch the Dashboard

Start the interactive Streamlit dashboard:

```bash
streamlit run championship_dashboard_2025.py
```

Your browser will automatically open to `http://localhost:8501`

**Dashboard Features:**
- 📊 Interactive rankings by age and gender
- 🏊 Individual swimmer event breakdowns
- 🏁 Event-by-event rankings
- 📈 FINA points analysis charts
- 📥 Download reports as CSV

---

## 🎯 One-Command Quick Start

If your data is already in place, run all steps:

```bash
# Extract events
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files --output-dir WSC_Club_Champs_2025

# Calculate scores
python club_championships_scoreboard.py

# Launch dashboard
streamlit run championship_dashboard_2025.py
```

---

## 📁 Expected File Structure

After running all steps:

```
WSC_Club_Champs_2025/
├── raw_files/                    # Your .RES files
│   ├── CC25E301.RES
│   ├── CC25E302.RES
│   └── ...
├── cleaned_files/                # Extracted CSVs (auto-created)
│   ├── event_301.csv
│   ├── event_302.csv
│   └── ...
└── championship_results/         # Championship scores (auto-created)
    ├── championship_scoreboard_boys.csv
    ├── championship_scoreboard_girls.csv
    ├── championship_age_group_winners.csv
    ├── championship_swimmer_narratives.csv
    └── events_all.parquet
```

---

## 🔧 Troubleshooting

### No .RES files found
**Problem**: `RES folder not found` error

**Solution**: Check the path to your raw_files folder:
```bash
python swim_event_extractor.py --res-dir WSC_Club_Champs_2025/raw_files
```

### Module not found error
**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Dashboard shows no data
**Problem**: Dashboard displays "No data available"

**Solution**: Make sure you've run the scoreboard calculator first:
```bash
python club_championships_scoreboard.py
```

### Wrong championship folder
**Problem**: Scripts can't find your data

**Solution**: Update the folder name in the scripts:
- In `club_championships_scoreboard.py`, line 547: `base_folder = 'YOUR_FOLDER_NAME'`
- In `championship_dashboard_2025.py`, line 488: `events_folder = 'YOUR_FOLDER_NAME'`

---

## 🎨 Customization

### Change Worcester SC branding colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1a1d5a"        # Your primary color
backgroundColor = "#ffffff"      # Background
textColor = "#1a1d5a"           # Text color
```

### Add more club codes

Edit `swim_event_extractor.py`, around line 713:
```python
mapping = {
    'WORM': 'Worcester',
    'YOUR_CODE': 'Your Club Name',
}
```

---

## 📱 Mobile Access

The dashboard is mobile-responsive! Access it on your phone by:

1. Find your computer's local IP address:
   ```bash
   # Mac/Linux
   ipconfig getifaddr en0
   
   # Windows
   ipconfig
   ```

2. Run the dashboard with network access:
   ```bash
   streamlit run championship_dashboard_2025.py --server.address 0.0.0.0
   ```

3. On your phone, visit: `http://YOUR_IP_ADDRESS:8501`

---

## 🚀 Deploy to Streamlit Community Cloud (Free!)

Share your dashboard online:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with:
   - **Main file**: `championship_dashboard_2025.py`
   - **Python version**: 3.9+
   - **Requirements**: Uses `requirements.txt` automatically

Your dashboard will be live with a public URL! 🎉

---

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Championship Rules**: See the dashboard's "Championship Rules & Scoring" section
- **Worcester SC Website**: [worcestersc.co.uk](https://worcestersc.co.uk)

---

## 🏊 Next Steps

1. ✅ Run the complete workflow with your data
2. ✅ Explore the dashboard features
3. ✅ Download reports for your coaches
4. ✅ Share the dashboard URL with your club
5. ✅ Update data after each competition session

Happy swimming! 🏊‍♂️🏊‍♀️

---

**Need Help?**
- Check the full `README.md` for detailed documentation
- Review error messages carefully
- Ensure your .RES files are in the correct format
- Contact Worcester SC via [worcestersc.co.uk/contact](https://worcestersc.co.uk/contact)
