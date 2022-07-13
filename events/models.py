from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from taggit.managers import TaggableManager


# Create your models here.
class Category(models.Model):

    CATEGORY_CHOICES = [
        ("Wedding", "Wedding"),
        ("Concert", "Concert"),
        ("Party", "Party"),
        ("Conference", "Conference"),
        ("Festival", "Festival"),
        ("Exhibition", "Exhibition"),
        ("Meeting", "Meeting"),
        ("Sport Event", "Sport Event"),
        ("Others", "Others"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=50, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("events:category-detail", kwargs={"slug": self.slug})


class EventList(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=20, default="My Event list")
    slug = models.SlugField(max_length=25, default="my-event-list")

    class Meta:
        verbose_name = "Event List"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PrivateEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(make_private=True)


class PublicEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(make_private=False)


class Event(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True, null=True)
    event_list = models.ForeignKey(
        EventList, on_delete=models.PROTECT, null=True, blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to="media/event imgs", null=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField()
    host = models.CharField(max_length=50, blank=True)
    special_guests = models.CharField(max_length=100, blank=True)
    venue = models.CharField(max_length=100)
    date_of_event = models.DateTimeField()
    make_private = models.BooleanField(
        verbose_name="Make Private?",
        help_text="Do you want to keep this evnt from others?",
        default=False,
    )
    ticket_price = models.PositiveIntegerField(blank=True, null=True)

    # Managers
    objects = models.Manager()
    tags = TaggableManager()
    public = PublicEventManager()
    private = PrivateEventManager()
    
    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:event-detail", kwargs={"slug": self.slug})

    def get_absolute_url_for_private_events(self):
        return reverse("events:private-event-detail", kwargs={"slug": self.slug})

    @property
    def past_event(self):
        date = timezone.now().date()
        if self.date_of_event.date() < date:
            return True


class Comment(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    username = models.CharField(max_length=20)
    comment = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username}, {self.comment}"
