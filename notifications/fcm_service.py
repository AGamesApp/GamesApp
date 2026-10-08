"""
Firebase Cloud Messaging Service
Handles sending push notifications to devices using FCM.
"""

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from django.utils import timezone
from .models import DeviceToken, NotificationLog
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized, so initialize it
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
        if not cred_path:
            logger.warning("FIREBASE_CREDENTIALS_PATH not set in settings")
            return False
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    return True


class FCMService:
    """Service class for Firebase Cloud Messaging operations."""
    
    TOPIC_ALL_USERS = 'all_users'  # Topic name for broadcasting to all users
    
    def __init__(self):
        self.initialized = initialize_firebase()
    
    def send_notification(
        self,
        title,
        body,
        tokens,
        data=None,
        notification_type='custom',
        image_url=None
    ):
        """
        Send notification to multiple devices.
        
        Args:
            title (str): Notification title
            body (str): Notification body
            tokens (list): List of FCM device tokens
            data (dict): Additional data payload
            notification_type (str): Type of notification
            image_url (str): URL of notification image (optional)
            
        Returns:
            dict: Results with success and failure counts
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return {'success': 0, 'failure': len(tokens), 'errors': ['Firebase not initialized']}
        
        if not tokens:
            return {'success': 0, 'failure': 0, 'errors': []}
        
        # Prepare notification payload
        notification_payload = messaging.Notification(
            title=title,
            body=body,
            image=image_url if image_url else None
        )
        
        # Prepare data payload
        data_payload = data or {}
        data_payload['notification_type'] = notification_type
        data_payload['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
        
        # Convert all data values to strings (FCM requirement)
        data_payload = {k: str(v) for k, v in data_payload.items()}
        
        results = {
            'success': 0,
            'failure': 0,
            'errors': [],
            'invalid_tokens': []
        }
        
        # Send in batches of 500 (FCM limit)
        batch_size = 500
        for i in range(0, len(tokens), batch_size):
            batch_tokens = tokens[i:i + batch_size]
            
            try:
                # Create multicast message
                message = messaging.MulticastMessage(
                    notification=notification_payload,
                    data=data_payload,
                    tokens=batch_tokens,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            channel_id='game_notifications'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        headers={'apns-priority': '10'},
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )
                
                # Send message
                response = messaging.send_multicast(message)
                
                results['success'] += response.success_count
                results['failure'] += response.failure_count
                
                # Handle failed tokens
                if response.failure_count > 0:
                    for idx, resp in enumerate(response.responses):
                        if not resp.success:
                            token = batch_tokens[idx]
                            error_msg = str(resp.exception) if resp.exception else 'Unknown error'
                            results['errors'].append({
                                'token': token[:20] + '...',
                                'error': error_msg
                            })
                            
                            # Mark invalid tokens
                            if 'not-registered' in error_msg.lower() or 'invalid' in error_msg.lower():
                                results['invalid_tokens'].append(token)
                                self._handle_invalid_token(token)
                
                logger.info(f"Batch sent: {response.success_count} success, {response.failure_count} failed")
                
            except Exception as e:
                logger.error(f"Error sending batch: {e}")
                results['failure'] += len(batch_tokens)
                results['errors'].append(str(e))
        
        return results
    
    def _handle_invalid_token(self, token):
        """Handle invalid or unregistered tokens."""
        try:
            device_token = DeviceToken.objects.get(token=token, is_active=True)
            device_token.failure_count += 1
            
            # Deactivate after 3 consecutive failures
            if device_token.failure_count >= 3:
                device_token.deactivate()
                logger.info(f"Deactivated token after {device_token.failure_count} failures")
            else:
                device_token.save(update_fields=['failure_count'])
        except DeviceToken.DoesNotExist:
            pass
    
    def send_to_topic(self, topic, title, body, data=None, notification_type='normal', image_url=None):
        """
        Send notification to a topic with full configuration.
        
        Args:
            topic (str): Topic name
            title (str): Notification title
            body (str): Notification body
            data (dict): Additional data payload
            notification_type (str): Type of notification (normal, fix, update, error)
            image_url (str): URL of notification image (optional)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Prepare data payload
            notification_data = data or {}
            notification_data['type'] = notification_type
            
            # Convert all data values to strings (FCM requirement)
            notification_data = {k: str(v) for k, v in notification_data.items()}
            
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url if image_url else None
            )
            
            # Android-specific config
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#FF6B35',
                    sound='default',
                    channel_id='default',
                    image=image_url if image_url else None
                )
            )
            
            # iOS-specific config
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body
                        ),
                        badge=1,
                        sound='default',
                        mutable_content=True if image_url else False
                    )
                ),
                headers={'apns-priority': '10'} if notification_type in ['fix', 'update', 'error'] else {}
            )
            
            # Create message
            message = messaging.Message(
                notification=notification,
                data=notification_data,
                topic=topic,
                android=android_config,
                apns=apns_config
            )
            
            response = messaging.send(message)
            logger.info(f"Successfully sent to topic '{topic}': {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending to topic '{topic}': {e}")
            return False


def send_notification_to_all_devices(
    title,
    body,
    notification_type='normal',
    data=None,
    user=None,
    image_url=None,
    force=False,
):
    """
    Convenience function to send notification to all active devices.
    Also saves notification to database for registered users.
    
    Args:
        title (str): Notification title
        body (str): Notification body
        notification_type (str): Type of notification (normal, fix, update, error)
        data (dict): Additional data payload
        user (User): Optional - send to specific user only
        image_url (str): URL of notification image (optional)
        
    Returns:
        NotificationLog: Log entry for this notification
    """
    from .models import Notification
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get ALL active device tokens (both registered and anonymous users)
    if user:
        device_tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        ).values_list('token', flat=True)
        sent_to_all = False
        target_users = [user]
    else:
        # Get all active device tokens
        device_tokens = DeviceToken.objects.filter(
            is_active=True
        ).values_list('token', flat=True)
        sent_to_all = True
        # Get all registered users with accounts for database notification
        target_users = User.objects.filter(is_active=True)
    
    tokens = list(device_tokens)
    
    # Create notification log
    log = NotificationLog.objects.create(
        notification_type=notification_type,
        title=title,
        body=body,
        image_url=image_url,
        data=data or {},
        target_user=user,
        sent_to_all=sent_to_all,
        total_devices=len(tokens)
    )
    
    # Save notification to database for registered users
    if notification_type in ['normal', 'fix', 'update', 'error']:
        notifications_to_create = []
        for target_user in target_users:
            notifications_to_create.append(
                Notification(
                    user=target_user,
                    notification_type=notification_type,
                    title=title,
                    body=body,
                    image_url=image_url,
                    data=data or {}
                )
            )
        
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
            logger.info(f"Created {len(notifications_to_create)} database notifications for registered users")
    
    if not tokens:
        logger.info(f"No active devices to send push notification: {title}")
        return log
    
    # Send push notification to ALL devices (registered and anonymous)
    fcm_service = FCMService()
    results = fcm_service.send_notification(
        title=title,
        body=body,
        tokens=tokens,
        data=data,
        notification_type=notification_type,
        image_url=image_url
    )
    
    # Update log with results
    log.successful_sends = results['success']
    log.failed_sends = results['failure']
    log.save(update_fields=['successful_sends', 'failed_sends'])
    
    logger.info(
        f"Notification sent: {title} | "
        f"Success: {results['success']}, Failed: {results['failure']}"
    )
    
    return log


def send_notification_to_all_users_topic(
    title,
    body,
    notification_type='normal',
    data=None,
    image_url=None,
    force=False,
):
    """
    Send notification to all users using FCM Topics (optimized method).
    This is much more efficient than sending to individual tokens.
    
    Args:
        title (str): Notification title
        body (str): Notification body
        notification_type (str): Type of notification (normal, fix, update, error)
        data (dict): Additional data payload
        image_url (str): URL of notification image (optional)
        
    Returns:
        NotificationLog: Log entry for this notification
    """
    from .models import Notification
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get all registered AND verified users for database notification
    target_users = User.objects.filter(is_active=True, is_email_verified=True)
    
    # Create notification log
    log = NotificationLog.objects.create(
        notification_type=notification_type,
        title=title,
        body=body,
        image_url=image_url,
        data=data or {},
        target_user=None,  # None indicates broadcast to all
        sent_to_all=True,
        total_devices=0  # Topics don't report exact device count
    )
    
    # Save notification to database for registered users
    if notification_type in ['normal', 'fix', 'update', 'error']:
        notifications_to_create = []
        for target_user in target_users:
            notifications_to_create.append(
                Notification(
                    user=target_user,
                    notification_type=notification_type,
                    title=title,
                    body=body,
                    image_url=image_url,
                    data=data or {}
                )
            )
        
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
            logger.info(f"Created {len(notifications_to_create)} database notifications for registered users")
    
    # Send push notification to topic (reaches ALL subscribed devices)
    fcm_service = FCMService()
    success = fcm_service.send_to_topic(
        topic=FCMService.TOPIC_ALL_USERS,
        title=title,
        body=body,
        data=data,
        notification_type=notification_type,
        image_url=image_url
    )
    
    # Update log with results
    if success:
        log.successful_sends = 1  # 1 successful topic send
        log.failed_sends = 0
    else:
        log.successful_sends = 0
        log.failed_sends = 1
    
    log.save(update_fields=['successful_sends', 'failed_sends'])
    
    status = "SUCCESS" if success else "FAILED"
    logger.info(
        f"Topic notification sent: {title} | "
        f"Topic: {FCMService.TOPIC_ALL_USERS} | Status: {status}"
    )
    
    return log
