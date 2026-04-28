# HR-аналитика IT-компании

Демо-проект на **Django 6** с админ-панелью и интерактивным дашбордом
по ключевым HR-метрикам IT-компании:

- **Текучесть кадров** (turnover rate, динамика найма/увольнений, причины)
- **Зарплаты по грейдам и стекам** (мин/средняя/макс, гистограмма распределения)
- **Время закрытия вакансий** (по отделам и грейдам)
- **Численность по отделам**, **популярность технологий**, **статусы вакансий**

Аналитика на чистом Django ORM (агрегации в БД), визуализация — Chart.js.
Админ-панель — стандартный `django.contrib.admin` с расширенными списками,
фильтрами, цветовыми бейджами и аннотациями.

---

## Стек

- Python 3.10+
- Django 6.0
- SQLite (по умолчанию) — можно заменить на PostgreSQL в `settings.py`
- Chart.js 4 (с CDN)

## Установка и запуск

```bash
# 1. Создать и активировать виртуальное окружение (опционально, рекомендуется)
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить миграции
python manage.py migrate

# 4. Заполнить демо-данными и создать суперпользователя
python manage.py seed_demo --employees 200 --vacancies 80 --admin

# 5. Запустить сервер
python manage.py runserver
```

После запуска открой:

- Дашборд: http://127.0.0.1:8000/
- Админ-панель: http://127.0.0.1:8000/admin/ (логин `admin`, пароль `admin12345`)

## Структура проекта

```
HR-admin-panel/
├── manage.py
├── requirements.txt
├── hr_project/                # Конфигурация Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
└── analytics/                 # Основное приложение
    ├── models.py              # Department, TechStack, Grade, Employee, Vacancy
    ├── admin.py               # Админ-панель с аннотациями и бейджами
    ├── analytics_service.py   # Бизнес-логика метрик (агрегации в БД)
    ├── views.py               # Дашборд + JSON API для графиков
    ├── urls.py
    ├── management/commands/
    │   └── seed_demo.py       # Генератор демо-данных
    ├── templates/
    │   ├── base.html
    │   └── dashboard.html
    └── static/
        ├── css/dashboard.css
        └── js/dashboard.js
```

## Модель данных

| Модель        | Назначение                                                         |
|---------------|--------------------------------------------------------------------|
| `Department`  | Отдел (Backend, Frontend, QA, Data & ML и т. д.)                   |
| `TechStack`   | Технология/стек (Python, React, Kubernetes…) с категорией          |
| `Grade`       | Грейд (Intern → Principal)                                         |
| `Employee`    | Сотрудник: ФИО, отдел, грейд, стеки, ЗП, дата найма/увольнения     |
| `Vacancy`     | Вакансия: статус, даты открытия/закрытия, требуемый грейд и стек    |

## Метрики на дашборде

| Метрика                                  | Расчёт                                                              |
|------------------------------------------|---------------------------------------------------------------------|
| Текучесть (turnover, %)                  | увольнения за период / средняя численность × 100%                   |
| Найм vs увольнения                       | агрегация по `TruncMonth(hire_date / termination_date)`             |
| Причины увольнений                       | `GROUP BY termination_reason`                                       |
| Зарплаты по грейдам                      | `Avg/Min/Max(salary)` среди активных сотрудников                    |
| Зарплаты по стекам                       | `Avg(salary)` через M2M `Employee.tech_stacks`                       |
| Время закрытия вакансий                  | `closed_at − opened_at`, среднее по отделам и грейдам               |
| ФОТ                                      | `Sum(salary)` среди активных сотрудников                            |

## Полезные команды

```bash
# Полный сброс и пересоздание демо-данных
python manage.py seed_demo --reset --employees 300 --vacancies 120 --admin

# Создать суперпользователя вручную
python manage.py createsuperuser

# Проверить корректность настроек
python manage.py check
```

