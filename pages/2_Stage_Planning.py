#!/usr/bin/env python3
"""Netflix Studios Stage Planning & Recommendations."""

import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Stage Planning", page_icon="📅", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2.5rem; max-width: 1400px; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a1a; margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem; border-bottom: 2px solid #E50914;
    }
    .rate-note {
        background: #f8f9fa; border-left: 3px solid #E50914; padding: 12px 16px;
        border-radius: 0 8px 8px 0; font-size: 0.88rem; color: #4b5563;
        margin-top: 2rem; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Banner
st.markdown("""
<div style="background:linear-gradient(135deg, #B20710 0%, #E50914 50%, #B20710 100%);
    color:white; padding:1.5rem 2rem; border-radius:12px; margin-bottom:1.5rem;">
    <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.15em; color:rgba(255,255,255,0.7);">Netflix Studios</div>
    <h1 style="color:white !important; font-size:1.6rem; font-weight:700; margin:0;">Stage Planning & Fill Recommendations</h1>
    <p style="color:rgba(255,255,255,0.85); font-size:0.85rem; margin:0.2rem 0 0 0;">
        Upcoming titles matched to Netflix facility availability
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fef3c7; border:2px solid #f59e0b; border-radius:8px; padding:10px 16px; margin-bottom:10px; text-align:center;">
    <span style="font-size:1rem; font-weight:700; color:#92400e;">⚠️ CONCEPT ONLY — NOT FOR PRODUCTION USE</span>
</div>
""", unsafe_allow_html=True)

# Load data
data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
upcoming_path = os.path.join(data_dir, "upcoming_titles.json")
title_lookup_path = os.path.join(data_dir, "title_lookup.json")

if os.path.exists(upcoming_path):
    with open(upcoming_path) as f:
        UPCOMING = json.load(f)
else:
    UPCOMING = []

if os.path.exists(title_lookup_path):
    with open(title_lookup_path) as f:
        TITLE_LOOKUP = json.load(f)
else:
    TITLE_LOOKUP = {}

def fmt(val):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:,.1f}M"
    elif abs(val) >= 1_000:
        return f"${val/1_000:,.0f}K"
    return f"${val:,.0f}"

# ── Facility Utilization Overview ──
FACILITIES = {
    "Los Angeles": {"investment": 60, "facilities": "Raleigh · Sunset Bronson · Sunset Gower", "utilization": 27, "stages": 25, "incentive": "0%"},
    "Albuquerque": {"investment": 20, "facilities": "Netflix Studios Albuquerque (Owned)", "utilization": 40, "stages": 12, "incentive": "25%"},
    "Atlanta": {"investment": 15, "facilities": "Cinespace Atlanta", "utilization": 50, "stages": 12, "incentive": "30%"},
    "New York": {"investment": 25, "facilities": "Netflix Studios Brooklyn", "utilization": 60, "stages": 6, "incentive": "30%"},
    "New Jersey": {"investment": 0, "facilities": "Fort Monmouth (Opening Soon)", "utilization": 0, "stages": 18, "incentive": "35%", "note": "Highest UCAN incentive — prioritize high ATL titles"},
    "UK": {"investment": 130, "facilities": "Shepperton · Longcross · Uxbridge", "utilization": 34, "stages": 27, "incentive": "25%"},
    "Vancouver": {"investment": 40, "facilities": "CMPP · Martini Film Studios", "utilization": 77, "stages": 14, "incentive": "25%"},
    "Madrid": {"investment": 10, "facilities": "Madrid Content City", "utilization": 31, "stages": 11, "incentive": "30%"},
    "Japan": {"investment": 5, "facilities": "Toho Studios", "utilization": 55, "stages": 3, "incentive": "0%"},
    "Korea": {"investment": 3, "facilities": "K-ART · YCDSMC Studios", "utilization": 40, "stages": 3, "incentive": "0%"},
}

st.markdown('<div class="section-header">Facility Utilization Overview</div>', unsafe_allow_html=True)

cols = st.columns(5)
for i, (region, info) in enumerate(FACILITIES.items()):
    util = info["utilization"]
    color = "#dc2626" if util < 35 else ("#f59e0b" if util < 60 else "#16a34a")
    border_color = "#fca5a5" if util < 35 else ("#fcd34d" if util < 60 else "#86efac")
    with cols[i % 5]:
        st.markdown(f"""
        <div style="background:white; border:2px solid {border_color}; border-radius:10px; padding:14px; margin-bottom:10px; text-align:center;">
            <div style="font-size:0.88rem; font-weight:700; color:#1a1a1a;">{region}</div>
            <div style="font-size:2rem; font-weight:900; color:{color};">{util}%</div>
            <div style="font-size:0.78rem; color:#6b7280;">utilization · {info['stages']} stages</div>
            <div style="font-size:0.78rem; color:#888;">${info['investment']}M/yr · {info['incentive']} incentive</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Priority Fills ──
st.markdown('<div class="section-header">🔴 Priority Fills — Low Utilization Facilities</div>', unsafe_allow_html=True)
st.markdown("These Netflix facilities need more titles to improve cost recovery. Every empty stage = Netflix pays fixed costs with no recovery.")

no_stage_titles = [t for t in UPCOMING if not t.get("has_stage") and t.get("budget", 0) > 0]

def match_titles_to_region(region, titles):
    """Match upcoming titles to a region based on location, buying org, and budget."""
    matched = []
    for t in titles:
        loc = (t.get("shoot_location") or "").lower()
        org = t.get("buying_org", "")
        budget = t.get("budget", 0)
        
        if region == "Los Angeles":
            if "los angeles" in loc or "california" in loc or (not loc and org in ("Film", "UCAN Scripted Series", "Nonfiction Series")):
                matched.append(t)
        elif region == "Albuquerque":
            if "albuquerque" in loc or "new mexico" in loc:
                matched.append(t)
        elif region == "New Jersey":
            if "new jersey" in loc or (budget > 80000000 and org in ("Film", "UCAN Scripted Series") and ("new york" in loc or "united states" in loc or not loc)):
                matched.append(t)
        elif region == "Atlanta":
            if "atlanta" in loc or "georgia" in loc:
                matched.append(t)
        elif region == "New York":
            if "new york" in loc:
                matched.append(t)
        elif region == "UK":
            if "uk" in loc or "london" in loc or "england" in loc or org == "EMEA":
                matched.append(t)
        elif region == "Madrid":
            if "spain" in loc or "madrid" in loc:
                matched.append(t)
        elif region == "Vancouver":
            if "vancouver" in loc or "canada" in loc:
                matched.append(t)
    
    matched.sort(key=lambda x: -x.get("budget", 0))
    return matched

low_util_regions = [(r, i) for r, i in FACILITIES.items() if i["utilization"] < 40]

for region, info in low_util_regions:
    matched = match_titles_to_region(region, no_stage_titles)
    note = info.get("note", "")
    
    with st.expander(f"**{region}** — {info['utilization']}% utilization | {info['facilities']} | {info['incentive']} incentive" + (f" | ⚡ {note}" if note else ""), expanded=True):
        if matched:
            data = [{
                "Title": t["title"],
                "Buying Org": t["buying_org"],
                "Budget": f"${t['budget']:,.0f}",
                "Phase": t["phase"],
                "Current Location": (t.get("shoot_location") or "TBD")[:45],
            } for t in matched[:10]]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            st.caption(f"{len(matched)} potential titles for {region}")
        else:
            st.info(f"No upcoming titles currently targeting {region}. Consider steering unassigned titles here.")

st.markdown("---")

# ── Fort Monmouth Special Section ──
st.markdown('<div class="section-header">🏗️ Fort Monmouth (New Jersey) — High ATL Title Recommendations</div>', unsafe_allow_html=True)
st.markdown("""
Fort Monmouth offers **35% tax incentive** — the highest among all UCAN locations.
**High above-the-line (ATL) titles benefit most** since talent, writers, and director costs are eligible for the NJ incentive.
The following high-budget titles without a confirmed stage are strong candidates:
""")

nj_candidates = []
for t in no_stage_titles:
    org = t.get("buying_org", "")
    budget = t.get("budget", 0)
    loc = (t.get("shoot_location") or "").lower()
    if budget > 50000000 and org in ("Film", "UCAN Scripted Series"):
        if "new jersey" in loc or "new york" in loc or "united states" in loc or not loc:
            nj_candidates.append(t)
nj_candidates.sort(key=lambda x: -x["budget"])

if nj_candidates:
    nj_data = [{
        "Title": t["title"],
        "Buying Org": t["buying_org"],
        "Budget": f"${t['budget']:,.0f}",
        "Est. NJ Incentive (35%)": f"${t['budget'] * 0.35:,.0f}",
        "Savings vs LA (0%)": f"${t['budget'] * 0.35:,.0f}",
        "Phase": t["phase"],
        "Current Location": (t.get("shoot_location") or "TBD")[:40],
    } for t in nj_candidates[:15]]
    st.dataframe(pd.DataFrame(nj_data), use_container_width=True, hide_index=True)
    
    total_incentive = sum(t["budget"] * 0.35 for t in nj_candidates[:15])
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:2px solid #16a34a; border-radius:12px; padding:16px; text-align:center; margin-top:8px;">
        <div style="font-size:0.88rem; color:#15803d; text-transform:uppercase;">Potential NJ Incentive Recovery (top 15 titles)</div>
        <div style="font-size:2rem; font-weight:900; color:#166534;">{fmt(total_incentive)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── All Unassigned Titles ──
st.markdown('<div class="section-header">📋 All Upcoming Titles Without Stage Assignment</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    filter_org = st.selectbox("Filter by Buying Org", ["All"] + sorted(set(t["buying_org"] for t in UPCOMING if t["buying_org"])), key="plan_org")
with col2:
    filter_budget = st.selectbox("Min Budget", ["All", "$50M+", "$100M+", "$150M+"], key="plan_budget")

filtered = [t for t in no_stage_titles]
if filter_org != "All":
    filtered = [t for t in filtered if t["buying_org"] == filter_org]
if filter_budget == "$50M+":
    filtered = [t for t in filtered if t.get("budget", 0) >= 50000000]
elif filter_budget == "$100M+":
    filtered = [t for t in filtered if t.get("budget", 0) >= 100000000]
elif filter_budget == "$150M+":
    filtered = [t for t in filtered if t.get("budget", 0) >= 150000000]
filtered.sort(key=lambda x: -x.get("budget", 0))

all_data = [{
    "Title": t["title"],
    "Buying Org": t["buying_org"],
    "Budget": f"${t['budget']:,.0f}" if t["budget"] > 0 else "TBD",
    "Phase": t["phase"],
    "Location": (t.get("shoot_location") or "TBD")[:50],
} for t in filtered]

if all_data:
    st.dataframe(pd.DataFrame(all_data), use_container_width=True, hide_index=True, height=500)
st.caption(f"Showing {len(all_data)} titles")

# Footer
st.markdown("""
<div class="rate-note">
    <strong>⚠️ Disclaimer:</strong> Stage planning recommendations are based on high-level estimates,
    current utilization data, and title metadata from Slate Manager. Actual stage assignments require
    coordination with Production Planning. Contact the Production Services team for formal placement decisions.
</div>
""", unsafe_allow_html=True)
