"""
Custom template to disable/hide Django Allauth default login pages.
This project uses API-based authentication with tokens.
"""
from django.http import JsonResponse
from django.views import View


class DisableAllauthWebUI(View):
    """
    Return JSON response for Allauth web pages since we use API-based auth.
    """
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'message': 'This project uses API-based authentication',
            'api_endpoint': '/api/users/auth/google/',
            'documentation': 'Send POST request with id_token from Google Sign-In',
            'example': {
                'method': 'POST',
                'url': f'{request.scheme}://{request.get_host()}/api/users/auth/google/',
                'body': {
                    'id_token': 'YOUR_GOOGLE_ID_TOKEN'
                },
                'response': {
                    'token': 'your_api_token',
                    'user': {
                        'email': 'user@example.com',
                        'username': 'user'
                    }
                }
            }
        }, json_dumps_params={'indent': 2})
