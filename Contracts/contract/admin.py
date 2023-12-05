from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Contract, Job
from .forms import ProfileChangeForm, ProfileCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = ProfileCreationForm
    form = ProfileChangeForm
    model = Profile
    list_display = ("username", "is_staff", "is_active",)
    list_filter = ("username", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "balance", "profession", "type")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "password", "first_name", "last_name", "balance", "profession", "type"
            )}
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)

admin.site.register(Profile, CustomUserAdmin)
admin.site.register(Contract)
admin.site.register(Job)