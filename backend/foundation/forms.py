from django import forms
from django.contrib.auth.models import User
from .models import Member, Campaign


class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=120)
    profile_picture = forms.ImageField(required=False)
    category = forms.ChoiceField(choices=Member.CATEGORY_CHOICES, initial="Member")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # Admin must approve user before login
        user.is_active = False
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                profile_picture=self.cleaned_data.get("profile_picture"),
                category=self.cleaned_data.get("category", "Member"),
            )
        return user


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "category", "summary", "cta_text", "cta_url", "highlight", "feature", "image", "deadline"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Ramadan Food Drive 2026", "class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "summary": forms.Textarea(attrs={"placeholder": "Brief description of the campaign…", "rows": 3, "class": "form-input"}),
            "cta_text": forms.TextInput(attrs={"placeholder": "e.g. Donate Now", "class": "form-input"}),
            "cta_url": forms.URLInput(attrs={"placeholder": "https://example.com/donate", "class": "form-input"}),
            "highlight": forms.CheckboxInput(attrs={"class": "form-check"}),
            "feature": forms.CheckboxInput(attrs={"class": "form-check"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-input", "accept": "image/*"}),
            "deadline": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
        }
        labels = {
            "title": "Campaign Title",
            "category": "Category",
            "summary": "Description",
            "cta_text": "Button Label (CTA)",
            "cta_url": "Button Link (CTA URL)",
            "highlight": "Show in marquee ticker",
            "feature": "Feature in image carousel",
            "image": "Campaign Image",
            "deadline": "Deadline",
        }
