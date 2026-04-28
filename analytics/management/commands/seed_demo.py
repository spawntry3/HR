from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from analytics.models import (
    Department,
    Employee,
    Grade,
    TechStack,
    Vacancy,
)

DEPARTMENTS = [
    ("Backend", "Разработка серверной части и API"),
    ("Frontend", "Разработка веб-интерфейсов"),
    ("Mobile", "iOS/Android-разработка"),
    ("Data & ML", "Data Engineering, аналитика и ML"),
    ("DevOps", "Инфраструктура, CI/CD, SRE"),
    ("QA", "Контроль качества и автотесты"),
    ("Design", "UX/UI-дизайн"),
    ("Product", "Продуктовый менеджмент"),
]

STACKS = [
    ("Python", "backend"),
    ("Django", "backend"),
    ("FastAPI", "backend"),
    ("Go", "backend"),
    ("Java", "backend"),
    ("Kotlin", "mobile"),
    ("Swift", "mobile"),
    ("React", "frontend"),
    ("TypeScript", "frontend"),
    ("Vue", "frontend"),
    ("Next.js", "frontend"),
    ("PostgreSQL", "backend"),
    ("ClickHouse", "data"),
    ("Spark", "data"),
    ("Airflow", "data"),
    ("PyTorch", "data"),
    ("Kubernetes", "devops"),
    ("Terraform", "devops"),
    ("Docker", "devops"),
    ("AWS", "devops"),
    ("Selenium", "qa"),
    ("Pytest", "qa"),
    ("Cypress", "qa"),
    ("Figma", "other"),
]

DEPT_STACKS = {
    "Backend": ["Python", "Django", "FastAPI", "Go", "Java", "PostgreSQL"],
    "Frontend": ["React", "TypeScript", "Vue", "Next.js"],
    "Mobile": ["Kotlin", "Swift"],
    "Data & ML": ["Python", "ClickHouse", "Spark", "Airflow", "PyTorch", "PostgreSQL"],
    "DevOps": ["Kubernetes", "Terraform", "Docker", "AWS"],
    "QA": ["Selenium", "Pytest", "Cypress"],
    "Design": ["Figma"],
    "Product": ["Figma"],
}

FIRST_NAMES = [
    "Александр", "Дмитрий", "Максим", "Иван", "Артём", "Никита", "Михаил",
    "Андрей", "Илья", "Кирилл", "Роман", "Сергей", "Павел", "Денис",
    "Анастасия", "Мария", "Анна", "Екатерина", "Ольга", "Юлия", "Виктория",
    "Дарья", "Наталья", "Полина", "Алина", "Елена", "Татьяна", "Ксения",
]

LAST_NAMES = [
    "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров", "Соколов",
    "Михайлов", "Новиков", "Фёдоров", "Морозов", "Волков", "Алексеев", "Лебедев",
    "Семёнов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев", "Орлов",
    "Андреев", "Макаров", "Никитин", "Захаров", "Зайцев", "Соловьёв", "Борисов",
]

VACANCY_TITLES = {
    "Backend": ["Backend-разработчик", "Senior Python Engineer", "Go Developer"],
    "Frontend": ["Frontend-разработчик", "React Engineer", "Tech Lead Frontend"],
    "Mobile": ["iOS-разработчик", "Android-разработчик"],
    "Data & ML": ["Data Engineer", "ML Engineer", "Data Analyst"],
    "DevOps": ["DevOps Engineer", "SRE", "Cloud Architect"],
    "QA": ["QA Engineer", "QA Automation"],
    "Design": ["Product Designer"],
    "Product": ["Product Manager"],
}

GRADE_BASE_SALARY = {
    1: 60_000,
    2: 110_000,
    3: 200_000,
    4: 320_000,
    5: 450_000,
    6: 600_000,
}

STACK_MULTIPLIER = {
    "Go": 1.10,
    "Kotlin": 1.08,
    "Swift": 1.10,
    "PyTorch": 1.12,
    "Spark": 1.08,
    "Kubernetes": 1.10,
    "Terraform": 1.06,
    "AWS": 1.07,
    "Next.js": 1.05,
    "ClickHouse": 1.08,
}


class Command(BaseCommand):
    help = "Генерирует демо-данные для HR-аналитики IT-компании"

    def add_arguments(self, parser):
        parser.add_argument("--employees", type=int, default=200)
        parser.add_argument("--vacancies", type=int, default=80)
        parser.add_argument("--reset", action="store_true",
                            help="Удалить существующие данные перед заполнением")
        parser.add_argument("--admin", action="store_true",
                            help="Создать суперпользователя admin / admin12345")

    @transaction.atomic
    def handle(self, *args, **opts):
        random.seed(42)

        if opts["reset"]:
            self.stdout.write(self.style.WARNING("Очищаем данные…"))
            Vacancy.objects.all().delete()
            Employee.objects.all().delete()
            TechStack.objects.all().delete()
            Department.objects.all().delete()
            Grade.objects.all().delete()

        self._seed_grades()
        depts = self._seed_departments()
        stacks = self._seed_stacks()
        employees = self._seed_employees(depts, stacks, opts["employees"])
        self._seed_vacancies(depts, stacks, employees, opts["vacancies"])

        if opts["admin"]:
            self._create_admin()

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Сотрудников: {Employee.objects.count()}, "
            f"вакансий: {Vacancy.objects.count()}, "
            f"отделов: {Department.objects.count()}, "
            f"стеков: {TechStack.objects.count()}."
        ))

    def _seed_grades(self):
        for level, _ in Grade.LEVEL_CHOICES:
            Grade.objects.get_or_create(level=level)

    def _seed_departments(self):
        result = {}
        for name, desc in DEPARTMENTS:
            d, _ = Department.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            result[name] = d
        return result

    def _seed_stacks(self):
        result = {}
        for name, cat in STACKS:
            s, _ = TechStack.objects.get_or_create(
                name=name, defaults={"category": cat}
            )
            result[name] = s
        return result

    def _calc_salary(self, grade_level: int, stack_names: list[str]) -> Decimal:
        base = GRADE_BASE_SALARY[grade_level]
        mult = 1.0
        for s in stack_names:
            mult *= STACK_MULTIPLIER.get(s, 1.0)
        noise = random.uniform(0.88, 1.12)
        salary = base * mult * noise
        return Decimal(str(int(round(salary / 1000) * 1000)))

    def _random_hire_date(self) -> date:
        today = date.today()
        days_ago = random.randint(7, 365 * 5)
        return today - timedelta(days=days_ago)

    def _seed_employees(self, depts, stacks, count):
        grades = list(Grade.objects.order_by("level"))
        grade_weights = [1, 4, 6, 5, 2, 1]
        today = date.today()

        used_emails = set()
        employees = []
        for i in range(count):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            if fn[-1] in "ая" and not ln.endswith(("ва", "на", "ая")):
                ln = ln + "а"
            full_name = f"{fn} {ln}"
            email = f"{i+1}.{ln.lower()}@itcompany.ru"
            while email in used_emails:
                email = f"{random.randint(1000,9999)}.{ln.lower()}@itcompany.ru"
            used_emails.add(email)

            dept_name = random.choice(list(depts.keys()))
            dept = depts[dept_name]
            grade = random.choices(grades, weights=grade_weights, k=1)[0]

            possible_stacks = DEPT_STACKS.get(dept_name, [])
            n_stacks = min(len(possible_stacks), random.randint(2, 4))
            chosen = random.sample(possible_stacks, n_stacks) if possible_stacks else []

            salary = self._calc_salary(grade.level, chosen)
            hire = self._random_hire_date()

            terminated = random.random() < 0.18
            term_date = None
            term_reason = ""
            status = Employee.STATUS_ACTIVE
            if terminated:
                tenure = random.randint(60, max(61, (today - hire).days))
                term_date = hire + timedelta(days=tenure)
                if term_date >= today:
                    term_date = today - timedelta(days=random.randint(1, 30))
                term_reason = random.choice([c[0] for c in Employee.REASON_CHOICES])
                status = Employee.STATUS_TERMINATED

            emp = Employee.objects.create(
                full_name=full_name,
                email=email,
                department=dept,
                grade=grade,
                salary=salary,
                hire_date=hire,
                termination_date=term_date,
                termination_reason=term_reason,
                status=status,
            )
            if chosen:
                emp.tech_stacks.set([stacks[s] for s in chosen])
            employees.append(emp)
        return employees

    def _seed_vacancies(self, depts, stacks, employees, count):
        grades = list(Grade.objects.order_by("level"))
        grade_weights = [1, 4, 6, 5, 2, 1]
        today = date.today()

        for i in range(count):
            dept_name = random.choice(list(depts.keys()))
            dept = depts[dept_name]
            grade = random.choices(grades, weights=grade_weights, k=1)[0]
            title_pool = VACANCY_TITLES.get(dept_name, [f"{dept_name} Engineer"])
            title = random.choice(title_pool)

            opened = today - timedelta(days=random.randint(5, 365))

            possible_stacks = DEPT_STACKS.get(dept_name, [])
            n = min(len(possible_stacks), random.randint(2, 4))
            chosen = random.sample(possible_stacks, n) if possible_stacks else []

            base = GRADE_BASE_SALARY[grade.level]
            salary_min = Decimal(str(int(base * 0.9 / 1000) * 1000))
            salary_max = Decimal(str(int(base * 1.3 / 1000) * 1000))

            r = random.random()
            if r < 0.65:
                # Закрытая
                close_days = self._sample_time_to_close(grade.level, dept_name)
                closed = opened + timedelta(days=close_days)
                if closed > today:
                    closed = today - timedelta(days=random.randint(0, 5))
                hired = random.choice(
                    [e for e in employees if e.department_id == dept.id]
                ) if any(e.department_id == dept.id for e in employees) else None
                v = Vacancy.objects.create(
                    title=title,
                    department=dept,
                    grade=grade,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    opened_at=opened,
                    closed_at=closed,
                    status=Vacancy.STATUS_CLOSED,
                    hired_employee=hired,
                )
            elif r < 0.92:
                v = Vacancy.objects.create(
                    title=title,
                    department=dept,
                    grade=grade,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    opened_at=opened,
                    status=Vacancy.STATUS_OPEN,
                )
            else:
                cancel = opened + timedelta(days=random.randint(10, 60))
                if cancel > today:
                    cancel = today
                v = Vacancy.objects.create(
                    title=title,
                    department=dept,
                    grade=grade,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    opened_at=opened,
                    closed_at=cancel,
                    status=Vacancy.STATUS_CANCELLED,
                )
            if chosen:
                v.tech_stacks.set([stacks[s] for s in chosen])

    def _sample_time_to_close(self, grade_level: int, dept_name: str) -> int:
        base = {1: 14, 2: 25, 3: 40, 4: 60, 5: 80, 6: 110}[grade_level]
        dept_factor = {
            "Backend": 1.0, "Frontend": 0.9, "Mobile": 1.1, "Data & ML": 1.2,
            "DevOps": 1.15, "QA": 0.85, "Design": 0.95, "Product": 1.0,
        }.get(dept_name, 1.0)
        return max(3, int(random.gauss(base * dept_factor, base * 0.25)))

    def _create_admin(self):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@itcompany.ru", password="admin12345"
            )
            self.stdout.write(self.style.SUCCESS(
                "Создан суперпользователь: admin / admin12345"
            ))
        else:
            self.stdout.write("Суперпользователь admin уже существует.")
