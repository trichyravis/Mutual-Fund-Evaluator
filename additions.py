# This file generates the two HTML blocks as plain Python strings
# then patches them into app.py safely

G   = "#FFD700"
BL  = "#003366"
MD  = "#004d80"
CA  = "#112240"
TX  = "#e6f1ff"
MU  = "#8892b0"
LB  = "#ADD8E6"
GR  = "#28a745"
RD  = "#dc3545"

def formula_box(label, formula, note):
    return f"""<div style="background:rgba(0,51,102,.5);border-radius:6px;
      padding:.5rem .8rem;margin-bottom:6px;">
      <div style="color:{G};-webkit-text-fill-color:{G};
        font-weight:700;font-size:.78rem;margin-bottom:3px;">{label}</div>
      <div style="font-family:monospace;color:{LB};
        -webkit-text-fill-color:{LB};font-size:.75rem;margin-bottom:3px;white-space:pre-line;">{formula}</div>
      <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.72rem;">{note}</div>
    </div>"""

def strat_card(strat, formula, desc):
    return f"""<div style="background:rgba(0,51,102,.45);border-radius:8px;padding:.75rem;">
      <div style="color:{G};-webkit-text-fill-color:{G};
        font-weight:700;font-size:.8rem;margin-bottom:4px;">{strat}</div>
      <div style="font-family:monospace;color:{LB};-webkit-text-fill-color:{LB};
        font-size:.73rem;margin-bottom:4px;">{formula}</div>
      <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.71rem;">{desc}</div>
    </div>"""

def corr_row(rho, scenario, sigma, vs, saving, rclr, sclr):
    return f"""<tr style="border-bottom:1px solid {MD};">
      <td style="color:{rclr};-webkit-text-fill-color:{rclr};padding:.45rem .8rem;font-weight:700;">{rho}</td>
      <td style="color:{TX};-webkit-text-fill-color:{TX};padding:.45rem .8rem;">{scenario}</td>
      <td style="color:{LB};-webkit-text-fill-color:{LB};padding:.45rem .8rem;font-family:monospace;font-weight:700;">{sigma}</td>
      <td style="color:{MU};-webkit-text-fill-color:{MU};padding:.45rem .8rem;">{vs}</td>
      <td style="color:{sclr};-webkit-text-fill-color:{sclr};padding:.45rem .8rem;font-weight:700;">{saving}</td>
    </tr>"""

# ── BLOCK 1: How to Use — Calculation section ──────────────────────────────
app_calc_boxes = (
    formula_box("Lumpsum Growth",
        "Value(t) = L x NAV(t) / NAV(t0)",
        "L = lumpsum invested. Value scales directly with NAV movement from start date.") +
    formula_box("SIP Corpus",
        "Units(m) = SIP / NAV(m)\nCorpus = sum(Units) x NAV(latest)",
        "Each month buys units at that month NAV. More units when NAV is low — Rupee Cost Averaging.") +
    formula_box("Period CAGR",
        "CAGR = (NAV_end / NAV_start)^(1/N) - 1",
        "N = years. Smoothed annualised return ignoring interim volatility.") +
    formula_box("Daily Return",
        "r(t) = NAV(t)/NAV(t-1) - 1",
        "Used to compute Volatility, Sharpe, Correlation, and Drawdown.")
)

true_portfolio_boxes = (
    formula_box("Portfolio Value at time t",
        "P(t) = Capital x sum[ wi x NAVi(t)/NAVi(t0) ]",
        "Weighted sum of each fund's growth. wi = fraction of total capital allocated to fund i.") +
    formula_box("Portfolio Return",
        "R_p = sum(wi x Ri)",
        "Simple weighted average of individual returns. Linear — no diversification benefit here.") +
    formula_box("Portfolio Volatility",
        "sig_p = sqrt[ sum_ij(wi wj si sj rho_ij) ]",
        "Non-linear. When rho_ij < 1, sig_p < weighted avg sigma. THIS is the diversification benefit.") +
    formula_box("Portfolio Sharpe",
        "Sharpe_p = (R_p - Rf) / sig_p",
        "A well-diversified portfolio achieves higher Sharpe than most of its individual components.")
)

HOW_TO_CALC_SECTION = f"""
    # ── HOW THE APP CALCULATES VALUES ────────────────────────────────────────
    st.html(\"\"\"
    <div style="background:{CA};border:1px solid {G};
      border-radius:12px;padding:1.1rem 1.4rem;margin-top:.8rem;user-select:none;">
      <div style="color:{G};-webkit-text-fill-color:{G};
        font-weight:900;font-size:1rem;margin-bottom:.8rem;">
        🔢 How the App Calculates Values — Under the Hood
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            This App — Independent Fund Evaluation
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;
            margin-bottom:.6rem;line-height:1.5;">
            Each fund receives the same lumpsum and SIP. No cross-fund weighting.
          </div>
          {app_calc_boxes}
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            True Weighted Portfolio Framework
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;
            margin-bottom:.6rem;line-height:1.5;">
            With weights w1+w2+...+w5 = 1, the blended portfolio:
          </div>
          {true_portfolio_boxes}
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            Why Correlation Changes Everything
          </div>
          <div style="background:rgba(0,0,0,.3);border-radius:5px;padding:.4rem .7rem;
            font-family:monospace;color:{G};-webkit-text-fill-color:{G};
            font-size:.77rem;margin-bottom:.4rem;">
            rho=1.0  → sig_p = weighted avg sigma (no benefit)
            rho=0.0  → sig_p = sqrt(w1^2 s1^2 + w2^2 s2^2)
            rho=-1.0 → sig_p → 0 (perfect hedge)
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;line-height:1.5;">
            Two similar Large Cap funds: rho ≈ 0.90 — almost no risk reduction.
            Large Cap + Gold: rho ≈ -0.10 to -0.20 — meaningful 25-35% risk reduction.
            Always check the Correlation heatmap before finalising your fund mix.
          </div>
        </div>

        <div style="background:rgba(0,51,102,.35);border-radius:8px;padding:.9rem;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};font-weight:700;
            font-size:.83rem;margin-bottom:.5rem;">
            Reading the Correlation Tab Correctly
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;line-height:1.5;">
            The heatmap shows pairwise daily-return correlations.
          </div>
          <div style="margin-top:.4rem;">
            <div style="display:flex;gap:8px;margin-bottom:4px;align-items:center;">
              <div style="width:14px;height:14px;border-radius:3px;background:{RD};flex-shrink:0;"></div>
              <span style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;">
                rho > 0.7 — High overlap. Adding this fund barely reduces risk.
              </span>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:4px;align-items:center;">
              <div style="width:14px;height:14px;border-radius:3px;background:{G};flex-shrink:0;"></div>
              <span style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;">
                rho 0.3-0.7 — Moderate diversification. Partial risk reduction.
              </span>
            </div>
            <div style="display:flex;gap:8px;margin-bottom:4px;align-items:center;">
              <div style="width:14px;height:14px;border-radius:3px;background:#00bfff;flex-shrink:0;"></div>
              <span style="color:{MU};-webkit-text-fill-color:{MU};font-size:.74rem;">
                rho < 0.3 — Excellent diversification. Significant portfolio risk reduction.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    \"\"\")

"""

# ── BLOCK 2: Education tab — Portfolio Value & Weights ─────────────────────
corr_rows = (
    corr_row("+1.0", "Two similar Large Cap funds", "16.5%", "= Wtd Avg", "No benefit", RD, MU) +
    corr_row("+0.8", "Large Cap + Mid Cap", "15.6%", "-0.9%", "-5.5%", "#FFC107", "#FFC107") +
    corr_row("+0.5", "Large Cap + Flexi Cap", "14.3%", "-2.2%", "-13.3%", GR, GR) +
    corr_row("0.0",  "Equity + Liquid Debt", "11.8%", "-4.7%", "-28.5%", GR, GR) +
    corr_row("-0.2", "Large Cap + Gold (typical)", "10.8%", "-5.7%", "-34.5%", "#00bfff", "#00bfff") +
    corr_row("-1.0", "Perfect hedge (theoretical)", "1.5%", "-15.0%", "Perfect hedge", "#00bfff", "#00bfff")
)

strat_cards = (
    strat_card("Equal Weight (1/N)", "wi = 1/N  for all i",
        "Simplest strategy. For 5 funds: 20% each. No forecasting needed. Surprisingly robust.") +
    strat_card("Risk Parity", "wi proportional to 1/sigma_i",
        "Higher weight to lower-volatility funds. Balances risk contribution rather than capital.") +
    strat_card("Min-Variance Portfolio", "min sig_p  s.t. sum(wi)=1, wi>=0",
        "Uses full covariance matrix. Solved via quadratic programming. Minimises total risk.") +
    strat_card("Max Sharpe Portfolio", "max (R_p - Rf) / sig_p",
        "Finds the tangency portfolio on the efficient frontier. Requires return forecasts.") +
    strat_card("Goal-Based Weights", "User-defined by objective",
        "e.g. 50% Large Cap + 20% Mid + 15% Gold + 15% Debt for balanced long-term growth.") +
    strat_card("Market Cap / AUM Weights", "wi proportional to AUM_i",
        "Mimics institutional allocation. Larger AUM funds get higher weight — passive logic.")
)

EDU_PORTFOLIO_SECTION = f"""
    # ── PORTFOLIO VALUE & WEIGHTS ────────────────────────────────────────────
    st.html(\"\"\"
    <div style="color:{G};-webkit-text-fill-color:{G};
      font-size:1.05rem;font-weight:900;margin:1rem 0 .6rem;user-select:none;">
      🏗️ Portfolio Value and Weights — Formulas and Concepts
    </div>
    \"\"\")

    _c1, _c2 = st.columns(2)
    with _c1:
        st.html(\"\"\"
        <div style="background:{CA};border:1px solid {MD};
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};
            font-weight:800;font-size:.9rem;margin-bottom:.5rem;">
            This App — How Fund Values Are Computed
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};
            font-size:.78rem;margin-bottom:.6rem;line-height:1.5;">
            Each fund is evaluated independently. All 5 funds receive the same
            lumpsum and SIP — no cross-fund weight allocation currently.
          </div>
          {app_calc_boxes}
        </div>
        \"\"\")

    with _c2:
        st.html(\"\"\"
        <div style="background:{CA};border:1px solid {MD};
          border-radius:12px;padding:1rem 1.2rem;user-select:none;">
          <div style="color:{LB};-webkit-text-fill-color:{LB};
            font-weight:800;font-size:.9rem;margin-bottom:.5rem;">
            True Weighted Portfolio — The Full Framework
          </div>
          <div style="color:{MU};-webkit-text-fill-color:{MU};
            font-size:.78rem;margin-bottom:.6rem;line-height:1.5;">
            Assign weights w1+w2+...+w5 = 1 and the blended portfolio becomes:
          </div>
          {true_portfolio_boxes}
        </div>
        \"\"\")

    st.html(\"\"\"
    <div style="background:{CA};border:1px solid {MD};
      border-radius:12px;padding:1rem 1.2rem;margin-top:.7rem;user-select:none;">
      <div style="color:{LB};-webkit-text-fill-color:{LB};
        font-weight:800;font-size:.9rem;margin-bottom:.7rem;">
        📐 How Correlation Drives Portfolio Volatility — Numerical Example
      </div>
      <div style="color:{MU};-webkit-text-fill-color:{MU};font-size:.78rem;margin-bottom:.7rem;">
        Two-fund portfolio: Fund A (Large Cap, sigma=18%) + Fund B (Gold, sigma=15%), equal weights w=0.5.
        Formula: sig_p = sqrt(0.25 x 18^2 + 0.25 x 15^2 + 2 x 0.5 x 0.5 x 18 x 15 x rho)
        Weighted average sigma = 0.5 x 18 + 0.5 x 15 = 16.5%
      </div>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:.78rem;">
          <thead>
            <tr style="background:linear-gradient(135deg,{BL},{MD});">
              <th style="color:{G};-webkit-text-fill-color:{G};padding:.5rem .8rem;text-align:left;">Correlation rho</th>
              <th style="color:{G};-webkit-text-fill-color:{G};padding:.5rem .8rem;text-align:left;">Scenario</th>
              <th style="color:{G};-webkit-text-fill-color:{G};padding:.5rem .8rem;text-align:left;">Portfolio sig_p</th>
              <th style="color:{G};-webkit-text-fill-color:{G};padding:.5rem .8rem;text-align:left;">vs Wtd Avg (16.5%)</th>
              <th style="color:{G};-webkit-text-fill-color:{G};padding:.5rem .8rem;text-align:left;">Risk Saved</th>
            </tr>
          </thead>
          <tbody>
            {corr_rows}
          </tbody>
        </table>
      </div>
      <div style="margin-top:.6rem;color:{MU};-webkit-text-fill-color:{MU};font-size:.73rem;">
        ▸ A rho of -0.2 between Equity and Gold saves ~34% of portfolio risk vs two similar equity funds (rho~1.0).
        Check your Correlation heatmap values against this table to quantify your actual diversification benefit.
      </div>
    </div>

    <div style="background:{CA};border:1px solid {MD};
      border-radius:12px;padding:1rem 1.2rem;margin-top:.7rem;margin-bottom:.7rem;user-select:none;">
      <div style="color:{LB};-webkit-text-fill-color:{LB};
        font-weight:800;font-size:.9rem;margin-bottom:.6rem;">
        🎯 Weight Allocation Strategies — How Practitioners Assign wi
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
        {strat_cards}
      </div>
    </div>
    \"\"\")

"""

print("HOW_TO section length:", len(HOW_TO_CALC_SECTION))
print("EDU section length:", len(EDU_PORTFOLIO_SECTION))

# Write both to temp files for patching
with open('/tmp/htu_section.txt','w') as f: f.write(HOW_TO_CALC_SECTION)
with open('/tmp/edu_section.txt','w') as f: f.write(EDU_PORTFOLIO_SECTION)
print("Written to temp files")
