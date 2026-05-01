from pydantic import BaseModel


class FinancialFacts(BaseModel):
    accn: str = ""
    start_date: str = ""
    end_date: str = ""
    filed_date: str = ""
    fiscal_period: str = ""
    form_report: str = ""
    frame: str = ""
