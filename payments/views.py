from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import stripe
import uuid
import logging
from .models import Payment, GooglePlayPurchase
from .serializers import (
    PaymentSerializer, PaymentIntentSerializer,
    GooglePlayVerifySerializer, GooglePlayPurchaseSerializer,
)
from subscriptions.models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger('payments')

# ---------- Default Google Play package name ----------
GOOGLE_PLAY_PACKAGE = getattr(settings, 'GOOGLE_PLAY_PACKAGE_NAME', 'com.agames.play')


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing payment history."""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        # Users can only see their own payments
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)


# =================================================================
#  POST /api/payments/verify  –  Google Play receipt validation
# =================================================================

class GooglePlayVerifyView(APIView):
    """
    Verify a Google Play subscription purchase token.

    ✅ Validates the token with Google Play Developer API
    ✅ Anti-fraud: rejects already-claimed tokens
    ✅ Grants premium status + saves expiration
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GooglePlayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        purchase_token = serializer.validated_data['purchase_token']
        product_id = serializer.validated_data['product_id']
        package_name = serializer.validated_data.get('package_name', GOOGLE_PLAY_PACKAGE)

        user = request.user

        # ---------- 1. Anti-fraud: token already claimed? ----------
        existing = GooglePlayPurchase.objects.filter(purchase_token=purchase_token).first()
        if existing:
            if existing.user_id == user.id:
                # Same user re-sending (e.g. app retry) – idempotent success
                return Response({
                    'message': 'Purchase verified successfully',
                    'is_premium': user.is_premium,
                    'expiration_date': existing.expiry_time,
                    'product_id': existing.product_id,
                }, status=status.HTTP_200_OK)
            else:
                # Different user trying to re-use token → fraud attempt
                logger.warning(
                    f"⚠️ Token reuse attempt: user {user.email} tried token already "
                    f"claimed by user_id={existing.user_id}"
                )
                return Response({
                    'error': 'This purchase token has already been claimed by another account.',
                    'is_premium': False,
                }, status=status.HTTP_409_CONFLICT)

        # ---------- 2. Verify with Google Play API v2 ----------
        from .google_play import verify_subscription
        result = verify_subscription(package_name, product_id, purchase_token)

        if not result['success']:
            error_msg = result['error'] or 'Google Play verification failed'
            logger.info(f"❌ Google Play verification failed for {user.email}: {error_msg}")

            # Invalid/bad token → 400; server/permission errors → 502
            if 'Invalid purchase token' in error_msg or 'not found' in error_msg.lower():
                http_status = status.HTTP_400_BAD_REQUEST
            else:
                http_status = status.HTTP_502_BAD_GATEWAY

            return Response({
                'error': error_msg,
                'is_premium': False,
            }, status=http_status)

        expiry_time = result['expiry_time']
        order_id = result['order_id']

        # ---------- 3. Save verified purchase (anti-fraud record) ----------
        GooglePlayPurchase.objects.create(
            user=user,
            purchase_token=purchase_token,
            product_id=product_id,
            order_id=order_id,
            expiry_time=expiry_time,
            is_active=True,
            raw_response=result['raw'],
        )

        # ---------- 4. Grant premium status ----------
        user.is_premium = True
        user.premium_expiration = expiry_time
        user.save(update_fields=['is_premium', 'premium_expiration'])

        logger.info(
            f"✅ Premium granted to {user.email} via Google Play "
            f"({product_id}), expires {expiry_time}"
        )

        return Response({
            'message': 'Purchase verified successfully!',
            'is_premium': True,
            'expiration_date': expiry_time,
            'product_id': product_id,
        }, status=status.HTTP_200_OK)


class CreatePaymentIntentView(APIView):
    """API endpoint for creating payment intent."""
    
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subscription_id = serializer.validated_data['subscription_id']
        payment_method = serializer.validated_data['payment_method']
        
        try:
            subscription = Subscription.objects.get(
                id=subscription_id,
                user=request.user
            )
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        amount = subscription.plan.price
        transaction_id = str(uuid.uuid4())
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=amount,
            status='PENDING',
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        
        if payment_method == 'STRIPE':
            try:
                # Create Stripe PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'payment_id': payment.id,
                        'subscription_id': subscription.id,
                        'user_id': request.user.id
                    }
                )
                
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return Response({
                    'client_secret': intent.client_secret,
                    'payment_id': payment.id,
                    'amount': str(amount)
                })
            except stripe.error.StripeError as e:
                payment.status = 'FAILED'
                payment.save()
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(PaymentSerializer(payment).data)


class StripeWebhookView(APIView):
    """Webhook endpoint for Stripe events."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Update payment status
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = 'COMPLETED'
                payment.save()
                
                # Update subscription status
                if payment.subscription:
                    payment.subscription.status = 'ACTIVE'
                    payment.subscription.save()
            except Payment.DoesNotExist:
                pass
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = 'FAILED'
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return Response(status=status.HTTP_200_OK)
