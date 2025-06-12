from django.urls import path,include
from .views      import CandidateJobSearchView,JobPostApplicantsView,JobPostListView, JobPostCreateView,JobPostUpdateView
app_name = 'jobposts'

urlpatterns = [
    path('',               JobPostListView.as_view(),   name='list'),
    path('new/',           JobPostCreateView.as_view(), name='create'),
     path('<int:pk>/edit/', JobPostUpdateView.as_view(),   name='edit'),# you can add detail/edit/delete routes here later…
    path('<int:pk>/applicants/',
         JobPostApplicantsView.as_view(),
         name='applicants'),
      path(
        'search/',
        CandidateJobSearchView.as_view(),
        name='search'
    ),
]