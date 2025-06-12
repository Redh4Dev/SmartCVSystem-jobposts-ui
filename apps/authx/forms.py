# authx/forms.py
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
        label="Password"
    )
 

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

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
