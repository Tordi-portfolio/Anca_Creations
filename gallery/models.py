import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .validators import VIDEO_EXTENSIONS, validate_media_file


class MediaItem(models.Model):
    class Category(models.TextChoices):
        PARTIES = "parties", "Parties & Events"
        PEN_BAR = "pen_bar", "Pen Bar"
        KEYCHAIN_BAR = "keychain_bar", "Keychain Bar"
        DIY_BAR = "diy_bar", "DIY Bar"
        FACE_PAINT = "face_paint", "Face Paint"
        GIFTS = "gifts", "Custom Gifts"
        STUDIO = "studio", "The Studio"
        OTHER = "other", "Other"

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, max_length=1000)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, db_index=True)
    file = models.FileField(upload_to="brand_media/%Y/%m/", validators=[validate_media_file])
    media_type = models.CharField(
        max_length=10, choices=MediaType.choices, default=MediaType.IMAGE, editable=False, db_index=True
    )
    is_featured = models.BooleanField(
        default=False, help_text="Featured items appear on the home page."
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploads"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    @property
    def is_video(self):
        return self.media_type == self.MediaType.VIDEO

    @property
    def is_image(self):
        return self.media_type == self.MediaType.IMAGE

    def save(self, *args, **kwargs):
        ext = os.path.splitext(self.file.name)[1].lower()
        self.media_type = self.MediaType.VIDEO if ext in VIDEO_EXTENSIONS else self.MediaType.IMAGE

        old_name = None
        if self.pk:
            old_name = (
                MediaItem.objects.filter(pk=self.pk).values_list("file", flat=True).first()
            )

        super().save(*args, **kwargs)

        # If the file was replaced, remove the old one from storage.
        if old_name and old_name != self.file.name:
            self.file.storage.delete(old_name)


@receiver(post_delete, sender=MediaItem)
def delete_file_with_item(sender, instance, **kwargs):
    """Remove the file from disk when its database row is deleted."""
    if instance.file:
        instance.file.delete(save=False)
