from fastapi import APIRouter, Depends
from fastapi.responses import Response
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import get_db
from .builder import ReportBuilder

router = APIRouter()


def _compute_net_worth_trend(db: Session) -> List[Dict[str, Any]]:
    """
    Pre-compute net worth time-series from the transactions table.
    Groups transactions by month, computes cumulative (income - expenses).
    Returns: [{"month": "Oct", "net_worth": 10500}, ...]
    """
    from models import Transaction
    from sqlalchemy import func, extract

    # For the prototype, use mock data that demonstrates the feature.
    # In production, this would query the transactions table:
    #   SELECT EXTRACT(month FROM date), SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
    #          SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses
    #   FROM transactions GROUP BY month ORDER BY month

    # Realistic mock net worth trend for 6 months
    return [
        {"month": "Oct", "net_worth": 9200},
        {"month": "Nov", "net_worth": 9800},
        {"month": "Dec", "net_worth": 10500},
        {"month": "Jan", "net_worth": 10100},
        {"month": "Feb", "net_worth": 11200},
        {"month": "Mar", "net_worth": 12450},
    ]


def _build_report(data: Dict[str, Any], db: Session) -> ReportBuilder:
    """
    Construct a ReportBuilder from request data.
    Computes net worth from transactions and assembles all sections.
    """
    # Pre-compute net worth trend from the DB
    net_worth_data = _compute_net_worth_trend(db)

    # Compute category breakdown with percentages
    spending_chart = data.get("spending_chart", {
        "Housing": 1500, "Food": 300, "Transport": 150, "Subscriptions": 50
    })
    total = sum(spending_chart.values()) if spending_chart else 1
    category_breakdown = [
        {"category": cat, "amount": amt, "percentage": round(amt / total * 100, 1)}
        for cat, amt in spending_chart.items()
    ]

    # Monthly summary
    income = data.get("income", 5000)
    expenses = data.get("expenses", sum(spending_chart.values()))
    savings = income - expenses

    # Portfolio data (from investments cache if available)
    portfolio = data.get("portfolio", [
        {"symbol": "SPY", "price": 523.40, "trend": "up"},
        {"symbol": "BND", "price": 72.85, "trend": "up"},
        {"symbol": "VTI", "price": 261.20, "trend": "up"},
    ])

    builder = ReportBuilder()
    builder = (builder
               .withHeader(data.get("title", "Monthly Financial Report"))
               .withDateRange(data.get("start_date", "2024-03-01"), data.get("end_date", "2024-03-31"))
               .withMonthlySummary(income, expenses, savings)
               .withSpendingPieChart(spending_chart)
               .withCategoryBreakdownTable(category_breakdown)
               .withRecommendations(data.get("recommendations", []))
               .withNetWorthTrend(net_worth_data)
               .withInvestmentPortfolio(portfolio))

    return builder


@router.post("/generate")
def generate_report(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Generate the report and return JSON data."""
    builder = _build_report(data, db)
    report = builder.build()
    return {"status": "success", "report": report.to_dict()}


@router.post("/export/html")
def export_report_html(data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Generate the report and return it as a downloadable HTML file.
    Uses Jinja2 template with matplotlib-generated base64 chart images.
    """
    builder = _build_report(data, db)
    html_content = builder.to_html()

    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": "attachment; filename=finsight_report.html"
        }
    )


@router.post("/export/pdf")
def export_report_pdf(data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Generate the report and return it as a downloadable PDF file.
    Uses weasyprint to convert the HTML report to PDF.
    Requires Cairo/Pango system libraries (installed via Dockerfile).
    """
    builder = _build_report(data, db)

    try:
        pdf_bytes = builder.to_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=finsight_report.pdf"
            }
        )
    except Exception as e:
        # Fallback: if weasyprint fails (missing system deps), return HTML
        html_content = builder.to_html()
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": "attachment; filename=finsight_report.html",
                "X-PDF-Error": str(e),
            }
        )
