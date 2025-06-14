from django.shortcuts import render
from ..authx.auth_utils import SessionRequiredMixin
from ..authx.models     import User, UsersRole
from django.views       import View
from apps.jobposts.models import JobPost, UserJob
from apps.profiles.models import ResumeFile
from django.utils import timezone
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
        
        # flatten list of role names
        roles = [ur.role.role_name.lower() for ur in UsersRole.objects.filter(user_id=user_id).select_related('role')]

        context = {
            'user':  user,
            'roles': roles,
        }

        if 'candidate' in roles:
            # Candidate metrics
            resumes_qs     = ResumeFile.objects.filter(UserID_id=user_id)
            context.update({
                'resume_count':  resumes_qs.count(),
                'has_active':    resumes_qs.filter(IsSelected=True).exists(),
                'applied_count': UserJob.objects.filter(User_id=user_id, IsApplied=True).count(),
                'saved_count':   UserJob.objects.filter(User_id=user_id, IsSaved=True).count(),
            })

        if 'company_hr' in roles or 'recruiter' in roles:
            # Company HR / Recruiter metrics
            context.update({
                'total_jobs':   JobPost.objects.filter(Recruiter_id=user_id).count(),
                'expired_jobs': JobPost.objects.filter(
                    Recruiter_id=user_id,
                    ApplicationDeadline__lt=timezone.now()
                ).count(),
                'total_apps':   UserJob.objects.filter(
                    JobPost__Recruiter_id=user_id,
                    IsApplied=True
                ).count(),
            })

        return render(request, 'common/dashboard.html', context)