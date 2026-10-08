/**
 * FCM Topics Implementation - Flutter
 * 
 * This replaces individual device token registration with topic subscription.
 * All users automatically subscribe to 'all_users' topic.
 */

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:device_info_plus/device_info_plus.dart';

const String API_URL = 'https://games.agames.cv/api';
const String TOPIC_NAME = 'all_users';

class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  
  /// Setup push notifications with FCM Topic subscription
  /// Call this in your main.dart or app initialization
  Future<bool> setupPushNotifications() async {
    try {
      // 1. Request notification permission
      NotificationSettings settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
        provisional: false,
      );

      if (settings.authorizationStatus != AuthorizationStatus.authorized &&
          settings.authorizationStatus != AuthorizationStatus.provisional) {
        debugPrint('Notification permission denied');
        return false;
      }

      debugPrint('✓ Notification permission granted');

      // 2. Get device token (still needed for tracking)
      String? fcmToken = await _messaging.getToken();
      if (fcmToken == null) {
        debugPrint('Failed to get FCM token');
        return false;
      }

      debugPrint('✓ FCM Token obtained: ${fcmToken.substring(0, 20)}...');

      // 3. Subscribe to 'all_users' topic
      await _messaging.subscribeToTopic(TOPIC_NAME);
      debugPrint('✓ Subscribed to topic: $TOPIC_NAME');

      // 4. Register token with backend
      await _registerDeviceToken(fcmToken);

      // 5. Setup notification handlers
      _setupNotificationHandlers();

      // 6. Listen for token refresh
      _messaging.onTokenRefresh.listen((newToken) {
        debugPrint('Token refreshed: ${newToken.substring(0, 20)}...');
        _registerDeviceToken(newToken);
      });

      return true;
    } catch (error) {
      debugPrint('Error setting up notifications: $error');
      return false;
    }
  }

  /// Register device token with backend
  Future<void> _registerDeviceToken(String token) async {
    try {
      final deviceInfo = DeviceInfoPlugin();
      String deviceId;

      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        deviceId = androidInfo.id;
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        deviceId = iosInfo.identifierForVendor ?? '';
      } else {
        deviceId = 'unknown';
      }

      final response = await http.post(
        Uri.parse('$API_URL/device-tokens/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'token': token,
          'platform': Platform.isIOS ? 'ios' : 'android',
          'device_id': deviceId,
          'subscribed_to_all_users': true,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        debugPrint('✓ Device registered with backend');
      } else {
        debugPrint('Failed to register device: ${response.statusCode}');
      }
    } catch (error) {
      debugPrint('Error registering device: $error');
      rethrow;
    }
  }

  /// Setup notification event handlers
  void _setupNotificationHandlers() {
    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      debugPrint('Notification received (foreground): ${message.messageId}');
      
      if (message.notification != null) {
        _displayNotification(message);
      }
    });

    // Handle notification tap when app is in background
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      debugPrint('Notification opened app from background: ${message.messageId}');
      _handleNotificationNavigation(message);
    });

    // Handle notification tap when app was completely quit
    _messaging.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        debugPrint('Notification opened app from quit state: ${message.messageId}');
        _handleNotificationNavigation(message);
      }
    });
  }

  /// Display notification in foreground
  void _displayNotification(RemoteMessage message) {
    final notification = message.notification;
    if (notification != null) {
      debugPrint('Notification: ${notification.title} - ${notification.body}');
      
      // Show notification using flutter_local_notifications or similar
      // Example:
      // await localNotifications.show(
      //   notification.hashCode,
      //   notification.title,
      //   notification.body,
      //   platformChannelSpecifics,
      // );
    }
  }

  /// Handle navigation based on notification data
  void _handleNotificationNavigation(RemoteMessage message) {
    final data = message.data;
    
    if (data.containsKey('screen')) {
      debugPrint('Navigate to: ${data['screen']}');
      // Implement your navigation logic
      // Example: navigatorKey.currentState?.pushNamed(data['screen']);
    }
  }

  /// Unsubscribe from topic
  Future<bool> unsubscribeFromNotifications() async {
    try {
      await _messaging.unsubscribeFromTopic(TOPIC_NAME);
      debugPrint('✓ Unsubscribed from topic: $TOPIC_NAME');
      
      // Optionally update backend
      await http.post(
        Uri.parse('$API_URL/device-tokens/unsubscribe/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'topic': TOPIC_NAME}),
      );
      
      return true;
    } catch (error) {
      debugPrint('Error unsubscribing: $error');
      return false;
    }
  }

  /// Delete FCM token (when user logs out completely)
  Future<void> deleteToken() async {
    try {
      await _messaging.deleteToken();
      debugPrint('✓ FCM token deleted');
    } catch (error) {
      debugPrint('Error deleting token: $error');
    }
  }
}

// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint('Handling background message: ${message.messageId}');
  // Handle background message
}

/// Usage in main.dart:
/*
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Set background message handler
  FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  
  // Setup notifications
  final notificationService = NotificationService();
  await notificationService.setupPushNotifications();
  
  runApp(MyApp());
}
*/
