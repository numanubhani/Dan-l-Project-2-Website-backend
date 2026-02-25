from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class UserRole(models.TextChoices):
    VIEWER = 'VIEWER', 'Viewer'
    CREATOR = 'CREATOR', 'Creator'
    ADMIN = 'ADMIN', 'Admin'


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True, help_text="External avatar URL if not using uploaded image")
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.VIEWER
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username or self.email
    
    def get_display_name(self):
        """Return display name (name if set, otherwise username)"""
        return self.name if self.name else self.username
    
    def get_avatar_url(self):
        """Return avatar URL (uploaded image or external URL)"""
        if self.avatar:
            return self.avatar.url
        return self.avatar_url or ''
    
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(max_length=500, blank=True)


class Follow(models.Model):
    """User follow relationships"""
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        db_table = 'follows'
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class Video(models.Model):
    """Video/Reel model"""
    creator = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.URLField(max_length=500, blank=True, help_text="External video URL")
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    video_type = models.CharField(
        max_length=10,
        choices=[('short', 'Short'), ('long', 'Long'), ('live', 'Live')],
        default='short'
    )
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class BetMarker(models.Model):
    """Betting markers for videos"""
    video = models.ForeignKey(Video, related_name='bet_markers', on_delete=models.CASCADE)
    timestamp = models.FloatField(help_text="Timestamp in seconds")
    question = models.CharField(max_length=255)
    option1_text = models.CharField(max_length=100)
    option2_text = models.CharField(max_length=100)
    option1_odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    option2_odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    total_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bet_markers'
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.video.title} - {self.timestamp}s'


class InboxMessage(models.Model):
    """Inbox messages between users"""
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inbox_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.sender.username} to {self.recipient.username}'


class ShopItem(models.Model):
    """Shop items for sale"""
    seller = models.ForeignKey(User, related_name='shop_items', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='shop/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('sold', 'Sold'), ('pending', 'Pending')],
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shop_items'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

