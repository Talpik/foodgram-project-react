from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import AppUser
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    """
    Registering the required fields
    of the user model in the Django admin panel.
    """
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("email", "username", "first_name",
                    "last_name", "is_admin")
    list_filter = ("is_admin", "email", "username")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name",
                       "last_name", "password_1", "password_2"),
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(AppUser, UserAdmin)

admin.site.unregister(Group)
