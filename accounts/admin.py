from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Follow, Video, BetMarker, BetMarkerOption,
    BetEvent, BetEventOption, InboxMessage, ShopItem,
    PlacedMarkerBet, PlacedEventBet, Notification,
)


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


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'video_type', 'views', 'likes', 'created_at')
    list_filter = ('video_type', 'is_live')


class BetMarkerOptionInline(admin.TabularInline):
    model = BetMarkerOption
    extra = 0


@admin.register(BetMarker)
class BetMarkerAdmin(admin.ModelAdmin):
    list_display = ('video', 'timestamp', 'question', 'total_pool', 'participants')
    inlines = [BetMarkerOptionInline]


class BetEventOptionInline(admin.TabularInline):
    model = BetEventOption
    extra = 0


@admin.register(BetEvent)
class BetEventAdmin(admin.ModelAdmin):
    list_display = ('question', 'creator', 'video', 'status', 'expires_at', 'total_pool')
    list_filter = ('status',)
    inlines = [BetEventOptionInline]


@admin.register(PlacedMarkerBet)
class PlacedMarkerBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'marker', 'option', 'amount', 'resolved', 'payout', 'created_at')
    list_filter = ('resolved',)


@admin.register(PlacedEventBet)
class PlacedEventBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'option', 'amount', 'resolved', 'payout', 'created_at')
    list_filter = ('resolved',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notif_type', 'message', 'is_read', 'created_at')
    list_filter = ('notif_type', 'is_read')


@admin.register(InboxMessage)
class InboxMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'status', 'created_at')

