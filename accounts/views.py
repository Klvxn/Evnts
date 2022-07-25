from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeDoneView,  PasswordChangeView
from django.urls import reverse_lazy

from events.models import Event

from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser


# Create your views here.
def get_user(username: str) -> CustomUser:
    user = get_object_or_404(CustomUser, username=username)
    return user


class RegisterUser(View):

    form_class = CustomUserCreationForm
    template_name: str = "register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account creation was successful.")
            return redirect("events:home")
        else:
            messages.error(
                request, "Error creating account. Check and resubmit the form."
            )
        context = {"form": form}
        return render(request, self.template_name, context)


class UserProfile(View):

    template_name: str = "user_profile.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        user = get_user(username)
        posted_events = Event.objects.filter(user=user)
        context = {"user": user, "user_events": posted_events}
        return render(request, self.template_name, context)


class UserEditProfile(LoginRequiredMixin, View):

    form_class = CustomUserEditForm
    template_name: str = "edit_profile.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        user = get_user(username)
        if request.user == user:
            form = self.form_class(instance=user)
        else:
            return HttpResponseForbidden()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        user = get_user(username)
        if request.user == user:
            form = self.form_class(
                instance=user, data=request.POST, files=request.FILES
            )
            if form.is_valid():
                form.save()
                messages.success(request, "Profile was updated successfully.")
                return redirect(user.get_absolute_url())
            else:
                messages.error(request, "Error updating your profile.")
        else:
            return HttpResponseForbidden()
        context = {"form": form}
        return render(request, self.template_name, context)


class DeleteUserAccount(LoginRequiredMixin, View):

    template_name: str = "delete_account.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        user = get_user(username)
        if request.user == user:
            context = {"user": user}
            return render(request, self.template_name, context)
        else:
            return HttpResponseForbidden()

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        user = get_user(username)
        if request.user.is_superuser or request.user == user:
            user.delete()
            return redirect("events:home")
        else:
            return HttpResponseForbidden()


class PasswordChange(PasswordChangeView):

    template_name: str = "password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class PasswordChangeDone(PasswordChangeDoneView):

    template_name: str = "password_change_done.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        messages.success(request, "Your password has been changed successfully.")
        return render(request, self.template_name)
