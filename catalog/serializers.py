from rest_framework import serializers
from .models import CartiCatalog, SheetTab, SongMetadata, ArtMedia, Interview, FitPic, SocialMedia, SongVote

class SheetTabSerializer(serializers.ModelSerializer):
    """
    TODO: Add any computed fields you want to include in the API response
    Example: song_count, icon, description
    """
    class Meta:
        model = SheetTab
        fields = ['id', 'name', 'sheet_id']
        # TODO: Add any additional computed fields here

class SongMetadataSerializer(serializers.ModelSerializer):
    """
    TODO: Include related fields if needed
    """
    sheet_tab = SheetTabSerializer(read_only=True)
    
    class Meta:
        model = SongMetadata
        fields = ['sheet_tab', 'subsection']

class CartiCatalogSerializer(serializers.ModelSerializer):
    """
    Main song serializer
    TODO: 
    1. Add computed properties from your model (producer, featuring, etc.)
    2. Include related metadata
    3. Add preview_url handling
    4. Add any calculated fields like vote counts
    """
    metadata = SongMetadataSerializer(read_only=True)
    # TODO: Add these computed fields from your model
    # producer = serializers.ReadOnlyField()
    # featuring = serializers.ReadOnlyField()
    # has_playable_link = serializers.ReadOnlyField()
    # album_track_number = serializers.ReadOnlyField()
    # album_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CartiCatalog
        fields = [
            'id', 'name', 'era', 'notes', 'track_length', 'leak_date', 
            'file_date', 'type', 'available_length', 'quality', 'links', 
            'primary_link', 'preview_url', 'metadata'
        ]
        # TODO: Add computed fields to this list

class ArtMediaSerializer(serializers.ModelSerializer):
    """
    TODO: Add thumbnail property, handle image URLs properly
    """
    class Meta:
        model = ArtMedia
        fields = ['id', 'name', 'era', 'notes', 'image_url', 'media_type', 'was_used', 'links']

class InterviewSerializer(serializers.ModelSerializer):
    """
    TODO: Add thumbnail property for video interviews
    """
    class Meta:
        model = Interview
        fields = [
            'id', 'era', 'date', 'outlet', 'subject_matter', 'special_notes', 
            'interview_type', 'available', 'archived_link', 'source_links'
        ]

class FitPicSerializer(serializers.ModelSerializer):
    """
    TODO: Add thumbnail property, handle image URLs
    """
    class Meta:
        model = FitPic
        fields = [
            'id', 'era', 'caption', 'notes', 'photographer', 'release_date', 
            'pic_type', 'portion', 'quality', 'image_url', 'source_links'
        ]

class SocialMediaSerializer(serializers.ModelSerializer):
    """
    TODO: Add thumbnail/icon for different platforms
    """
    class Meta:
        model = SocialMedia
        fields = [
            'id', 'era', 'username', 'notes', 'platform', 'last_post', 
            'still_used', 'link'
        ]

class SongVoteSerializer(serializers.ModelSerializer):
    """
    TODO: Handle vote creation/updates, add validation for duplicate votes
    """
    class Meta:
        model = SongVote
        fields = ['id', 'song', 'vote_type', 'created_at']
        read_only_fields = ['id', 'created_at']

# TODO: Create list serializers for paginated responses
# TODO: Create nested serializers for complex relationships
# TODO: Add validation methods for user input
# TODO: Add custom fields for computed properties 