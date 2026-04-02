from typing import Dict, Any, List

class Report:
    def __init__(self):
        self.sections = {}

    def __str__(self):
        return str(self.sections)

class ReportBuilder:
    def __init__(self):
        self._report = Report()
        self._report.sections = {
            "header": "",
            "date_range": "",
            "spending_chart": {},
            "category_breakdown": {},
            "recommendations": [],
            "net_worth_trend": {"status": "neutral"}
        }

    def withHeader(self, title: str) -> 'ReportBuilder':
        self._report.sections["header"] = title
        return self

    def withDateRange(self, start_date: str, end_date: str) -> 'ReportBuilder':
        self._report.sections["date_range"] = f"{start_date} to {end_date}"
        return self

    def withSpendingPieChart(self, data: Dict[str, float]) -> 'ReportBuilder':
        self._report.sections["spending_chart"] = data
        return self

    def withCategoryBreakdownTable(self, table_data: List[Dict[str, Any]]) -> 'ReportBuilder':
        self._report.sections["category_breakdown"] = table_data
        return self

    def withRecommendations(self, recommendations: List[str]) -> 'ReportBuilder':
        self._report.sections["recommendations"] = recommendations
        return self

    def withNetWorthTrend(self, trend: Dict[str, Any]) -> 'ReportBuilder':
        self._report.sections["net_worth_trend"] = trend
        return self

    def build(self) -> Report:
        return self._report
