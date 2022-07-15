from datetime import datetime, timedelta
from pprint import pprint
from model_bakery import baker

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from accounts.models import CustomUser

from .models import Category, Event, Comment
from .views import get_event


# Create your tests here.
class BaseSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            password="password1234",
            email="testuser@events.com",
            gender="Male",
        )

        cls.user_2 = CustomUser.objects.create_user(
            username="testuser_2",
            password="4321drowssap",
            email="testuser2@events.com",
            gender="Female"
        )

        cls.category = Category.objects.create(
            name="Wedding",
            description="testing category description",
            slug="wedding",
        )

        cls.event = Event.objects.create(
            user=cls.user,
            category=cls.category,
            name="test event",
            description="Van is getting married on new year's eve",
            venue="The Slum",
            date_of_event=datetime(2022, 9, 1),
            tags="Test",
        )


# Model tests.
class CategoryModelTest(BaseSetUp):
    def test_string_rep(self):
        category = self.category
        self.assertEqual(str(category.name), self.category.name)

    def test_get_absolute_url(self):
        self.assertEqual(self.category.get_absolute_url(), "/category/wedding/")


class EventModelTest(BaseSetUp):
    def test_string_representation(self):
        event = self.event
        self.assertEqual(str(event), "test event")

    def test_get_absolute_url(self):
        self.assertEqual(self.event.get_absolute_url(), "/events/test-event/")

    def test_past_event_date(self):
        time = timezone.now() -  timedelta(days=1)
        event = Event(name="Halloween", date_of_event=time)
        self.assertIs(event.past_event, True)


class CommentModelTest(BaseSetUp):
    def test_string_rep(self):
        comment = Comment(username="testuser", comment="test comment")
        self.assertEqual(
            f"{comment.username}, {comment.comment}", "testuser, test comment"
        )

    def test_comment_date(self):
        date = timezone.now()
        comment = Comment(username="testuser", comment="testcomment")
        self.assertEqual(date, comment.date_added)


# View tests.
class GetEventFunctionTest(BaseSetUp):
    def test_get_event_function(self):
        event = get_event("test-event")
        self.assertEqual(event, self.event)


class IndexViewTest(TestCase):
    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Welcome to EVNTS")

    def test_indexpage_url_exists_by_name(self):
        response = self.client.get(reverse("events:index"))
        self.assertEqual(response.status_code, 200)


class CategoriesListViewTest(BaseSetUp):
    def test_view_url(self):
        response = self.client.get("/categories/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("events:categories"))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/categories/")
        self.assertTemplateUsed(response, "categories.html")
        self.assertContains(response, "Categories")


class CategoryDetailViewTest(BaseSetUp):
    def test_view_url(self):
        response = self.client.get("/category/wedding/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("events:category-detail", args=["wedding"]))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/category/wedding/")
        self.assertTemplateUsed(response, "category.html")
        self.assertContains(response, "Category: Wedding")


class EventsListViewTest(BaseSetUp):
    def test_view_url(self):
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("events:home"))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/home/")
        self.assertTemplateUsed(response, "homepage.html")
        self.assertContains(response, "Evnts")


class EventDetailViewTest(BaseSetUp):
    def test_view_url(self):
        response = self.client.get("/events/test-event/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("events:event-detail", args=["test-event"]))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/events/test-event/")
        self.assertTemplateUsed(response, "event_detail.html")
        self.assertContains(response, "test event")

    def test_user_can_post_comment(self):
        response = self.client.post(
            "/events/test-event/", {"username": "sam", "comment": "test comment"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/events/test-event/")


class PrivateEventViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/private-events/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get(reverse("events:private-events"))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/private-events/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/private-events/")

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/private-events/")
        self.assertTemplateUsed(response, "private_events.html")
        self.assertContains(response, "My Private Evnts")

    def test_user_cannot_view_another_user_private_event(self):
        Event.objects.filter(id=self.event.id).update(make_private=True)
        self.client.login(username="testuser_2", password="4321drowssap")
        response = self.client.get("/my-private-events/test-event/")
        self.assertEqual(response.status_code, 403)

    def test_view_queryset_is_correct(self):
        event = self.event
        Event.objects.filter(id=event.id).update(make_private=True)
        self.assertQuerysetEqual(Event.private.filter(user=self.user), values=[event,])
        self.assertQuerysetEqual(Event.private.filter(user=self.user_2), values=[])
                

class ManageEventsViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/manage-events/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get(reverse("events:manage-events"))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_for_logged_in_users_only(self):
        response = self.client.get("/manage-events/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/manage-events/")

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/manage-events/")
        self.assertTemplateUsed(response, "manage_events.html")
        self.assertContains(response, "Manage Your Evnts")
        

class AddEventViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/add-event/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get(reverse("events:add-event"))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/add-event/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/add-event/")

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/add-event/")
        self.assertTemplateUsed(response, "add_event.html")
        self.assertContains(response, "Add an evnt")

    def test_add_event(self):
        self.client.login(username="testuser", password="password1234")
        data = {
            "user": self.user,
            "category": self.category,
            "name": "test event 2",
            "description": "test add event",
            "venue": "test venue",
            "date_of_event": timezone.datetime(2022, 10, 1),
            "ticket_price": "12",
            "tags": "test",
        }
        response = self.client.post("/add-event/",data=data)
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your evnt was not posted. Try again.")
        self.assertContains(response, "This field is required")


class EditEventViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/events/test-event/edit-event/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get(reverse("events:edit-event", args=["test-event"]))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/events/test-event/edit-event/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/events/test-event/edit-event/"
        )

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/events/test-event/edit-event/")
        self.assertTemplateUsed(response, "edit_event.html")
        self.assertContains(response, "Edit evnt")


    def test_edit_event(self):
        self.client.login(username="testuser", password="password1234")
        event = baker.make(
            Event,
            # category=self.category,
            name="testubg model bakery",
            description="event description updated",
            image="media/concert.png",
            ticket_price=20,
            tags="kanye",
            make_m2m=True
        )
        # data = {
        #     "category": self.category,
        #     "name": "test event updated",
        #     "description": "description update",
        #     "venue": "Venue update",
        #     "date_of_event": datetime.t(2022, 10, 1),
        #     "make_private": True,
        #     "tags": "Test edit"
        # },
        pprint(event.__dict__)
        response = self.client.post("/events/test-event/edit-event/", data=event.__dict__)
        # self.assertEqual(response.status_code, 302)
        self.assertContains(response, "Error while updating evnt.")
        print(response.content)
        self.assertContains(response, "Enter a valid category")

    def test_only_event_user_can_edit_their_event(self):
        self.client.login(username="testuser_2", password="4321drowssap")
        get_response = self.client.get("/events/test-event/edit-event/")
        post_response = self.client.post("/events/test-event/edit-event/")
        self.assertEqual(get_response.status_code, post_response.status_code, 403)


class DeleteEventViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/events/test-event/delete-event/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get(reverse("events:delete-event", args=["test-event"]))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/events/test-event/delete-event/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/events/test-event/delete-event/"
        )

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.get("/events/test-event/delete-event/")
        self.assertTemplateUsed(response, "delete_event.html")
        self.assertContains(response, "Delete evnt")

    def test_user_can_delete_event(self):
        self.client.login(username="testuser", password="password1234")
        response = self.client.post("/events/test-event/delete-event/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/home/")

    def test_only_event_user_can_delete_their_event(self):
        self.client.login(username="testuser_2", password="4321drowssap")
        get_response = self.client.get("/events/test-event/delete-event/")
        post_response = self.client.post("/events/test-event/delete-event/")
        self.assertEqual(get_response.status_code, post_response.status_code, 403)
