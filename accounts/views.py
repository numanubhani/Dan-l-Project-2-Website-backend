from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import User, Follow, Video, BetMarker, InboxMessage, ShopItem
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    VideoSerializer,
    VideoCreateSerializer,
    InboxMessageSerializer,
    ShopItemSerializer
)


@extend_schema(
    request=RegisterSerializer,
    responses={201: UserSerializer},
    description='Register a new user account',
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'test123',
                'password2': 'test123',
                'name': 'Test User',
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'user': user_serializer.data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginSerializer,
    responses={200: UserSerializer},
    description='Login with username and password',
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'username': 'admin',
                'password': 'admin123',
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Login user and return token"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'user': user_serializer.data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: OpenApiTypes.OBJECT},
    description='Logout user and delete authentication token',
    summary='Logout'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user and delete token"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: UserSerializer},
    description='Get current user profile',
    summary='Get Profile'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
    description='Update user profile information',
    summary='Update Profile'
)
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update current user profile"""
    # Handle file uploads (avatar)
    data = request.data.copy()
    
    serializer = UserProfileSerializer(
        request.user,
        data=data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: UserSerializer},
    description='Get current authenticated user information',
    summary='Get Current User'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: UserProfileSerializer},
    description='Get user profile by ID',
    summary='Get User Profile'
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_profile(request, user_id):
    """Get user profile by ID"""
    try:
        user = User.objects.get(id=user_id)
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={200: OpenApiTypes.OBJECT},
    description='Follow or unfollow a user',
    summary='Toggle Follow'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_follow(request, user_id):
    """Follow or unfollow a user"""
    try:
        target_user = User.objects.get(id=user_id)
        if target_user == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if not created:
            follow.delete()
            return Response({'message': 'Unfollowed', 'is_following': False}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Followed', 'is_following': True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={200: VideoSerializer},
    description='Get a single video by ID',
    summary='Get Video'
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_video(request, video_id):
    """Get a single video by ID"""
    try:
        video = Video.objects.get(id=video_id)
        # Check if user is owner to show bet markers
        is_owner = request.user.is_authenticated and request.user.id == video.creator.id
        # Check if preview mode is requested
        is_preview = request.query_params.get('preview', 'false').lower() == 'true'
        # Show bet markers if owner or in preview mode
        show_bet_markers = is_owner or is_preview
        serializer = VideoSerializer(video, context={'request': request, 'is_owner': show_bet_markers})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={200: VideoSerializer(many=True)},
    description='Get user videos/reels',
    summary='Get User Videos',
    parameters=[
        OpenApiParameter('type', OpenApiTypes.STR, description='Filter by type: reels, videos, or live', required=False),
    ]
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_videos(request, user_id):
    """Get videos/reels for a user"""
    try:
        user = User.objects.get(id=user_id)
        video_type = request.query_params.get('type', None)
        
        videos = Video.objects.filter(creator=user)
        
        # Filter by type if provided
        if video_type == 'reels':
            videos = videos.filter(video_type='short')
        elif video_type == 'videos':
            videos = videos.filter(video_type='long')  # Long videos only
        elif video_type == 'live':
            videos = videos.filter(is_live=True)
        
        # Check if user is owner to include bet markers
        is_owner = request.user.is_authenticated and request.user.id == int(user_id)
        
        videos = videos.order_by('-created_at')
        serializer = VideoSerializer(videos, many=True, context={'request': request, 'is_owner': is_owner})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    responses={200: InboxMessageSerializer(many=True)},
    description='Get user inbox messages',
    summary='Get Inbox'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_inbox(request):
    """Get inbox messages for current user"""
    messages = InboxMessage.objects.filter(recipient=request.user).order_by('-created_at')
    serializer = InboxMessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: ShopItemSerializer(many=True)},
    description='Get user shop items',
    summary='Get Shop Items'
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_shop_items(request, user_id):
    """Get shop items for a user"""
    try:
        user = User.objects.get(id=user_id)
        items = ShopItem.objects.filter(seller=user).order_by('-created_at')
        serializer = ShopItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    request=VideoCreateSerializer,
    responses={201: VideoSerializer},
    description='Upload a new video',
    summary='Upload Video'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_video(request):
    """Upload a new video"""
    import json
    
    serializer = VideoCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        video = serializer.save()
        
        # Create bet markers if provided
        bet_markers_str = request.data.get('bet_markers', '[]')
        try:
            if isinstance(bet_markers_str, str):
                bet_markers_data = json.loads(bet_markers_str)
            else:
                bet_markers_data = bet_markers_str
        except (json.JSONDecodeError, TypeError):
            bet_markers_data = []
        
        for marker_data in bet_markers_data:
            options = marker_data.get('options', [])
            BetMarker.objects.create(
                video=video,
                timestamp=float(marker_data.get('timestamp', 0)),
                question=marker_data.get('question', ''),
                option1_text=options[0].get('text', 'Yes') if len(options) > 0 else 'Yes',
                option2_text=options[1].get('text', 'No') if len(options) > 1 else 'No',
                option1_odds=float(options[0].get('odds', 2.0)) if len(options) > 0 else 2.0,
                option2_odds=float(options[1].get('odds', 2.0)) if len(options) > 1 else 2.0,
            )
        
        # Return created video with bet markers
        video_serializer = VideoSerializer(video, context={'request': request, 'is_owner': True})
        return Response(video_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

