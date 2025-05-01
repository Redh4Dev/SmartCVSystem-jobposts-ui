from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class LoginView(View):
    def get(self, request):
        return render(request, "authx/login.html")

class RegisterView(View):
    def get(self, request):
        return render(request, "authx/register.html")
class LogoutView(LoginRequiredMixin, View):
    """
    Logs out on GET and redirects to the login page.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("authx:login")
