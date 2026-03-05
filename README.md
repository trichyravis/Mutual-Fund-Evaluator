# 🏔️ MF Fund Portfolio Evaluator
### The Mountain Path — World of Finance
**Prof. V. Ravichandran** | 28+ Years Corporate Finance | 10+ Years Academic Excellence

---

## Overview
A professional Streamlit application that fetches **live mutual fund NAV data from AMFI India** via the public `mfapi.in` API and lets you compare up to 5 funds across comprehensive analytics.

## Features
| Module | Details |
|---|---|
| 📈 NAV Growth | Indexed to 100 comparison chart across all selected funds |
| 📊 Annual Returns | Year-on-year grouped bar chart |
| 🔄 Rolling CAGR | Adjustable window: 1 / 2 / 3 / 5 / 7 / 10 years |
| 📉 Drawdown | Peak-to-trough loss history for each fund |
| ⚖️ Risk-Return | Volatility vs CAGR scatter with Sharpe bubble sizing |
| 💳 SIP Tracker | Monthly SIP corpus growth with invested line |
| 💰 Lumpsum Growth | One-time investment value over period |
| 🔗 Correlation | Daily return correlation heatmap (diversification insight) |
| 🎻 Distribution | Daily return violin charts |
| 📋 Scorecard | Full 1Y/3Y/5Y/7Y/10Y CAGR · Sharpe · Volatility · Max DD · Best/Worst Year |
| ⬇ Export | Download full scorecard as CSV |

## Fund Categories (13)
Large Cap · Mid Cap · Small Cap · ELSS/Tax · Flexi/Multi Cap ·
Index Fund · ETF · Debt/Liquid · Hybrid · Gold/Commodity ·
International · Sectoral · Thematic

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open in browser
```
http://localhost:8501
```

## How to Use
1. **Set Date Range** — default Jan 2015 to today
2. **Set Investment** — lumpsum amount + monthly SIP
3. **Select up to 5 funds** — each fund has its own Category filter + Fund Name dropdown
4. Click **▶ ANALYSE PORTFOLIO**
5. Navigate the 7 analysis tabs

## Data Source
- **AMFI India** via `https://api.mfapi.in/mf` (free, public API)
- ~18,000+ schemes available
- NAV data updated daily
- No API key required

## Design
Mountain Path colour palette:
- Dark Blue: `#003366`
- Mid Blue: `#004d80`  
- Gold: `#FFD700`
- Card: `#112240`
- Background: `linear-gradient(135deg, #1a2332, #243447, #2a3f5f)`

---
*For educational purposes only. Not investment advice.*

**LinkedIn:** https://www.linkedin.com/in/trichyravis  
**GitHub:** https://github.com/trichyravis
