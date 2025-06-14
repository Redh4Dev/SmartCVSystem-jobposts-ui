from django.shortcuts           import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from apps.authx.auth_utils      import login_required_custom
from ..authx.auth_utils import SessionRequiredMixin
from ..authx.models     import User, UsersRole
from django.contrib.auth.hashers import check_password, make_password
from django.contrib             import messages
from apps.authx.auth_utils import SessionRequiredMixin
from django.contrib.auth.forms          import PasswordChangeForm
from apps.authx.models    import UserProfile
from .forms               import ProfileForm
from apps.authx.models          import (
    User, UsersRole, UserProfile,
    Company, CompanyUser
)
from .forms import ResumeForm
from .models import ResumeFile
from apps.jobposts.models import JobPost, UserJob
from django.utils import timezone

class DetailView(View):
    def get(self, request):
        return render(request, "profile/detailView.html")
class ManageResumesView(SessionRequiredMixin,View):

    def get(self, request):
        user_id = request.session['user_id']
        resume_form = ResumeForm()
        resumes     = ResumeFile.objects.filter(UserID=user_id).order_by('-UploadedAt')
        return render(request, 'profile/resume.html', {
            'resume_form': resume_form,
            'resumes': resumes,
        })

    def post(self, request):
        user_id = request.session['user_id']
        action  = request.POST.get('action')

        if action == 'upload':
            form = ResumeForm(request.POST, request.FILES)
            if form.is_valid():
                rf = form.save(commit=False)
                rf.UserID_id = user_id 
                rf.Status = 'Uploaded'
                rf.save()
                messages.success(request, "Resume uploaded.")
            else:
                 return render(request, 'profile/resume.html', {
                    'resume_form': form
                })
        elif action == 'select':
            sel_id = request.POST.get('selected_id')
            # clear previous
            ResumeFile.objects.filter(UserID=user_id, IsSelected=True).update(IsSelected=False)
            # mark new
            ResumeFile.objects.filter(pk=sel_id, UserID=user_id).update(IsSelected=True)
            messages.success(request, "Selected resume updated.")
        return redirect('profiles:resume')
class DashboardView(SessionRequiredMixin, View):
    """
    Shows the logged-in user’s info and roles.
    """
    def get(self, request):
        user_id = request.session['user_id']
        user    = User.objects.get(users_id=user_id)

        # Fetch all Roles assigned to this user
        roles = [ur.role.role_name.lower() for ur in UsersRole.objects.filter(user_id=user_id).select_related('role')]

        context = {
            'user':  user,
            'roles': roles,
        }
        print(roles)
        if 'candidate' in roles:
            # Candidate metrics
            resumes_qs     = ResumeFile.objects.filter(UserID_id=user_id)
            context.update({
                'resume_count':  resumes_qs.count(),
                'has_active':    resumes_qs.filter(IsSelected=True).exists(),
                'applied_count': UserJob.objects.filter(User_id=user_id, IsApplied=True).count(),
                'saved_count':   UserJob.objects.filter(User_id=user_id, IsSaved=True).count(),
            })

        if 'company hr' in roles or 'recruiter' in roles:
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
        print(context)
        return render(request, 'dashboard.html', context)

class ChangePasswordView(SessionRequiredMixin,View):
    def get(self, request):
        user = User.objects.get(users_id=request.session['user_id'])
        form = PasswordChangeForm(user=user)
        return render(request, 'profile/password_change_form.html', {'form': form})

    def post(self, request):
        user = User.objects.get(users_id=request.session['user_id'])
        form = PasswordChangeForm(user=user, data=request.POST)

        if not form.is_valid():
            # errors will show in the template
            return render(request, 'profile/password_change_form.html', {'form': form})

        # This will hash and save the new password for us:
        form.save()
        messages.success(request, "Your password has been updated.")
        return redirect('profiles:dashboard')

class ProfileEditView(SessionRequiredMixin,View):
    def get(self, request):
        user_id = request.session['user_id']
        # load user & profile
        profile = UserProfile.objects.get(user_id=user_id)
        # detect company role
        role_names = UsersRole.objects.filter(user_id=user_id) \
                                     .values_list('role__role_name', flat=True)
        print(role_names)
        print(role_names)
        has_company_role = any(r.lower() in ('company hr','recruiter') for r in role_names)
        print(has_company_role)
        # load or init company
        company = None
        if has_company_role:
            cu = CompanyUser.objects.filter(user_id=user_id).first()
            if cu:
                company = cu.company
            else:
                company = None
        print(company)
        # build initial data
        initial = {
            'phone':    profile.phone,
            'location': profile.location,
        }
        if company:
            initial.update({
                'company_name':    company.name,
                'company_address': company.address,
                'company_website': company.website,
            })

        form = ProfileForm(initial=initial)
        return render(request, 'profile/profile_edit.html', {
            'form':             form,
            'profile':          profile,
            'has_company_role': has_company_role,
        })

    def post(self, request):
        user_id = request.session['user_id']
        profile = UserProfile.objects.get(user_id=user_id)

        # detect company role same as above
        role_names = UsersRole.objects.filter(user_id=user_id) \
                                     .values_list('role__role_name', flat=True)
        has_company_role = any(r.lower() in ('company hr','recruiter') for r in role_names)

        form = ProfileForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'profile/profile_edit.html', {
                'form':             form,
                'profile':          profile,
                'has_company_role': has_company_role,
            })

        # save profile fields
        profile.phone    = form.cleaned_data['phone']
        profile.location = form.cleaned_data['location']
        avatar = form.cleaned_data.get('avatar')
        if avatar:
            profile.avatar = avatar
        profile.save()

        # save company if needed
        if has_company_role:
            # find or create company & link
            cu = CompanyUser.objects.filter(user_id=user_id).first()
            if cu:
                company = cu.company
            else:
                company = Company.objects.create(
                    name    = form.cleaned_data['company_name'],
                    address = form.cleaned_data['company_address'],
                    website = form.cleaned_data['company_website'],
                )
                CompanyUser.objects.create(
                    user_id    = user_id,
                    company_id = company.id,
                )

            # update existing company
            company.name    = form.cleaned_data['company_name']
            company.address = form.cleaned_data['company_address']
            company.website = form.cleaned_data['company_website']
            company.save()

        messages.success(request, "Your profile has been updated.")
        return redirect('profiles:profile_edit')
