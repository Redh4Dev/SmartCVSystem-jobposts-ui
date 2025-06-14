from django.conf import settings
from django.urls  import reverse
def site_name(request):
    return {
        "site_name": getattr(settings, "SITE_NAME", "My Site")
    }

def sidebar_menu(request):
    roles = request.session.get('roles', [])
    raw    = settings.SIDEBAR_MENU
    menu   = []
    for role in roles:
        for entry in raw.get(role, []):
            menu.append({
                'label': entry['label'],
                'url':   reverse(entry['url_name']),
            })
    return { 'sidebar_menu': menu }