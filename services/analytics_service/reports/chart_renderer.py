"""
Server-side chart renderer using matplotlib with Agg backend.
Generates base64-encoded PNG images for embedding in HTML/PDF reports.
"""
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import Dict, List


# FinSight color palette (matching frontend design)
COLORS = {
    "indigo": "#6366f1",
    "rose": "#f43f5e",
    "emerald": "#10b981",
    "amber": "#f59e0b",
    "purple": "#a855f7",
    "cyan": "#06b6d4",
    "pink": "#ec4899",
    "sky": "#0ea5e9",
}
COLOR_LIST = list(COLORS.values())
BG_COLOR = "#0a0a0a"
TEXT_COLOR = "#e5e5e5"
GRID_COLOR = "#262626"


def _fig_to_base64(fig) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=BG_COLOR, edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def render_spending_pie_chart(data: Dict[str, float]) -> str:
    """
    Render a spending breakdown pie/doughnut chart.
    Args:
        data: dict mapping category name to amount, e.g. {"Food": 300, "Housing": 1500}
    Returns:
        Base64-encoded PNG string
    """
    if not data:
        return ""

    labels = list(data.keys())
    values = list(data.values())
    colors = COLOR_LIST[:len(labels)]

    fig, ax = plt.subplots(figsize=(6, 4), facecolor=BG_COLOR)
    wedges, texts, autotexts = ax.pie(
        values, labels=None, colors=colors, autopct='%1.1f%%',
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor=BG_COLOR, linewidth=2),
    )

    for text in autotexts:
        text.set_color(TEXT_COLOR)
        text.set_fontsize(9)

    ax.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5),
              fontsize=9, facecolor=BG_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR)

    ax.set_title('Spending Breakdown', color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=15)
    fig.patch.set_facecolor(BG_COLOR)

    return _fig_to_base64(fig)


def render_net_worth_line_chart(data: List[Dict]) -> str:
    """
    Render a net worth trend line/area chart.
    Args:
        data: list of dicts with 'month' and 'net_worth' keys,
              e.g. [{"month": "Jan", "net_worth": 10000}, ...]
    Returns:
        Base64-encoded PNG string
    """
    if not data:
        return ""

    months = [d.get("month", "") for d in data]
    values = [d.get("net_worth", 0) for d in data]

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.fill_between(range(len(months)), values, alpha=0.15, color=COLORS["indigo"])
    ax.plot(range(len(months)), values, color=COLORS["indigo"], linewidth=2.5,
            marker='o', markersize=6, markerfacecolor=COLORS["indigo"],
            markeredgecolor=BG_COLOR, markeredgewidth=2)

    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, color=TEXT_COLOR, fontsize=9)
    ax.tick_params(axis='y', colors=TEXT_COLOR, labelsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.grid(axis='y', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)

    ax.set_title('Net Worth Trend', color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=15)

    return _fig_to_base64(fig)


def render_category_bar_chart(data: Dict[str, float]) -> str:
    """
    Render a horizontal bar chart for category breakdown.
    Args:
        data: dict mapping category name to amount
    Returns:
        Base64-encoded PNG string
    """
    if not data:
        return ""

    categories = list(data.keys())
    amounts = list(data.values())
    colors = COLOR_LIST[:len(categories)]

    fig, ax = plt.subplots(figsize=(7, max(3, len(categories) * 0.6)), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(categories, amounts, color=colors, height=0.5, edgecolor='none')

    for bar, amount in zip(bars, amounts):
        ax.text(bar.get_width() + max(amounts) * 0.02, bar.get_y() + bar.get_height() / 2,
                f'${amount:,.0f}', va='center', color=TEXT_COLOR, fontsize=9)

    ax.tick_params(axis='y', colors=TEXT_COLOR, labelsize=10)
    ax.tick_params(axis='x', colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.grid(axis='x', color=GRID_COLOR, linewidth=0.5, alpha=0.5)
    ax.invert_yaxis()

    ax.set_title('Category Breakdown', color=TEXT_COLOR, fontsize=14, fontweight='bold', pad=15)

    return _fig_to_base64(fig)
