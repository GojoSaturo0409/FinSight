from fastapi import APIRouter
from typing import Dict, Any, List
from .builder import ReportBuilder

router = APIRouter()

@router.post("/generate")
def generate_report(data: Dict[str, Any]):
    # data can include raw info which is processed by the builder
    builder = ReportBuilder()
    
    report = (builder
              .withHeader("Monthly Financial Report")
              .withDateRange(data.get("start_date", "2024-01-01"), data.get("end_date", "2024-01-31"))
              .withSpendingPieChart(data.get("spending_chart", {}))
              .withCategoryBreakdownTable(data.get("category_breakdown", []))
              .withRecommendations(data.get("recommendations", []))
              .withNetWorthTrend(data.get("net_worth_trend", {}))
              .build())
              
    return {"status": "success", "report": report.sections}
