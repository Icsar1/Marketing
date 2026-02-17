from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl, ValidationError

from app.config import settings
from app.models import SeoLead
from app.seo_service import SeoAnalyzer
from app.storage import Storage

app = FastAPI(title="SEO Lead Analyzer")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
storage = Storage()
analyzer = SeoAnalyzer()
scheduler = BackgroundScheduler()


class LeadPayload(BaseModel):
    name: str
    phone: str
    email: str
    site_url: HttpUrl


def _pick_first(payload: Dict[str, Any], keys: list) -> Optional[str]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


async def _extract_request_payload(request: Request) -> Dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    data: Any = None

    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            data = None

    if data is None:
        form_data = await request.form()
        data = dict(form_data)

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=422,
            detail="Body должен быть JSON-объектом или form-data.",
        )

    return {
        "name": _pick_first(data, ["name", "Name", "fullname", "full_name"]),
        "phone": _pick_first(data, ["phone", "Phone", "tel", "phone_number"]),
        "email": _pick_first(data, ["email", "Email", "mail"]),
        "site_url": _pick_first(data, ["site_url", "site", "website", "url", "siteUrl"]),
    }


@app.on_event("startup")
def startup() -> None:
    scheduler.add_job(
        func=lambda: storage.delete_expired(datetime.now(tz=timezone.utc)),
        trigger="interval",
        hours=1,
        id="cleanup_expired_reports",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": settings.seo_data_provider}


@app.post("/lead/seo")
async def create_seo_report(request: Request, payload: Optional[LeadPayload] = None):
    if payload is None:
        raw_payload = await _extract_request_payload(request)
        try:
            payload = LeadPayload(**raw_payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors())

    lead = SeoLead(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        site_url=str(payload.site_url),
    )
    report = await analyzer.analyze(lead)
    storage.save_report(report)

    report_url = f"{settings.app_base_url.rstrip('/')}/r/{report.report_id}"
    return JSONResponse(
        {
            "message": "SEO отчет создан",
            "report_url": report_url,
            "expires_at": report.expires_at.isoformat(),
        }
    )


@app.get("/r/{report_id}")
def report_page(request: Request, report_id: str):
    report = storage.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден или удален")

    if report.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=410, detail="Срок хранения отчета истек")

    return templates.TemplateResponse(
        "report.html",
        {
            "request": request,
            "report": report,
        },
    )
