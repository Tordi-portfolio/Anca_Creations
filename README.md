# Anca Creations – Website

A professional, modern Django website for **Anca Creations** (Custom Gifts & Experiences, Harrisonburg VA).

* Public site: Home, Our Story, Experiences, Gallery, Contact (with long-form brand copy)
* **Staff-only dashboard** where the admin uploads/edits/deletes photos and videos about the brand
* Authentication: Django's built-in session auth, staff accounts only, 8-hour sessions, CSRF protection, POST-only logout
* Contact form with spam honeypot and a staff inbox for customer messages

## 1. Run it locally

```bash
cd anca_creations
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations core gallery
python manage.py migrate
python manage.py createsuperuser  # this is the admin account (is_staff is set automatically)
python manage.py runserver
```

Open http://127.0.0.1:8000/

| What | URL |
| --- | --- |
| Public website | `/` |
| Staff login | `/manage/login/` (also linked in the footer as "Staff login") |
| Dashboard | `/manage/` |
| Upload photos & videos | `/manage/media/upload/` |
| Media library (edit/delete) | `/manage/media/` |
| Customer messages | `/manage/messages/` |
| Change password | `/manage/password/` |
| Django admin (optional extra) | `/django-admin/` |

Run the tests: `python manage.py test`

## 2. How authentication works

* There is **no public sign-up**. Only accounts created with `createsuperuser` (or by the admin in `/django-admin/`) can exist.
* Every `/manage/...` page uses `StaffRequiredMixin` (`accounts/mixins.py`):
  * not logged in → redirected to the login page
  * logged in but not `is_staff` → 403 page
* The login form (`accounts/forms.py`) also refuses non-staff accounts.
* To give a second person access: `/django-admin/` → Users → add user → tick **Staff status**.

## 3. Upload rules

* Photos: JPG, PNG, WEBP, GIF up to 10 MB. Videos: MP4, WEBM, MOV up to 200 MB (change in `gallery/validators.py`).
* File extension **and** file signature are checked, so renamed files are rejected.
* Tick "Feature on the home page" to show items in the home-page gallery.
* Deleting an item (or replacing its file) also removes the old file from disk.

## 4. Make it yours

* **Brand details** (address, links, WhatsApp, Instagram): `BRAND` dict in `config/settings.py`.
* **All written content** (services, values, FAQs): `core/content.py`. Please read it through and adjust the wording so it matches how the studio really works. Opening hours and prices are deliberately not included, add them when you have them.
* **Colours / fonts**: CSS variables at the top of `static/css/main.css`.
* **Logo**: the header uses a text wordmark. To use an image, replace the `.wordmark` link in `templates/base.html` with an `<img>` placed in `static/img/`.

## 5. Deploying

Set these environment variables (see `.env.example`): `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`.

```bash
python manage.py collectstatic --noinput
gunicorn config.wsgi
```

* Static files are served by WhiteNoise.
* **Uploaded media is not served by Django when `DEBUG=0`.** Serve `/media/` with nginx/Caddy, or switch `STORAGES["default"]` to cloud storage (e.g. `django-storages` with S3). On hosts with temporary disks (Heroku, Render free tier), you *must* use cloud storage or uploads will disappear.
* For large video uploads, raise your web server's body-size limit (nginx: `client_max_body_size 200M;`).
* SQLite is fine for a small brand site; switch `DATABASES` to PostgreSQL for heavier use.
* Consider `django-axes` for login rate-limiting once the site is public.

## Project layout

```
anca_creations/
├── manage.py
├── requirements.txt
├── config/            settings, root urls, wsgi/asgi
├── core/              public pages, brand copy (content.py), contact form + inbox
├── accounts/          staff login, password change, StaffRequiredMixin
├── gallery/           MediaItem model, validators, public gallery, staff upload/edit/delete
├── templates/         base, core/, gallery/, accounts/, manage/, partials/
└── static/            css/main.css, js/main.js
```
