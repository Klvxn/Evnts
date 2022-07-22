from django.urls import path

from .views import (
    AddEventView,
    Attendlist,
    CategoryDetailView,
    CategoryListView,
    DeleteEventView,
    EditEventView,
    EventDetailView,
    EventsListView,
    EventTagView,
    IndexView,
    ManageEventsView,
    PrivateEventDetailView,
    PrivateEventsView,
    SearchEventView,
)


app_name = "events"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("home/", EventsListView.as_view(), name="home"),
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    path("private-events/", PrivateEventsView.as_view(), name="private-events"),
    path("my-private-events/<slug:slug>/", PrivateEventDetailView.as_view(), name="private-event-detail"),
    path("manage-events/", ManageEventsView.as_view(), name="manage-events"),
    path("events/<slug:slug>/", EventDetailView.as_view(), name="event-detail"),
    path("events/tags/<slug:slug>/", EventTagView.as_view(), name="event-tag"),
    path("add-event/", AddEventView.as_view(), name="add-event"),
    path("events/<slug:slug>/delete-event/", DeleteEventView.as_view(), name="delete-event"),
    path("events/<slug:slug>/edit-event/", EditEventView.as_view(), name="edit-event"),
    path("events/", SearchEventView.as_view(), name="search"),
    path("attend-list/", Attendlist.as_view(), name="attend-list"),
]
