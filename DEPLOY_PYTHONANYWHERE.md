# Deploy VPulse Backend on PythonAnywhere

Follow these steps to deploy this Django backend on [PythonAnywhere](https://www.pythonanywhere.com/).

---

## ⚠️ You must run the correct project (vpulse_backend)

The Web app must use **this** project (the one with `vpulse_backend/` and `accounts/`), not a different folder named only `vpulse` with a basic Django site.

- **Wrong:** Code path `/home/.../vpulse` and settings `vpulse.settings` → gives "no such table: auth_user", 404 on `/api/docs`, only `admin/` in URLs.
- **Right:** Code path = the folder that contains **`manage.py`**, **`vpulse_backend/`**, and **`accounts/`**. In the WSGI file use **`vpulse_backend.settings`** and set **`path`** to that folder.

If you see **"Using settings module vpulse.settings"** or **"no such table: auth_user"**, the Web app is still pointing at the wrong project. Fix the **Code** path and **WSGI** file as in sections 2 and 6 below, then **Reload**.

---

## 1. Create account and get a project path

- Sign up at https://www.pythonanywhere.com/ (free tier is fine).
- Note your **username**; your app URL will be `https://<username>.pythonanywhere.com`.

## 2. Upload the project (this repo, not a plain "vpulse" project)

In a **Bash** console on PythonAnywhere:

```bash
cd ~
# Clone THIS backend repo (the one with vpulse_backend and accounts)
git clone https://github.com/yourusername/Dan-l-Project-2-Website-backend.git
cd Dan-l-Project-2-Website-backend
# If the Django app is in a subfolder (e.g. backend), cd into it so you see manage.py and vpulse_backend/
# cd backend
ls -la   # you must see: manage.py  vpulse_backend/  accounts/  requirements.txt
```

Or upload the project via **Files** tab (zip and upload, then unzip).

**Project root** = the directory that contains **`manage.py`**, **`vpulse_backend/`**, and **`accounts/`**. The Web app **Code** path and the WSGI **path** must both point to this directory.

## 3. Create virtualenv and install dependencies

In the same Bash console (project root = folder with `manage.py`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. PythonAnywhere config (in settings.py) and environment variables

**In `vpulse_backend/settings.py`** the PythonAnywhere section defines (edit if your path or username differ):

- `PYTHONANYWHERE_USER` – your PythonAnywhere username
- `PYTHONANYWHERE_PROJECT_DIR` – path to the project folder on the server (must match where you clone the repo)
- `PYTHONANYWHERE_DOMAIN` – used for `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- Static/media roots on PythonAnywhere are derived from `PYTHONANYWHERE_PROJECT_DIR` when running under `/home/`

**In the Web tab → Environment variables**, set only:

| Variable          | Example value                                    |
|-------------------|--------------------------------------------------|
| `SECRET_KEY`      | (generate a new one, see below)                  |
| `DEBUG`           | `False`                                          |
| `CORS_EXTRA_ORIGINS` | Your frontend URL(s), comma-separated (optional) |

Generate a secret key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. Database and collectstatic

In the **Bash** console (with venv activated), from your project root:

```bash
python manage.py migrate
python manage.py collectstatic
```

This gathers all static files into the directory set by `STATIC_ROOT` (e.g. `/home/muhammadnumansubhan1/yourproject/static/` if you set that in env). Use `--noinput` to skip prompts:

```bash
python manage.py collectstatic --noinput
```

Optional:

```bash
python manage.py createsuperuser
python manage.py create_default_admin
```

## 6. Web app configuration

In the **Web** tab:

1. **Source code**: set to your project root (the directory that contains `manage.py` and the `vpulse_backend` folder).
2. **Working directory**: set to the same project root.
3. **Virtualenv**: set to the path of your venv, e.g. `/home/muhammadnumansubhan1/your-repo/venv`.
4. **WSGI configuration file**: click the link to edit the WSGI file (e.g. `/var/www/muhammadnumansubhan1_pythonanywhere_com_wsgi.py`).

**Important:** Django must use **`vpulse_backend.settings`** (not `vpulse.settings`). The URLconf is `vpulse_backend.urls`, which defines `/api/docs/`, `/admin/`, etc. If you use the wrong project name, you will get 404 on `/api/docs`.

Replace the contents of that WSGI file with:

```python
import sys
import os

# Project root: the directory that contains manage.py and the vpulse_backend package
path = '/home/muhammadnumansubhan1/your-repo'  # <-- Replace your-repo with your actual project folder name
if path not in sys.path:
    sys.path.insert(0, path)

# Must be vpulse_backend.settings (this loads vpulse_backend.urls with api/docs, api/, admin/)
os.environ['DJANGO_SETTINGS_MODULE'] = 'vpulse_backend.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Use your **actual** project directory. For example if you cloned into `Dan-l-Project-2-Website-backend` and the folder that contains `manage.py` is that one, then:
`path = '/home/muhammadnumansubhan1/Dan-l-Project-2-Website-backend'`
If your backend is inside a `backend` subfolder: `path = '/home/muhammadnumansubhan1/YourRepoName/backend'`.

## 7. Static and media files (Web tab)

In the **Web** tab, under **Static files**, add mappings. Paths are set in `settings.py` (`PYTHONANYWHERE_PROJECT_DIR`):

- **URL**: `/static/`  
  **Directory**: `{PYTHONANYWHERE_PROJECT_DIR}/static` (e.g. `/home/muhammadnumansubhan1/Dan-l-Project-2-Website-backend/static`)
- **URL**: `/media/`  
  **Directory**: `{PYTHONANYWHERE_PROJECT_DIR}/media`

Then click **Reload** so static files are served correctly.

## 8. Reload the app

Click **Reload** for your web app. The API should be available at:

- API: `https://yourusername.pythonanywhere.com/api/`
- Admin: `https://yourusername.pythonanywhere.com/admin/`
- API docs: `https://yourusername.pythonanywhere.com/api/docs/`

## Troubleshooting

- **"no such table: auth_user"** or **"Using settings module vpulse.settings"** – The app is running a different project (plain `vpulse`), not this backend. This backend uses `accounts.User` (table `accounts_user`), not `auth.User`. Do this: (1) In **Web** → **Code**, set the path to the folder that contains **manage.py**, **vpulse_backend/**, and **accounts/** (e.g. `Dan-l-Project-2-Website-backend` or `.../backend`). (2) In the **WSGI file**, set `path = '/home/muhammadnumansubhan1/YourActualProjectFolder'` and `os.environ['DJANGO_SETTINGS_MODULE'] = 'vpulse_backend.settings'`. (3) Reload. Then in a Bash console **in that project directory** run `python manage.py migrate` (and create a superuser if needed).
- **404 on `/api/docs`** – Same cause: wrong project (vpulse.urls instead of vpulse_backend.urls). Fix the Code path and WSGI as above; use `vpulse_backend.settings`.
- **500 error**: Check **Web** tab → **Error log** and **Server log**.
- **Static files 404**: Confirm `collectstatic` was run in the correct project and the static URL/directory mappings match your paths.
- **Import errors**: Ensure the path in the WSGI file is the project root (where `manage.py` and `vpulse_backend` live) and that the virtualenv is set correctly.
