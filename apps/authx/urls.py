from django.urls import path
from .views import RegisterView, LoginView,LogoutView
from django.contrib.auth import views as auth_views
from django.urls           import path, reverse_lazy
app_name = "authx"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",    LoginView.as_view(),    name="login"),
    path("logout/",  LogoutView.as_view(),   name="logout"),

  # 1) The form to ask for an email:
    path(
      'password_reset/',
      auth_views.PasswordResetView.as_view(
        template_name='authx/password_reset_form.html',
        email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
        # <— override the default reverse('password_reset_done') to your namespaced name
        success_url=reverse_lazy('authx:password_reset_done'),
      ),
      name='password_reset'
    ),

    # 2) Where we land after POSTing that form:
    path(
      'password_reset/done/',
      auth_views.PasswordResetDoneView.as_view(
        template_name='authx/password_reset_done.html'
      ),
      name='password_reset_done'
    ),

    # 3) The link the user clicks in their email:
      path(
      'reset/<uidb64>/<token>/',
      auth_views.PasswordResetConfirmView.as_view(
        template_name='authx/password_reset_confirm.html',
        success_url=reverse_lazy('authx:password_reset_complete'),
      ),
      name='password_reset_confirm'
    ),

    # 4) Final “your password’s changed” page:
    path(
      'reset/done/',
      auth_views.PasswordResetCompleteView.as_view(
        template_name='authx/password_reset_complete.html'
      ),
      name='password_reset_complete'
    ),

      # 1) The form to let a logged-in user change their password:
 
]