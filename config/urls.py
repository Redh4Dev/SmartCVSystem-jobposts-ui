"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from apps.common.views import landing,DashboardView
import debug_toolbar
from django.http    import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def dummy(request):
    return HttpResponse("🚧 Placeholder — coming soon!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("apps.authx.urls", namespace="authx")),

    path("", landing, name="landing"),

    path("", include("apps.profiles.urls", namespace="profiles")),

    path("jobs/", include('apps.jobposts.urls', namespace='jobposts')),


        # ——— Dummy recruiter URLs ———
    path('recruiter/', include(([
        path('job_list/',    dummy, name='job_list'),

    ], 'recruiter'), namespace='recruiter')),

    # ——— Dummy candidate URLs ———
    path('candidate/', include(([
        path('my_applications/', dummy, name='my_applications'),
    ], 'candidate'), namespace='candidate')),

    # ——— Dummy company URLs ———
    path('company/', include(([
        path('overview/', dummy, name='overview'),
        path('onboard/',  dummy, name='onboard'),
    ], 'company'), namespace='company')),

    path("debug/", include(debug_toolbar.urls)),

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )