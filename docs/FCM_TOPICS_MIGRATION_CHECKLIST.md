# FCM Topics Migration Checklist

Use this checklist to track your migration from token-based to topic-based push notifications.

---

## 📋 Pre-Migration

- [ ] **Read Documentation**
  - [ ] Read `FCM_TOPICS_MIGRATION_GUIDE.md`
  - [ ] Read `FCM_TOPICS_QUICK_REFERENCE.md`
  - [ ] Review `ADMIN_DASHBOARD_UPDATE_EXAMPLE.md`

- [ ] **Backup Everything**
  - [ ] Backup database: `pg_dump gamezone_db > backup_$(date +%Y%m%d).sql`
  - [ ] Commit current code: `git add . && git commit -m "Backup before FCM Topics"`
  - [ ] Create git tag: `git tag before-fcm-topics`
  
- [ ] **Verify Current System**
  - [ ] Count active tokens: Check database
  - [ ] Test current notification sending: Works correctly
  - [ ] Review Firebase Console: Check current stats

---

## 🔧 Backend Migration

### Phase 1: Code Implementation (✅ Complete)

- [x] **FCM Service Updates** (`notifications/fcm_service.py`)
  - [x] Added `TOPIC_ALL_USERS = 'all_users'` constant
  - [x] Enhanced `send_to_topic()` method
  - [x] Created `send_notification_to_all_users_topic()` function
  
- [x] **Migration Command** (`notifications/management/commands/migrate_tokens_to_topic.py`)
  - [x] Created migration script
  - [x] Added dry-run mode
  - [x] Added batch processing
  - [x] Added error handling

- [x] **Documentation**
  - [x] Created migration guide
  - [x] Created quick reference
  - [x] Created admin dashboard example
  - [x] Created client-side guides

### Phase 2: Database Migration

- [ ] **Test Migration (Dry Run)**
  ```bash
  python manage.py migrate_tokens_to_topic --dry-run
  ```
  - [ ] Command executes without errors
  - [ ] Output shows expected token count
  - [ ] Batch calculation is correct

- [ ] **Run Actual Migration**
  ```bash
  python manage.py migrate_tokens_to_topic
  ```
  - [ ] Confirm when prompted
  - [ ] Wait for completion
  - [ ] Review success/failure statistics
  - [ ] Note: Success rate ____% (Target: >95%)

- [ ] **Verify Migration**
  - [ ] Check Firebase Console → Topics
  - [ ] 'all_users' topic exists: Yes/No
  - [ ] Subscriber count matches: Expected _____ vs Actual _____
  - [ ] Check Django logs for errors

---

## 📱 Mobile App Updates

### React Native App

- [ ] **Update Notification Service**
  - [ ] Add/update notification service file
  - [ ] Implement topic subscription code
  - [ ] Add backend registration with `subscribed_to_all_users` flag
  - [ ] Test on development build

- [ ] **Testing**
  - [ ] Test on Android emulator
  - [ ] Test on iOS simulator
  - [ ] Test on physical Android device
  - [ ] Test on physical iOS device
  - [ ] Verify topic subscription in Firebase Console

- [ ] **Deployment**
  - [ ] Update version number
  - [ ] Build production APK/AAB
  - [ ] Build iOS archive
  - [ ] Submit to Play Store
  - [ ] Submit to App Store

### Flutter App

- [ ] **Update Notification Service**
  - [ ] Add/update NotificationService class
  - [ ] Implement topic subscription code
  - [ ] Add backend registration with `subscribed_to_all_users` flag
  - [ ] Test on development build

- [ ] **Testing**
  - [ ] Test on Android emulator
  - [ ] Test on iOS simulator
  - [ ] Test on physical Android device
  - [ ] Test on physical iOS device
  - [ ] Verify topic subscription in Firebase Console

- [ ] **Deployment**
  - [ ] Update version number
  - [ ] Build production APK/AAB
  - [ ] Build iOS archive
  - [ ] Submit to Play Store
  - [ ] Submit to App Store

---

## 🖥️ Admin Dashboard Updates (Optional)

- [ ] **Update Notification Views** (`customadmin/views.py`)
  - [ ] Change import to `send_notification_to_all_users_topic`
  - [ ] Update function call
  - [ ] Update success message
  - [ ] Test sending notification

- [ ] **OR Keep Both Methods**
  - [ ] Import both functions
  - [ ] Add checkbox in template
  - [ ] Add logic to choose method
  - [ ] Test both methods

- [ ] **OR Keep Original**
  - [ ] No changes needed
  - [ ] Continue using `send_notification_to_all_devices()`
  - [ ] Can switch later

---

## 🧪 Testing & Verification

### Backend Testing

- [ ] **Django Shell Test**
  ```python
  from notifications.fcm_service import send_notification_to_all_users_topic
  
  log = send_notification_to_all_users_topic(
      title='Test Topic Notification',
      body='Testing FCM Topics!',
      notification_type='normal'
  )
  
  print(f"Success: {log.successful_sends}, Failed: {log.failed_sends}")
  ```
  - [ ] Command executes successfully
  - [ ] Log entry created
  - [ ] Success count > 0

- [ ] **Admin Dashboard Test**
  - [ ] Login to admin dashboard
  - [ ] Navigate to Send Notification
  - [ ] Fill in test notification
  - [ ] Click Send
  - [ ] Success message displayed

### Mobile Testing

- [ ] **iOS Device**
  - [ ] Receives notification
  - [ ] Image displays (if sent)
  - [ ] Tapping opens app
  - [ ] Custom data received
  - [ ] Latency < 2 seconds

- [ ] **Android Device**
  - [ ] Receives notification
  - [ ] Image displays (if sent)
  - [ ] Tapping opens app
  - [ ] Custom data received
  - [ ] Latency < 2 seconds

### Firebase Console

- [ ] **Topic Statistics**
  - [ ] Navigate to Cloud Messaging → Topics
  - [ ] 'all_users' topic visible
  - [ ] Subscriber count accurate
  - [ ] Delivery statistics showing

- [ ] **Message History**
  - [ ] Recent messages visible
  - [ ] Delivery rates shown
  - [ ] Error rates acceptable (< 5%)

---

## 📊 Performance Monitoring

### Week 1: Initial Monitoring

- [ ] **Day 1**
  - [ ] Send test notification
  - [ ] Monitor delivery time: _____ seconds
  - [ ] Check success rate: _____%
  - [ ] Review logs for errors

- [ ] **Day 3**
  - [ ] Send production notification
  - [ ] Monitor delivery time: _____ seconds
  - [ ] Check success rate: _____%
  - [ ] Compare with old method

- [ ] **Day 7**
  - [ ] Review weekly statistics
  - [ ] Compare performance metrics
  - [ ] Document improvements
  - [ ] Note any issues

### Week 2-4: Ongoing Monitoring

- [ ] **Weekly Review**
  - [ ] Check Firebase Console statistics
  - [ ] Review Django notification logs
  - [ ] Monitor delivery success rates
  - [ ] Track user feedback

---

## 📈 Success Metrics

Record your results:

### Before Migration (Token-based)

- Active devices: _____
- Average API calls per notification: _____
- Average delivery time: _____ seconds
- Average success rate: _____%

### After Migration (Topic-based)

- Active devices: _____
- Average API calls per notification: 1
- Average delivery time: _____ seconds
- Average success rate: _____%

### Improvements

- API call reduction: _____%
- Delivery time improvement: _____%
- Success rate change: +/- _____%

---

## 🚨 Troubleshooting

### If migration fails:

- [ ] **Check Logs**
  ```bash
  tail -f logs/django.log | grep -i "error"
  ```

- [ ] **Verify Firebase Credentials**
  - [ ] serviceAccountKey.json exists
  - [ ] Firebase initialized correctly

- [ ] **Re-run Migration**
  - [ ] Check for invalid tokens
  - [ ] Run with smaller batch size
  - [ ] Review error messages

### If notifications not received:

- [ ] **Check Topic Subscription**
  - [ ] Firebase Console shows subscribers
  - [ ] Mobile app subscribes on start
  - [ ] Backend registration successful

- [ ] **Check Notification Sending**
  - [ ] Django logs show "SUCCESS"
  - [ ] NotificationLog entry exists
  - [ ] Firebase Console shows send

- [ ] **Check Mobile App**
  - [ ] Permissions granted
  - [ ] Firebase configured correctly
  - [ ] App in foreground/background

### If performance not improved:

- [ ] **Verify Using Topics**
  - [ ] Code uses `send_notification_to_all_users_topic()`
  - [ ] Logs show "Topic notification sent"
  - [ ] Firebase Console shows topic sends

- [ ] **Check Network**
  - [ ] Server connection stable
  - [ ] Firebase services reachable
  - [ ] No rate limiting

---

## 📝 Notes & Observations

### Migration Date: ________________

### Active Tokens Before: ________________

### Active Tokens After: ________________

### Issues Encountered:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

### Solutions Applied:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

### Performance Improvements:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

### User Feedback:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

## ✅ Migration Complete

- [ ] **All Steps Completed**
  - [ ] Backend migrated
  - [ ] Mobile apps updated
  - [ ] Testing passed
  - [ ] Performance improved
  - [ ] Documentation updated

- [ ] **Final Verification**
  - [ ] Send production notification
  - [ ] All devices receive within 2 seconds
  - [ ] Success rate > 95%
  - [ ] Firebase Console shows activity

- [ ] **Cleanup**
  - [ ] Remove old code (if applicable)
  - [ ] Archive documentation
  - [ ] Update README
  - [ ] Celebrate! 🎉

---

## 📞 Support Resources

- **Documentation**: `/root/game/docs/`
  - `FCM_TOPICS_MIGRATION_GUIDE.md`
  - `FCM_TOPICS_QUICK_REFERENCE.md`
  - `ADMIN_DASHBOARD_UPDATE_EXAMPLE.md`

- **Code Examples**:
  - React Native: `docs/client-side-fcm-topics-react-native.js`
  - Flutter: `docs/client-side-fcm-topics-flutter.dart`

- **Commands**:
  ```bash
  # Migration
  python manage.py migrate_tokens_to_topic --dry-run
  python manage.py migrate_tokens_to_topic
  
  # Testing
  python manage.py shell
  
  # Logs
  tail -f logs/django.log
  ```

---

**Migration Status**: ⏳ In Progress / ✅ Complete

**Last Updated**: ________________

**Completed By**: ________________
