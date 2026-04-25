import os
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader


class Report:
    """A built report object containing all assembled sections."""
    def __init__(self):
        self.sections = {}

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict of all report sections."""
        return dict(self.sections)

    def __str__(self):
        return str(self.sections)


class ReportBuilder:
    """
    Builder pattern for constructing a monthly financial report.
    Supports a fluent interface with optional, independently testable steps.
    Each `with*` method is optional — the report builds with whatever sections are configured.
    """
    def __init__(self):
        self._report = Report()
        self._report.sections = {
            "header": "",
            "date_range": "",
            "monthly_summary": None,
            "spending_chart": {},
            "category_breakdown": [],
            "recommendations": [],
            "net_worth_trend": [],
            "portfolio": [],
        }

    def withHeader(self, title: str) -> 'ReportBuilder':
        """Set the report title/header."""
        self._report.sections["header"] = title
        return self

    def withDateRange(self, start_date: str, end_date: str) -> 'ReportBuilder':
        """Set the reporting period."""
        self._report.sections["date_range"] = f"{start_date} to {end_date}"
        return self

    def withMonthlySummary(self, income: float, expenses: float, savings: float) -> 'ReportBuilder':
        """Add a monthly income/expenses/savings summary."""
        self._report.sections["monthly_summary"] = {
            "income": income,
            "expenses": expenses,
            "savings": savings,
        }
        return self

    def withSpendingPieChart(self, data: Dict[str, float]) -> 'ReportBuilder':
        """Set spending breakdown data (category -> amount) for pie chart rendering."""
        self._report.sections["spending_chart"] = data
        return self

    def withCategoryBreakdownTable(self, table_data: List[Dict[str, Any]]) -> 'ReportBuilder':
        """Set the category breakdown table data."""
        self._report.sections["category_breakdown"] = table_data
        return self

    def withRecommendations(self, recommendations: List[str]) -> 'ReportBuilder':
        """Set the list of financial recommendations."""
        self._report.sections["recommendations"] = recommendations
        return self

    def withNetWorthTrend(self, trend: List[Dict[str, Any]]) -> 'ReportBuilder':
        """
        Set the net worth trend time-series data.
        Expected format: [{"month": "Jan", "net_worth": 10000}, ...]
        Data should be pre-computed by the caller (router), not computed here.
        """
        self._report.sections["net_worth_trend"] = trend
        return self

    def withInvestmentPortfolio(self, portfolio_data: List[Dict[str, Any]]) -> 'ReportBuilder':
        """Set the investment portfolio data for the report."""
        self._report.sections["portfolio"] = portfolio_data
        return self

    def build(self) -> Report:
        """Finalize and return the built Report object."""
        return self._report

    def to_html(self) -> str:
        """
        Render the report as an HTML string using the Jinja2 template.
        Generates matplotlib charts as base64 PNG images embedded inline.
        """
        from .chart_renderer import (
            render_spending_pie_chart,
            render_net_worth_line_chart,
        )

        sections = self._report.sections

        # Generate chart images
        spending_chart_img = ""
        if sections.get("spending_chart"):
            spending_chart_img = render_spending_pie_chart(sections["spending_chart"])

        net_worth_chart_img = ""
        if sections.get("net_worth_trend"):
            net_worth_chart_img = render_net_worth_line_chart(sections["net_worth_trend"])

        # Compute category breakdown percentages
        category_breakdown = sections.get("category_breakdown", [])
        total_spending = sum(row.get("amount", 0) for row in category_breakdown)
        for row in category_breakdown:
            row["percentage"] = (row.get("amount", 0) / total_spending * 100) if total_spending > 0 else 0

        # Load and render the Jinja2 template
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report.html")

        html = template.render(
            header=sections.get("header", "Monthly Financial Report"),
            date_range=sections.get("date_range", ""),
            monthly_summary=sections.get("monthly_summary"),
            spending_chart_img=spending_chart_img,
            category_breakdown=category_breakdown,
            net_worth_chart_img=net_worth_chart_img,
            recommendations=sections.get("recommendations", []),
            portfolio=sections.get("portfolio", []),
        )

        return html

    def to_pdf(self) -> bytes:
        """
        Render the report as a PDF byte string.
        First generates HTML via to_html(), then converts using weasyprint.
        """
        from weasyprint import HTML

        html_content = self.to_html()
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
