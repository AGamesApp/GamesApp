#!/usr/bin/env python
"""
Test script to verify new AppSettings fields
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import AppSettings
from games.serializers import AppSettingsSerializer
from customadmin.forms import AppSettingsForm

def test_model_fields():
    """Test that model has new fields"""
    print("\n" + "="*70)
    print("TEST 1: Model Fields")
    print("="*70)
    
    settings, created = AppSettings.objects.get_or_create(pk=1)
    
    # Check new fields exist
    print(f"✓ show_popup: {settings.show_popup}")
    print(f"✓ popup_title: {settings.popup_title}")
    print(f"✓ popup_description: {settings.popup_description}")
    print(f"✓ popup_link: {settings.popup_link}")
    
    # Update fields
    settings.show_popup = True
    settings.popup_title = "Test Title"
    settings.popup_description = "Test Description"
    settings.popup_link = "https://example.com"
    settings.save()
    
    print("\n✅ Model fields working correctly!")
    return True

def test_serializer():
    """Test that serializer includes new fields"""
    print("\n" + "="*70)
    print("TEST 2: Serializer Fields")
    print("="*70)
    
    settings = AppSettings.objects.get(pk=1)
    serializer = AppSettingsSerializer(settings)
    data = serializer.data
    
    print(f"Serializer fields: {list(data.keys())}")
    
    required_fields = ['show_popup', 'popup_title', 'popup_description', 'popup_link']
    for field in required_fields:
        if field in data:
            print(f"✓ {field}: {data[field]}")
        else:
            print(f"✗ {field}: MISSING!")
            return False
    
    print("\n✅ Serializer working correctly!")
    return True

def test_form():
    """Test that form includes new fields"""
    print("\n" + "="*70)
    print("TEST 3: Form Fields")
    print("="*70)
    
    form = AppSettingsForm()
    form_fields = list(form.fields.keys())
    
    print(f"Form fields: {form_fields}")
    
    required_fields = ['show_popup', 'popup_title', 'popup_description', 'popup_link']
    for field in required_fields:
        if field in form_fields:
            print(f"✓ {field}: Present")
        else:
            print(f"✗ {field}: MISSING!")
            return False
    
    print("\n✅ Form working correctly!")
    return True

def test_api_response():
    """Test API endpoint response"""
    print("\n" + "="*70)
    print("TEST 4: API Response")
    print("="*70)
    
    from django.test import Client
    
    client = Client()
    response = client.get('/api/app_details/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"API Response: {data}")
        
        required_fields = ['show_popup', 'popup_title', 'popup_description', 'popup_link']
        for field in required_fields:
            if field in data:
                print(f"✓ {field}: {data[field]}")
            else:
                print(f"✗ {field}: MISSING!")
                return False
        
        print("\n✅ API working correctly!")
        return True
    else:
        print(f"✗ API returned status {response.status_code}")
        return False

if __name__ == '__main__':
    results = []
    
    try:
        results.append(("Model Fields", test_model_fields()))
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        results.append(("Model Fields", False))
    
    try:
        results.append(("Serializer", test_serializer()))
    except Exception as e:
        print(f"✗ Serializer test failed: {e}")
        results.append(("Serializer", False))
    
    try:
        results.append(("Form", test_form()))
    except Exception as e:
        print(f"✗ Form test failed: {e}")
        results.append(("Form", False))
    
    try:
        results.append(("API Response", test_api_response()))
    except Exception as e:
        print(f"✗ API test failed: {e}")
        results.append(("API Response", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("="*70))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*70)
