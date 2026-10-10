from django import forms
from games.models import Game, Emulator, Genre, GameImage, GameAdditionalFile, EmulatorAdditionalFile, AppSettings
from pages.models import Page
from ckeditor.widgets import CKEditorWidget


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'description', 'emulator', 'priority', 'image_url', 'size', 
                  'download_url', 'game_url', 'video_url', 'region', 'is_premium', 'year', 'genres']
        widgets = {
            'genres': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter game description...'}),
            'year': forms.TextInput(attrs={'type': 'text', 'placeholder': 'e.g., 2005', 'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'value': '0'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg', 'class': 'form-control'}),
            'download_url': forms.URLInput(attrs={'placeholder': 'https://example.com/game.zip', 'class': 'form-control'}),
            'game_url': forms.URLInput(attrs={'placeholder': 'https://example.com/game-page', 'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/watch?v=...', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500MB, 2GB'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USA, Europe, Japan'}),
            'emulator': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'description': 'Detailed description of the game',
            'priority': 'Higher number = appears first (100=featured, 0=normal, -100=hidden)',
            'download_url': 'Direct download link (supports .zip, .7z, .rar, .iso, etc.)',
            'game_url': 'Link to game information page or external site',
            'video_url': 'Link to game trailer or gameplay video (YouTube, etc.)',
            'genres': 'Select one or more genres for this game',
        }


class EmulatorForm(forms.ModelForm):
    class Meta:
        model = Emulator
        fields = ['name', 'priority', 'icon', 'package_name', 'download_url', 'video_url', 'open_outside']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'value': '0'}),
            'package_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., com.example.app'}),
            'download_url': forms.URLInput(attrs={'placeholder': 'https://example.com/emulator.zip', 'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/watch?v=...', 'class': 'form-control'}),
            'open_outside': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'icon': 'Upload emulator icon image',
            'priority': 'Higher number = appears first (100=featured, 0=normal, -100=hidden)',
            'package_name': 'Optional Android package name for deep-linking (e.g., com.example.app)',
            'download_url': 'Link to download the emulator',
            'video_url': 'Link to emulator tutorial or demo video',
            'open_outside': 'If checked, emulator will open in external browser/app instead of in-app webview',
        }


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class GameImageForm(forms.ModelForm):
    class Meta:
        model = GameImage
        fields = ['image_path', 'image_file']
        widgets = {
            'image_path': forms.URLInput(attrs={
                'placeholder': 'https://example.com/screenshot.jpg', 
                'class': 'form-control image-url-input'
            }),
            'image_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }
        help_texts = {
            'image_path': 'Enter URL OR upload a file below (not both)',
            'image_file': 'Upload image file OR enter URL above (not both)'
        }
    
    def clean(self):
        """Ensure only one of image_path or image_file is filled, not both."""
        cleaned_data = super().clean()
        image_path = cleaned_data.get('image_path')
        image_file = cleaned_data.get('image_file')
        
        # Check if both are filled
        if image_path and image_file:
            raise forms.ValidationError(
                "Please provide either an image URL or upload a file, not both."
            )
        
        # Check if neither is filled (unless being deleted)
        if not image_path and not image_file and not self.cleaned_data.get('DELETE'):
            raise forms.ValidationError(
                "Please provide either an image URL or upload a file."
            )
        
        return cleaned_data


# Create formset for managing multiple game images
GameImageFormSet = forms.inlineformset_factory(
    Game, 
    GameImage, 
    form=GameImageForm,
    extra=1,  # Show 1 empty form by default
    can_delete=True,
    min_num=0,
    validate_min=False,
    can_order=False,
)


class GameAdditionalFileForm(forms.ModelForm):
    class Meta:
        model = GameAdditionalFile
        fields = ['file_name', 'download_link', 'file_path']
        widgets = {
            'file_name': forms.TextInput(attrs={
                'placeholder': 'e.g., Patch 1.5, DLC Pack, HD Mod', 
                'class': 'form-control'
            }),
            'download_link': forms.TextInput(attrs={
                'placeholder': 'https://example.com/file.zip', 
                'class': 'form-control'
            }),
            'file_path': forms.TextInput(attrs={
                'placeholder': 'e.g., patches/v1.5, dlc/extra_content', 
                'class': 'form-control'
            }),
        }
        help_texts = {
            'file_name': 'Name/description of the additional file',
            'download_link': 'Download URL for this file',
            'file_path': 'File path or identifier (optional)',
        }


# Create formset for managing multiple game additional files
GameAdditionalFileFormSet = forms.inlineformset_factory(
    Game, 
    GameAdditionalFile, 
    form=GameAdditionalFileForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
    can_order=False,
)


class EmulatorAdditionalFileForm(forms.ModelForm):
    class Meta:
        model = EmulatorAdditionalFile
        fields = ['file_name', 'download_link', 'file_path']
        widgets = {
            'file_name': forms.TextInput(attrs={
                'placeholder': 'e.g., BIOS Files, Graphics Plugin', 
                'class': 'form-control'
            }),
            'download_link': forms.TextInput(attrs={
                'placeholder': 'https://example.com/file.zip', 
                'class': 'form-control'
            }),
            'file_path': forms.TextInput(attrs={
                'placeholder': 'e.g., bios/ps2, plugins/graphics', 
                'class': 'form-control'
            }),
        }
        help_texts = {
            'file_name': 'Name/description of the additional file',
            'download_link': 'Download URL for this file',
            'file_path': 'File path or identifier (optional)',
        }


# Create formset for managing multiple emulator additional files
EmulatorAdditionalFileFormSet = forms.inlineformset_factory(
    Emulator, 
    EmulatorAdditionalFile, 
    form=EmulatorAdditionalFileForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
    can_order=False,
)


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., about, help, support'
            }),
            'content': CKEditorWidget(config_name='default'),
        }
        help_texts = {
            'title': "Unique page identifier (lowercase, no spaces)",
        }


class AppSettingsForm(forms.ModelForm):
    class Meta:
        model = AppSettings
        fields = ['app_version', 'app_link', 'under_maintenance', 'show_popup', 'popup_title', 'popup_description', 'popup_link', 'device_mode_required']
        widgets = {
            'app_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1.0.0, 2.3.1'
            }),
            'app_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://play.google.com/store/apps/details?id=...'
            }),
            'under_maintenance': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_popup': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'popup_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Update Available'
            }),
            'popup_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter popup message...',
                'rows': 3
            }),
            'popup_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/update'
            }),
            'device_mode_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_device_mode_required',
            }),
        }
        help_texts = {
            'app_version': 'Current version of the mobile app',
            'app_link': 'Link to the app on Google Play Store',
            'under_maintenance': 'Enable this to put the app in maintenance mode',
            'show_popup': 'Show popup dialog to users in the app',
            'popup_title': 'Title text for the popup dialog',
            'popup_description': 'Description/message text for the popup',
            'popup_link': 'Optional: Link/URL for popup action button',
        }
