from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from app.utils.jwt import get_current_user
from app.utils.summary import get_weekly_summary, get_summary_for_range

router = APIRouter()


def _parse_date(value: str, field_name: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"{field_name} must be YYYY-MM-DD")


def _month_range(month: str):
    try:
        start = datetime.strptime(month, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="month must be YYYY-MM")

    if start.month == 12:
        next_month = date(start.year + 1, 1, 1)
    else:
        next_month = date(start.year, start.month + 1, 1)
    end = next_month - timedelta(days=1)
    return start, end


def _pdf_escape(text: str):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(title: str, lines):
    text_lines = [title, ""] + [str(line) for line in lines]
    content = "BT /F1 12 Tf 50 790 Td 14 TL " + " ".join(f"({_pdf_escape(line)}) Tj T*" for line in text_lines) + " ET"
    content_bytes = content.encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>endobj\n",
        f"4 0 obj<< /Length {len(content_bytes)} >>stream\n".encode("ascii") + content_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    header = b"%PDF-1.4\n"
    output = bytearray(header)
    offsets = [0]
    for obj in objects:
        offsets.append(len(output))
        output.extend(obj)

    xref_start = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("ascii")
    )
    return bytes(output)


def _summary_lines(summary):
    return [
        f"Average calories: {summary.get('avg_calories', 0):.2f}",
        f"Workouts completed: {summary.get('workouts_completed', 0)}",
        f"Average sleep hours: {summary.get('avg_sleep', 0):.2f}",
        f"Average steps: {summary.get('avg_steps', 0):.2f}",
        f"Average weight: {summary.get('avg_weight', 0):.2f}",
    ]


@router.get("/weekly")
def weekly_summary_report(week_start: str, user_id: str = Depends(get_current_user)):
    start = _parse_date(week_start, "week_start")
    summary = get_weekly_summary(user_id, start.isoformat())
    return {
        "period": "weekly",
        "week_start": start.isoformat(),
        "week_end": (start + timedelta(days=6)).isoformat(),
        "summary": summary,
    }


@router.get("/monthly")
def monthly_summary_report(month: str, user_id: str = Depends(get_current_user)):
    start, end = _month_range(month)
    summary = get_summary_for_range(user_id, start.isoformat(), end.isoformat())
    return {
        "period": "monthly",
        "month": month,
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "summary": summary,
    }


@router.get("/export")
def export_report_pdf(
    period: str = "weekly",
    week_start: str = None,
    month: str = None,
    user_id: str = Depends(get_current_user),
):
    if period == "weekly":
        if not week_start:
            raise HTTPException(status_code=400, detail="week_start is required for weekly export")
        start = _parse_date(week_start, "week_start")
        summary = get_weekly_summary(user_id, start.isoformat())
        title = f"Health Tracker Weekly Report ({start.isoformat()} to {(start + timedelta(days=6)).isoformat()})"
        filename = f"weekly-report-{start.isoformat()}.pdf"
    elif period == "monthly":
        if not month:
            raise HTTPException(status_code=400, detail="month is required for monthly export")
        start, end = _month_range(month)
        summary = get_summary_for_range(user_id, start.isoformat(), end.isoformat())
        title = f"Health Tracker Monthly Report ({month})"
        filename = f"monthly-report-{month}.pdf"
    else:
        raise HTTPException(status_code=400, detail="period must be weekly or monthly")

    pdf_bytes = _build_pdf(title, _summary_lines(summary))
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
