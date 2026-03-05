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

# ─── AMFI DATA ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_schemes():
    try:
        r = requests.get("https://api.mfapi.in/mf", timeout=15)
        df = pd.DataFrame(r.json(), columns=["scheme_code", "scheme_name"])
        df["scheme_code"] = df["scheme_code"].astype(int)
        return df
    except:
        return pd.DataFrame(columns=["scheme_code","scheme_name"])

@st.cache_data(ttl=1800, show_spinner=False)
def load_nav(code:int, start:str, end:str):
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=20)
        j = r.json()
        df = pd.DataFrame(j["data"])
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna().sort_values("date").set_index("date")
        df = df[(df.index >= start) & (df.index <= end)]
        return df["nav"], j.get("meta",{}).get("scheme_name","Fund")
    except:
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
    fig.update_layout(**PL("⚖️  Risk–Return Map  (bubble size ∝ Sharpe)"),showlegend=False,height=430)
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
    fig.update_layout(**PL("🎻  Daily Returns Distribution"),height=380)
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

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    hero()
    with st.spinner("🔄 Loading AMFI scheme list…"):
        schemes=load_schemes(); catdf=categorize(schemes)
    if schemes.empty:
        st.error("❌ Could not fetch AMFI data."); return

    sels,start,end,lump,sip,run=sidebar(schemes,catdf)

    st.html(f"""
    <div style="background:{C['card']};border:1px solid {C['mid']};border-radius:8px;
      padding:.42rem 1rem;margin-bottom:.8rem;
      display:flex;justify-content:space-between;align-items:center;user-select:none;">
      <span style="color:{C['muted']};-webkit-text-fill-color:{C['muted']};font-size:.76rem;">
        📡&nbsp;Live data · {len(schemes):,} AMFI schemes · mfapi.in
      </span>
      <span style="color:{'#28a745' if sels else C['muted']};
        -webkit-text-fill-color:{'#28a745' if sels else C['muted']};
        font-size:.76rem;font-weight:700;">
        {'● '+str(len(sels))+' fund(s) selected' if sels else '○ No funds selected'}
      </span>
    </div>
    """)

    if not run: welcome(); return
    if not sels: st.warning("⚠️ Select at least one fund."); return

    funds=[]
    prog=st.progress(0,"Fetching NAV data from AMFI…")
    for i,s in enumerate(sels):
        prog.progress((i+1)/len(sels),f"Loading {s['name'][:45]}…")
        nav,_=load_nav(s["code"],start,end)
        if nav is not None and len(nav)>=20:
            m=compute(nav,lump,sip)
            if m: funds.append({"name":s["name"],"c":s["c"],"m":m,"code":s["code"]})
    prog.empty()

    if not funds: st.error("❌ No NAV data. Try different funds or wider date range."); return

    slabel("📊","Fund Performance Snapshot",
           f"Period: {start} → {end}  ·  Lumpsum: {fi(lump)}  ·  SIP: {fi(sip)}/month")
    snapshot_row(funds)
    st.html(f"""<div style="height:1px;background:linear-gradient(90deg,transparent,{C['gold']},transparent);margin:1rem 0;"></div>""")

    t1,t2,t3,t4,t5,t6,t7=st.tabs([
        "📈 Growth & Drawdown","📊 Annual & Rolling",
        "⚖️ Risk-Return","💳 SIP","💰 Lumpsum","🔗 Correlation","📋 Scorecard"
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
