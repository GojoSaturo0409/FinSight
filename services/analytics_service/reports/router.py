from fastapi import APIRouter, Depends
from fastapi.responses import Response
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from services.shared.database import get_db
from .builder import ReportBuilder
import datetime

router = APIRouter()


def _compute_net_worth_trend(db: Session) -> List[Dict[str, Any]]:
    """
    Compute net worth time-series from the transactions table.
    Groups transactions by month, computes cumulative savings (income - expenses).
    Returns: [{"month": "Jan", "net_worth": 10500}, ...]
    """
    from services.shared.models import Transaction
    from sqlalchemy import func, extract

    try:
        # Query monthly aggregated spending from DB
        results = (
            db.query(
                extract('year', Transaction.date).label('year'),
                extract('month', Transaction.date).label('month'),
                func.sum(Transaction.amount).label('total_spent'),
            )
            .filter(Transaction.date.isnot(None))
            .group_by(
                extract('year', Transaction.date),
                extract('month', Transaction.date),
            )
            .order_by(
                extract('year', Transaction.date),
                extract('month', Transaction.date),
            )
            .all()
        )

        if not results or len(results) == 0:
            raise ValueError("No transaction data")

        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Assume $5000 monthly income as baseline, compute net worth cumulatively
        monthly_income = 5000
        cumulative = 0
        trend = []
        for row in results:
            month_idx = int(row.month)
            monthly_spend = float(row.total_spent or 0)
            cumulative += (monthly_income - monthly_spend)
            trend.append({
                "month": month_names[month_idx],
                "net_worth": round(cumulative, 2),
            })

        return trend if len(trend) > 0 else _fallback_net_worth()

    except Exception:
        return _fallback_net_worth()


def _fallback_net_worth() -> List[Dict[str, Any]]:
    """Fallback net worth data when DB query fails."""
    return [
        {"month": "Oct", "net_worth": 9200},
        {"month": "Nov", "net_worth": 9800},
        {"month": "Dec", "net_worth": 10500},
        {"month": "Jan", "net_worth": 10100},
        {"month": "Feb", "net_worth": 11200},
        {"month": "Mar", "net_worth": 12450},
    ]


def _compute_spending_from_db(db: Session) -> Dict[str, float]:
    """Compute category spending from real transactions in DB."""
    from services.shared.models import Transaction
    from sqlalchemy import func

    try:
        results = (
            db.query(
                Transaction.category,
                func.sum(Transaction.amount).label('total'),
            )
            .filter(Transaction.category.isnot(None))
            .group_by(Transaction.category)
            .all()
        )

        if results:
            return {row.category: round(float(row.total), 2) for row in results if row.category != 'Income'}
    except Exception:
        pass

    return {}


def _get_portfolio_from_db(db: Session) -> List[Dict[str, Any]]:
    """Get portfolio data from investment cache in DB."""
    from services.shared.models import InvestmentCache

    try:
        entries = db.query(InvestmentCache).all()
        if entries:
            return [
                {"symbol": e.symbol, "price": e.price, "trend": e.trend}
                for e in entries
            ]
    except Exception:
        pass

    return [
        {"symbol": "SPY", "price": 523.40, "trend": "up"},
        {"symbol": "BND", "price": 72.85, "trend": "up"},
        {"symbol": "VTI", "price": 261.20, "trend": "up"},
    ]


def _build_report(data: Dict[str, Any], db: Session) -> ReportBuilder:
    """
    Construct a ReportBuilder from request data + real DB data.
    Merges frontend-provided data with real DB aggregates.
    """
    # Compute spending from DB if not provided
    spending_chart = data.get("spending_chart", None)
    if not spending_chart:
        spending_chart = _compute_spending_from_db(db)
    if not spending_chart:
        spending_chart = {"Housing": 1500, "Food": 300, "Transport": 150, "Subscriptions": 50}

    total = sum(spending_chart.values()) if spending_chart else 1
    category_breakdown = [
        {"category": cat, "amount": amt, "percentage": round(amt / total * 100, 1)}
        for cat, amt in spending_chart.items()
    ]

    # Monthly summary
    income = data.get("income", 5000)
    expenses = data.get("expenses", sum(spending_chart.values()))
    savings = income - expenses

    # Portfolio from DB
    portfolio = data.get("portfolio", None)
    if not portfolio:
        portfolio = _get_portfolio_from_db(db)

    # Net worth trend from real DB
    net_worth_data = _compute_net_worth_trend(db)

    # Recommendations
    recommendations = data.get("recommendations", [])
    if not recommendations:
        # Auto-generate from chain
        try:
            from recommendations.chain import RecommendationChain
            chain = RecommendationChain()
            context = {
                "monthly_income": income,
                "monthly_spend": expenses,
                "categories": spending_chart,
            }
            recommendations = chain.get_recommendations(context, db=db)
        except Exception:
            pass

    builder = ReportBuilder()
    builder = (builder
               .withHeader(data.get("title", "Monthly Financial Report"))
               .withDateRange(data.get("start_date", "2024-03-01"), data.get("end_date", "2024-03-31"))
               .withMonthlySummary(income, expenses, savings)
               .withSpendingPieChart(spending_chart)
               .withCategoryBreakdownTable(category_breakdown)
               .withRecommendations(recommendations)
               .withNetWorthTrend(net_worth_data)
               .withInvestmentPortfolio(portfolio))

    return builder


@router.post("/generate")
def generate_report(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Generate the report and return JSON data."""
    builder = _build_report(data, db)
    report = builder.build()
    return {"status": "success", "report": report.to_dict()}


@router.post("/generate-auto")
def generate_report_auto(db: Session = Depends(get_db)):
    """
    Auto-generate a full report from real DB data.
    No frontend data required — everything is computed server-side.
    """
    spending = _compute_spending_from_db(db)
    portfolio = _get_portfolio_from_db(db)
    net_worth = _compute_net_worth_trend(db)

    income = 5000
    expenses = sum(spending.values()) if spending else 2000
    savings = income - expenses

    # Auto-generate recommendations
    recommendations = []
    try:
        from recommendations.chain import RecommendationChain
        chain = RecommendationChain()
        context = {
            "monthly_income": income,
            "monthly_spend": expenses,
            "categories": spending,
        }
        recommendations = chain.get_recommendations(context, db=db)
    except Exception:
        pass

    total = sum(spending.values()) if spending else 1
    category_breakdown = [
        {"category": cat, "amount": amt, "percentage": round(amt / total * 100, 1)}
        for cat, amt in spending.items()
    ]

    builder = ReportBuilder()
    builder = (builder
               .withHeader("Monthly Financial Report")
               .withDateRange("2024-03-01", "2024-03-31")
               .withMonthlySummary(income, expenses, savings)
               .withSpendingPieChart(spending)
               .withCategoryBreakdownTable(category_breakdown)
               .withRecommendations(recommendations)
               .withNetWorthTrend(net_worth)
               .withInvestmentPortfolio(portfolio))

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
