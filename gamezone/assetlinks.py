"""
Android App Links verification endpoint.
Returns assetlinks.json for app deep linking.
"""
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def assetlinks_json(request):
    """Return Android assetlinks.json for app verification."""
    sha256_fingerprints = [
        "50:11:B2:A8:71:A9:F4:B5:DF:35:C8:40:41:62:09:18:9D:34:56:A9:B5:92:E9:8E:62:7C:9E:C4:50:24:D4:B0",
        "BE:2E:BE:09:E6:E5:30:5B:E7:E3:11:22:7D:EB:8D:74:28:B8:6B:62:C6:9D:D9:37:9D:21:79:B0:C6:DB:CD:D9"
    ]

    package_name = getattr(settings, 'ANDROID_PACKAGE_NAME', 'com.agames.zone')
    packages = [package_name]
    if "com.agames.play" not in packages:
        packages.append("com.agames.play")

    data = [
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": pkg,
                "sha256_cert_fingerprints": sha256_fingerprints
            }
        }
        for pkg in packages
    ]
    
    return JsonResponse(data, safe=False)


def privacy_policy(request):
    """Display privacy policy page."""
    return render(request, 'privacy_policy.html')
