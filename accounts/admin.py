from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserEditForm
    model = CustomUser
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "image",
                    "first_name",
                    "last_name",
                    "email",
                    "gender",
                    "date_of_birth",
                )
            },
        ),
        ("Status", {"fields": ("is_superuser", "is_staff", "is_active")}),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "gender",
        "is_staff",
        "date_of_birth",
    )
    list_filter = ("is_staff", "is_superuser")


admin.site.register(CustomUser, CustomUserAdmin)
