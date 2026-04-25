"""
CPID Project — Phase 5: Visualizations
5 charts: CPID bar, tenure scatter, city heatmap, weekly trend, DiD proof
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# ── STYLING ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
    'font.size': 11,
    'axes.facecolor': '#f8f7f4',
    'figure.facecolor': '#ffffff',
    'axes.edgecolor': '#d0cdc5',
    'axes.linewidth': 0.5,
    'grid.color': '#e5e3de',
    'grid.linewidth': 0.4,
})

COLORS = {
    'surge': '#1a6b3c',
    'streak': '#1a4fad',
    'flat': '#c0392b',
    'none': '#8e8e8e',
    'tier1': '#c0392b',
    'tier2': '#1a4fad',
    'tier3': '#1a6b3c',
    'bg': '#f8f7f4',
    'ink': '#1c1c1c',
    'ink2': '#3d3d3d',
    'ink3': '#6b6b6b',
}


def generate_all_charts(data_dir, output_dir):
    """Generate all 5 visualization charts."""
    print("\n" + "=" * 65)
    print("  CPID PROJECT — VISUALIZATION GENERATION (5 CHARTS)")
    print("=" * 65)

    os.makedirs(output_dir, exist_ok=True)

    shifts = pd.read_csv(os.path.join(data_dir, "shifts.csv"))
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    print(f"  Loaded {len(shifts):,} shifts, {len(orders):,} orders\n")

    # Compute baseline per rider
    baseline = (
        shifts[shifts["incentive_type"] == "none"]
        .groupby("rider_id")["deliveries_completed"].mean()
        .rename("baseline")
    )
    inc_weeks = shifts[shifts["incentive_type"] != "none"].copy()
    inc_weeks = inc_weeks.merge(baseline, on="rider_id", how="inner")
    valid_cpid = inc_weeks[inc_weeks["cpid"].notna() & (inc_weeks["cpid"] > 0)].copy()

    # ═══════════════════════════════════════════════════════════════
    # CHART 1: CPID by Incentive Type (Hero Bar Chart)
    # ═══════════════════════════════════════════════════════════════
    print("  [1/5] CPID by Incentive Type — Hero bar chart...")

    fig, ax = plt.subplots(figsize=(10, 6))

    types = ['surge_topup', 'streak_bonus', 'flat_per_order']
    labels = ['Surge Top-up', 'Streak Bonus', 'Flat Per-Order']
    colors = [COLORS['surge'], COLORS['streak'], COLORS['flat']]

    medians = []
    ci_lowers = []
    ci_uppers = []
    for t in types:
        data = valid_cpid[valid_cpid["incentive_type"] == t]["cpid"].values
        med = np.median(data)
        medians.append(med)
        boot = [np.median(np.random.choice(data, len(data), replace=True)) for _ in range(2000)]
        ci_lowers.append(np.percentile(boot, 2.5))
        ci_uppers.append(np.percentile(boot, 97.5))

    bars = ax.barh(range(len(types)), medians, color=colors, height=0.55, edgecolor='white', linewidth=0.5)

    for i, (med, lo, hi) in enumerate(zip(medians, ci_lowers, ci_uppers)):
        ax.errorbar(med, i, xerr=[[med-lo], [hi-med]], fmt='none', color='#1c1c1c',
                    capsize=4, capthick=1.2, linewidth=1.2)
        ax.text(hi + 1.5, i, f'₹{med:.1f}', va='center', fontsize=13, fontweight='bold', color=colors[i])
        ax.text(hi + 1.5, i + 0.22, f'95% CI: [{lo:.1f}, {hi:.1f}]', va='center', fontsize=9, color=COLORS['ink3'])

    ax.set_yticks(range(len(types)))
    ax.set_yticklabels(labels, fontsize=12, fontweight='500')
    ax.invert_yaxis()
    ax.set_xlabel('CPID — Cost Per Incremental Delivery (₹)', fontsize=11, color=COLORS['ink2'])
    ax.set_title('Which Incentive Type Generates the\nCheapest Incremental Deliveries?',
                fontsize=16, fontweight='bold', color=COLORS['ink'], pad=15)

    # Add ROI annotation
    ax.text(0.98, 0.02, 'Flat ROI: 0.98× (loss-making)  |  Streak ROI: 1.17×  |  Surge ROI: 1.50×',
            transform=ax.transAxes, fontsize=9, color=COLORS['ink3'], ha='right', style='italic')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart1_cpid_by_type.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved chart1_cpid_by_type.png")

    # ═══════════════════════════════════════════════════════════════
    # CHART 2: Tenure × CPID Scatter (Bubble)
    # ═══════════════════════════════════════════════════════════════
    print("  [2/5] Tenure × CPID Scatter — Bubble chart...")

    fig, ax = plt.subplots(figsize=(12, 7))

    agg = (
        valid_cpid.groupby(["tenure_band", "incentive_type"])
        .agg(
            cpid_median=("cpid", "median"),
            total_spend=("incentive_pay", "sum"),
            count=("cpid", "count")
        ).reset_index()
    )

    tenure_order = {"0-2mo": 1, "2-6mo": 2, "6-12mo": 3, "12+mo": 4}
    agg["x"] = agg["tenure_band"].map(tenure_order)
    color_map = {"surge_topup": COLORS['surge'], "streak_bonus": COLORS['streak'], "flat_per_order": COLORS['flat']}
    label_map = {"surge_topup": "Surge Top-up", "streak_bonus": "Streak Bonus", "flat_per_order": "Flat Per-Order"}

    for it in ["surge_topup", "streak_bonus", "flat_per_order"]:
        d = agg[agg["incentive_type"] == it]
        sizes = (d["total_spend"] / d["total_spend"].max()) * 800 + 100
        ax.scatter(d["x"] + ({"surge_topup": -0.15, "streak_bonus": 0, "flat_per_order": 0.15}[it]),
                  d["cpid_median"], s=sizes, c=color_map[it], alpha=0.7,
                  edgecolors='white', linewidth=1.5, label=label_map[it], zorder=3)

    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["0-2 months", "2-6 months\n★ sweet spot", "6-12 months", "12+ months"], fontsize=11)
    ax.set_ylabel('CPID — ₹ per incremental delivery', fontsize=11, color=COLORS['ink2'])
    ax.set_title('Rider Tenure × CPID by Incentive Type\nBubble size = total spend',
                fontsize=16, fontweight='bold', color=COLORS['ink'], pad=15)

    ax.axvspan(1.5, 2.5, alpha=0.08, color=COLORS['surge'], zorder=0)
    ax.text(2, ax.get_ylim()[1]*0.95, '← Lowest CPID zone', ha='center', fontsize=10,
           color=COLORS['surge'], style='italic', fontweight='bold')

    ax.legend(fontsize=10, loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart2_tenure_scatter.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved chart2_tenure_scatter.png")

    # ═══════════════════════════════════════════════════════════════
    # CHART 3: City Tier × Incentive Type Heatmap
    # ═══════════════════════════════════════════════════════════════
    print("  [3/5] City × Incentive CPID Heatmap...")

    fig, ax = plt.subplots(figsize=(9, 5))

    heatmap_data = (
        valid_cpid.groupby(["city_tier", "incentive_type"])["cpid"]
        .median().unstack()
    )
    heatmap_data = heatmap_data.reindex(["Tier3", "Tier2", "Tier1"])
    heatmap_data = heatmap_data[["surge_topup", "streak_bonus", "flat_per_order"]]
    heatmap_data.columns = ["Surge Top-up", "Streak Bonus", "Flat Per-Order"]
    heatmap_data.index = ["Tier-3 (Surat, Bhopal…)", "Tier-2 (Pune, Jaipur…)", "Tier-1 (Mumbai, Delhi…)"]

    sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn_r',
               linewidths=2, linecolor='white', ax=ax,
               annot_kws={'size': 14, 'fontweight': 'bold'},
               cbar_kws={'label': 'CPID (₹) — lower is better', 'shrink': 0.8})

    ax.set_title('CPID Decision Matrix: City Tier × Incentive Type\nDarker red = higher cost per incremental delivery',
                fontsize=14, fontweight='bold', color=COLORS['ink'], pad=15)
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.tick_params(labelsize=11)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart3_heatmap.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved chart3_heatmap.png")

    # ═══════════════════════════════════════════════════════════════
    # CHART 4: Weekly CPID Trend (Dual-axis)
    # ═══════════════════════════════════════════════════════════════
    print("  [4/5] Weekly CPID vs Coverage Trend — Dual axis...")

    fig, ax1 = plt.subplots(figsize=(13, 6))

    weekly = (
        valid_cpid.groupby("week_start")
        .agg(cpid_median=("cpid", "median"), total_deliveries=("deliveries_completed", "sum"))
        .reset_index()
    )
    weekly["week_start"] = pd.to_datetime(weekly["week_start"])
    weekly = weekly.sort_values("week_start")

    ax1.plot(weekly["week_start"], weekly["cpid_median"], color=COLORS['flat'],
            linewidth=2.5, marker='o', markersize=5, label='CPID (₹)', zorder=3)
    ax1.fill_between(weekly["week_start"], weekly["cpid_median"],
                     alpha=0.1, color=COLORS['flat'])
    ax1.set_ylabel('CPID (₹ per incremental delivery)', fontsize=11, color=COLORS['flat'])
    ax1.tick_params(axis='y', labelcolor=COLORS['flat'])

    ax2 = ax1.twinx()
    ax2.bar(weekly["week_start"], weekly["total_deliveries"] / 1000,
           width=5, alpha=0.3, color=COLORS['surge'], label='Deliveries (000s)')
    ax2.set_ylabel('Total Deliveries (thousands)', fontsize=11, color=COLORS['surge'])
    ax2.tick_params(axis='y', labelcolor=COLORS['surge'])

    ax1.set_title('Weekly CPID Trend vs Delivery Volume\n26 Weeks — Jul 2024 to Dec 2024',
                 fontsize=16, fontweight='bold', color=COLORS['ink'], pad=15)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10, framealpha=0.9)

    ax1.spines['top'].set_visible(False)
    ax1.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=30, fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart4_weekly_trend.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved chart4_weekly_trend.png")

    # ═══════════════════════════════════════════════════════════════
    # CHART 5: DiD Parallel Trends + Treatment Effect
    # ═══════════════════════════════════════════════════════════════
    print("  [5/5] DiD Parallel Trends + Treatment Effect...")

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 6))

    # Left panel: baseline distributions
    for it, color, label in [
        ("streak_bonus", COLORS['streak'], "Streak weeks"),
        ("flat_per_order", COLORS['flat'], "Flat weeks"),
    ]:
        data = shifts[(shifts["incentive_type"] == "none")].merge(
            shifts[shifts["incentive_type"] == it][["rider_id"]].drop_duplicates(),
            on="rider_id"
        )["deliveries_completed"]
        ax_l.hist(data, bins=40, alpha=0.5, color=color, label=f'{label} riders (baseline)',
                 density=True, edgecolor='white', linewidth=0.5)

    ax_l.set_title('Panel A: Baseline Distributions\n(Control weeks — no incentive active)',
                  fontsize=12, fontweight='bold', color=COLORS['ink'])
    ax_l.set_xlabel('Weekly Deliveries (baseline)', fontsize=10)
    ax_l.set_ylabel('Density', fontsize=10)
    ax_l.legend(fontsize=9)
    ax_l.spines['top'].set_visible(False)
    ax_l.spines['right'].set_visible(False)

    # Right panel: incremental deliveries
    streak_incr = inc_weeks[inc_weeks["incentive_type"] == "streak_bonus"]["incr_deliveries"]
    flat_incr   = inc_weeks[inc_weeks["incentive_type"] == "flat_per_order"]["incr_deliveries"]

    bp = ax_r.boxplot(
        [streak_incr.clip(-50, 100), flat_incr.clip(-50, 100)],
        labels=['Streak Bonus', 'Flat Per-Order'],
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color='#1c1c1c', linewidth=2),
    )
    bp['boxes'][0].set_facecolor(COLORS['streak'])
    bp['boxes'][0].set_alpha(0.6)
    bp['boxes'][1].set_facecolor(COLORS['flat'])
    bp['boxes'][1].set_alpha(0.6)

    ax_r.axhline(y=0, color='#999', linestyle='--', linewidth=0.8, alpha=0.5)
    ax_r.set_title('Panel B: Treatment Effect\n(Incremental deliveries above baseline)',
                  fontsize=12, fontweight='bold', color=COLORS['ink'])
    ax_r.set_ylabel('Incremental Deliveries / Week', fontsize=10)

    # Add annotation
    ax_r.text(0.5, 0.95, f'Streak median: +{streak_incr.median():.1f}\nFlat median: +{flat_incr.median():.1f}',
             transform=ax_r.transAxes, fontsize=10, va='top', ha='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f5ff', edgecolor='#b5d4f4', alpha=0.9))

    ax_r.spines['top'].set_visible(False)
    ax_r.spines['right'].set_visible(False)

    fig.suptitle('Difference-in-Differences: Streak vs Flat Bonus',
                fontsize=16, fontweight='bold', color=COLORS['ink'], y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart5_did.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("    ✓ Saved chart5_did.png")

    print("\n" + "=" * 65)
    print("  ✓ ALL 5 CHARTS GENERATED SUCCESSFULLY")
    print(f"  Output: {output_dir}")
    print("=" * 65)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    output_dir = os.path.join(os.path.dirname(script_dir), "charts")
    generate_all_charts(data_dir, output_dir)
