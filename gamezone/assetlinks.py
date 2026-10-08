"""
Android App Links verification endpoint.
Returns assetlinks.json for app deep linking.
"""
from django.http import JsonResponse
from django.shortcuts import render


def assetlinks_json(request):
    """Return Android assetlinks.json for app verification."""
    data = [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.agames.play",
            "sha256_cert_fingerprints": [
                "A8:55:08:61:E9:BE:BE:9F:12:4B:D6:67:98:83:F9:72:C5:06:CB:82:6D:67:06:82:B6:00:E8:D9:FC:E9:A1:2C",
                "BE:2E:BE:09:E6:E5:30:5B:E7:E3:11:22:7D:EB:8D:74:28:B8:6B:62:C6:9D:D9:37:9D:21:79:B0:C6:DB:CD:D9",
                "C4:60:F8:B3:E7:3D:05:01:C6:B6:7D:9D:DD:94:BC:AF:37:8E:76:D1:E4:3C:F9:14:A8:21:97:5A:DA:39:06:A6"
            ]
        }
    }]
    
    return JsonResponse(data, safe=False)


def privacy_policy(request):
    """Display privacy policy page."""
    return render(request, 'privacy_policy.html')
