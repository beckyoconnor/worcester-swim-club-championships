#!/bin/bash

# Swimming Analysis Notebook Launcher
# This script activates the virtual environment and launches Jupyter

echo "=================================="
echo "Swimming Analysis Notebook Launcher"
echo "=================================="
echo ""

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$DIR/swim_analysis_env/bin/activate"

echo "✓ Virtual environment activated"
echo "✓ Starting Jupyter Notebook..."
echo ""
echo "The notebook will open in your browser."
echo "To stop the server, press Ctrl+C"
echo ""

# Launch Jupyter notebook
cd "$DIR"
jupyter notebook swimming_analysis.ipynb

