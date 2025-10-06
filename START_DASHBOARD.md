# 🏊 Quick Start - Championship Dashboard

## Launch the Dashboard

### Option 1: Double-click the launch script (Easiest)
```bash
./run_dashboard.sh
```

### Option 2: Run from terminal
```bash
cd /Users/boconnor/Documents/worcester_swim_club
streamlit run championship_dashboard.py
```

## What You'll See

The dashboard will automatically open in your web browser at:
**http://localhost:8501**

## Quick Guide

### 📊 View Rankings

1. **Select Gender** (left sidebar)
   - Boys
   - Girls  
   - All

2. **Select Age Group** (left sidebar)
   - 9-10 years
   - 11-12 years
   - 13-14 years
   - 15-16 years
   - 17+ years
   - All

3. **Choose View** (left sidebar)
   - All Swimmers (everyone who competed)
   - Championship Eligible Only (5+ categories)

### 📥 Export Results

Click the **"Download Rankings as CSV"** button at the bottom to export the current view.

### ✅ Championship Eligibility

Look for the ✅ symbol in the "Eligible" column:
- ✅ = Eligible for championship (competed in 5+ categories)
- ❌ = Not eligible (competed in fewer than 5 categories)

## Features

- **Real-time filtering** - No page reloads needed
- **Complete rankings** - Every swimmer included
- **Category breakdown** - See events per category for each swimmer
- **Sortable columns** - Click headers to sort
- **Export to CSV** - Download any filtered view

## Stopping the Dashboard

Press **Ctrl+C** in the terminal window to stop the dashboard.

## Troubleshooting

### Dashboard won't open?
1. Check that you're in the correct directory
2. Make sure these files exist:
   - `WSC Club Champs 2024.xlsx`
   - `WSC_Club_Champs_2024/cleaned_files/` folder

### Port already in use?
Try a different port:
```bash
streamlit run championship_dashboard.py --server.port 8502
```

---

**Worcester Swimming Club Championships** 🏆


