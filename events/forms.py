from django import forms
from django.utils import timezone

from .models import EventList, Event, Comment


# Forms
class AddEventListForm(forms.ModelForm):
    class Meta:
        model = EventList
        fields = ("name",)


class AddEventForm(forms.ModelForm):
    date_of_event = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"placeholder": "YYYY-MM-DD / hh-mm-ss"}),
    )

    class Meta:
        model = Event
        exclude = ("user", "slug")

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
        exclude = ("user", "slug")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("username", "comment")
