from django.views.generic import CreateView
from django.urls           import reverse_lazy
from django.contrib        import messages

from apps.authx.auth_utils import SessionRequiredMixin
from .models               import JobPost
from .forms                import JobPostForm
from django.views.generic import ListView, CreateView, UpdateView
from .models               import JobPost, UserJob
from django.db.models      import Count, Q
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View

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
class CandidateJobSearchView(SessionRequiredMixin, View):
    """
    Let candidates search available jobs, apply or save them.
    """
    template_name = 'jobposts/search.html'

    def get(self, request):
        q = request.GET.get('q', '').strip()
        # base queryset: active jobs
        qs = JobPost.objects.filter(IsActive=True)
        if q:
            qs = qs.filter(
                Q(Title__icontains=q) |
                Q(Description__icontains=q)
            )
        # gather user’s existing UserJob records
        uid = request.session['user_id']
        uj_qs = UserJob.objects.filter(User_id=uid)
        status_map = {uj.JobPost_id: uj for uj in uj_qs}

        return render(request, self.template_name, {
            'jobs': qs.order_by('-CreatedAt'),
            'status_map': status_map,
            'query': q,
        })

    def post(self, request):
        action = request.POST.get('action')
        job_id = int(request.POST.get('job_id'))
        uid    = request.session['user_id']

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