#!/usr/bin/env python3
"""
Quick test script to send a notification to 'all_users' topic
Runs standalone without needing Django shell
"""

import firebase_admin
from firebase_admin import credentials, messaging
from datetime import datetime
import json

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')

# Check if already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Prepare the message
now = datetime.utcnow().isoformat()
message = messaging.Message(
    notification=messaging.Notification(
        title='📣 Test: Backend -> all_users',
        body=f'Test sent at {now}'
    ),
    data={
        'env': 'manual',
        'purpose': 'user_requested_test',
        'timestamp': now,
        'notification_type': 'test'
    },
    topic='all_users'
)

# Send the message
try:
    response = messaging.send(message)
    print('✅ SUCCESS!')
    print('─' * 60)
    print(f'Message ID: {response}')
    print(f'Topic: all_users')
    print(f'Title: 📣 Test: Backend -> all_users')
    print(f'Body: Test sent at {now}')
    print(f'Timestamp: {now}')
    print('─' * 60)
    print('\n✅ Notification sent successfully to FCM!')
    print('📱 If any devices are subscribed to "all_users" topic, they will receive it.')
    print('🔍 Check Firebase Console: https://console.firebase.google.com/project/agames-21123/messaging')
except Exception as e:
    print('❌ FAILED!')
    print('─' * 60)
    print(f'Error: {str(e)}')
    print('─' * 60)
