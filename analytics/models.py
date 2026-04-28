from datetime import date
from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TechStack(models.Model):
    CATEGORY_CHOICES = [
        ("backend", "Backend"),
        ("frontend", "Frontend"),
        ("mobile", "Mobile"),
        ("data", "Data / ML"),
        ("devops", "DevOps / Infra"),
        ("qa", "QA"),
        ("other", "Другое"),
    ]

    name = models.CharField("Название", max_length=80, unique=True)
    category = models.CharField(
        "Категория", max_length=20, choices=CATEGORY_CHOICES, default="other"
    )

    class Meta:
        verbose_name = "Технология"
        verbose_name_plural = "Технологии / стеки"
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name


class Grade(models.Model):
    LEVEL_CHOICES = [
        (1, "Intern"),
        (2, "Junior"),
        (3, "Middle"),
        (4, "Senior"),
        (5, "Lead"),
        (6, "Principal"),
    ]

    level = models.PositiveSmallIntegerField(
        "Уровень", choices=LEVEL_CHOICES, unique=True
    )

    class Meta:
        verbose_name = "Грейд"
        verbose_name_plural = "Грейды"
        ordering = ["level"]

    def __str__(self) -> str:
        return self.get_level_display()

    @property
    def name(self) -> str:
        return self.get_level_display()


class Employee(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_TERMINATED = "terminated"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Работает"),
        (STATUS_TERMINATED, "Уволен(а)"),
    ]

    REASON_CHOICES = [
        ("voluntary", "По собственному желанию"),
        ("better_offer", "Перешёл(шла) к конкуренту"),
        ("relocation", "Переезд / релокация"),
        ("performance", "Низкая эффективность"),
        ("layoff", "Сокращение"),
        ("other", "Другое"),
    ]

    full_name = models.CharField("ФИО", max_length=150)
    email = models.EmailField("Email", unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name="Отдел",
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name="Грейд",
    )
    tech_stacks = models.ManyToManyField(
        TechStack,
        related_name="employees",
        verbose_name="Стек технологий",
        blank=True,
    )
    salary = models.DecimalField(
        "Зарплата (₸/мес)", max_digits=10, decimal_places=2
    )
    hire_date = models.DateField("Дата найма")
    termination_date = models.DateField(
        "Дата увольнения", null=True, blank=True
    )
    termination_reason = models.CharField(
        "Причина увольнения",
        max_length=20,
        choices=REASON_CHOICES,
        blank=True,
    )
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["-hire_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["hire_date"]),
            models.Index(fields=["termination_date"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def is_active(self) -> bool:
        return self.status == self.STATUS_ACTIVE

    @property
    def tenure_days(self) -> int:
        """Стаж в компании в днях."""
        end = self.termination_date or timezone.localdate()
        return (end - self.hire_date).days

    @property
    def tenure_years(self) -> float:
        return round(self.tenure_days / 365.25, 2)

    def save(self, *args, **kwargs):
        if self.termination_date and self.status != self.STATUS_TERMINATED:
            self.status = self.STATUS_TERMINATED
        if self.status == self.STATUS_ACTIVE:
            self.termination_date = None
            self.termination_reason = ""
        super().save(*args, **kwargs)


class Vacancy(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыта"),
        (STATUS_CLOSED, "Закрыта"),
        (STATUS_CANCELLED, "Отменена"),
    ]

    title = models.CharField("Название вакансии", max_length=160)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="vacancies",
        verbose_name="Отдел",
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        related_name="vacancies",
        verbose_name="Требуемый грейд",
    )
    tech_stacks = models.ManyToManyField(
        TechStack,
        related_name="vacancies",
        verbose_name="Требуемый стек",
        blank=True,
    )
    salary_min = models.DecimalField(
        "Зарплата от", max_digits=10, decimal_places=2
    )
    salary_max = models.DecimalField(
        "Зарплата до", max_digits=10, decimal_places=2
    )
    opened_at = models.DateField("Дата открытия")
    closed_at = models.DateField("Дата закрытия", null=True, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN
    )
    hired_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacancies",
        verbose_name="Нанятый сотрудник",
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["opened_at"]),
            models.Index(fields=["closed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    @property
    def days_to_close(self) -> int | None:
        if self.closed_at:
            return (self.closed_at - self.opened_at).days
        return None

    @property
    def days_open(self) -> int:
        end = self.closed_at or timezone.localdate()
        return (end - self.opened_at).days

    def save(self, *args, **kwargs):
        if self.closed_at and self.status == self.STATUS_OPEN:
            self.status = self.STATUS_CLOSED
        super().save(*args, **kwargs)
