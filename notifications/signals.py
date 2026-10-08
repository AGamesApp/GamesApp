"""
Django signals for automatic notifications - DISABLED.
All automatic notifications have been permanently disabled.
Only manual notifications from the admin panel will work.
"""

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from games.models import Game, Emulator, AppSettings
# from .fcm_service import send_notification_to_all_users_topic
# import logging

# logger = logging.getLogger(__name__)


# AUTOMATIC NOTIFICATIONS PERMANENTLY DISABLED
# All signal receivers below are commented out to prevent automatic notifications
# when games or emulators are created or updated.
# Manual notifications from the admin panel still work normally.


# @receiver(post_save, sender=Game)
# def notify_new_game(sender, instance, created, **kwargs):
#     """Send notification when a new game is added."""
#     if created:
#         # Respect global toggle in AppSettings
#         try:
#             app_settings = AppSettings.objects.first()
#             if app_settings and getattr(app_settings, 'disable_automatic_notifications', False):
#                 logger.info("Automatic notifications disabled in AppSettings; skipping new game notification")
#                 return
#         except Exception:
#             # If anything goes wrong reading settings, continue and attempt to send
#             logger.exception("Failed to read AppSettings; proceeding to send notification")
#         try:
#             send_notification_to_all_users_topic(
#                 title="🎮 New Game Added!",
#                 body=f"{instance.title} is now available for {instance.emulator.name}!",
#                 notification_type='new_game',
#                 data={
#                     'game_id': instance.id,
#                     'game_title': instance.title,
#                     'emulator': instance.emulator.name,
#                     'screen': 'game_detail'
#                 }
#             )
#             logger.info(f"Sent new game notification for: {instance.title}")
#         except Exception as e:
#             logger.error(f"Failed to send new game notification: {e}")


# @receiver(post_save, sender=Game)
# def notify_trending_game(sender, instance, created, **kwargs):
#     """Send notification when game becomes trending (high views)."""
#     if not created:
#         # Respect global toggle in AppSettings
#         try:
#             app_settings = AppSettings.objects.first()
#             if app_settings and getattr(app_settings, 'disable_automatic_notifications', False):
#                 logger.info("Automatic notifications disabled in AppSettings; skipping trending notification")
#                 return
#         except Exception:
#             logger.exception("Failed to read AppSettings; proceeding to send notification")
#         # Check if views just crossed the trending threshold (e.g., 1000)
#         TRENDING_THRESHOLD = 1000
#         if instance.views == TRENDING_THRESHOLD:
#             try:
#                 send_notification_to_all_users_topic(
#                     title="🔥 Trending Game Alert!",
#                     body=f"{instance.title} is trending now! Check it out!",
#                     notification_type='trending',
#                     data={
#                         'game_id': instance.id,
#                         'game_title': instance.title,
#                         'views': instance.views,
#                         'screen': 'game_detail'
#                     }
#                 )
#                 logger.info(f"Sent trending notification for: {instance.title}")
#             except Exception as e:
#                 logger.error(f"Failed to send trending notification: {e}")


# @receiver(post_save, sender=Game)
# def notify_high_downloads(sender, instance, created, **kwargs):
#     """Send notification when game reaches high download count."""
#     if not created:
#         # Respect global toggle in AppSettings
#         try:
#             app_settings = AppSettings.objects.first()
#             if app_settings and getattr(app_settings, 'disable_automatic_notifications', False):
#                 logger.info("Automatic notifications disabled in AppSettings; skipping high downloads notification")
#                 return
#         except Exception:
#             logger.exception("Failed to read AppSettings; proceeding to send notification")
#         # Check if downloads just crossed the threshold (e.g., 500)
#         HIGH_DOWNLOADS_THRESHOLD = 500
#         if instance.downloads == HIGH_DOWNLOADS_THRESHOLD:
#             try:
#                 send_notification_to_all_users_topic(
#                     title="📥 Popular Download!",
#                     body=f"{instance.title} has been downloaded {instance.downloads} times! Don't miss out!",
#                     notification_type='high_downloads',
#                     data={
#                         'game_id': instance.id,
#                         'game_title': instance.title,
#                         'downloads': instance.downloads,
#                         'screen': 'game_detail'
#                     }
#                 )
#                 logger.info(f"Sent high downloads notification for: {instance.title}")
#             except Exception as e:
#                 logger.error(f"Failed to send high downloads notification: {e}")


# @receiver(post_save, sender=Game)
# def notify_milestone(sender, instance, created, **kwargs):
#     """Send notification for download milestones."""
#     if not created:
#         # Respect global toggle in AppSettings
#         try:
#             app_settings = AppSettings.objects.first()
#             if app_settings and getattr(app_settings, 'disable_automatic_notifications', False):
#                 logger.info("Automatic notifications disabled in AppSettings; skipping milestone notifications")
#                 return
#         except Exception:
#             logger.exception("Failed to read AppSettings; proceeding to send notification")
#         milestones = [1000, 5000, 10000, 50000, 100000]
#         if instance.downloads in milestones:
#             try:
#                 send_notification_to_all_users_topic(
#                     title="🎉 Milestone Reached!",
#                     body=f"{instance.title} just hit {instance.downloads:,} downloads!",
#                     notification_type='milestone',
#                     data={
#                         'game_id': instance.id,
#                         'game_title': instance.title,
#                         'downloads': instance.downloads,
#                         'screen': 'game_detail'
#                     }
#                 )
#                 logger.info(f"Sent milestone notification for: {instance.title}")
#             except Exception as e:
#                 logger.error(f"Failed to send milestone notification: {e}")
#         
#         # Also check view milestones
#         view_milestones = [5000, 10000, 50000, 100000]
#         if instance.views in view_milestones:
#             try:
#                 send_notification_to_all_users_topic(
#                     title="🎉 Viral Alert!",
#                     body=f"{instance.title} has reached {instance.views:,} views!",
#                     notification_type='milestone',
#                     data={
#                         'game_id': instance.id,
#                         'game_title': instance.title,
#                         'views': instance.views,
#                         'screen': 'game_detail'
#                     }
#                 )
#                 logger.info(f"Sent view milestone notification for: {instance.title}")
#             except Exception as e:
#                 logger.error(f"Failed to send view milestone notification: {e}")


# @receiver(post_save, sender=Emulator)
# def notify_new_emulator(sender, instance, created, **kwargs):
#     """Send notification when a new emulator is added."""
#     if created:
#         # Respect global toggle in AppSettings
#         try:
#             app_settings = AppSettings.objects.first()
#             if app_settings and getattr(app_settings, 'disable_automatic_notifications', False):
#                 logger.info("Automatic notifications disabled in AppSettings; skipping new emulator notification")
#                 return
#         except Exception:
#             logger.exception("Failed to read AppSettings; proceeding to send notification")
#         try:
#             send_notification_to_all_users_topic(
#                 title="🕹️ New Emulator Added!",
#                 body=f"{instance.name} emulator is now available!",
#                 notification_type='new_emulator',
#                 data={
#                     'emulator_id': instance.id,
#                     'emulator_name': instance.name,
#                     'screen': 'emulator_games'
#                 }
#             )
#             logger.info(f"Sent new emulator notification for: {instance.name}")
#         except Exception as e:
#             logger.error(f"Failed to send new emulator notification: {e}")
