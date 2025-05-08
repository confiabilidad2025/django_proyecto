# authentication/forms.py
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput()
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        return f"{username}@miteleferico.bo"