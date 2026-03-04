from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.http import HttpResponse
from .models import Campaign
from .forms import SignUpForm, CampaignForm


def custom_logout(request):
    """Handle logout for both GET and POST requests."""
    auth_logout(request)
    return redirect('index')


def _get_nisab_data():
    import requests as http_requests
    # Defaults / Fallbacks
    data = {
        "gold_price_ngn": 230000.0,  # Per gram
        "silver_price_ngn": 3700.0,   # Per gram
        "ngn_per_usd": 1360.0,
        "nisab_gold_ngn": 0,
        "nisab_silver_ngn": 0,
        "mahr_fatimi_ngn": 0,
        "mahr_min_ngn": 0,
        "diyyah_ngn": 0,
        "date": "2026-03-04",
        "error": None,
    }

    try:
        # 1. Fetch Currency (USD to NGN)
        curr_resp = http_requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if curr_resp.status_code == 200:
            curr_data = curr_resp.json()
            data["ngn_per_usd"] = curr_data.get("rates", {}).get("NGN", 1360.0)

        # 2. Fetch Gold Price in USD
        gold_resp = http_requests.get("https://dailynisab.org/index.php/api/v1/rates/latest", timeout=5)
        if gold_resp.status_code == 200:
            gold_data = gold_resp.json()
            if isinstance(gold_data, list) and len(gold_data) > 0:
                entry = gold_data[0]
            elif isinstance(gold_data, dict):
                entry = gold_data.get("data", gold_data) if "data" in gold_data else gold_data
            else:
                entry = {}
            
            # Unit: USD per troy ounce (31.1035g)
            gold_oz_usd = entry.get("drtInUSD") or entry.get("rate_usd")
            data["date"] = entry.get("drtDate") or entry.get("date") or data["date"]

            if gold_oz_usd:
                # Calculate gold per gram in NGN
                data["gold_price_ngn"] = (float(gold_oz_usd) / 31.1035) * data["ngn_per_usd"]
                
                # Silver Price Approx (using Gold/Silver ratio of approx 85-95)
                # Current market silver is usually ~1/90th of gold price
                data["silver_price_ngn"] = data["gold_price_ngn"] / 90.0

    except Exception as e:
        data["error"] = str(e)

    # 3. Calculate Islamic Benchmarks
    # Zakah Nisab Gold = 87.48g
    data["nisab_gold_ngn"] = data["gold_price_ngn"] * 87.48
    # Zakah Nisab Silver = 612.36g
    data["nisab_silver_ngn"] = data["silver_price_ngn"] * 612.36
    
    # Mahr Fatimi = 500 Dirhams = 1487.5g Silver
    data["mahr_fatimi_ngn"] = data["silver_price_ngn"] * 1487.5
    # Mahr Minimum = 10 Dirhams = 29.75g Silver
    data["mahr_min_ngn"] = data["silver_price_ngn"] * 29.75
    
    # Blood Money (Diyyah) = 1,000 Dinars = 4250g Gold
    data["diyyah_ngn"] = data["gold_price_ngn"] * 4250

    # Format values for display (add commas)
    def fmt(n): return f"{n:,.2f}"
    display = {k: fmt(v) if isinstance(v, (int, float)) else v for k, v in data.items()}
    return display


def index(request):
    campaigns = Campaign.objects.all()
    featured = [c for c in campaigns if c.feature]
    highlighted = [c for c in campaigns if c.highlight]
    
    # Realistic prayer times for Ibadan
    prayer_times = [
        {"name": "Fajr", "time": "05:47 AM", "icon": "🌅"},
        {"name": "Sunrise", "time": "06:54 AM", "icon": "☀️"},
        {"name": "Dhuhr", "time": "12:58 PM", "icon": "🌞"},
        {"name": "Asr", "time": "04:18 PM", "icon": "🌤️"},
        {"name": "Maghrib", "time": "06:58 PM", "icon": "🌇"},
        {"name": "Isha", "time": "08:03 PM", "icon": "🌙"},
    ]
    
    donate_info = {
        "bank": "First Bank Nigeria",
        "account_name": "Al‑Khalil Masjid & Islamic Foundation",
        "account_number": "2041234567",
        "reference": "AL-KHALIL"
    }
    
    nisab_display = _get_nisab_data()
    
    return render(request, "index.html", {
        "campaigns": campaigns,
        "featured": featured,
        "highlighted": highlighted,
        "donate": donate_info,
        "prayer_times": prayer_times,
        "z": nisab_display
    })


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You may now sign in.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
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


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def campaign_delete(request, pk):
    obj = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.info(request, "Campaign deleted.")
        return redirect("index")
    return render(request, "confirm_delete.html", {"object": obj})


def donate(request):
    categories = [
        {"icon": "💰", "title": "Money", "desc": "General monetary donations to support all foundation activities and programmes."},
        {"icon": "🍚", "title": "Food", "desc": "Food items and supplies for distribution to those in need within our community."},
        {"icon": "🏠", "title": "Houseware", "desc": "Household essentials — kitchenware, bedding, furniture — for families starting afresh."},
        {"icon": "🏥", "title": "Medical Caravan", "desc": "Sponsor mobile medical outreach providing free check-ups and medicines to underserved areas."},
        {"icon": "📚", "title": "Education", "desc": "Fund Qur'an classes, textbooks, school supplies and scholarships for students."},
        {"icon": "👕", "title": "Clothing", "desc": "Donate clean, usable clothes for distribution during relief drives and Eid programmes."},
        {"icon": "🤝", "title": "Skill Empowerment", "desc": "Support vocational training — tailoring, computing, farming — to help community members earn a livelihood."},
        {"icon": "🕌", "title": "Masjid Maintenance", "desc": "Contribute towards the upkeep, renovation and expansion of the mosque facility."},
    ]
    bank = {
        "bank": "First Bank Nigeria",
        "account_name": "Al‑Khalil Masjid & Islamic Foundation",
        "account_number": "2041234567",
        "reference": "AL-KHALIL DONATE",
    }
    steps = [
        {"num": "1", "title": "Choose Category", "desc": "Pick what you'd like to support from the categories above."},
        {"num": "2", "title": "Transfer Funds", "desc": "Send your donation to the bank account shown below."},
        {"num": "3", "title": "Add Reference", "desc": "Include the category name in the transfer reference so we can allocate correctly."},
        {"num": "4", "title": "Confirmation", "desc": "We'll confirm receipt and update you on the impact of your generosity."},
    ]
    return render(request, "donate.html", {"categories": categories, "bank": bank, "steps": steps})


def zakah(request):
    display = _get_nisab_data()
    calc_fields = [
        {"id": "cash", "label": "Cash on hand & in bank accounts", "icon": "💵"},
        {"id": "gold", "label": "Gold (market value)", "icon": "🥇"},
        {"id": "silver", "label": "Silver (market value)", "icon": "🥈"},
        {"id": "investments", "label": "Investments, shares & mutual funds", "icon": "📈"},
        {"id": "business", "label": "Business assets & inventory", "icon": "🏪"},
        {"id": "property_income", "label": "Rental / property income receivable", "icon": "🏠"},
        {"id": "debts_owed", "label": "Debts owed to you (expected to be repaid)", "icon": "📋"},
        {"id": "crypto", "label": "Cryptocurrency holdings", "icon": "🪙"},
        {"id": "agriculture", "label": "Agricultural produce (if applicable)", "icon": "🌾"},
    ]
    deductions = [
        {"id": "debts_you_owe", "label": "Debts you owe (due within the year)", "icon": "📉"},
        {"id": "expenses", "label": "Immediate essential expenses", "icon": "🧾"},
    ]
    
    bank_info = {
        "bank": "First Bank Nigeria",
        "account_name": "Al‑Khalil Masjid & Islamic Foundation",
        "account_number": "2041234567",
        "reference": "ZAKAH"
    }

    return render(request, "zakah.html", {
        "z": display,
        "calc_fields": calc_fields,
        "deductions": deductions,
        "donate": bank_info
    })


def vite_client_stub(request):
    return HttpResponse("// vite client not used; stubbed to silence 404s\n", content_type="application/javascript")
