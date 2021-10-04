from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import AppUser


class UserCreationForm(forms.ModelForm):
    """
    Form with the required fields to
    create a user on the basis of the AppUser model
    """
    password_1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput
    )

    class Meta:
        model = AppUser
        fields = ('email', 'username', 'first_name', 'last_name',)

    def clean_password2(self):
        password_1 = self.cleaned_data.get('password_1')
        password_2 = self.cleaned_data.get('password_2')
        if (password_1 and password_2) and password_1 != password_2:
            raise ValidationError("Passwords don't match")
        return password_2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password_1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AppUser
        fields = ('email', 'password', 'username', 'first_name',
                  'last_name', 'is_active', 'is_admin', 'is_staff')

    def clean_password(self):
        return self.initial['password']
