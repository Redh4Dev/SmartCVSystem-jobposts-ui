from django.shortcuts import render
from ..authx.auth_utils import SessionRequiredMixin
from ..authx.models     import User, UsersRole
from django.views       import View
# Create your views here.
def landing(request):
    """
    Public landing page for SmartCVSystem.
    """
    context = {
        "site_name": "SmartCVSystem",
        "tagline": "Intelligent resume parsing & candidate matching",
        "features": [
            "Automatic resume parsing",
            "Role-based matching scores",
            "Secure S3-backed storage",
            "Admin dashboards & reports",
        ],
    }
    return render(request, "landing.html", context)

class DashboardView(SessionRequiredMixin, View):
    """
    Shows the logged-in user’s info and roles.
    """
    def get(self, request):
        user_id = request.session['user_id']
        user    = User.objects.get(users_id=user_id)

        # Fetch all Roles assigned to this user
        role_links = UsersRole.objects.filter(user_id=user_id).select_related('role')
        roles      = [rl.role for rl in role_links]

        return render(request, 'dashboard.html', {
            'user':  user,
            'roles': roles,
        })