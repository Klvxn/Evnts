from django.test import TestCase
from django.urls import reverse

from .models import CustomUser
from .views import get_user


# Create your tests here.
class BaseSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = CustomUser.objects.create_user(
            username="testuser_1",
            password="password1234",
            email="testuser1@events.com",
            gender="Others",
            first_name="Test",
            last_name="User",
        )

        cls.user_2 = CustomUser.objects.create_user(
            username="testuser_2",
            password="4321drowssap",
            email="testuser2@events.com",
            first_name="Django",
            last_name="Test",
        )


class UserModelTests(BaseSetUp):
    def test_string_representation(self):
        user = self.user_1
        self.assertEqual(str(user), "testuser_1")

    def test_get_absolute_url(self):
        user = self.user_1
        self.assertEqual(user.get_absolute_url(), "/accounts/testuser_1/profile/")


class LoginViewTest(BaseSetUp):
    def test_get_user_function(self):
        user = self.user_1
        self.assertEqual(get_user(user.username), self.user_1)

    def test_view_url(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_1.username, CustomUser.objects.all()[0].username)
        self.assertEqual(self.user_1.password, CustomUser.objects.all()[0].password)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/accounts/login/")
        self.assertTemplateUsed(response, "login.html")
        self.assertContains(response, "Login")

    def test_login_user(self):
        response = self.client.login(username="testuser_1", password="password1234")
        self.assertIs(response, True)


class LogoutViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = CustomUser.objects.create_user(username="user_2", password="123@A%")

    def test_logout_user(self):
        self.client.login(username="user_2", password="123@A%")
        response = self.client.logout()
        self.assertIs(response, None)
    
    def test_view_redirects_to_index_page(self):
        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")


class RegisterViewTest(TestCase):
    def test_view_url(self):
        response = self.client.get("/accounts/register/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get("/accounts/register/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, "Register")

    def test_register_user(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "skete",
                "email": "skete@email.com",
                "gender": "Male",
                "password1": "hello-django$",
                "password2": "hello-django$",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/home/")


class UserProfileViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/profile/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get(reverse("accounts:user-profile", args=["testuser_1"]))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_users(self):
        response = self.client.get("/accounts/testuser_1/profile/")
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/profile/")
        self.assertTemplateUsed(response, "user_profile.html")
        self.assertContains(response, "testuser_1")


class EditUserProfileViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/edit-profile/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get(reverse("accounts:edit-profile", args=["testuser_1"]))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/edit-profile/")
        self.assertTemplateUsed(response, "edit_profile.html")
        self.assertContains(response, "Edit your profile")

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/accounts/testuser_1/edit-profile/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/testuser_1/edit-profile/"
        )

    def test_edit_user_profile(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.post(
            "/accounts/testuser_1/edit-profile/",
            {
                "username": "testuser_1",
                "password": "lilbitCH21",
                "email": "t_user@events.com",
                "gender": "Male",
                "first_name": "Test",
                "last_name": "User",
            },
        )  # Edited the test user's email and gender.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/testuser_1/profile/")
        

    def test_a_user_cannot_edit_another_user_profile(self):
        self.client.login(username="testuser_2", password="4321drowssap")
        get_response = self.client.get("/accounts/testuser_1/edit-profile/")
        post_response = self.client.post(
            "/accounts/testuser_1/edit-profile/",
            {
                "username": "testuser_1",
                "password": "password1234",
                "email": "fake_user@events.com",
                "gender": "Female",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        self.assertEqual(get_response.status_code, post_response.status_code, 403)


class DeleteUserAccountViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/delete-account/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get(reverse("accounts:delete-account", args=["testuser_1"]))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/accounts/testuser_1/delete-account/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/testuser_1/delete-account/"
        )

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/testuser_1/delete-account/")
        self.assertTemplateUsed(response, "delete_account.html")
        self.assertContains(response, "Delete account")

    def test_delete_user_account(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.post("/accounts/testuser_1/delete-account/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/home/")
        # Check that the user account was successfully deleted.
        response = self.client.login(username="testuser_1", password="password1234")
        self.assertIs(response, False)

    def test_a_user_cannot_delete_another_user_profile(self):
        self.client.login(username="testuser_2", password="4321drowssap")
        get_response = self.client.get("/accounts/testuser_1/delete-profile/")
        post_response = self.client.post("/accounts/testuser_1/delete-profile/")
        self.assertEqual(get_response.status_code, post_response.status_code, 403)


class ChangePasswordViewTest(BaseSetUp):
    def test_view_url(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/change-password/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/accounts/change-password/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/change-password/"
        )

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/change-password/")
        self.assertTemplateUsed(response, "password_change.html")
        self.assertContains(response, "Change password")

    def test_change_user_password(self):
        pass


class ChangePasswordDoneViewTest(BaseSetUp):

    def test_view_url(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/password-change-done/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_by_name(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get(reverse("accounts:password_change_done"))
        self.assertEqual(response.status_code, 200)

    def test_view_is_accessible_to_logged_in_users_only(self):
        response = self.client.get("/accounts/password-change-done/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/password-change-done/"
        )

    def test_view_renders_correct_template(self):
        self.client.login(username="testuser_1", password="password1234")
        response = self.client.get("/accounts/password-change-done/")
        self.assertTemplateUsed(response, "password_change_done.html")
        self.assertContains(response, "Password Change Done")



