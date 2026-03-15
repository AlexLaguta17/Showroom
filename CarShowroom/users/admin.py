"""Admin registration for the users app models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class CustomUserAdmin(UserAdmin):
    """Custom admin for User that adds extra fields to the creation form."""

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "type",
                    "phone_number",
                    "country",
                    "age",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
