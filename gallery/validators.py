import os

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}

MAX_IMAGE_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_BYTES = 200 * 1024 * 1024  # 200 MB

ACCEPT_ATTR = ",".join(sorted(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS))


def _signature_ok(ext, head):
    """Check the first bytes of the file really look like the claimed type."""
    if ext in (".jpg", ".jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == ".gif":
        return head[:6] in (b"GIF87a", b"GIF89a")
    if ext == ".webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext in (".mp4", ".mov"):
        return head[4:8] in (b"ftyp", b"moov", b"mdat", b"free", b"wide")
    if ext == ".webm":
        return head.startswith(b"\x1a\x45\xdf\xa3")
    return False


def validate_media_file(file):
    """Accept only common image/video formats, within size limits, with a matching file signature."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type. Use JPG, PNG, WEBP, GIF, MP4, WEBM or MOV.",
            code="bad_extension",
        )

    try:
        size = file.size
    except (OSError, ValueError):
        return  # file is missing from disk; nothing more to check

    limit = MAX_VIDEO_BYTES if ext in VIDEO_EXTENSIONS else MAX_IMAGE_BYTES
    if size > limit:
        raise ValidationError(
            f"'{file.name}' is too large. The limit is {limit // (1024 * 1024)} MB for this file type.",
            code="too_large",
        )

    # Only sniff brand-new uploads (existing stored files were checked when uploaded).
    if isinstance(file, UploadedFile):
        file.seek(0)
        head = file.read(16)
        file.seek(0)
        if not _signature_ok(ext, head):
            raise ValidationError(
                f"'{file.name}' does not look like a valid {ext[1:].upper()} file.",
                code="bad_signature",
            )
