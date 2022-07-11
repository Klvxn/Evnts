from django.contrib import admin

from .models import Category, EventList, Event, Comment


# Register your models here.
@admin.register(Category)
class CatergoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EventList)
class EventList(admin.ModelAdmin):
    list_display = ("name", "user")
    prepopulated_fields = {"slug": ("name",)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Event)
class Event(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "host",
        "venue",
        "date",
        "ticket_price",
        "make_private",
    )
    list_filter = ("ticket_price", "category", "make_private")
    search_fields = [
        "name",
        "venue",
        "host",
    ]
    ordering = ("date",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        CommentInline,
    ]


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = ("username", "comment", "event")
    list_filter = ("event",)
