from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from .models import Page
from .serializers import PageSerializer


class PageDetailView(RetrieveAPIView):
    """
    API endpoint to retrieve page content by title.
    Example: GET /api/pages/about/
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'title'
