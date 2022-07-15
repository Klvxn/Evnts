from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


# Forms
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        min_length=3, 
        required=True, 
        widget=forms.TextInput(),
    )
    password1 = forms.CharField(
        label="Password",
        min_length=8, 
        required=True, 
        widget=forms.PasswordInput(),
        help_text="Password should be unique and contain at least 8 characters"
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "image",
            "username",
            "email",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
        )


class CustomUserEditForm(UserChangeForm):
    
    class Meta:
        model = CustomUser
        fields = (
            "image",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
        )
