from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, CreatePaymentIntentView, StripeWebhookView, GooglePlayVerifyView

app_name = 'payments'

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    # ⚠️  Custom paths MUST come before router include so that
    #     'payments/verify/' is not swallowed by 'payments/<pk>/'
    path('payments/verify/', GooglePlayVerifyView.as_view(), name='google-play-verify'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('', include(router.urls)),
]
