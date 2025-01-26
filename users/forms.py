from dataclasses import field

from django import forms
from django.contrib.auth import validators
from django.contrib.auth.password_validation import validate_password
from django.forms import ModelForm, TextInput

from users.models import User, Client
from utils import delete_null_choice


class ClientRegisterForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput(),
    #                            validators=[validate_password])
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(max_length=20,
                               validators=[validators.UnicodeUsernameValidator()],
                               error_messages={'unique': 'user with that username already exists'})
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'gender']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_coach = False
        if commit:
            user.save()
            client = Client.objects.create(user=user)
            return client


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = delete_null_choice(self.fields['gender'].choices)
        print(type(self.fields['gender'].choices))


class UserEditFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class CoachEditForm(UserEditFrom):
    hourly_rate = forms.DecimalField(max_digits=5, decimal_places=2)
    description = forms.CharField(widget=forms.Textarea)
    phone_number = forms.CharField(widget=forms.TextInput)

