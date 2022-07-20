from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.views import View
from pydantic import PostgresDsn

from taggit.models import Tag

from .forms import AddEventForm, CommentForm, EditEventForm
from .models import Category, Event, Comment


# Create your views here.
def get_event(slug: str) -> Event:
    queryset = get_object_or_404(Event, slug=slug, make_private=False)
    return queryset

def get_private_event(slug: str) -> Event:
    queryset = get_object_or_404(Event, slug=slug, make_private=True)
    return queryset


class IndexView(View):

    template_name: str = "index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


# Category views.
class CategoryListView(View):

    template_name: str = "categories.html"

    def get(self, request: HttpRequest):
        categories = Category.objects.all()
        events = []
        for category in categories:
            events.append((category, Event.public.filter(category=category)))
        context = {
            "categories": categories,
            "events": events,
        }
        return render(request, self.template_name, context)


class CategoryDetailView(View):

    template_name: str = "category.html"

    def get(self, request: HttpRequest, slug):
        category = Category.objects.get(slug=slug)
        if request.user.is_authenticated:
            queryset = (
                category.events(manager="public").all()
                | category.events(manager="private").filter(user=request.user)
            ).order_by("-date_posted")
        else:
            queryset = category.events(manager="public").all().order_by("-date_posted")
        context = {"queryset": queryset, "category": category}
        return render(request, self.template_name, context)


# Event Views
class EventsListView(View):

    template_name: str = "homepage.html"

    def get(self, request: HttpRequest):
        events = Event.public.all().order_by("-date_posted")
        context = {"events": events}
        return render(request, self.template_name, context)


class EventDetailView(View):

    form_class = CommentForm
    template_name: str = "event_detail.html"

    def get(self, request: HttpRequest, slug):
        event = get_event(slug)
        tags = event.tags.all()
        related_events = (
            Event.objects.filter(tags__id__in=tags).exclude(id=event.id).order_by("date_posted").distinct()
        )
        form = self.form_class()
        comment_set = event.comments.all()
        context = {
            "event": event,
            "events": Event,
            "comment": Comment,
            "tags": tags,
            "related_events": related_events[:4],
            "comments": comment_set,
            "form": form,  
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, slug):
        event = get_event(slug)
        
        if request.POST[str(event.id)] == "Add to attend-list":
            event.user_attending.add(request.user)
            print(event.user_attending.all())
            # count = event.user_attending.count()
            return HttpResponse("This evnt has been added to your evnt list.")
        elif request.POST[str(event.id)] == "Remove from attend-list":
            event.user_attending.remove(request.user)
            print(event.user_attending.all())
            return HttpResponse("This evnt has been removed from your attend-list")
            
        form = self.form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = get_event(slug)
            comment.save()
            return redirect(event)


class EventTagView(View):

    template_name: str = "event_tag.html"

    def get(self, request: HttpRequest, slug):
        events = Event.objects.filter(tags__slug__contains=slug)
        tag = get_object_or_404(Tag, slug=slug)
        context = {"events": events, "tag": tag}
        return render(request, self.template_name, context)


class ManageEventsView(LoginRequiredMixin, View):

    template_name: str = "manage_events.html"

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


class PrivateEventsView(LoginRequiredMixin, View):

    template_name: str = "private_events.html"

    def get(self, request: HttpRequest):
        my_events = Event.private.filter(user=request.user)
        context = {"my_events": my_events}
        return render(request, self.template_name, context)


class PrivateEventDetailView(LoginRequiredMixin, View):

    template_name: str = "private_event_detail.html"

    def get(self, request: HttpRequest, slug):
        event = get_private_event(slug)
        if request.user == event.user:
            event = Event.private.get(user=request.user, name=event)
            tags = event.tags.all()
            related_events =(
                Event.objects.filter(tags__id__in=tags).exclude(id=event.id).order_by("date_posted").distinct()
            )
        else:
            return HttpResponseForbidden()
        context = {
            "event": event,
            "tags": tags,
            "related_events": related_events[:4],
        }
        return render(request, self.template_name, context)


class AddEventView(LoginRequiredMixin, View):

    form_class = AddEventForm
    template_name: str = "add_event.html"

    def get(self, request: HttpRequest):
        form = self.form_class()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.slug = slugify(event.name)
            event.save()
            form.save_m2m()
            messages.success(request, "Evnt posted successfully.")
            return redirect(event)
        else:
            messages.error(request, "Your evnt was not posted. Try again.")
        context = {"form": form}
        return render(request, self.template_name, context)


class EditEventView(LoginRequiredMixin, View):

    form_class = EditEventForm
    template_name: str = "edit_event.html"

    def get(self, request: HttpRequest, slug):
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            form = self.form_class(instance=event)
        else:
            return HttpResponseForbidden()
        context = {"form": form, "event": event}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, slug):
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            form = self.form_class(
                instance=event, data=request.POST, files=request.FILES
            )
            if form.is_valid():
                edit = form.save(commit=False)
                edit.slug = slugify(edit.name)
                edit.save()
                form.save_m2m()
                messages.success(request, "Changes saved!")
                return redirect(edit)
            else:
                messages.error(request, "Error while updating evnt.")
        else:
            return HttpResponseForbidden()
        context = {"form": form, "event": event}
        return render(request, self.template_name, context)


class DeleteEventView(LoginRequiredMixin, View):

    template_name: str = "delete_event.html"

    def get(self, request: HttpRequest, slug):
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            context = {"event": event}
            return render(request, self.template_name, context)
        else:
            return HttpResponseForbidden()

    def post(self, request: HttpRequest, slug) -> HttpResponse:
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            event.delete()
            return redirect("events:home")
        else:
            return HttpResponseForbidden()


class SearchEventView(View):

    template_name: str = "search_events.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.GET.get("search")
        print(query)
        if query == ("" or " "):
            raise ValidationError("Enter a value")
        else:
            search_results = Event.objects.filter(name__contains=query)
        context = {"events": search_results}
        return render(request, self.template_name, context)


class Attendlist(LoginRequiredMixin, View):
    
    template_name: str = "attend_list.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        events = Event.public.filter(user_attending=request.user)
        context = {"events": events}
        return render(request, self.template_name, context)