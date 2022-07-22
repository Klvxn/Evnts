from django import forms
from django.utils import timezone

from .models import Event, Comment


# Forms
class AddEventForm(forms.ModelForm):
    date_of_event = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"placeholder": "YYYY-MM-DD / hh-mm-ss"}),
    )

    class Meta:
        model = Event
        exclude = ("user", "slug", "users_attending")

    def clean_date(self):
        date_of_event = self.cleaned_data["date"]
        if date_of_event < timezone.now():
            raise forms.ValidationError(
                "The date you set is in the past. Only future events can be posted."
            )
        return date_of_event


class EditEventForm(forms.ModelForm):
    date_of_event = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"placeholder": "YYYY-MM-DD / hh-mm-ss"}),
    )

    class Meta:
        model = Event
        exclude = ("user", "slug", "users_attending")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("username", "comment")
