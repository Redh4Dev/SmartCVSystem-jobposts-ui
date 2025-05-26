from django.shortcuts import render

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

def dashboard(request):
    return render(request,"dashboard.html")