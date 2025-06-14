# authx/forms.py
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Role

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
        label="Password"
    )

    role = forms.ChoiceField(
        label="Account Type",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

 

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # fetch all roles and build choices list
        roles = Role.objects.all()
        self.fields['role'].choices = [
            (r.role_id, r.role_name.capitalize()) for r in roles
        ]

        # default to the “candidate” role if it exists
        candidate = roles.filter(role_name__iexact='Candidate').first()
        if candidate:
            self.fields['role'].initial = candidate.role_id

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # you could add extra password validation here
        return make_password(pwd)
    
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),
        label="Password"
    )
