from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    DeleteUserAccount,
    PasswordChange,
    PasswordChangeDone,
    RegisterUser,
    UserProfile,
    UserEditProfile,
)


app_name = "accounts"

urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("<slug:username>/profile/", UserProfile.as_view(), name="user-profile"),
    path("<slug:username>/edit-profile/", UserEditProfile.as_view(), name="edit-profile"),
    path("<slug:username>/delete-account/", DeleteUserAccount.as_view(), name="delete-account"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", PasswordChange.as_view(), name="password_change"),
    path("password-change-done/", PasswordChangeDone.as_view(), name="password_change_done"),
]
