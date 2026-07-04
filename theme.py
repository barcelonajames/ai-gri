"""
theme.py
Central AI-gri branding and theming for the whole app.

This is the single source of truth for the AI-gri look. Every page
(login, register, dashboard) calls inject_theme() once at the top of
its render, and pulls the logo + toggle from here. Change a color or
the logo here and all three pages update together.

What this enforces:
  - Arial across the whole interface
  - Bold headers, regular subtext
  - Two uniform themes controlled by one toggle:
      * dark  -> navy background, light text, green-white logo  (default)
      * light -> beige background, dark text,  green-black logo
    The toggle flips EVERYTHING together (background, sidebar, text,
    inputs, accent) so the whole app changes at once.
  - Brand green (#669933, taken straight from the logo) replaces
    Streamlit's default red accent everywhere.
"""

import base64
import os
import streamlit as st

# ---------------------------------------------------------------------------
# Brand palette  (all values pulled from the AI-gri logo + pitch deck)
# ---------------------------------------------------------------------------
GREEN      = "#669933"   # exact green in both logo files (thumb / leaf)
GREEN_DARK = "#4F7A26"   # hover / pressed state for the green button
LEAF_LIGHT = "#97C459"   # lighter green accent (links on dark bg)
INK        = "#0A0A0A"   # wordmark black (light-mode text)
NAVY       = "#0E2A47"   # dark-mode background (matches the deck)
NAVY_DEEP  = "#0A2038"   # slightly deeper navy for inputs on dark
BEIGE      = "#F4F6F1"   # light-mode background (matches the deck)
WHITE      = "#FFFFFF"

# Per-theme token sets. Every page reads from the active one.
DARK = {
    "bg":        NAVY,
    "sidebar":   NAVY_DEEP,
    "surface":   "#12314F",   # cards / bordered containers
    "text":      "#EAF3DE",
    "text2":     "#A8C0AC",   # subtext / captions
    "muted":     "#7C9080",
    "border":    "#1E3A28",
    "input_bg":  NAVY_DEEP,
    "accent":    GREEN,
    "link":      LEAF_LIGHT,
    "logo":      "aigri_greenwhite.png",
}
LIGHT = {
    "bg":        BEIGE,
    "sidebar":   "#EBEEE6",
    "surface":   WHITE,
    "text":      "#13261A",
    "text2":     "#5A6B5E",
    "muted":     "#8A968C",
    "border":    "#D3D1C7",
    "input_bg":  WHITE,
    "accent":    GREEN,
    "link":      GREEN_DARK,
    "logo":      "aigri_greenblack.png",
}

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")


# ---------------------------------------------------------------------------
# Theme state + toggle
# ---------------------------------------------------------------------------
def init_theme():
    """Ensure a theme value exists. Defaults to dark (matches the deck)."""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def current() -> dict:
    """Return the active token set."""
    init_theme()
    return DARK if st.session_state.theme == "dark" else LIGHT


def _toggle():
    st.session_state.theme = (
        "light" if st.session_state.theme == "dark" else "dark"
    )


def theme_toggle(where="corner"):
    """
    Render the light/dark switch.
      where="corner"  -> floating top-right (login / register)
      where="sidebar" -> full-width button (dashboard sidebar)
    """
    init_theme()
    is_dark = st.session_state.theme == "dark"
    label = "Light mode" if is_dark else "Dark mode"
    icon = "\u2600\ufe0f" if is_dark else "\U0001F319"  # sun / moon

    if where == "sidebar":
        if st.button(f"{icon}  {label}", use_container_width=True,
                     key="theme_toggle_sidebar"):
            _toggle()
            st.rerun()
        return

    # corner: place the button inside a right-aligned narrow column,
    # then nudge it to the top-right with CSS targeting its wrapper.
    st.markdown('<div id="aigri-corner-toggle"></div>', unsafe_allow_html=True)
    spacer, btn = st.columns([6, 1])
    with btn:
        if st.button(f"{icon} {label}", key="theme_toggle_corner"):
            _toggle()
            st.rerun()


# ---------------------------------------------------------------------------
# Logo helpers
# ---------------------------------------------------------------------------
def _logo_b64(filename: str):
    path = os.path.join(_ASSETS, filename)
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None


def logo_centered(width: int = 150):
    """Centered logo for the login / register header (theme-aware)."""
    t = current()
    b64 = _logo_b64(t["logo"])
    if b64:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;margin-bottom:8px;">
              <img src="data:image/png;base64,{b64}" width="{width}"
                   alt="AI-gri logo"/>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Fallback if the asset is missing, so the app still runs.
        st.markdown(
            f"<h1 style='text-align:center;color:{t['accent']};'>Ai-gri</h1>",
            unsafe_allow_html=True,
        )


def logo_sidebar(width: int = 130):
    """Logo pinned at the bottom of the dashboard sidebar (theme-aware)."""
    t = current()
    b64 = _logo_b64(t["logo"])
    if b64:
        st.sidebar.markdown(
            f"""
            <div style="display:flex;justify-content:center;
                        margin-top:24px;padding-top:16px;
                        border-top:1px solid {t['border']};">
              <img src="data:image/png;base64,{b64}" width="{width}"
                   alt="AI-gri logo"/>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# The big one: CSS injection that themes the whole interface
# ---------------------------------------------------------------------------
def inject_theme():
    """Call once at the top of every page render."""
    t = current()
    css = f"""
    <style>
      /* ---- Arial everywhere ------------------------------------ */
      html, body, [class*="css"], .stApp, .stMarkdown,
      input, textarea, select, button,
      [data-testid="stWidgetLabel"], [data-baseweb="select"] * {{
          font-family: Arial, Helvetica, sans-serif !important;
      }}

      /* ---- App background + base text -------------------------- */
      .stApp {{ background: {t['bg']}; color: {t['text']}; }}
      .block-container {{ padding-top: 3rem; }}

      /* ---- Headers bold, captions regular ---------------------- */
      h1, h2, h3, h4, h5, h6 {{
          font-weight: 700 !important; color: {t['text']} !important;
      }}
      [data-testid="stCaptionContainer"], .stCaption {{
          font-weight: 400 !important; color: {t['text2']} !important;
      }}
      p, span, label, li {{ color: {t['text']}; }}

      /* ---- Sidebar flips with the theme ------------------------ */
      [data-testid="stSidebar"] {{ background: {t['sidebar']} !important; }}
      [data-testid="stSidebar"] * {{ color: {t['text']} !important; }}

      /* ---- Bordered containers / cards ------------------------- */
      [data-testid="stVerticalBlockBorderWrapper"] {{
          background: {t['surface']};
          border-radius: 12px;
      }}

      /* ---- Inputs ---------------------------------------------- */
      .stTextInput input, .stNumberInput input, .stDateInput input,
      [data-baseweb="select"] > div {{
          background: {t['input_bg']} !important;
          color: {t['text']} !important;
          border: 1px solid {t['border']} !important;
          border-radius: 8px !important;
      }}
      .stTextInput input::placeholder {{ color: {t['muted']} !important; }}

      /* ---- Primary button = brand green (replaces red) --------- */
      .stButton button[kind="primary"] {{
          background: {t['accent']} !important;
          color: #FFFFFF !important;
          border: none !important;
          border-radius: 8px !important;
          font-weight: 700 !important;
      }}
      .stButton button[kind="primary"]:hover {{
          background: {GREEN_DARK} !important;
      }}
      /* secondary buttons: subtle, themed border */
      .stButton button[kind="secondary"] {{
          background: transparent !important;
          color: {t['text']} !important;
          border: 1px solid {t['border']} !important;
          border-radius: 8px !important;
      }}

      /* ---- Radio nav (sidebar) selected dot = green ------------ */
      [data-testid="stSidebar"] [data-baseweb="radio"] [aria-checked="true"] div {{
          background: {t['accent']} !important;
          border-color: {t['accent']} !important;
      }}

      /* ---- Metric cards ---------------------------------------- */
      [data-testid="stMetricValue"] {{
          color: {t['text']} !important; font-weight: 700 !important;
      }}
      [data-testid="stMetricLabel"] {{ color: {t['text2']} !important; }}

      /* ---- Float the corner theme toggle to the top-right ------ */
      div[data-testid="stHorizontalBlock"]:has(#aigri-corner-toggle) {{
          position: absolute; top: 0.5rem; right: 1rem;
          width: auto; z-index: 999;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
