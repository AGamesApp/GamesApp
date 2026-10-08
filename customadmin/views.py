from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from games.models import Game, Emulator, Genre, AppSettings, GameReview, GameRating, GameLove
from pages.models import Page
from notifications.models import DeviceToken
from notifications.fcm_service import send_notification_to_all_users_topic
from support.models import SupportMessage
from .forms import (
    GameForm, EmulatorForm, GenreForm, PageForm, 
    GameImageFormSet, GameAdditionalFileFormSet,
    EmulatorAdditionalFileFormSet, AppSettingsForm
)
from django import forms
from django.contrib.auth import get_user_model
import import_games as importer
from django.urls import reverse
from django.http import HttpResponseRedirect
import threading
import logging

logger = logging.getLogger(__name__)


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only superusers can access the view"""
    login_url = '/customadmin/login/'
    
    def test_func(self):
        return self.request.user.is_superuser


class LoginView(View):
    """Custom login view for superusers"""
    template_name = 'customadmin/login.html'
    
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect('customadmin:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        print("="*60)
        print(f"LOGIN ATTEMPT")
        print(f"Email: [{email}]")
        print(f"Email bytes: {email.encode()}")
        print(f"Email repr: {repr(email)}")
        print(f"Password: [{password}]")
        print(f"All POST keys: {list(request.POST.keys())}")
        print(f"All POST values: {list(request.POST.values())}")
        
        # List all users in database
        all_users = User.objects.all()
        print(f"\nDatabase has {all_users.count()} users:")
        for u in all_users:
            print(f"  - [{u.email}] (bytes: {u.email.encode()})")
        print("="*60)
        
        # Find user (case-insensitive)
        user = None
        try:
            user = User.objects.get(email__iexact=email)
            print(f"✓ Found user: {user.email}")
        except User.DoesNotExist:
            print(f"✗ No user with email: {email}")
            messages.error(request, 'User not found.')
            return render(request, self.template_name)
        except User.MultipleObjectsReturned:
            print(f"✗ Multiple users with email: {email}")
            user = User.objects.filter(email__iexact=email).first()
            print(f"Using first: {user.email}")
        
        # Check password
        if not user.check_password(password):
            print(f"✗ Invalid password")
            messages.error(request, 'Invalid password.')
            return render(request, self.template_name)
        
        print(f"✓ Password valid")
        
        # Check if superuser
        if not user.is_superuser:
            print(f"✗ Not a superuser")
            messages.error(request, 'Access denied. Superuser only.')
            return render(request, self.template_name)
        
        print(f"✓ Is superuser")
        
        # Check if active
        if not user.is_active:
            print(f"✗ User not active")
            messages.error(request, 'Account is disabled.')
            return render(request, self.template_name)
        
        print(f"✓ User is active")
        
        # Login the user manually (bypass authenticate)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"✓ User logged in successfully")
        print("="*60)
        
        messages.success(request, f'Welcome back, {user.email}!')
        return redirect('customadmin:dashboard')


class LogoutView(View):
    """Logout view"""
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('customadmin:login')


class DashboardView(SuperUserRequiredMixin, TemplateView):
    """Dashboard view showing stats and overview"""
    template_name = 'customadmin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        from django.db.models import Count, Avg, Sum, Q, Max, Min
        from django.contrib.auth import get_user_model
        from datetime import timedelta
        from django.utils import timezone
        
        User = get_user_model()
        context = super().get_context_data(**kwargs)
        
        # Basic counts (optimized with single queries)
        context['games_count'] = Game.objects.count()
        context['emulators_count'] = Emulator.objects.count()
        context['genres_count'] = Genre.objects.count()
        context['pages_count'] = Page.objects.count()
        context['active_devices'] = DeviceToken.objects.filter(is_active=True).count()
        context['pending_support_messages'] = SupportMessage.objects.filter(is_reviewed=False).count()
        
        # Game statistics (combined query)
        game_stats = Game.objects.aggregate(
            premium_count=Count('id', filter=Q(is_premium=True)),
            free_count=Count('id', filter=Q(is_premium=False)),
            total_views=Sum('views'),
            avg_views=Avg('views'),
            max_views=Max('views')
        )
        context['premium_games_count'] = game_stats['premium_count']
        context['free_games_count'] = game_stats['free_count']
        context['total_views'] = game_stats['total_views'] or 0
        context['avg_views_per_game'] = round(game_stats['avg_views'] or 0, 1)
        context['max_views'] = game_stats['max_views'] or 0
        
        # User statistics (combined query)
        user_stats = User.objects.aggregate(
            total=Count('id'),
            premium=Count('id', filter=Q(is_premium=True)),
            verified=Count('id', filter=Q(is_email_verified=True))
        )
        context['total_users'] = user_stats['total']
        context['premium_users'] = user_stats['premium']
        context['verified_users'] = user_stats['verified']
        
        # Activity statistics (combined query)
        from games.models import GameRating, GameReview, GameLove
        from django.db.models import Sum
        
        # Get total downloads from all games (sum of downloads field)
        total_downloads = Game.objects.aggregate(total=Sum('downloads'))['total'] or 0
        
        activity_stats = {
            'downloads': total_downloads,
            'ratings': GameRating.objects.count(),
            'reviews': GameReview.objects.count(),
            'loves': GameLove.objects.count(),
        }
        context.update({
            'total_downloads': activity_stats['downloads'],
            'total_ratings': activity_stats['ratings'],
            'total_reviews': activity_stats['reviews'],
            'total_loves': activity_stats['loves'],
        })
        
        # Average rating
        avg_rating = GameRating.objects.aggregate(avg=Avg('score'))
        context['average_rating'] = round(avg_rating['avg'], 2) if avg_rating['avg'] else 0
        
        # VIEW STATISTICS - NEW SECTION
        # Most viewed games (top 10)
        context['most_viewed_games'] = Game.objects.select_related('emulator').order_by('-views')[:10]
        
        # Views by emulator
        context['views_by_emulator'] = Emulator.objects.annotate(
            total_views=Sum('games__views'),
            game_count=Count('games')
        ).order_by('-total_views')[:5]
        
        # Recent 7 days statistics
        seven_days_ago = timezone.now() - timedelta(days=7)
        context['recent_games_count'] = Game.objects.filter(created_at__gte=seven_days_ago).count()
        # Note: Download count is now a simple counter, cannot track by date
        context['recent_downloads_count'] = 0  # No longer tracking individual downloads
        
        # Games with most views but no downloads (potential issues)
        context['high_views_no_downloads'] = Game.objects.filter(
            views__gte=10, downloads=0
        ).order_by('-views')[:5]
        
        # Games by genre (optimized)
        context['games_by_genre'] = Genre.objects.annotate(
            game_count=Count('games')
        ).order_by('-game_count')[:5]
        
        # Top emulators by game count (optimized with views)
        context['top_emulators'] = Emulator.objects.annotate(
            game_count=Count('games'),
            total_views=Sum('games__views')
        ).order_by('-game_count')[:5]
        
        # Most loved games (optimized)
        context['most_loved_games'] = Game.objects.select_related('emulator').annotate(
            love_count=Count('loves')
        ).filter(love_count__gt=0).order_by('-love_count')[:5]
        
        # Most downloaded games (optimized)
        context['most_downloaded_games'] = Game.objects.select_related('emulator').filter(
            downloads__gt=0
        ).order_by('-downloads')[:5]
        
        # Top rated games (optimized)
        context['top_rated_games'] = Game.objects.select_related('emulator').annotate(
            avg_rating=Avg('ratings__score'),
            rating_count=Count('ratings')
        ).filter(rating_count__gt=0).order_by('-avg_rating')[:5]
        
        # Recent activity (optimized with select_related)
        context['recent_games'] = Game.objects.select_related('emulator').order_by('-created_at')[:5]
        # Most downloaded games instead of recent downloads (no longer tracking individual downloads)
        context['recent_downloads'] = Game.objects.select_related('emulator').filter(downloads__gt=0).order_by('-downloads')[:5]
        context['recent_ratings'] = GameRating.objects.select_related('game__emulator', 'user').order_by('-created_at')[:5]
        context['recent_reviews'] = GameReview.objects.select_related('game__emulator', 'user').order_by('-created_at')[:5]
        
        # Most active reviewers (optimized)
        context['top_reviewers'] = User.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-review_count')[:5]
        
        return context


class GameListView(SuperUserRequiredMixin, ListView):
    """List all games with search functionality"""
    model = Game
    template_name = 'customadmin/game_list.html'
    context_object_name = 'games'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Game.objects.select_related('emulator').prefetch_related('genres').order_by('-priority', '-id')
        search = self.request.GET.get('search', '')
        emulators = self.request.GET.getlist('emulator')  # Get selected emulator IDs
        
        # Filter by emulators if selected
        if emulators:
            queryset = queryset.filter(emulator_id__in=emulators)
        
        # Filter by search text
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(region__icontains=search) |
                Q(genres__name__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_emulators'] = self.request.GET.getlist('emulator')
        context['all_emulators'] = Emulator.objects.all().order_by('name')
        
        if context['search'] or context['selected_emulators']:
            # Use paginator's count (already calculated) instead of re-querying
            context['total_results'] = context['paginator'].count
        return context


class GameCreateView(SuperUserRequiredMixin, CreateView):
    """Create a new game"""
    model = Game
    template_name = 'customadmin/game_form.html'
    form_class = GameForm
    success_url = reverse_lazy('customadmin:game_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        if self.request.POST:
            context['image_formset'] = GameImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
            context['additional_file_formset'] = GameAdditionalFileFormSet(self.request.POST, instance=self.object)
        else:
            context['image_formset'] = GameImageFormSet(instance=self.object)
            context['additional_file_formset'] = GameAdditionalFileFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        additional_file_formset = context['additional_file_formset']
        
        if image_formset.is_valid() and additional_file_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            additional_file_formset.instance = self.object
            additional_file_formset.save()
            messages.success(self.request, f'Game "{self.object.title}" created successfully!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class GameUpdateView(SuperUserRequiredMixin, UpdateView):
    """Update an existing game"""
    model = Game
    template_name = 'customadmin/game_form.html'
    form_class = GameForm
    success_url = reverse_lazy('customadmin:game_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        if self.request.POST:
            context['image_formset'] = GameImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
            context['additional_file_formset'] = GameAdditionalFileFormSet(self.request.POST, instance=self.object)
        else:
            context['image_formset'] = GameImageFormSet(instance=self.object)
            context['additional_file_formset'] = GameAdditionalFileFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        additional_file_formset = context['additional_file_formset']
        
        if image_formset.is_valid() and additional_file_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            additional_file_formset.instance = self.object
            additional_file_formset.save()
            messages.success(self.request, f'Game "{self.object.title}" updated successfully!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class GameDeleteView(SuperUserRequiredMixin, DeleteView):
    """Delete a game"""
    model = Game
    template_name = 'customadmin/game_confirm_delete.html'
    success_url = reverse_lazy('customadmin:game_list')


class GameBulkDeleteView(SuperUserRequiredMixin, View):
    """Delete selected games from the games list page."""
    def post(self, request):
        game_ids = request.POST.getlist('game_ids[]') or request.POST.getlist('game_ids')
        if not game_ids:
            messages.warning(request, 'No games selected for deletion.')
            return HttpResponseRedirect(reverse('customadmin:game_list'))

        deleted_count, _ = Game.objects.filter(id__in=game_ids).delete()
        messages.success(request, f'{deleted_count} game records deleted successfully.')
        return HttpResponseRedirect(reverse('customadmin:game_list'))


class ImportGamesForm(forms.Form):
    excel_file = forms.FileField(
        label='Upload Excel File', 
        required=True, 
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text='Upload an Excel file (.xlsx, .xls) or CSV file containing game data'
    )


class ImportGamesView(SuperUserRequiredMixin, TemplateView):
    template_name = 'customadmin/import_games.html'

    def get(self, request, *args, **kwargs):
        form = ImportGamesForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ImportGamesForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            
            # Read file directly into memory (don't save to disk)
            import pandas as pd
            from io import BytesIO
            
            try:
                # Read file content into memory
                file_content = BytesIO(excel_file.read())
                file_name = excel_file.name.lower()
                
                # Validate file format
                if not (file_name.endswith('.xlsx') or file_name.endswith('.xls') or file_name.endswith('.csv')):
                    messages.error(request, '❌ Invalid file format. Please upload .xlsx, .xls, or .csv files only.')
                    return render(request, self.template_name, {'form': form})
                
                # Test if file can be read and validate columns
                try:
                    if file_name.endswith('.csv'):
                        test_df = pd.read_csv(file_content)
                    else:
                        test_df = pd.read_excel(file_content)
                    
                    # Normalize column names for checking
                    columns = [col.strip().lower() for col in test_df.columns]
                    
                    # Check for required columns
                    required_columns = ['game_name', 'console']
                    missing_columns = [col for col in required_columns if col not in columns]
                    
                    if missing_columns:
                        messages.error(
                            request, 
                            f'❌ Wrong template! Missing required columns: {", ".join(missing_columns)}. '
                            f'Required columns are: game_name, console'
                        )
                        return render(request, self.template_name, {'form': form})
                    
                    # Check if file has data
                    if len(test_df) == 0:
                        messages.error(request, '❌ File is empty. Please upload a file with game data.')
                        return render(request, self.template_name, {'form': form})
                    
                    file_content.seek(0)  # Reset file pointer
                    
                except pd.errors.EmptyDataError:
                    messages.error(request, '❌ File is empty or has no data.')
                    return render(request, self.template_name, {'form': form})
                except Exception as e:
                    messages.error(
                        request, 
                        f'❌ Cannot read file. Please ensure it\'s a valid Excel/CSV file with correct column names. '
                        f'Required columns: game_name, console. Error: {str(e)}'
                    )
                    return render(request, self.template_name, {'form': form})
                
            except Exception as e:
                messages.error(request, f'❌ Error reading uploaded file: {str(e)}')
                return render(request, self.template_name, {'form': form})
            
            # Run import in background thread to avoid timeout
            def run_import():
                try:
                    logger.info(f"Starting background import from uploaded file: {excel_file.name}")
                    # Process directly from memory
                    result = importer.import_games_from_memory(file_content, file_name)
                    if result and 'error' in result:
                        logger.error(f"Import validation failed: {result['error']}")
                    else:
                        logger.info("Import completed successfully")
                except Exception as e:
                    logger.error(f"Import failed: {str(e)}")
            
            # Start background thread
            import_thread = threading.Thread(target=run_import, daemon=True)
            import_thread.start()
            
            messages.success(
                request, 
                '✅ Import started in background! The process will continue even if you navigate away. '
                'Check the games list in a few minutes to see the imported games.'
            )
            return HttpResponseRedirect(reverse('customadmin:game_list'))
        return render(request, self.template_name, {'form': form})


class UserListView(SuperUserRequiredMixin, ListView):
    """List users with search and delete capability"""
    model = get_user_model()
    template_name = 'customadmin/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        User = get_user_model()
        qs = User.objects.all().order_by('-id')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(email__icontains=search) | Q(username__icontains=search))
        premium_filter = self.request.GET.get('premium', '').strip()
        if premium_filter == 'yes':
            qs = qs.filter(is_premium=True)
        elif premium_filter == 'no':
            qs = qs.filter(is_premium=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '').strip()
        context['premium_filter'] = self.request.GET.get('premium', '').strip()
        context['total_results'] = context['paginator'].count
        return context



class UserDeleteView(SuperUserRequiredMixin, View):
    """Delete a user and cascade delete related data"""
    def post(self, request, user_id):
        User = get_user_model()
        user = get_object_or_404(User, pk=user_id)
        # Prevent deleting superuser accounts
        if user.is_superuser:
            from django.contrib import messages
            messages.error(request, 'Cannot delete a superuser account.')
            return HttpResponseRedirect(reverse('customadmin:user_list'))

        # Delete related data explicitly
        from games.models import GameReview, GameRating, GameLove
        from notifications.models import DeviceToken, Notification
        GameReview.objects.filter(user=user).delete()
        GameRating.objects.filter(user=user).delete()
        GameLove.objects.filter(user=user).delete()
        DeviceToken.objects.filter(user=user).delete()
        Notification.objects.filter(user=user).delete()

        # Finally delete user
        user.delete()
        from django.contrib import messages
        messages.success(request, 'User and related data deleted successfully.')
        return HttpResponseRedirect(reverse('customadmin:user_list'))


class ReviewListView(SuperUserRequiredMixin, ListView):
    model = GameReview
    template_name = 'customadmin/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 30

    def get_queryset(self):
        from django.db.models import OuterRef, Subquery
        
        # Subquery to get the rating score for each review
        rating_subquery = GameRating.objects.filter(
            user_id=OuterRef('user_id'),
            game_id=OuterRef('game_id')
        ).values('score')[:1]
        
        qs = GameReview.objects.select_related(
            'user', 'game', 'game__emulator'
        ).annotate(
            rating_score=Subquery(rating_subquery)
        ).order_by('-created_at')
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(review__icontains=search) | Q(user__email__icontains=search) | Q(game__title__icontains=search))        
        # Filter by rating (stars)
        rating_filter = self.request.GET.get('rating', '')
        if rating_filter:
            try:
                rating_value = int(rating_filter)
                if 1 <= rating_value <= 5:
                    qs = qs.filter(rating_score=rating_value)
            except ValueError:
                pass
                
        # Filter by stars (integer values only)
        stars = self.request.GET.get('stars', '')
        if stars:
            try:
                stars_int = int(stars)
                if 1 <= stars_int <= 5:
                    qs = qs.filter(rating_score=stars_int)
            except (ValueError, TypeError):
                pass  # Ignore invalid star values
        
        return qs


class ReviewDeleteView(SuperUserRequiredMixin, View):
    def post(self, request, review_id):
        review = get_object_or_404(GameReview, pk=review_id)
        game = review.game  # Store game reference before deletion
        review.delete()
        
        # Recalculate and update only this game's average rating in cache
        from django.core.cache import cache
        from django.db.models import Avg
        
        # Calculate new average rating
        result = game.ratings.aggregate(avg=Avg('score'))
        new_avg_rating = round(result['avg'], 1) if result['avg'] else 0
        
        # Clear all cache keys related to this game's reviews
        # This ensures the app API will show updated review list
        try:
            from django.core.cache import caches
            default_cache = caches['default']
            
            # Clear view cache for reviews endpoint
            if hasattr(default_cache, 'delete_pattern'):
                # Redis backend with pattern support
                default_cache.delete_pattern(f"view_cache:GameViewSet.reviews:*{game.id}*")
                default_cache.delete_pattern(f"view_cache:game-detail*{game.id}*")
            else:
                # Fallback: clear common cache keys
                # Clear all possible review list cache keys for this game
                for page in range(1, 100):  # Clear up to 100 pages of reviews
                    cache.delete(f"view_cache:GameViewSet.reviews:pk={game.id}&page={page}")
                    cache.delete(f"view_cache:GameViewSet.reviews:pk={game.id}")
                    if page > 10:  # Only clear first 10 pages to avoid excessive loops
                        break
                
                # Clear game detail cache
                cache.delete(f"game_{game.id}")
                cache.delete(f"view_cache:game-detail-{game.id}")
        except Exception as e:
            # Log error but don't fail the deletion
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to clear review cache after deletion: {e}")
        
        from django.contrib import messages
        messages.success(request, f'Review deleted successfully. Game rating updated to {new_avg_rating}.')
        return HttpResponseRedirect(reverse('customadmin:review_list'))


class ReviewBulkDeleteView(SuperUserRequiredMixin, View):
    """Delete selected reviews from the reviews list page."""
    def post(self, request):
        review_ids = request.POST.getlist('review_ids[]') or request.POST.getlist('review_ids')
        if not review_ids:
            messages.warning(request, 'No reviews selected for deletion.')
            return HttpResponseRedirect(reverse('customadmin:review_list'))

        deleted_count, _ = GameReview.objects.filter(id__in=review_ids).delete()
        messages.success(request, f'{deleted_count} review records deleted successfully.')
        return HttpResponseRedirect(reverse('customadmin:review_list'))


class EmulatorListView(SuperUserRequiredMixin, ListView):
    """List all emulators with search functionality"""
    model = Emulator
    template_name = 'customadmin/emulator_list.html'
    context_object_name = 'emulators'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Emulator.objects.order_by('-priority', '-id')
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        if context['search']:
            # Use paginator's count (already calculated) instead of re-querying
            context['total_results'] = context['paginator'].count
        return context
        return context


class EmulatorCreateView(SuperUserRequiredMixin, CreateView):
    """Create a new emulator"""
    model = Emulator
    template_name = 'customadmin/emulator_form.html'
    form_class = EmulatorForm
    success_url = reverse_lazy('customadmin:emulator_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        if self.request.POST:
            context['additional_file_formset'] = EmulatorAdditionalFileFormSet(self.request.POST, instance=self.object)
        else:
            context['additional_file_formset'] = EmulatorAdditionalFileFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        additional_file_formset = context['additional_file_formset']
        
        if additional_file_formset.is_valid():
            self.object = form.save()
            additional_file_formset.instance = self.object
            additional_file_formset.save()
            messages.success(self.request, f'Emulator "{self.object.name}" created successfully!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class EmulatorUpdateView(SuperUserRequiredMixin, UpdateView):
    """Update an existing emulator"""
    model = Emulator
    template_name = 'customadmin/emulator_form.html'
    form_class = EmulatorForm
    success_url = reverse_lazy('customadmin:emulator_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        if self.request.POST:
            context['additional_file_formset'] = EmulatorAdditionalFileFormSet(self.request.POST, instance=self.object)
        else:
            context['additional_file_formset'] = EmulatorAdditionalFileFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        additional_file_formset = context['additional_file_formset']
        
        if additional_file_formset.is_valid():
            self.object = form.save()
            additional_file_formset.instance = self.object
            additional_file_formset.save()
            messages.success(self.request, f'Emulator "{self.object.name}" updated successfully!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class EmulatorDeleteView(SuperUserRequiredMixin, DeleteView):
    """Delete an emulator"""
    model = Emulator
    template_name = 'customadmin/emulator_confirm_delete.html'
    success_url = reverse_lazy('customadmin:emulator_list')


# ==================== GENRE VIEWS ====================

class GenreListView(SuperUserRequiredMixin, ListView):
    """List all genres with search functionality"""
    model = Genre
    template_name = 'customadmin/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Genre.objects.order_by('name')
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        if context['search']:
            # Use paginator's count (already calculated) instead of re-querying
            context['total_results'] = context['paginator'].count
        return context
        return context


class GenreCreateView(SuperUserRequiredMixin, CreateView):
    """Create a new genre"""
    model = Genre
    template_name = 'customadmin/genre_form.html'
    fields = ['name']
    success_url = reverse_lazy('customadmin:genre_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class GenreUpdateView(SuperUserRequiredMixin, UpdateView):
    """Update an existing genre"""
    model = Genre
    template_name = 'customadmin/genre_form.html'
    fields = ['name']
    success_url = reverse_lazy('customadmin:genre_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class GenreDeleteView(SuperUserRequiredMixin, DeleteView):
    """Delete a genre"""
    model = Genre
    template_name = 'customadmin/genre_confirm_delete.html'
    success_url = reverse_lazy('customadmin:genre_list')


# Page Management Views
class PageListView(SuperUserRequiredMixin, ListView):
    """List all pages"""
    model = Page
    template_name = 'customadmin/page_list.html'
    context_object_name = 'pages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Page.objects.all().order_by('title')
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        if context['search']:
            # Use paginator's count (already calculated) instead of re-querying
            context['total_results'] = context['paginator'].count
        return context
        return context


class PageCreateView(SuperUserRequiredMixin, CreateView):
    """Create a new page"""
    model = Page
    form_class = PageForm
    template_name = 'customadmin/page_form.html'
    success_url = reverse_lazy('customadmin:page_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class PageUpdateView(SuperUserRequiredMixin, UpdateView):
    """Update an existing page"""
    model = Page
    form_class = PageForm
    template_name = 'customadmin/page_form.html'
    success_url = reverse_lazy('customadmin:page_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class PageDeleteView(SuperUserRequiredMixin, DeleteView):
    """Delete a page"""
    model = Page
    template_name = 'customadmin/page_confirm_delete.html'
    success_url = reverse_lazy('customadmin:page_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Page deleted successfully!')
        return super().delete(request, *args, **kwargs)


class NotificationSendView(SuperUserRequiredMixin, View):
    """Send push notification to all users via FCM Topics"""
    template_name = 'customadmin/notification_send.html'
    
    def get(self, request):
        # Get active device count for display
        active_devices = DeviceToken.objects.filter(is_active=True).count()
        
        context = {
            'active_devices': active_devices,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        notification_type = request.POST.get('notification_type', 'normal').strip()
        
        # Validate required fields
        if not title or not body:
            messages.error(request, 'Title and message are required.')
            return redirect('customadmin:notification_send')
        
        # Validate notification type
        valid_types = ['normal', 'fix', 'update', 'error']
        if notification_type not in valid_types:
            notification_type = 'normal'
        
        # Validate image URL if provided
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            messages.error(request, 'Image URL must be a valid HTTP/HTTPS URL.')
            return redirect('customadmin:notification_send')
        
        try:
            # Send notification using FCM Topics (single API call to all users)
            # Force sending from the admin UI even if automatic notifications are disabled
            log = send_notification_to_all_users_topic(
                title=title,
                body=body,
                notification_type=notification_type,
                data={
                    'sent_from': 'dashboard',
                    'sent_by': request.user.email
                },
                image_url=image_url if image_url else None,
                force=True,
            )
            
            # Show success message
            if log.successful_sends > 0:
                messages.success(
                    request,
                    f'✅ Notification sent to all users via Topics! '
                    f'Check Firebase Console for delivery statistics.'
                )
            else:
                messages.error(
                    request,
                    f'❌ Failed to send notification. Check logs for details.'
                )
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
        
        return redirect('customadmin:notification_send')


class AppSettingsView(SuperUserRequiredMixin, View):
    """View to manage app settings"""
    template_name = 'customadmin/app_settings.html'
    
    def get(self, request):
        # Get or create the app settings (singleton)
        settings, created = AppSettings.objects.get_or_create(
            pk=1,
            defaults={
                'app_version': '1.0.0',
                'app_link': 'https://play.google.com/store/apps/details?id=get.orepsp2.emulatorgame',
                'under_maintenance': False
            }
        )
        form = AppSettingsForm(instance=settings)
        return render(request, self.template_name, {'form': form, 'settings': settings})
    
    def post(self, request):
        settings = AppSettings.objects.get(pk=1)
        form = AppSettingsForm(request.POST, instance=settings)
        
        if form.is_valid():
            form.save()
            messages.success(request, '✅ App settings updated successfully!')
            return redirect('customadmin:app_settings')
        
        messages.error(request, '❌ Please correct the errors below.')
        return render(request, self.template_name, {'form': form, 'settings': settings})


class ExportGamesView(SuperUserRequiredMixin, View):
    """View to export games to Excel file"""
    template_name = 'customadmin/export_games.html'
    
    def get(self, request):
        # Get all emulators for checkbox selection
        emulators = Emulator.objects.all().order_by('name')
        return render(request, self.template_name, {'emulators': emulators})
    
    def post(self, request):
        import pandas as pd
        from django.http import HttpResponse
        from io import BytesIO
        
        # Get selected emulator IDs from checkboxes
        selected_emulator_ids = request.POST.getlist('emulators')
        
        if not selected_emulator_ids:
            messages.error(request, '❌ Please select at least one emulator to export.')
            return redirect('customadmin:export_games')
        
        # Filter games by selected emulators
        games = Game.objects.filter(emulator_id__in=selected_emulator_ids).select_related('emulator').prefetch_related('genres', 'images')
        
        if not games.exists():
            messages.error(request, '❌ No games found for the selected emulator(s).')
            return redirect('customadmin:export_games')
        
        # Prepare data for Excel
        data = []
        for game in games:
            # Get genres as comma-separated string
            genres_str = ', '.join([genre.name for genre in game.genres.all()])
            
            # Get additional images
            images = game.images.all().order_by('order')
            image_urls = {f'image_{i+1}': img.image_path for i, img in enumerate(images[:5])}
            
            row = {
                'game_name': game.title,
                'console': game.emulator.name,
                'priority': game.priority,
                'description': game.description,
                'image_url': game.image_url,
                'image_1': image_urls.get('image_1', ''),
                'image_2': image_urls.get('image_2', ''),
                'image_3': image_urls.get('image_3', ''),
                'image_4': image_urls.get('image_4', ''),
                'image_5': image_urls.get('image_5', ''),
                'size': game.size,
                'download_url': game.download_url,
                'game_url': game.game_url,
                'video_url': game.video_url,
                'region': game.region,
                'genres': genres_str,
                'is_premium': 'true' if game.is_premium else 'false',
                'year': game.year,
            }
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Games', index=False)
        
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Get emulator names for filename
        emulator_names = '_'.join([e.name for e in Emulator.objects.filter(id__in=selected_emulator_ids)[:3]])
        if len(selected_emulator_ids) > 3:
            emulator_names += '_and_more'
        
        filename = f'games_export_{emulator_names}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
