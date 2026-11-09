#!/usr/bin/env python3
"""
Worcester SC Club Championships - year switcher.

Entry point for Streamlit Community Cloud. Shows a year switcher in the top bar:
  2025         -> championship_dashboard_2025.py (top-8, category-limit rules)
  2026 (test)  -> championship_dashboard_2026.py (four-bucket rules)

2025 is the default while the 2026 dashboard is being tested.
"""

import runpy

import streamlit as st

st.set_page_config(page_title="Worcester SC - Club Championships", page_icon="🏊", layout="wide")

# Mobile tweaks shared by every year's page.
# - styles.css hides the sidebar, but on narrow screens Streamlit moves the top-bar year
#   switcher into the sidebar, so re-show it there (higher specificity beats styles.css).
# - Shrink the club header so it doesn't fill a phone screen.
st.html("""<style>
@media (max-width: 768px) {
  html body section[data-testid="stSidebar"] { display: flex !important; }
  .wsc-header { padding: 1rem !important; gap: 0.9rem !important; margin-bottom: 1rem !important; }
  .wsc-header-logo img { width: 64px !important; }
  .wsc-header-text h1 { font-size: 1.35rem !important; line-height: 1.2 !important; }
  .wsc-header-text h2 { font-size: 0.95rem !important; margin-top: 0.25rem !important; }
  .wsc-header-text p { font-size: 0.8rem !important; margin-top: 0.25rem !important; }
}
</style>""")


def run_dashboard(path: str, year: int):
    def page():
        runpy.run_path(path, init_globals={'CHAMPS_YEAR': year}, run_name='__main__')
    # Streamlit identifies callable pages by function name, so each year needs a unique one
    page.__name__ = page.__qualname__ = f"champs_{year}"
    return page


pages = [
    st.Page(run_dashboard('championship_dashboard_2025.py', 2025), title="2025",
            url_path="2025", icon=":material/emoji_events:", default=True),
    st.Page(run_dashboard('championship_dashboard_2026.py', 2026), title="2026 (test)",
            url_path="2026", icon=":material/science:"),
]

st.navigation(pages, position="top").run()
