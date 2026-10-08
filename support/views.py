from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SupportMessage
from .serializers import SupportMessageSerializer, SupportMessageDetailSerializer


# API Views
class SupportMessageViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for support messages
    - Users can create support messages
    - Only admins can view all messages
    """
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Anyone can create a support message
            return [permissions.AllowAny()]
        # Only staff can view messages
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list'] and self.request.user.is_staff:
            return SupportMessageDetailSerializer
        return SupportMessageSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by review status
        is_reviewed = self.request.query_params.get('is_reviewed')
        if is_reviewed is not None:
            queryset = queryset.filter(is_reviewed=is_reviewed.lower() == 'true')
        
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def mark_reviewed(self, request, pk=None):
        """Mark a message as reviewed"""
        message = self.get_object()
        message.mark_as_reviewed(admin_user=request.user)
        return Response({
            'status': 'success',
            'message': f'Message marked as reviewed by {request.user.username}'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def mark_pending(self, request, pk=None):
        """Mark a message as pending"""
        message = self.get_object()
        message.mark_as_pending()
        return Response({
            'status': 'success',
            'message': 'Message marked as pending'
        })


# Custom Admin Views
@method_decorator(login_required, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class SupportMessagesListView(View):
    """Custom admin view for listing support messages"""
    
    def get(self, request):
        # Get filter parameters (default to 'pending')
        filter_status = request.GET.get('status', 'pending')
        
        # Base queryset
        messages_qs = SupportMessage.objects.select_related('user', 'reviewed_by')
        
        # Apply filters
        if filter_status == 'pending':
            messages_qs = messages_qs.filter(is_reviewed=False)
        elif filter_status == 'reviewed':
            messages_qs = messages_qs.filter(is_reviewed=True)
        
        # Get counts for badges
        total_count = SupportMessage.objects.count()
        pending_count = SupportMessage.objects.filter(is_reviewed=False).count()
        reviewed_count = SupportMessage.objects.filter(is_reviewed=True).count()
        
        context = {
            'messages': messages_qs,
            'filter_status': filter_status,
            'total_count': total_count,
            'pending_count': pending_count,
            'reviewed_count': reviewed_count,
        }
        
        return render(request, 'customadmin/support_messages_list.html', context)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ToggleReviewView(View):
    """Toggle the review status of a support message"""
    
    def post(self, request, message_id):
        from django.http import JsonResponse
        
        message = get_object_or_404(SupportMessage, id=message_id)
        
        if message.is_reviewed:
            message.mark_as_pending()
            status_text = 'pending'
        else:
            message.mark_as_reviewed(admin_user=request.user)
            status_text = 'reviewed'
        
        # Check if this is an AJAX request (JSON content type or XMLHttpRequest header)
        is_ajax = (
            request.headers.get('Content-Type') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )
        
        # Return JSON response for AJAX requests
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Message marked as {status_text}',
                'is_reviewed': message.is_reviewed,
                'reviewed_by': message.reviewed_by.username if message.reviewed_by else None,
                'reviewed_at': message.reviewed_at.strftime('%b %d, %Y %H:%M') if message.reviewed_at else None,
            })
        
        # Fallback for form submissions
        messages.success(request, f'Message "{message.subject}" marked as {status_text}.')
        redirect_url = request.POST.get('next', '/customadmin/support/')
        return redirect(redirect_url)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DeleteSupportMessageView(View):
    """Delete a single support message"""
    
    def post(self, request, message_id):
        from django.http import JsonResponse
        
        message = get_object_or_404(SupportMessage, id=message_id)
        subject = message.subject
        message.delete()
        
        # Check if AJAX request
        is_ajax = (
            request.headers.get('Content-Type') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Message "{subject}" deleted successfully'
            })
        
        messages.success(request, f'Message "{subject}" deleted successfully.')
        return redirect('/customadmin/support/')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DeleteAllSupportMessagesView(View):
    """Delete all support messages with optional filter"""
    
    def post(self, request):
        from django.http import JsonResponse
        import json
        
        # Get filter from POST data or JSON body
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                filter_status = data.get('filter', 'all')
            else:
                filter_status = request.POST.get('filter', 'all')
        except:
            filter_status = request.POST.get('filter', 'all')
        
        # Base queryset
        messages_qs = SupportMessage.objects.all()
        
        # Apply filter
        if filter_status == 'pending':
            messages_qs = messages_qs.filter(is_reviewed=False)
        elif filter_status == 'reviewed':
            messages_qs = messages_qs.filter(is_reviewed=True)
        
        # Count and delete
        count = messages_qs.count()
        messages_qs.delete()
        
        # Check if AJAX request
        is_ajax = (
            request.headers.get('Content-Type') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'{count} message(s) deleted successfully',
                'count': count
            })
        
        if filter_status == 'all':
            messages.success(request, f'All {count} messages deleted successfully.')
        else:
            messages.success(request, f'All {count} {filter_status} messages deleted successfully.')
        
        return redirect('/customadmin/support/')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class MarkAllAsReviewedView(View):
    """Mark all support messages (or filtered) as reviewed"""
    
    def post(self, request):
        from django.http import JsonResponse
        import json
        
        # Get filter from POST data or JSON body
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                filter_status = data.get('filter', 'all')
            else:
                filter_status = request.POST.get('filter', 'all')
        except:
            filter_status = request.POST.get('filter', 'all')
        
        # Base queryset - only pending messages can be marked as reviewed
        messages_qs = SupportMessage.objects.filter(is_reviewed=False)
        
        # Additional filter if specified
        if filter_status == 'pending':
            # Already filtered to pending above
            pass
        elif filter_status == 'reviewed':
            # No pending messages in reviewed filter, return 0
            messages_qs = SupportMessage.objects.none()
        # 'all' means all pending messages
        
        # Count and mark as reviewed
        count = messages_qs.count()
        
        # Mark all as reviewed by current admin
        for message in messages_qs:
            message.mark_as_reviewed(admin_user=request.user)
        
        # Check if AJAX request
        is_ajax = (
            request.headers.get('Content-Type') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.content_type == 'application/json'
        )
        
        if is_ajax:
            from django.utils import timezone
            return JsonResponse({
                'success': True,
                'message': f'{count} message(s) marked as reviewed',
                'count': count,
                'reviewed_by': request.user.username,
                'reviewed_at': timezone.now().strftime('%b %d, %Y %H:%M')
            })
        
        messages.success(request, f'{count} messages marked as reviewed.')
        return redirect('/customadmin/support/')
