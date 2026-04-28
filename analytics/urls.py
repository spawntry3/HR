from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("employees/", views.employees_list, name="employees"),
    path("vacancies/", views.vacancies_list, name="vacancies"),
    path("salaries/", views.salaries_page, name="salaries"),
    path("turnover/", views.turnover_page, name="turnover"),
    path("api/charts/", views.api_charts, name="api_charts"),
]
