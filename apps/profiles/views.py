from django.shortcuts import render
from django.views import View
# Create your views here.

class DetailView(View):
    def get(self, request):
        return render(request, "profile/detailView.html")
    
class DashboardView(View):
    def get(self, request):
        return render(request, "profile/dashboard.html")
