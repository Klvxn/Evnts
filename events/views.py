from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.views import View

from taggit.models import Tag

from .forms import AddEventForm, CommentForm, EditEventForm
from .models import Category, Event


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

    def get(self, request: HttpRequest) -> HttpResponse:
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

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        category = Category.objects.get(slug=slug)
        if request.user.is_authenticated:
            queryset = (
                category.events(manager="public").all() |
                category.events(manager="private").filter(user=request.user)
            )
        else:
            queryset = category.events(manager="public").all()
        context = {"queryset": queryset, "category": category}
        return render(request, self.template_name, context)


# Event Views
class EventsListView(View):

    template_name: str = "homepage.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        events = Event.public.all()
        context = {"events": events}
        return render(request, self.template_name, context)


class EventDetailView(View):

    form_class = CommentForm
    template_name: str = "event_detail.html"

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_event(slug)
        tags = event.tags.all()
        related_events = (
            Event.public.filter(tags__id__in=tags).exclude(id=event.id)
        ).distinct()
        form = self.form_class()
        comments = event.comments.all()
        for comment in comments:
            print(comment.replies.all())
        context = {
            "event": event,
            "tags": tags,
            "related_events": related_events,
            "comments": comments,
            "form": form,
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_event(slug)
        event_action = request.POST.get(str(event.id))
        if event_action == "Add to attend-list":
            event.users_attending.add(request.user)
            return HttpResponse("This evnt has been added to your evnt list.")
        if event_action == "Remove from attend-list":
            event.users_attending.remove(request.user)
            return HttpResponse("This evnt has been removed from your attend-list")

        form = self.form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = get_event(slug)
            comment.username = request.user
            comment.save()
            return redirect(event.get_absolute_url())


class EventTagView(View):

    template_name: str = "event_tag.html"

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        events = Event.objects.filter(tags__slug__contains=slug)
        tag = get_object_or_404(Tag, slug=slug)
        context = {"events": events, "tag": tag}
        return render(request, self.template_name, context)


class ManageEventsView(LoginRequiredMixin, View):

    template_name: str = "manage_events.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


class PrivateEventsView(LoginRequiredMixin, View):

    template_name: str = "private_events.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        my_events = Event.private.filter(user=request.user)
        context = {"my_events": my_events}
        return render(request, self.template_name, context)


class PrivateEventDetailView(LoginRequiredMixin, View):

    template_name: str = "private_event_detail.html"

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_private_event(slug)
        if request.user == event.user:
            event = Event.private.get(user=request.user, name=event)
            tags = event.tags.all()
        else:
            return HttpResponseForbidden()
        context = {"event": event, "tags": tags}
        return render(request, self.template_name, context)


class AddEventView(LoginRequiredMixin, View):

    form_class = AddEventForm
    template_name: str = "add_event.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.slug = slugify(event.name)
            event.save()
            form.save_m2m()
            messages.success(request, "Evnt posted successfully.")
            return redirect(event)
        messages.error(request, "Your evnt was not posted. Try again.")
        context = {"form": form}
        return render(request, self.template_name, context)


class EditEventView(LoginRequiredMixin, View):

    form_class = EditEventForm
    template_name: str = "edit_event.html"

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_object_or_404(Event, slug=slug)
        if request.user == event.user:
            form = self.form_class(instance=event)
        else:
            return HttpResponseForbidden()
        context = {"form": form, "event": event}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_object_or_404(Event, slug=slug)
        if request.user == event.user:
            form = self.form_class(
                instance=event, data=request.POST, files=request.FILES
            )
            if form.is_valid():
                edit = form.save(commit=False)
                edit.slug = slugify(edit.name)
                edit.save()
                form.save_m2m()
                messages.success(request, "Changes saved!")
                return redirect(event.get_absolute_url())
            messages.error(request, "Error while updating evnt.")
        else:
            return HttpResponseForbidden()
        context = {"form": form, "event": event}
        return render(request, self.template_name, context)


class DeleteEventView(LoginRequiredMixin, View):

    template_name: str = "delete_event.html"

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            context = {"event": event}
            return render(request, self.template_name, context)
        return HttpResponseForbidden()

    def post(self, request: HttpRequest, slug) -> HttpResponse:
        event = get_object_or_404(Event, slug=slug)
        if request.user.is_superuser or request.user == event.user:
            event.delete()
            return redirect("events:home")
        return HttpResponseForbidden()


class SearchEventView(View):

    template_name: str = "search_events.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.GET.get("search")
        search_results = None
        if not query:
            pass
        else:
            if request.user.is_authenticated:
                search_results = (
                    Event.private.filter(name__icontains=query, user=request.user)
                    | Event.public.filter(name__icontains=query)
                ).distinct()
            else:
                search_results = Event.public.filter(name__icontains=query)
        context = {"search_results": search_results, "query": query}
        return render(request, self.template_name, context)


class Attendlist(LoginRequiredMixin, View):

    template_name: str = "attend_list.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        all_events = Event.public.all()[:7]
        attend_list = Event.public.filter(users_attending=request.user)
        users_attending = []
        for event in attend_list:
            users_attending += event.users_attending.exclude(id=request.user.id)
        users_count = len(users_attending)
        max_attndts_events = {}
        for events in all_events:
            max_attndts_events[events] = events.users_attending.count()
        max_attndts_events = {
            key: value
            for key, value in sorted(
                max_attndts_events.items(), key=lambda item: item[1], reverse=True
            )
        }
        context = {
            "events": attend_list,
            "users": users_count,
            "max_attndts": max_attndts_events,
        }
        return render(request, self.template_name, context)
