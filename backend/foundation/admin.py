from django.contrib import admin
from .models import Member, Campaign

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "category", "is_approved", "joined_at"]
    list_filter = ["category", "is_approved"]
    actions = ["approve_members"]

    def approve_members(self, request, queryset):
        for member in queryset:
            member.is_approved = True
            member.save()
            # Also activate the base user
            member.user.is_active = True
            member.user.save()
    approve_members.short_description = "Approve selected members"

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "highlight", "feature", "deadline"]
    list_filter = ["category", "highlight", "feature"]
