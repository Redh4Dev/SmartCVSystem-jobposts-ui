from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts    import render, redirect

from django.contrib      import messages

from django.contrib.auth.hashers import check_password,is_password_usable
from django.shortcuts            import render, redirect


from .forms   import LoginForm, RegisterForm
from .models     import (
    User,
    Role,
    UsersRole,
    Company,
    CompanyUser,
    UserProfile,
)
from pprint import pprint
import logging
logger = logging.getLogger(__name__)
from .services import register_user

class LoginView(View):
    def get(self, request):
        form = LoginForm()
         # If already logged in, go home
        if request.session.get('user_id'):
            return redirect('/dashboard')
        return render(request, "authx/login.html", {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, "authx/login.html", {'form': form})

        uname = form.cleaned_data['username']
        pwd   = form.cleaned_data['password']

        user = User.objects.filter(username=uname).first()
        # If you prefer print(), make sure to format correctly:
        if user:
            print(f"DEBUG: Found user → {user!r}")
            print(f"DEBUG: Stored hash → {user.password!r}")
            print(f"DEBUG: Raw password → {pwd!r}")
            match = check_password(pwd, user.password)
            print(f"DEBUG: check_password(...) → {match!r}")
            logger.debug(
                "Login Debug: user=%r, hash=%r, raw_pwd=%r, match=%s",
                user, user.password, pwd, match
            )
            print((user.password))
            print(is_password_usable(user.password))
            print((check_password(pwd,user.password)))#wrong bcoz arg  position swapped
        else:
            print(f"DEBUG: No user found for username={uname!r}")
            logger.debug("Login Debug: no user for username=%r", uname)

        if not user or not check_password(pwd,user.password):
            messages.error(request, "Invalid username or password.")
            return render(request, "authx/login.html", {'form': form})

        # SUCCESS!  Store your own session keys:
        request.session['user_id']   = user.users_id
        request.session['username']  = user.username
        request.session['first_name']= user.first_name

        messages.success(request, f"Welcome back, {user.first_name}!")
        return redirect(request.GET.get('next') or '/dashboard')

class RegisterView(View):
    def get(self, request):
        form  = RegisterForm()
        roles = Role.objects.all()
        return render(request, "authx/register.html", {
            "form":  form,
            "roles": roles,
        })

    def post(self, request):
        form  = RegisterForm(request.POST)
        roles = Role.objects.all()
        if not form.is_valid():
            return render(request, "authx/register.html", {"form": form, "roles": roles})

        # Prepare data dicts
        cd = form.cleaned_data
        user_data = {
            "first_name": cd["first_name"],
            "last_name":  cd["last_name"],
            "email":      cd["email"],
            "username":   cd["username"],
            "password":   cd["password"],            # raw
            "role_id":    request.POST.get("role"),
        }
        company_data = None
        if user_data["role_id"] and Role.objects.get(pk=user_data["role_id"]).role_name.lower()=="company hr":
            company_data = {
                "name":    request.POST.get("company_name","").strip(),
                "address": request.POST.get("company_address","").strip(),
                "website": request.POST.get("company_website","").strip(),
            }

        try:
            register_user(user_data, company_data)
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            return render(request, "authx/register.html", {"form": form, "roles": roles})

        messages.success(request, "Registration successful! Please check your email.")
        return redirect("authx:login")
    
class LogoutView(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        messages.info(request, "You’ve been logged out.")
        return redirect('authx:login')
    
# class DebugPasswordResetView(PasswordResetView):
#     template_name           = 'authx/password_reset_form.html'
#     email_template_name     = 'emails/password_reset_email.html'
#     subject_template_name   = 'emails/password_reset_subject.txt'
#     success_url             = reverse_lazy('authx:password_reset_done')

#     def form_valid(self, form):
#         email = form.cleaned_data['email']
#         users = list(form.get_users(email))
#         print(f"PasswordReset for %r matched %d users", email, len(users))
#         logger.debug("PasswordReset for %r matched %d users", email, len(users))
#         # now actually send:
#         super().form_valid(form)
#         return super().form_valid(form)