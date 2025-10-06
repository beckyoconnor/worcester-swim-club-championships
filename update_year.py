#!/usr/bin/env python3
"""
Year Update Script for Worcester Swimming Club Championships
==========================================================

This script automatically updates all hardcoded year references in the pipeline
from 2024 to 2025 (or any other year you specify).

Usage:
    python update_year.py                    # Updates 2024 -> 2025
    python update_year.py 2025 2026         # Updates 2025 -> 2026
    python update_year.py --dry-run         # Shows what would be changed without making changes
"""

import os
import re
import sys
import argparse
from pathlib import Path


class YearUpdater:
    """Updates year references in championship pipeline files."""
    
    def __init__(self, from_year="2024", to_year="2025", dry_run=False):
        self.from_year = from_year
        self.to_year = to_year
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_updated = []
        
    def update_file(self, file_path: str, patterns: list):
        """Update a single file with the given patterns."""
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_changes = 0
            
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    file_changes += 1
            
            if file_changes > 0:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                print(f"✓ {file_path}: {file_changes} changes")
                self.changes_made += file_changes
                self.files_updated.append(file_path)
                return True
            else:
                print(f"○ {file_path}: No changes needed")
                return False
                
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            return False
    
    def update_dashboard(self):
        """Update championship_dashboard.py"""
        patterns = [
            # Dashboard title (2 locations)
            (rf'Club Championships Dashboard {self.from_year}', f'Club Championships Dashboard {self.to_year}'),
            # Events folder path
            (rf"events_folder = 'WSC_Club_Champs_{self.from_year}'", f"events_folder = 'WSC_Club_Champs_{self.to_year}'"),
            # Copyright year
            (rf'© {self.from_year} Worcester Swimming Club', f'© {self.to_year} Worcester Swimming Club')
        ]
        return self.update_file('championship_dashboard.py', patterns)
    
    def update_scoreboard(self):
        """Update club_championships_scoreboard.py"""
        patterns = [
            # Excel file name
            (rf"'WSC Club Champs {self.from_year}\.xlsx'", f"'WSC Club Champs {self.to_year}.xlsx'"),
            # Events folder path
            (rf"'WSC_Club_Champs_{self.from_year}/cleaned_files'", f"'WSC_Club_Champs_{self.to_year}/cleaned_files'"),
            # Output folder path
            (rf"'WSC_Club_Champs_{self.from_year}'", f"'WSC_Club_Champs_{self.to_year}'")
        ]
        return self.update_file('club_championships_scoreboard.py', patterns)
    
    def update_examples(self):
        """Update example files (optional)"""
        example_files = [
            'example_usage.py',
            'swim_event_extractor.py'
        ]
        
        patterns = [
            # Excel file references
            (rf"'WSC Club Champs {self.from_year}\.xlsx'", f"'WSC Club Champs {self.to_year}.xlsx'"),
            (rf'"WSC Club Champs {self.from_year}\.xlsx"', f'"WSC Club Champs {self.to_year}.xlsx"'),
            # Folder references
            (rf'WSC_Club_Champs_{self.from_year}', f'WSC_Club_Champs_{self.to_year}')
        ]
        
        updated = False
        for file_path in example_files:
            if os.path.exists(file_path):
                if self.update_file(file_path, patterns):
                    updated = True
        return updated
    
    def run(self):
        """Run the complete update process."""
        print("=" * 60)
        print(f"🔄 UPDATING CHAMPIONSHIP PIPELINE: {self.from_year} → {self.to_year}")
        print("=" * 60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()
        
        # Update main files
        print("📊 Updating main dashboard...")
        self.update_dashboard()
        
        print("\n🏆 Updating scoreboard script...")
        self.update_scoreboard()
        
        print("\n📝 Updating example files...")
        self.update_examples()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        
        if self.changes_made > 0:
            print(f"✅ {self.changes_made} changes made in {len(self.files_updated)} files:")
            for file_path in self.files_updated:
                print(f"   • {file_path}")
            
            if not self.dry_run:
                print(f"\n🎉 Pipeline updated successfully!")
                print(f"\n📁 Expected file structure for {self.to_year}:")
                print(f"   • WSC Club Champs {self.to_year}.xlsx")
                print(f"   • WSC_Club_Champs_{self.to_year}/")
                print(f"   • WSC_Club_Champs_{self.to_year}/cleaned_files/")
                
                print(f"\n🚀 Next steps:")
                print(f"   1. Extract data: python swim_event_extractor.py \"WSC Club Champs {self.to_year}.xlsx\"")
                print(f"   2. Test scoreboard: python club_championships_scoreboard.py")
                print(f"   3. Test dashboard: streamlit run championship_dashboard.py")
            else:
                print(f"\n💡 Run without --dry-run to apply these changes")
        else:
            print("ℹ️  No changes needed - files are already up to date")
        
        print("=" * 60)


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Update year references in Worcester Swimming Club Championship pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_year.py                    # Update 2024 -> 2025
  python update_year.py 2025 2026         # Update 2025 -> 2026  
  python update_year.py --dry-run          # Show what would change
        """
    )
    
    parser.add_argument(
        'from_year', 
        nargs='?', 
        default='2024',
        help='Year to update from (default: 2024)'
    )
    
    parser.add_argument(
        'to_year', 
        nargs='?', 
        default='2025',
        help='Year to update to (default: 2025)'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    args = parser.parse_args()
    
    # Validate years
    try:
        int(args.from_year)
        int(args.to_year)
    except ValueError:
        print("❌ Error: Years must be numeric (e.g., 2024, 2025)")
        sys.exit(1)
    
    # Run the updater
    updater = YearUpdater(args.from_year, args.to_year, args.dry_run)
    updater.run()


if __name__ == "__main__":
    main()
