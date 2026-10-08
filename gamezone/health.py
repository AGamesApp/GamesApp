from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
import os


@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring services.
    Returns status of database, cache, and file system.
    """
    status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['checks']['database'] = 'ok'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['checks']['database'] = f'error: {str(e)}'
    
    # Check cache (Redis)
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['checks']['cache'] = 'ok'
        else:
            status['status'] = 'unhealthy'
            status['checks']['cache'] = 'error: cache not working'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['checks']['cache'] = f'error: {str(e)}'
    
    # Check file system (media directory writable)
    try:
        from django.conf import settings
        test_file = os.path.join(settings.MEDIA_ROOT, '.health_check')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        status['checks']['filesystem'] = 'ok'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['checks']['filesystem'] = f'error: {str(e)}'
    
    # Return appropriate HTTP status code
    http_status = 200 if status['status'] == 'healthy' else 503
    
    return JsonResponse(status, status=http_status)
