import os

from django import forms
from django.core.exceptions import ValidationError

from .models import MediaItem
from .validators import ACCEPT_ATTR, validate_media_file


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A file field that accepts several files at once (Django's documented pattern)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": ACCEPT_ATTR}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]


class MediaUploadForm(forms.Form):
    """Upload one or many photos/videos in a single go."""

    files = MultipleFileField(label="Photos & videos")
    title = forms.CharField(
        max_length=150,
        required=False,
        label="Title (optional)",
        help_text="Leave blank to use each file's name. If you add a title and pick several files, a number is added.",
    )
    description = forms.CharField(
        required=False, max_length=1000, label="Description (optional)", widget=forms.Textarea(attrs={"rows": 3})
    )
    category = forms.ChoiceField(choices=MediaItem.Category.choices, initial=MediaItem.Category.OTHER)
    is_featured = forms.BooleanField(
        required=False, label="Feature on the home page", help_text="Tick to show these on the home page."
    )

    def clean_files(self):
        files = self.cleaned_data.get("files") or []
        files = [f for f in files if f]
        if not files:
            raise ValidationError("Please choose at least one photo or video.")
        errors = []
        for f in files:
            try:
                validate_media_file(f)
            except ValidationError as exc:
                errors.extend(exc.messages)
        if errors:
            raise ValidationError(errors)
        return files

    @staticmethod
    def title_from_filename(name):
        stem = os.path.splitext(os.path.basename(name))[0]
        return stem.replace("_", " ").replace("-", " ").strip().title()[:150] or "Untitled"


class MediaItemForm(forms.ModelForm):
    """Edit one existing item. Choosing a new file replaces the old one."""

    class Meta:
        model = MediaItem
        fields = ["title", "description", "category", "file", "is_featured"]
        labels = {"file": "Replace file (optional)", "is_featured": "Feature on the home page"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "file": forms.FileInput(attrs={"accept": ACCEPT_ATTR}),
        }
