from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


# Forms
class CustomUserCreationForm(UserCreationForm):

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
