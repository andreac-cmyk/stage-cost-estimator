#!/usr/bin/env python3
"""Netflix Stage Utilization Calculator — Streamlit Dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os

# Load title lookup data (from Kragle/Slate Manager + utilization history)
TITLE_LOOKUP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "title_lookup.json")
if os.path.exists(TITLE_LOOKUP_PATH):
    with open(TITLE_LOOKUP_PATH) as _f:
        TITLE_LOOKUP = json.load(_f)
else:
    TITLE_LOOKUP = {}

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Netflix Studios Stage Cost Estimator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2.5rem; max-width: 1400px; }
    [data-testid="stSidebar"] {
        min-width: 320px;
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] [data-testid="stNumberInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * { color: #1a1a1a !important; }
    [data-testid="stSidebar"] .predict-card * { color: inherit !important; }
    [data-testid="stSidebar"] .predict-card h3 { color: #2563eb !important; }
    [data-testid="stSidebar"] .predict-card .pred-val { color: #1a1a1a !important; }
    [data-testid="stSidebar"] .title-intel * { color: #000000 !important; }
    [data-testid="stSidebar"] .title-intel .ti-header { color: #5b21b6 !important; }
    [data-testid="stSidebar"] .title-intel strong { color: #000000 !important; }
    [data-testid="stSidebar"] .returning-series * { color: #000000 !important; }
    [data-testid="stSidebar"] .returning-series .rs-header { color: #5b21b6 !important; }
    [data-testid="stSidebar"] .returning-series strong { color: #000000 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stTextInput label {
        color: #aaa !important; font-size: 0.88rem; text-transform: uppercase;
        letter-spacing: 0.05em; font-weight: 500;
    }
    [data-testid="stMetric"] {
        background: #ffffff; border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
    }
    [data-testid="stMetric"] label { font-size: 0.78rem !important; color: #888 !important;
        text-transform: uppercase; letter-spacing: 0.04em; font-weight: 500; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.4rem !important; font-weight: 700 !important; color: #1a1a1a !important; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a1a; margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem; border-bottom: 2px solid #E50914; letter-spacing: -0.01em;
    }
    .section-subheader { font-size: 0.95rem; color: #888; margin: -0.5rem 0 1rem 0; }
    .top-banner {
        background: linear-gradient(135deg, #B20710 0%, #E50914 50%, #B20710 100%);
        color: white; padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
    }
    .top-banner h1 { color: white !important; font-size: 1.6rem; font-weight: 700; margin: 0; }
    .top-banner p { color: rgba(255,255,255,0.85); font-size: 0.85rem; margin: 0.2rem 0 0 0; }
    .loc-card {
        background: #fff; border-radius: 12px; padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;
        text-align: center; height: 100%;
    }
    .loc-card.best { border: 2px solid #22c55e; background: #f0fdf4; }
    .loc-card.worst { border: 1px solid #fecaca; background: #fef2f2; }
    .loc-card.disabled { opacity: 0.35; }
    .loc-card h3 { font-size: 1rem; font-weight: 600; margin: 0 0 12px 0; color: #1a1a1a; }
    .loc-card .big-num { font-size: 1.5rem; font-weight: 700; color: #1a1a1a; }
    .loc-card .sub { font-size: 0.88rem; color: #888; margin-top: 4px; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600; margin-top: 8px; text-transform: uppercase; }
    .badge-best { background: #dcfce7; color: #16a34a; }
    .badge-worst { background: #fee2e2; color: #dc2626; }
    .badge-na { background: #f3f4f6; color: #9ca3af; }
    .rec-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e; border-radius: 16px; padding: 24px 32px;
        height: 100%; box-sizing: border-box;
    }
    .rec-card h2 { font-size: 1.3rem; font-weight: 700; color: #15803d; margin: 0 0 4px 0; }
    .rec-card .rec-loc { font-size: 2rem; font-weight: 800; color: #166534; }
    .rec-card .rec-detail { font-size: 0.85rem; color: #4b5563; }
    .predict-card {
        background: #ffffff; border: 2px solid #3b82f6; border-radius: 16px;
        padding: 16px 20px; margin-bottom: 1rem;
    }
    .predict-card h3 { font-size: 0.85rem; font-weight: 600; color: #2563eb !important; margin: 0 0 10px 0; }
    .predict-card .pred-val { font-size: 1rem; color: #1a1a1a !important; line-height: 1.8; }
    .rate-note {
        background: #f8f9fa; border-left: 3px solid #E50914; padding: 12px 16px;
        border-radius: 0 8px 8px 0; font-size: 0.92rem; color: #4b5563;
        margin-top: 2rem; line-height: 1.6;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}

    /* Equal-height columns */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

BUYING_ORGS = {
    "Animation Series": ["Adult Animation Comedy Series", "Adult Animation Genre Series",
                         "Kids Animation Series", "Kids Co-Commissions & Licensing", "Preschool Series"],
    "APAC": ["Anime", "Australia/New Zealand", "Chinese Language", "Indonesia", "Japan",
             "Korea", "Philippines", "RoSEA", "Thailand"],
    "EMEA": ["Africa", "Arabic", "Benelux", "CEE", "France", "Germany", "Israel",
             "Italy", "Nordics", "Rest of EMEA", "Spain", "Turkey", "UK"],
    "Film": ["Action/Sci-Fi/Fantasy/Horror Film", "Animation Film", "Comedy/RomCom Film",
             "Documentary Film", "Drama/Thriller/Family Film", "Feature Animation",
             "Film Acquisitions", "YA/Faith Based/Holiday Film"],
    "India": ["India"],
    "LatAm": ["Brazil", "Mexico", "Rest of LatAm"],
    "Licensing": ["Film Licensing", "TV Licensing"],
    "Nonfiction Series": ["Doc Series", "Nonfiction Live Events", "Sports", "Unscripted Series"],
    "UCAN Scripted Series": ["Canada", "Comedy Series", "Drama Series", "Stand-Up & Comedy Formats"],
}

# Location routing: which regions to show based on buying org/team
LOCATION_ROUTING = {
    # UCAN → US locations + UK + New Jersey + Canada only (no Madrid/Japan)
    "UCAN Scripted Series": ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey", "UK", "Vancouver"],
    "Film": ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey", "UK", "Vancouver"],
    "Animation Series": ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey", "UK", "Vancouver"],
    "Nonfiction Series": ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey"],
    "Licensing": ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey", "UK"],
    # Local content → route to local + nearby
    "APAC": ["Japan", "Korea"],  # default, overridden per buying team below
    "India": ["UK"],  # typically shoot in UK
    "LatAm": ["Madrid"],  # Spanish-language often in Madrid
    "EMEA": ["UK", "Madrid"],  # default, overridden per buying team below
}

# Buying team specific overrides
TEAM_LOCATION_OVERRIDES = {
    # APAC teams
    "Japan": ["Japan"],
    "Korea": ["Korea", "Japan"],
    "Anime": ["Japan"],
    "Chinese Language": ["Japan"],
    "Australia/New Zealand": ["UK"],
    "Indonesia": ["Japan"],
    "Philippines": ["Japan"],
    "RoSEA": ["Japan"],
    "Thailand": ["Japan"],
    # EMEA teams
    "Spain": ["Madrid"],
    "Turkey": ["Madrid", "UK"],
    "UK": ["UK"],
    "France": ["UK", "Madrid"],
    "Germany": ["UK", "Madrid"],
    "Italy": ["Madrid", "UK"],
    "Nordics": ["UK"],
    "Benelux": ["UK"],
    "CEE": ["UK", "Madrid"],
    "Africa": ["UK", "Madrid"],
    "Arabic": ["Madrid", "UK"],
    "Israel": ["UK"],
    "Rest of EMEA": ["UK", "Madrid"],
    # LatAm teams
    "Brazil": ["Madrid"],
    "Mexico": ["Madrid", "Albuquerque"],
    "Rest of LatAm": ["Madrid"],
    # UCAN with Canada preference
    "Canada": ["Vancouver", "Los Angeles", "New York", "UK"],
}

# Prediction model based on real utilization data (488 productions analyzed)
POD_PREDICTIONS = {
    "APAC": {"avg_stages": 1.9, "median_stages": 2, "avg_duration_days": 98, "avg_sqft": 15106},
    "EMEA": {"avg_stages": 4.0, "median_stages": 4, "avg_duration_days": 242, "avg_sqft": 12621},
    "Los Angeles": {"avg_stages": 2.5, "median_stages": 2, "avg_duration_days": 75, "avg_sqft": 12467},
    "Spain": {"avg_stages": 1.9, "median_stages": 1, "avg_duration_days": 144, "avg_sqft": 14135},
    "UCAN East": {"avg_stages": 2.9, "median_stages": 2, "avg_duration_days": 126, "avg_sqft": 18350},
    "UCAN West": {"avg_stages": 2.6, "median_stages": 2, "avg_duration_days": 155, "avg_sqft": 18725},
    "UK": {"avg_stages": 4.3, "median_stages": 4, "avg_duration_days": 127, "avg_sqft": 16735},
}

# Map buying org to pod for predictions
ORG_TO_POD = {
    "Animation Series": "Los Angeles",
    "APAC": "APAC",
    "EMEA": "EMEA",
    "Film": "Los Angeles",
    "India": "UK",
    "LatAm": "Spain",
    "Licensing": "Los Angeles",
    "Nonfiction Series": "Los Angeles",
    "UCAN Scripted Series": "UCAN East",
}

# ── Production Type Classification ──
# Determines stage needs and location preferences
PRODUCTION_TYPES = {
    "1hr Drama Series": {"needs_stages": True, "typical_stages": 3, "la_affinity": 0.3, "notes": "Large footprint, benefits from dedicated facility"},
    "30min Comedy Series": {"needs_stages": True, "typical_stages": 2, "la_affinity": 0.8, "notes": "Multi-cam typically LA-based, talent won't relocate"},
    "Limited Series": {"needs_stages": True, "typical_stages": 2, "la_affinity": 0.4, "notes": "Flexible on location"},
    "Feature Film": {"needs_stages": True, "typical_stages": 3, "la_affinity": 0.3, "notes": "Location flexible, incentive-driven"},
    "Unscripted / Reality": {"needs_stages": False, "typical_stages": 1, "la_affinity": 0.6, "notes": "Usually purpose-built sets or locations, not traditional stages"},
    "Documentary": {"needs_stages": False, "typical_stages": 0, "la_affinity": 0.2, "notes": "Location-based, no stage needed"},
    "Stand-Up / Comedy Special": {"needs_stages": False, "typical_stages": 0, "la_affinity": 0.7, "notes": "Venue-based, no stage needed"},
    "Animation": {"needs_stages": False, "typical_stages": 0, "la_affinity": 0.9, "notes": "Office/post-based, no physical stage needed"},
    "Live Event": {"needs_stages": False, "typical_stages": 0, "la_affinity": 0.5, "notes": "Venue-based"},
}

# Map buying teams to default production types
TEAM_TO_PROD_TYPE = {
    "Drama Series": "1hr Drama Series",
    "Comedy Series": "30min Comedy Series",
    "Stand-Up & Comedy Formats": "Stand-Up / Comedy Special",
    "Canada": "1hr Drama Series",
    "Doc Series": "Documentary",
    "Unscripted Series": "Unscripted / Reality",
    "Nonfiction Live Events": "Live Event",
    "Sports": "Unscripted / Reality",
    "Adult Animation Comedy Series": "Animation",
    "Adult Animation Genre Series": "Animation",
    "Kids Animation Series": "Animation",
    "Kids Co-Commissions & Licensing": "Animation",
    "Preschool Series": "Animation",
    "Feature Animation": "Animation",
    "Animation Film": "Animation",
    "Film Acquisitions": "Feature Film",
    "Action/Sci-Fi/Fantasy/Horror Film": "Feature Film",
    "Comedy/RomCom Film": "Feature Film",
    "Documentary Film": "Documentary",
    "Drama/Thriller/Family Film": "Feature Film",
    "YA/Faith Based/Holiday Film": "Feature Film",
    "Film Licensing": "Feature Film",
    "TV Licensing": "1hr Drama Series",
}

# Prior season location mapping (franchise -> region where it shoots)
FRANCHISE_LOCATIONS = {
    "Stranger Things": {"region": "Atlanta", "facility": "Cinespace Atlanta"},
    "Bridgerton": {"region": "UK", "facility": "Netflix Studios Uxbridge"},
    "The Witcher": {"region": "UK", "facility": "Shepperton Studios"},
    "The Sandman": {"region": "UK", "facility": "Shepperton Studios"},
    "Avatar: The Last Airbender": {"region": "Canada", "facility": "Canadian Motion Picture Park"},
    "Cobra Kai": {"region": "Atlanta", "facility": "Cinespace Atlanta"},
    "Virgin River": {"region": "Canada", "facility": "Canadian Motion Picture Park"},
    "Ozark": {"region": "Atlanta", "facility": "Cinespace Atlanta"},
    "Monster": {"region": "Los Angeles", "facility": "Raleigh Studios"},
    "The Boroughs": {"region": "Albuquerque", "facility": "Netflix Studios Albuquerque"},
    "Ransom Canyon": {"region": "Albuquerque", "facility": "Netflix Studios Albuquerque"},
    "Snowpiercer": {"region": "Canada", "facility": "Canadian Motion Picture Park"},
    "The Night Agent": {"region": "Atlanta", "facility": "Cinespace Atlanta"},
    "Survival of the Thickest": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "That 90": {"region": "Los Angeles", "facility": "Sunset Gower Studios"},
    "That '90": {"region": "Los Angeles", "facility": "Sunset Gower Studios"},
    "Grace and Frankie": {"region": "Los Angeles", "facility": "Sunset Gower Studios"},
    "The Upshaws": {"region": "Los Angeles", "facility": "Sunset Gower Studios"},
    "Elite": {"region": "Madrid", "facility": "Madrid Content City"},
    "Berlin": {"region": "Madrid", "facility": "Madrid Content City"},
    "La Casa de Papel": {"region": "Madrid", "facility": "Madrid Content City"},
    "Black Mirror": {"region": "UK", "facility": "Shepperton Studios"},
    "Enola Holmes": {"region": "UK", "facility": "Shepperton Studios"},
    "The Three Body Problem": {"region": "UK", "facility": "Shepperton Studios"},
    "Better Call Saul": {"region": "Albuquerque", "facility": "Netflix Studios Albuquerque"},
    "No Good Deed": {"region": "Los Angeles", "facility": "Sunset Gower Studios"},
    "From Scratch": {"region": "Los Angeles", "facility": "Sunset Bronson Studios"},
    "Fubar": {"region": "Atlanta", "facility": "Cinespace Atlanta"},
    "Squid Game": {"region": "Korea", "facility": "YCDSMC Studios"},
    "Hierarchy": {"region": "Korea", "facility": "K-ART Studio"},
    "The Night Agent": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "Survival of the Thickest": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "The Diplomat": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "Kaleidoscope": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "The Watcher": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
    "The Madness": {"region": "New York", "facility": "Netflix Studios Brooklyn"},
}


def detect_franchise(title):
    """Check if title is a returning series with an established shoot location."""
    if not title or title == "-- Enter custom title --":
        return None
    for franchise, info in FRANCHISE_LOCATIONS.items():
        if franchise.lower() in title.lower():
            return {"franchise": franchise, **info}
    return None


def get_production_type(buying_org, buying_team):
    """Determine production type from buying team."""
    if buying_team in TEAM_TO_PROD_TYPE:
        return TEAM_TO_PROD_TYPE[buying_team]
    if buying_org == "Animation Series":
        return "Animation"
    if buying_org == "Nonfiction Series":
        return "Unscripted / Reality"
    if buying_org == "Film":
        return "Feature Film"
    return "1hr Drama Series"  # default


# Title keyword → location hints (boosts score for matching regions)
TITLE_LOCATION_HINTS = {
    "Albuquerque": [
        "western", "desert", "ranch", "cowboy", "frontier", "nuclear", "meth", "cartel",
        "border", "southwest", "mesa", "canyon", "outlaw", "vegas", "nevada", "new mexico",
        "albuquerque", "breaking", "saul", "ozymandias", "wild west", "ranch", "rodeo",
        "apocalypse", "wasteland", "military", "base camp", "test site", "bunker",
    ],
    "Los Angeles": [
        "hollywood", "studio", "celebrity", "red carpet", "beverly hills", "malibu",
        "sunset", "la ", "los angeles", "comedian", "comedy", "stand-up", "standup",
        "talk show", "game show", "reality", "competition", "cooking", "baking",
        "dating", "mulaney", "golf", "sports", "multi-cam", "multicam", "sitcom",
        "late night", "awards", "premiere", "industry", "agent", "actor",
    ],
    "Atlanta": [
        "south", "southern", "georgia", "atlanta", "peach", "plantation",
        "civil war", "bayou", "swamp", "rural america", "small town",
    ],
    "UK": [
        "british", "london", "england", "castle", "manor", "royal", "queen", "king",
        "medieval", "period", "victorian", "regency", "tudor", "fantasy", "dragon",
        "knight", "witch", "wizard", "magic", "hobbit", "narnia", "chronicles",
        "sherlock", "bond", "spy", "mi5", "mi6", "scotland", "wales", "irish",
    ],
    "New York": [
        "new york", "nyc", "manhattan", "brooklyn", "bronx", "queens",
        "wall street", "broadway", "harlem", "urban", "city",
        "diplomat", "agent", "night agent", "thickest", "watcher",
        "madness", "kaleidoscope", "gotham", "empire state",
    ],
    "New Jersey": [
        "new jersey", "jersey", "sopranos", "shore", "suburban", "east coast",
        "monmouth", "fort",
    ],
    "Japan": [
        "japan", "tokyo", "samurai", "ninja", "anime", "manga", "borderland",
        "yakuza", "shogun", "ronin", "karate", "judo", "sumo", "geisha",
        "sakura", "edo", "kyoto", "osaka", "okinawa", "alice in borderland",
    ],
    "Korea": [
        "korea", "korean", "k-drama", "seoul", "busan", "squid game",
        "parasyte", "hierarchy", "bloodhounds", "black knight", "mask girl",
        "sweet home", "all of us are dead", "kingdom", "hellbound",
    ],
    "Madrid": [
        "spain", "spanish", "madrid", "barcelona", "asalto", "banco", "casa de papel",
        "elite", "berlin", "heist", "flamenco", "bullfight", "ibiza", "andalusia",
        "mexico", "mexican", "cartel", "narco", "colombian", "latin", "telenovela",
        "portuguese", "brazil", "rio", "sao paulo", "buenos aires", "bogota",
    ],
}


# Map audience country to region
COUNTRY_TO_REGION = {
    "JP": "Japan", "KR": "Japan", "TH": "Japan", "PH": "Japan", "ID": "Japan",
    "IN": "UK", "AU": "UK", "NZ": "UK",
    "ES": "Madrid", "PT": "Madrid",
    "MX": "Madrid", "BR": "Madrid", "AR": "Madrid", "CO": "Madrid", "CL": "Madrid", "PE": "Madrid",
    "FR": "UK", "DE": "UK", "IT": "Madrid", "NL": "UK", "BE": "UK",
    "SE": "UK", "NO": "UK", "DK": "UK", "FI": "UK",
    "PL": "UK", "CZ": "UK", "HU": "UK", "RO": "UK",
    "TR": "Madrid", "IL": "UK", "ZA": "UK", "NG": "UK", "EG": "Madrid",
    "GB": "UK", "IE": "UK",
    "US": None, "CA": "Canada",  # US handled by buying team logic
}

# Map language to region as fallback
LANGUAGE_TO_REGION = {
    "ja": "Japan", "ko": "Japan", "th": "Japan", "zh": "Japan",
    "es": "Madrid", "pt": "Madrid", "pt-BR": "Madrid",
    "fr": "UK", "de": "UK", "it": "Madrid", "nl": "UK",
    "sv": "UK", "no": "UK", "da": "UK", "fi": "UK",
    "pl": "UK", "cs": "UK", "hu": "UK", "ro": "UK",
    "tr": "Madrid", "ar": "Madrid", "he": "UK",
    "hi": "UK", "ta": "UK", "te": "UK",
}


def get_title_location_hints(title):
    """Check title for location hints using keywords, historical data, and audience country."""
    if not title or title == "-- Enter custom title --":
        return {}
    title_lower = title.lower()
    hints = {}

    # 1. Keyword matching
    for region, keywords in TITLE_LOCATION_HINTS.items():
        for kw in keywords:
            if kw in title_lower:
                hints[region] = hints.get(region, 0) + 1

    # 2. Historical facility data from utilization (strongest signal)
    title_data = TITLE_LOOKUP.get(title, {})
    if "facility" in title_data and title_data.get("pod"):
        pod = title_data["pod"]
        # Map pod to region
        pod_to_region = {
            "Los Angeles": "Los Angeles",
            "UCAN East": "Atlanta",  # default, but facility overrides below
            "UCAN West": "Albuquerque",  # default, but facility overrides below
            "UK": "UK",
            "Spain": "Madrid",
            "APAC": "Japan",
        }
        facility = title_data.get("facility", "")
        # Use facility name for more precise mapping
        if "Albuquerque" in facility: hints["Albuquerque"] = hints.get("Albuquerque", 0) + 3
        elif "Canadian" in facility or "Toronto" in facility or "Pinewood Toronto" in facility or "Martini" in facility: hints["Vancouver"] = hints.get("Canada", 0) + 3
        elif "Cinespace Atlanta" in facility: hints["Atlanta"] = hints.get("Atlanta", 0) + 3
        elif "Brooklyn" in facility: hints["New York"] = hints.get("New York", 0) + 3
        elif "Shepperton" in facility or "Longcross" in facility or "Uxbridge" in facility: hints["UK"] = hints.get("UK", 0) + 3
        elif "Madrid" in facility: hints["Madrid"] = hints.get("Madrid", 0) + 3
        elif "Toho" in facility: hints["Japan"] = hints.get("Japan", 0) + 3
        elif "Raleigh" in facility or "Gower" in facility or "Bronson" in facility or "LA Center" in facility: hints["Los Angeles"] = hints.get("Los Angeles", 0) + 3
        elif pod in pod_to_region: hints[pod_to_region[pod]] = hints.get(pod_to_region[pod], 0) + 2

    # 3. Audience country / language from title lookup
    if title_data:
        country = title_data.get("audience_country", "")
        lang = title_data.get("language", "")
        if country in COUNTRY_TO_REGION and COUNTRY_TO_REGION[country]:
            region = COUNTRY_TO_REGION[country]
            hints[region] = hints.get(region, 0) + 2
        elif lang in LANGUAGE_TO_REGION:
            region = LANGUAGE_TO_REGION[lang]
            hints[region] = hints.get(region, 0) + 1

    return hints


def score_regions(results, relevant_regions, prod_type_key, franchise_info, buying_org, title_hints=None):
    """Score each region with weighted factors beyond just cost."""
    prod_type = PRODUCTION_TYPES.get(prod_type_key, PRODUCTION_TYPES["1hr Drama Series"])
    scores = {}

    valid_results = {k: v for k, v in results.items()
                     if k in relevant_regions and v["available"] > 0}

    if not valid_results:
        return {}

    # Normalize costs (0-1 scale, lower is better)
    costs = {k: v["cost_to_title_nflx_net"] for k, v in valid_results.items()}
    max_cost = max(costs.values()) if costs else 1
    min_cost = min(costs.values()) if costs else 0
    cost_range = max_cost - min_cost if max_cost != min_cost else 1

    has_franchise = franchise_info is not None
    has_historical = title_hints and any(v >= 3 for v in title_hints.values())  # facility-based hints are 3+

    for region, r in valid_results.items():
        score = 0
        reasons = []

        # Adjust weights: if we have franchise/historical data, weight that higher
        cost_weight = 25 if (has_franchise or has_historical) else 40
        franchise_weight = 35 if has_franchise else 0
        history_weight = 20 if has_historical else 0

        # 1. Cost — lower is better
        cost_score = 1 - ((r["cost_to_title_nflx_net"] - min_cost) / cost_range)
        score += cost_score * cost_weight
        if cost_score > 0.8:
            reasons.append("Lowest cost")

        # 2. Prior season / franchise loyalty (strongest signal when present)
        if franchise_info and franchise_info["region"] == region:
            score += franchise_weight
            reasons.append(f"Prior seasons shot here ({franchise_info['franchise']})")

        # 3. Historical facility match (from utilization data)
        if title_hints and region in title_hints:
            hint_val = title_hints[region]
            if hint_val >= 3:  # facility-based hint (strong)
                score += history_weight
                reasons.append(f"Historical: shot at this location")
            else:  # keyword hint (weaker)
                score += min(hint_val * 5, 10)
                reasons.append(f"Title suggests {region}")

        # 4. LA affinity for talent-heavy productions (10% weight)
        if region == "Los Angeles":
            la_bonus = prod_type["la_affinity"] * 10
            score += la_bonus
            if prod_type["la_affinity"] >= 0.7:
                reasons.append("Talent base & crew in LA")
        elif region in ("New York", "New Jersey"):
            score += prod_type["la_affinity"] * 5
        
        # 5. Tax incentive value (10% weight)
        if r["incentive_rate"] > 0:
            incentive_score = r["incentive_rate"] / 0.35
            score += min(incentive_score * 10, 10)
            if r["incentive_rate"] >= 0.25:
                reasons.append(f"{r['incentive_rate']:.0%} tax incentive")

        # 6. Stage availability (5% weight)
        avail_score = min(r["available"] / 10, 1)
        score += avail_score * 5
        if r["available"] >= 8:
            reasons.append(f"{r['available']} stages available")

        # 7. Crew cost advantage (5% weight)
        if r["crew_idx"] < 1.0:
            score += (1 - r["crew_idx"]) * 50
            reasons.append(f"Lower crew costs ({r['crew_idx']:.0%} of LA)")

        scores[region] = {
            "score": round(score, 1),
            "reasons": reasons,
            "cost_rank": cost_score,
        }

    return scores

# Real titles from Kragle + utilization data (exclude placeholders like "2031 TBD Film #4")
import re
_placeholder_re = re.compile(r'^20[2-4]\d\s')
REAL_TITLES = ["-- Enter custom title --"] + sorted(
    t for t in TITLE_LOOKUP.keys() if not _placeholder_re.match(t)
)

# Title-level historical data for known titles
TITLE_HISTORY = {
    "Stranger Things S05": {"stages": 12, "duration": 652, "pod": "UCAN East", "facility": "Cinespace Atlanta"},
    "Stranger Things S04": {"stages": 7, "duration": 490, "pod": "UCAN East", "facility": "Cinespace Atlanta"},
    "Bridgerton S04": {"stages": 7, "duration": 266, "pod": "UK", "facility": "Netflix Studios Uxbridge"},
    "Bridgerton S05": {"stages": 3, "duration": 455, "pod": "UK", "facility": "Netflix Studios Uxbridge"},
    "The Witcher S04": {"stages": 5, "duration": 577, "pod": "UK", "facility": "Shepperton Studios"},
    "The Witcher S05": {"stages": 5, "duration": 258, "pod": "UK", "facility": "Shepperton Studios"},
    "Avatar: The Last Airbender S02": {"stages": 6, "duration": 436, "pod": "UCAN West", "facility": "Canadian Motion Picture Park"},
    "The Sandman S02": {"stages": 8, "duration": 365, "pod": "UK", "facility": "Shepperton Studios"},
    "Black Mirror S07": {"stages": 8, "duration": 93, "pod": "UK", "facility": "Shepperton Studios"},
    "The Residence S01": {"stages": 11, "duration": 484, "pod": "Los Angeles", "facility": "Raleigh Studios"},
    "Rebel Moon": {"stages": 9, "duration": 304, "pod": "Los Angeles", "facility": "Sunset Gower Studios"},
    "Heart of Stone": {"stages": 10, "duration": 175, "pod": "UK", "facility": "Segro Enfield"},
    "Monster S01": {"stages": 8, "duration": 214, "pod": "Los Angeles", "facility": "Raleigh Studios"},
    "Back In Action": {"stages": 13, "duration": 118, "pod": "UK", "facility": "Cinespace Atlanta"},
    "Unfrosted": {"stages": 9, "duration": 142, "pod": "Los Angeles", "facility": "Raleigh Studios"},
    "Virgin River S06": {"stages": 5, "duration": 428, "pod": "UCAN West", "facility": "Canadian Motion Picture Park"},
    "Virgin River S07": {"stages": 4, "duration": 334, "pod": "UCAN West", "facility": "Canadian Motion Picture Park"},
    "The Boroughs S01": {"stages": 8, "duration": 204, "pod": "UCAN West", "facility": "Netflix Studios Albuquerque"},
    "Elite S07": {"stages": 5, "duration": 185, "pod": "Spain", "facility": "Madrid Content City"},
    "Squid Game S02": {"stages": 3, "duration": 55, "pod": "APAC", "facility": "Toho Studios"},
    "The Three Body Problem S01": {"stages": 10, "duration": 195, "pod": "UK", "facility": "Shepperton Studios"},
}

STAGES = [
    # Albuquerque
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 01", 18000, 1512),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 02", 18000, 1512),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 03", 24000, 2015),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 04", 24000, 2015),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 05", 18000, 1512),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 06", 18000, 1512),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 07", 24000, 2015),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 08", 24000, 2015),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 09", 20000, 1680),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 10", 20000, 1680),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 11", 18000, 1512),
    ("Netflix Studios Albuquerque", "Albuquerque", "Stage 12", 18000, 1512),
    # Brooklyn
    ("Netflix Studios Brooklyn", "New York", "333 Stage 1", 23809, 9122),
    ("Netflix Studios Brooklyn", "New York", "333 Stage 2", 14158, 5425),
    ("Netflix Studios Brooklyn", "New York", "333 Stage 3", 11174, 4282),
    ("Netflix Studios Brooklyn", "New York", "333 Stage 4", 9272, 3553),
    ("Netflix Studios Brooklyn", "New York", "333 Stage 5", 8676, 3324),
    ("Netflix Studios Brooklyn", "New York", "333 Stage 6", 10315, 3951),
    # New Jersey - Fort Monmouth (18 stages, rates TBD - estimated from NJ market)
    # Stage Type 1: ~15,000 usable sf (31,500 GSF)
    ("Fort Monmouth", "New Jersey", "Stage 01 (Type 1)", 15000, 3200),
    ("Fort Monmouth", "New Jersey", "Stage 02 (Type 1)", 15000, 3200),
    # Stage Type 2: ~20,000 usable sf (42,000 GSF)
    ("Fort Monmouth", "New Jersey", "Stage 03 (Type 2)", 20000, 4200),
    ("Fort Monmouth", "New Jersey", "Stage 04 (Type 2)", 20000, 4200),
    ("Fort Monmouth", "New Jersey", "Stage 05 (Type 2)", 20000, 4200),
    ("Fort Monmouth", "New Jersey", "Stage 06 (Type 2)", 20000, 4200),
    ("Fort Monmouth", "New Jersey", "Stage 07 (Type 2)", 20000, 4200),
    ("Fort Monmouth", "New Jersey", "Stage 08 (Type 2)", 20000, 4200),
    # Stage Type 3: ~25,000 usable sf (52,500 GSF)
    ("Fort Monmouth", "New Jersey", "Stage 09 (Type 3)", 25000, 5300),
    ("Fort Monmouth", "New Jersey", "Stage 10 (Type 3)", 25000, 5300),
    ("Fort Monmouth", "New Jersey", "Stage 11 (Type 3)", 25000, 5300),
    ("Fort Monmouth", "New Jersey", "Stage 12 (Type 3)", 25000, 5300),
    ("Fort Monmouth", "New Jersey", "Stage 13 (Type 3)", 25000, 5300),
    ("Fort Monmouth", "New Jersey", "Stage 14 (Type 3)", 25000, 5300),
    # Stage Type 4: ~30,000 usable sf (63,000 GSF)
    ("Fort Monmouth", "New Jersey", "Stage 15 (Type 4)", 30000, 6400),
    ("Fort Monmouth", "New Jersey", "Stage 16 (Type 4)", 30000, 6400),
    # Stage Type 5: ~40,000 usable sf (84,000 GSF)
    ("Fort Monmouth", "New Jersey", "Stage 17 (Type 5)", 40000, 8500),
    ("Fort Monmouth", "New Jersey", "Stage 18 (Type 5)", 40000, 8500),
    # LA - Sunset Gower
    ("Sunset Gower Studios", "Los Angeles", "Stage 01", 15084, 2731),
    ("Sunset Gower Studios", "Los Angeles", "Stage 02", 12538, 2270),
    ("Sunset Gower Studios", "Los Angeles", "Stage 03", 13658, 2498),
    ("Sunset Gower Studios", "Los Angeles", "Stage 04", 11679, 2142),
    ("Sunset Gower Studios", "Los Angeles", "Stage 05", 5720, 1036),
    ("Sunset Gower Studios", "Los Angeles", "Stage 07", 17558, 3208),
    ("Sunset Gower Studios", "Los Angeles", "Stage 08", 10916, 1977),
    ("Sunset Gower Studios", "Los Angeles", "Stage 09", 16275, 2946),
    ("Sunset Gower Studios", "Los Angeles", "Stage 12", 15983, 2960),
    ("Sunset Gower Studios", "Los Angeles", "Stage 14", 17029, 3083),
    ("Sunset Gower Studios", "Los Angeles", "Stage 15", 15272, 2819),
    ("Sunset Gower Studios", "Los Angeles", "Stage 16", 14144, 2624),
    # LA - Sunset Bronson
    ("Sunset Bronson Studios", "Los Angeles", "Stage 01", 18252, 3018),
    ("Sunset Bronson Studios", "Los Angeles", "Stage 03", 9509, 1580),
    ("Sunset Bronson Studios", "Los Angeles", "Stage 09", 22728, 3775),
    # LA - Raleigh
    ("Raleigh Studios", "Los Angeles", "Stage 01", 15480, 2872),
    ("Raleigh Studios", "Los Angeles", "Stage 02", 12114, 2248),
    ("Raleigh Studios", "Los Angeles", "Stage 03", 8992, 1669),
    ("Raleigh Studios", "Los Angeles", "Stage 05", 15364, 2852),
    ("Raleigh Studios", "Los Angeles", "Stage 07", 7151, 1328),
    ("Raleigh Studios", "Los Angeles", "Stage 08", 5923, 1100),
    ("Raleigh Studios", "Los Angeles", "Stage 10", 6599, 1225),
    ("Raleigh Studios", "Los Angeles", "Stage 11", 16610, 3378),
    ("Raleigh Studios", "Los Angeles", "Stage 12", 16607, 3378),
    ("Raleigh Studios", "Los Angeles", "Stage 14", 14632, 2715),
    # UK - Shepperton
    ("Shepperton Studios", "UK", "Stage 01", 14847, 3097),
    ("Shepperton Studios", "UK", "Stage 02", 14576, 3041),
    ("Shepperton Studios", "UK", "Stage 03", 14847, 3097),
    ("Shepperton Studios", "UK", "Stage 04", 24321, 5073),
    ("Shepperton Studios", "UK", "Stage 05", 24321, 5073),
    ("Shepperton Studios", "UK", "Stage 06", 29362, 6125),
    ("Shepperton Studios", "UK", "Stage 07", 29362, 6125),
    ("Shepperton Studios", "UK", "Stage 08", 40736, 8497),
    ("Shepperton Studios", "UK", "Stage A", 18000, 3498),
    ("Shepperton Studios", "UK", "Stage B", 12000, 2332),
    ("Shepperton Studios", "UK", "Stage C", 18000, 3498),
    ("Shepperton Studios", "UK", "Stage D", 12000, 2332),
    ("Shepperton Studios", "UK", "Stage G", 6768, 1315),
    ("Shepperton Studios", "UK", "Stage H", 30000, 5829),
    ("Shepperton Studios", "UK", "Stage J", 15000, 2915),
    ("Shepperton Studios", "UK", "Stage K", 12000, 2332),
    ("Shepperton Studios", "UK", "Stage L", 6664, 1295),
    ("Shepperton Studios", "UK", "Stage R", 10200, 1982),
    ("Shepperton Studios", "UK", "Stage S", 10000, 1943),
    ("Shepperton Studios", "UK", "Stage W", 10400, 2021),
    # UK - Longcross
    ("Netflix Studios Longcross", "UK", "Stage 01", 36900, 7116),
    ("Netflix Studios Longcross", "UK", "Stage 02", 17413, 3110),
    ("Netflix Studios Longcross", "UK", "Stage 03", 12028, 2182),
    ("Netflix Studios Longcross", "UK", "Stage 04", 19516, 3624),
    ("Netflix Studios Longcross", "UK", "Stage 05", 19516, 3624),
    # UK - Uxbridge
    ("Netflix Studios Uxbridge", "UK", "Stage 01", 28728, 3998),
    ("Netflix Studios Uxbridge", "UK", "Stage 02", 18557, 2583),
    # Atlanta - Cinespace
    ("Cinespace Atlanta", "Atlanta", "Stage 01", 15000, 1753),
    ("Cinespace Atlanta", "Atlanta", "Stage 02", 15000, 1753),
    ("Cinespace Atlanta", "Atlanta", "Stage 03", 11375, 1329),
    ("Cinespace Atlanta", "Atlanta", "Stage 04", 11375, 1329),
    ("Cinespace Atlanta", "Atlanta", "Stage 05", 13000, 1520),
    ("Cinespace Atlanta", "Atlanta", "Stage 07", 18500, 2163),
    ("Cinespace Atlanta", "Atlanta", "Stage 08", 18500, 2163),
    ("Cinespace Atlanta", "Atlanta", "Stage 10", 15000, 1753),
    ("Cinespace Atlanta", "Atlanta", "Stage 11", 15000, 1753),
    ("Cinespace Atlanta", "Atlanta", "Stage 12", 21350, 2496),
    ("Cinespace Atlanta", "Atlanta", "Stage 14", 21325, 2492),
    ("Cinespace Atlanta", "Atlanta", "Stage 15", 21325, 2492),
    # Atlanta - Martini
    ("Martini Studios", "Vancouver", "Stage 01", 11600, 1040),
    ("Martini Studios", "Vancouver", "Stage 02", 18000, 1615),
    ("Martini Studios", "Vancouver", "Stage 03", 15600, 1400),
    ("Martini Studios", "Vancouver", "Stage 04", 15600, 1400),
    ("Martini Studios", "Vancouver", "Stage 05", 15600, 1400),
    ("Martini Studios", "Vancouver", "Stage 06", 15600, 1400),
    ("Martini Studios", "Vancouver", "Stage 07", 23650, 2122),
    ("Martini Studios", "Vancouver", "Stage 08", 24950, 2238),
    # Canada
    ("Canadian Motion Picture Park", "Vancouver", "CMPP1 - Stage 01", 21200, 4734),
    ("Canadian Motion Picture Park", "Vancouver", "CMPP1 - Stage 02", 17000, 3796),
    ("Canadian Motion Picture Park", "Vancouver", "CMPP1 - Stage 03", 16900, 3774),
    ("Canadian Motion Picture Park", "Vancouver", "CMPP1 - Stage 04", 9184, 2051),
    ("Canadian Motion Picture Park", "Vancouver", "Pacific Studios - Stage 01", 36000, 8038),
    ("Canadian Motion Picture Park", "Vancouver", "Pacific Studios - Stage 02", 23000, 5136),
    # Madrid
    ("Madrid Content City", "Madrid", "Stage 01", 12375, 850),
    ("Madrid Content City", "Madrid", "Stage 02", 12375, 850),
    ("Madrid Content City", "Madrid", "Stage 03", 12375, 850),
    ("Madrid Content City", "Madrid", "Stage 04", 15280, 1111),
    ("Madrid Content City", "Madrid", "Stage 05", 15280, 1111),
    ("Madrid Content City", "Madrid", "Stage 06", 20350, 1567),
    ("Madrid Content City", "Madrid", "Stage 07", 7560, 549),
    ("Madrid Content City", "Madrid", "Stage 07 VFX", 7559, 548),
    ("Madrid Content City", "Madrid", "Stage 08", 15119, 1097),
    ("Madrid Content City", "Madrid", "Stage 09", 15119, 1097),
    ("Madrid Content City", "Madrid", "Stage 10", 15119, 1097),
    # Japan
    ("Toho Studios", "Japan", "Stage 07", 11429, 1800),
    ("Toho Studios", "Japan", "Stage 09", 19160, 2133),
    ("Toho Studios", "Japan", "Stage 10", 8514, 1500),
]

MARKET = {
    "Los Angeles":  {"third_party_rate": 0.18, "incentive": 0.00, "crew_idx": 1.00, "per_diem": 350, "travel": 0},
    "Albuquerque":  {"third_party_rate": 0.08, "incentive": 0.25, "crew_idx": 0.85, "per_diem": 200, "travel": 500},
    "Atlanta":      {"third_party_rate": 0.12, "incentive": 0.30, "crew_idx": 0.88, "per_diem": 225, "travel": 400},
    "New York":     {"third_party_rate": 0.38, "incentive": 0.30, "crew_idx": 1.10, "per_diem": 400, "travel": 350},
    "New Jersey":   {"third_party_rate": 0.25, "incentive": 0.35, "crew_idx": 1.05, "per_diem": 350, "travel": 300},
    "UK":           {"third_party_rate": 0.19, "incentive": 0.25, "crew_idx": 0.95, "per_diem": 300, "travel": 1200},
    "Vancouver":   {"third_party_rate": 0.22, "incentive": 0.25, "crew_idx": 0.90, "per_diem": 250, "travel": 600},
    "Madrid":       {"third_party_rate": 0.07, "incentive": 0.30, "crew_idx": 0.75, "per_diem": 200, "travel": 1000},
    "Japan":        {"third_party_rate": 0.15, "incentive": 0.00, "crew_idx": 1.05, "per_diem": 350, "travel": 1500},
    "Korea":        {"third_party_rate": 0.12, "incentive": 0.00, "crew_idx": 0.85, "per_diem": 250, "travel": 1400},
}

# ── Helper Functions ─────────────────────────────────────────────────────────

@st.cache_data
def get_stages_df():
    df = pd.DataFrame(STAGES, columns=["Facility", "Region", "Stage", "SqFt", "DailyRate"])
    df["WeeklyRate"] = df["DailyRate"] * 5
    df["MonthlyRate"] = df["DailyRate"] * 20
    return df


def get_relevant_regions(buying_org, buying_team):
    """Determine which regions to show based on buying org and team."""
    # Check team-level override first
    if buying_team in TEAM_LOCATION_OVERRIDES:
        return TEAM_LOCATION_OVERRIDES[buying_team]
    # Fall back to org-level routing
    if buying_org in LOCATION_ROUTING:
        return LOCATION_ROUTING[buying_org]
    # Default: all regions
    return list(MARKET.keys())


def get_prediction(buying_org, buying_team, title):
    """Get predicted stages/duration based on historical data."""
    # Check title-level history first
    if title in TITLE_HISTORY:
        h = TITLE_HISTORY[title]
        return {
            "stages": h["stages"],
            "duration_weeks": round(h["duration"] / 7),
            "sqft": 15000,
            "source": f"Based on {title} history ({h['facility']})",
        }
    # Fall back to pod prediction
    pod = ORG_TO_POD.get(buying_org, "Los Angeles")
    pred = POD_PREDICTIONS.get(pod, POD_PREDICTIONS["Los Angeles"])
    return {
        "stages": int(pred["median_stages"]),
        "duration_weeks": round(pred["avg_duration_days"] / 7),
        "sqft": int(pred["avg_sqft"]),
        "source": f"Based on {pod} pod avg ({pred['avg_stages']:.1f} stages, {pred['avg_duration_days']:.0f} days)",
    }


def calc_region(region, stages_df, num_stages, min_sqft, duration_weeks, crew_size,
                episodes, gross_budget, atl_pct):
    matching = stages_df[(stages_df["Region"] == region) & (stages_df["SqFt"] >= min_sqft)]
    market = MARKET.get(region, MARKET["Los Angeles"])

    available = len(matching) if len(matching) > 0 else 0
    avg_rate = matching["DailyRate"].mean() if available > 0 else 0

    weekly_cost = avg_rate * 5
    facilities = weekly_cost * duration_weeks * num_stages
    utilities = facilities * 0.088
    storage = facilities * 0.159
    office = facilities * 0.148
    total_facilities = facilities + utilities + storage + office

    avg_sqft = matching["SqFt"].mean() if available > 0 else min_sqft
    third_party_daily = avg_sqft * market["third_party_rate"]
    third_party_total = third_party_daily * 5 * duration_weeks * num_stages

    # ── Production Incentive ──
    # Higher ATL spend (talent-heavy) = more eligible spend in incentive regions like UK
    # ATL + stage costs are both eligible for incentives
    total_production_spend = gross_budget * episodes
    atl_spend = total_production_spend * atl_pct
    # Incentive on stage costs specifically
    incentive_on_nflx = total_facilities * market["incentive"]
    incentive_on_3p = third_party_total * market["incentive"]
    # Bonus: ATL incentive uplift (UK creative industry relief covers ATL)
    atl_incentive_uplift = atl_spend * market["incentive"]

    # ── NETFLIX STAGE: Net Neutral to Netflix ──
    # Production pays rate card → internal cost recovery → offsets fixed facility costs
    # Net impact to Netflix P&L = $0 (internal transfer)
    cost_to_title_nflx = total_facilities
    cost_to_title_nflx_net = total_facilities - incentive_on_nflx
    nflx_net_impact = 0  # NET NEUTRAL

    # ── 3RD PARTY: Net Incremental Cost to Netflix ──
    # Money leaves Netflix to external landlord
    # PLUS Netflix still pays fixed costs on empty stages (overhang / vacancy cost)
    cost_to_title_3p = third_party_total
    cost_to_title_3p_net = third_party_total - incentive_on_3p
    overhang = total_facilities  # lost cost recovery from vacant Netflix stages
    nflx_incremental = third_party_total + overhang  # true Netflix cost

    # Travel
    travel = market["travel"] * crew_size * 2
    per_diem = market["per_diem"] * crew_size * duration_weeks * 5
    travel_total = travel + per_diem

    # ── All-In Impact to Netflix ──
    all_in_nflx = travel_total  # stage is net neutral, only travel is real cost
    all_in_3p = nflx_incremental + travel_total - incentive_on_3p

    per_episode = total_facilities / episodes if episodes > 0 else 0
    pct_budget = per_episode / gross_budget if gross_budget > 0 else 0

    return {
        "region": region, "available": available, "avg_rate": avg_rate,
        "facilities": facilities, "utilities": utilities, "storage": storage, "office": office,
        "total_facilities": total_facilities,
        "cost_to_title_nflx": cost_to_title_nflx,
        "cost_to_title_nflx_net": cost_to_title_nflx_net,
        "cost_to_title_3p": cost_to_title_3p,
        "cost_to_title_3p_net": cost_to_title_3p_net,
        "incentive_rate": market["incentive"],
        "incentive_nflx": incentive_on_nflx,
        "incentive_3p": incentive_on_3p,
        "atl_incentive_uplift": atl_incentive_uplift,
        "nflx_net_impact": nflx_net_impact,
        "overhang": overhang,
        "nflx_incremental": nflx_incremental,
        "travel_total": travel_total,
        "all_in_nflx": all_in_nflx,
        "all_in_3p": all_in_3p,
        "incremental_vs_nflx": all_in_3p - all_in_nflx,
        "per_episode": per_episode, "pct_budget": pct_budget,
        "crew_idx": market["crew_idx"],
    }


def fmt(val):
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:,.1f}M"
    elif abs(val) >= 1_000:
        return f"${val / 1_000:,.0f}K"
    return f"${val:,.0f}"


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size: 2.5rem; font-weight: 900; color: #E50914;">N</div>
        <div style="font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.15em; margin-top: -4px;">
            Stage Calculator
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Title dropdown with real titles
    selected_title = st.selectbox("Production Title", options=REAL_TITLES, index=0)
    if selected_title == "-- Enter custom title --":
        title = st.text_input("Enter Title", placeholder="e.g. New Project S01")
    else:
        title = selected_title

    # Auto-populate from title lookup
    title_data = TITLE_LOOKUP.get(title, {}) if title and title != "-- Enter custom title --" else {}

    if title_data:
        # 1. Slate Manager buying org (highest priority)
        sm_org = title_data.get("buying_org_sm", "")
        pod = title_data.get("pod", "")
        facility = title_data.get("facility", "")
        ac = title_data.get("audience_country", "US")
        lang = title_data.get("language", "en")

        if sm_org and sm_org in BUYING_ORGS:
            default_org = sm_org
        # 2. Historical pod/facility (second priority)
        elif pod == "APAC" or "Toho" in facility or "K-ART" in facility or "YCDSMC" in facility or "Samsung" in facility:
            default_org = "APAC"
        elif pod == "Spain" or "Madrid" in facility:
            default_org = "EMEA"
        elif pod == "UK" or "Shepperton" in facility or "Longcross" in facility or "Uxbridge" in facility:
            default_org = "EMEA"
        # 3. Content type / audience country (fallback)
        elif title_data.get("is_animated"):
            default_org = "Animation Series"
        elif title_data.get("is_unscripted") or title_data.get("is_live_event"):
            default_org = "Nonfiction Series"
        elif title_data.get("content_type") == "Features":
            default_org = "Film"
        elif ac in ("JP", "KR", "TH", "PH", "ID", "AU", "NZ", "IN"):
            default_org = "APAC"
        elif ac in ("MX", "BR", "AR", "CO", "CL"):
            default_org = "LatAm"
        elif ac in ("ES", "FR", "DE", "IT"):
            default_org = "EMEA"
        elif ac == "GB":
            default_org = "EMEA"
        elif ac in ("US", "CA") or lang.startswith("en"):
            default_org = "UCAN Scripted Series"
        else:
            default_org = "UCAN Scripted Series"

        # Show Slate Manager / historical info
        sm_loc = title_data.get("shoot_location_sm", "")
        sm_phase = title_data.get("phase", "")
        if sm_loc or sm_phase or facility:
            intel_parts = []
            if sm_org:
                intel_parts.append(f"<strong>Org:</strong> {sm_org}")
            if sm_loc:
                intel_parts.append(f"<strong>Shoot:</strong> {sm_loc}")
            if facility:
                intel_parts.append(f"<strong>Historical:</strong> {facility} ({pod})")
            if sm_phase:
                intel_parts.append(f"<strong>Phase:</strong> {sm_phase}")
            st.markdown('<div class="title-intel" style="background:#ffffff; border:2px solid #8b5cf6; border-radius:8px; padding:12px; margin:8px 0;"><div class="ti-header" style="font-weight:600; font-size:0.9rem;">📋 Title Intel</div><div style="font-size:0.88rem; line-height:1.7; margin-top:4px;">' + "<br>".join(intel_parts) + '</div></div>', unsafe_allow_html=True)

        org_idx = list(BUYING_ORGS.keys()).index(default_org) + 1 if default_org in BUYING_ORGS else 0
    else:
        org_idx = 0

    buying_org = st.selectbox("Buying Org", options=[""] + list(BUYING_ORGS.keys()), index=org_idx)
    if buying_org:
        teams = BUYING_ORGS[buying_org]
        # Auto-select sub-buying team from Slate Manager if available
        sm_team = title_data.get("buying_team_sm", "") if title_data else ""
        team_idx = 0
        if sm_team:
            # Exact match first
            for i, t in enumerate(teams):
                if sm_team.lower() == t.lower():
                    team_idx = i
                    break
            else:
                # Word overlap match — find best match by shared words
                sm_words = set(sm_team.lower().split())
                best_overlap = 0
                for i, t in enumerate(teams):
                    t_words = set(t.lower().split())
                    overlap = len(sm_words & t_words)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        team_idx = i
        buying_team = st.selectbox("Buying Team", options=teams, index=team_idx)
    else:
        buying_team = st.selectbox("Buying Team", options=["Select Buying Org first"], disabled=True)
        buying_team = ""

    # Get prediction for smart defaults — use historical stage data if available
    prediction = None
    if title_data and "stages" in title_data:
        prediction = {
            "stages": title_data["stages"],
            "duration_weeks": max(1, round(title_data.get("duration_days", 140) / 7)),
            "sqft": title_data.get("avg_sqft", 15000),
            "source": f"Historical: {title_data['stages']} stages, {title_data.get('total_sqft',0):,} total sqft at {title_data.get('facility', 'N/A')}",
        }
    elif buying_org:
        prediction = get_prediction(buying_org, buying_team, title)

    st.markdown("---")

    # Production type (auto-detected from buying team, can override)
    auto_prod_type = get_production_type(buying_org, buying_team) if buying_org else "1hr Drama Series"
    prod_type_key = st.selectbox("Production Type", options=list(PRODUCTION_TYPES.keys()),
                                 index=list(PRODUCTION_TYPES.keys()).index(auto_prod_type))
    prod_type_info = PRODUCTION_TYPES[prod_type_key]

    # Detect franchise / prior season
    franchise_info = detect_franchise(title)

    if not prod_type_info["needs_stages"]:
        st.markdown(f"""
        <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div style="font-weight: 600; color: #92400e; font-size: 0.85rem;">⚠️ No Stage Needed</div>
            <div style="color: #78350f; font-size: 0.8rem;">{prod_type_info['notes']}</div>
        </div>
        """, unsafe_allow_html=True)

    if franchise_info:
        st.markdown(f"""
        <div class="returning-series" style="background: #ffffff; border: 2px solid #8b5cf6; border-radius: 8px; padding: 12px; margin: 8px 0;">
            <div class="rs-header" style="font-weight: 700; font-size: 0.9rem;">🔄 Returning Series</div>
            <div style="font-size: 0.88rem; margin-top: 4px;">
                {franchise_info['franchise']} previously shot at<br>
                <strong>{franchise_info['facility']}</strong> ({franchise_info['region']})
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if prediction:
        st.markdown(f"""
        <div class="predict-card">
            <h3>📊 Predicted Footprint</h3>
            <div class="pred-val">
                🎬 <strong>{prediction['stages']}</strong> stages<br>
                📅 <strong>{prediction['duration_weeks']}</strong> weeks<br>
                📐 <strong>{prediction['sqft']:,}</strong> sq ft<br>
                <span style="font-size:0.85rem; color:#6b7280; margin-top:4px; display:block;">{prediction['source']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='color:#888; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;'>Production Parameters</div>", unsafe_allow_html=True)

    default_stages = prediction["stages"] if prediction else (title_data.get("stages", 2) if title_data else 2)
    default_sqft = prediction["sqft"] if prediction else (title_data.get("avg_sqft", 15000) if title_data else 15000)
    default_duration = prediction["duration_weeks"] if prediction else 20

    num_stages = st.slider("Number of Stages", 1, 15, min(default_stages, 15))
    min_sqft = st.slider("Min Stage Size (sq ft)", 5000, 40000, min(default_sqft, 40000), step=1000)
    duration = st.slider("Duration (weeks)", 4, 104, min(default_duration, 104))
    crew_size = st.slider("Crew Size", 25, 200, 75)
    default_eps = title_data.get("episodes", 5) if title_data else 5
    default_eps = max(1, min(50, int(default_eps))) if default_eps else 5
    default_budget = int(title_data.get("gross_direct_cost_usd", 0) / max(default_eps, 1)) if title_data and title_data.get("gross_direct_cost_usd", 0) > 0 else 9000000
    default_budget = max(100000, min(100000000, default_budget))
    
    episodes = st.number_input("Number of Episodes", min_value=1, max_value=50, value=default_eps)
    gross_budget = st.number_input("Gross Budget / Episode ($)", min_value=100000, max_value=100000000,
                                   value=default_budget, step=500000, format="%d")
    # Auto-estimate ATL% based on content type
    default_atl = 35
    if title_data:
        cost = title_data.get("total_cost_usd", 0)
        eps = max(1, title_data.get("episodes", 1) or 1)
        per_ep = cost / eps if cost > 0 else 0
        if per_ep > 20000000: default_atl = 50  # big budget = high talent
        elif per_ep > 10000000: default_atl = 40
        elif title_data.get("is_unscripted"): default_atl = 15
        elif title_data.get("is_animated"): default_atl = 20
    atl_pct = st.slider("Above the Line % of Budget", 0, 80, default_atl, step=5,
                        help="Higher ATL = more eligible spend for incentives (UK/NJ creative tax relief covers ATL)") / 100.0


# ── Main Content ─────────────────────────────────────────────────────────────

# Banner
subtitle_parts = []
if title and title != "-- Enter custom title --":
    subtitle_parts.append(f"📋 {title}")
if buying_org:
    subtitle_parts.append(buying_org)
if buying_team:
    subtitle_parts.append(buying_team)

st.markdown(f"""
<div style="background:#fef3c7; border:2px solid #f59e0b; border-radius:8px; padding:10px 16px; margin-bottom:10px; text-align:center;">
    <span style="font-size:1rem; font-weight:700; color:#92400e;">⚠️ CONCEPT ONLY — NOT FOR PRODUCTION USE</span><br>
    <span style="font-size:0.88rem; color:#78350f;">This tool is a proof of concept for internal discussion purposes only. Do not use for budgeting or decision-making.</span>
</div>
<div class="top-banner" style="display:flex; align-items:center; justify-content:space-between;">
    <div>
        <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:0.15em; color:rgba(255,255,255,0.7); margin-bottom:2px;">Netflix Studios</div>
        <h1 style="margin:0;">Stage Cost Estimator</h1>
        <p style="margin:4px 0 0 0;">{' · '.join(subtitle_parts) if subtitle_parts else 'Optimize stage allocation and understand financial impact'}</p>
    </div>
    <div style="text-align:right;">
        <div style="font-size:3rem; font-weight:900; color:rgba(255,255,255,0.2); line-height:1;">N</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fef3c7; border-left:3px solid #f59e0b; padding:12px 16px; border-radius:0 8px 8px 0; font-size:0.9rem; color:#92400e; margin-bottom:8px; line-height:1.6;">
    <strong>⚠️ Disclaimer:</strong> Stage costs shown are high-level estimates and are not intended to be used for budgeting purposes.
    Please reach out to <strong>Production Planning</strong> for formal quotes and stage availability.
</div>
<div class="rate-note">
    <strong>Rate Card Philosophy:</strong> Netflix rate card is set at open market rates.
    Stage costs are charged to the title and capitalized per GAAP.
    Unallocated costs (vacancies/discounts) become Studio Costs allocated to buying teams.
    Discounts are generally discouraged — see Rate Card Philosophy Refresh.
    Using a Netflix stage is <strong>net neutral</strong> to Netflix (internal cost recovery).
    Using a 3rd party stage is <strong>incremental cost</strong> (money leaves Netflix + vacant stage overhang).
</div>
""", unsafe_allow_html=True)

# Determine which regions to show
if buying_org:
    relevant_regions = get_relevant_regions(buying_org, buying_team)
else:
    # Default: show UCAN regions when no org selected (exclude Madrid/Japan)
    relevant_regions = ["Los Angeles", "Albuquerque", "Atlanta", "New York", "New Jersey", "UK", "Vancouver"]

all_regions = list(MARKET.keys())

# Calculate all regions
stages_df = get_stages_df()
results = {}
for region in all_regions:
    results[region] = calc_region(region, stages_df, num_stages, min_sqft, duration, crew_size, episodes, gross_budget, atl_pct)

# Find best/worst using weighted scoring
valid = {k: v for k, v in results.items() if v["available"] > 0 and k in relevant_regions}
title_hints = get_title_location_hints(title)
region_scores = score_regions(results, relevant_regions, prod_type_key, franchise_info, buying_org, title_hints)
if valid and region_scores:
    best_region = max(region_scores, key=lambda r: region_scores[r]["score"])
    worst_region = min(region_scores, key=lambda r: region_scores[r]["score"])
else:
    best_region = worst_region = None

# Override with historical location if title previously shot somewhere
historical_region = None
historical_facility = None
if title_data and title_data.get("facility"):
    fac = title_data["facility"]
    fac_to_region = {
        "Netflix Studios Albuquerque": "Albuquerque",
        "Raleigh Studios": "Los Angeles", "Sunset Gower Studios": "Los Angeles",
        "Sunset Bronson Studios": "Los Angeles",
        "Cinespace Atlanta": "Atlanta",
        "Netflix Studios Brooklyn": "New York",
        "Shepperton Studios": "UK", "Netflix Studios Longcross": "UK", "Netflix Studios Uxbridge": "UK",
        "Canadian Motion Picture Park": "Vancouver", "Martini Studios": "Vancouver",
        "Pinewood Toronto Studios": "Vancouver", "Cinespace Toronto Studios": "Vancouver",
        "Madrid Content City": "Madrid",
        "Toho Studios": "Japan",
        "K-ART Studio": "Korea", "zzOLD - YCDSMC Studios": "Korea",
    }
    for fac_name, reg in fac_to_region.items():
        if fac_name in fac:
            historical_region = reg
            historical_facility = fac
            break

if historical_region and valid:
    if historical_region not in valid and historical_region in results and results[historical_region]["available"] > 0:
        valid[historical_region] = results[historical_region]
        region_scores[historical_region] = {"score": 100, "reasons": ["Title previously shot here"]}
    if historical_region in valid:
        best_region = historical_region

# Show "no stage needed" banner for non-stage production types
if not prod_type_info["needs_stages"]:
    st.markdown(f"""
    <div style="background: #fef3c7; border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; margin-bottom: 1.5rem; text-align: center;">
        <div style="font-size: 1.3rem; font-weight: 700; color: #92400e;">⚠️ {prod_type_key}: Stage Not Typically Required</div>
        <div style="color: #78350f; font-size: 0.9rem; margin-top: 4px;">{prod_type_info['notes']}</div>
        <div style="color: #78350f; font-size: 0.85rem; margin-top: 8px;">
            The comparison below is shown for reference only. This production type typically does not need dedicated stage space.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Map: Recommended Location ────────────────────────────────────────────────
FACILITY_COORDS = {
    "Los Angeles": {"lat": 34.09, "lon": -118.33, "fac": "Raleigh · Sunset Bronson · Sunset Gower"},
    "Albuquerque": {"lat": 35.08, "lon": -106.65, "fac": "Netflix Studios Albuquerque (Owned)"},
    "Atlanta": {"lat": 33.75, "lon": -84.39, "fac": "Cinespace Atlanta"},
    "New York": {"lat": 40.68, "lon": -73.94, "fac": "Netflix Studios Brooklyn"},
    "New Jersey": {"lat": 40.32, "lon": -74.05, "fac": "Fort Monmouth"},
    "UK": {"lat": 51.41, "lon": -0.56, "fac": "Shepperton · Longcross · Uxbridge"},
    "Vancouver": {"lat": 49.28, "lon": -123.12, "fac": "CMPP · Martini Film Studios"},
    "Madrid": {"lat": 40.42, "lon": -3.70, "fac": "Madrid Content City"},
    "Japan": {"lat": 35.68, "lon": 139.65, "fac": "Toho Studios"},
    "Korea": {"lat": 37.55, "lon": 127.00, "fac": "K-ART · YCDSMC · Samsung Studios"},
}

if valid and best_region:
    fig_map = go.Figure()

    for region, coords in FACILITY_COORDS.items():
        is_best = (region == best_region)
        is_relevant = region in relevant_regions
        sc = region_scores.get(region, {})
        r_data = results.get(region, {})

        if is_best:
            dot_color, dot_size, label_color, label_font = "#E50914", 22, "#E50914", "Arial Black"
        else:
            dot_color, dot_size, label_color, label_font = "#64748b", 10, "#475569", "Arial"

        hover = f"<b>{'RECOMMENDED — ' if is_best else ''}{region}</b><br>{coords['fac']}"
        if sc:
            hover += f"<br>Score: {sc.get('score', 0):.0f}/100"
        if r_data and r_data.get("available", 0) > 0:
            hover += f"<br>Cost: {fmt(r_data['cost_to_title_nflx_net'])}<br>Stages: {r_data['available']}"

        fig_map.add_trace(go.Scattergeo(
            lat=[coords["lat"]], lon=[coords["lon"]],
            text=[hover], hoverinfo="text",
            marker=dict(size=dot_size, color=dot_color, opacity=0.9 if is_best else 0.7,
                       line=dict(width=3 if is_best else 1.5, color="#ffffff")),
            showlegend=False,
        ))

        label = region.upper()
        # Offset labels to avoid overlaps
        label_offsets = {
            "Los Angeles": (3, -2),
            "Albuquerque": (-3, 0),
            "Atlanta": (3, 3),
            "New York": (3, 5),
            "New Jersey": (-3, 5),
            "UK": (4, 0),
            "Vancouver": (3, 0),
            "Madrid": (-3, -3),
            "Japan": (3, 3),
            "Korea": (-3, -3),
        }
        lat_off, lon_off = label_offsets.get(region, (3, 0))
        fig_map.add_trace(go.Scattergeo(
            lat=[coords["lat"] + lat_off], lon=[coords["lon"] + lon_off],
            text=[label], mode="text",
            textfont=dict(size=14 if is_best else 10, color=label_color, family=label_font),
            hoverinfo="skip", showlegend=False,
        ))

    fig_map.update_geos(
        showcountries=True, countrycolor="#e0e0e0",
        showland=True, landcolor="#eaeaea",
        showocean=True, oceancolor="#ffffff",
        showlakes=False,
        showcoastlines=True, coastlinecolor="#d0d0d0",
        showframe=False,
        projection_type="natural earth",
        lataxis_range=[20, 62], lonaxis_range=[-130, 150],
    )
    fig_map.update_layout(
        margin=dict(t=25, b=0, l=0, r=0), height=300,
        paper_bgcolor="white", geo=dict(bgcolor="white"),
        title=dict(text="STAGE MLA PORTFOLIO", font=dict(size=11, color="#999", family="Arial"), x=0.5, y=0.97),
    )
    st.plotly_chart(fig_map, use_container_width=True)


# ── Section 3: Recommendation ───────────────────────────────────────────────
st.markdown('<div class="section-header">Recommendation</div>', unsafe_allow_html=True)

if valid and best_region:
    sorted_regions = sorted(region_scores, key=lambda r: region_scores[r]["score"], reverse=True)

    # Allow user to override the recommendation
    rec_header_col1, rec_header_col2 = st.columns([3, 1])
    with rec_header_col1:
        st.markdown(f'<div class="section-subheader">Auto-recommended: <strong>{best_region}</strong> (score {region_scores[best_region]["score"]:.0f}/100). Override below if needed.</div>', unsafe_allow_html=True)
    with rec_header_col2:
        override_options = ["Auto (highest score)"] + sorted_regions
        override_choice = st.selectbox("Override Location", options=override_options, index=0, label_visibility="collapsed")

    if override_choice != "Auto (highest score)":
        best_region = override_choice



    best = results[best_region]
    runner_up_candidates = [r for r in sorted_regions if r != best_region]
    runner_up = runner_up_candidates[0] if runner_up_candidates else None
    third_place = runner_up_candidates[1] if len(runner_up_candidates) > 1 else None

    rec_col1, rec_col2, rec_col3 = st.columns([2, 2, 3])

    with rec_col1:
        reasons_html = "".join(f"<div>✓ {r}</div>" for r in region_scores[best_region].get("reasons", []))
        # Get real facility names for the recommended region
        region_facility_names = {
            "Los Angeles": "Raleigh Studios, Sunset Bronson Studios, or Sunset Gower Studios",
            "Albuquerque": "Netflix Studios Albuquerque",
            "Atlanta": "Cinespace Atlanta",
            "New York": "Netflix Studios Brooklyn",
            "New Jersey": "Fort Monmouth",
            "UK": "Shepperton Studios, Netflix Studios Longcross, or Netflix Studios Uxbridge",
            "Vancouver": "Canadian Motion Picture Park or Martini Film Studios",
            "Madrid": "Madrid Content City",
            "Japan": "Toho Studios",
            "Korea": "K-ART Studio or YCDSMC Studios",
        }
        facility_name = region_facility_names.get(best_region, best_region)
        savings_amt = best["incremental_vs_nflx"]
        st.markdown(f"""
        <div class="rec-card" style="padding:16px 20px; min-height:280px;">
            <div style="font-size:0.88rem; color:#15803d; text-transform:uppercase; letter-spacing:0.05em;">Recommended</div>
            <div style="font-size:1.8rem; font-weight:800; color:#166534; margin:2px 0 8px 0;">{best_region}</div>
            <div style="font-size:0.9rem; color:#166534; font-weight:600; line-height:1.5; margin-bottom:8px;">
                {"📍 This title previously shot at " + historical_facility + ". " if historical_region == best_region and historical_facility else ""}Netflix saves {fmt(savings_amt)} if this title shoots at {facility_name} instead of a 3rd party stage.
            </div>
            <div style="font-size:0.85rem; color:#4b5563; line-height:1.6;">
                <strong>{fmt(best['cost_to_title_nflx_net'])}</strong> net to title · <strong>{best['pct_budget']:.1%}</strong> of budget<br>
                <span style="color:#16a34a; font-weight:600;">$0 impact to Netflix</span> · {best['available']} stages · {best['incentive_rate']:.0%} incentive
            </div>
            <div style="font-size:0.88rem; color:#4b5563; margin-top:8px; line-height:1.5;">{reasons_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with rec_col2:
        col2_html = ""
        if runner_up:
            ru = results[runner_up]
            ru_reasons = "".join(f"<div>✓ {r}</div>" for r in region_scores.get(runner_up, {}).get("reasons", [])[:2])
            col2_html += f"""
                <div style="margin-bottom:8px;">
                    <div style="font-size:0.85rem; color:#888; text-transform:uppercase; letter-spacing:0.05em;">Runner-Up</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#1a1a1a; margin:2px 0 8px 0;">{runner_up}</div>
                    <div style="font-size:0.9rem; color:#4b5563; line-height:1.6;">
                        <strong>{fmt(ru['cost_to_title_nflx_net'])}</strong> net to title<br>
                        Score: {region_scores.get(runner_up, {}).get('score', 0):.0f}/100 · {ru['available']} stages
                    </div>
                    <div style="font-size:0.85rem; color:#6b7280; margin-top:6px; line-height:1.4;">{ru_reasons}</div>
                </div>"""

        if third_place:
            tp = results[third_place]
            col2_html += f"""
                <div style="border-top:1px solid #e5e7eb; padding-top:10px; margin-top:4px;">
                    <div style="font-size:0.85rem; color:#888; text-transform:uppercase;">3rd Option</div>
                    <div style="font-size:1rem; font-weight:600; color:#1a1a1a;">{third_place}</div>
                    <div style="font-size:0.88rem; color:#6b7280;">
                        {fmt(tp['cost_to_title_nflx_net'])} · Score: {region_scores.get(third_place, {}).get('score', 0):.0f}/100
                    </div>
                </div>"""

        full_html = '<div style="background:#f8f9fa; border:1px solid #e5e7eb; border-radius:12px; padding:16px 20px; min-height:280px; box-sizing:border-box;">' + col2_html + '</div>'
        st.markdown(full_html, unsafe_allow_html=True)

    with rec_col3:
        st.markdown(f"""
        <div style="background:#f8f9fa; border:1px solid #e5e7eb; border-radius:12px; padding:16px 20px; min-height:280px; box-sizing:border-box;">
            <div style="font-size:0.85rem; color:#888; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">Key Metrics</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div>
                    <div style="font-size:0.85rem; color:#888;">Net Cost to Title</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#1a1a1a;">{fmt(best['cost_to_title_nflx_net'])}</div>
                </div>
                <div>
                    <div style="font-size:0.85rem; color:#888;">Netflix Impact</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#16a34a;">$0</div>
                    <div style="font-size:0.85rem; color:#16a34a;">Net Neutral</div>
                </div>
                <div>
                    <div style="font-size:0.85rem; color:#888;">Per Episode</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#1a1a1a;">{fmt(best['per_episode'])}</div>
                </div>
                <div>
                    <div style="font-size:0.85rem; color:#888;">If 3rd Party Instead</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#dc2626;">+{fmt(best['incremental_vs_nflx'])}</div>
                    <div style="font-size:0.85rem; color:#dc2626;">Incremental</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)



# ── Section 2: Financial Impact — Dynamic Location Detail ────────────────────
st.markdown('<div class="section-header">Financial Impact — Location Deep Dive</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subheader">Select a location to see detailed financial breakdown aligned to production top sheet</div>', unsafe_allow_html=True)

# Location selector tabs
available_regions = [r for r in relevant_regions if results[r]["available"] > 0]
if available_regions:
    selected_loc = st.radio("Select Location", available_regions, horizontal=True,
                            index=available_regions.index(best_region) if best_region in available_regions else 0)

    # Facility selector — drill down to specific Netflix facility within the region
    region_facilities = stages_df[stages_df["Region"] == selected_loc]["Facility"].unique().tolist()
    if len(region_facilities) > 1:
        loc_col1, loc_col2 = st.columns([1, 3])
        with loc_col1:
            selected_facility = st.selectbox(
                "Netflix Facility",
                options=["All Facilities"] + sorted(region_facilities),
                help="Filter to a specific Netflix facility within this region"
            )
        if selected_facility != "All Facilities":
            facility_stages = stages_df[(stages_df["Facility"] == selected_facility) & (stages_df["SqFt"] >= min_sqft)]
            if len(facility_stages) > 0:
                with loc_col2:
                    st.markdown(f"""
                    <div style="background:#eff6ff; border-radius:8px; padding:10px 16px; margin-top:24px; font-size:0.9rem; color:#1e40af;">
                        <strong>{selected_facility}</strong> — {len(facility_stages)} stages ≥ {min_sqft:,} sqft · 
                        Avg rate: ${facility_stages['DailyRate'].mean():,.0f}/day · 
                        Range: {facility_stages['SqFt'].min():,}–{facility_stages['SqFt'].max():,} sqft
                    </div>
                    """, unsafe_allow_html=True)
    else:
        selected_facility = region_facilities[0] if region_facilities else "All Facilities"

    r = results[selected_loc]
    rs = region_scores.get(selected_loc, {})

    # ── Big savings callout ──
    savings_amt = r["incremental_vs_nflx"]
    st.markdown(f"""
    <div style="display:flex; gap:16px; margin-bottom:16px;">
        <div style="flex:1; background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:2px solid #22c55e; border-radius:12px; padding:20px; text-align:center;">
            <div style="font-size:0.88rem; color:#15803d; text-transform:uppercase; letter-spacing:0.08em; font-weight:600;">Netflix Stage</div>
            <div style="font-size:2.2rem; font-weight:800; color:#166534;">{fmt(r['cost_to_title_nflx_net'])}</div>
            <div style="font-size:0.85rem; color:#15803d; font-weight:600;">Cost to Title</div>
            <div style="font-size:1.4rem; font-weight:800; color:#166534; margin-top:8px;">$0 to Netflix</div>
            <div style="font-size:0.88rem; color:#4b5563;">Internal transfer · Net neutral to P&L</div>
        </div>
        <div style="flex:0.5; display:flex; align-items:center; justify-content:center;">
            <div style="text-align:center; padding:8px;">
                <div style="font-size:0.9rem; color:#888; text-transform:uppercase; letter-spacing:0.1em;">Netflix saves</div>
                <div style="font-size:2.8rem; font-weight:900; color:#E50914; line-height:1.1;">{fmt(savings_amt)}</div>
                <div style="font-size:0.85rem; color:#6b7280; margin-top:4px;">by using MLA stage<br>vs 3rd party</div>
                <div style="margin-top:10px; font-size:1.2rem;">→</div>
            </div>
        </div>
        <div style="flex:1; background:linear-gradient(135deg,#fff5f5,#fee2e2); border:2px solid #fca5a5; border-radius:12px; padding:20px; text-align:center;">
            <div style="font-size:0.85rem; color:#991b1b; text-transform:uppercase; letter-spacing:0.1em; font-weight:600;">⚠ 3rd Party Stage</div>
            <div style="font-size:2.2rem; font-weight:800; color:#dc2626; margin-top:4px;">+{fmt(savings_amt)}</div>
            <div style="font-size:0.85rem; color:#991b1b; font-weight:600;">Incremental Cost to Netflix</div>
            <div style="font-size:0.9rem; color:#6b7280; margin-top:4px; line-height:1.4;">3rd party lease paid externally<br>+ Netflix stage sits vacant (overhang)</div>
            <div style="border-top:2px solid #fca5a5; margin:10px 0; padding-top:10px;">
                <div style="font-size:1rem; color:#991b1b;">{fmt(r['cost_to_title_3p_net'])}</div>
                <div style="font-size:0.9rem; color:#6b7280;">cost to title</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics right below savings
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Score", f"{rs.get('score', 0):.0f} / 100", "✓ Recommended" if selected_loc == best_region else "")
    with m2:
        st.metric("Per Episode", fmt(r["per_episode"]))
    with m3:
        st.metric("% of Gross Budget", f"{r['pct_budget']:.1%}")
    with m4:
        st.metric("Tax Incentive", f"{r['incentive_rate']:.0%}")
    with m5:
        st.metric("Crew Cost Index", f"{r['crew_idx']:.2f}x vs LA")

    # ── Breakdown details in expander ──
    st.markdown('<div class="section-subheader">📊 Detailed Cost Breakdown</div>', unsafe_allow_html=True)
if True:
        col_nflx, col_3p = st.columns(2)

        with col_nflx:
            st.markdown("""
            <div style="font-weight:700; color:#15803d; font-size:0.9rem; margin-bottom:8px;">🏢 Netflix Stage Breakdown</div>
            """, unsafe_allow_html=True)

            nflx_data = {
                "Line Item": [
                    "Stage Rental (Facilities)",
                    "Utilities (8.8%)",
                    "Storage (15.9%)",
                    "Office Space (14.8%)",
                    "TOTAL STAGES/FACILITIES",
                    "Production Incentive",
                    "NET COST TO TITLE",
                    "",
                    "Travel (round trip crew)",
                    "Per Diem",
                    "TOTAL TRAVEL",
                    "",
                    "ATL Incentive Uplift",
                    "",
                    "IMPACT TO NETFLIX: $0",
                ],
                "Amount": [
                    f"${r['facilities']:,.0f}",
                    f"${r['utilities']:,.0f}",
                    f"${r['storage']:,.0f}",
                    f"${r['office']:,.0f}",
                    f"${r['total_facilities']:,.0f}",
                    f"-${r['incentive_nflx']:,.0f}",
                    f"${r['cost_to_title_nflx_net']:,.0f}",
                    "",
                    f"${r['travel_total'] - (MARKET[selected_loc]['per_diem'] * crew_size * duration * 5):,.0f}",
                    f"${MARKET[selected_loc]['per_diem'] * crew_size * duration * 5:,.0f}",
                    f"${r['travel_total']:,.0f}",
                    "",
                    f"${r['atl_incentive_uplift']:,.0f}",
                    "",
                    "Net Neutral (internal transfer)",
                ],
            }
            st.dataframe(pd.DataFrame(nflx_data), use_container_width=True, hide_index=True, height=530)

        with col_3p:
            st.markdown("""
            <div style="font-weight:700; color:#991b1b; font-size:0.9rem; margin-bottom:8px;">🏗️ 3rd Party Breakdown</div>
            """, unsafe_allow_html=True)

            tp_data = {
                "Line Item": [
                    "3rd Party Stage Rental",
                    "Utilities (est)",
                    "Storage (est)",
                    "Office Space (est)",
                    "TOTAL 3RD PARTY FACILITIES",
                    "Production Incentive",
                    "NET COST TO TITLE (3RD PARTY)",
                    "",
                    "PLUS: Netflix Stage Sits Vacant",
                    "Netflix still pays rent/depreciation",
                    "TOTAL UNUSED STAGE COST",
                    "",
                    "ATL Incentive Uplift",
                    "",
                    f"TOTAL INCREMENTAL TO NETFLIX",
                ],
                "Amount": [
                    f"${r['cost_to_title_3p']:,.0f}",
                    f"${r['cost_to_title_3p'] * 0.088:,.0f}",
                    f"${r['cost_to_title_3p'] * 0.159:,.0f}",
                    f"${r['cost_to_title_3p'] * 0.148:,.0f}",
                    f"${r['cost_to_title_3p'] * 1.395:,.0f}",
                    f"-${r['incentive_3p']:,.0f}",
                    f"${r['cost_to_title_3p_net']:,.0f}",
                    "",
                    f"${r['overhang']:,.0f}",
                    "Netflix still pays fixed costs",
                    f"${r['overhang']:,.0f}",
                    "",
                    f"${r['atl_incentive_uplift']:,.0f}",
                    "",
                    f"${r['incremental_vs_nflx']:,.0f}",
                ],
            }
            st.dataframe(pd.DataFrame(tp_data), use_container_width=True, hide_index=True, height=530)



st.markdown("<br>", unsafe_allow_html=True)




# ── Section 4: Stage Inventory ───────────────────────────────────────────────
with st.expander("📋 Stage Inventory Explorer", expanded=False):
    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        default_filter = relevant_regions if buying_org else stages_df["Region"].unique().tolist()
        filter_region = st.multiselect("Filter by Region", options=stages_df["Region"].unique().tolist(),
                                       default=[r for r in default_filter if r in stages_df["Region"].unique()])
    with inv_col2:
        filter_sqft = st.slider("Min Sq Ft", 0, 45000, 0, step=1000, key="inv_sqft")

    filtered = stages_df[(stages_df["Region"].isin(filter_region)) & (stages_df["SqFt"] >= filter_sqft)]
    display_inv = filtered.copy()
    display_inv["DailyRate"] = display_inv["DailyRate"].apply(lambda x: f"${x:,.0f}")
    display_inv["WeeklyRate"] = display_inv["WeeklyRate"].apply(lambda x: f"${x:,.0f}")
    display_inv["MonthlyRate"] = display_inv["MonthlyRate"].apply(lambda x: f"${x:,.0f}")
    display_inv["SqFt"] = display_inv["SqFt"].apply(lambda x: f"{x:,}")
    st.dataframe(display_inv, use_container_width=True, hide_index=True, height=400)
    st.caption(f"Showing {len(filtered)} of {len(stages_df)} stages")



# ── Section 1: Stage Cost Comparison ─────────────────────────────────────────
if buying_org:
    region_label = f"for {buying_org}" + (f" — {buying_team}" if buying_team else "")
else:
    region_label = "all locations"

st.markdown(f'<div class="section-header">Stage Cost Comparison — {region_label}</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subheader">Net cost to title by location (after tax incentives). Greyed-out locations are outside typical routing.</div>', unsafe_allow_html=True)

# Show cards in rows of 4
display_regions = relevant_regions + [r for r in all_regions if r not in relevant_regions]
# First show relevant, then others greyed out
rows_of_4 = [display_regions[i:i + 4] for i in range(0, len(display_regions), 4)]

for row_regions in rows_of_4:
    cols = st.columns(len(row_regions))
    for i, region in enumerate(row_regions):
        r = results[region]
        is_relevant = region in relevant_regions
        card_class = ""
        badge = ""

        if is_relevant and r["available"] > 0:
            if region == best_region:
                card_class = "best"
                badge = '<div class="badge badge-best">✓ Recommended</div>'
            elif region == worst_region:
                card_class = "worst"
                badge = '<div class="badge badge-worst">Highest Cost</div>'
        elif not is_relevant:
            card_class = "disabled"
            badge = '<div class="badge badge-na">Outside routing</div>'
        elif r["available"] == 0:
            card_class = "disabled"
            badge = '<div class="badge badge-na">No matching stages</div>'

        with cols[i]:
            if r["available"] > 0:
                rs = region_scores.get(region, {})
                score_val = rs.get("score", 0)
                score_reasons = rs.get("reasons", [])
                reasons_html = "<br>".join(f"✓ {r}" for r in score_reasons[:3]) if score_reasons else ""
                st.markdown(f"""
                <div class="loc-card {card_class}">
                    <h3>{region} <span style="font-size:0.88rem; color:#888;">({score_val:.0f} pts)</span></h3>
                    <div class="big-num">{fmt(r['cost_to_title_nflx_net'])}</div>
                    <div class="sub">Net cost to title · {fmt(r['per_episode'])} / ep · {r['pct_budget']:.1%}</div>
                    <div class="sub" style="color:#16a34a; font-weight:600;">Netflix stage: Net neutral to Netflix</div>
                    <div class="sub">3rd Party alt: {fmt(r['incremental_vs_nflx'])} incremental (unused stage + 3rd party lease)</div>
                    <div class="sub">{r['available']} stages · {r['incentive_rate']:.0%} incentive</div>
                    <div class="sub" style="text-align:left; color:#4b5563; font-size:0.85rem; margin-top:6px;">{reasons_html}</div>
                    {badge}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="loc-card disabled">
                    <h3>{region}</h3>
                    <div class="big-num">—</div>
                    <div class="sub">No stages ≥ {min_sqft:,} sq ft</div>
                    {badge}
                </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)





# ── Netflix vs Market Rate Comparison ────────────────────────────────────────
if valid:
    st.markdown('<div class="section-header">Netflix Rate Card vs 3rd Party Market Rates</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Netflix rates are set at open market comparable rates. Here is how they compare.</div>', unsafe_allow_html=True)

    rate_data = []
    for region in [r for r in relevant_regions if results[r]["available"] > 0]:
        matching = stages_df[(stages_df["Region"] == region) & (stages_df["SqFt"] >= min_sqft)]
        if len(matching) == 0:
            continue
        nflx_avg = matching["DailyRate"].mean()
        nflx_min = matching["DailyRate"].min()
        nflx_max = matching["DailyRate"].max()
        mkt = MARKET[region]
        avg_sqft = matching["SqFt"].mean()
        third_party_rate = avg_sqft * mkt["third_party_rate"]
        diff_pct = ((nflx_avg - third_party_rate) / third_party_rate * 100) if third_party_rate > 0 else 0

        rate_data.append({
            "Location": region,
            "Netflix Avg Daily Rate": f"${nflx_avg:,.0f}",
            "Netflix Range": f"${nflx_min:,.0f} – ${nflx_max:,.0f}",
            "Est. 3P Market Rate": f"${third_party_rate:,.0f}",
            "Netflix vs Market": f"{diff_pct:+.0f}%",
            "Avg Stage Size": f"{avg_sqft:,.0f} sqft",
            "Stages Available": len(matching),
        })

    if rate_data:
        st.dataframe(pd.DataFrame(rate_data), use_container_width=True, hide_index=True)
        st.caption("3P market rates are estimates based on $/sqft benchmarks. Netflix rate card is reviewed annually against local market comps.")

    st.markdown("<br>", unsafe_allow_html=True)

# ── Chart: Cost Comparison ───────────────────────────────────────────────────
if valid and best_region:
    sorted_regions_chart = sorted(region_scores, key=lambda r: region_scores[r]["score"], reverse=True)
    st.markdown('<div class="section-header">Cost Comparison Chart</div>', unsafe_allow_html=True)

    chart_data = []
    for region in sorted_regions_chart:
        r = results[region]
        chart_data.append({
            "Location": region,
            "Netflix Stage (net neutral)": r["cost_to_title_nflx_net"],
            "3rd Party Incremental to Netflix": r["incremental_vs_nflx"],
        })
    chart_df = pd.DataFrame(chart_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Netflix Stage Cost to Title (net neutral to NFLX)",
        x=chart_df["Location"], y=chart_df["Netflix Stage (net neutral)"],
        marker_color="#3b82f6",
        text=[fmt(v) for v in chart_df["Netflix Stage (net neutral)"]],
        textposition="auto", textfont=dict(size=11)))
    fig.add_trace(go.Bar(
        name="3rd Party Incremental: Vacant Netflix Stage Cost + 3rd Party Lease",
        x=chart_df["Location"], y=chart_df["3rd Party Incremental to Netflix"],
        marker_color="#dc2626",
        text=[fmt(v) for v in chart_df["3rd Party Incremental to Netflix"]],
        textposition="auto", textfont=dict(size=11)))
    fig.update_layout(
        barmode="group",
        title=dict(text="Netflix Stage (Net Neutral) vs 3rd Party (Vacant Stage Cost + External Lease)", font=dict(size=16, family="Inter")),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Cost ($)", gridcolor="#f0f0f0", tickformat="$,.0f"),
        xaxis=dict(title=""), margin=dict(t=60, b=40, l=60, r=20), height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)


