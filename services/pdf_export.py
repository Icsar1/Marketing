from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .media_planner import MediaPlan


def render_media_plan_pdf(plan: MediaPlan) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleRu", parent=styles["Heading1"], fontSize=18, leading=24)
    body = ParagraphStyle("BodyRu", parent=styles["BodyText"], fontSize=10, leading=14)

    story = [
        Paragraph("Медиаплан для Яндекс Директа", title),
        Spacer(1, 10),
        Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", body),
        Paragraph(f"Ниша: {plan.niche_description}", body),
        Paragraph(f"Регион: {plan.region}", body),
        Paragraph(f"Цель: {plan.objective}", body),
        Paragraph(f"Бюджет в месяц: {plan.monthly_budget:,.0f} ₽".replace(",", " "), body),
        Spacer(1, 12),
    ]

    table_data = [["Ключевая фраза", "Частотность", "CPC, ₽", "Оценка кликов/мес", "Источник"]]
    for kw in plan.keywords:
        table_data.append(
            [kw.phrase, str(kw.frequency), f"{kw.cpc:.2f}", str(kw.monthly_clicks), kw.source]
        )

    table = Table(table_data, colWidths=[165, 65, 55, 85, 130])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (3, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Средний CPC: {plan.average_cpc:.2f} ₽", body))
    story.append(Paragraph(f"Прогноз кликов при бюджете: {plan.expected_clicks}", body))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Примечания:", styles["Heading3"]))
    for note in plan.notes:
        story.append(Paragraph(f"• {note}", body))

    doc.build(story)
    return buffer.getvalue()
