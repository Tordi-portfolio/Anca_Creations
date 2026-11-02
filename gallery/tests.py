import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MediaItem

TEMP_MEDIA = tempfile.mkdtemp()
PASSWORD = "Str0ng-test-pass-123"
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"0" * 64

PROTECTED_URLS = ["dashboard", "media_list", "media_upload", "messages_manage", "password_change"]


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class MediaAccessAndUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("owner", password=PASSWORD, is_staff=True)
        cls.visitor = User.objects.create_user("visitor", password=PASSWORD)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    # ---- access control -------------------------------------------------
    def test_anonymous_users_are_sent_to_login(self):
        for name in PROTECTED_URLS:
            with self.subTest(url=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response["Location"])

    def test_non_staff_users_are_forbidden(self):
        self.client.force_login(self.visitor)
        for name in PROTECTED_URLS:
            with self.subTest(url=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_staff_can_open_dashboard_pages(self):
        self.client.force_login(self.staff)
        for name in PROTECTED_URLS:
            with self.subTest(url=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    # ---- login ----------------------------------------------------------
    def test_staff_can_log_in(self):
        response = self.client.post(reverse("login"), {"username": "owner", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboard"))

    def test_non_staff_cannot_log_in(self):
        response = self.client.post(reverse("login"), {"username": "visitor", "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "staff only")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(reverse("login"), {"username": "owner", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    # ---- uploads --------------------------------------------------------
    def _upload(self, files, **extra):
        data = {"files": files, "category": "parties", "title": "", "description": ""}
        data.update(extra)
        return self.client.post(reverse("media_upload"), data)

    def test_staff_can_upload_image_and_video(self):
        self.client.force_login(self.staff)
        response = self._upload(
            [
                SimpleUploadedFile("party_day.png", PNG, content_type="image/png"),
                SimpleUploadedFile("pen-bar.mp4", MP4, content_type="video/mp4"),
            ]
        )
        self.assertRedirects(response, reverse("media_list"))
        self.assertEqual(MediaItem.objects.count(), 2)
        self.assertEqual(MediaItem.objects.get(title="Party Day").media_type, "image")
        self.assertEqual(MediaItem.objects.get(title="Pen Bar").media_type, "video")
        self.assertEqual(MediaItem.objects.first().uploaded_by, self.staff)

    def test_rejects_unsupported_extension(self):
        self.client.force_login(self.staff)
        response = self._upload([SimpleUploadedFile("evil.exe", b"MZ" + b"0" * 50)])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MediaItem.objects.count(), 0)

    def test_rejects_file_whose_content_does_not_match_extension(self):
        self.client.force_login(self.staff)
        response = self._upload([SimpleUploadedFile("fake.png", b"<script>alert(1)</script>")])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MediaItem.objects.count(), 0)

    def test_non_staff_cannot_upload(self):
        self.client.force_login(self.visitor)
        response = self._upload([SimpleUploadedFile("a.png", PNG)])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MediaItem.objects.count(), 0)

    def test_anonymous_cannot_upload(self):
        response = self._upload([SimpleUploadedFile("a.png", PNG)])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MediaItem.objects.count(), 0)

    # ---- public gallery & deletion --------------------------------------
    def test_public_gallery_lists_uploaded_items(self):
        item = MediaItem.objects.create(
            title="Studio Shot", category="studio", file=SimpleUploadedFile("studio.png", PNG)
        )
        response = self.client.get(reverse("gallery"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.title)

    def test_gallery_filter_by_category(self):
        MediaItem.objects.create(title="Party One", category="parties", file=SimpleUploadedFile("p.png", PNG))
        MediaItem.objects.create(title="Pen One", category="pen_bar", file=SimpleUploadedFile("q.png", PNG))
        response = self.client.get(reverse("gallery"), {"category": "pen_bar"})
        self.assertContains(response, "Pen One")
        self.assertNotContains(response, "Party One")

    def test_deleting_an_item_removes_its_file(self):
        self.client.force_login(self.staff)
        item = MediaItem.objects.create(title="Temp", file=SimpleUploadedFile("temp.png", PNG))
        path = item.file.path
        self.assertTrue(os.path.exists(path))
        response = self.client.post(reverse("media_delete", args=[item.pk]))
        self.assertRedirects(response, reverse("media_list"))
        self.assertFalse(MediaItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(os.path.exists(path))
