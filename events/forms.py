from django import forms
from django.utils import timezone

from .models import EventList, Event, Comment


# Forms
class AddEventListForm(forms.ModelForm):
    class Meta:
        model = EventList
        fields = ("name",)


class AddEventForm(forms.ModelForm):
    date = forms.DateTimeField(
        label="Date & Time",
        widget=forms.DateTimeInput(attrs={"placeholder": "YYYY-MM-DD / hh-mm-ss"}),
    )

    class Meta:
        model = Event
        exclude = ("user", "slug")

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < timezone.now():
            raise forms.ValidationError(
                "The date you set is in the past. Only future events can be posted."
            )
        return date


class EditEventForm(forms.ModelForm):
    date = forms.DateTimeField(
        label="Date & Time",
        widget=forms.DateTimeInput(attrs={"placeholder": "YYYY-MM-DD / hh-mm-ss"}),
    )

    class Meta:
        model = Event
        exclude = ("user", "slug")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("username", "comment")
