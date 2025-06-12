import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    """
    Given a FileField’s name (e.g. "resumes/2025/06/12/foo.pdf"),
    returns just "foo.pdf".
    """
    return os.path.basename(value)
