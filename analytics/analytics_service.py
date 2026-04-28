from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth

from .models import Employee, Grade, TechStack, Vacancy


@dataclass
class KpiCard:
    title: str
    value: str
    subtitle: str = ""
    trend: str = ""


def _format_money(value) -> str:
    if value is None:
        return "—"
    return f"{int(value):,} ₸".replace(",", " ")


def kpi_summary(today: date | None = None) -> list[KpiCard]:
    """Главные KPI-карточки для дашборда."""
    today = today or date.today()
    year_ago = today - timedelta(days=365)

    total_active = Employee.objects.filter(status=Employee.STATUS_ACTIVE).count()
    avg_salary = (
        Employee.objects.filter(status=Employee.STATUS_ACTIVE).aggregate(
            v=Avg("salary")
        )["v"]
    )

    fund = (
        Employee.objects.filter(status=Employee.STATUS_ACTIVE).aggregate(
            v=Sum("salary")
        )["v"]
        or Decimal("0")
    )

    turnover = turnover_rate(year_ago, today)

    closed_last_year = Vacancy.objects.filter(
        status=Vacancy.STATUS_CLOSED,
        closed_at__gte=year_ago,
        closed_at__lte=today,
    ).values_list("opened_at", "closed_at")
    diffs = [(c - o).days for o, c in closed_last_year if c and o]
    avg_close_days = round(sum(diffs) / len(diffs)) if diffs else 0

    open_vacs = Vacancy.objects.filter(status=Vacancy.STATUS_OPEN).count()

    return [
        KpiCard(
            title="Сотрудников",
            value=str(total_active),
            subtitle="активных в компании",
        ),
        KpiCard(
            title="ФОТ (мес.)",
            value=_format_money(fund),
            subtitle="суммарный фонд оплаты труда",
        ),
        KpiCard(
            title="Средняя ЗП",
            value=_format_money(avg_salary),
            subtitle="по активным сотрудникам",
        ),
        KpiCard(
            title="Текучесть (12 мес.)",
            value=f"{turnover:.1f} %",
            subtitle="annualized turnover rate",
        ),
        KpiCard(
            title="Открытых вакансий",
            value=str(open_vacs),
            subtitle="на текущий момент",
        ),
        KpiCard(
            title="Среднее время закрытия",
            value=f"{avg_close_days} дн.",
            subtitle="закрытые вакансии за 12 мес.",
        ),
    ]


def turnover_rate(start: date, end: date) -> float:
    """Annualized turnover = увольнения / среднюю численность × 100%."""
    terminated = Employee.objects.filter(
        termination_date__gte=start, termination_date__lte=end
    ).count()
    headcount_start = Employee.objects.filter(
        hire_date__lte=start
    ).filter(
        Q(termination_date__isnull=True) | Q(termination_date__gt=start)
    ).count()
    headcount_end = Employee.objects.filter(
        hire_date__lte=end
    ).filter(
        Q(termination_date__isnull=True) | Q(termination_date__gt=end)
    ).count()
    avg_headcount = (headcount_start + headcount_end) / 2 or 1
    return terminated / avg_headcount * 100


def turnover_by_month(months: int = 12) -> dict:
    """Текучесть и найм по месяцам."""
    today = date.today()
    start = date(today.year, today.month, 1) - timedelta(days=31 * (months - 1))
    start = date(start.year, start.month, 1)

    hired = (
        Employee.objects.filter(hire_date__gte=start)
        .annotate(m=TruncMonth("hire_date"))
        .values("m")
        .annotate(c=Count("id"))
        .order_by("m")
    )
    terminated = (
        Employee.objects.filter(termination_date__gte=start)
        .annotate(m=TruncMonth("termination_date"))
        .values("m")
        .annotate(c=Count("id"))
        .order_by("m")
    )

    months_list: list[date] = []
    cur = start
    for _ in range(months):
        months_list.append(cur)
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)

    hired_map = {row["m"].date() if hasattr(row["m"], "date") else row["m"]: row["c"] for row in hired}
    term_map = {row["m"].date() if hasattr(row["m"], "date") else row["m"]: row["c"] for row in terminated}

    labels = [m.strftime("%b %y") for m in months_list]
    hired_data = [hired_map.get(m, 0) for m in months_list]
    term_data = [term_map.get(m, 0) for m in months_list]

    return {
        "labels": labels,
        "hired": hired_data,
        "terminated": term_data,
    }


def turnover_reasons() -> dict:
    """Распределение причин увольнений."""
    qs = (
        Employee.objects.filter(status=Employee.STATUS_TERMINATED)
        .values("termination_reason")
        .annotate(c=Count("id"))
        .order_by("-c")
    )
    reason_map = dict(Employee.REASON_CHOICES)
    labels = []
    data = []
    for row in qs:
        key = row["termination_reason"] or "other"
        labels.append(reason_map.get(key, "Другое"))
        data.append(row["c"])
    return {"labels": labels, "data": data}


def salary_by_grade() -> dict:
    """Средняя/мин/макс ЗП по грейдам."""
    qs = (
        Grade.objects.annotate(
            avg=Avg("employees__salary", filter=Q(employees__status=Employee.STATUS_ACTIVE)),
            mn=Min("employees__salary", filter=Q(employees__status=Employee.STATUS_ACTIVE)),
            mx=Max("employees__salary", filter=Q(employees__status=Employee.STATUS_ACTIVE)),
            cnt=Count("employees", filter=Q(employees__status=Employee.STATUS_ACTIVE)),
        )
        .order_by("level")
    )
    return {
        "labels": [g.get_level_display() for g in qs],
        "avg": [float(g.avg or 0) for g in qs],
        "min": [float(g.mn or 0) for g in qs],
        "max": [float(g.mx or 0) for g in qs],
        "count": [g.cnt for g in qs],
    }


def salary_by_stack(limit: int = 12) -> dict:
    """Средняя ЗП по технологиям/стекам."""
    qs = (
        TechStack.objects.annotate(
            avg=Avg(
                "employees__salary",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
            ),
            cnt=Count(
                "employees",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
                distinct=True,
            ),
        )
        .filter(cnt__gt=0)
        .order_by("-avg")[:limit]
    )
    return {
        "labels": [t.name for t in qs],
        "avg": [float(t.avg or 0) for t in qs],
        "count": [t.cnt for t in qs],
        "categories": [t.get_category_display() for t in qs],
    }


def salary_distribution(bins: int = 10) -> dict:
    """Гистограмма распределения зарплат."""
    salaries = list(
        Employee.objects.filter(status=Employee.STATUS_ACTIVE)
        .values_list("salary", flat=True)
    )
    if not salaries:
        return {"labels": [], "data": []}
    salaries = [float(s) for s in salaries]
    lo, hi = min(salaries), max(salaries)
    if hi == lo:
        return {"labels": [f"{int(lo):,} ₸".replace(",", " ")], "data": [len(salaries)]}
    step = (hi - lo) / bins
    counts = [0] * bins
    for s in salaries:
        idx = min(int((s - lo) / step), bins - 1)
        counts[idx] += 1
    labels = []
    for i in range(bins):
        a = lo + i * step
        b = lo + (i + 1) * step
        labels.append(
            f"{int(a/1000)}—{int(b/1000)}k"
        )
    return {"labels": labels, "data": counts}


def time_to_close_by_department() -> dict:
    """Среднее время закрытия вакансий по отделам."""
    closed = Vacancy.objects.filter(
        status=Vacancy.STATUS_CLOSED, closed_at__isnull=False
    )
    rows: dict[str, list[int]] = {}
    for v in closed.select_related("department"):
        rows.setdefault(v.department.name, []).append(v.days_to_close or 0)
    labels = sorted(rows.keys())
    avg = [round(sum(rows[k]) / len(rows[k]), 1) for k in labels]
    counts = [len(rows[k]) for k in labels]
    return {"labels": labels, "avg": avg, "count": counts}


def time_to_close_by_grade() -> dict:
    """Среднее время закрытия по грейдам."""
    closed = Vacancy.objects.filter(
        status=Vacancy.STATUS_CLOSED, closed_at__isnull=False
    ).select_related("grade")
    rows: dict[str, list[int]] = {}
    grade_levels: dict[str, int] = {}
    for v in closed:
        name = v.grade.get_level_display()
        rows.setdefault(name, []).append(v.days_to_close or 0)
        grade_levels[name] = v.grade.level
    labels = sorted(rows.keys(), key=lambda n: grade_levels[n])
    avg = [round(sum(rows[k]) / len(rows[k]), 1) for k in labels]
    return {"labels": labels, "avg": avg}


def vacancies_status_counts() -> dict:
    """Сколько вакансий в каждом статусе."""
    qs = (
        Vacancy.objects.values("status").annotate(c=Count("id")).order_by("status")
    )
    status_map = dict(Vacancy.STATUS_CHOICES)
    labels = [status_map.get(r["status"], r["status"]) for r in qs]
    data = [r["c"] for r in qs]
    return {"labels": labels, "data": data}


def headcount_by_department() -> dict:
    """Численность по отделам (активные)."""
    from .models import Department
    qs = (
        Department.objects.annotate(
            cnt=Count("employees", filter=Q(employees__status=Employee.STATUS_ACTIVE))
        )
        .filter(cnt__gt=0)
        .order_by("-cnt")
    )
    return {
        "labels": [d.name for d in qs],
        "data": [d.cnt for d in qs],
    }


def stack_popularity(limit: int = 15) -> dict:
    """Топ технологий по числу владеющих сотрудников."""
    qs = (
        TechStack.objects.annotate(
            cnt=Count(
                "employees",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
                distinct=True,
            )
        )
        .filter(cnt__gt=0)
        .order_by("-cnt")[:limit]
    )
    return {
        "labels": [t.name for t in qs],
        "data": [t.cnt for t in qs],
    }
