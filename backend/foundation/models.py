from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    CATEGORY_CHOICES = [
        ("Member", "Member"),
        ("Volunteer", "Volunteer"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Member")
    is_approved = models.BooleanField(default=False, help_text="Designates whether this user has been approved by an admin.")
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username


class Campaign(models.Model):
    CATEGORY_CHOICES = [
        ("Project", "Project"),
        ("Food", "Food"),
        ("Community Programme", "Community Programme"),
        ("Medical", "Medical"),
        ("Relief", "Relief"),
    ]
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="Project")
    summary = models.TextField(blank=True)
    cta_text = models.CharField(max_length=48, blank=True, help_text="CTA = Call To Action button text, e.g., Donate")
    cta_url = models.URLField(blank=True, help_text="Link opened when CTA is clicked")
    highlight = models.BooleanField(default=True, help_text="Show in marquee")
    feature = models.BooleanField(default=True, help_text="Feature in carousel")
    image = models.ImageField(upload_to="campaigns/", blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
