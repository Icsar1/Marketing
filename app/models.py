from dataclasses import dataclass
from datetime import datetime


@dataclass
class SeoLead:
    name: str
    phone: str
    email: str
    site_url: str


@dataclass
class SeoReport:
    report_id: str
    site_url: str
    summary: str
    critical_errors: list[str]
    demand_score: int
    competitors: list[dict]
    recommendations: list[str]
    created_at: datetime
    expires_at: datetime
