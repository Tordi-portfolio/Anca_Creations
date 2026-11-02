from django.conf import settings
from django.utils import timezone


def brand(request):
    """Make brand details and the current year available in every template."""
    return {"brand": settings.BRAND, "current_year": timezone.now().year}
