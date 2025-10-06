# 🏊 Club Championships Dashboard

An interactive Streamlit dashboard to view and explore championship rankings.

## Features

✅ **Interactive Filtering**
- Filter by gender (Boys/Girls/All)
- Filter by age group (9-10, 11-12, 13-14, 15-16, 17+, All)
- Toggle between all swimmers or championship-eligible only

✅ **Complete Rankings**
- View all swimmers sorted by total points
- See detailed category breakdown for each swimmer
- Championship eligibility indicator (✅/❌)

✅ **Real-time Statistics**
- Total swimmers count
- Championship-eligible count
- Average total points
- Highest score

✅ **Export Functionality**
- Download filtered rankings as CSV
- Custom filename based on filters

## How to Run

### Option 1: Using the launch script
```bash
./run_dashboard.sh
```

### Option 2: Direct command
```bash
streamlit run championship_dashboard.py
```

### Option 3: From Python
```bash
python3 -m streamlit run championship_dashboard.py
```

## Dashboard Opens Automatically

Once launched, the dashboard will automatically open in your default web browser at:
- **Local URL**: http://localhost:8501

## Using the Dashboard

### Sidebar Filters

1. **Gender**: Select Boys, Girls, or All swimmers
2. **Age Group**: Choose specific age group or view all ages
3. **Swimmers**: Toggle between:
   - **All Swimmers** - Shows everyone who competed
   - **Championship Eligible Only** - Shows only swimmers with 5+ categories

### Main Display

The main table shows:
- **Rank** - Position in filtered view
- **Name** - Swimmer name
- **Age** - Individual age
- **Age Group** - Championship age group
- **Club** - Club affiliation
- **Total Points** - Sum of best 8 events
- **Avg Points** - Average points per event
- **Events** - Number of events counted (up to 8)
- **Categories** - Number of categories competed in
- **Eligible** - ✅ if eligible for championship (5+ categories)
- **Category Breakdown** - Number of events per category:
  - Sprint (50m events)
  - Free (100m, 200m, 400m freestyle)
  - 100 Form (100m back/breast/fly)
  - 200 Form (200m back/breast/fly)
  - IM (100m, 200m, 400m IM)
  - Distance (800m, 1500m)

### Export Rankings

Click the **"📥 Download Rankings as CSV"** button to export the current filtered view to a CSV file.

## Championship Rules

### Eligibility
- Must compete in **at least 5 of the 6 categories**
- Best 8 events are counted

### Category Limits
- **Under 12s**: Maximum 3 races per category
- **12 and over**: Maximum 2 races per category

### Categories
1. **Sprint** - 50m free, back, breast and fly
2. **Free** - 100m, 200m and 400m free
3. **100 Form** - 100m back, breast and fly
4. **200 Form** - 200m back, breast and fly
5. **IM** - 100m, 200m, and 400m IM
6. **Distance** - 800m and 1500m

## Technical Details

### Data Source
- Reads from `WSC Club Champs 2024.xlsx`
- Loads cleaned event data from `WSC_Club_Champs_2024/cleaned_files/`

### Caching
The dashboard uses Streamlit's caching to improve performance:
- Event data is cached on first load
- Calculations are cached for faster filtering

### Requirements
- Python 3.7+
- streamlit
- pandas
- openpyxl

## Troubleshooting

### Dashboard won't start
1. Ensure you're in the correct directory
2. Check that all required files exist:
   - `WSC Club Champs 2024.xlsx`
   - `WSC_Club_Champs_2024/cleaned_files/` folder with event CSVs

### Port already in use
If port 8501 is already in use:
```bash
streamlit run championship_dashboard.py --server.port 8502
```

### Clear cache
If data seems stale, stop the app (Ctrl+C) and restart it.

## Support

For issues or questions, contact the swim club administrator.

---

**Worcester Swimming Club** 🏊‍♂️🏊‍♀️


