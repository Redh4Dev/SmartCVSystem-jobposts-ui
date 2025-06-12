# apps/profiles/forms.py
from django import forms
from .models import ResumeFile

class ProfileForm(forms.Form):
    phone           = forms.CharField(max_length=20,   required=False)
    location        = forms.CharField(max_length=100,  required=False)
    avatar          = forms.ImageField(required=False)

    # company fields for recruiters or HRs
    company_name    = forms.CharField(max_length=200,  required=False)
    company_address = forms.CharField(widget=forms.Textarea, required=False)
    company_website = forms.URLField(required=False)
class ResumeForm(forms.ModelForm):
    """
    Form for uploading a new resume file.
    """
    class Meta:
        model = ResumeFile
        # FilePath maps to your file upload field
        fields = ['FilePath']
        labels = {
            'FilePath': 'Choose Resume File',
        }
        widgets = {
            'FilePath': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_FilePath(self):
        file = self.cleaned_data.get('FilePath')
        if file:
            # Optionally enforce file type/size here
            if not file.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError('Only PDF or Word documents are allowed.')
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5 MB.')
        return file

