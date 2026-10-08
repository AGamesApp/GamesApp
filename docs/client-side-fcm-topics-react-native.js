/**
 * FCM Topics Implementation - React Native
 * 
 * This replaces individual device token registration with topic subscription.
 * All users automatically subscribe to 'all_users' topic.
 */

import messaging from '@react-native-firebase/messaging';
import { Platform } from 'react-native';
import DeviceInfo from 'react-native-device-info';
import axios from 'axios';

const API_URL = 'https://games.agames.cv/api';
const TOPIC_NAME = 'all_users';

/**
 * Setup push notifications with FCM Topic subscription
 * Call this when app initializes
 */
export const setupPushNotifications = async () => {
  try {
    // 1. Request notification permission
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (!enabled) {
      console.log('Notification permission denied');
      return false;
    }

    console.log('✓ Notification permission granted');

    // 2. Get device token (still needed for tracking)
    const fcmToken = await messaging().getToken();
    console.log('✓ FCM Token obtained:', fcmToken.substring(0, 20) + '...');

    // 3. Subscribe to 'all_users' topic
    await messaging().subscribeToTopic(TOPIC_NAME);
    console.log(`✓ Subscribed to topic: ${TOPIC_NAME}`);

    // 4. Register token with backend (for analytics/tracking)
    await registerDeviceToken(fcmToken);

    // 5. Setup notification handlers
    setupNotificationHandlers();

    return true;
  } catch (error) {
    console.error('Error setting up notifications:', error);
    return false;
  }
};

/**
 * Register device token with backend
 * This is still useful for analytics and user-specific notifications
 */
const registerDeviceToken = async (token) => {
  try {
    const deviceId = await DeviceInfo.getUniqueId();
    
    const response = await axios.post(`${API_URL}/device-tokens/`, {
      token: token,
      platform: Platform.OS,
      device_id: deviceId,
      subscribed_to_all_users: true, // New field to track topic subscription
    });

    console.log('✓ Device registered with backend');
    return response.data;
  } catch (error) {
    console.error('Failed to register device:', error);
    throw error;
  }
};

/**
 * Setup notification event handlers
 */
const setupNotificationHandlers = () => {
  // Handle notifications when app is in foreground
  messaging().onMessage(async (remoteMessage) => {
    console.log('Notification received (foreground):', remoteMessage);
    
    // Show local notification or update UI
    // You can use a library like react-native-push-notification
    displayNotification(remoteMessage);
  });

  // Handle notification tap when app is in background
  messaging().onNotificationOpenedApp((remoteMessage) => {
    console.log('Notification opened app from background:', remoteMessage);
    handleNotificationNavigation(remoteMessage);
  });

  // Handle notification tap when app was completely quit
  messaging()
    .getInitialNotification()
    .then((remoteMessage) => {
      if (remoteMessage) {
        console.log('Notification opened app from quit state:', remoteMessage);
        handleNotificationNavigation(remoteMessage);
      }
    });

  // Handle background messages
  messaging().setBackgroundMessageHandler(async (remoteMessage) => {
    console.log('Message handled in background:', remoteMessage);
  });
};

/**
 * Display notification in foreground
 */
const displayNotification = (remoteMessage) => {
  // Implement your notification display logic
  // Example using Alert or custom notification component
  if (remoteMessage.notification) {
    const { title, body } = remoteMessage.notification;
    console.log(`Notification: ${title} - ${body}`);
    // Show notification banner/alert
  }
};

/**
 * Handle navigation based on notification data
 */
const handleNotificationNavigation = (remoteMessage) => {
  // Navigate based on notification data
  const { data } = remoteMessage;
  
  if (data?.screen) {
    // Navigate to specific screen
    // Example: navigation.navigate(data.screen, { id: data.id });
    console.log('Navigate to:', data.screen);
  }
};

/**
 * Unsubscribe from topic (e.g., when user logs out or disables notifications)
 */
export const unsubscribeFromNotifications = async () => {
  try {
    await messaging().unsubscribeFromTopic(TOPIC_NAME);
    console.log(`✓ Unsubscribed from topic: ${TOPIC_NAME}`);
    
    // Optionally update backend
    await axios.post(`${API_URL}/device-tokens/unsubscribe/`, {
      topic: TOPIC_NAME,
    });
    
    return true;
  } catch (error) {
    console.error('Error unsubscribing:', error);
    return false;
  }
};

/**
 * Check if device is subscribed to topic
 */
export const isSubscribedToTopic = async () => {
  try {
    // Note: FCM doesn't provide a direct API to check subscription
    // You'll need to track this in your app state or backend
    // This is a placeholder for your implementation
    return true;
  } catch (error) {
    console.error('Error checking subscription:', error);
    return false;
  }
};

// Usage in your App.js or index.js:
/*
import { setupPushNotifications } from './services/notifications';

const App = () => {
  useEffect(() => {
    setupPushNotifications();
  }, []);

  return (
    // Your app components
  );
};
*/
