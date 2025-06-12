from django.urls import path
from .views import  *
app_name = "profiles"

urlpatterns = [
    #path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path('dashboard/',DashboardView.as_view(), name='dashboard'),
    path('detail',DetailView.as_view(), name='detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('resumes/', ManageResumesView.as_view(), name='resume'),
]