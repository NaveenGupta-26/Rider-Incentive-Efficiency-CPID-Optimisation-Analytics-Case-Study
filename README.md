# Rider Incentive Efficiency — Cost Per Incremental Delivery (CPID) Optimization

> **[View the Live Case Study →](https://naveengupta-26.github.io/cpid-rider-incentive-optimization/)**

> **Last-mile delivery platforms (Swiggy, Zomato, Blinkit, Zepto) spend ₹200–400 Cr per quarter on rider incentives. Most of that spend uses a flat-per-order bonus structure with an ROI of 0.98× — meaning the platform recovers less in incremental revenue than it spends. This project builds a full analytical framework to measure the true cost of each additional delivery generated, and redesigns the incentive structure to benefit both the platform and the riders.**

---

## Key Findings

| Finding | Metric | Value |
|---|---|---|
| Flat bonus ROI | Revenue from incr. deliveries / spend | **0.98×** (loss-making) |
| Surge top-up ROI | Revenue from incr. deliveries / spend | **1.50×** (★ Best) |
| Best CPID segment | Tier-2/3, 2–6mo riders, surge | **₹35.2** |
| Worst CPID segment | Tier-1, 12+mo riders, flat bonus | **₹92.5** |
| Quarterly saving | Platform-scale (350K riders) | **₹60.7 Cr** |
| Rider earnings | Optimized structure vs control | **+₹334/week** |

> **The optimised incentive structure increases platform efficiency AND rider earnings simultaneously. This is not a cost-cutting project.**

---

## Project Structure

```
cpid-rider-incentive-optimization/
├── README.md
├── requirements.txt
├── run_all.py                     # Master pipeline — runs all phases
│
├── data/
│   └── generate_data.py           # Phase 2: Synthetic data generator
│                                  #   Sources: Swiggy DRHP, AIF 2025, CNN
│                                  #   CSVs generated at runtime (gitignored)
│
├── sql/
│   └── run_queries.py             # Phase 3: 8 SQL queries via DuckDB
│
├── analysis/
│   ├── phase4_stats.py            # Phase 4: Statistical validation
│   └── phase5_charts.py           # Phase 5: 5 professional visualizations
│
├── experiment/
│   └── simulation.py              # Phase 6: A/B experiment simulation
│
├── charts/                        # Generated chart PNGs
│   ├── chart1_cpid_by_type.png
│   ├── chart2_tenure_scatter.png
│   ├── chart3_heatmap.png
│   ├── chart4_weekly_trend.png
│   └── chart5_did.png
│
└── docs/                          # Live showcase (GitHub Pages)
    ├── index.html                 # Main portfolio page
    ├── phase1_problem.html        # Problem framing deep-dive
    ├── phase3_sql.html            # SQL analysis worksheet
    └── phase6_experiment.html     # Experiment design
```

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/NaveenGupta-26/cpid-rider-incentive-optimization.git
cd cpid-rider-incentive-optimization

# Install dependencies
pip install -r requirements.txt

# Execute the full pipeline (generates data + runs all analysis)
python run_all.py
```

This runs all 5 phases in sequence: data generation → SQL analysis → statistical validation → chart generation → A/B experiment simulation.

---

## Methodology

### Phase 1 — Problem Framing
Defines **CPID** from first principles. Explains why total deliveries is a misleading metric and how to isolate the *incremental* effect. Maps the rider supply funnel and identifies where each incentive type acts.

### Phase 2 — Data Schema + Synthetic Generation
4-table schema built on verified sources: Swiggy DRHP/FY25 (₹86/order cost), AIF March 2025 report (rider earnings reality), CNN January 2026 (direct rider testimony), December 2025 strike coverage (real incentive amounts). Every constant is cited. Rider earnings guard rail: zero riders earned below base pay.

### Phase 3 — 8 SQL Queries
All 8 queries run on DuckDB. Covers baseline delivery rate, CPID by incentive type, tenure × type segmentation, city-tier analysis, cliff effect detection, streak completion rate, time-of-day efficiency, and full P&L unit economics.

### Phase 4 — Statistical Validation
| Test | Method | Result |
|---|---|---|
| H1: Streak < Flat CPID | Mann-Whitney U + t-test | ✓ Confirmed (p = 0.0068) |
| H2: 2–6mo is sweet spot | ANOVA + Tukey HSD | ✓ Confirmed (p = 1.09×10⁻⁸) |
| H3: Tier-1 ≥ 2× Tier-2 | Welch's t-test | ⚡ Partial (1.66×, not 2×) |

H3 is reported honestly as partial — the gap is statistically significant and directionally correct, but the 2× threshold was not met.

### Phase 5 — Visualizations
5 charts answering one question each: hero bar with bootstrap CI, tenure scatter with bubble encoding, city-tier heatmap, dual-axis CPID vs coverage time series, and DiD proof chart.

### Phase 6 — A/B Experiment Design
Full experiment spec: 3 arms, cluster randomization at city level (SUTVA violation identified and solved), sample size calculation (7,834 rider-weeks/arm, 5 weeks), power = 80%. Variant B redesigned as hybrid surge after pure surge failed rider earnings guard rail.

---

## The Rider-First Principle

This project treats rider welfare as a hard constraint:

- Zero riders in the dataset have average weekly earnings below base pay
- Variant B was redesigned when pure surge failed the earnings guard rail
- The final recommended structure increases rider earnings by ₹334/week vs control
- Cliff churn (post-incentive supply drop) is measured and flagged as a welfare signal
- The December 2025 nationwide strike (200,000+ workers) is acknowledged as direct context

---

## Technical Stack

| Category | Tools |
|---|---|
| Data generation | Python (pandas, numpy) |
| SQL analysis | DuckDB (local), compatible with PostgreSQL/BigQuery |
| Statistical validation | scipy, statsmodels |
| Visualization | matplotlib, seaborn |
| Showcase | Vanilla HTML/CSS (GitHub Pages) |

---

## Data Sources

All constants in the synthetic dataset are sourced from:
- Swiggy DRHP + FY25 SWOT (delivery cost per order, fleet size)
- Swiggy Annual Report FY24 (rider churn rate)
- CNN, January 2026 (direct rider testimony — daily deliveries, earnings)
- AIF Report, March 2025 (gig worker financial reality)
- IFAT/TGPWU strike coverage, December 2025 (real incentive amounts)
- Swiggy/Zomato public filings (AOV, take rate)

---

*Created by Naveen Gupta · Growth Analytics Portfolio Project*
