from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import (
    User, Follow, Video, BetMarker, BetMarkerOption,
    BetEvent, BetEventOption, InboxMessage, ShopItem,
    PlacedMarkerBet, PlacedEventBet, Notification,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'avatar_url', 'role', 'balance', 'date_joined', 'date_of_birth', 'bio', 'location', 'website')
        read_only_fields = ('id', 'date_joined', 'balance')
    
    def get_avatar_url(self, obj):
        """Return avatar URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return obj.avatar_url or ''


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates"""
    
    avatar_url = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'name', 'avatar', 'avatar_url', 'role', 'balance',
            'date_of_birth', 'bio', 'location', 'date_joined',
            'followers_count', 'following_count', 'videos_count', 'is_following'
        )
        read_only_fields = ('id', 'username', 'role', 'balance', 'date_joined', 'followers_count', 'following_count', 'videos_count', 'is_following')
    
    def get_avatar_url(self, obj):
        """Return avatar URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return obj.avatar_url or ''
    
    def get_followers_count(self, obj):
        return obj.followers_set.count()
    
    def get_following_count(self, obj):
        return obj.following_set.count()
    
    def get_videos_count(self, obj):
        return obj.videos.count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'name', 'role')
        extra_kwargs = {
            'name': {'required': False},
            'role': {'required': False},
            'username': {'required': True}
        }
    
    def validate_username(self, value):
        """Validate username is not a number and is unique"""
        # Check if username is a number
        if value.isdigit():
            raise serializers.ValidationError("Username cannot be a number. Please use letters and/or numbers.")
        
        # Check if username already exists
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists. Please choose a different username.")
        
        # Check username length and characters
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Username can only contain letters, numbers, hyphens, and underscores.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        return attrs


class VideoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating videos"""
    
    class Meta:
        model = Video
        fields = (
            'title', 'description', 'video_file', 'video_url', 'thumbnail', 'thumbnail_url',
            'video_type', 'is_live'
        )
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model"""
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    creator_avatar = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    video_file_url = serializers.SerializerMethodField()
    bet_markers = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = (
            'id', 'creator', 'creator_name', 'creator_avatar', 'title', 'description',
            'video_file', 'video_file_url', 'video_url', 'thumbnail', 'thumbnail_url', 'views', 'likes',
            'comments', 'video_type', 'is_live', 'created_at', 'bet_markers', 'bet_event'
        )
        read_only_fields = ('id', 'created_at', 'views', 'likes', 'comments')
    
    def get_creator_avatar(self, obj):
        return obj.creator.get_avatar_url()
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return obj.thumbnail_url or ''
    
    def get_video_file_url(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None
    
    def get_bet_markers(self, obj):
        # Show bet markers for all users (viewers place bets on them)
        markers = obj.bet_markers.all()
        result = []
        for m in markers:
            opts = list(m.options_list.order_by('order', 'id').values('id', 'text', 'odds'))
            if not opts:
                opts = [
                    {'id': 'option1', 'text': m.option1_text or 'Yes', 'odds': float(m.option1_odds)},
                    {'id': 'option2', 'text': m.option2_text or 'No', 'odds': float(m.option2_odds)}
                ]
            else:
                opts = [{'id': str(o['id']), 'text': o['text'], 'odds': float(o['odds'])} for o in opts]
            result.append({
                'id': str(m.id),
                'timestamp': m.timestamp,
                'question': m.question,
                'options': opts,
                'total_pool': float(m.total_pool),
                'participants': m.participants
            })
        return result

    bet_event = serializers.SerializerMethodField()

    def get_bet_event(self, obj):
        """Active (open) live bet event for this video, if any"""
        event = obj.bet_events.filter(status='open').order_by('-created_at').first()
        if not event or (event.expires_at and event.expires_at <= timezone.now()):
            return None
        options = list(event.options_list.order_by('order', 'id').values('id', 'text', 'odds'))
        return {
            'id': str(event.id),
            'question': event.question,
            'options': [{'id': str(o['id']), 'text': o['text'], 'odds': float(o['odds'])} for o in options],
            'totalPool': float(event.total_pool),
            'participants': event.participants,
            'expiresAt': int(event.expires_at.timestamp() * 1000) if event.expires_at else None,
        }


class InboxMessageSerializer(serializers.ModelSerializer):
    """Serializer for InboxMessage model"""
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = InboxMessage
        fields = ('id', 'sender', 'sender_name', 'sender_avatar', 'recipient', 'message', 'is_read', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_sender_avatar(self, obj):
        return obj.sender.get_avatar_url()


class ShopItemSerializer(serializers.ModelSerializer):
    """Serializer for ShopItem model"""
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ShopItem
        fields = ('id', 'seller', 'seller_name', 'title', 'description', 'price', 'image', 'image_url', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url or ''

