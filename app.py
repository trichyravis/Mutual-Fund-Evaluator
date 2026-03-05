"""
MF Fund Portfolio Evaluator
The Mountain Path - World of Finance
Prof. V. Ravichandran | Live AMFI Data
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="MF Portfolio Evaluator | Mountain Path",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

C = {
    "gold":  "#FFD700", "blue":  "#003366", "mid":   "#004d80",
    "card":  "#112240", "dark":  "#0a192f", "txt":   "#e6f1ff",
    "muted": "#8892b0", "grn":   "#28a745", "red":   "#dc3545",
    "lb":    "#ADD8E6", "bg1":   "#1a2332", "bg2":   "#243447", "bg3": "#2a3f5f",
}
FUND_COLS   = ["#FFD700", "#00bfff", "#28a745", "#ff6b6b", "#c084fc"]

st.html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;color:{C['txt']};}}
.stApp{{background:linear-gradient(135deg,{C['bg1']},{C['bg2']},{C['bg3']});}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,{C['dark']},{C['card']})!important;border-right:2px solid {C['gold']}!important;}}
[data-testid="stSidebar"] *{{color:{C['txt']}!important;}}
[data-testid="stSidebar"] [data-baseweb="select"]>div{{background:{C['card']}!important;border:1px solid {C['mid']}!important;color:{C['txt']}!important;border-radius:6px;}}
.main .block-container{{padding:1rem 2rem!important;max-width:100%!important;}}
[data-baseweb="select"]>div{{background:{C['card']}!important;border:1px solid {C['mid']}!important;color:{C['txt']}!important;border-radius:6px;}}
[data-baseweb="menu"]{{background:{C['card']}!important;border:1px solid {C['mid']}!important;}}
[data-baseweb="option"]{{background:{C['card']}!important;color:{C['txt']}!important;}}
[data-baseweb="option"]:hover{{background:{C['mid']}!important;}}
.stButton>button{{background:linear-gradient(135deg,{C['gold']},#e6c200)!important;color:{C['blue']}!important;font-weight:800!important;border:none!important;border-radius:8px!important;padding:.55rem 1.5rem!important;font-size:.95rem!important;box-shadow:0 4px 15px rgba(255,215,0,.35)!important;transition:all .25s!important;width:100%!important;}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(255,215,0,.5)!important;}}
[data-baseweb="tab-list"]{{background:{C['card']}!important;border-radius:10px!important;gap:4px!important;padding:5px!important;border:1px solid {C['mid']}!important;}}
[data-baseweb="tab"]{{background:transparent!important;color:{C['muted']}!important;border-radius:7px!important;padding:8px 15px!important;font-weight:600!important;font-size:.84rem!important;}}
[aria-selected="true"]{{background:linear-gradient(135deg,{C['blue']},{C['mid']})!important;color:{C['gold']}!important;border-bottom:2px solid {C['gold']}!important;}}
[data-testid="stMetricValue"]{{color:{C['gold']}!important;font-size:1.25rem!important;font-weight:800!important;}}
[data-testid="stMetricLabel"]{{color:{C['muted']}!important;font-size:.7rem!important;}}
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:{C['dark']};}}
::-webkit-scrollbar-thumb{{background:{C['mid']};border-radius:3px;}}
input{{color:{C['txt']}!important;background:{C['card']}!important;}}
[data-baseweb="input"]>div{{background:{C['card']}!important;border:1px solid {C['mid']}!important;color:{C['txt']}!important;border-radius:6px!important;}}
.stNumberInput>div>div{{background:{C['card']}!important;border:1px solid {C['mid']}!important;border-radius:6px!important;}}
.stNumberInput input{{color:{C['txt']}!important;}}
[data-testid="stDownloadButton"]>button{{background:{C['mid']}!important;color:{C['gold']}!important;border:1px solid {C['gold']}!important;font-weight:700!important;border-radius:7px!important;}}
</style>
""")

# ─── PLOTLY BASE LAYOUT ─────────────────────────────────────────────────────
def PL(title="", h=420):
    return dict(
        height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,34,64,.55)",
        font=dict(family="Inter", color=C["txt"], size=11),
        title=dict(text=title, font=dict(color=C["gold"], size=14), x=.01, y=.97),
        xaxis=dict(gridcolor="rgba(0,77,128,.35)", linecolor=C["mid"],
                   tickfont=dict(color=C["muted"]), title_font=dict(color=C["muted"])),
        yaxis=dict(gridcolor="rgba(0,77,128,.35)", linecolor=C["mid"],
                   tickfont=dict(color=C["muted"]), title_font=dict(color=C["muted"])),
        legend=dict(bgcolor="rgba(17,34,64,.85)", bordercolor=C["mid"], borderwidth=1,
                    font=dict(color=C["txt"], size=10), orientation="h",
                    x=0, y=-.22, xanchor="left"),
        margin=dict(l=52, r=16, t=42, b=72),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["card"], bordercolor=C["mid"], font=dict(color=C["txt"])),
    )

# ─── DEMO SCHEME LIST (used as fallback if AMFI API is unreachable) ──────────
DEMO_SCHEMES = [
    (100033, "SBI Blue Chip Fund - Regular Plan - Growth"),
    (120503, "Mirae Asset Large Cap Fund - Regular Plan - Growth"),
    (119598, "Axis Bluechip Fund - Regular Growth"),
    (118834, "ICICI Prudential Bluechip Fund - Growth"),
    (112090, "HDFC Top 100 Fund - Growth Plan"),
    (120505, "Mirae Asset Emerging Bluechip Fund - Regular Plan - Growth"),
    (119775, "Axis Midcap Fund - Regular Growth"),
    (118989, "HDFC Mid-Cap Opportunities Fund - Growth"),
    (120594, "DSP Midcap Fund - Regular Plan - Growth"),
    (118272, "SBI Small Cap Fund - Regular Plan - Growth"),
    (125354, "Axis Small Cap Fund - Regular Growth"),
    (120843, "Nippon India Small Cap Fund - Growth Plan"),
    (120503, "Axis Long Term Equity Fund - Regular Growth"),  # ELSS
    (118825, "ICICI Prudential Long Term Equity Fund - Growth"),
    (119597, "Axis Flexi Cap Fund - Regular Growth"),
    (118701, "Parag Parikh Flexi Cap Fund - Regular Plan Growth"),
    (120716, "UTI Nifty 50 Index Fund - Growth"),
    (120847, "HDFC Index Fund Nifty 50 Plan"),
    (120716, "Nippon India Index Fund Nifty 50 Plan - Growth"),
    (101305, "HDFC Liquid Fund - Growth Option"),
    (118701, "SBI Liquid Fund - Regular Plan - Growth"),
    (119775, "ICICI Prudential Gilt Fund - Growth"),
    (120594, "HDFC Balanced Advantage Fund - Growth"),
    (118989, "ICICI Prudential Equity & Debt Fund - Growth"),
    (120503, "SBI Gold Fund - Regular Plan - Growth"),
    (119598, "Nippon India Gold Savings Fund - Growth Plan"),
    (120843, "Motilal Oswal Nasdaq 100 FoF - Regular Growth"),
    (118272, "ICICI Prudential US Bluechip Equity Fund - Growth"),
    (125354, "Nippon India Banking & PSU Debt Fund - Growth"),
    (120716, "SBI Banking & Financial Services Fund - Regular Growth"),
]

@st.cache_data(ttl=3600, show_spinner=False)
def load_schemes():
    """Fetch all MF schemes from AMFI. Falls back to demo list if unreachable."""
    AMFI_URLS = [
        "https://api.mfapi.in/mf",
        "https://mfapi.in/mf",
    ]
    last_err = ""
    for url in AMFI_URLS:
        try:
            r = requests.get(url, timeout=18)
            r.raise_for_status()
            raw = r.json()
            if not raw:
                continue
            # API returns [{schemeCode, schemeName}, ...] or [[code, name], ...]
            first = raw[0]
            if isinstance(first, dict):
                df = pd.DataFrame(raw)
                df.columns = [c.lower().replace(" ","_") for c in df.columns]
                rename_map = {}
                for col in df.columns:
                    if "code" in col: rename_map[col] = "scheme_code"
                    if "name" in col: rename_map[col] = "scheme_name"
                df = df.rename(columns=rename_map)
            elif isinstance(first, (list, tuple)):
                df = pd.DataFrame(raw, columns=["scheme_code", "scheme_name"])
            else:
                # Flat alternating list fallback
                df = pd.DataFrame(raw, columns=["scheme_code", "scheme_name"])
            df["scheme_code"] = pd.to_numeric(df["scheme_code"], errors="coerce")
            df = df.dropna(subset=["scheme_code","scheme_name"])
            df["scheme_code"] = df["scheme_code"].astype(int)
            if len(df) > 50:
                return df, "live"
        except Exception as e:
            last_err = str(e)
            continue
    # Fallback: curated demo list
    df = pd.DataFrame(DEMO_SCHEMES, columns=["scheme_code","scheme_name"])
    return df, f"demo|{last_err[:120]}"

@st.cache_data(ttl=1800, show_spinner=False)
def load_nav(code:int, start:str, end:str):
    """Fetch historical NAV for a scheme from mfapi.in with retry."""
    URLS = [
        f"https://api.mfapi.in/mf/{code}",
        f"https://mfapi.in/mf/{code}",
    ]
    for url in URLS:
        try:
            r = requests.get(url, timeout=22)
            r.raise_for_status()
            j = r.json()
            if "data" not in j or len(j["data"]) == 0:
                continue
            df = pd.DataFrame(j["data"])
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
            df = df.dropna().sort_values("date").set_index("date")
            df = df[(df.index >= start) & (df.index <= end)]
            name = j.get("meta",{}).get("scheme_name","Fund")
            return df["nav"], name
        except Exception:
            continue
    return None, "Error"

def categorize(df):
    kw = {
        "Large Cap":         ["large cap","largecap","top 100","bluechip","nifty 50 index","sensex index","top100"],
        "Mid Cap":           ["mid cap","midcap","nifty midcap"],
        "Small Cap":         ["small cap","smallcap","nifty smallcap"],
        "ELSS / Tax":        ["elss","tax saver","tax saving"],
        "Flexi / Multi Cap": ["flexi cap","multicap","multi cap","flexicap"],
        "Index Fund":        ["index fund","nifty index","sensex index","index - "],
        "ETF":               ["etf","exchange traded"],
        "Debt / Liquid":     ["liquid","debt","gilt","overnight","bond","income","money market","g-sec","gsec"],
        "Hybrid":            ["hybrid","balanced","multi asset","equity savings"],
        "Gold / Commodity":  ["gold","silver","commodity"],
        "International":     ["international","global","nasdaq","s&p","us equity","world"],
        "Sectoral":          ["bank","pharma","tech","infra","fmcg","auto","energy","realty","health","it fund","consumption"],
        "Thematic":          ["esg","momentum","value","quality","dividend","focussed","focused"],
    }
    def gc(n):
        nl = n.lower()
        for cat,keys in kw.items():
            if any(k in nl for k in keys): return cat
        return "Other"
    d = df.copy(); d["category"] = d["scheme_name"].apply(gc); return d

# ─── ANALYTICS ───────────────────────────────────────────────────────────────
def compute(nav:pd.Series, lump:float, sip:float):
    if nav is None or len(nav) < 20: return None
    nav = nav.dropna()
    dr    = nav.pct_change().dropna()
    nyrs  = max((nav.index[-1]-nav.index[0]).days/365.25, .1)
    tot   = (nav.iloc[-1]/nav.iloc[0])-1
    cagr  = (1+tot)**(1/nyrs)-1
    vol   = dr.std()*np.sqrt(252)
    sharpe= (cagr-.065)/vol if vol>0 else 0
    dd    = (nav-nav.cummax())/nav.cummax()
    mxdd  = dd.min()
    def rc(y):
        w=int(y*252)
        if len(nav)<w+3: return np.nan
        return ((nav.iloc[-1]/nav.iloc[-w])**(1/y))-1
    lv    = lump*(nav.iloc[-1]/nav.iloc[0])
    nm    = nav.resample("ME").last().dropna()
    si    = sip*len(nm); su=(sip/nm).sum(); sv=su*nm.iloc[-1]
    sr    = (sv-si)/si if si>0 else 0
    ann   = nav.resample("YE").last().pct_change().dropna()
    by    = ann.max() if len(ann) else np.nan
    wy    = ann.min() if len(ann) else np.nan
    bl    = str(ann.idxmax().year) if len(ann) else "—"
    wl    = str(ann.idxmin().year) if len(ann) else "—"
    return dict(nav=nav, dr=dr, nyrs=nyrs, tot=tot, cagr=cagr, vol=vol,
                sharpe=sharpe, mxdd=mxdd,
                r1=rc(1), r3=rc(3), r5=rc(5), r7=rc(7), r10=rc(10),
                li=lump, lv=lv, si=si, sv=sv, sr=sr, spm=sip,
                by=by, bl=bl, wy=wy, wl=wl, g100=(nav.iloc[-1]/nav.iloc[0])*100)

def fp(v, d=1):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "—"
    return f"{v*100:.{d}f}%"

def fi(v):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "—"
    if v>=1e7: return f"₹{v/1e7:.2f} Cr"
    if v>=1e5: return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"

# ─── UI ──────────────────────────────────────────────────────────────────────
def hero():
    st.html(f"""
    <div style="background:linear-gradient(135deg,{C['blue']},{C['mid']});
      border:2px solid {C['gold']};border-radius:14px;padding:1.2rem 2rem;
      display:flex;align-items:center;justify-content:space-between;
      margin-bottom:1.1rem;user-select:none;">
      <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-size:2.4rem;">🏔️</span>
        <div>
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
            font-size:1.65rem;font-weight:900;letter-spacing:-.5px;">THE MOUNTAIN PATH</div>
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};
            font-size:.9rem;font-weight:600;">World of Finance &nbsp;·&nbsp; MF Portfolio Evaluator</div>
        </div>
      </div>
      <div style="text-align:right;">
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:800;font-size:1rem;">Prof. V. Ravichandran</div>
        <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.73rem;">28+ Yrs Corporate Finance · 10+ Yrs Academic</div>
        <div style="color:{C['grn']};-webkit-text-fill-color:{C['grn']};font-size:.7rem;margin-top:2px;">● Live AMFI NAV Data</div>
      </div>
    </div>
    """)

def slabel(icon, txt, sub=""):
    st.html(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:.8rem 0 .5rem;user-select:none;">
      <div style="width:4px;height:28px;background:linear-gradient({C['gold']},{C['mid']});border-radius:2px;"></div>
      <div>
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:1rem;font-weight:800;">{icon}&nbsp;{txt}</div>
        {f'<div style="color:{C["muted"]};-webkit-text-fill-color:{C["muted"]};font-size:.74rem;">{sub}</div>' if sub else ''}
      </div>
    </div>
    """)

def snapshot_row(funds):
    cols = st.columns(len(funds))
    for f,col in zip(funds,cols):
        m=f["m"]; cc=C["grn"] if m["cagr"]>0 else C["red"]
        sc=C["grn"] if m["sharpe"]>1 else (C["gold"] if m["sharpe"]>0 else C["red"])
        with col:
            st.html(f"""
            <div style="background:{C['card']};border:1px solid {f['c']};
              border-radius:10px;padding:.9rem 1rem;user-select:none;">
              <div style="display:flex;align-items:center;gap:7px;margin-bottom:8px;
                border-bottom:1px solid {C['mid']};padding-bottom:7px;">
                <div style="width:9px;height:9px;border-radius:50%;background:{f['c']};
                  box-shadow:0 0 5px {f['c']};"></div>
                <div style="color:{f['c']};-webkit-text-fill-color:{f['c']};
                  font-weight:800;font-size:.74rem;white-space:nowrap;overflow:hidden;
                  text-overflow:ellipsis;max-width:180px;" title="{f['name']}">
                  {f['name'][:32]}{'…' if len(f['name'])>32 else ''}
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 10px;">
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">PERIOD CAGR</div>
                  <div style="color:{cc};-webkit-text-fill-color:{cc};font-size:1.15rem;font-weight:800;">{fp(m['cagr'])}</div>
                </div>
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">SHARPE</div>
                  <div style="color:{sc};-webkit-text-fill-color:{sc};font-size:1.15rem;font-weight:800;">{m['sharpe']:.2f}</div>
                </div>
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">VOLATILITY</div>
                  <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-size:.95rem;font-weight:700;">{fp(m['vol'])}</div>
                </div>
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">MAX DRAWDOWN</div>
                  <div style="color:{C['red']};-webkit-text-fill-color:{C['red']};font-size:.95rem;font-weight:700;">{fp(m['mxdd'])}</div>
                </div>
              </div>
              <div style="border-top:1px solid {C['mid']};margin-top:8px;padding-top:7px;
                display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">LUMPSUM → VALUE</div>
                  <div style="color:{C['grn']};-webkit-text-fill-color:{C['grn']};font-size:.88rem;font-weight:700;">{fi(m['li'])} → {fi(m['lv'])}</div>
                </div>
                <div>
                  <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.58rem;">SIP CORPUS</div>
                  <div style="color:{C['grn']};-webkit-text-fill-color:{C['grn']};font-size:.88rem;font-weight:700;">{fi(m['sv'])}</div>
                </div>
              </div>
            </div>
            """)

# ─── CHARTS ──────────────────────────────────────────────────────────────────
def ch_nav(funds):
    fig=go.Figure()
    for f in funds:
        nav=f["m"]["nav"]; idx=(nav/nav.iloc[0])*100
        fig.add_trace(go.Scatter(x=idx.index,y=np.round(idx.values,2),name=f["name"][:28],
            line=dict(color=f["c"],width=2.4),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>%{{x|%d %b %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>"))
    fig.update_layout(**PL("📈  NAV Growth — Indexed to 100"))
    fig.update_yaxes(title_text="Indexed NAV"); return fig

def ch_dd(funds):
    fig=go.Figure()
    for f in funds:
        nav=f["m"]["nav"]; dd=((nav-nav.cummax())/nav.cummax())*100
        fig.add_trace(go.Scatter(x=dd.index,y=np.round(dd.values,2),name=f["name"][:28],
            fill="tozeroy",line=dict(color=f["c"],width=1.5),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>DD: %{{y:.2f}}%<extra></extra>"))
    fig.update_layout(**PL("📉  Drawdown from Peak (%)"))
    fig.update_yaxes(title_text="Drawdown %"); return fig

def ch_annual(funds):
    fig=go.Figure()
    for f in funds:
        nav=f["m"]["nav"]; ann=nav.resample("YE").last().pct_change().dropna()*100
        ann.index=ann.index.year
        fig.add_trace(go.Bar(x=ann.index,y=np.round(ann.values,1),name=f["name"][:28],
            marker_color=f["c"],opacity=.82,
            hovertemplate=f"<b>{f['name'][:28]}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>"))
    fig.update_layout(**PL("📊  Annual Returns (%)"),barmode="group")
    fig.update_xaxes(dtick=1,title_text="Year"); fig.update_yaxes(title_text="Return %"); return fig

def ch_rolling(funds,w=3):
    fig=go.Figure()
    for f in funds:
        nav=f["m"]["nav"]; wn=int(w*252)
        if len(nav)<wn+5: continue
        r=nav.pct_change(wn).dropna(); ra=((1+r)**(1/w)-1)*100
        fig.add_trace(go.Scatter(x=ra.index,y=np.round(ra.values,2),name=f["name"][:28],
            line=dict(color=f["c"],width=2),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>%{{x|%b %Y}}<br>{w}Y CAGR: %{{y:.1f}}%<extra></extra>"))
    fig.add_hline(y=0,line_dash="dot",line_color=C["muted"],annotation_text="0%",
                  annotation_font=dict(color=C["muted"]))
    fig.update_layout(**PL(f"🔄  Rolling {w}-Year CAGR (%)"))
    fig.update_yaxes(title_text="CAGR %"); return fig

def ch_rr(funds):
    fig=go.Figure()
    for f in funds:
        m=f["m"]; v=m["vol"]*100; c=m["cagr"]*100; s=m["sharpe"]
        sz=max(16,min(50,abs(s)*14+14))
        fig.add_trace(go.Scatter(x=[v],y=[c],name=f["name"][:25],
            mode="markers+text",
            marker=dict(size=sz,color=f["c"],opacity=.88,line=dict(color="white",width=1.5)),
            text=[f["name"][:18]],textposition="top center",textfont=dict(color=f["c"],size=9.5),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>Volatility: {v:.1f}%<br>CAGR: {c:.1f}%<br>Sharpe: {s:.2f}<extra></extra>"))
    fig.add_hline(y=12,line_dash="dash",line_color=C["muted"],line_width=.8)
    fig.add_vline(x=15,line_dash="dash",line_color=C["muted"],line_width=.8)
    fig.update_layout(**PL("⚖️  Risk–Return Map  (bubble size ∝ Sharpe)",h=430),showlegend=False)
    fig.update_xaxes(title_text="Annualised Volatility (%)"); fig.update_yaxes(title_text="Period CAGR (%)"); return fig

def ch_sip(funds,sip):
    fig=go.Figure(); ref=None
    for f in funds:
        nav=f["m"]["nav"]; nm=nav.resample("ME").last().dropna()
        if len(nm)<2: continue
        ref=nm; pv=(sip/nm).cumsum()*nm
        fig.add_trace(go.Scatter(x=pv.index,y=np.round(pv.values,0),name=f["name"][:28],
            line=dict(color=f["c"],width=2.4),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>%{{x|%b %Y}}<br>₹%{{y:,.0f}}<extra></extra>"))
    if ref is not None:
        inv=sip*np.arange(1,len(ref)+1)
        fig.add_trace(go.Scatter(x=ref.index,y=inv,name="Amount Invested",
            line=dict(color=C["muted"],dash="dot",width=1.5),
            hovertemplate="Invested: ₹%{y:,.0f}<extra></extra>"))
    fig.update_layout(**PL(f"💳  SIP Growth — ₹{sip:,}/month"))
    fig.update_yaxes(title_text="Portfolio Value (₹)",tickformat=","); return fig

def ch_lump(funds):
    fig=go.Figure()
    for f in funds:
        nav=f["m"]["nav"]; g=(nav/nav.iloc[0])*f["m"]["li"]
        fig.add_trace(go.Scatter(x=g.index,y=np.round(g.values,0),name=f["name"][:28],
            line=dict(color=f["c"],width=2.4),
            hovertemplate=f"<b>{f['name'][:28]}</b><br>%{{x|%d %b %Y}}<br>₹%{{y:,.0f}}<extra></extra>"))
    fig.update_layout(**PL(f"💰  Lumpsum Growth (₹{funds[0]['m']['li']:,.0f})"))
    fig.update_yaxes(title_text="Value (₹)",tickformat=","); return fig

def ch_corr(funds):
    if len(funds)<2: return None
    rd={f["name"][:20]:f["m"]["dr"] for f in funds}
    dfr=pd.DataFrame(rd).dropna(); corr=dfr.corr().round(2)
    fig=go.Figure(go.Heatmap(
        z=corr.values,x=corr.columns.tolist(),y=corr.index.tolist(),
        colorscale=[[0,C["blue"]],[.5,C["mid"]],[1,C["gold"]]],
        zmin=-1,zmax=1,text=corr.values,texttemplate="%{text:.2f}",
        textfont=dict(color=C["txt"],size=12),hoverongaps=False,
        colorbar=dict(tickfont=dict(color=C["txt"]),outlinecolor=C["mid"]),
    ))
    fig.update_layout(height=380,paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=f"rgba(17,34,64,.55)",font=dict(family="Inter",color=C["txt"]),
        title=dict(text="🔗  Return Correlation Matrix",font=dict(color=C["gold"],size=14),x=.01),
        margin=dict(l=20,r=20,t=42,b=20),
        xaxis=dict(tickfont=dict(color=C["muted"])),yaxis=dict(tickfont=dict(color=C["muted"])))
    return fig

def ch_violin(funds):
    fig=go.Figure()
    for f in funds:
        dr=f["m"]["dr"]*100
        fig.add_trace(go.Violin(y=dr.values,name=f["name"][:22],
            box_visible=True,meanline_visible=True,
            fillcolor=f["c"],opacity=.55,line_color=f["c"]))
    fig.update_layout(**PL("🎻  Daily Returns Distribution",h=380))
    fig.update_yaxes(title_text="Daily Return (%)"); return fig

# ─── TABLES ──────────────────────────────────────────────────────────────────
def scorecard(funds):
    rows=[{"Fund Name":f["name"],"1Y":fp(f["m"]["r1"]),"3Y":fp(f["m"]["r3"]),
           "5Y":fp(f["m"]["r5"]),"7Y":fp(f["m"]["r7"]),"10Y":fp(f["m"]["r10"]),
           "Period CAGR":fp(f["m"]["cagr"]),"Volatility":fp(f["m"]["vol"]),
           "Sharpe":f"{f['m']['sharpe']:.2f}","Max DD":fp(f["m"]["mxdd"]),
           "₹100→":f"₹{f['m']['g100']:.0f}",
           "Best Yr":f"{fp(f['m']['by'])} ({f['m']['bl']})",
           "Worst Yr":f"{fp(f['m']['wy'])} ({f['m']['wl']})"}
          for f in funds]
    return pd.DataFrame(rows).set_index("Fund Name")

def sip_tbl(funds):
    rows=[{"Fund":f["name"],"SIP/Mo":fi(f["m"]["spm"]),"Invested":fi(f["m"]["si"]),
           "Value":fi(f["m"]["sv"]),"Gain":fi(f["m"]["sv"]-f["m"]["si"]),"Return":fp(f["m"]["sr"])}
          for f in funds]
    return pd.DataFrame(rows).set_index("Fund")

def lump_tbl(funds):
    rows=[{"Fund":f["name"],"Invested":fi(f["m"]["li"]),"Value":fi(f["m"]["lv"]),
           "Gain":fi(f["m"]["lv"]-f["m"]["li"]),"Total Ret":fp(f["m"]["tot"]),
           "CAGR":fp(f["m"]["cagr"]),"Years":f"{f['m']['nyrs']:.1f}"}
          for f in funds]
    return pd.DataFrame(rows).set_index("Fund")

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def sidebar(schemes, catdf):
    with st.sidebar:
        st.html(f"""
        <div style="text-align:center;padding:1rem 0 .6rem;user-select:none;">
          <div style="font-size:1.8rem;margin-bottom:2px;">🏔️</div>
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
            font-size:1.1rem;font-weight:900;letter-spacing:.5px;">THE MOUNTAIN PATH</div>
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};
            font-size:.75rem;font-weight:500;">World of Finance</div>
          <div style="height:2px;background:linear-gradient(90deg,transparent,{C['gold']},transparent);
            margin:8px 0;"></div>
        </div>
        """)
        st.html(f"""<div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
          font-size:.8rem;font-weight:700;margin-bottom:3px;user-select:none;">📅 DATE RANGE</div>""")
        c1,c2=st.columns(2)
        with c1:
            st.markdown(f'<span style="color:{C["muted"]};font-size:.68rem">Start</span>',unsafe_allow_html=True)
            s=st.date_input("s",value=date(2015,1,1),min_value=date(2000,1,1),
                            max_value=date.today(),label_visibility="collapsed",key="ds")
        with c2:
            st.markdown(f'<span style="color:{C["muted"]};font-size:.68rem">End</span>',unsafe_allow_html=True)
            e=st.date_input("e",value=date.today(),min_value=date(2000,1,1),
                            max_value=date.today(),label_visibility="collapsed",key="de")
        st.html(f"""<div style="height:1px;background:{C['mid']};margin:9px 0;"></div>
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
          font-size:.8rem;font-weight:700;margin-bottom:3px;user-select:none;">💰 INVESTMENT</div>""")
        lump=st.number_input("Lumpsum (₹)",10000,10000000,100000,10000,key="lp")
        sip =st.number_input("Monthly SIP (₹)",500,500000,10000,500,key="sp")
        st.html(f"""<div style="height:1px;background:{C['mid']};margin:9px 0;"></div>
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
          font-size:.8rem;font-weight:700;margin-bottom:5px;user-select:none;">🎯 SELECT 5 FUNDS</div>""")
        cats=["— All Categories —"]+sorted(catdf["category"].unique().tolist())
        sels=[]
        for i in range(1,6):
            col=FUND_COLS[i-1]
            st.html(f"""<div style="background:{C['card']};border-left:3px solid {col};
              padding:5px 10px;border-radius:0 6px 6px 0;margin-bottom:3px;user-select:none;">
              <span style="color:{col};-webkit-text-fill-color:{col};
                font-size:.74rem;font-weight:800;letter-spacing:1px;">FUND {i}</span></div>""")
            cat=st.selectbox(f"C{i}",cats,key=f"c{i}",label_visibility="collapsed")
            pool=catdf if cat=="— All Categories —" else catdf[catdf["category"]==cat]
            nms=["— Skip —"]+pool["scheme_name"].tolist()
            nm=st.selectbox(f"F{i}",nms,key=f"f{i}",label_visibility="collapsed")
            if nm!="— Skip —":
                cd=pool[pool["scheme_name"]==nm]["scheme_code"].values
                if len(cd): sels.append({"name":nm,"code":int(cd[0]),"c":col})
        st.html(f"""<div style="height:1px;background:{C['mid']};margin:9px 0;"></div>""")
        run=st.button("▶  ANALYSE PORTFOLIO",key="run",use_container_width=True)
        if st.button("🔄  Refresh Scheme List", key="refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.html(f"""
        <div style="text-align:center;margin-top:1.2rem;padding:.7rem;
          background:{C['card']};border-radius:8px;border:1px solid {C['mid']};user-select:none;">
          <div style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};font-size:.7rem;margin-bottom:5px;">
            Prof. V. Ravichandran</div>
          <div style="display:flex;justify-content:center;gap:18px;">
            <a href="https://www.linkedin.com/in/trichyravis" target="_blank"
              style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.74rem;font-weight:700;text-decoration:none;">🔗 LinkedIn</a>
            <a href="https://github.com/trichyravis" target="_blank"
              style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.74rem;font-weight:700;text-decoration:none;">⌥ GitHub</a>
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.64rem;margin-top:5px;">
            Data: AMFI India · mfapi.in</div>
        </div>
        """)
    return sels,str(s),str(e),lump,sip,run

# ─── WELCOME ─────────────────────────────────────────────────────────────────
def welcome():
    feats=[("📈","NAV Growth","Indexed comparison"),("📊","Annual Returns","Year-on-year bars"),
           ("🔄","Rolling CAGR","1/3/5Y windows"),("📉","Drawdown","Peak-trough loss"),
           ("⚖️","Risk-Return","Sharpe bubble map"),("💳","SIP Tracker","Monthly corpus"),
           ("💰","Lumpsum","One-time investment"),("🔗","Correlation","Diversification matrix"),
           ("🎻","Distribution","Daily return violin"),("📋","Scorecard","Full metrics table")]
    cards="".join([f"""<div style="background:rgba(0,51,102,.45);border:1px solid {C['mid']};
      border-radius:8px;padding:.7rem .9rem;">
      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.95rem;margin-bottom:3px;">{ic} <b>{t}</b></div>
      <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.73rem;">{d}</div>
    </div>""" for ic,t,d in feats])
    st.html(f"""
    <div style="background:{C['card']};border:2px solid {C['gold']};
      border-radius:16px;padding:2.5rem;margin:1rem 0;user-select:none;">
      <div style="text-align:center;margin-bottom:2rem;">
        <div style="font-size:3.5rem;margin-bottom:.5rem;">🏔️</div>
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
          font-size:1.8rem;font-weight:900;margin-bottom:.4rem;">MF Portfolio Evaluator</div>
        <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-size:.98rem;margin-bottom:.3rem;">
          Compare up to 5 mutual funds with live AMFI NAV data</div>
        <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.83rem;">
          13 categories · CAGR · Sharpe · Drawdown · SIP · Lumpsum · Correlation</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:1.5rem;">
        {cards}
      </div>
      <div style="text-align:center;color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.9rem;">
        👈&nbsp;Select up to <strong style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};">5 funds</strong>
        from the sidebar and click
        <strong style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};">ANALYSE PORTFOLIO</strong>
      </div>
    </div>
    """)

# ─── HOW TO USE TAB ──────────────────────────────────────────────────────────
def how_to_use_tab():
    st.html(f"""
    <div style="background:linear-gradient(135deg,{C['blue']},{C['mid']});
      border:2px solid {C['gold']};border-radius:14px;padding:1.4rem 2rem;
      margin-bottom:1.4rem;user-select:none;">
      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
        font-size:1.4rem;font-weight:900;margin-bottom:.3rem;">📖 How to Use — MF Portfolio Evaluator</div>
      <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-size:.9rem;">
        A step-by-step guide to comparing mutual funds and interpreting results
      </div>
    </div>
    """)

    # ── STEP CARDS ──────────────────────────────────────────────────────────
    steps = [
        ("1","🗓️","Set Your Date Range",
         "In the sidebar, choose a <b>Start Date</b> and <b>End Date</b>.",
         ["Default range is Jan 2015 → Today (10 years of data)",
          "Shorter range (e.g. 3Y) = recent performance focus",
          "Longer range (e.g. 10Y) = includes full market cycles (2018 crash, 2020 COVID, 2021 bull run)",
          "Tip: Use 7–10 years to get statistically meaningful CAGR & Sharpe"]),
        ("2","💰","Enter Investment Amounts",
         "Set the <b>Lumpsum amount</b> (one-time investment) and <b>Monthly SIP</b>.",
         ["Lumpsum default: ₹1,00,000 — see how it grows in the Lumpsum tab",
          "SIP default: ₹10,000/month — see corpus growth in the SIP tab",
          "These are used only for illustration — not actual transactions",
          "Tip: Try ₹5,000 SIP across 5 different category funds to see diversification in action"]),
        ("3","🎯","Select Up to 5 Funds",
         "Each fund slot has two dropdowns: <b>Category</b> → <b>Fund Name</b>.",
         ["Step 1: Pick a category (e.g. Large Cap, ELSS, Gold, Index Fund)",
          "Step 2: Pick a specific fund from that category",
          "You can mix categories — e.g. Large Cap + Mid Cap + ELSS + Gold + International",
          "Leave slots as '— Skip —' if you want fewer than 5 funds",
          "Tip: Compare a fund against its benchmark index fund to test active vs passive"]),
        ("4","▶️","Click Analyse Portfolio",
         "Press the gold <b>▶ ANALYSE PORTFOLIO</b> button. The app fetches live NAV data from AMFI.",
         ["Data is fetched from api.mfapi.in (free AMFI public API — no login needed)",
          "NAV data may take 5–15 seconds depending on your internet speed",
          "Data is cached for 30 minutes — click 🔄 Refresh Scheme List to force a reload",
          "Ensure you are connected to the internet for live data"]),
        ("5","📊","Explore the 7 Analysis Tabs",
         "Navigate across tabs to view different aspects of fund performance.",
         ["📈 Growth & Drawdown — Start here. See who grew most & who fell hardest",
          "📊 Annual & Rolling — See consistency year-by-year and rolling CAGR windows",
          "⚖️ Risk-Return — Best single view: high CAGR with low volatility = top-right quadrant",
          "💳 SIP — Compare the power of systematic investing across funds",
          "💰 Lumpsum — Compare one-time investment outcomes",
          "🔗 Correlation — Check if your funds actually diversify each other",
          "📋 Scorecard — Full table: 1Y/3Y/5Y/7Y/10Y CAGR + all risk metrics + CSV export"]),
        ("6","📥","Export Your Results",
         "In the <b>Scorecard tab</b>, click <b>⬇ Export Scorecard (CSV)</b>.",
         ["The CSV includes all CAGR periods, Sharpe, Volatility, Max Drawdown, Best/Worst Year",
          "Use it in Excel for further analysis or to share with students",
          "File is named mf_scorecard_YYYYMMDD.csv automatically"]),
    ]

    for i in range(0, len(steps), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j >= len(steps): break
            num,icon,title,desc,bullets = steps[i+j]
            bhtml = "".join([f"""<div style="display:flex;gap:8px;margin-bottom:5px;">
              <span style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.8rem;margin-top:1px;">▸</span>
              <span style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.78rem;">{b}</span>
            </div>""" for b in bullets])
            with col:
                st.html(f"""
                <div style="background:{C['card']};border:1px solid {C['mid']};
                  border-radius:12px;padding:1.1rem 1.2rem;margin-bottom:.8rem;
                  border-left:4px solid {C['gold']};user-select:none;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:.6rem;">
                    <div style="background:linear-gradient(135deg,{C['blue']},{C['mid']});
                      color:{C['gold']};-webkit-text-fill-color:{C['gold']};
                      border:1px solid {C['gold']};border-radius:50%;
                      width:30px;height:30px;display:flex;align-items:center;justify-content:center;
                      font-weight:900;font-size:.95rem;flex-shrink:0;">
                      {num}
                    </div>
                    <div>
                      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
                        font-weight:800;font-size:.95rem;">{icon} {title}</div>
                    </div>
                  </div>
                  <div style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};
                    font-size:.82rem;margin-bottom:.6rem;">{desc}</div>
                  {bhtml}
                </div>
                """)

    # ── QUICK TIPS ────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="background:{C['card']};border:1px solid {C['gold']};
      border-radius:12px;padding:1.1rem 1.4rem;margin-top:.4rem;user-select:none;">
      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
        font-weight:900;font-size:1rem;margin-bottom:.8rem;">
        ⚡ Quick Reference — What to Look For
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            🏆 Consistent Outperformer
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            High CAGR across 3Y, 5Y, 7Y windows<br>
            Sharpe &gt; 1.0<br>
            Max Drawdown &lt; -35%<br>
            Positive rolling returns most of the time
          </div>
        </div>
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            ⚠️ High Return but Risky
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            High CAGR but Volatility &gt; 25%<br>
            Sharpe between 0.5–1.0<br>
            Max Drawdown worse than -50%<br>
            Fits aggressive investors only
          </div>
        </div>
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            🛡️ Defensive / Stable
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Moderate CAGR (10–14%)<br>
            Low Volatility (&lt; 15%)<br>
            Sharpe &gt; 1.2 despite moderate returns<br>
            Suits conservative / hybrid investors
          </div>
        </div>
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            🔗 Good Diversification Pair
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Correlation &lt; 0.3 between two funds<br>
            e.g. Equity + Gold, Equity + Debt<br>
            Reduces portfolio volatility meaningfully<br>
            Check Correlation tab heatmap
          </div>
        </div>
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            📉 Recovery Speed Check
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            In Drawdown chart, see how fast a fund recovers after a crash<br>
            Fast V-shaped recovery = strong fund manager<br>
            Prolonged trough = structural issue
          </div>
        </div>
        <div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.8rem;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            💳 SIP Power Check
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            A fund that looks bad on lumpsum may shine on SIP<br>
            Volatile funds benefit more from rupee-cost averaging<br>
            Compare SIP corpus vs amount invested line
          </div>
        </div>
      </div>
    </div>
    """)

    # ── SUGGESTED FUND COMBINATIONS ──────────────────────────────────────────
    st.html(f"""
    <div style="background:{C['card']};border:1px solid {C['mid']};
      border-radius:12px;padding:1.1rem 1.4rem;margin-top:.8rem;user-select:none;">
      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
        font-weight:900;font-size:1rem;margin-bottom:.8rem;">
        🧪 Suggested Comparison Sets for Classroom Use
      </div>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
        <div style="background:rgba(0,77,128,.3);border:1px solid {C['mid']};border-radius:8px;padding:.85rem;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            Set A — Active vs Passive (Large Cap)
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Fund 1: SBI Bluechip Fund (Large Cap)<br>
            Fund 2: Mirae Asset Large Cap (Large Cap)<br>
            Fund 3: UTI Nifty 50 Index Fund (Index Fund)<br>
            Fund 4: HDFC Index Fund Nifty 50 (Index Fund)<br>
            <i>Goal: Does active management beat the index?</i>
          </div>
        </div>
        <div style="background:rgba(0,77,128,.3);border:1px solid {C['mid']};border-radius:8px;padding:.85rem;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            Set B — Risk Spectrum Portfolio
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Fund 1: Nippon India Small Cap (Small Cap)<br>
            Fund 2: Axis Midcap Fund (Mid Cap)<br>
            Fund 3: SBI Bluechip Fund (Large Cap)<br>
            Fund 4: ICICI Pru Equity & Debt (Hybrid)<br>
            Fund 5: HDFC Liquid Fund (Debt)<br>
            <i>Goal: Visualise risk-return spectrum</i>
          </div>
        </div>
        <div style="background:rgba(0,77,128,.3);border:1px solid {C['mid']};border-radius:8px;padding:.85rem;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            Set C — Diversification Study
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Fund 1: Parag Parikh Flexi Cap (Flexi)<br>
            Fund 2: SBI Gold Fund (Gold)<br>
            Fund 3: Motilal Oswal Nasdaq 100 (International)<br>
            Fund 4: ICICI Pru Gilt Fund (Debt)<br>
            <i>Goal: Low correlation across asset classes</i>
          </div>
        </div>
        <div style="background:rgba(0,77,128,.3);border:1px solid {C['mid']};border-radius:8px;padding:.85rem;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:700;font-size:.82rem;margin-bottom:5px;">
            Set D — ELSS Tax Planning Comparison
          </div>
          <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;">
            Fund 1: Axis Long Term Equity (ELSS)<br>
            Fund 2: Mirae Asset ELSS (ELSS)<br>
            Fund 3: SBI Long Term Equity (ELSS)<br>
            Fund 4: ICICI Pru Long Term Equity (ELSS)<br>
            <i>Goal: Best ELSS fund for 80C tax saving</i>
          </div>
        </div>
      </div>
    </div>
    """)


    # ── HOW THE APP CALCULATES VALUES ─────────────────────────────────────
    _ht_html1 = """<div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Lumpsum Growth</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Value(t) = L × NAV(t) / NAV(t0)</div><div style="color:#8892b0;font-size:.72rem;">L = lumpsum entered. Value scales directly with NAV from start date.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">SIP Corpus</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Units(m) = SIP / NAV(m)
Corpus = Σ Units(m) × NAV(latest)</div><div style="color:#8892b0;font-size:.72rem;">Each month buys units at that month's NAV. More units at lower prices = Rupee Cost Averaging.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Period CAGR</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">CAGR = (NAV_end / NAV_start)^(1/N) - 1</div><div style="color:#8892b0;font-size:.72rem;">N = years. Annualised growth rate smoothing out interim volatility.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Daily Return</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">r(t) = NAV(t) / NAV(t-1) - 1</div><div style="color:#8892b0;font-size:.72rem;">Foundation for Volatility, Sharpe Ratio, Correlation, and Drawdown calculations.</div></div>"""
    _ht_html2 = """<div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Value</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">P(t) = Capital × Σᵢ[ wᵢ × NAVᵢ(t) / NAVᵢ(t0) ]</div><div style="color:#8892b0;font-size:.72rem;">wᵢ = weight of fund i (e.g. 0.40). Weighted blend of each fund's indexed growth.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Return</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">R_p = Σᵢ wᵢ × Rᵢ</div><div style="color:#8892b0;font-size:.72rem;">Weighted average return. Linear — no diversification benefit appears here.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Volatility</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">σ_p = √[ Σᵢ Σⱼ wᵢ wⱼ σᵢ σⱼ ρᵢⱼ ]</div><div style="color:#8892b0;font-size:.72rem;">Non-linear. When ρᵢⱼ < 1, σ_p < weighted avg σ. This IS the diversification benefit.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Sharpe</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Sharpe_p = (R_p - Rf) / σ_p</div><div style="color:#8892b0;font-size:.72rem;">Rf = 6.5% risk-free. A diversified portfolio usually achieves higher Sharpe than individual funds.</div></div>"""
    st.html(f"""
    <div style="background:#112240;border:1px solid #FFD700;border-radius:12px;
      padding:1.1rem 1.4rem;margin-top:.8rem;user-select:none;">
      <div style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-weight:900;
        font-size:1rem;margin-bottom:.8rem;">
        🔢 How the App Calculates Values — Under the Hood
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            This App — Each Fund Evaluated Independently
          </div>
          <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;
            margin-bottom:.5rem;line-height:1.5;">
            All 5 funds receive the same lumpsum and SIP. No cross-fund weight allocation yet.
          </div>
          {_ht_html1}
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            True Weighted Portfolio — The Full Framework
          </div>
          <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;
            margin-bottom:.5rem;line-height:1.5;">
            With weights w₁+w₂+…+w₅ = 1, the blended portfolio:
          </div>
          {_ht_html2}
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">Why Correlation Drives σ_p</div>
          <div style="background:rgba(0,0,0,.3);border-radius:5px;padding:.4rem .7rem;
            font-family:monospace;color:#FFD700;-webkit-text-fill-color:#FFD700;
            font-size:.76rem;margin-bottom:.4rem;white-space:pre;">ρ = +1.0  →  σ_p = weighted avg σ   (zero benefit)
ρ =  0.0  →  σ_p = √(w₁²σ₁² + w₂²σ₂²)
ρ = -1.0  →  σ_p → 0               (perfect hedge)</div>
          <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;line-height:1.5;">
            Two Large Cap funds: ρ ≈ 0.90 — almost no risk reduction.<br>
            Large Cap + Gold: ρ ≈ -0.15 — meaningful 30-35% risk reduction.<br>
            Always check the Correlation heatmap before finalising your fund mix.
          </div>
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">Reading the Correlation Tab</div>
          <div style="display:flex;flex-direction:column;gap:6px;margin-top:.3rem;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:13px;height:13px;border-radius:3px;
                background:#dc3545;flex-shrink:0;"></div>
              <span style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;">
                ρ &gt; 0.7 — High overlap. Barely reduces portfolio risk.
              </span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:13px;height:13px;border-radius:3px;
                background:#FFC107;flex-shrink:0;"></div>
              <span style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;">
                ρ 0.3–0.7 — Moderate diversification. Partial risk reduction.
              </span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:13px;height:13px;border-radius:3px;
                background:#00bfff;flex-shrink:0;"></div>
              <span style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.74rem;">
                ρ &lt; 0.3 — Excellent diversification. Significant σ_p reduction.
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
    """)



# ─── EDUCATION TAB ───────────────────────────────────────────────────────────
def education_tab():
    st.html(f"""
    <div style="background:linear-gradient(135deg,{C['blue']},{C['mid']});
      border:2px solid {C['gold']};border-radius:14px;padding:1.4rem 2rem;
      margin-bottom:1.4rem;user-select:none;">
      <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
        font-size:1.4rem;font-weight:900;margin-bottom:.3rem;">🎓 Finance Education Centre</div>
      <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-size:.9rem;">
        Concepts, formulas, and interpretation frameworks for MBA · CFA · FRM students
      </div>
    </div>
    """)

    # ── SECTION 1: KEY METRICS ────────────────────────────────────────────────
    st.html(f"""
    <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
      font-size:1.05rem;font-weight:900;margin-bottom:.6rem;user-select:none;">
      📐 Core Performance Metrics — What They Mean & How They're Calculated
    </div>
    """)

    metrics = [
        ("CAGR — Compound Annual Growth Rate",
         f"CAGR = (Ending NAV / Beginning NAV)^(1 / N) - 1",
         "The annualised return that would take the investment from its starting NAV to the ending NAV over N years, assuming reinvestment. It smooths out year-to-year volatility.",
         ["N = number of years in the period",
          "A fund with CAGR of 14% doubles in ~5.1 years (Rule of 72: 72/14 = 5.1)",
          "CAGR ignores intermediate volatility — two funds can have same CAGR with very different risk profiles",
          "Always compare CAGR with Volatility and Sharpe Ratio together"]),
        ("Volatility — Annualised Standard Deviation",
         "σ_annual = σ_daily × √252",
         "Measures how much a fund's daily returns deviate from its mean. Higher volatility means larger swings in NAV — both up and down. Annualised by multiplying daily SD by √252 (trading days in a year).",
         ["Equity funds: typically 15–25% · Debt funds: 1–5% · Gold: 12–18%",
          "Volatility alone is not bad — a fund can have high volatility but still be rewarding if CAGR compensates",
          "Volatility is symmetric — it captures both upside and downside variability",
          "Used as the denominator in Sharpe Ratio"]),
        ("Sharpe Ratio",
         f"Sharpe = (CAGR - Risk-Free Rate) / σ_annual",
         "Measures excess return per unit of total risk. A Sharpe of 1.0 means the fund earned exactly 1% excess return for every 1% of volatility. Risk-free rate assumed: 6.5% (91-day T-bill).",
         ["< 0: Fund destroyed value vs risk-free",
          "0–1: Marginal — low excess return for risk taken",
          "> 1: Good — adequate compensation for risk",
          "> 2: Excellent — rare for pure equity funds over full cycles",
          "Limitation: assumes normal distribution of returns; understates tail risk"]),
        ("Maximum Drawdown",
         "Max DD = min[(NAV_t - Peak NAV_t) / Peak NAV_t]",
         "The largest peak-to-trough decline in NAV during the period. It answers: 'What is the worst loss a patient investor would have experienced?' Critical for understanding investor psychology and risk.",
         ["Nifty 50 fell ~38% in COVID crash (Jan–Mar 2020)",
          "Small cap funds often see -50% to -60% drawdowns in bear markets",
          "Recovery time matters: a -40% drawdown needs a +67% gain to recover",
          "Good funds have smaller drawdowns AND faster V-shaped recovery"]),
        ("Rolling Returns",
         "Rolling CAGR(t, W) = (NAV_t / NAV_{{t-W}})^(1/Y) - 1",
         "CAGR calculated over a rolling window of W trading days (e.g. 756 days = 3Y), computed at every point in time. Unlike point-to-point CAGR, rolling returns show consistency across different entry points.",
         ["If 3Y rolling returns are always positive → the fund never lost money over any 3-year holding period",
          "Wide dispersion in rolling returns = performance highly dependent on entry timing",
          "Narrow, consistently positive rolling returns = low sequence-of-returns risk",
          "Best used to answer: 'Would I have made money if I invested 3 years ago at any point?'"]),
        ("SIP Return (XIRR proxy)",
         "SIP corpus = Σ (SIP_amount / NAV_t) × NAV_final",
         "Each monthly SIP buys units at that month's NAV. Total units accumulate. Final corpus = total units × last NAV. Return is expressed as (Corpus - Invested) / Invested. A true SIP return would use XIRR.",
         ["SIP benefits most from volatile funds via Rupee Cost Averaging (RCA)",
          "In falling markets, SIP buys more units at lower prices → lower average cost",
          "Volatile small/mid cap funds often have better SIP returns than lumpsum returns",
          "SIP return ≠ CAGR — it depends on the entire time path of NAVs, not just start and end"]),
    ]

    for title, formula, explanation, bullets in metrics:
        bhtml = "".join([f"""<div style="display:flex;gap:8px;margin-bottom:4px;">
          <span style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.75rem;margin-top:1px;">▸</span>
          <span style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.76rem;">{b}</span>
        </div>""" for b in bullets])
        st.html(f"""
        <div style="background:{C['card']};border:1px solid {C['mid']};
          border-radius:12px;padding:1rem 1.2rem;margin-bottom:.7rem;user-select:none;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};
            font-weight:800;font-size:.9rem;margin-bottom:.4rem;">{title}</div>
          <div style="background:rgba(0,51,102,.6);border:1px solid {C['mid']};
            border-radius:6px;padding:.45rem .8rem;margin-bottom:.5rem;
            font-family:monospace;color:{C['gold']};-webkit-text-fill-color:{C['gold']};
            font-size:.82rem;">{formula}</div>
          <div style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};
            font-size:.8rem;margin-bottom:.5rem;line-height:1.5;">{explanation}</div>
          {bhtml}
        </div>
        """)

    # ── SECTION: PORTFOLIO VALUE & WEIGHTS ──────────────────────────────────
    _edu_html1 = """<div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Lumpsum Growth</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Value(t) = L × NAV(t) / NAV(t0)</div><div style="color:#8892b0;font-size:.72rem;">L = lumpsum entered. Value scales directly with NAV from start date.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">SIP Corpus</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Units(m) = SIP / NAV(m)
Corpus = Σ Units(m) × NAV(latest)</div><div style="color:#8892b0;font-size:.72rem;">Each month buys units at that month's NAV. More units at lower prices = Rupee Cost Averaging.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Period CAGR</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">CAGR = (NAV_end / NAV_start)^(1/N) - 1</div><div style="color:#8892b0;font-size:.72rem;">N = years. Annualised growth rate smoothing out interim volatility.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Daily Return</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">r(t) = NAV(t) / NAV(t-1) - 1</div><div style="color:#8892b0;font-size:.72rem;">Foundation for Volatility, Sharpe Ratio, Correlation, and Drawdown calculations.</div></div>"""
    _edu_html2 = """<div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Value</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">P(t) = Capital × Σᵢ[ wᵢ × NAVᵢ(t) / NAVᵢ(t0) ]</div><div style="color:#8892b0;font-size:.72rem;">wᵢ = weight of fund i (e.g. 0.40). Weighted blend of each fund's indexed growth.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Return</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">R_p = Σᵢ wᵢ × Rᵢ</div><div style="color:#8892b0;font-size:.72rem;">Weighted average return. Linear — no diversification benefit appears here.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Volatility</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">σ_p = √[ Σᵢ Σⱼ wᵢ wⱼ σᵢ σⱼ ρᵢⱼ ]</div><div style="color:#8892b0;font-size:.72rem;">Non-linear. When ρᵢⱼ < 1, σ_p < weighted avg σ. This IS the diversification benefit.</div></div><div style="background:rgba(0,51,102,.5);border-radius:6px;padding:.5rem .8rem;margin-bottom:6px;"><div style="color:#FFD700;font-weight:700;font-size:.78rem;margin-bottom:3px;">Portfolio Sharpe</div><div style="font-family:monospace;color:#ADD8E6;font-size:.75rem;margin-bottom:3px;white-space:pre-line;">Sharpe_p = (R_p - Rf) / σ_p</div><div style="color:#8892b0;font-size:.72rem;">Rf = 6.5% risk-free. A diversified portfolio usually achieves higher Sharpe than individual funds.</div></div>"""
    _edu_corr  = """<tr style="border-bottom:1px solid #004d80;"><td style="color:#dc3545;padding:.45rem .8rem;font-weight:700;">+1.0</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Two similar Large Cap funds</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">16.5%</td><td style="color:#8892b0;padding:.45rem .8rem;">= Wtd Avg</td><td style="color:#8892b0;padding:.45rem .8rem;font-weight:700;">No benefit</td></tr><tr style="border-bottom:1px solid #004d80;"><td style="color:#FFC107;padding:.45rem .8rem;font-weight:700;">+0.8</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Large Cap + Mid Cap</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">15.6%</td><td style="color:#8892b0;padding:.45rem .8rem;">-0.9%</td><td style="color:#FFC107;padding:.45rem .8rem;font-weight:700;">-5.5%</td></tr><tr style="border-bottom:1px solid #004d80;"><td style="color:#28a745;padding:.45rem .8rem;font-weight:700;">+0.5</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Large Cap + Flexi Cap</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">14.3%</td><td style="color:#8892b0;padding:.45rem .8rem;">-2.2%</td><td style="color:#28a745;padding:.45rem .8rem;font-weight:700;">-13.3%</td></tr><tr style="border-bottom:1px solid #004d80;"><td style="color:#28a745;padding:.45rem .8rem;font-weight:700;">0.0</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Equity + Liquid Debt</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">11.8%</td><td style="color:#8892b0;padding:.45rem .8rem;">-4.7%</td><td style="color:#28a745;padding:.45rem .8rem;font-weight:700;">-28.5%</td></tr><tr style="border-bottom:1px solid #004d80;"><td style="color:#00bfff;padding:.45rem .8rem;font-weight:700;">-0.2</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Large Cap + Gold (typical)</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">10.8%</td><td style="color:#8892b0;padding:.45rem .8rem;">-5.7%</td><td style="color:#00bfff;padding:.45rem .8rem;font-weight:700;">-34.5%</td></tr><tr style="border-bottom:1px solid #004d80;"><td style="color:#00bfff;padding:.45rem .8rem;font-weight:700;">-1.0</td><td style="color:#e6f1ff;padding:.45rem .8rem;">Perfect hedge (theoretical)</td><td style="color:#ADD8E6;padding:.45rem .8rem;font-family:monospace;font-weight:700;">1.5%</td><td style="color:#8892b0;padding:.45rem .8rem;">-15.0%</td><td style="color:#00bfff;padding:.45rem .8rem;font-weight:700;">Perfect hedge</td></tr>"""
    _edu_strat = """<div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">Equal Weight (1/N)</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">wᵢ = 1/N  for all i</div><div style="color:#8892b0;font-size:.71rem;">Simplest. For 5 funds: 20% each. No forecasting needed. Robust in practice.</div></div><div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">Risk Parity</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">wᵢ ∝ 1/σᵢ  (normalised)</div><div style="color:#8892b0;font-size:.71rem;">Higher weight to lower-vol funds. Balances risk contribution rather than capital.</div></div><div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">Min-Variance</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">min σ_p  s.t. Σwᵢ=1, wᵢ≥0</div><div style="color:#8892b0;font-size:.71rem;">Uses full covariance matrix. Solved via quadratic programming (scipy.optimize).</div></div><div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">Max Sharpe</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">max (R_p - Rf) / σ_p</div><div style="color:#8892b0;font-size:.71rem;">Tangency portfolio on efficient frontier. Requires expected return forecasts.</div></div><div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">Goal-Based</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">User-defined by objective</div><div style="color:#8892b0;font-size:.71rem;">e.g. 50% Large Cap + 20% Mid Cap + 15% Gold + 15% Debt for balanced growth.</div></div><div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;"><div style="color:#FFD700;font-weight:700;font-size:.8rem;margin-bottom:4px;">AUM-Weighted</div><div style="font-family:monospace;color:#ADD8E6;font-size:.73rem;margin-bottom:4px;">wᵢ ∝ AUM of fund i</div><div style="color:#8892b0;font-size:.71rem;">Larger AUM funds get higher weight. Mimics passive / institutional allocation logic.</div></div>"""

    st.html(f"""
    <div style="color:#FFD700;-webkit-text-fill-color:#FFD700;
      font-size:1.05rem;font-weight:900;margin:1rem 0 .6rem;user-select:none;">
      🏗️ Portfolio Value and Weights — Formulas and Concepts
    </div>
    """)

    _pc1, _pc2 = st.columns(2)
    with _pc1:
        st.html(f"""
        <div style="background:#112240;border:1px solid #004d80;
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;
            font-weight:800;font-size:.9rem;margin-bottom:.5rem;">
            This App — How Fund Values Are Computed
          </div>
          <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;
            font-size:.78rem;margin-bottom:.6rem;line-height:1.5;">
            Each fund is evaluated independently. Same lumpsum and SIP for all 5 funds.
            No cross-fund weight allocation in the current version.
          </div>
          {_edu_html1}
        </div>
        """)
    with _pc2:
        st.html(f"""
        <div style="background:#112240;border:1px solid #004d80;
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;
            font-weight:800;font-size:.9rem;margin-bottom:.5rem;">
            True Weighted Portfolio — Full Mathematical Framework
          </div>
          <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;
            font-size:.78rem;margin-bottom:.6rem;line-height:1.5;">
            Assign weights w₁+w₂+…+w₅ = 1 across funds.
            Portfolio volatility benefits from low pairwise correlations.
          </div>
          {_edu_html2}
        </div>
        """)

    st.html(f"""
    <div style="background:#112240;border:1px solid #004d80;border-radius:12px;
      padding:1rem 1.2rem;margin-top:.7rem;user-select:none;">
      <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;
        font-weight:800;font-size:.9rem;margin-bottom:.6rem;">
        📐 Correlation vs Portfolio Volatility — Numerical Example
      </div>
      <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.78rem;margin-bottom:.7rem;">
        Two-fund equal-weight portfolio: Fund A Large Cap (σ=18%) + Fund B Gold (σ=15%), w=0.5 each.<br>
        σ_p = √(0.25×18² + 0.25×15² + 2×0.5×0.5×18×15×ρ) &nbsp;|&nbsp; Weighted avg σ = 16.5%
      </div>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:.78rem;">
          <thead>
            <tr style="background:linear-gradient(135deg,#003366,#004d80);">
              <th style="color:#FFD700;padding:.5rem .8rem;text-align:left;">Correlation ρ</th>
              <th style="color:#FFD700;padding:.5rem .8rem;text-align:left;">Scenario</th>
              <th style="color:#FFD700;padding:.5rem .8rem;text-align:left;">Portfolio σ_p</th>
              <th style="color:#FFD700;padding:.5rem .8rem;text-align:left;">vs Wtd Avg 16.5%</th>
              <th style="color:#FFD700;padding:.5rem .8rem;text-align:left;">Risk Saved</th>
            </tr>
          </thead>
          <tbody>{_edu_corr}</tbody>
        </table>
      </div>
      <div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.73rem;margin-top:.5rem;">
        ▸ ρ = -0.2 (Equity+Gold) saves ~34% portfolio risk vs two similar equity funds (ρ ≈ +1.0) at same expected return.
        Match your Correlation heatmap values against this table to quantify your diversification benefit.
      </div>
    </div>

    <div style="background:#112240;border:1px solid #004d80;border-radius:12px;
      padding:1rem 1.2rem;margin-top:.7rem;margin-bottom:.7rem;user-select:none;">
      <div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;
        font-weight:800;font-size:.9rem;margin-bottom:.6rem;">
        🎯 Weight Allocation Strategies — How Practitioners Assign wᵢ
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
        {_edu_strat}
      </div>
    </div>
    """)

    # ── SECTION 2: RISK FRAMEWORKS ────────────────────────────────────────────

    st.html(f"""
    <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
      font-size:1.05rem;font-weight:900;margin:1rem 0 .6rem;user-select:none;">
      🏗️ Risk Classification Frameworks for Indian Mutual Funds
    </div>
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.html(f"""
        <div style="background:{C['card']};border:1px solid {C['mid']};
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};
            font-weight:800;font-size:.9rem;margin-bottom:.7rem;">
            SEBI Risk-O-Meter (Riskometer)
          </div>
          {"".join([f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;">
            <div style="width:12px;height:12px;border-radius:2px;background:{col};flex-shrink:0;"></div>
            <div>
              <span style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};font-weight:700;font-size:.78rem;">{label}</span>
              <span style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.73rem;"> — {desc}</span>
            </div>
          </div>''' for label,desc,col in [
              ("Low Risk","Liquid, Overnight, Money Market funds","#28a745"),
              ("Low to Moderate","Ultra Short, Low Duration Debt","#8bc34a"),
              ("Moderate","Short/Medium Duration Debt, Balanced Advantage","#FFC107"),
              ("Moderately High","Large Cap Equity, Flexi Cap, Hybrid","#FF9800"),
              ("High","Mid Cap, Multi Cap, ELSS, Sectoral","#ff6b6b"),
              ("Very High","Small Cap, Thematic, International, Sector ETF","#dc3545"),
          ]])}
        </div>
        """)
    with c2:
        st.html(f"""
        <div style="background:{C['card']};border:1px solid {C['mid']};
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};
            font-weight:800;font-size:.9rem;margin-bottom:.7rem;">
            Volatility Benchmarks — Indian Markets
          </div>
          {"".join([f'''<div style="background:rgba(0,51,102,.4);border-radius:6px;
            padding:.45rem .8rem;margin-bottom:6px;">
            <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
              font-weight:700;font-size:.78rem;">{cat}</div>
            <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};
              font-size:.73rem;">{detail}</div>
          </div>''' for cat,detail in [
              ("Overnight / Liquid Fund","Volatility: 0.1–1.0% · Max DD: near zero"),
              ("Gilt / Long Duration Debt","Volatility: 4–8% · Sensitive to RBI rate changes"),
              ("Large Cap Equity","Volatility: 14–20% · Max DD: -30 to -45%"),
              ("Flexi / Multi Cap","Volatility: 16–22% · Max DD: -35 to -50%"),
              ("Mid Cap Equity","Volatility: 20–28% · Max DD: -45 to -55%"),
              ("Small Cap Equity","Volatility: 25–35% · Max DD: -55 to -65%"),
              ("Gold Fund","Volatility: 12–18% · Low correlation with equity"),
              ("International / Nasdaq","Volatility: 18–25% · Currency risk adds ~3–5%"),
          ]])}
        </div>
        """)

    # ── SECTION 3: PORTFOLIO THEORY ──────────────────────────────────────────
    st.html(f"""
    <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
      font-size:1.05rem;font-weight:900;margin:1rem 0 .6rem;user-select:none;">
      📚 Modern Portfolio Theory — Key Concepts
    </div>
    """)
    st.html('<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:.8rem;user-select:none;">')
    mpt_cards = [
        ("Diversification","Holding multiple low-correlation assets reduces portfolio volatility without proportionately reducing expected returns. When Corr(A,B) &lt; 1, the portfolio σ &lt; weighted average σ of individual assets.",
         f"σ_p = √(w₁²σ₁² + w₂²σ₂² + 2w₁w₂σ₁σ₂ρ₁₂)"),
        ("Efficient Frontier","The set of portfolios that offer maximum expected return for a given level of risk (or minimum risk for a given return). Portfolios below the frontier are suboptimal.",
         "Use Risk-Return tab to identify which fund sits closest to the efficient frontier"),
        ("Correlation & β","Correlation (-1 to +1) measures co-movement. Beta measures a fund's sensitivity to its benchmark. β &gt; 1 = amplifies market moves (aggressive); β &lt; 1 = dampens moves (defensive).",
         "Gold typically has ρ ≈ 0.0 to -0.2 vs equity — ideal diversifier"),
        ("Rupee Cost Averaging","SIP removes the need to time the market. By investing fixed amounts monthly, you buy more units when NAV is low and fewer when high — lowering average cost over time.",
         "RCA benefit is highest for volatile funds with long-term upward trend"),
        ("Time Value & Compounding","₹10,000/month at 14% CAGR for 20 years = ₹1.33 Crore vs ₹24L invested. The last 5 years contribute more than the first 15 — start early, stay invested.",
         "Rule of 72: Years to double = 72 / CAGR%. At 14%, money doubles every 5.1 years"),
        ("Sequence of Returns Risk","The order in which returns occur matters for SIP/SWP investors. Poor returns early in a withdrawal phase (SWP) can permanently deplete capital even if average return is positive.",
         "Drawdown chart reveals the worst sequences — key for retirement planning"),
    ]
    for ttl,desc,formula in mpt_cards:
        st.html(f"""
        <div style="background:{C['card']};border:1px solid {C['mid']};
          border-radius:10px;padding:.85rem 1rem;user-select:none;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
            font-weight:800;font-size:.82rem;margin-bottom:.4rem;">{ttl}</div>
          <div style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};
            font-size:.74rem;line-height:1.5;margin-bottom:.4rem;">{desc}</div>
          <div style="background:rgba(0,51,102,.5);border-radius:4px;
            padding:.3rem .6rem;font-size:.7rem;font-family:monospace;
            color:{C['lb']};-webkit-text-fill-color:{C['lb']};">{formula}</div>
        </div>
        """)
    st.html("</div>")

    # ── SECTION 4: SEBI CATEGORY GUIDE ───────────────────────────────────────
    st.html(f"""
    <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
      font-size:1.05rem;font-weight:900;margin:1rem 0 .6rem;user-select:none;">
      🏦 SEBI Fund Category Guide — Which Fund for Which Goal?
    </div>
    """)
    cats_guide = [
        ("Large Cap Fund","Min 80% in top 100 companies by market cap. Stable, lower volatility, benchmark-hugging. Good for conservative equity allocation.","3–5 years","Conservative to Moderate","Nifty 50 / Nifty 100"),
        ("Mid Cap Fund","Min 65% in 101st–250th companies. Higher growth potential, higher risk. Needs longer horizon for cycle smoothing.","5–7 years","Moderate to High","Nifty Midcap 150"),
        ("Small Cap Fund","Min 65% beyond 250th company. Highest potential returns, highest volatility. Severe drawdowns in bear markets.","7–10 years","High to Very High","Nifty Smallcap 250"),
        ("ELSS (Tax Saver)","Min 80% in equities. 3-year mandatory lock-in. Eligible for ₹1.5L deduction under Sec 80C. Often large/multi cap.","3+ years (locked)","High","Nifty 500 / BSE 500"),
        ("Flexi Cap Fund","Min 65% in equities — can allocate freely across large/mid/small cap. Fund manager has full flexibility.","5–7 years","Moderately High","Nifty 500"),
        ("Index Fund / ETF","Passively tracks an index (Nifty 50, Sensex, etc.). Lower expense ratio (~0.1–0.2%). Returns mirror index minus tracking error.","Any (3Y+)","Moderate to High","Same as tracked index"),
        ("Hybrid / Balanced","Mix of equity (40–80%) and debt (20–60%). Balanced Advantage Funds (BAFs) dynamically adjust allocation.","3–5 years","Moderate","Nifty 50 Hybrid Index"),
        ("Gilt Fund","Invests only in Government Securities (G-Secs). No credit risk, but high duration/interest rate risk.","3–5 years","Moderate","CRISIL Gilt Index"),
        ("Liquid Fund","Very short duration debt (&lt;91 days). Near-zero risk. Used as parking for emergency corpus or short-term cash.","&lt;3 months","Low","CRISIL Liquid Index"),
        ("Gold Fund","Invests in Gold ETFs, which track physical gold prices. Inflation hedge, low equity correlation.","5+ years","Moderately High","Domestic Gold Price"),
    ]
    rows_html = "".join([f"""
    <tr>
      <td style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.76rem;padding:.5rem .7rem;border-bottom:1px solid {C['mid']};">{cat}</td>
      <td style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};font-size:.73rem;padding:.5rem .7rem;border-bottom:1px solid {C['mid']};line-height:1.4;">{desc}</td>
      <td style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-size:.73rem;padding:.5rem .7rem;border-bottom:1px solid {C['mid']};white-space:nowrap;">{horizon}</td>
      <td style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.73rem;padding:.5rem .7rem;border-bottom:1px solid {C['mid']};">{risk}</td>
      <td style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.73rem;padding:.5rem .7rem;border-bottom:1px solid {C['mid']};">{benchmark}</td>
    </tr>""" for cat,desc,horizon,risk,benchmark in cats_guide])
    st.html(f"""
    <div style="background:{C['card']};border:1px solid {C['mid']};
      border-radius:12px;overflow:hidden;margin-bottom:.8rem;user-select:none;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:linear-gradient(135deg,{C['blue']},{C['mid']});">
            <th style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};padding:.6rem .7rem;text-align:left;font-size:.78rem;">Category</th>
            <th style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};padding:.6rem .7rem;text-align:left;font-size:.78rem;">Description</th>
            <th style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};padding:.6rem .7rem;text-align:left;font-size:.78rem;">Ideal Horizon</th>
            <th style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};padding:.6rem .7rem;text-align:left;font-size:.78rem;">Risk Level</th>
            <th style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};padding:.6rem .7rem;text-align:left;font-size:.78rem;">Benchmark</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """)

    # ── DISCLAIMER ────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="background:rgba(220,53,69,.1);border:1px solid rgba(220,53,69,.4);
      border-radius:10px;padding:.8rem 1.1rem;user-select:none;">
      <div style="color:#ff6b6b;-webkit-text-fill-color:#ff6b6b;
        font-weight:800;font-size:.85rem;margin-bottom:.35rem;">
        ⚠️ Important Disclaimer
      </div>
      <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.75rem;line-height:1.6;">
        This tool is built for <strong style="color:{C['txt']};-webkit-text-fill-color:{C['txt']};">educational purposes only</strong>
        as part of the Mountain Path — World of Finance curriculum.
        Past performance does not guarantee future returns.
        Mutual fund investments are subject to market risk.
        Please read all scheme-related documents carefully before investing.
        This is not SEBI-registered investment advice.
        All metrics are computed from historical NAV data sourced from AMFI India.
      </div>
    </div>
    """)


# ─── PORTFOLIO WEIGHTS TAB ───────────────────────────────────────────────────
def portfolio_weights_tab(funds):
    import numpy as np

    G  = C["gold"]; BL = C["blue"]; MD = C["mid"]; CA = C["card"]
    TX = C["txt"];  MU = C["muted"]; LB = C["lb"]; GR = C["grn"]; RD = C["red"]

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="background:linear-gradient(135deg,{BL},{MD});
      border:2px solid {G};border-radius:14px;padding:1.2rem 2rem;
      margin-bottom:1.2rem;user-select:none;">
      <div style="color:{G};-webkit-text-fill-color:{G};
        font-size:1.4rem;font-weight:900;margin-bottom:.3rem;">
        ⚖️ Portfolio Weights Creator
      </div>
      <div style="color:{LB};-webkit-text-fill-color:{LB};font-size:.9rem;">
        Assign weights · Auto-normalise to 100% · See blended portfolio analytics
      </div>
    </div>
    """)

    if not funds:
        st.warning("⚠️ Run the analysis first — select funds in the sidebar and click ▶ ANALYSE PORTFOLIO.")
        return

    n = len(funds)

    # ── SESSION STATE: initialise weights once per fund set ───────────────────
    fund_key = "pw_" + "_".join(str(f["code"]) for f in funds)

    def _set_weights(wlist):
        """Store weights list into session state keys."""
        for i, w in enumerate(wlist):
            st.session_state[f"pw_w{i}_{fund_key}"] = float(round(w, 1))

    def _get_weights():
        return [float(st.session_state.get(f"pw_w{i}_{fund_key}", round(100/n, 1)))
                for i in range(n)]

    # First visit — initialise equal weights
    if f"pw_w0_{fund_key}" not in st.session_state:
        _set_weights([round(100/n, 1)] * n)

    # ── STRATEGY PRESETS ──────────────────────────────────────────────────────
    slabel("⚖️", "Step 1 — Choose a Weighting Strategy",
           "Pick a preset to auto-fill weights, then adjust or auto-normalise")

    strat_col, norm_col = st.columns([3, 1])
    with strat_col:
        strategy = st.radio(
            "Strategy", ["Equal Weight (1/N)", "Risk Parity (1/σᵢ)", "Custom Weights"],
            horizontal=True, label_visibility="collapsed", key="pw_strat"
        )
    with norm_col:
        auto_norm = st.button("🔄 Auto-Normalise to 100%", key="pw_norm",
                              use_container_width=True)

    # Apply preset button — only triggers when user explicitly changes strategy
    apply_preset = st.button(
        f"▶ Apply {strategy.split('(')[0].strip()}",
        key="pw_apply", use_container_width=False
    )
    if apply_preset:
        if strategy == "Equal Weight (1/N)":
            _set_weights([round(100/n, 1)] * n)
        elif strategy == "Risk Parity (1/σᵢ)":
            sigmas = [f["m"]["vol"] for f in funds]
            inv    = [1/s for s in sigmas]
            tot    = sum(inv)
            _set_weights([round(x/tot*100, 1) for x in inv])
        # Custom: keep as-is
        st.rerun()

    # Apply auto-normalise
    if auto_norm:
        raw = _get_weights()
        tot = sum(raw)
        if tot > 0:
            _set_weights([round(w/tot*100, 1) for w in raw])
            # Fix rounding residual on largest weight
            normed = _get_weights()
            diff   = round(100.0 - sum(normed), 1)
            if diff != 0:
                max_i  = normed.index(max(normed))
                normed[max_i] = round(normed[max_i] + diff, 1)
                _set_weights(normed)
        st.rerun()

    # ── WEIGHT INPUTS ─────────────────────────────────────────────────────────
    st.html(f"""
    <div style="color:{G};-webkit-text-fill-color:{G};font-weight:700;
      font-size:.85rem;margin:.6rem 0 .3rem;user-select:none;">
      ✏️ Fine-tune Weights below — or click Auto-Normalise
    </div>
    """)

    wcols = st.columns(n)
    raw_weights = []
    for i, (ff, col) in enumerate(zip(funds, wcols)):
        with col:
            st.html(f"""
            <div style="background:{CA};border:1px solid {ff['c']};
              border-radius:8px 8px 0 0;padding:.45rem .6rem;
              text-align:center;user-select:none;">
              <div style="width:9px;height:9px;border-radius:50%;
                background:{ff['c']};margin:0 auto 3px;
                box-shadow:0 0 5px {ff['c']};"></div>
              <div style="color:{ff['c']};-webkit-text-fill-color:{ff['c']};
                font-size:.68rem;font-weight:700;white-space:nowrap;
                overflow:hidden;text-overflow:ellipsis;"
                title="{ff['name']}">
                {ff['name'][:20]}{'…' if len(ff['name'])>20 else ''}
              </div>
            </div>
            """)
            # Do NOT pass value= when key exists in session_state —
            # that causes reset conflicts. Session state owns the value.
            w_val = st.number_input(
                f"Fund {i+1} weight",
                min_value=0.0, max_value=100.0,
                step=0.5, format="%.1f",
                key=f"pw_w{i}_{fund_key}",
                label_visibility="collapsed"
            )
            raw_weights.append(w_val)

    total_w   = round(sum(raw_weights), 1)
    w_pct     = [w/100 for w in raw_weights]
    weights_ok = abs(total_w - 100.0) < 0.15

    # ── STATUS BAR ────────────────────────────────────────────────────────────
    bar_color = GR if weights_ok else RD
    bar_msg   = "✅ Weights sum to 100% — ready to compute" if weights_ok else f"⚠️ Weights sum to {total_w:.1f}% — click 🔄 Auto-Normalise"

    bar_segs = "".join([
        f'<div style="width:{w:.1f}%;background:{ff["c"]};height:100%;'
        f'display:inline-block;" title="{ff["name"][:25]}: {w:.1f}%"></div>'
        for ff, w in zip(funds, raw_weights) if w > 0
    ])
    legend_html = "".join([
        f'<div style="display:flex;align-items:center;gap:5px;">'
        f'<div style="width:10px;height:10px;border-radius:2px;background:{ff["c"]};"></div>'
        f'<span style="color:{MU};-webkit-text-fill-color:{MU};font-size:.72rem;">'
        f'{ff["name"][:22]}: {rw:.1f}%</span></div>'
        for ff, rw in zip(funds, raw_weights)
    ])

    st.html(f"""
    <div style="margin:.5rem 0 .8rem;user-select:none;">
      <div style="background:{CA};border:1px solid {bar_color};border-radius:8px;
        padding:.5rem .9rem;display:flex;justify-content:space-between;
        align-items:center;margin-bottom:.4rem;">
        <span style="color:{bar_color};-webkit-text-fill-color:{bar_color};
          font-size:.82rem;font-weight:700;">{bar_msg}</span>
        <span style="color:{MU};-webkit-text-fill-color:{MU};font-size:.78rem;">
          Total: <b style="color:{TX if weights_ok else RD};
          -webkit-text-fill-color:{TX if weights_ok else RD};">{total_w:.1f}%</b>
        </span>
      </div>
      <div style="height:12px;background:{CA};border-radius:6px;
        overflow:hidden;border:1px solid {MD};">{bar_segs}</div>
      <div style="display:flex;gap:14px;margin-top:.35rem;flex-wrap:wrap;">
        {legend_html}
      </div>
    </div>
    """)

    if not weights_ok:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(f"💡 Weights currently sum to **{total_w:.1f}%**. "
                    f"Click **🔄 Auto-Normalise to 100%** to fix instantly.")
        with c2:
            if st.button("🔄 Fix Now", key="pw_fix_now", use_container_width=True):
                tot = sum(raw_weights)
                if tot > 0:
                    normed = [round(w/tot*100, 1) for w in raw_weights]
                    diff   = round(100.0 - sum(normed), 1)
                    if diff != 0:
                        max_i = normed.index(max(normed))
                        normed[max_i] = round(normed[max_i] + diff, 1)
                    _set_weights(normed)
                st.rerun()
        return

    # ── COMPUTE PORTFOLIO ─────────────────────────────────────────────────────
    slabel("📊", "Step 2 — Blended Portfolio Analytics",
           "Weighted combination · vs individual fund performance")

    # Align NAV series to common dates
    nav_series = [ff["m"]["nav"] for ff in funds]
    combined   = pd.concat(nav_series, axis=1, join="inner").dropna()
    combined.columns = [ff["name"][:28] for ff in funds]

    if len(combined) < 20:
        st.error("❌ Insufficient overlapping NAV data across selected funds.")
        return

    indexed  = combined / combined.iloc[0] * 100
    port_idx = (indexed * w_pct).sum(axis=1)
    port_ret = port_idx.pct_change().dropna()

    nyrs  = (port_idx.index[-1] - port_idx.index[0]).days / 365.25
    tot   = (port_idx.iloc[-1] / port_idx.iloc[0]) - 1
    cagr  = (1 + tot) ** (1 / nyrs) - 1
    vol   = port_ret.std() * np.sqrt(252)
    shr   = (cagr - 0.065) / vol if vol > 0 else 0
    dd    = (port_idx - port_idx.cummax()) / port_idx.cummax()
    mxdd  = dd.min()
    wa_cagr = sum(wp * ff["m"]["cagr"] for wp, ff in zip(w_pct, funds))
    wa_vol  = sum(wp * ff["m"]["vol"]  for wp, ff in zip(w_pct, funds))
    div_ben = (wa_vol - vol) / wa_vol * 100 if wa_vol > 0 else 0

    # ── 5 METRIC CARDS ────────────────────────────────────────────────────────
    cards = [
        ("PORTFOLIO CAGR",      fp(cagr),     f"Wtd Avg: {fp(wa_cagr)}",
         GR if cagr >= wa_cagr else RD),
        ("PORTFOLIO VOLATILITY", fp(vol),      f"Wtd Avg: {fp(wa_vol)}",
         GR if vol <= wa_vol else RD),
        ("SHARPE RATIO",        f"{shr:.2f}",  "Rf = 6.5% p.a.",
         GR if shr > 1 else (G if shr > 0 else RD)),
        ("MAX DRAWDOWN",        fp(mxdd),      "Peak-to-trough",  RD),
        ("DIVERSIF. BENEFIT",   f"{div_ben:.1f}%", "σ reduction vs Wtd Avg",
         GR if div_ben > 3 else (G if div_ben > 0 else RD)),
    ]
    mcols = st.columns(5)
    for col, (lbl, val, sub, vc) in zip(mcols, cards):
        with col:
            st.html(f"""
            <div style="background:{CA};border:1px solid {MD};
              border-radius:10px;padding:.8rem;text-align:center;user-select:none;">
              <div style="color:{MU};-webkit-text-fill-color:{MU};
                font-size:.6rem;text-transform:uppercase;letter-spacing:.5px;
                margin-bottom:4px;">{lbl}</div>
              <div style="color:{vc};-webkit-text-fill-color:{vc};
                font-size:1.3rem;font-weight:900;margin-bottom:2px;">{val}</div>
              <div style="color:{MU};-webkit-text-fill-color:{MU};
                font-size:.68rem;">{sub}</div>
            </div>
            """)

    st.html(f"""<div style="height:1px;background:linear-gradient(90deg,
      transparent,{G},transparent);margin:.8rem 0;"></div>""")

    # ── SUB-TABS ──────────────────────────────────────────────────────────────
    tab_a, tab_b, tab_c, tab_d = st.tabs([
        "📈 Growth", "📉 Drawdown", "🥧 Allocation", "📋 Report"
    ])

    with tab_a:
        fig = go.Figure()
        for ff, wp in zip(funds, w_pct):
            s = indexed[ff["name"][:28]]
            fig.add_trace(go.Scatter(
                x=s.index, y=np.round(s.values, 2),
                name=f"{ff['name'][:22]} ({wp*100:.0f}%)",
                line=dict(color=ff["c"], width=1.6, dash="dot"), opacity=0.65,
                hovertemplate=f"<b>{ff['name'][:25]}</b><br>%{{x|%d %b %Y}}<br>%{{y:.1f}}<extra></extra>"
            ))
        fig.add_trace(go.Scatter(
            x=port_idx.index, y=np.round(port_idx.values, 2),
            name="⚖️ Portfolio",
            line=dict(color=G, width=3),
            hovertemplate="<b>Portfolio</b><br>%{x|%d %b %Y}<br>%{y:.1f}<extra></extra>"
        ))
        fig.update_layout(**PL("📈  Blended Portfolio vs Individual Funds (Indexed to 100)"))
        fig.update_yaxes(title_text="Indexed NAV")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab_b:
        fig2 = go.Figure()
        for ff, wp in zip(funds, w_pct):
            s  = indexed[ff["name"][:28]]
            di = (s - s.cummax()) / s.cummax() * 100
            fig2.add_trace(go.Scatter(
                x=di.index, y=np.round(di.values, 2),
                name=f"{ff['name'][:22]} ({wp*100:.0f}%)",
                line=dict(color=ff["c"], width=1.4, dash="dot"), opacity=0.6,
                hovertemplate=f"<b>{ff['name'][:25]}</b><br>DD: %{{y:.2f}}%<extra></extra>"
            ))
        pdd = (port_idx - port_idx.cummax()) / port_idx.cummax() * 100
        fig2.add_trace(go.Scatter(
            x=pdd.index, y=np.round(pdd.values, 2),
            name="⚖️ Portfolio", fill="tozeroy",
            line=dict(color=G, width=2.5),
            hovertemplate="<b>Portfolio DD</b>: %{y:.2f}%<extra></extra>"
        ))
        fig2.update_layout(**PL("📉  Portfolio Drawdown vs Individual Funds"))
        fig2.update_yaxes(title_text="Drawdown %")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with tab_c:
        pc1, pc2 = st.columns(2)
        with pc1:
            fig3 = go.Figure(go.Pie(
                labels=[ff["name"][:28] for ff in funds],
                values=[round(wp*100, 1) for wp in w_pct],
                hole=0.52,
                marker=dict(colors=[ff["c"] for ff in funds],
                            line=dict(color=CA, width=2)),
                textfont=dict(color=TX, size=11),
                hovertemplate="<b>%{label}</b><br>Weight: %{value:.1f}%<extra></extra>"
            ))
            fig3.add_annotation(text=f"<b>{n} Funds</b>", x=0.5, y=0.5,
                                font=dict(color=G, size=14), showarrow=False)
            fig3.update_layout(
                height=340, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color=TX),
                title=dict(text="🥧  Allocation Breakdown",
                           font=dict(color=G, size=13), x=0.01),
                legend=dict(bgcolor=f"rgba(17,34,64,.85)", bordercolor=MD,
                            borderwidth=1, font=dict(color=TX, size=10)),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        with pc2:
            vc_list  = [round(wp * ff["m"]["vol"] * 100, 2) for wp, ff in zip(w_pct, funds)]
            fig4 = go.Figure(go.Bar(
                x=[ff["name"][:20] for ff in funds],
                y=vc_list,
                marker_color=[ff["c"] for ff in funds],
                text=[f"{v:.1f}%" for v in vc_list],
                textposition="outside", textfont=dict(color=TX),
                hovertemplate="<b>%{x}</b><br>wᵢσᵢ = %{y:.2f}%<extra></extra>"
            ))
            fig4.add_hline(y=wa_vol*100, line_dash="dash", line_color=MU,
                           annotation_text=f"Wtd Avg σ = {wa_vol*100:.1f}%",
                           annotation_font=dict(color=MU, size=10))
            fig4.update_layout(
                height=340,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,34,64,.55)",
                font=dict(family="Inter", color=TX),
                title=dict(text="📊  Volatility Contribution (wᵢ × σᵢ)",
                           font=dict(color=G, size=13), x=0.01),
                xaxis=dict(tickfont=dict(color=MU, size=9),
                           gridcolor="rgba(0,77,128,.3)"),
                yaxis=dict(tickfont=dict(color=MU), title_text="wᵢσᵢ (%)",
                           title_font=dict(color=MU),
                           gridcolor="rgba(0,77,128,.3)"),
                margin=dict(l=42, r=16, t=40, b=60), showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

            div_clr = GR if div_ben > 5 else (G if div_ben > 0 else RD)
            st.html(f"""
            <div style="background:{CA};border:1px solid {div_clr};
              border-radius:8px;padding:.65rem 1rem;text-align:center;user-select:none;">
              <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.68rem;">
                Diversification Benefit</div>
              <div style="color:{div_clr};-webkit-text-fill-color:{div_clr};
                font-size:1.35rem;font-weight:900;">{div_ben:.1f}%</div>
              <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.68rem;">
                Portfolio σ {fp(vol)} vs Wtd Avg σ {fp(wa_vol)}</div>
            </div>
            """)

    with tab_d:
        slabel("📋", "Portfolio Weight Report", "Full breakdown + CSV export")

        rows = []
        for ff, wp in zip(funds, w_pct):
            m = ff["m"]
            rows.append({
                "Fund":        ff["name"][:40],
                "Weight":      f"{wp*100:.1f}%",
                "Wtd CAGR":   fp(wp * m["cagr"]),
                "Fund CAGR":  fp(m["cagr"]),
                "Fund σ":     fp(m["vol"]),
                "Wtd σ":      fp(wp * m["vol"]),
                "Sharpe":     f"{m['sharpe']:.2f}",
                "Max DD":     fp(m["mxdd"]),
            })
        rows.append({
            "Fund": "⚖️ BLENDED PORTFOLIO",
            "Weight": "100%",
            "Wtd CAGR": fp(cagr),
            "Fund CAGR": fp(cagr),
            "Fund σ": fp(vol),
            "Wtd σ": fp(vol),
            "Sharpe": f"{shr:.2f}",
            "Max DD": fp(mxdd),
        })
        df_rep = pd.DataFrame(rows).set_index("Fund")
        st.dataframe(df_rep, use_container_width=True,
                     column_config={c: st.column_config.TextColumn(c)
                                    for c in df_rep.columns})

        buf = io.BytesIO(); df_rep.to_csv(buf)
        st.download_button("⬇ Export Portfolio Report (CSV)", data=buf.getvalue(),
            file_name=f"portfolio_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv", key="dl_wt")

        formula_str = " + ".join([
            f"{wp*100:.0f}%×{ff['name'][:14]}" for ff, wp in zip(funds, w_pct)
        ])
        st.html(f"""
        <div style="background:{CA};border:1px solid {MD};border-radius:8px;
          padding:.8rem 1rem;margin-top:.6rem;user-select:none;">
          <div style="color:{G};-webkit-text-fill-color:{G};font-weight:700;
            font-size:.82rem;margin-bottom:.4rem;">Your Portfolio Formula</div>
          <div style="font-family:monospace;color:{LB};-webkit-text-fill-color:{LB};
            font-size:.78rem;line-height:1.7;word-break:break-word;">
            P(t) = {formula_str}
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};
            font-size:.72rem;margin-top:.4rem;">
            CAGR: {fp(cagr)} &nbsp;|&nbsp; σ: {fp(vol)} &nbsp;|&nbsp;
            Sharpe: {shr:.2f} &nbsp;|&nbsp; Max DD: {fp(mxdd)} &nbsp;|&nbsp;
            Diversif. Benefit: {div_ben:.1f}%
          </div>
        </div>
        """)


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    hero()
    with st.spinner("🔄 Loading AMFI scheme list…"):
        result = load_schemes()
        schemes, api_status = result if isinstance(result, tuple) else (result, "live")
        catdf = categorize(schemes)
    is_demo = str(api_status).startswith("demo")
    if schemes.empty:
        st.error("❌ Could not load scheme data. Check your internet connection and try again.")
        st.info("💡 The app connects to **api.mfapi.in** (free AMFI API). Make sure it is accessible from your machine.")
        return
    if is_demo:
        err_detail = str(api_status).replace("demo|","")
        st.warning(f"⚠️ **Demo Mode** — AMFI API unreachable. Showing 30 curated funds only.\n\n{err_detail}")

    sels,start,end,lump,sip,run=sidebar(schemes,catdf)

    st.html(f"""
    <div style="background:{C['card']};border:1px solid {C['mid']};border-radius:8px;
      padding:.42rem 1rem;margin-bottom:.8rem;
      display:flex;justify-content:space-between;align-items:center;user-select:none;">
      <span style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.76rem;">
        {'📡 Live data · '+str(len(schemes))+' AMFI schemes · mfapi.in' if not is_demo else '⚠️ Demo Mode · '+str(len(schemes))+' curated funds · connect to mfapi.in for full access'}
      </span>
      <span style="color:{'#28a745' if sels else C['muted']};
        -webkit-text-fill-color:{'#28a745' if sels else C['muted']};
        font-size:.76rem;font-weight:700;">
        {'● '+str(len(sels))+' fund(s) selected' if sels else '○ No funds selected'}
      </span>
    </div>
    """)

    # ── SESSION STATE: persist funds across widget interactions ──────────────
    # Build a cache key from current selection so changing funds invalidates cache
    sel_key = str([(s["code"], start, end, lump, sip) for s in sels]) if sels else ""

    if run and sels:
        # User clicked Analyse — fetch fresh data
        funds = []
        prog = st.progress(0, "Fetching NAV data from AMFI…")
        for i, s in enumerate(sels):
            prog.progress((i+1)/len(sels), f"Loading {s['name'][:45]}…")
            nav, _ = load_nav(s["code"], start, end)
            if nav is not None and len(nav) >= 20:
                m = compute(nav, lump, sip)
                if m: funds.append({"name": s["name"], "c": s["c"], "m": m, "code": s["code"]})
        prog.empty()
        if not funds:
            st.error("❌ No NAV data. Try different funds or wider date range.")
            st.session_state.pop("funds", None)
            st.session_state.pop("funds_key", None)
            return
        # Store in session state
        st.session_state["funds"]     = funds
        st.session_state["funds_key"] = sel_key

    elif "funds" in st.session_state and st.session_state.get("funds_key") == sel_key:
        # Widget interaction re-run — restore funds from session state
        funds = st.session_state["funds"]

    elif "funds" in st.session_state and sels:
        # Selection changed but user hasn't re-run — show stale data with a notice
        funds = st.session_state["funds"]
        st.info("💡 Fund selection or parameters changed. Click **▶ ANALYSE PORTFOLIO** to refresh.")

    else:
        # No data at all — show welcome
        welcome()
        return

    if not funds:
        welcome()
        return

    slabel("📊","Fund Performance Snapshot",
           f"Period: {start} → {end}  ·  Lumpsum: {fi(lump)}  ·  SIP: {fi(sip)}/month")
    snapshot_row(funds)
    st.html(f"""<div style="height:1px;background:linear-gradient(90deg,transparent,{C['gold']},transparent);margin:1rem 0;"></div>""")

    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10=st.tabs([
        "📈 Growth & Drawdown","📊 Annual & Rolling",
        "⚖️ Risk-Return","💳 SIP","💰 Lumpsum","🔗 Correlation","📋 Scorecard",
        "📖 How to Use","🎓 Education","⚖️ Portfolio Weights"
    ])

    with t1:
        st.plotly_chart(ch_nav(funds),use_container_width=True,config={"displayModeBar":False})
        st.plotly_chart(ch_dd(funds), use_container_width=True,config={"displayModeBar":False})

    with t2:
        st.plotly_chart(ch_annual(funds),use_container_width=True,config={"displayModeBar":False})
        c1,c2=st.columns([4,1])
        with c2:
            win=st.select_slider("Window",options=[1,2,3,5,7,10],value=3,key="rw")
        st.plotly_chart(ch_rolling(funds,win),use_container_width=True,config={"displayModeBar":False})
        st.plotly_chart(ch_violin(funds),use_container_width=True,config={"displayModeBar":False})

    with t3:
        st.plotly_chart(ch_rr(funds),use_container_width=True,config={"displayModeBar":False})
        st.html(f"""
        <div style="background:{C['card']};border:1px solid {C['mid']};border-radius:10px;
          padding:1rem 1.2rem;user-select:none;">
          <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
            font-weight:800;font-size:.9rem;margin-bottom:.6rem;">Risk Metrics — Interpretation Guide</div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
            <div>
              <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.8rem;margin-bottom:3px;">Sharpe Ratio</div>
              <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.74rem;">&gt;2 Excellent · &gt;1 Good · 0–1 Marginal · &lt;0 Destroys value<br><em>Risk-free: 6.5% p.a.</em></div>
            </div>
            <div>
              <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.8rem;margin-bottom:3px;">Annualised Volatility</div>
              <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.74rem;">SD of daily returns × √252<br>Equity: 15–25% · Debt: 1–5% · Gold: 12–18%</div>
            </div>
            <div>
              <div style="color:{C['lb']};-webkit-text-fill-color:{C['lb']};font-weight:700;font-size:.8rem;margin-bottom:3px;">Max Drawdown</div>
              <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.74rem;">Peak-to-trough fall in the period<br>Key stress-test & psychology metric</div>
            </div>
          </div>
        </div>
        """)

    with t4:
        st.plotly_chart(ch_sip(funds,sip),use_container_width=True,config={"displayModeBar":False})
        slabel("📋","SIP Returns Summary")
        df_s=sip_tbl(funds); st.dataframe(df_s,use_container_width=True,
            column_config={c:st.column_config.TextColumn(c) for c in df_s.columns})

    with t5:
        st.plotly_chart(ch_lump(funds),use_container_width=True,config={"displayModeBar":False})
        slabel("📋","Lumpsum Returns Summary")
        df_l=lump_tbl(funds); st.dataframe(df_l,use_container_width=True,
            column_config={c:st.column_config.TextColumn(c) for c in df_l.columns})

    with t6:
        if len(funds)>=2:
            cf=ch_corr(funds)
            if cf: st.plotly_chart(cf,use_container_width=True,config={"displayModeBar":False})
            st.html(f"""
            <div style="background:{C['card']};border:1px solid {C['mid']};border-radius:8px;
              padding:.8rem 1.1rem;user-select:none;">
              <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
                font-weight:700;font-size:.85rem;margin-bottom:5px;">Correlation Interpretation</div>
              <div style="display:flex;gap:2rem;">
                <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.77rem;">
                  <span style="color:{C['grn']};-webkit-text-fill-color:{C['grn']};">▪</span> &lt;0.3 = Excellent diversification</div>
                <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.77rem;">
                  <span style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};">▪</span> 0.3–0.7 = Moderate overlap</div>
                <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.77rem;">
                  <span style="color:{C['red']};-webkit-text-fill-color:{C['red']};">▪</span> &gt;0.7 = High redundancy</div>
              </div>
            </div>
            """)
        else: st.info("Select at least 2 funds to view correlation.")

    with t7:
        slabel("📋","Comprehensive Performance Scorecard",
               "1Y · 3Y · 5Y · 7Y · 10Y · Sharpe · Volatility · Drawdown · Best/Worst Year")
        sc=scorecard(funds)
        st.dataframe(sc,use_container_width=True,
            column_config={c:st.column_config.TextColumn(c) for c in sc.columns})
        buf=io.BytesIO(); sc.to_csv(buf)
        st.download_button("⬇ Export Scorecard (CSV)",data=buf.getvalue(),
            file_name=f"mf_scorecard_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",key="dl")


    with t8:
        how_to_use_tab()

    with t9:
        education_tab()

    with t10:
        portfolio_weights_tab(funds)

    st.html(f"""
    <div style="background:linear-gradient(135deg,{C['blue']},{C['mid']});
      border:1px solid {C['gold']};border-radius:12px;padding:1rem 1.5rem;
      margin-top:1.5rem;display:flex;justify-content:space-between;align-items:center;user-select:none;">
      <div>
        <div style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};
          font-weight:900;font-size:1rem;">🏔️ THE MOUNTAIN PATH · World of Finance</div>
        <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.71rem;margin-top:2px;">
          Prof. V. Ravichandran · 28+ Years Corporate Finance & Banking · 10+ Years Academic Excellence</div>
        <div style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.67rem;">
          Data: AMFI India via mfapi.in · For Educational Purposes Only · Not Investment Advice</div>
      </div>
      <div style="display:flex;gap:1.5rem;align-items:center;">
        <a href="https://www.linkedin.com/in/trichyravis" target="_blank"
          style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:800;font-size:.85rem;text-decoration:none;">LinkedIn ↗</a>
        <a href="https://github.com/trichyravis" target="_blank"
          style="color:{C['gold']};-webkit-text-fill-color:{C['gold']};font-weight:800;font-size:.85rem;text-decoration:none;">GitHub ↗</a>
      </div>
    </div>
    """)

if __name__=="__main__":
    main()
