from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .yandex_collectors import collect_keywords_from_wordstat, enrich_keywords_with_direct


@dataclass
class KeywordStat:
    phrase: str
    frequency: int
    cpc: float
    monthly_clicks: int
    source: str


@dataclass
class MediaPlan:
    niche_description: str
    region: str
    objective: str
    monthly_budget: float
    keywords: List[KeywordStat]
    notes: List[str]

    @property
    def average_cpc(self) -> float:
        if not self.keywords:
            return 0.0
        return sum(k.cpc for k in self.keywords) / len(self.keywords)

    @property
    def expected_clicks(self) -> int:
        if not self.average_cpc:
            return 0
        return int(self.monthly_budget / self.average_cpc)


DEFAULT_NOTES = [
    "Данные Wordstat и Direct могут требовать авторизацию Яндекса и подтверждение капчи.",
    "Если онлайн-сбор данных недоступен, используется оценочная модель на основе текстовой релевантности.",
    "Перед запуском кампании рекомендуется проверить ставки и прогноз в интерфейсе Яндекс Директа вручную.",
]


def build_media_plan(
    niche_description: str,
    region: str,
    monthly_budget: float,
    objective: str,
) -> MediaPlan:
    raw_keywords = collect_keywords_from_wordstat(niche_description=niche_description, region=region)
    enriched = enrich_keywords_with_direct(raw_keywords, region=region)

    keywords = [
        KeywordStat(
            phrase=item["phrase"],
            frequency=int(item["frequency"]),
            cpc=float(item["cpc"]),
            monthly_clicks=int(item["frequency"] * 0.12),
            source=item["source"],
        )
        for item in enriched
    ]

    return MediaPlan(
        niche_description=niche_description,
        region=region,
        objective=objective,
        monthly_budget=monthly_budget,
        keywords=keywords,
        notes=DEFAULT_NOTES,
    )
