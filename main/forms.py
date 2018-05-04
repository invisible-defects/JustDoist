from django import forms
from main.models import JustdoistUser

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = JustdoistUser
        fields = ('username', 'first_name', 'last_name', 'password')
