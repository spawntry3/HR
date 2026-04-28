"""Views для дашборда HR-аналитики."""

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import analytics_service as svc
from .models import Department, Employee, Grade, TechStack, Vacancy


def _build_chart_data() -> dict:
    return {
        "turnover_by_month": svc.turnover_by_month(12),
        "turnover_reasons": svc.turnover_reasons(),
        "salary_by_grade": svc.salary_by_grade(),
        "salary_by_stack": svc.salary_by_stack(12),
        "salary_distribution": svc.salary_distribution(10),
        "time_to_close_by_department": svc.time_to_close_by_department(),
        "time_to_close_by_grade": svc.time_to_close_by_grade(),
        "vacancies_status": svc.vacancies_status_counts(),
        "headcount_by_department": svc.headcount_by_department(),
        "stack_popularity": svc.stack_popularity(15),
    }


def dashboard(request):
    context = {
        "kpis": svc.kpi_summary(),
        "chart_data": _build_chart_data(),
        "recent_terminations": (
            Employee.objects.filter(status=Employee.STATUS_TERMINATED)
            .select_related("department", "grade")
            .order_by("-termination_date")[:8]
        ),
        "open_vacancies": (
            Vacancy.objects.filter(status=Vacancy.STATUS_OPEN)
            .select_related("department", "grade")
            .order_by("opened_at")[:8]
        ),
    }
    return render(request, "dashboard.html", context)


def employees_list(request):
    qs = (
        Employee.objects
        .select_related("department", "grade")
        .prefetch_related("tech_stacks")
        .order_by("-hire_date")
    )

    q = (request.GET.get("q") or "").strip()
    dept = request.GET.get("department") or ""
    grade = request.GET.get("grade") or ""
    status = request.GET.get("status") or ""

    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q))
    if dept.isdigit():
        qs = qs.filter(department_id=int(dept))
    if grade.isdigit():
        qs = qs.filter(grade_id=int(grade))
    if status in (Employee.STATUS_ACTIVE, Employee.STATUS_TERMINATED):
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "employees.html", {
        "page_obj": page,
        "departments": Department.objects.order_by("name"),
        "grades": Grade.objects.order_by("level"),
        "filters": {"q": q, "department": dept, "grade": grade, "status": status},
        "total": paginator.count,
        "active_count": Employee.objects.filter(status=Employee.STATUS_ACTIVE).count(),
    })


def vacancies_list(request):
    qs = (
        Vacancy.objects
        .select_related("department", "grade", "hired_employee")
        .prefetch_related("tech_stacks")
        .order_by("-opened_at")
    )

    dept = request.GET.get("department") or ""
    grade = request.GET.get("grade") or ""
    status = request.GET.get("status") or ""
    q = (request.GET.get("q") or "").strip()

    if q:
        qs = qs.filter(title__icontains=q)
    if dept.isdigit():
        qs = qs.filter(department_id=int(dept))
    if grade.isdigit():
        qs = qs.filter(grade_id=int(grade))
    if status in dict(Vacancy.STATUS_CHOICES):
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "vacancies.html", {
        "page_obj": page,
        "departments": Department.objects.order_by("name"),
        "grades": Grade.objects.order_by("level"),
        "status_choices": Vacancy.STATUS_CHOICES,
        "filters": {"q": q, "department": dept, "grade": grade, "status": status},
        "total": paginator.count,
        "open_count": Vacancy.objects.filter(status=Vacancy.STATUS_OPEN).count(),
    })


def salaries_page(request):
    chart_data = {
        "salary_by_grade": svc.salary_by_grade(),
        "salary_by_stack": svc.salary_by_stack(15),
        "salary_distribution": svc.salary_distribution(12),
        "headcount_by_department": svc.headcount_by_department(),
    }

    by_dept = (
        Employee.objects.filter(status=Employee.STATUS_ACTIVE)
        .values("department__name")
        .annotate(avg=Avg("salary"), cnt=Count("id"))
        .order_by("-avg")
    )
    chart_data["salary_by_department"] = {
        "labels": [r["department__name"] for r in by_dept],
        "avg":    [float(r["avg"] or 0) for r in by_dept],
        "count":  [r["cnt"] for r in by_dept],
    }

    overall = Employee.objects.filter(status=Employee.STATUS_ACTIVE)
    avg_total = overall.aggregate(v=Avg("salary"))["v"]

    return render(request, "salaries.html", {
        "chart_data": chart_data,
        "avg_total": avg_total,
        "total_active": overall.count(),
    })


def turnover_page(request):
    chart_data = {
        "turnover_by_month": svc.turnover_by_month(12),
        "turnover_reasons": svc.turnover_reasons(),
    }

    by_dept = (
        Department.objects.annotate(
            terminated=Count("employees",
                             filter=Q(employees__status=Employee.STATUS_TERMINATED)),
            active=Count("employees",
                         filter=Q(employees__status=Employee.STATUS_ACTIVE)),
        ).order_by("-terminated")
    )
    chart_data["turnover_by_department"] = {
        "labels": [d.name for d in by_dept],
        "terminated": [d.terminated for d in by_dept],
        "active": [d.active for d in by_dept],
    }

    by_grade = (
        Grade.objects.annotate(
            terminated=Count("employees",
                             filter=Q(employees__status=Employee.STATUS_TERMINATED)),
            active=Count("employees",
                         filter=Q(employees__status=Employee.STATUS_ACTIVE)),
        ).order_by("level")
    )
    chart_data["turnover_by_grade"] = {
        "labels": [g.get_level_display() for g in by_grade],
        "terminated": [g.terminated for g in by_grade],
        "active": [g.active for g in by_grade],
    }

    terminated_qs = Employee.objects.filter(status=Employee.STATUS_TERMINATED)
    avg_tenure_days = 0
    if terminated_qs.exists():
        days = [
            (e.termination_date - e.hire_date).days
            for e in terminated_qs.only("hire_date", "termination_date")
            if e.termination_date and e.hire_date
        ]
        avg_tenure_days = round(sum(days) / len(days)) if days else 0

    return render(request, "turnover.html", {
        "chart_data": chart_data,
        "total_terminated": terminated_qs.count(),
        "total_active": Employee.objects.filter(status=Employee.STATUS_ACTIVE).count(),
        "avg_tenure_days": avg_tenure_days,
    })


@require_GET
def api_charts(request):
    return JsonResponse(_build_chart_data())

