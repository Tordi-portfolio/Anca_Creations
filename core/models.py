from django.db import models


class ContactMessage(models.Model):
    class Interest(models.TextChoices):
        PEN_BAR = "pen_bar", "Pen Bar"
        KEYCHAIN_BAR = "keychain_bar", "Keychain Bar"
        DIY_BAR = "diy_bar", "DIY Bar"
        PARTY = "party", "Booking a party"
        FACE_PAINT = "face_paint", "Face paint"
        CUSTOM_GIFT = "custom_gift", "Custom gift order"
        OTHER = "other", "Something else"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    interest = models.CharField(max_length=20, choices=Interest.choices, default=Interest.OTHER)
    message = models.TextField(max_length=3000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} – {self.get_interest_display()} ({self.created_at:%b %d, %Y})"
