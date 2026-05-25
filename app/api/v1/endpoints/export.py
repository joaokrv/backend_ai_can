import io
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.api import deps
from app.services.plano_service import get_plano_detalhado_or_403
from app.core.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

_DARK = colors.HexColor("#0D0D0D")
_LIME = colors.HexColor("#D4FF00")
_GRAY = colors.HexColor("#A0A0A0")
_BORDER = colors.HexColor("#2A2A2A")


def _safe_str(value, max_len: int = 500) -> str:
    """Converte para string segura para ReportLab (ASCII + latin-1)."""
    if value is None:
        return ""
    return str(value)[:max_len]


def _build_pdf(plano) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"], fontSize=18, textColor=_DARK, spaceAfter=4
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontSize=12, textColor=_DARK, spaceBefore=12, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Heading3"], fontSize=10, textColor=_GRAY, spaceBefore=8, spaceAfter=2
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=9, textColor=_DARK, spaceAfter=2
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"], fontSize=8, textColor=_GRAY
    )

    story = []

    data_str = plano.created_at.strftime("%d/%m/%Y") if plano.created_at else ""
    story.append(Paragraph(_safe_str(plano.nome), title_style))
    if data_str:
        story.append(Paragraph(f"Gerado em {data_str}", small_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
    story.append(Spacer(1, 0.3 * cm))

    if plano.explicacao_ia:
        story.append(Paragraph("Por que esse plano?", section_style))
        story.append(Paragraph(_safe_str(plano.explicacao_ia, 2000), body_style))
        story.append(Spacer(1, 0.4 * cm))

    if plano.dias:
        story.append(Paragraph("Treino", section_style))
        for dia in sorted(plano.dias, key=lambda d: d.ordem or 0):
            label = _safe_str(dia.identificacao)
            if dia.foco_muscular:
                label += f" - {_safe_str(dia.foco_muscular)}"
            story.append(Paragraph(label, sub_style))

            if dia.exercicios:
                table_data = [["Exercicio", "Series", "Reps", "Descanso"]]
                for ex in sorted(dia.exercicios, key=lambda e: e.ordem or 0):
                    descanso = f"{ex.descanso_segundos}s" if ex.descanso_segundos else "-"
                    table_data.append([
                        _safe_str(ex.nome),
                        str(ex.series) if ex.series else "-",
                        _safe_str(ex.repeticoes) if ex.repeticoes else "-",
                        descanso,
                    ])

                t = Table(table_data, colWidths=[9 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), _LIME),
                    ("TEXTCOLOR", (0, 0), (-1, 0), _DARK),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.2 * cm))

    if plano.refeicoes:
        story.append(Spacer(1, 0.4 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=_BORDER))
        story.append(Paragraph("Sugestoes Nutricionais", section_style))

        for tipo_label, tipo_val in [("Pre-treino", "pre_treino"), ("Pos-treino", "pos_treino")]:
            refeicoes_tipo = [r for r in plano.refeicoes if r.tipo == tipo_val]
            if not refeicoes_tipo:
                continue
            story.append(Paragraph(tipo_label, sub_style))
            for ref in refeicoes_tipo:
                story.append(Paragraph(f"<b>{_safe_str(ref.nome)}</b>", body_style))
                if ref.ingredientes:
                    ingredientes_str = ", ".join(_safe_str(i) for i in ref.ingredientes)
                    story.append(Paragraph(ingredientes_str[:300], small_style))
                macros_parts = []
                if ref.calorias:
                    macros_parts.append(f"{ref.calorias} kcal")
                if ref.proteina_g:
                    macros_parts.append(f"P: {ref.proteina_g}g")
                if ref.carboidrato_g:
                    macros_parts.append(f"C: {ref.carboidrato_g}g")
                if ref.gordura_g:
                    macros_parts.append(f"G: {ref.gordura_g}g")
                if macros_parts:
                    story.append(Paragraph(" - ".join(macros_parts), small_style))
                story.append(Spacer(1, 0.15 * cm))

    doc.build(story)
    return buf.getvalue()


@router.post("/{plano_id}/export")
@limiter.limit("10/hour")
def exportar_plano_pdf(
    request: Request,
    plano_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    plano = get_plano_detalhado_or_403(plano_id, current_user.id, session)

    try:
        pdf_bytes = _build_pdf(plano)
    except Exception:
        logger.error("Falha ao gerar PDF: plano_id=%s user_id=%s", plano_id, current_user.id, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao gerar PDF. Tente novamente.")

    nome_arquivo = (plano.nome or "plano").replace(" ", "_").lower()[:50]
    logger.info("Export PDF: plano_id=%s user_id=%s", plano_id, current_user.id)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="plano_{nome_arquivo}.pdf"'},
    )