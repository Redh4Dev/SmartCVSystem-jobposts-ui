from functools import wraps
from django.shortcuts import redirect
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import UsersRole, RolePermission

def login_required_custom(view_func):
    """
    Decorator for function-based views that checks for a custom session key 'user_id'.
    Redirects to LOGIN_URL with ?next=original_path if user not in session.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('user_id'):
            login_url = settings.LOGIN_URL or 'authx:login'
            return redirect(f"{login_url}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped


class SessionRequiredMixin:
    """
    Mixin for class-based views to enforce custom session-based login.
    Usage: inherit before View in the MRO.
    """
    @method_decorator(login_required_custom)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

def get_user_permissions(user_id):

    role_ids = UsersRole.objects.filter(user_id=user_id).values_list('role_id', flat=True)
    print(role_ids)
    perms = RolePermission.objects.filter(role_id__in=role_ids)\
                                  .select_related('permission')\
                                  .values_list('permission__permission_name', flat=True)
    return set(perms)

