from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class PublicPageTests(TestCase):
    def test_public_pages_load(self):
        for name in ["home", "about", "services", "contact", "gallery", "login"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_home_mentions_the_brand(self):
        self.assertContains(self.client.get(reverse("home")), "Anca Creations")


class ContactFormTests(TestCase):
    payload = {
        "name": "Maria",
        "email": "maria@example.com",
        "phone": "",
        "interest": "party",
        "message": "I would love to book a birthday party.",
        "website": "",
    }

    def test_valid_submission_is_saved(self):
        response = self.client.post(reverse("contact"), self.payload)
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_honeypot_blocks_bots(self):
        response = self.client.post(reverse("contact"), {**self.payload, "website": "http://spam.example"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(reverse("contact"), {**self.payload, "email": "nope"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)


class InboxTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("owner", password="Str0ng-test-pass-123", is_staff=True)
        cls.msg = ContactMessage.objects.create(name="A", email="a@example.com", message="Hello")

    def test_toggle_and_delete_need_post_and_staff(self):
        toggle = reverse("message_toggle", args=[self.msg.pk])
        self.assertEqual(self.client.post(toggle).status_code, 302)  # anonymous -> login
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(toggle).status_code, 405)
        self.client.post(toggle)
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_read)
        self.client.post(reverse("message_delete", args=[self.msg.pk]))
        self.assertFalse(ContactMessage.objects.exists())
