from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("accounts/", include("accounts.urls")),
    path("results/", include("results.urls")),
]
