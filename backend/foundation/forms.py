from django import forms
from django.contrib.auth.models import User
from .models import Member, Campaign


class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=120)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
            )
        return user


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "category", "summary", "cta_text", "cta_url", "highlight", "feature", "image", "deadline"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }
