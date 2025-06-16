
from django.shortcuts   import redirect
from django.urls        import reverse
from django.conf        import settings
from django.utils.deprecation import MiddlewareMixin
from .auth_utils        import get_user_permissions

# stackoverflow code
class PermissionRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            # pull off required_permission as before
            perm = getattr(view_func, 'required_permission', None)
            if perm is None and hasattr(view_func, 'view_class'):
                perm = getattr(view_func.view_class, 'required_permission', None)

            if not perm:
                return None  # no permission required

            user_id = request.session.get('user_id')
            if not user_id:
                return redirect(settings.LOGIN_URL)

            user_perms = get_user_permissions(user_id)
            if perm not in user_perms:
                return redirect(reverse('profiles:dashboard'))

            return None
        except Exception as e:
            # log it so you can see in the console
            import traceback; traceback.print_exc()
            # optionally re-raise to get the full DEBUG page
            raise
