from django.urls import path
from .views import  *
app_name = "profiles"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("detail/", DetailView.as_view(), name="detail"),
]