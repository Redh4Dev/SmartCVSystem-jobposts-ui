from django.views.generic import CreateView,DetailView
from django.urls           import reverse_lazy
from django.contrib        import messages

from apps.authx.auth_utils import SessionRequiredMixin

from .forms                import JobPostForm
from django.views.generic import ListView, CreateView, UpdateView
from .models               import JobPost, UserJob
from ..profiles.models import ResumeFile
from django.db.models      import Count, Q
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class JobPostDetailView(SessionRequiredMixin, DetailView):
    """
    Shows full details of a single job, and handles apply/save POSTs.
    """
    model               = JobPost
    template_name       = 'jobposts/detail.html'
    context_object_name = 'job'

    def post(self, request, *args, **kwargs):
        # handle apply/save from the detail page
        action = request.POST.get('action')
        job_id = self.get_object().JobPostID
        uid    = request.session['user_id']

        if action == 'apply':
            has_resume = ResumeFile.objects.filter(
                UserID_id=uid,
                IsSelected=True
            ).exists()

            if not has_resume:
                messages.warning(
                    request,
                    "Please upload and select one of your resumes before applying."
                )
                return redirect(f"{request.path}?q={request.POST.get('q','')}")
            
    
        uj, created = UserJob.objects.get_or_create(
            User_id=uid,
            JobPost_id=job_id,
            defaults={'CreatedAt': timezone.now()}
        )

        
        if action == 'apply':
            uj.IsApplied = True
            uj.IsSaved   = False
            uj.save()
            messages.success(request, "You’ve applied for this job.")
        elif action == 'save':
            uj.IsSaved   = True
            uj.IsApplied = False
            uj.save()
            messages.success(request, "Job saved for later.")

        
        return redirect('jobposts:detail', pk=job_id)
class SavedJobsView(SessionRequiredMixin, ListView):
    """
    Lists all JobPosts that the current user has saved for later.
    """
    model               = UserJob
    template_name       = 'jobposts/saved_jobs.html'
    context_object_name = 'saved_apps'

    def get_queryset(self):
        user_id = self.request.session['user_id']
        return (
            UserJob.objects
                   .filter(User_id=user_id, IsSaved=True)
                   .select_related('JobPost')
                   .order_by('-CreatedAt')
        )
    
class MyApplicationsView(SessionRequiredMixin, ListView):
    model               = UserJob
    template_name       = 'jobposts/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        user_id = self.request.session['user_id']
        return (
            UserJob.objects
                   .filter(User_id=user_id, IsApplied=True)
                   .select_related('JobPost')
                   .order_by('-CreatedAt')
        )

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        # you might want to pass roles/user info too
        return ctx
class JobPostApplicantsView(SessionRequiredMixin, ListView):
    """
    Lists all users who have applied to a given JobPost.
    """
    model                 = UserJob
    template_name         = 'jobposts/applicants.html'
    context_object_name   = 'applications'

    def get_queryset(self):
        job_id = self.kwargs['pk']
        # only those who actually applied
        return (
            UserJob.objects
                   .filter(JobPost_id=job_id, IsApplied=True)
                   .select_related('User')  # bring in the User
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # fetch job to display its title in the template
        ctx['job'] = JobPost.objects.get(pk=self.kwargs['pk'])
        return ctx
    
class JobPostListView(SessionRequiredMixin, ListView):
    model               = JobPost
    template_name       = 'jobposts/list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return (
            JobPost.objects
                   .filter(Recruiter_id=self.request.session['user_id'])
                   .annotate(
                       num_applications=Count(
                           'applicants',
                           filter=Q(applicants__IsApplied=True)
                       )
                   )
        )
    
class JobPostCreateView(SessionRequiredMixin, CreateView):
    model         = JobPost
    form_class    = JobPostForm
    template_name = 'jobposts/create.html'
    success_url   = reverse_lazy('jobposts:list')

    def form_valid(self, form):
        form.instance.Recruiter_id = self.request.session['user_id']
        messages.success(self.request, "Job post created successfully.")
        return super().form_valid(form)

class JobPostUpdateView(SessionRequiredMixin, UpdateView):
    model         = JobPost
    form_class    = JobPostForm
    template_name = 'jobposts/edit.html'
    pk_url_kwarg  = 'pk'
    success_url   = reverse_lazy('jobposts:list')

    def get_queryset(self):
        return JobPost.objects.filter(Recruiter_id=self.request.session['user_id'])

    def form_valid(self, form):
        messages.success(self.request, "Job post updated successfully.")
        return super().form_valid(form)
    

class JobPostCandidateJobSearchView(SessionRequiredMixin, View):
    """
    Let candidates search available jobs, apply or save them.
    """
    template_name = 'jobposts/search.html'

    def get(self, request):
        print("sdsd")
        q = request.GET.get('q', '').strip()
        page = request.GET.get('page', 1)
        # base queryset: active jobs
        qs = JobPost.objects.filter(IsActive=True)
        if q:
            qs = qs.filter(
                Q(Title__icontains=q) |
                Q(Description__icontains=q)
            )

        # paginate at 10 jobs per page
        paginator = Paginator(qs.order_by('-CreatedAt'), 10)
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)
                                  
        # gather user’s existing UserJob records
        uid = request.session['user_id']
        uj_qs = UserJob.objects.filter(User_id=uid)
        status_map = {uj.JobPost_id: uj for uj in uj_qs}
        print(self.template_name)
        return render(request, 'jobposts/search.html', {
            'jobs': qs.order_by('-CreatedAt'),
            'status_map': status_map,
            'query': q,
            'paginator':  paginator,
        })

    def post(self, request):
        action = request.POST.get('action')
        job_id = int(request.POST.get('job_id'))
        uid    = request.session['user_id']

        if action == 'apply':
            has_resume = ResumeFile.objects.filter(
                UserID_id=uid,
                IsSelected=True
            ).exists()

            if not has_resume:
                messages.warning(
                    request,
                    "Please upload and select one of your resumes before applying."
                )
                return redirect(f"{request.path}?q={request.POST.get('q','')}")
            
        uj, created = UserJob.objects.get_or_create(
            User_id=uid, JobPost_id=job_id,
            defaults={'CreatedAt': timezone.now()}
        )
    
        if action == 'apply':
            uj.IsApplied = True
            uj.IsSaved   = False
            #uj.Status    = 'Applied'
            uj.DeletedAt = None
            uj.soft_delete = False
            uj.save()
            messages.success(request, "You have applied for this job.")
        elif action == 'save':
            uj.IsSaved = True
            uj.IsApplied = False
            uj.Status = 'Saved'
            uj.save()
            messages.success(request, "Job saved for later.")
        else:
            messages.error(request, "Unknown action.")

        return redirect(f"{request.path}?q={request.POST.get('q','')}")


    model               = UserJob
    template_name       = 'jobposts/applicants.html'
    context_object_name = 'applications'

    def get_queryset(self):
        job_id = self.kwargs['pk']
        return (
            UserJob.objects
                   .filter(JobPost_id=job_id, IsApplied=True)
                   .select_related('User')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['job'] = JobPost.objects.get(pk=self.kwargs['pk'])
        return ctx