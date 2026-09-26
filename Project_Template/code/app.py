"""StreamGlass — an academic OTT intelligence application."""

import os
import sys
import html
import math
import re
import base64
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import importlib

sys.path.insert(0, os.path.dirname(__file__))
import database
try:
    importlib.reload(database)
except Exception:
    pass
import discrete_math
import graph_engine
import recommender

def _get_or_create_demo_subscriber(identifier: str, db_path: str = None) -> str:
    """Finds or creates a subscriber profile matching the login identifier."""
    if not identifier:
        return "U101"
    ident = str(identifier).strip()
    try:
        conn = database.get_connection(db_path)
        cursor = conn.cursor()

        # 1. Exact match on user_id
        cursor.execute("SELECT user_id FROM users WHERE LOWER(user_id) = LOWER(?);", (ident,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]

        # 2. Match on name
        cursor.execute("SELECT user_id FROM users WHERE LOWER(name) = LOWER(?);", (ident,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]

        # 3. If email like 'user@domain.com', check if name matches prefix
        name_part = ident.split("@")[0].replace(".", " ").title()
        cursor.execute("SELECT user_id FROM users WHERE LOWER(name) = LOWER(?);", (name_part,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]

        # 4. Generate next user_id
        cursor.execute("SELECT user_id FROM users WHERE user_id LIKE 'U%';")
        all_uids = cursor.fetchall()
        max_num = 100
        for (uid,) in all_uids:
            try:
                num = int(str(uid)[1:])
                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                pass
        new_user_id = f"U{max_num + 1}"
        display_name = name_part if name_part else ident

        cursor.execute("""
        INSERT INTO users (user_id, name, age, primary_language, secondary_language, preferred_genres, persona_desc)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            new_user_id,
            display_name,
            25,
            "Telugu",
            "English",
            '["Drama", "Action"]',
            f"Signed-in subscriber account for {display_name}."
        ))
        conn.commit()
        conn.close()
        return new_user_id
    except Exception:
        try:
            users_df = database.get_all_users(db_path)
            if not users_df.empty:
                return users_df.iloc[0]["user_id"]
        except Exception:
            pass
        return "U101"

if not hasattr(database, "get_or_create_demo_subscriber"):
    database.get_or_create_demo_subscriber = _get_or_create_demo_subscriber

st.set_page_config(page_title="StreamGlass", page_icon="▷", layout="wide", initial_sidebar_state="collapsed")

BRAND_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "streamglass-logo.png")
with open(BRAND_LOGO_PATH, "rb") as brand_logo_file:
    BRAND_LOGO_DATA_URI = "data:image/png;base64," + base64.b64encode(brand_logo_file.read()).decode("ascii")

THEME_DEFAULT_VERSION = 1
if st.session_state.get("theme_default_version") != THEME_DEFAULT_VERSION:
    st.session_state.app_theme = "Light"
    st.session_state.theme_default_version = THEME_DEFAULT_VERSION
elif "app_theme" not in st.session_state:
    st.session_state.app_theme = "Light"

def get_apple_ui_css(theme_mode):
    light_vars = """
        --canvas:#f5f5f7;
        --surface:#ffffff;
        --ink:#1d1d1f;
        --ink-soft:#424245;
        --muted:#6e6e73;
        --faint:#86868b;
        --line:rgba(60,60,67,.16);
        --line-soft:rgba(60,60,67,.10);
        --blue:#0071e3;
        --blue-wash:#e8f2ff;
        --green:#248a3d;
        --orange:#b25000;
        --red:#c53b3b;
        --radius:18px;
        --glass-bg:rgba(250,250,252,.82);
        --glass-border:rgba(255,255,255,.75);
        --glass-shadow:rgba(30,30,35,.10);
        --glass-inset:rgba(255,255,255,.88);
        --hover-bg:rgba(60,60,67,.07);
        --pill-active-bg:rgba(255,255,255,.94);
        --pill-active-shadow:0 2px 8px rgba(60,60,67,.12), inset 0 0 0 1px rgba(60,60,67,.08);
        --formula-bg:#fbfbfc;
        --chip-bg:#f2f2f5;
        --chip-border:rgba(60,60,67,.10);
        --chip-color:#424245;
        --brand-bg:#1d1d1f;
        --brand-color:#ffffff;
        --card-border-hover:rgba(60,60,67,.20);
        --card-shadow-hover:0 8px 20px rgba(30,30,35,.08);
        --pipeline-bg:rgba(255,255,255,.58);
        --input-bg:rgba(255,255,255,.86);
    """
    dark_vars = """
        --canvas:#09090b;
        --surface:#17171a;
        --ink:#f5f5f7;
        --ink-soft:#d2d2d7;
        --muted:#9a9aa0;
        --faint:#636366;
        --line:rgba(255,255,255,.14);
        --line-soft:rgba(255,255,255,.08);
        --blue:#2997ff;
        --blue-wash:rgba(41,151,255,.16);
        --green:#30d158;
        --orange:#ff9f0a;
        --red:#ff453a;
        --radius:18px;
        --glass-bg:rgba(26,26,29,.85);
        --glass-border:rgba(255,255,255,.15);
        --glass-shadow:rgba(0,0,0,.50);
        --glass-inset:rgba(255,255,255,.10);
        --hover-bg:rgba(255,255,255,.08);
        --pill-active-bg:rgba(255,255,255,.18);
        --pill-active-shadow:0 2px 8px rgba(0,0,0,.45), inset 0 0 0 1px rgba(255,255,255,.14);
        --formula-bg:#121214;
        --chip-bg:#232326;
        --chip-border:rgba(255,255,255,.12);
        --chip-color:#d2d2d7;
        --brand-bg:#ffffff;
        --brand-color:#000000;
        --card-border-hover:rgba(255,255,255,.24);
        --card-shadow-hover:0 8px 24px rgba(0,0,0,.40);
        --pipeline-bg:rgba(255,255,255,.04);
        --input-bg:rgba(30,30,34,.90);
    """

    if theme_mode == "Dark":
        theme_rules = f":root {{ {dark_vars} }}"
        app_bg = "radial-gradient(circle at 84% -12%,rgba(41,151,255,.08),transparent 27rem),radial-gradient(circle at 7% 17%,rgba(255,255,255,.04),transparent 25rem),var(--canvas) !important;"
    elif theme_mode == "Light":
        theme_rules = f":root {{ {light_vars} }}"
        app_bg = "radial-gradient(circle at 84% -12%,rgba(0,113,227,.055),transparent 27rem),radial-gradient(circle at 7% 17%,rgba(125,126,135,.065),transparent 25rem),var(--canvas) !important;"
    else:
        theme_rules = f""":root {{ {light_vars} }}
        [data-testid="stAppViewContainer"] {{ background:radial-gradient(circle at 84% -12%,rgba(0,113,227,.055),transparent 27rem),radial-gradient(circle at 7% 17%,rgba(125,126,135,.065),transparent 25rem),var(--canvas) !important; }}
        @media (prefers-color-scheme: dark) {{
            :root {{ {dark_vars} }}
            [data-testid="stAppViewContainer"] {{ background:radial-gradient(circle at 84% -12%,rgba(41,151,255,.08),transparent 27rem),radial-gradient(circle at 7% 17%,rgba(255,255,255,.04),transparent 25rem),var(--canvas) !important; }}
        }}"""
        app_bg = None

    bg_style = f'[data-testid="stAppViewContainer"] {{ background: {app_bg}; }}' if app_bg else ""

    return f"""
<style>
{theme_rules}
{bg_style}
html, body, [class*="css"] {{ font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Segoe UI",sans-serif !important; color:var(--ink) !important; }}
[data-testid="stHeader"] {{ display:none !important; height:0 !important; pointer-events:none !important; }}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ visibility:hidden !important; display:none !important; }}
.block-container {{ max-width:1220px !important; padding:7.2rem 28px 3.5rem !important; }}

/* Glassmorphism navigation & theme bar */
.st-key-liquid_top_nav {{ position:fixed !important; top:14px !important; left:50% !important; transform:translateX(-50%) !important; width:min(1180px,calc(100vw - 40px)) !important; z-index:999999 !important; padding:7px 10px !important; border:1px solid var(--glass-border) !important; border-radius:24px !important; background:var(--glass-bg) !important; box-shadow:0 14px 34px var(--glass-shadow),inset 0 1px 0 var(--glass-inset) !important; backdrop-filter:blur(30px) saturate(155%) !important; -webkit-backdrop-filter:blur(30px) saturate(155%) !important; pointer-events:auto !important; }}
.st-key-liquid_top_nav [data-testid="stWidgetLabel"] {{ display:none !important; }}
 .st-key-liquid_top_nav [data-testid="stVerticalBlock"],
 .st-key-liquid_top_nav [data-testid="stHorizontalBlock"] {{ gap:12px !important; align-items:center !important; width:100% !important; }}
.st-key-liquid_top_nav [data-testid="stColumn"] {{ display:flex !important; align-items:center !important; min-width:0 !important; }}
.st-key-liquid_top_nav [data-testid="stColumn"]:nth-child(3) {{ border-left:1px solid var(--line-soft) !important; padding-left:8px !important; }}
.nav-brand {{ display:flex;align-items:center;gap:10px;white-space:nowrap;color:var(--ink);font-size:.92rem;font-weight:740;letter-spacing:-.025em; }}
.nav-brand .brand-mark {{ width:30px;height:30px;border-radius:10px;display:inline-grid;place-items:center;background:url("{BRAND_LOGO_DATA_URI}") center/cover no-repeat;color:transparent;font-size:0;box-shadow:0 5px 14px rgba(0,113,227,.24),inset 0 1px 0 rgba(255,255,255,.45); }}
.st-key-liquid_top_nav .st-key-liquid_brand button {{ min-height:32px !important;padding:0 1px !important;border:0 !important;border-radius:10px !important;background:transparent !important;color:var(--ink) !important;font-size:.92rem !important;font-weight:740 !important;letter-spacing:-.025em !important;box-shadow:none !important;display:flex !important;align-items:center !important;gap:10px !important;white-space:nowrap !important; }}
.st-key-liquid_top_nav .st-key-liquid_brand button:before {{ content:"";width:30px;height:30px;border-radius:10px;display:inline-grid;place-items:center;background:url("{BRAND_LOGO_DATA_URI}") center/cover no-repeat;box-shadow:0 5px 14px rgba(0,113,227,.24),inset 0 1px 0 rgba(255,255,255,.45); }}
.st-key-liquid_top_nav .st-key-liquid_brand button:hover {{ background:transparent !important;transform:translateY(-1px) !important;filter:brightness(1.06) !important; }}
.landing-header-marker {{ display:none !important; }}
/* Landing page full-viewport composition: zero outer padding, no horizontal line, seamless fluid canvas */
body:has(.landing-header-marker) .block-container,
body:has(.landing-header-marker) [data-testid="stAppViewContainer"],
body:has(.landing-header-marker) .main {{ max-width:100% !important;padding:0 !important;margin:0 !important;overflow-x:hidden !important; }}
.st-key-landing_top_nav,
.st-key-liquid_top_nav:has(.landing-header-marker) {{ position:fixed !important;top:0 !important;left:0 !important;transform:none !important;width:100% !important;padding:22px clamp(24px,5vw,68px) !important;border:0 !important;border-top:0 !important;border-bottom:0 !important;border-radius:0 !important;background:transparent !important;box-shadow:none !important;backdrop-filter:none !important;-webkit-backdrop-filter:none !important;pointer-events:none !important;z-index:999999 !important; }}
.st-key-landing_top_nav [data-testid="stHorizontalBlock"],
.st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stHorizontalBlock"] {{ display:flex !important;align-items:center !important;justify-content:space-between !important;gap:16px !important;border:none !important;border-bottom:none !important;border-top:none !important; }}
.st-key-landing_top_nav [data-testid="stColumn"],
.st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stColumn"] {{ width:auto !important;min-width:0 !important;border:none !important;border-left:0 !important;padding:0 !important; }}
.st-key-landing_top_nav [data-testid="stColumn"]:first-child,
.st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stColumn"]:first-child {{ flex:1 1 auto !important;justify-content:flex-start !important; }}
.st-key-landing_top_nav [data-testid="stColumn"]:last-child,
.st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stColumn"]:last-child {{ flex:0 0 auto !important;justify-content:flex-end !important;border-left:0 !important;padding-left:0 !important; }}
.st-key-landing_top_nav .st-key-liquid_brand button,
.st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_brand button {{ position:fixed !important;z-index:1000000 !important;top:22px !important;left:clamp(24px,5vw,68px) !important;width:auto !important;pointer-events:auto !important;min-height:32px !important;padding:0 1px !important;border:0 !important;border-radius:10px !important;background:transparent !important;color:var(--ink) !important;font-size:.92rem !important;font-weight:740 !important;letter-spacing:-.025em !important;box-shadow:none !important;display:flex !important;align-items:center !important;gap:10px !important;white-space:nowrap !important; }}
.st-key-landing_top_nav .st-key-liquid_brand button:before,
.st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_brand button:before {{ content:"";width:30px;height:30px;border-radius:10px;display:inline-grid;place-items:center;background:url("{BRAND_LOGO_DATA_URI}") center/cover no-repeat;box-shadow:0 5px 14px rgba(0,113,227,.24),inset 0 1px 0 rgba(255,255,255,.45); }}
.st-key-landing_top_nav .st-key-liquid_brand button:hover,
.st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_brand button:hover {{ background:transparent !important;transform:translateY(-1px) !important;filter:brightness(1.06) !important; }}
.st-key-landing_top_nav .st-key-liquid_login button,
.st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_login button {{ position:fixed !important;z-index:1000000 !important;top:22px !important;right:clamp(24px,5vw,68px) !important;width:auto !important;pointer-events:auto !important;min-height:36px !important;padding:0 15px !important;border:1px solid rgba(0,113,227,.24) !important;border-radius:13px !important;background:linear-gradient(135deg,#1683f5,#0066d5) !important;color:#fff !important;font-size:.78rem !important;font-weight:700 !important;white-space:nowrap !important;box-shadow:0 6px 16px rgba(0,113,227,.20),inset 0 1px 0 rgba(255,255,255,.3) !important; }}
.st-key-landing_top_nav .st-key-liquid_login button:hover,
.st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_login button:hover {{ transform:translateY(-1px) !important;filter:brightness(1.06) !important;box-shadow:0 9px 20px rgba(0,113,227,.27),inset 0 1px 0 rgba(255,255,255,.35) !important; }}
.st-key-liquid_top_nav > [data-testid="stElementContainer"],
.st-key-liquid_top_nav [data-testid="stRadio"] {{ width:100% !important; margin:0 !important; padding:0 !important; }}
 .st-key-liquid_top_nav [data-testid="stRadioGroup"],
 .st-key-liquid_top_nav [role="radiogroup"] {{ display:flex !important; flex-direction:row !important; flex-wrap:nowrap !important; align-items:center !important; justify-content:space-between !important; gap:7px !important; width:100% !important; margin:0 !important; padding:0 !important; }}
 /* Each selection pill sizes itself to its label, rather than to an equal grid cell. */
 .st-key-liquid_top_nav [data-testid="stRadioGroup"] > div,
 .st-key-liquid_top_nav .react-aria-RadioField {{ flex:0 0 auto !important; width:auto !important; min-width:0 !important; display:flex !important; align-items:stretch !important; justify-content:center !important; margin:0 !important; padding:0 !important; }}
 .st-key-liquid_top_nav [data-testid="stRadioOption"] {{ flex:0 0 auto !important; width:auto !important; min-width:0 !important; min-height:36px !important; display:flex !important; align-items:center !important; justify-content:center !important; margin:0 !important; padding:0 12px !important; border:0 !important; border-radius:14px !important; background:transparent !important; cursor:pointer !important; pointer-events:auto !important; box-sizing:border-box !important; transition:background 180ms ease,color 180ms ease,transform 180ms ease,box-shadow 180ms ease !important; }}
 /* Nuke the native radio circle/dot — all known selector patterns */
 .st-key-liquid_top_nav input[type="radio"],
 .st-key-liquid_top_nav [data-testid="stRadioOption"] input {{ position:absolute !important; opacity:0 !important; width:0 !important; height:0 !important; margin:0 !important; padding:0 !important; clip:rect(0,0,0,0) !important; overflow:hidden !important; pointer-events:none !important; }}
 .st-key-liquid_top_nav [data-testid="stRadioOption"] [class*="indicator"],
 .st-key-liquid_top_nav [data-testid="stRadioOption"] > div > div:first-child,
 .st-key-liquid_top_nav [data-testid="stRadioOption"] svg {{ display:none !important; width:0 !important; height:0 !important; margin:0 !important; padding:0 !important; overflow:hidden !important; flex:none !important; }}
.st-key-liquid_top_nav [data-testid="stRadioOption"] > div {{ display:flex !important; align-items:center !important; justify-content:center !important; gap:0 !important; margin:0 !important; padding:0 !important; cursor:pointer !important; }}
.st-key-liquid_top_nav [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"],
.st-key-liquid_top_nav [data-testid="stRadioOption"] .stMarkdown,
.st-key-liquid_top_nav [data-testid="stRadioOption"] > div > div:last-child {{ display:flex !important; align-items:center !important; justify-content:center !important; margin:0 !important; padding:0 !important; }}
 .st-key-liquid_top_nav [data-testid="stRadioOption"] p,
 .st-key-liquid_top_nav [data-testid="stRadioOption"] label,
 .st-key-liquid_top_nav [data-testid="stRadioOption"] span {{ margin:0 !important; padding:0 !important; color:var(--muted) !important; font-size:.78rem !important; font-weight:600 !important; letter-spacing:.005em !important; white-space:nowrap !important; text-align:center !important; cursor:pointer !important; transition:color 180ms ease !important; background:transparent !important; }}
/* Keep the selected state visible after hiding Streamlit's native radio marker. */
.st-key-liquid_top_nav [data-testid="stRadioOption"][data-selected="true"],
.st-key-liquid_top_nav [data-testid="stRadioOption"]:has(input:checked),
.st-key-liquid_top_nav [data-testid="stRadioOption"][aria-checked="true"],
.st-key-liquid_top_nav .react-aria-RadioField[data-selected="true"] [data-testid="stRadioOption"],
.st-key-liquid_top_nav .react-aria-RadioField:has(input:checked) [data-testid="stRadioOption"] {{ background:var(--pill-active-bg) !important; box-shadow:var(--pill-active-shadow) !important; }}
.st-key-liquid_top_nav [data-testid="stRadioOption"][data-selected="true"] p,
.st-key-liquid_top_nav [data-testid="stRadioOption"][data-selected="true"] label,
.st-key-liquid_top_nav [data-testid="stRadioOption"][data-selected="true"] span,
.st-key-liquid_top_nav [data-testid="stRadioOption"]:has(input:checked) p,
.st-key-liquid_top_nav [data-testid="stRadioOption"]:has(input:checked) label,
.st-key-liquid_top_nav [data-testid="stRadioOption"]:has(input:checked) span,
.st-key-liquid_top_nav [data-testid="stRadioOption"][aria-checked="true"] p,
.st-key-liquid_top_nav [data-testid="stRadioOption"][aria-checked="true"] label,
.st-key-liquid_top_nav [data-testid="stRadioOption"][aria-checked="true"] span,
.st-key-liquid_top_nav .react-aria-RadioField[data-selected="true"] [data-testid="stRadioOption"] p,
.st-key-liquid_top_nav .react-aria-RadioField[data-selected="true"] [data-testid="stRadioOption"] span,
.st-key-liquid_top_nav .react-aria-RadioField:has(input:checked) [data-testid="stRadioOption"] p,
.st-key-liquid_top_nav .react-aria-RadioField:has(input:checked) [data-testid="stRadioOption"] span {{ color:var(--blue) !important; font-weight:700 !important; }}
.st-key-liquid_top_nav [data-testid="stRadioOption"]:focus-visible {{ outline:2px solid var(--blue) !important;outline-offset:2px !important; }}
.st-key-liquid_top_nav [data-testid="stRadioOption"]:active {{ transform:scale(.97) !important; }}
.st-key-liquid_top_nav .st-key-liquid_login button {{ min-height:36px !important;padding:0 15px !important;border:1px solid rgba(0,113,227,.24) !important;border-radius:13px !important;background:linear-gradient(135deg,#1683f5,#0066d5) !important;color:#fff !important;font-size:.78rem !important;font-weight:700 !important;white-space:nowrap !important;box-shadow:0 6px 16px rgba(0,113,227,.20),inset 0 1px 0 rgba(255,255,255,.3) !important; }}
.st-key-liquid_top_nav .st-key-liquid_login button:hover {{ transform:translateY(-1px) !important;filter:brightness(1.06) !important;box-shadow:0 9px 20px rgba(0,113,227,.27),inset 0 1px 0 rgba(255,255,255,.35) !important; }}
@media (hover:hover) and (pointer:fine) {{
    .st-key-liquid_top_nav [data-testid="stRadioOption"]:hover {{ background:var(--hover-bg) !important;transform:translateY(-1px) scale(1.015) !important;box-shadow:0 5px 12px rgba(30,30,35,.10) !important; }}
    .st-key-liquid_top_nav [data-testid="stRadioOption"]:hover p,
    .st-key-liquid_top_nav [data-testid="stRadioOption"]:hover label,
    .st-key-liquid_top_nav [data-testid="stRadioOption"]:hover span {{ color:var(--ink) !important; }}
}}

.brandline {{ display:flex;align-items:center;gap:9px;margin:0 0 26px;color:var(--muted);font-size:.82rem;font-weight:650;letter-spacing:.01em; }}
.brand-mark {{ width:22px;height:22px;border-radius:7px;display:inline-grid;place-items:center;background:url("{BRAND_LOGO_DATA_URI}") center/cover no-repeat;color:transparent;font-size:0;box-shadow:inset 0 1px 0 rgba(255,255,255,.22); }}
.brand-divider {{ width:1px;height:14px;background:var(--line); }}
.page-header {{ max-width:830px;margin-bottom:34px; }}
.eyebrow {{ color:var(--blue);font-size:.73rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase;margin-bottom:9px; }}
.page-header h1 {{ color:var(--ink);font-size:clamp(2.15rem,5vw,3.9rem);letter-spacing:-.055em;line-height:1.03;margin:0 0 13px;font-weight:720; }}
.page-header p {{ color:var(--muted);font-size:1.08rem;line-height:1.52;margin:0;max-width:760px;letter-spacing:-.012em; }}
.section-heading {{ display:flex;align-items:end;justify-content:space-between;gap:18px;margin:39px 0 14px; }}
.section-heading h2 {{ margin:0;font-size:1.34rem;letter-spacing:-.035em;line-height:1.15;font-weight:700;color:var(--ink); }}
.section-heading p {{ margin:4px 0 0;color:var(--muted);font-size:.88rem; }}

/* One-screen welcome surface: a live-feeling catalog and recommendation signal map. */
:root {{
    --orbit-rx: 205px;
    --orbit-ry: 175px;
}}
@keyframes landing-viewport-reveal {{ 0% {{ opacity:0;filter:blur(10px);transform:translateY(16px) scale(.99); }} 100% {{ opacity:1;filter:blur(0);transform:translateY(0) scale(1); }} }}
.st-key-landing_hero {{ position:relative;isolation:isolate;overflow:hidden;overflow-x:clip !important;min-height:100vh !important;min-height:100svh !important;margin:0 !important;padding:clamp(96px,12vh,138px) clamp(24px,5vw,72px) 48px !important;border:0 !important;border-top:0 !important;border-bottom:0 !important;border-radius:0 !important;background:radial-gradient(ellipse at 76% 50%,rgba(0,113,227,.14),transparent 42%),radial-gradient(ellipse at 18% 12%,rgba(111,139,255,.09),transparent 36%),linear-gradient(135deg,color-mix(in srgb,var(--surface) 92%,transparent),var(--canvas)) !important;box-shadow:none !important;backdrop-filter:none !important;-webkit-backdrop-filter:none !important;display:flex !important;flex-direction:column !important;justify-content:center !important;animation:landing-viewport-reveal 960ms cubic-bezier(.16,1,.3,1) both; }}
body:has(.landing-header-marker) .st-key-landing_hero {{ min-height:100vh !important;min-height:100svh !important;margin:0 !important;padding:clamp(96px,12vh,138px) clamp(24px,5vw,72px) 48px !important;border:0 !important;border-radius:0 !important;box-shadow:none !important;backdrop-filter:none !important;-webkit-backdrop-filter:none !important; }}
/* Keep the liquid contour in the artwork, never through the fixed brand controls. */
body:has(.landing-header-marker) .st-key-landing_hero:before {{ top:clamp(180px,25vh,240px) !important;right:-145px !important; }}
.st-key-landing_hero:before {{ content:"";position:absolute;z-index:-1;width:390px;height:390px;right:-145px;top:-170px;border:1px solid rgba(0,113,227,.12);border-radius:50%;box-shadow:0 0 0 36px rgba(0,113,227,.025),0 0 0 82px rgba(0,113,227,.018);animation:orbit-drift 24s linear infinite; }}
.st-key-landing_hero [data-testid="stHorizontalBlock"] {{ min-height:100%;align-items:center !important;gap:clamp(24px,4vw,64px) !important; }}
.landing-copy {{ max-width:580px;padding:14px 0 18px;animation:landing-reveal 850ms cubic-bezier(.16,1,.3,1) both; }}
.landing-kicker {{ display:inline-flex;align-items:center;gap:9px;padding:7px 11px;border:1px solid var(--line-soft);border-radius:999px;background:color-mix(in srgb,var(--surface) 74%,transparent);color:var(--muted);font-size:.69rem;font-weight:730;letter-spacing:.11em;text-transform:uppercase;transition:translate 260ms cubic-bezier(.2,.8,.2,1),border-color 260ms ease,box-shadow 260ms ease;animation:landing-line 620ms 120ms cubic-bezier(.2,.8,.2,1) both; }}
.landing-live-dot {{ width:7px;height:7px;border-radius:50%;background:#30d158;box-shadow:0 0 0 4px rgba(48,209,88,.14);animation:signal-pulse 2.4s ease-out infinite; }}
.landing-copy h1 {{ max-width:600px;margin:21px 0 16px;color:var(--ink);font-size:clamp(2.8rem,5.5vw,5.25rem);line-height:.99;letter-spacing:-.067em;font-weight:760;transition:translate 300ms cubic-bezier(.2,.8,.2,1),filter 300ms ease;text-wrap:balance;animation:landing-line 780ms 140ms cubic-bezier(.16,1,.3,1) both; }}
.landing-copy h1 > [data-heading-text] {{ color:var(--ink) !important; }}
.landing-copy h1 > [data-heading-text] > span {{ color:var(--blue) !important; }}
.landing-copy p {{ max-width:520px;color:var(--muted);font-size:1.02rem;line-height:1.62;transition:translate 260ms cubic-bezier(.2,.8,.2,1),color 260ms ease;animation:landing-line 780ms 220ms cubic-bezier(.16,1,.3,1) both; }}
.landing-proofline {{ display:flex;flex-wrap:wrap;gap:8px;margin-top:22px;animation:landing-line 780ms 300ms cubic-bezier(.16,1,.3,1) both; }}
.landing-proofline span {{ padding:7px 10px;border:1px solid var(--line-soft);border-radius:999px;background:color-mix(in srgb,var(--surface) 74%,transparent);color:var(--ink-soft);font-size:.72rem;font-weight:620;transition:translate 240ms cubic-bezier(.2,.8,.2,1),background 240ms ease,border-color 240ms ease,box-shadow 240ms ease; }}
.landing-stats {{ display:flex;gap:24px;margin-top:29px;animation:landing-line 780ms 380ms cubic-bezier(.16,1,.3,1) both; }}
.landing-stat {{ display:flex;flex-direction:column;gap:3px;padding:5px 7px;border-radius:12px;transition:translate 240ms cubic-bezier(.2,.8,.2,1),background 240ms ease,box-shadow 240ms ease; }}
.landing-stat strong {{ color:var(--ink);font-size:1.1rem;letter-spacing:-.04em; }}
.landing-stat span {{ color:var(--muted);font-size:.68rem; }}
.landing-visual {{ position:relative;min-height:480px;width:100%;display:grid;place-items:center;perspective:1200px;animation:landing-reveal 950ms 80ms cubic-bezier(.16,1,.3,1) both; }}
.signal-map {{ position:absolute;z-index:1;width:112%;height:105%;inset:-2% -6%;overflow:visible;opacity:.9;transition:opacity 360ms ease,filter 360ms ease; }}
.signal-map circle {{ fill:#48a6ff;filter:drop-shadow(0 0 7px rgba(41,151,255,.78)); }}
.signal-orbit {{ position:absolute;width:min(92%,440px);aspect-ratio:1;border:1px solid rgba(0,113,227,.18);border-radius:50%;transform:rotate(-14deg);box-shadow:0 0 0 35px rgba(0,113,227,.025),0 0 0 76px rgba(0,113,227,.018);transition:scale 420ms cubic-bezier(.2,.8,.2,1),filter 420ms ease;animation:orbit-drift 32s linear infinite; }}
.signal-orbit:before,.signal-orbit:after {{ content:"";position:absolute;width:10px;height:10px;border-radius:50%;background:#54a7ff;box-shadow:0 0 20px rgba(41,151,255,.8); }}
.signal-orbit:before {{ top:14%;left:18%; }}
.signal-orbit:after {{ right:8%;bottom:28%;width:7px;height:7px;background:#55d6ad; }}
.hero-signal-card {{ position:absolute;z-index:30;top:4%;right:2%;padding:12px 15px;border:1px solid var(--glass-border);border-radius:16px;background:var(--glass-bg);box-shadow:0 14px 30px rgba(10,20,40,.12),inset 0 1px 0 var(--glass-inset);backdrop-filter:blur(22px) saturate(160%);-webkit-backdrop-filter:blur(22px) saturate(160%);transition:transform 260ms cubic-bezier(.2,.8,.2,1),box-shadow 260ms ease;animation:float-card 6s ease-in-out infinite,poster-reveal 720ms 180ms cubic-bezier(.2,.8,.2,1) both; }}
.hero-signal-card span {{ display:block;color:var(--muted);font-size:.61rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase; }}
.hero-signal-card strong {{ display:block;margin-top:4px;color:var(--ink);font-size:.88rem; }}
.hero-match-badge {{ position:absolute;z-index:30;left:0;bottom:4%;padding:13px 15px;border:1px solid var(--glass-border);border-radius:17px;background:var(--glass-bg);color:var(--ink);box-shadow:0 16px 34px rgba(10,20,40,.14),inset 0 1px 0 var(--glass-inset);backdrop-filter:blur(22px) saturate(160%);-webkit-backdrop-filter:blur(22px) saturate(160%);transition:transform 260ms cubic-bezier(.2,.8,.2,1),box-shadow 260ms ease;animation:float-card 7.5s ease-in-out -3s infinite,poster-reveal 760ms 300ms cubic-bezier(.2,.8,.2,1) both; }}
.hero-match-badge span {{ display:block;color:var(--muted);font-size:.61rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase; }}
.hero-match-badge strong {{ display:block;margin-top:3px;font-size:.84rem; }}
.movie-orbit-stage {{ position:absolute;inset:0;width:100%;height:100%;pointer-events:auto;z-index:10; }}
.movie-orbit-stage:hover .hero-orbital-card,
.landing-visual:hover .hero-orbital-card {{ animation-play-state:paused !important; }}
.hero-orbital-card {{ position:absolute;top:50%;left:50%;width:120px;height:156px;border-radius:18px;overflow:hidden;padding:11px 12px;display:flex;flex-direction:column;justify-content:space-between;color:#ffffff;border:1px solid rgba(255,255,255,.42);background:linear-gradient(155deg,var(--poster-accent,#0071e3),#0b1528 88%);box-shadow:0 22px 48px rgba(6,14,30,.30),inset 0 1px 0 rgba(255,255,255,.52);cursor:pointer;user-select:none;will-change:transform,opacity;transition:box-shadow 260ms ease,border-color 260ms ease,filter 260ms ease; }}
.hero-orbital-card:before {{ content:"";position:absolute;inset:0;background:linear-gradient(150deg,rgba(255,255,255,.32) 0%,transparent 40%,rgba(2,6,18,.56) 100%);pointer-events:none; }}
.hero-orbital-card:after {{ content:"";position:absolute;width:136px;height:136px;right:-45px;top:-45px;border:1px solid rgba(255,255,255,.28);border-radius:50%;box-shadow:0 0 0 11px rgba(255,255,255,.06),0 0 0 26px rgba(255,255,255,.03);pointer-events:none; }}
.hero-orbital-card:hover {{ z-index:60 !important;filter:brightness(1.12);box-shadow:0 32px 64px rgba(0,113,227,.40),inset 0 1px 0 rgba(255,255,255,.7) !important;border-color:rgba(255,255,255,.85) !important; }}
.hero-orbital-card .poster-topline {{ position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;gap:6px; }}
.hero-orbital-card .poster-topline span {{ font-size:.54rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.90);text-shadow:0 1px 4px rgba(0,0,0,.4); }}
.hero-orbital-card .poster-monogram {{ position:absolute;inset:34% 0 auto;text-align:center;color:rgba(255,255,255,.32);font-size:2.6rem;font-weight:800;letter-spacing:-.09em;text-shadow:0 4px 18px rgba(0,0,0,.25);pointer-events:none; }}
.hero-orbital-card .poster-bottomline {{ position:relative;z-index:2; }}
.hero-orbital-card .poster-title {{ font-size:.73rem;font-weight:750;line-height:1.15;letter-spacing:-.025em;color:#ffffff;text-shadow:0 1px 8px rgba(0,0,0,.6);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden; }}
.hero-orbital-card .poster-genre {{ margin-top:3px;font-size:.53rem;font-weight:600;color:rgba(255,255,255,.80);letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }}
.st-key-hero_open_overview div.stButton > button {{ background:color-mix(in srgb,var(--surface) 76%,transparent) !important;color:var(--ink) !important;border:1px solid var(--line-soft) !important;box-shadow:inset 0 1px 0 var(--glass-inset) !important; }}
.st-key-hero_open_overview div.stButton > button:hover {{ background:var(--surface-raised) !important;transform:translateY(-1px) !important; }}
.login-intro {{ color:var(--muted);font-size:.88rem;line-height:1.55;margin:0 0 14px; }}
.login-footnote {{ padding:11px 13px;border:1px solid var(--line-soft);border-radius:13px;background:color-mix(in srgb,var(--surface) 84%,transparent);color:var(--muted);font-size:.73rem;line-height:1.45; }}
.st-key-streamglass_login_submit button {{ min-height:46px !important;border-radius:14px !important;background:linear-gradient(135deg,#1683f5,#0066d5) !important;color:#fff !important;font-weight:720 !important;box-shadow:0 9px 22px rgba(0,113,227,.22) !important; }}
[data-testid="stDialog"] {{ background:rgba(5,9,19,.46) !important;backdrop-filter:blur(28px) saturate(145%) !important;-webkit-backdrop-filter:blur(28px) saturate(145%) !important; }}
[data-testid="stDialog"] section[role="dialog"] {{ width:min(540px,calc(100vw - 32px)) !important;padding:27px 28px 24px !important;border:1px solid var(--glass-border) !important;border-radius:28px !important;background:var(--glass-bg) !important;color:var(--ink) !important;box-shadow:0 28px 90px rgba(4,10,24,.34),inset 0 1px 0 var(--glass-inset) !important;backdrop-filter:blur(34px) saturate(165%) !important;-webkit-backdrop-filter:blur(34px) saturate(165%) !important; }}
[data-testid="stDialog"] section[role="dialog"] h2 {{ margin:0 0 8px !important;color:var(--ink) !important;font-size:1.55rem !important;letter-spacing:-.045em !important;font-weight:740 !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stForm"] {{ border:0 !important;background:transparent !important;padding:0 !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stTextInput"] input {{ min-height:44px !important;border:1px solid var(--line) !important;border-radius:13px !important;background:var(--input-bg) !important;color:var(--ink) !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.07) !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stTextInputRootElement"] {{ border:1px solid var(--line) !important;border-radius:13px !important;background:var(--input-bg) !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stTextInput"] input::placeholder {{ color:var(--muted) !important;opacity:.85 !important; }}
[data-testid="stDialog"] section[role="dialog"] button[aria-label="Show password"] {{ color:var(--ink-soft) !important;background:transparent !important;border:0 !important;box-shadow:none !important; }}
[data-testid="stDialog"] section[role="dialog"] input[type="checkbox"] {{ accent-color:var(--blue) !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stTextInput"] label {{ color:var(--ink-soft) !important;font-size:.78rem !important;font-weight:650 !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stCheckbox"] label {{ color:var(--ink-soft) !important;font-size:.75rem !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stAlert"] {{ border:1px solid rgba(255,159,10,.34) !important;border-radius:13px !important;background:rgba(255,159,10,.14) !important;color:var(--ink) !important; }}
[data-testid="stDialog"] section[role="dialog"] [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stDialog"] section[role="dialog"] [data-testid="stAlert"] p {{ color:var(--ink) !important; }}
[data-testid="stDialog"] section[role="dialog"] button[aria-label="Close"] {{ color:var(--muted) !important; }}
@keyframes float-card {{ 0%,100% {{ translate:0 0; }} 50% {{ translate:0 -11px; }} }}
@keyframes landing-reveal {{ from {{ opacity:0;filter:blur(9px);translate:0 13px; }} to {{ opacity:1;filter:blur(0);translate:0 0; }} }}
@keyframes landing-line {{ from {{ opacity:0;filter:blur(7px);translate:0 18px; }} to {{ opacity:1;filter:blur(0);translate:0 0; }} }}
@keyframes poster-reveal {{ from {{ opacity:0;filter:blur(12px);scale:.88; }} to {{ opacity:1;filter:blur(0);scale:1; }} }}
@keyframes catalog-run {{ 0% {{ opacity:0;transform:translateY(-112px) rotate(-3deg); }} 3% {{ opacity:1;transform:translateY(-20px) rotate(-1deg); }} 6% {{ opacity:1;transform:translateY(0) rotate(1deg); }} 10% {{ opacity:1;transform:translateY(3px) rotate(-1deg); }} 12.5% {{ opacity:0;transform:translateY(168px) rotate(4deg); }} 14.286%,100% {{ opacity:0;transform:translateY(168px) rotate(4deg); }} }}
@keyframes orbit-drift {{ to {{ rotate:346deg; }} }}
@keyframes signal-pulse {{ 0% {{ box-shadow:0 0 0 0 rgba(48,209,88,.32); }} 75%,100% {{ box-shadow:0 0 0 7px rgba(48,209,88,0); }} }}
@media (hover:hover) and (pointer:fine) {{
    .landing-kicker:hover {{ translate:0 -3px;border-color:color-mix(in srgb,var(--blue) 45%,var(--line-soft));box-shadow:0 9px 20px rgba(0,113,227,.11); }}
    .landing-copy h1:hover {{ translate:0 -4px;filter:drop-shadow(0 13px 22px rgba(0,113,227,.16)); }}
    .landing-copy p:hover {{ translate:0 -2px;color:var(--ink-soft); }}
    .landing-proofline span:hover {{ translate:0 -4px;background:var(--blue-wash);border-color:color-mix(in srgb,var(--blue) 42%,var(--line-soft));box-shadow:0 8px 16px rgba(0,113,227,.10); }}
    .landing-stat:hover {{ translate:0 -4px;background:color-mix(in srgb,var(--surface) 86%,transparent);box-shadow:0 10px 19px rgba(10,20,40,.08); }}
    .landing-visual:hover .signal-map {{ opacity:1;filter:drop-shadow(0 0 12px rgba(41,151,255,.26)); }}
    .landing-visual:hover .signal-orbit {{ scale:1.035;filter:brightness(1.14); }}
    .hero-signal-card:hover,.hero-match-badge:hover {{ transform:translateY(-6px) scale(1.025);box-shadow:0 22px 40px rgba(10,20,40,.20),inset 0 1px 0 var(--glass-inset); }}
}}

/* Content surfaces are quiet paper-like panels, not glass. */
.surface,.data-surface,.title-card,.metric-card,.proof-card,.profile-card {{ background:var(--surface);border:1px solid var(--line-soft);border-radius:var(--radius); }}
.surface {{ padding:21px 22px; }}
.surface h3 {{ font-size:1.02rem;letter-spacing:-.022em;margin:0 0 11px;color:var(--ink); }}
.surface p,.surface li {{ color:var(--ink-soft);font-size:.9rem;line-height:1.58; }}
.surface ul {{ padding-left:18px;margin:10px 0 0; }}
.quote {{ border-left:3px solid var(--blue);padding:4px 0 4px 14px;margin:13px 0;color:var(--ink-soft);font-size:.95rem;font-style:normal;line-height:1.48; }}
.people-list {{ display:grid;gap:1px; }}
.person-row {{ display:flex;align-items:center;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--line-soft);font-size:.84rem; }}
.person-row:last-child {{ border-bottom:0;padding-bottom:0; }}
.person-row span {{ font-weight:650;color:var(--ink-soft); }}
.person-row code {{ color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.74rem; }}
.pipeline-step {{ min-height:168px;padding:20px;border-top:3px solid var(--step-color,var(--blue));background:var(--pipeline-bg);border-radius:16px;border-left:1px solid var(--line-soft);border-right:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft); }}
.pipeline-step .step-label {{ color:var(--muted);font-size:.71rem;letter-spacing:.06em;text-transform:uppercase;font-weight:740; }}
.pipeline-step h3 {{ font-size:1rem;letter-spacing:-.025em;margin:10px 0 8px;color:var(--ink); }}
.pipeline-step p {{ color:var(--muted);font-size:.84rem;line-height:1.5;margin:0; }}
.metric-card {{ padding:17px 18px;min-height:102px; }}
.metric-label {{ color:var(--muted);font-size:.76rem;font-weight:650;letter-spacing:.01em; }}
.metric-value {{ color:var(--ink);font-size:1.75rem;font-weight:720;letter-spacing:-.055em;margin-top:7px;line-height:1; }}
.metric-note {{ color:var(--faint);font-size:.73rem;margin-top:8px; }}
.data-surface {{ padding:10px 13px 14px; }}
.status-line {{ display:flex;align-items:center;gap:7px;color:var(--muted);font-size:.82rem;margin:8px 0 18px; }}
.status-dot {{ width:7px;height:7px;border-radius:999px;background:var(--green);box-shadow:0 0 0 3px rgba(36,138,61,.12); }}
.profile-card {{ padding:19px 21px;margin:4px 0 18px;display:flex;align-items:center;justify-content:space-between;gap:18px; }}
.profile-title {{ font-size:1.1rem;font-weight:720;letter-spacing:-.025em;color:var(--ink); }}
.profile-copy {{ color:var(--muted);margin-top:4px;font-size:.86rem; }}
.chip-row {{ display:flex;flex-wrap:wrap;gap:6px; }}
.chip {{ background:var(--chip-bg);border:1px solid var(--chip-border);color:var(--chip-color);border-radius:999px;padding:5px 9px;font-size:.72rem;font-weight:620;white-space:nowrap; }}
.chip-blue {{ background:var(--blue-wash);border-color:rgba(0,113,227,.16);color:var(--blue); }}
.feed-head {{ display:flex;align-items:center;justify-content:space-between;gap:12px;margin:5px 0 9px; }}
.feed-head h2 {{ display:inline-flex;align-items:center;min-height:36px;padding:0 13px;border:1px solid var(--line-soft);border-radius:12px;font-size:1.12rem;letter-spacing:-.03em;margin:0;color:var(--ink);background:var(--surface);box-shadow:inset 0 1px 0 var(--glass-inset); }}
.feed-head span {{ padding:5px 8px;border-radius:999px;font-size:.65rem;font-weight:760;letter-spacing:.055em;color:var(--muted);background:var(--hover-bg); }}
.feed-head-popular h2 {{ border-color:rgba(255,149,0,.52) !important;background:linear-gradient(135deg,rgba(255,149,0,.22),rgba(255,149,0,.08)) !important;color:var(--ink) !important;font-size:1.24rem !important;font-weight:780 !important;letter-spacing:-.035em !important;box-shadow:0 4px 18px rgba(255,149,0,.20),inset 0 1px 0 rgba(255,255,255,.45) !important;border-radius:14px !important;padding:6px 16px !important; }}
.feed-head-popular span {{ color:#ff9500 !important;background:rgba(255,149,0,.15) !important;border:1px solid rgba(255,149,0,.3) !important; }}
.feed-head-personal h2 {{ border-color:rgba(0,113,227,.52) !important;background:linear-gradient(135deg,rgba(0,113,227,.22),rgba(0,113,227,.08)) !important;color:var(--blue) !important;font-size:1.24rem !important;font-weight:780 !important;letter-spacing:-.035em !important;box-shadow:0 4px 18px rgba(0,113,227,.24),inset 0 1px 0 rgba(255,255,255,.45) !important;border-radius:14px !important;padding:6px 16px !important; }}
.feed-head-personal span {{ color:var(--blue) !important;background:rgba(0,113,227,.15) !important;border:1px solid rgba(0,113,227,.3) !important; }}
.feed-copy {{ margin:0 0 15px;color:var(--muted);font-size:.83rem;line-height:1.45; }}
.title-card {{ overflow:hidden;margin:0 0 11px;transition:transform 180ms ease,border-color 180ms ease,box-shadow 180ms ease; }}
.title-card:hover {{ transform:translateY(-2px);border-color:var(--card-border-hover);box-shadow:var(--card-shadow-hover); }}
.title-top {{ display:flex;min-height:104px; }}
.poster-swatch {{ width:92px;flex:none;padding:12px;display:flex;flex-direction:column;justify-content:space-between;color:#fff;position:relative;overflow:hidden; }}
.poster-swatch:after {{ content:"";position:absolute;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.16);right:-54px;top:-42px; }}
.poster-id,.poster-year {{ position:relative;z-index:1;font-size:.69rem;font-weight:750;letter-spacing:.04em; }}
.poster-year {{ opacity:.8;font-weight:600; }}
.title-detail {{ padding:13px 14px;min-width:0;flex:1; }}
.title-meta {{ display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:.73rem; }}
.title-name {{ margin:5px 0 4px;color:var(--ink);font-size:1rem;line-height:1.18;letter-spacing:-.023em;font-weight:700; }}
.title-detail p {{ color:var(--muted);margin:0;font-size:.76rem;line-height:1.36; }}
.card-foot {{ border-top:1px solid var(--line-soft);padding:10px 13px;color:var(--muted);font-size:.74rem;line-height:1.35; }}
.match {{ color:var(--blue);font-weight:720; }}
.mismatch {{ color:var(--red);font-weight:700; }}
.rating {{ color:var(--orange);font-weight:720; }}
.proof-card {{ padding:18px;min-height:205px; }}
.proof-kicker {{ color:var(--green);font-size:.7rem;font-weight:760;letter-spacing:.07em; }}
.proof-card h3 {{ font-size:1.03rem;margin:8px 0 6px;letter-spacing:-.02em;color:var(--ink); }}
.proof-card code {{ display:block;color:var(--muted);font-size:.75rem;white-space:normal; }}
.proof-card p {{ color:var(--muted);font-size:.8rem;line-height:1.46;margin:11px 0 0; }}
.formula-surface {{ background:var(--formula-bg);border:1px solid var(--line-soft);border-radius:15px;padding:16px;overflow-x:auto; }}

[data-testid="stSelectbox"] > div > div,[data-baseweb="select"] > div,[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input {{ background:var(--input-bg) !important;border-color:var(--line) !important;border-radius:12px !important;color:var(--ink) !important;box-shadow:none !important; }}
[data-testid="stSelectbox"] label,[data-testid="stSlider"] label,[data-testid="stRadio"] label,[data-testid="stExpander"] label {{ color:var(--ink-soft) !important;font-size:.83rem !important;font-weight:650 !important; }}
div.stButton > button {{ background:var(--blue) !important;color:#fff !important;border:0 !important;border-radius:12px !important;font-weight:680 !important;min-height:42px !important;transition:transform 160ms ease,background 160ms ease !important; }}
div.stButton > button:hover {{ background:var(--blue) !important;filter:brightness(1.08);transform:translateY(-1px) !important;box-shadow:0 5px 14px rgba(0,113,227,.22) !important; }}
 /* Native content tabs: restrained, touch-friendly, and left fully operable. */
 [data-testid="stTabs"] [role="tablist"] {{ display:flex !important; align-items:center !important; gap:4px !important; min-height:44px !important; padding:4px !important; overflow-x:auto !important; scrollbar-width:none !important; border:1px solid var(--line-soft) !important; border-radius:14px !important; background:color-mix(in srgb,var(--surface) 82%,transparent) !important; }}
 [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {{ display:none !important; }}
[data-testid="stTabs"] [role="tab"] {{ flex:0 0 auto !important; min-height:34px !important; padding:8px 13px !important; border:0 !important; border-radius:10px !important; color:var(--muted) !important; font-size:.8rem !important; font-weight:650 !important; line-height:1.15 !important; white-space:nowrap !important; background:transparent !important; transform:none !important; transition:background 180ms ease,color 180ms ease,box-shadow 180ms ease,transform 180ms ease !important; }}
 [data-testid="stTabs"] [role="tab"]:focus-visible {{ outline:2px solid var(--blue) !important;outline-offset:2px !important; }}
 [data-testid="stTabs"] [role="tab"]:active {{ transform:scale(.98) !important; }}
 [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{ background:var(--pill-active-bg) !important; color:var(--blue) !important; box-shadow:var(--pill-active-shadow) !important; }}
@media (hover:hover) and (pointer:fine) {{
    [data-testid="stTabs"] [role="tab"]:hover {{ background:var(--hover-bg) !important;color:var(--ink) !important;transform:translateY(-1px) !important;box-shadow:0 4px 10px rgba(30,30,35,.08) !important; }}
}}
 [data-testid="stTabs"] [role="tab"] .react-aria-SelectionIndicator {{ display:none !important; }}
.katex,.katex * {{ color:var(--ink) !important; }}
[data-testid="stDataFrame"],[data-testid="stPlotlyChart"] {{ border:1px solid var(--line-soft);border-radius:15px;overflow:hidden;background:var(--surface) !important; }}
[data-testid="stAlert"] {{ border-radius:14px !important;border:1px solid var(--line-soft) !important;background:var(--surface) !important;color:var(--ink-soft) !important; }}
[data-testid="stExpander"] {{ background:var(--surface) !important;border:1px solid var(--line-soft);border-radius:16px;overflow:hidden; }}
[data-testid="stMetric"] {{ background:var(--surface) !important;border:1px solid var(--line-soft);border-radius:16px;padding:15px; }}
[data-testid="stMetricLabel"] {{ color:var(--muted) !important; }}
[data-testid="stMetricValue"] {{ color:var(--ink) !important;letter-spacing:-.04em; }}
code {{ color:var(--ink) !important; }}
::-webkit-scrollbar {{ width:10px;height:10px; }}
::-webkit-scrollbar-thumb {{ background:var(--line);border:3px solid var(--canvas);border-radius:999px; }}
.streamglass-footer {{ margin-top:18px;border-top:1px solid rgba(60,60,67,.12);padding:18px 0 0;color:#86868b;font-size:.76rem;text-align:center; }}
body:has(.landing-header-marker) .streamglass-footer {{ position:fixed;z-index:4;left:0;right:0;bottom:18px;margin:0;padding:0 20px;border:0;color:var(--faint);font-size:.68rem;letter-spacing:.015em;pointer-events:none; }}
@media (min-width:761px) {{
    body:has(.landing-header-marker),body:has(.landing-header-marker) [data-testid="stAppViewContainer"] {{ overflow:hidden !important; }}
}}

@media (max-width:960px) {{
    .block-container {{ padding:8.9rem 16px 2.4rem !important; }}
    .st-key-landing_hero {{ padding:clamp(20px,3vw,32px); }}
    .st-key-liquid_top_nav {{ top:8px !important;width:calc(100vw - 16px) !important;padding:6px !important; }}
    .st-key-liquid_top_nav [data-testid="stHorizontalBlock"] {{ display:grid !important;grid-template-columns:minmax(0,1fr) auto !important;grid-template-areas:"brand login" "navigation navigation" "theme theme" !important;gap:5px 9px !important; }}
    .st-key-liquid_top_nav [data-testid="stColumn"] {{ width:auto !important;min-width:0 !important;flex:initial !important; }}
    .st-key-liquid_top_nav [data-testid="stColumn"]:nth-child(1) {{ grid-area:brand; }}
    .st-key-liquid_top_nav [data-testid="stColumn"]:nth-child(2) {{ grid-area:navigation; }}
    .st-key-liquid_top_nav [data-testid="stColumn"]:nth-child(3) {{ grid-area:theme;border-left:0 !important;border-top:1px solid var(--line-soft) !important;padding:5px 0 0 !important; }}
    .st-key-liquid_top_nav [data-testid="stColumn"]:nth-child(4) {{ grid-area:login;justify-self:end; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stHorizontalBlock"] {{ display:flex !important;flex-wrap:nowrap !important;justify-content:space-between !important; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stColumn"]:first-child {{ width:auto !important;flex:1 1 auto !important; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) [data-testid="stColumn"]:last-child {{ width:auto !important;flex:0 0 auto !important; }}
    body:has(.landing-header-marker) .block-container {{ padding:0 !important; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) {{ top:0 !important;width:100% !important;padding:16px 20px !important; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_brand button {{ top:16px !important;left:20px !important; }}
    .st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_login button {{ top:16px !important;right:20px !important; }}
    body:has(.landing-header-marker) .st-key-landing_hero {{ min-height:100svh;margin:0 !important;padding:96px 20px 58px !important;border:0 !important;border-radius:0 !important; }}
    .st-key-liquid_top_nav .nav-brand {{ font-size:.83rem; }}
    .st-key-liquid_top_nav [data-testid="stRadioGroup"] {{ overflow-x:auto !important;justify-content:flex-start !important; }}
    .st-key-liquid_top_nav [data-testid="stRadioGroup"] > div,
    .st-key-liquid_top_nav .react-aria-RadioField {{ flex:0 0 auto !important;min-width:0 !important; }}
    .st-key-liquid_top_nav [data-testid="stRadioOption"] {{ flex:0 0 auto !important;min-width:0 !important;min-height:34px !important;font-size:.72rem !important;padding:0 10px !important; }}
    .st-key-liquid_top_nav [aria-label="Theme selection"] {{ justify-content:center !important; }}
    .landing-copy {{ padding:0 0 18px; }}
    .landing-copy h1 {{ max-width:460px;font-size:clamp(2.45rem,5.4vw,2.9rem);margin:15px 0 10px; }}
    .landing-copy p {{ font-size:.91rem;line-height:1.5; }}
    .landing-proofline {{ gap:6px;margin-top:12px; }}
    .landing-proofline span {{ padding:6px 8px;font-size:.66rem; }}
    .landing-stats {{ gap:17px;margin-top:15px; }}
    :root {{
        --orbit-rx: 155px;
        --orbit-ry: 135px;
    }}
    .st-key-landing_top_nav,
    .st-key-liquid_top_nav:has(.landing-header-marker) {{ padding:16px 20px !important; }}
    .st-key-landing_top_nav .st-key-liquid_brand button,
    .st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_brand button {{ top:16px !important;left:20px !important; }}
    .st-key-landing_top_nav .st-key-liquid_login button,
    .st-key-liquid_top_nav:has(.landing-header-marker) .st-key-liquid_login button {{ top:16px !important;right:20px !important; }}
    .landing-visual {{ min-height:380px; }}
    .hero-orbital-card {{ width:100px;height:132px;padding:9px 10px;border-radius:15px; }}
    .hero-orbital-card .poster-title {{ font-size:.66rem; }}
    .hero-orbital-card .poster-genre {{ font-size:.48rem; }}
    .hero-orbital-card .poster-monogram {{ font-size:2.1rem; }}
}}
@media (max-width:760px) {{
    :root {{
        --orbit-rx: 128px;
        --orbit-ry: 112px;
    }}
    .st-key-landing_hero {{ min-height:100svh;margin:0 !important;padding:90px 20px 58px !important;border:0 !important;border-radius:0 !important; }}
    .landing-copy {{ padding:8px 0 0; }}
    .landing-copy h1 {{ font-size:clamp(2.45rem,9vw,3.1rem);margin:15px 0 10px; }}
    .landing-copy p {{ font-size:.93rem; }}
    .landing-proofline {{ margin-top:12px; }}
    .landing-stats {{ margin-top:15px; }}
    .landing-visual {{ min-height:340px;margin-top:12px; }}
    .hero-orbital-card {{ width:88px;height:118px;padding:8px 9px;border-radius:13px; }}
    .hero-orbital-card .poster-title {{ font-size:.60rem; }}
    .hero-orbital-card .poster-genre {{ font-size:.45rem; }}
    .hero-orbital-card .poster-monogram {{ font-size:1.8rem; }}
    .hero-signal-card {{ top:0;right:0; }}
    .hero-match-badge {{ bottom:0; }}
    body:has(.landing-header-marker) .st-key-landing_hero {{ min-height:100svh;margin:0 !important;padding:90px 20px 58px !important;border:0 !important;border-radius:0 !important; }}
    .page-header {{ margin-bottom:26px; }}
    .page-header h1 {{ font-size:2.35rem; }}
    .page-header p {{ font-size:1rem; }}
    .section-heading {{ margin-top:30px; }}
    .profile-card {{ display:block; }}
    .profile-card .chip-row {{ margin-top:13px; }}
    .poster-swatch {{ width:76px; }}
    [data-testid="stTabs"] [role="tablist"] {{ overflow-x:auto; }}
}}
@media (prefers-reduced-motion:reduce) {{
    .st-key-landing_hero:before,.signal-orbit,.hero-poster,.hero-signal-card,.hero-match-badge,.landing-live-dot,.landing-copy,.landing-visual,.hero-orbital-card {{ animation:none !important; }}
    .hero-poster,.title-card,.nav-tab,.hero-orbital-card {{ transition:none !important; }}
}}
</style>
"""

st.markdown(get_apple_ui_css(st.session_state.app_theme), unsafe_allow_html=True)

@st.cache_resource
def get_system_engine():
    database.seed_database()
    return recommender.HybridScoringEngine()

engine = get_system_engine()
NAV_ITEMS = [("Overview","overview"),("Coursework","coursework"),("Data","data"),("Model Lab","model"),("Studio","studio"),("Analytics","analytics")]
NAV_LOOKUP = dict(NAV_ITEMS)
NAV_LABELS = [label for label, _ in NAV_ITEMS]
THEME_MODES = ["Light", "Dark", "System"]

if st.session_state.get("current_module") == "home":
    st.session_state.current_module = "landing"
if st.session_state.get("current_module") not in {*NAV_LOOKUP.values(), "landing"}:
    st.session_state.current_module = "landing"
if not st.session_state.get("streamglass_home_entry_initialized"):
    st.session_state.current_module = "landing"
    st.session_state.streamglass_home_entry_initialized = True
if "selected_user_id" not in st.session_state:
    st.session_state.selected_user_id = "U101"
if "k_neighbors" not in st.session_state:
    st.session_state.k_neighbors = 5
if "alpha_weight" not in st.session_state:
    st.session_state.alpha_weight = .60
if "login_dialog_open" not in st.session_state:
    st.session_state.login_dialog_open = False
if "logged_in_user_id" not in st.session_state:
    st.session_state.logged_in_user_id = None
if "signed_in_identifier" not in st.session_state:
    st.session_state.signed_in_identifier = None
engine.set_hyperparameters(st.session_state.k_neighbors, st.session_state.alpha_weight)

is_landing = st.session_state.current_module == "landing"
if is_landing:
    st.session_state.streamglass_main_nav = None
current_label = next((label for label, key in NAV_ITEMS if key == st.session_state.current_module), None)
current_idx = NAV_LABELS.index(current_label) if current_label in NAV_LABELS else None
current_theme_idx = THEME_MODES.index(st.session_state.app_theme) if st.session_state.app_theme in THEME_MODES else 2

def on_navigation_change():
    selected = st.session_state.streamglass_main_nav
    if selected in NAV_LOOKUP:
        st.session_state.current_module = NAV_LOOKUP[selected]

def on_theme_change():
    selected = st.session_state.streamglass_theme_nav
    if selected in THEME_MODES:
        st.session_state.app_theme = selected

def open_studio():
    st.session_state.current_module = "studio"
    st.session_state.streamglass_main_nav = "Studio"

def open_overview():
    st.session_state.current_module = "overview"
    st.session_state.streamglass_main_nav = "Overview"

def open_landing():
    st.session_state.current_module = "landing"
    st.session_state.streamglass_main_nav = None

def open_login_dialog():
    st.session_state.login_dialog_open = True

def close_login_dialog():
    st.session_state.login_dialog_open = False

@st.dialog("Sign in to StreamGlass", width="small", on_dismiss=close_login_dialog)
def show_login_dialog():
    st.markdown(
        '<p class="login-intro">Your viewing signals stay yours. Sign in to continue to a more personal discovery experience.</p>',
        unsafe_allow_html=True,
    )
    with st.form("streamglass_login_form"):
        email = st.text_input("Email or subscriber ID", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        keep_signed_in, help_text = st.columns([.56, .44])
        with keep_signed_in:
            st.checkbox("Keep me signed in")
        with help_text:
            st.markdown('<div style="text-align:right;padding-top:8px;color:var(--muted);font-size:.74rem">Demo access</div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("Sign in", key="streamglass_login_submit", use_container_width=True)
    if submitted:
        if not email.strip() or not password:
            st.warning("Enter your email or subscriber ID and password to continue.")
        else:
            try:
                st.session_state.logged_in_user_id = database.get_or_create_demo_subscriber(email)
            except Exception:
                st.session_state.logged_in_user_id = _get_or_create_demo_subscriber(email)
            st.session_state.signed_in_identifier = email.strip()
            st.session_state.selected_user_id = st.session_state.logged_in_user_id
            st.session_state.current_module = "studio"
            st.session_state.streamglass_main_nav = "Studio"
            st.session_state.login_dialog_open = False
            st.rerun()
    st.markdown(
        '<div class="login-footnote">StreamGlass demo · Any non-empty demo details open the live workspace; they are not verified or saved.</div>',
        unsafe_allow_html=True,
    )

if is_landing:
    with st.container(key="landing_top_nav"):
        landing_brand_col, landing_login_col = st.columns([.86, .14], gap="small")
        with landing_brand_col:
            st.markdown('<span class="landing-header-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
            st.button("StreamGlass", key="liquid_brand", on_click=open_landing)
        with landing_login_col:
            st.button("Sign in", key="liquid_login", on_click=open_login_dialog)
else:
    with st.container(key="liquid_top_nav"):
        brand_col, nav_col, theme_col, login_col = st.columns([.17, .55, .17, .11], gap="small")
        with brand_col:
            st.button("StreamGlass", key="liquid_brand", on_click=open_landing)
        with nav_col:
            nav_selected = st.radio(
                "Primary navigation",
                options=NAV_LABELS,
                index=current_idx,
                key="streamglass_main_nav",
                horizontal=True,
                label_visibility="collapsed",
                on_change=on_navigation_change,
            )
        with theme_col:
            theme_selected = st.radio(
                "Theme selection",
                options=THEME_MODES,
                index=current_theme_idx,
                key="streamglass_theme_nav",
                horizontal=True,
                label_visibility="collapsed",
                on_change=on_theme_change,
            )
        with login_col:
            st.button("Sign in", key="liquid_login", on_click=open_login_dialog, use_container_width=True)

def esc(value): return html.escape(str(value))
def brandline(section): st.markdown(f'<div class="brandline"><span class="brand-mark">SG</span><span>StreamGlass</span><span class="brand-divider"></span><span>{esc(section)}</span></div>',unsafe_allow_html=True)
def page_header(eyebrow,title,description): st.markdown(f'<section class="page-header"><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(title)}</h1><p>{esc(description)}</p></section>',unsafe_allow_html=True)
def section_heading(title,description=""):
    copy=f"<p>{esc(description)}</p>" if description else ""
    st.markdown(f'<div class="section-heading"><div><h2>{esc(title)}</h2>{copy}</div></div>',unsafe_allow_html=True)
def metric_card(label,value,note): st.markdown(f'<div class="metric-card"><div class="metric-label">{esc(label)}</div><div class="metric-value">{esc(value)}</div><div class="metric-note">{esc(note)}</div></div>',unsafe_allow_html=True)
def apply_chart_theme(fig,height=None):
    is_dark = (st.session_state.get("app_theme") == "Dark")
    text_color = "#d2d2d7" if is_dark else "#424245"
    grid_color = "rgba(255,255,255,.10)" if is_dark else "rgba(60,60,67,.10)"
    line_color = "rgba(255,255,255,.14)" if is_dark else "rgba(60,60,67,.13)"
    hover_bg = "#1c1c1e" if is_dark else "#ffffff"
    hover_border = "#3a3a3c" if is_dark else "#d2d2d7"
    hover_font = "#f5f5f7" if is_dark else "#1d1d1f"
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",color=text_color,size=12),margin=dict(t=24,r=18,b=26,l=18),hoverlabel=dict(bgcolor=hover_bg,bordercolor=hover_border,font=dict(color=hover_font)))
    if height: fig.update_layout(height=height)
    fig.update_xaxes(gridcolor=grid_color,zeroline=False,linecolor=line_color)
    fig.update_yaxes(gridcolor=grid_color,zeroline=False,linecolor=line_color)
    return fig
def title_card(item,personalized=False,primary_language=None,secondary_language=None):
    accent,title,language,genre,secondary=esc(item.get("accent_color","#5f789c")),esc(item["title"]),esc(item["language"]),esc(item["primary_genre"]),esc(item.get("secondary_genre") or "")
    rating=float(item.get("avg_rating",0))
    if personalized:
        status=f'<span class="match">{int(item["confidence_pct"])}% match</span><span class="rating">{rating:.1f} / 5</span>'; reason=esc(item["why_recommended"])
    else:
        status='<span class="match">Language fit</span>' if item["language"] in {primary_language,secondary_language} else '<span class="mismatch">Language mismatch</span>'; reason=esc(item["why_recommended"])
    st.markdown(f'''<article class="title-card"><div class="title-top"><div class="poster-swatch" style="background:{accent}"><span class="poster-id">{esc(item["movie_id"])}</span><span class="poster-year">{esc(item["release_year"])}</span></div><div class="title-detail"><div class="title-meta"><span>{language} · {genre}</span>{status}</div><div class="title-name">{title}</div><p>{secondary} · {esc(item["duration_min"])} min</p></div></div><div class="card-foot">{reason}</div></article>''',unsafe_allow_html=True)
def profile_surface(subscriber,history_size):
    tags="".join(f'<span class="chip">{esc(genre)}</span>' for genre in subscriber.preferred_genres)
    st.markdown(f'''<section class="profile-card"><div><div class="profile-title">{esc(subscriber.name)} <span style="color:#86868b;font-weight:500;font-size:.83rem">· {esc(subscriber.user_id)} · {subscriber.age}</span></div><div class="profile-copy">{esc(subscriber.persona_desc)}</div></div><div class="chip-row"><span class="chip chip-blue">{esc(subscriber.primary_language)}</span><span class="chip">{esc(subscriber.secondary_language or "No secondary language")}</span>{tags}<span class="chip">{history_size} watched</span></div></section>''',unsafe_allow_html=True)

if st.session_state.current_module == "landing":
    hero_metrics = database.get_db_metrics()
    hero_titles = database.get_all_movies().to_dict(orient="records")
    num_movies = len(hero_titles)
    total_orbit_duration = 52.0  # seconds for full cinematic 360-degree orbital revolution

    # Build continuous orbital keyframes across all movies
    steps = 40
    keyframe_stops = []
    for k in range(steps + 1):
        pct = round((k / steps) * 100, 2)
        u = k / steps
        theta = -math.pi / 3 + u * 2 * math.pi
        cos_val = round(math.cos(theta), 4)
        sin_val = round(math.sin(theta), 4)

        if u <= 0.16:
            prog = u / 0.16
            opacity = round(0.0 + 0.88 * prog, 3)
            scale = round(0.76 + 0.22 * prog, 3)
            z_idx = int(8 + 10 * prog)
            pt = "auto" if opacity > 0.3 else "none"
        elif u <= 0.62:
            prog = (u - 0.16) / 0.46
            peak = math.sin(prog * math.pi)
            opacity = round(0.88 + 0.12 * peak, 3)
            scale = round(0.96 + 0.12 * peak, 3)
            z_idx = int(18 + 7 * peak)
            pt = "auto"
        elif u <= 0.80:
            prog = (u - 0.62) / 0.18
            opacity = round(0.88 * (1.0 - prog), 3)
            scale = round(0.96 - 0.22 * prog, 3)
            z_idx = int(14 * (1.0 - prog))
            pt = "auto" if opacity > 0.3 else "none"
        else:
            opacity = 0.0
            scale = 0.72
            z_idx = 1
            pt = "none"

        tilt = round(-12.0 * math.cos(theta), 1)
        keyframe_stops.append(
            f"        {pct}% {{{{ transform: translate(calc(var(--orbit-rx, 205px) * {cos_val} - 50%), calc(var(--orbit-ry, 175px) * {sin_val} - 50%)) scale({scale}) rotate({tilt}deg); opacity: {opacity}; z-index: {z_idx}; pointer-events: {pt}; }}}}"
        )
    keyframe_css = "\n".join(keyframe_stops)

    orbit_styles = f'''<style>
    @keyframes movie-orbit-flow {{
{keyframe_css}
    }}
    .hero-orbital-card {{
        animation: movie-orbit-flow {total_orbit_duration:.1f}s linear infinite both;
    }}
    </style>'''

    orbital_cards = []
    for index, item in enumerate(hero_titles):
        accent = str(item.get("accent_color", "#5f789c"))
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            accent = "#5f789c"
        title = esc(item.get("title", "StreamGlass original"))
        language = esc(item.get("language", "Regional"))
        genre = esc(item.get("primary_genre", "Discovery"))
        year = esc(item.get("release_year", "2024"))
        monogram = esc("".join(token[0] for token in re.findall(r"[A-Za-z0-9]+", str(item.get("title", "SG")))[:2]).upper())
        delay = -round(total_orbit_duration * (index / num_movies), 2)
        orbital_cards.append(
            f'<article class="hero-orbital-card" style="--poster-accent:{accent}; animation-delay:{delay}s;" title="{title} ({year}) · {language} · {genre}">'
            f'<div class="poster-topline"><span>{language}</span><span>SG · {index + 1:02d}</span></div>'
            f'<div class="poster-monogram">{monogram}</div>'
            f'<div class="poster-bottomline">'
            f'<div class="poster-title">{title}</div>'
            f'<div class="poster-genre">{genre} · {year}</div>'
            f'</div>'
            f'</article>'
        )
    orbital_cards_html = "".join(orbital_cards)

    with st.container(key="landing_hero"):
        copy_col, visual_col = st.columns([1.04, .96], gap="large")
        with copy_col:
            st.markdown(
                f'''<div class="landing-copy">
                    <div class="landing-kicker"><span class="landing-live-dot"></span>Personalized OTT intelligence</div>
                    <h1>Find the next story <span>that feels like yours.</span></h1>
                    <p>Regional discovery, made personal. StreamGlass brings subscriber taste, catalog diversity, and co-watch signals together in one transparent recommendation experience.</p>
                    <div class="landing-proofline"><span>Language-aware</span><span>Graph-powered</span><span>Explainable ranking</span></div>
                    <div class="landing-stats">
                      <div class="landing-stat"><strong>{int(hero_metrics['user_count']):,}</strong><span>subscriber profiles</span></div>
                      <div class="landing-stat"><strong>{int(hero_metrics['movie_count']):,}</strong><span>catalog titles</span></div>
                      <div class="landing-stat"><strong>{int(hero_metrics['interaction_count']):,}</strong><span>watch signals</span></div>
                    </div>
                </div>''',
                unsafe_allow_html=True,
            )
        with visual_col:
            st.markdown(
                f'''<div class="landing-visual" aria-label="A live recommendation map with real StreamGlass catalog titles">
                    <svg class="signal-map" viewBox="0 0 520 420" aria-hidden="true">
                      <path d="M60 300 C130 240 165 125 250 164 S375 312 465 115" fill="none" stroke="rgba(66,154,255,.34)" stroke-width="1.5" stroke-dasharray="4 8"/>
                      <path d="M55 125 C145 190 220 290 305 242 S395 130 475 300" fill="none" stroke="rgba(65,207,174,.30)" stroke-width="1.5" stroke-dasharray="3 9"/>
                      <circle cx="60" cy="300" r="5"/><circle cx="250" cy="164" r="5"/><circle cx="465" cy="115" r="5"/><circle cx="55" cy="125" r="4"/><circle cx="305" cy="242" r="4"/><circle cx="475" cy="300" r="4"/>
                    </svg>
                    <div class="signal-orbit"></div>
                    <div class="movie-orbit-stage" aria-label="Continuous floating movie catalog orbit">
                        {orbit_styles}
                        {orbital_cards_html}
                    </div>
                    <div class="hero-signal-card"><span>Live recommendation signals</span><strong>Taste · language · co-watch</strong></div>
                    <div class="hero-match-badge"><span>Discovery, with context</span><strong>Made for every viewer</strong></div>
                </div>''',
                unsafe_allow_html=True,
            )

elif st.session_state.current_module == "overview":
    brandline("OTT intelligence platform")
    page_header("Personalized discovery, made legible","A calmer way to understand an OTT recommendation engine.","StreamGlass brings the subscriber, catalog, and recommendation model into one focused academic product—without hiding the mathematics behind the interface.")
    left,right=st.columns([1.18,.82],gap="large")
    with left: st.markdown('''<section class="surface"><h3>Why StreamGlass exists</h3><div class="quote">A regional streaming platform should not present the same popular list to every viewer.</div><p>The system counters catalog starvation by accounting for language, genre, historic interactions, and the relationships that form in co-watch behavior.</p><ul><li><b>Regional relevance</b> supports primary and secondary language affinity.</li><li><b>Catalog diversity</b> is preserved through equivalence-class partitioning.</li><li><b>Transparent ranking</b> exposes the signals behind every recommendation.</li></ul></section>''',unsafe_allow_html=True)
    with right: st.markdown('''<section class="surface"><h3>Project dossier</h3><div class="people-list"><div class="person-row"><span>Kovvuri Venkata Reddy</span><code>25B21A4502</code></div><div class="person-row"><span>Pantadi H. Durga Prasad</span><code>25B21A4503</code></div><div class="person-row"><span>Battula Sravan Kumar</span><code>25B21A4501</code></div><div class="person-row"><span>Bodireddy Kanaka Mani</span><code>25B21A4504</code></div><div class="person-row"><span>Kapa Kumar</span><code>25B21A4506</code></div></div></section>''',unsafe_allow_html=True)
    section_heading("The intelligence pipeline","Four academic perspectives, connected in a single recommendation flow.")
    steps=[("DBMS","Relational ingestion","3NF SQLite schema records subscribers, titles, and watch events.","#0071e3"),("DMGT","Quotient partitioning","Equivalence classes protect language–genre diversity in discovery.","#248a3d"),("ADSA","Co-watch topology","Weighted adjacency lists surface bridge titles and neighbor paths.","#b25000"),("OOPJ + ML","Hybrid scoring","Cosine similarity and graph centrality shape personal relevance.","#5c5ce2")]
    for column,(label,title,copy,color) in zip(st.columns(4,gap="small"),steps):
        with column: st.markdown(f'<section class="pipeline-step" style="--step-color:{color}"><div class="step-label">{label}</div><h3>{title}</h3><p>{copy}</p></section>',unsafe_allow_html=True)

elif st.session_state.current_module == "coursework":
    brandline("Coursework")
    page_header("JNTUK R23 · II B.Tech I Sem","Formal foundations, presented as a product surface.","Proofs, relational integrity, graph traversal, and collaborative filtering remain live rather than becoming static documentation.")
    tab_db,tab_dmgt,tab_adsa,tab_ml=st.tabs(["DBMS","DMGT","ADSA","OOPJ + Python"])
    with tab_db:
        section_heading("Relational model","Entities stay normalized while interactions retain their own transaction history.")
        one,two=st.columns(2,gap="large")
        with one:
            st.markdown('<div class="formula-surface">',unsafe_allow_html=True)
            st.latex(r"\text{Users}(\underline{\text{user\_id}},\; \text{name},\; \text{age},\; \text{primary\_language},\; \text{secondary\_language})")
            st.latex(r"\text{Movies}(\underline{\text{movie\_id}},\; \text{title},\; \text{year},\; \text{language},\; \text{primary\_genre},\; \text{director})")
            st.latex(r"\text{WatchHistory}(\underline{\text{history\_id}},\; \text{user\_id}^{*},\; \text{movie\_id}^{*},\; \text{watch\_percentage},\; \text{rating})")
            st.markdown('</div>',unsafe_allow_html=True)
        with two: st.markdown('''<section class="surface"><h3>3NF validation</h3><p>Each entity is identified by a candidate key. User, movie, and interaction attributes are fully dependent on their own key, avoiding transitive dependencies between content and viewing events.</p><p><b>Indexes</b> accelerate subscriber, title, language–genre, and popularity lookup paths.</p></section>''',unsafe_allow_html=True)
        st.markdown('''<div class="formula-surface" style="margin-top:16px"><b>Functional dependencies</b><br><br>F₁: user_id → {name, age, primary_language}<br>F₂: movie_id → {title, year, language, primary_genre}<br>F₃: history_id → {user_id, movie_id, watch_pct, rating}</div>''',unsafe_allow_html=True)
    with tab_dmgt:
        movies_df=database.get_all_movies(); records=movies_df.to_dict(orient="records"); ref=discrete_math.verify_reflexivity(records); sym=discrete_math.verify_symmetry(records); trn=discrete_math.verify_transitivity(records); quotient=discrete_math.compute_equivalence_classes(records); partition=discrete_math.verify_partition_theorem(records,quotient)
        section_heading("Equivalence relation","Live verification over the catalog—not a mocked proof state.")
        st.latex(r"(x, y) \in R \iff \text{Genre}(x) = \text{Genre}(y) \land \text{Language}(x) = \text{Language}(y)")
        for column,proof in zip(st.columns(3,gap="small"),[ref,sym,trn]):
            with column: st.markdown(f'<section class="proof-card"><div class="proof-kicker">VERIFIED AXIOM</div><h3>{esc(proof["property"])}</h3><code>{esc(proof["formula"])}</code><p>{esc(proof["mathematical_proof"])}</p></section>',unsafe_allow_html=True)
        st.markdown(f'<section class="surface" style="margin-top:16px"><h3>Partition theorem</h3><p>The quotient set produces <b>{partition["num_classes"]} pairwise-disjoint classes</b>. Its union covers <b>{partition["union_coverage_size"]} of {partition["total_universe_size"]} catalog items</b>; disjointness and exhaustive coverage both pass.</p></section>',unsafe_allow_html=True)
    with tab_adsa:
        graph=graph_engine.build_cowatch_graph_from_db(); metrics=graph.get_graph_metrics(); section_heading("Co-watch graph","A custom weighted adjacency list turns shared viewing behavior into topology.")
        st.latex(r"W(u,v) = \sum_{s \in S_{uv}} \left[\left(\frac{r_{s,u}+r_{s,v}}{10}\right)\times\left(\frac{\min(w_{s,u},w_{s,v})}{100}\right)\right]")
        a,b=st.columns([1.08,.92],gap="large")
        with a: st.markdown('''<section class="surface"><h3>Traversal and centrality</h3><p><b>Breadth-first search</b> visits related titles through a FIFO queue in O(|V| + |E|). Normalized weighted degree centrality identifies titles that bridge regional co-watch communities.</p></section>''',unsafe_allow_html=True)
        with b: st.markdown(f'<section class="surface"><h3>Live topology</h3><p>Vertices <b>{metrics["num_nodes"]}</b> · Edges <b>{metrics["num_edges"]}</b> · Density <b>{metrics["density"]:.4f}</b></p><p>Top bridge: <b>{esc(metrics["top_hub_movie"])}</b> · centrality {metrics["top_hub_centrality"]:.4f}</p></section>',unsafe_allow_html=True)
    with tab_ml:
        section_heading("Hybrid recommendation model","A clear model contract for personal relevance and catalog discovery.")
        st.markdown('<div class="formula-surface">',unsafe_allow_html=True); st.latex(r"\text{Cosine Similarity}(i,j)=\frac{\vec{v}_i\cdot\vec{v}_j}{\|\vec{v}_i\|_2\|\vec{v}_j\|_2}"); st.latex(r"\text{Score}(u,i)=\left[\alpha\cdot\frac{\widehat{r}_{u,i}}{5.0}+(1-\alpha)\cdot\frac{C_D(i)}{\max_k C_D(k)}\right]\times\beta_{\text{lang}}(u,i)\times\gamma_{\text{genre}}(u,i)"); st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<section class="surface" style="margin-top:16px"><h3>Interpretation</h3><p>The α control balances collaborative ratings with graph connectivity. Language and genre modifiers preserve the regional relevance that a popularity-only feed ignores.</p></section>',unsafe_allow_html=True)

elif st.session_state.current_module == "data":
    brandline("Engineering & data"); page_header("Live SQLite system view","Operationally simple, structurally rigorous.","Inspect the actual relational tables and storage metrics powering the recommender—without leaving the product.")
    db_metrics=database.get_db_metrics(); cards=[("Subscribers",db_metrics["user_count"],"registered user profiles"),("Catalog titles",db_metrics["movie_count"],"regional media records"),("Watch events",db_metrics["interaction_count"],"recorded interactions"),("SQLite footprint",f'{db_metrics["database_size_kb"]} KB',"on-disk engine size")]
    for column,(label,value,note) in zip(st.columns(4,gap="small"),cards):
        with column: metric_card(label,value,note)
    section_heading("Table explorer","The selected relation is queried from the live local database.")
    table_choice=st.radio("Relation",["users","movies","watch_history"],horizontal=True,label_visibility="collapsed"); conn=database.get_connection()
    if table_choice=="users": df_view=pd.read_sql_query("SELECT user_id, name, age, primary_language, secondary_language, preferred_genres, persona_desc FROM users;",conn)
    elif table_choice=="movies": df_view=pd.read_sql_query("SELECT movie_id, title, release_year, language, primary_genre, director, avg_rating, popularity_score FROM movies;",conn)
    else: df_view=pd.read_sql_query("SELECT history_id, user_id, movie_id, watch_percentage, rating, watched_at FROM watch_history ORDER BY watched_at DESC;",conn)
    conn.close(); st.markdown('<div class="data-surface">',unsafe_allow_html=True); st.dataframe(df_view,use_container_width=True,height=345,hide_index=True); st.markdown('</div>',unsafe_allow_html=True)
    section_heading("Runtime","The application services currently composing this interface.")
    for column,(label,value) in zip(st.columns(4,gap="small"),[("Python",sys.version.split()[0]),("Streamlit",st.__version__),("SQLite",db_metrics["sqlite_version"]),("Graph engine","NetworkX")]):
        with column: metric_card(label,value,"service available")

elif st.session_state.current_module == "model":
    brandline("Model lab"); page_header("Tune the ranking model","Move from an abstract formula to a visible recommendation decision.","The controls update the existing hybrid scoring engine; the vector view and force graph reflect its live database state.")
    section_heading("Recommendation controls","Personal relevance and catalog discovery share a deliberate balance."); controls=st.columns(2,gap="large")
    with controls[0]:
        new_k=st.slider("Nearest neighbors",2,8,st.session_state.k_neighbors,1)
        if new_k != st.session_state.k_neighbors: st.session_state.k_neighbors=new_k; engine.set_hyperparameters(new_k,st.session_state.alpha_weight)
    with controls[1]:
        new_alpha=st.slider("Collaborative weighting",0.0,1.0,st.session_state.alpha_weight,.05)
        if new_alpha != st.session_state.alpha_weight: st.session_state.alpha_weight=new_alpha; engine.set_hyperparameters(st.session_state.k_neighbors,new_alpha)
    st.markdown(f'<div class="status-line"><span class="status-dot"></span>{int(st.session_state.alpha_weight*100)}% collaborative filtering · {int((1-st.session_state.alpha_weight)*100)}% graph centrality · k = {st.session_state.k_neighbors}</div>',unsafe_allow_html=True)
    section_heading("Cosine similarity","Choose any two catalog titles to inspect the exact vector calculation."); all_movies=database.get_all_movies(); movie_options={row["movie_id"]:f'{row["title"]} · {row["language"]}' for _,row in all_movies.iterrows()}; m1,m2=st.columns(2,gap="large")
    with m1: movie_a=st.selectbox("First title",list(movie_options),index=0,format_func=lambda item:movie_options[item])
    with m2: movie_b=st.selectbox("Second title",list(movie_options),index=1,format_func=lambda item:movie_options[item])
    breakdown=engine.knn.get_stepwise_vector_math(movie_a,movie_b)
    if "error" in breakdown: st.warning(breakdown["error"])
    else:
        values=[("Cosine similarity",breakdown["cosine_similarity"],"normalized affinity"),("Dot product",breakdown["dot_product"],"shared rating signal"),("Norm A",breakdown["norm_a"],movie_a),("Norm B",breakdown["norm_b"],movie_b)]
        for column,(label,value,note) in zip(st.columns(4,gap="small"),values):
            with column: metric_card(label,value,note)
    section_heading("Co-watch topology","Node scale reflects normalized degree centrality; links represent shared viewing behavior."); network=graph_engine.build_cowatch_graph_from_db().generate_plotly_network(); network.update_traces(selector=dict(mode="lines"),line=dict(color="rgba(60,60,67,.24)")); network.update_traces(selector=dict(mode="markers+text"),textfont=dict(color="#424245"),marker=dict(line=dict(color="#ffffff",width=1.3))); st.plotly_chart(apply_chart_theme(network,510),use_container_width=True,config={"displayModeBar":False})

elif st.session_state.current_module == "studio":
    brandline("Live studio"); page_header("Recommendation, side by side","Your private StreamGlass studio.","The feeds below are generated only from the signed-in subscriber profile and its watch signals.")
    users_df = database.get_all_users()
    logged_in_id = st.session_state.get("logged_in_user_id")
    if not logged_in_id:
        st.markdown(
            '''<section class="surface" style="text-align:center;padding:36px 24px;margin:20px 0;">
                <div style="font-size:1.25rem;font-weight:740;color:var(--ink);margin-bottom:8px;">Sign in to view your Studio</div>
                <p style="color:var(--muted);max-width:500px;margin:0 auto 20px;font-size:.9rem;line-height:1.55;">
                    The Studio displays personalized recommendations, viewing history, and watch signals for your signed-in subscriber profile.
                </p>
            </section>''',
            unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Sign in to StreamGlass", key="studio_login_cta", use_container_width=True):
                open_login_dialog()
                st.rerun()
    else:
        matched = users_df[users_df["user_id"] == logged_in_id]
        if matched.empty:
            raw_user = users_df.iloc[0].to_dict()
        else:
            raw_user = matched.iloc[0].to_dict()
        subscriber = recommender.Subscriber.from_dict(raw_user)
        history = database.get_user_watch_history(subscriber.user_id)
        subscriber.load_history(history.to_dict(orient="records"))

        # Active Subscriber Section
        section_heading("Active subscriber", "Only the signed-in viewer profile and its interactions are shown in this Studio.")
        profile_surface(subscriber, len(history))

        # Title Section (placed below Active Subscriber section and above both Popular Now and For This Subscriber)
        section_heading("Title Section", "Watch, rate, and manage catalog titles, then inspect their effect on platform recommendation feeds.")
        with st.expander("Watch and rate a title", expanded=False):
            all_movies = database.get_all_movies()
            watched_ids = set(subscriber.get_watched_movie_ids())
            unwatched = {row["movie_id"]:f'{row["title"]} · {row["language"]} · {row["primary_genre"]}' for _,row in all_movies.iterrows() if row["movie_id"] not in watched_ids}
            if not unwatched:
                st.success("You have rated every title in the catalog.")
            else:
                c1,c2,c3 = st.columns([1.55,1,1],gap="medium")
                with c1: target_movie = st.selectbox("Title",list(unwatched),format_func=lambda item:unwatched[item])
                with c2: watch_percentage = st.slider("Completion",10,100,95,5,format="%d%%")
                with c3: rating = st.slider("Rating",1.0,5.0,4.5,.5)
                if st.button("Record interaction", key="record_studio_interaction", use_container_width=True):
                    history_id = database.record_user_interaction(subscriber.user_id,target_movie,watch_percentage,rating)
                    engine.refresh()
                    st.success(f"Interaction {history_id} was recorded for {subscriber.name}. The ranking engine is refreshed.")
                    st.rerun()

        # Item 3: Add Movies option
        with st.expander("Add Movies", expanded=False):
            st.caption("Add a title to the shared demo catalog. It becomes available to this Studio immediately.")
            with st.form("add_movie_form", clear_on_submit=True):
                first, second = st.columns(2, gap="medium")
                with first:
                    movie_title = st.text_input("Movie title")
                    movie_language = st.text_input("Language", value="Telugu")
                    movie_year = st.number_input("Release year", min_value=1900, max_value=2100, value=2026, step=1)
                with second:
                    movie_genre = st.text_input("Primary genre", value="Drama")
                    movie_director = st.text_input("Director")
                    movie_duration = st.number_input("Duration (minutes)", min_value=1, max_value=500, value=120, step=1)
                movie_secondary_genre = st.text_input("Secondary genre (optional)")
                add_movie_submitted = st.form_submit_button("Add Movie", use_container_width=True)
            if add_movie_submitted:
                try:
                    movie_id = database.add_movie(movie_title, movie_year, movie_language, movie_genre, movie_director, movie_secondary_genre, movie_duration)
                    engine.refresh()
                    st.success(f"{movie_title.strip()} was added to the catalog as {movie_id}.")
                    st.rerun()
                except ValueError as error:
                    st.warning(str(error))

        # Popular Now and For This Subscriber (below Title Section, highlighted headings)
        baseline,personalized=st.columns(2,gap="large")
        with baseline:
            st.markdown('<div class="feed-head feed-head-popular"><h2>Popular Now</h2><span>STATIC BASELINE</span></div><p class="feed-copy">The same ordering is delivered to every subscriber, regardless of language or prior viewing.</p>',unsafe_allow_html=True)
            for item in engine.get_static_popular_feed(limit=6): title_card(item,primary_language=subscriber.primary_language,secondary_language=subscriber.secondary_language)
        with personalized:
            st.markdown('<div class="feed-head feed-head-personal"><h2>For This Subscriber</h2><span>STREAMGLASS</span></div><p class="feed-copy">Hybrid ranking uses observed ratings, co-watch topology, language affinity, and preferred genres.</p>',unsafe_allow_html=True); recommendations=engine.get_personalized_recommendations(subscriber,limit=6)
            if recommendations:
                for item in recommendations: title_card(item,personalized=True)
            else: st.info("This subscriber has no remaining unwatched titles to recommend.")

elif st.session_state.current_module == "analytics":
    brandline("Analytics"); page_header("Catalog intelligence","Three views of a recommendation system’s structure.","Explore catalog partitions, centrality hubs, and the sparsity that makes hybrid recommendation valuable.")
    tab_partition,tab_centrality,tab_matrix=st.tabs(["Catalog partitions","Co-watch centrality","Utility matrix"]); movies_df=database.get_all_movies()
    with tab_partition:
        section_heading("Language and genre partitions","The catalog is divided into language → genre → title equivalence classes."); sunburst=px.sunburst(movies_df,path=["language","primary_genre","title"],values="popularity_score",color="language",color_discrete_map={"Telugu":"#5b8ec7","Tamil":"#58a496","Hindi":"#d29652","English":"#8a7bc4"}); st.plotly_chart(apply_chart_theme(sunburst,550),use_container_width=True,config={"displayModeBar":False})
    with tab_centrality:
        section_heading("Bridge titles","Weighted degree centrality measures which titles connect the catalog’s co-watch communities."); graph=graph_engine.build_cowatch_graph_from_db(); centralities=graph.calculate_degree_centrality(); movie_names={row["movie_id"]:row["title"] for _,row in movies_df.iterrows()}; centrality_df=pd.DataFrame([{"Title":movie_names.get(movie_id,movie_id),"Centrality":score} for movie_id,score in centralities.items()]).sort_values("Centrality",ascending=True); bar=px.bar(centrality_df,x="Centrality",y="Title",orientation="h",color_discrete_sequence=["#0071e3"]); st.plotly_chart(apply_chart_theme(bar,550),use_container_width=True,config={"displayModeBar":False})
    with tab_matrix:
        section_heading("Observed ratings","Unobserved cells in the user–item matrix are the space where the model has to infer relevance."); matrix=recommender.InteractionMatrix(); sparsity=matrix.get_sparsity(); metric_card("Matrix sparsity",f"{sparsity*100:.1f}%","unobserved user–title rating pairs")
        if not matrix.matrix_df.empty:
            # Reindex against the live catalog and subscriber table so cold-start
            # subscribers remain visible rather than disappearing from the matrix.
            user_order=sorted(database.get_all_users()["user_id"].tolist(),key=lambda user_id:int(user_id[1:]))
            movie_order=sorted(movies_df["movie_id"].tolist(),key=lambda movie_id:int(movie_id[1:]))
            utility=matrix.matrix_df.reindex(index=user_order,columns=movie_order)
            hover_labels=utility.map(lambda rating: "Unobserved" if pd.isna(rating) else f"{float(rating):.1f} / 5")
            heat=go.Figure(data=go.Heatmap(
                z=utility.fillna(0.0).values,
                x=utility.columns.tolist(),
                y=utility.index.tolist(),
                customdata=hover_labels.values,
                colorscale=[[0,"#f3f6f9"],[0.18,"#e2edf8"],[0.55,"#79afe2"],[1,"#0071e3"]],
                zmin=0,
                zmax=5,
                xgap=2,
                ygap=2,
                colorbar=dict(title="Rating",tickvals=[0,1,2,3,4,5],ticktext=["—", "1", "2", "3", "4", "5"]),
                hovertemplate="Subscriber: %{y}<br>Title: %{x}<br>Rating: %{customdata}<extra></extra>",
            ))
            heat.update_xaxes(title="Movie",tickangle=-45,side="bottom")
            heat.update_yaxes(title="Subscriber",autorange="reversed")
            st.plotly_chart(apply_chart_theme(heat,535),use_container_width=True,config={"displayModeBar":False})

if st.session_state.login_dialog_open:
    show_login_dialog()

st.markdown('<div class="streamglass-footer"><div>StreamGlass · OTT subscriber and personalized recommendation system · JNTUK R23 · TEAM-18</div></div>',unsafe_allow_html=True)
