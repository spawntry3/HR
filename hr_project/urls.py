from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "HR-аналитика IT-компании"
admin.site.site_title = "HR Admin"
admin.site.index_title = "Управление HR-данными"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("analytics.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
]
