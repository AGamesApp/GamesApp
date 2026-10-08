from rest_framework import serializers
from .models import Page


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'content', 'updated_at']
        read_only_fields = ['updated_at']
