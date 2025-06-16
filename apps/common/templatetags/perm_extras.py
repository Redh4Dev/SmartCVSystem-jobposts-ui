# apps/authx/templatetags/perm_extras.py

from django import template
from apps.authx.auth_utils import get_user_permissions

register = template.Library()

@register.simple_tag(takes_context=True)
def has_perm(context, perm_name):
    user_id = context.request.session.get('user_id')
    if not user_id:
        return False
    return perm_name in get_user_permissions(user_id)
