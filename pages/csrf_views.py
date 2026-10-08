"""
Custom views to handle CSRF issues properly
"""
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFSafeLandingView(TemplateView):
    """
    Landing page view with proper CSRF handling.
    This ensures CSRF cookies are set properly without causing warnings.
    """
    template_name = 'pages/landing.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests with proper CSRF cookie setup"""
        response = super().get(request, *args, **kwargs)
        return response