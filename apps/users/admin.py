from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import AccountChangeForm, AccountCreationForm


@admin.register(User)
class AccountAdmin(BaseUserAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm
    list_display = ('id', 'phone', 'first_name', 'last_name'
                    , 'is_superuser', 'is_staff',
                    'is_active')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    ordering = ()
    fieldsets = (
        (None, {'fields': ('phone', 'password', 'username', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_superuser', 'is_staff', 'is_active',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('phone', 'password1', 'password2'), }),
    )
    search_fields = ('phone', 'first_name', 'last_name')
