from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import (
    User, Follow, Video, BetMarker, BetMarkerOption,
    BetEvent, BetEventOption, InboxMessage, ShopItem,
    PlacedMarkerBet, PlacedEventBet, Notification,
)
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
    description='Get a single video by ID, or delete it (DELETE: owner only)',
    summary='Get or delete video',
)
@api_view(['GET', 'DELETE'])
@permission_classes([permissions.AllowAny])
def get_video(request, video_id):
    """Get a single video by ID, or delete if requester is the creator."""
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if video.creator_id != request.user.id:
            return Response({'error': 'You can only delete your own videos'}, status=status.HTTP_403_FORBIDDEN)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # GET
    # Check if user is owner to show bet markers
    is_owner = request.user.is_authenticated and request.user.id == video.creator.id
    # Check if preview mode is requested
    is_preview = request.query_params.get('preview', 'false').lower() == 'true'
    # Show bet markers if owner or in preview mode
    show_bet_markers = is_owner or is_preview
    serializer = VideoSerializer(video, context={'request': request, 'is_owner': show_bet_markers})
    return Response(serializer.data, status=status.HTTP_200_OK)


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
            marker = BetMarker.objects.create(
                video=video,
                timestamp=float(marker_data.get('timestamp', 0)),
                question=marker_data.get('question', ''),
                option1_text=options[0].get('text', 'Yes') if len(options) > 0 else '',
                option2_text=options[1].get('text', 'No') if len(options) > 1 else '',
                option1_odds=float(options[0].get('odds', 2.0)) if len(options) > 0 else 2.0,
                option2_odds=float(options[1].get('odds', 2.0)) if len(options) > 1 else 2.0,
            )
            for i, opt in enumerate(options):
                BetMarkerOption.objects.create(
                    marker=marker,
                    text=opt.get('text', 'Option'),
                    odds=float(opt.get('odds', 2.0)),
                    order=i,
                )
        
        # Return created video with bet markers
        video_serializer = VideoSerializer(video, context={'request': request, 'is_owner': True})
        return Response(video_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Betting ----------

@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT},
    description='Place a bet on a video bet marker',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def place_marker_bet(request):
    """Place bet on a bet marker (timestamp-based)"""
    marker_id = request.data.get('marker_id')
    option_id = request.data.get('option_id')
    amount = request.data.get('amount')
    if not all([marker_id, option_id, amount]):
        return Response(
            {'error': 'marker_id, option_id and amount are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount must be positive')
    except (TypeError, ValueError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user.balance < amount:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        marker = BetMarker.objects.get(pk=marker_id)
        option = BetMarkerOption.objects.get(pk=option_id, marker=marker)
    except (BetMarker.DoesNotExist, BetMarkerOption.DoesNotExist):
        return Response({'error': 'Marker or option not found'}, status=status.HTTP_404_NOT_FOUND)
    bet = PlacedMarkerBet.objects.create(user=user, marker=marker, option=option, amount=amount)
    user.balance -= amount
    user.save(update_fields=['balance'])
    marker.total_pool += amount
    marker.participants += 1
    marker.save(update_fields=['total_pool', 'participants'])
    return Response({
        'message': 'Bet placed',
        'balance': float(user.balance),
        'bet_id': bet.id,
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT},
    description='Place a bet on a live bet event',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def place_event_bet(request):
    """Place bet on a live bet event"""
    event_id = request.data.get('event_id')
    option_id = request.data.get('option_id')
    amount = request.data.get('amount')
    if not all([event_id, option_id, amount]):
        return Response(
            {'error': 'event_id, option_id and amount are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount must be positive')
    except (TypeError, ValueError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user.balance < amount:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        event = BetEvent.objects.get(pk=event_id, status='open')
        option = BetEventOption.objects.get(pk=option_id, event=event)
    except (BetEvent.DoesNotExist, BetEventOption.DoesNotExist):
        return Response({'error': 'Event or option not found or event is closed'}, status=status.HTTP_404_NOT_FOUND)
    from django.utils import timezone
    if event.expires_at and event.expires_at <= timezone.now():
        return Response({'error': 'Betting has closed'}, status=status.HTTP_400_BAD_REQUEST)
    bet = PlacedEventBet.objects.create(user=user, event=event, option=option, amount=amount)
    user.balance -= amount
    user.save(update_fields=['balance'])
    event.total_pool += amount
    event.participants += 1
    event.save(update_fields=['total_pool', 'participants'])
    return Response({
        'message': 'Bet placed',
        'balance': float(user.balance),
        'bet_id': bet.id,
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT},
    description='Resolve a bet marker and pay out winners (creator only)',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resolve_marker_bet(request):
    """Resolve a marker: set winning option and pay out winners"""
    marker_id = request.data.get('marker_id')
    winning_option_id = request.data.get('winning_option_id')
    if not marker_id or not winning_option_id:
        return Response(
            {'error': 'marker_id and winning_option_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        marker = BetMarker.objects.get(pk=marker_id)
    except BetMarker.DoesNotExist:
        return Response({'error': 'Marker not found'}, status=status.HTTP_404_NOT_FOUND)
    if marker.video.creator_id != request.user.id:
        return Response({'error': 'Only the video creator can resolve'}, status=status.HTTP_403_FORBIDDEN)
    try:
        winning_option = BetMarkerOption.objects.get(pk=winning_option_id, marker=marker)
    except BetMarkerOption.DoesNotExist:
        return Response({'error': 'Winning option not found'}, status=status.HTTP_404_NOT_FOUND)
    for bet in PlacedMarkerBet.objects.filter(marker=marker, resolved=False):
        bet.resolved = True
        if bet.option_id == int(winning_option_id):
            payout = float(bet.amount * bet.option.odds)
            bet.payout = payout
            bet.user.balance += payout
            bet.user.save(update_fields=['balance'])
            Notification.objects.create(
                user=bet.user,
                notif_type='bet_win',
                message=f'You won ${payout:.2f} on "{marker.question}"',
                link=f'/watch/{marker.video_id}',
            )
        else:
            Notification.objects.create(
                user=bet.user,
                notif_type='bet_loss',
                message=f'You lost ${bet.amount} on "{marker.question}"',
                link=f'/watch/{marker.video_id}',
            )
        bet.save()
    return Response({'message': 'Marker resolved'}, status=status.HTTP_200_OK)


@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT},
    description='Resolve a live bet event and pay out winners (creator only)',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resolve_event_bet(request):
    """Resolve a live bet event"""
    event_id = request.data.get('event_id')
    winning_option_id = request.data.get('winning_option_id')
    if not event_id or not winning_option_id:
        return Response(
            {'error': 'event_id and winning_option_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        event = BetEvent.objects.get(pk=event_id)
    except BetEvent.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    if event.creator_id != request.user.id:
        return Response({'error': 'Only the event creator can resolve'}, status=status.HTTP_403_FORBIDDEN)
    try:
        winning_option = BetEventOption.objects.get(pk=winning_option_id, event=event)
    except BetEventOption.DoesNotExist:
        return Response({'error': 'Winning option not found'}, status=status.HTTP_404_NOT_FOUND)
    event.status = 'resolved'
    event.winning_option = winning_option
    event.save(update_fields=['status', 'winning_option'])
    for bet in PlacedEventBet.objects.filter(event=event, resolved=False):
        bet.resolved = True
        if bet.option_id == int(winning_option_id):
            payout = float(bet.amount * bet.option.odds)
            bet.payout = payout
            bet.user.balance += payout
            bet.user.save(update_fields=['balance'])
            Notification.objects.create(
                user=bet.user,
                notif_type='bet_win',
                message=f'You won ${payout:.2f} on "{event.question}"',
                link=event.video_id and f'/watch/{event.video_id}' or '',
            )
        else:
            Notification.objects.create(
                user=bet.user,
                notif_type='bet_loss',
                message=f'You lost ${bet.amount} on "{event.question}"',
                link=event.video_id and f'/watch/{event.video_id}' or '',
            )
        bet.save()
    return Response({'message': 'Event resolved'}, status=status.HTTP_200_OK)


@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses={201: OpenApiTypes.OBJECT},
    description='Create a live bet event (e.g. during stream)',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_bet_event(request):
    """Create a live bet event (for live stream or video)"""
    from django.utils import timezone
    from datetime import timedelta
    video_id = request.data.get('video_id')
    question = request.data.get('question')
    options = request.data.get('options')  # [{"text": "...", "odds": 1.5}, ...]
    duration_seconds = request.data.get('duration_seconds', 60)
    if not question or not options or len(options) < 2:
        return Response(
            {'error': 'question and at least 2 options are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    video = None
    if video_id:
        try:
            video = Video.objects.get(pk=video_id)
            if video.creator_id != request.user.id:
                return Response({'error': 'Not your video'}, status=status.HTTP_403_FORBIDDEN)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
    expires_at = timezone.now() + timedelta(seconds=int(duration_seconds))
    event = BetEvent.objects.create(
        video=video,
        creator=request.user,
        question=question,
        expires_at=expires_at,
        status='open',
    )
    for i, opt in enumerate(options):
        BetEventOption.objects.create(
            event=event,
            text=opt.get('text', 'Option'),
            odds=float(opt.get('odds', 2.0)),
            order=i,
        )
    options_out = list(event.options_list.order_by('order', 'id').values('id', 'text', 'odds'))
    return Response({
        'id': event.id,
        'question': event.question,
        'options': [{'id': o['id'], 'text': o['text'], 'odds': float(o['odds'])} for o in options_out],
        'expires_at': event.expires_at.isoformat(),
        'expiresAt': int(event.expires_at.timestamp() * 1000),
    }, status=status.HTTP_201_CREATED)


# ---------- Notifications ----------

@extend_schema(
    responses={200: OpenApiTypes.OBJECT},
    description='List notifications for current user',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_notifications(request):
    """List user notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    data = [{
        'id': n.id,
        'message': n.message,
        'type': n.notif_type,
        'timestamp': int(n.created_at.timestamp() * 1000),
        'is_read': n.is_read,
        'link': n.link or '',
    } for n in notifications]
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: OpenApiTypes.OBJECT},
    description='Mark a notification as read',
)
@api_view(['PATCH', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        n = Notification.objects.get(pk=notification_id, user=request.user)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return Response({'message': 'Marked as read'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# ---------- Feed ----------

@extend_schema(
    responses={200: VideoSerializer(many=True)},
    description='Get feed videos (home/feed). Returns most recent videos.',
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def feed_videos(request):
    """List videos for feed (most recent first)"""
    videos = Video.objects.all().order_by('-created_at')[:100]
    serializer = VideoSerializer(videos, many=True, context={'request': request, 'is_owner': False})
    return Response(serializer.data, status=status.HTTP_200_OK)

