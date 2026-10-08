# Support Dashboard UI - Quick Reference

## Tab Structure

```
┌──────────────────────────────────────────────────────────┐
│  SUPPORT MESSAGES DASHBOARD                              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────┐  ┌──────────┐                              │
│  │ PENDING │  │ REVIEWED │                              │
│  │  (4)    │  │   (2)    │                              │
│  └─────────┘  └──────────┘                              │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Button Visibility Logic

### PENDING TAB (Active)
```
┌──────────────────────────────────────────────────────────────────┐
│ Pending Messages                                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ [✓ Mark All as Reviewed]  [🗑️ Delete All Pending]              │
│         VISIBLE                     VISIBLE                      │
│                                                                   │
│  ┌──────────────────────────────────────────┐                   │
│  │ Subject: Game not loading                │                   │
│  │ From: user@example.com                   │                   │
│  │ Status: ● Pending                        │                   │
│  │                                           │                   │
│  │ [✓ Mark as Reviewed] [🗑️ Delete]        │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### REVIEWED TAB (Active)
```
┌──────────────────────────────────────────────────────────────────┐
│ Reviewed Messages                                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│                              [🗑️ Delete All Reviewed]           │
│         HIDDEN                          VISIBLE                  │
│                                                                   │
│  ┌──────────────────────────────────────────┐                   │
│  │ Subject: Feature request                 │                   │
│  │ From: user2@example.com                  │                   │
│  │ Status: ✓ Reviewed                       │                   │
│  │ Reviewed by: admin on Dec 22, 2024       │                   │
│  │                                           │                   │
│  │ [Mark as Pending] [🗑️ Delete]           │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Button Logic Matrix

| Tab       | Mark All as Reviewed | Delete All        |
|-----------|---------------------|-------------------|
| Pending   | ✅ VISIBLE          | ✅ VISIBLE        |
| Reviewed  | ❌ HIDDEN           | ✅ VISIBLE        |

## Operations Flow

### Mark All as Reviewed (Pending Tab Only)
```
User clicks "Mark All as Reviewed"
    ↓
Confirmation dialog: "Mark 4 pending messages as reviewed?"
    ↓
User confirms
    ↓
POST to /customadmin/support/mark-all-reviewed/
    ↓
Backend marks all pending as reviewed
    ↓
Toast notification: "✓ Successfully marked 4 messages as reviewed"
    ↓
Page reloads after 800ms
    ↓
Returns to Pending tab (now empty or with remaining pending)
```

### Delete All (Both Tabs)
```
User clicks "Delete All"
    ↓
Confirmation dialog: "Delete 4 [pending/reviewed] messages?"
    ↓
User confirms
    ↓
POST to /customadmin/support/delete-all/ with filter
    ↓
Backend deletes filtered messages
    ↓
Toast notification: "✓ Successfully deleted 4 messages"
    ↓
Page reloads after 800ms
    ↓
Returns to same tab with updated count
```

### Delete Single Message (Both Tabs)
```
User clicks "Delete" on individual message
    ↓
Confirmation dialog: "Delete message 'Subject'?"
    ↓
User confirms
    ↓
POST to /customadmin/support/{id}/delete/
    ↓
Backend deletes message
    ↓
Toast notification: "✓ Message deleted successfully"
    ↓
Page reloads after 800ms
    ↓
Returns to same tab
```

## Default Behavior

1. **First Visit**: Automatically shows Pending tab
2. **No URL Parameter**: Defaults to `?status=pending`
3. **Empty State**: Shows appropriate message:
   - Pending: "There are no pending support messages at the moment."
   - Reviewed: "There are no reviewed messages yet."

## Badge Colors

- **Pending Badge**: Yellow (#ffc107) - Urgent/actionable
- **Reviewed Badge**: Green (#28a745) - Completed/archived

## Toast Notifications

```
Success (Green):
┌─────────────────────────────────────┐
│ ✓ Message marked as reviewed        │
└─────────────────────────────────────┘

Error (Red):
┌─────────────────────────────────────┐
│ ✗ Failed to delete message          │
└─────────────────────────────────────┘
```

Duration: 3 seconds + slide out animation

## Keyboard Navigation

- Click tab to switch
- Confirm/Cancel dialogs use Enter/Escape
- Auto-focus on confirmation dialogs

## Responsive Design

- Tabs stack horizontally
- Buttons stack vertically on mobile
- Cards remain full-width with responsive padding
- Touch-friendly button sizes (min 44x44px)
