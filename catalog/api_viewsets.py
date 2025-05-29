from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .models import CartiCatalog, SheetTab, ArtMedia, Interview, FitPic, SocialMedia, SongVote
from .serializers import (
    CartiCatalogSerializer, SheetTabSerializer, ArtMediaSerializer,
    InterviewSerializer, FitPicSerializer, SocialMediaSerializer, SongVoteSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    """
    TODO: Customize pagination settings
    - Set page_size based on your needs
    - Add page_size_query_param for flexible pagination
    - Set max_page_size to prevent abuse
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CartiCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Main songs API endpoint
    TODO:
    1. Add custom filtering logic
    2. Implement search functionality 
    3. Add custom actions for specific queries (recent, popular, etc.)
    4. Add voting endpoints
    5. Handle preview file serving
    """
    queryset = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab')
    serializer_class = CartiCatalogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # TODO: Configure these based on your model fields
    filterset_fields = ['era', 'type', 'quality']  # Add more fields as needed
    search_fields = ['name', 'notes']  # Add more searchable fields
    ordering_fields = ['name', 'era', 'leak_date', 'id']
    ordering = ['name']

    def get_queryset(self):
        """
        TODO: Add custom filtering logic
        - Filter by sheet_tab parameter
        - Filter by producer, features
        - Add any complex filtering logic
        """
        queryset = super().get_queryset()
        
        # TODO: Add sheet_tab filtering
        # sheet_tab_id = self.request.query_params.get('sheet_tab', None)
        # if sheet_tab_id:
        #     queryset = queryset.filter(Q(metadata__sheet_tab_id=sheet_tab_id) | Q(categories__sheet_tab_id=sheet_tab_id)).distinct()
        
        return queryset

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        TODO: Implement recent songs endpoint
        - Get last 20 songs by ID or date
        - Return simplified data for homepage
        """
        # recent_songs = self.get_queryset()[:20]
        # serializer = self.get_serializer(recent_songs, many=True)
        # return Response(serializer.data)
        return Response({'message': 'TODO: Implement recent songs'})

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """
        TODO: Implement voting endpoint
        - Handle like/dislike votes
        - Prevent duplicate votes
        - Return updated vote counts
        """
        return Response({'message': 'TODO: Implement voting'})

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        TODO: Implement similar songs endpoint
        - Find songs by same producer
        - Find songs from same era
        - Use any ML/similarity logic you want
        """
        return Response({'message': 'TODO: Implement similar songs'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Implement stats endpoint
        - Total songs count
        - Songs by era
        - Songs by quality/type
        - Sheet tab counts
        """
        # Count distinct eras (excluding null/empty)
        distinct_eras = CartiCatalog.objects.exclude(
            Q(era__isnull=True) | Q(era='')
        ).values('era').distinct().count()
        
        # Total songs count
        total_songs = CartiCatalog.objects.count()
        
        return Response({
            'distinct_eras': distinct_eras,
            'total_songs': total_songs
        })

class SheetTabViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Sheet tabs API endpoint
    TODO:
    1. Add song counts to each tab
    2. Add custom actions for tab-specific queries
    """
    queryset = SheetTab.objects.all()
    serializer_class = SheetTabSerializer

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """
        TODO: Get all songs for a specific sheet tab
        - Include both primary and secondary categorizations
        - Add pagination
        """
        return Response({'message': 'TODO: Implement tab songs'})

class ArtMediaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Art media API endpoint
    TODO:
    1. Add image serving/thumbnails
    2. Filter by era, media type
    3. Add search functionality
    """
    queryset = ArtMedia.objects.all()
    serializer_class = ArtMediaSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # TODO: Configure filtering
    filterset_fields = ['era', 'media_type', 'was_used']
    search_fields = ['name', 'notes']
    ordering_fields = ['name', 'era']
    ordering = ['-id']

class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Interviews API endpoint  
    TODO:
    1. Add video thumbnails
    2. Filter by era, outlet, interview type
    3. Handle archived vs live links
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # TODO: Configure filtering
    filterset_fields = ['era', 'outlet', 'interview_type', 'available']
    search_fields = ['outlet', 'subject_matter', 'special_notes']
    ordering_fields = ['date', 'era']
    ordering = ['-date']

class FitPicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Fit pics API endpoint
    TODO:
    1. Add image thumbnails
    2. Filter by era, photographer, type
    3. Handle image quality/portions
    """
    queryset = FitPic.objects.all()
    serializer_class = FitPicSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # TODO: Configure filtering
    filterset_fields = ['era', 'photographer', 'pic_type', 'quality']
    search_fields = ['caption', 'notes', 'photographer']
    ordering_fields = ['release_date', 'era']
    ordering = ['-id']

class SocialMediaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Social media API endpoint
    TODO:
    1. Add platform icons
    2. Filter by platform, era
    3. Handle active vs inactive accounts
    """
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # TODO: Configure filtering
    filterset_fields = ['era', 'platform', 'still_used']
    search_fields = ['username', 'notes']

# TODO: Add authentication/permissions if needed
# TODO: Add custom exception handling
# TODO: Add caching for expensive queries
# TODO: Add API versioning
# TODO: Add rate limiting 