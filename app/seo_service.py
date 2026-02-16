from datetime import datetime, timedelta, timezone
from hashlib import md5
import uuid

from app.config import settings
from app.models import SeoLead, SeoReport


class SeoAnalyzer:
    """
    Lightweight SEO analyzer skeleton:
    - Keeps footprint low.
    - Ready for real Yandex API calls (Webmaster/Metrica/Direct Wordstat proxies).
    """

    async def analyze(self, lead: SeoLead) -> SeoReport:
        # In production replace this block with real calls:
        # webmaster = await self._fetch_webmaster_issues(lead.site_url)
        # demand = await self._fetch_search_demand(lead.site_url)
        # competitors = await self._fetch_competitors_snapshot(lead.site_url)
        website_hash = int(md5(lead.site_url.encode("utf-8")).hexdigest(), 16)
        demand_score = 35 + website_hash % 66

        report_id = str(uuid.uuid4())
        created_at = datetime.now(tz=timezone.utc)
        expires_at = created_at + timedelta(hours=settings.report_ttl_hours)

        critical_errors = [
            "Нет явного Title/Description на части страниц",
            "Медленная загрузка мобильной версии",
            "Не настроены расширенные сниппеты (schema.org)",
        ]

        competitors = [
            {"domain": "competitor-a.ru", "gap": "Больше посадочных страниц под коммерческие запросы"},
            {"domain": "competitor-b.ru", "gap": "Выше видимость по инфозапросам"},
            {"domain": "competitor-c.ru", "gap": "Сильнее ссылочный профиль"},
        ]

        recommendations = [
            "Собрать и кластеризовать семантику по коммерческим и информационным интентам",
            "Оптимизировать ключевые страницы под E-E-A-T и коммерческие факторы",
            "Ускорить Core Web Vitals и внедрить технический мониторинг",
            "Сделать контент-план и усилить внутреннюю перелинковку",
        ]

        summary = (
            "Покажем за 30 минут, почему сайт не приносит заявки. "
            "Выявлены критические точки роста в техническом SEO, спросе и сравнении с конкурентами."
        )

        return SeoReport(
            report_id=report_id,
            site_url=lead.site_url,
            summary=summary,
            critical_errors=critical_errors,
            demand_score=demand_score,
            competitors=competitors,
            recommendations=recommendations,
            created_at=created_at,
            expires_at=expires_at,
        )
