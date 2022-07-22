from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


# Create your models here.
class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    image = models.ImageField(
        verbose_name="Profile picture",
        upload_to="media/profile pics",
        null=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ("Male", "Male"), 
        ("Female", "Female"), 
        ("Others", "Others")
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)

    def __str__(self):
        return f"{self.username}"

    def get_absolute_url(self):
        return reverse("accounts:user-profile", args=[self.username])
