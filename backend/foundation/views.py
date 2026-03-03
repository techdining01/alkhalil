from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Campaign
from .forms import SignUpForm, CampaignForm


def index(request):
    campaigns = Campaign.objects.all()
    featured = [c for c in campaigns if c.feature]
    highlighted = [c for c in campaigns if c.highlight]
    donate_info = {
        "bank": "Sample Bank",
        "account_name": "Al‑Khalil Masjid Foundation",
        "account_number": "0000000000",
        "reference": "AL-KHALIL SUPPORT"
    }
    return render(request, "index.html", {
        "campaigns": campaigns,
        "featured": featured,
        "highlighted": highlighted,
        "donate": donate_info
    })


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You may now sign in.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


@login_required
def campaign_new(request):
    if request.method == "POST":
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Campaign created.")
            return redirect("index")
    else:
        form = CampaignForm()
    return render(request, "campaign_form.html", {"form": form})


@login_required
def campaign_delete(request, pk):
    obj = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.info(request, "Campaign deleted.")
        return redirect("index")
    return render(request, "confirm_delete.html", {"object": obj})


def vite_client_stub(request):
    return HttpResponse("// vite client not used; stubbed to silence 404s\n", content_type="application/javascript")
