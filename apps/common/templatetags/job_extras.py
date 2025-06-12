# apps/jobposts/templatetags/job_extras.py
import os
from django import template

register = template.Library()

@register.filter
def get_item(dict_obj, key):
    return dict_obj.get(key)

@register.filter
def selected_resume(user):
    """
    Returns the ResumeFile instance that has IsSelected=True for this user, or None.
    """
    return user.resumes.filter(IsSelected=True).first()

@register.filter
def filename(path):
    """
    Given a FileField path, returns only the basename.
    """
    return os.path.basename(path)
