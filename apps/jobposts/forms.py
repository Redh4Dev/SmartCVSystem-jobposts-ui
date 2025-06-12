# apps/jobposts/forms.py
from django import forms
from .models import JobPost

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = [
            'Title', 'Description', 'RequiredSkills', 'Location',
            'EmploymentType', 'MinSalary', 'MaxSalary', 'RemoteOption',
            'Industry', 'ExperienceLevel', 'EducationLevel',
            'ApplicationDeadline', 'Benefits', 'IsActive',
        ]
        widgets = {
            'Description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Use Markdown'}),
            'RequiredSkills': forms.Textarea(attrs={'rows': 2, 'placeholder': '- Python- Django'}),
            'Benefits': forms.Textarea(attrs={'rows': 3}),
            'ApplicationDeadline': forms.DateInput(attrs={'type': 'date'}),
        }
