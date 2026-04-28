from django.contrib import admin
from django.db.models import Avg, Count, Q
from django.utils.html import format_html

from .models import Department, Employee, Grade, TechStack, Vacancy


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "employees_count", "active_count", "open_vacancies")
    search_fields = ("name", "description")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _employees_count=Count("employees", distinct=True),
            _active_count=Count(
                "employees",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
                distinct=True,
            ),
            _open_vacancies=Count(
                "vacancies",
                filter=Q(vacancies__status=Vacancy.STATUS_OPEN),
                distinct=True,
            ),
        )

    @admin.display(description="Всего сотрудников", ordering="_employees_count")
    def employees_count(self, obj):
        return obj._employees_count

    @admin.display(description="Активных", ordering="_active_count")
    def active_count(self, obj):
        return obj._active_count

    @admin.display(description="Открытых вакансий", ordering="_open_vacancies")
    def open_vacancies(self, obj):
        return obj._open_vacancies


@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "employees_count", "avg_salary")
    list_filter = ("category",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _employees_count=Count(
                "employees",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
                distinct=True,
            ),
            _avg_salary=Avg(
                "employees__salary",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
            ),
        )

    @admin.display(description="Сотрудников (активных)", ordering="_employees_count")
    def employees_count(self, obj):
        return obj._employees_count

    @admin.display(description="Средняя ЗП, ₸", ordering="_avg_salary")
    def avg_salary(self, obj):
        if obj._avg_salary is None:
            return "—"
        return f"{int(obj._avg_salary):,} ₸".replace(",", " ")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "employees_count", "avg_salary")
    ordering = ("level",)
    search_fields = ("level",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _employees_count=Count(
                "employees",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
                distinct=True,
            ),
            _avg_salary=Avg(
                "employees__salary",
                filter=Q(employees__status=Employee.STATUS_ACTIVE),
            ),
        )

    @admin.display(description="Сотрудников", ordering="_employees_count")
    def employees_count(self, obj):
        return obj._employees_count

    @admin.display(description="Средняя ЗП, ₸", ordering="_avg_salary")
    def avg_salary(self, obj):
        if obj._avg_salary is None:
            return "—"
        return f"{int(obj._avg_salary):,} ₸".replace(",", " ")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "department",
        "grade",
        "salary_formatted",
        "status_badge",
        "hire_date",
        "termination_date",
        "tenure_display",
    )
    list_filter = (
        "status",
        "department",
        "grade",
        "termination_reason",
        "tech_stacks",
    )
    search_fields = ("full_name", "email")
    autocomplete_fields = ("department", "grade")
    filter_horizontal = ("tech_stacks",)
    date_hierarchy = "hire_date"
    list_per_page = 30
    fieldsets = (
        ("Личные данные", {"fields": ("full_name", "email")}),
        (
            "Работа",
            {
                "fields": (
                    "department",
                    "grade",
                    "tech_stacks",
                    "salary",
                )
            },
        ),
        (
            "Сроки и статус",
            {
                "fields": (
                    "status",
                    "hire_date",
                    "termination_date",
                    "termination_reason",
                )
            },
        ),
    )
    readonly_fields = ()

    @admin.display(description="ЗП, ₸", ordering="salary")
    def salary_formatted(self, obj):
        return f"{int(obj.salary):,} ₸".replace(",", " ")

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        if obj.status == Employee.STATUS_ACTIVE:
            color = "#10b981"
            label = "Работает"
        else:
            color = "#f43f5e"
            label = "Уволен(а)"
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 11px;'
            'border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.3px;">{}</span>',
            color, label,
        )

    @admin.display(description="Стаж")
    def tenure_display(self, obj):
        years = obj.tenure_years
        return f"{years} г."


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "department",
        "grade",
        "salary_range",
        "opened_at",
        "closed_at",
        "status_badge",
        "days_display",
    )
    list_filter = ("status", "department", "grade", "tech_stacks")
    search_fields = ("title",)
    autocomplete_fields = ("department", "grade", "hired_employee")
    filter_horizontal = ("tech_stacks",)
    date_hierarchy = "opened_at"
    list_per_page = 30

    fieldsets = (
        ("Описание", {"fields": ("title", "department", "grade", "tech_stacks")}),
        ("Зарплата", {"fields": ("salary_min", "salary_max")}),
        (
            "Сроки",
            {"fields": ("status", "opened_at", "closed_at", "hired_employee")},
        ),
    )

    @admin.display(description="ЗП-вилка")
    def salary_range(self, obj):
        return (
            f"{int(obj.salary_min):,}—{int(obj.salary_max):,} ₸".replace(",", " ")
        )

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        colors = {
            Vacancy.STATUS_OPEN: "#10b981",
            Vacancy.STATUS_CLOSED: "#f43f5e",
            Vacancy.STATUS_CANCELLED: "#f43f5e",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 11px;'
            'border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.3px;">{}</span>',
            colors.get(obj.status, "#f43f5e"),
            obj.get_status_display(),
        )

    @admin.display(description="Дней")
    def days_display(self, obj):
        if obj.status == Vacancy.STATUS_CLOSED and obj.closed_at:
            return f"{obj.days_to_close} (закрыта)"
        if obj.status == Vacancy.STATUS_OPEN:
            return f"{obj.days_open} (открыта)"
        return "—"
