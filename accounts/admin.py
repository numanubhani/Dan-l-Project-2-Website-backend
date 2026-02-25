from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ('username', 'email', 'name', 'role', 'get_balance_display', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'name')
    ordering = ('-date_joined',)
    
    def get_balance_display(self, obj):
        """Format balance for display"""
        return f"${obj.balance:,.2f}"
    get_balance_display.short_description = 'Balance'
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('VPulse Profile', {
            'fields': ('name', 'avatar', 'avatar_url', 'role', 'balance')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('VPulse Profile', {
            'fields': ('name', 'avatar', 'avatar_url', 'role', 'balance')
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')

