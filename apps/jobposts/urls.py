from django.urls import path,include
from .views      import (
    JobPostListView,
    JobPostCreateView,
    JobPostUpdateView,
    JobPostApplicantsView,
    JobPostCandidateJobSearchView,
)
app_name = 'jobposts'

urlpatterns = [
    # LIST & CREATE are all static → keep them first
    path('',      JobPostListView.as_view(),   name='list'),
    path('new/',  JobPostCreateView.as_view(), name='create'),

    # SEARCH is also a static literal → must go before any '<int:pk>' patterns
    path('search/', JobPostCandidateJobSearchView.as_view(), name='search'),

    # now your dynamic patterns
    path('<int:pk>/edit/',       JobPostUpdateView.as_view(),     name='edit'),
    path('<int:pk>/applicants/', JobPostApplicantsView.as_view(), name='applicants'),
]