from rest_framework import serializers
from .models import SupportMessage


class SupportMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating support messages"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    # Make name and email optional in serializer (they'll be auto-filled for authenticated users)
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    
    # Make subject and message explicitly required
    subject = serializers.CharField(max_length=300, required=True, allow_blank=False, 
                                    error_messages={'required': 'Subject is required.', 
                                                   'blank': 'Subject cannot be blank.'})
    message = serializers.CharField(required=True, allow_blank=False,
                                    error_messages={'required': 'Message is required.',
                                                   'blank': 'Message cannot be blank.'})
    
    class Meta:
        model = SupportMessage
        fields = [
            'id',
            'user',
            'user_email',
            'name',
            'email',
            'subject',
            'message',
            'status',
            'is_reviewed',
            'reviewed_at',
            'reviewed_by',
            'reviewed_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'is_reviewed',
            'reviewed_at',
            'reviewed_by',
            'created_at',
            'updated_at',
        ]
    
    def validate(self, data):
        """Validate that name and email are provided for anonymous users"""
        request = self.context.get('request')
        
        # If user is not authenticated, name and email are required
        if not (request and request.user.is_authenticated):
            if not data.get('name'):
                raise serializers.ValidationError({'name': 'This field is required for anonymous submissions.'})
            if not data.get('email'):
                raise serializers.ValidationError({'email': 'This field is required for anonymous submissions.'})
        
        return data
    
    def create(self, validated_data):
        # Automatically assign the authenticated user if available
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            # Auto-fill name and email from user if not provided
            if not validated_data.get('name'):
                validated_data['name'] = request.user.get_full_name() or request.user.username
            if not validated_data.get('email'):
                validated_data['email'] = request.user.email
        
        return super().create(validated_data)


class SupportMessageDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for admin view"""
    
    user_details = serializers.SerializerMethodField()
    reviewed_by_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportMessage
        fields = '__all__'
    
    def get_user_details(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'full_name': obj.user.get_full_name(),
            }
        return None
    
    def get_reviewed_by_details(self, obj):
        if obj.reviewed_by:
            return {
                'id': obj.reviewed_by.id,
                'username': obj.reviewed_by.username,
                'email': obj.reviewed_by.email,
            }
        return None
