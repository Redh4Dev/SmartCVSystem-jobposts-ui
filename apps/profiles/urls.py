from django.urls import path
from .views import  DetailView
app_name = "profiles"

urlpatterns = [
    path("detail/", DetailView.as_view(), name="detail"),
]