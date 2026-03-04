# Deploy VPulse Backend on PythonAnywhere

Follow these steps to deploy this Django backend on [PythonAnywhere](https://www.pythonanywhere.com/).

## 1. Create account and get a project path

- Sign up at https://www.pythonanywhere.com/ (free tier is fine).
- Note your **username**; your app URL will be `https://<username>.pythonanywhere.com`.

## 2. Upload the project

In a **Bash** console on PythonAnywhere:

```bash
cd ~
# Clone your repo (replace with your actual repo URL)
git clone https://github.com/yourusername/your-repo.git
cd your-repo
# If the Django project is in a subfolder (e.g. backend), cd into it
# cd backend
```

Or upload the project via **Files** tab (zip and upload, then unzip).

Make sure the folder that contains `manage.py` and `vpulse_backend/` is your project root.

## 3. Create virtualenv and install dependencies

In the same Bash console (project root = folder with `manage.py`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Environment variables

In the **Web** tab → your web app → **Environment variables**, add:

| Variable          | Example value                                                                 |
|-------------------|-------------------------------------------------------------------------------|
| `SECRET_KEY`      | (generate a new one, see below)                                               |
| `DEBUG`           | `False`                                                                       |
| `ALLOWED_HOSTS`   | `muhammadnumansubhan1.pythonanywhere.com` (already default in settings)      |
| `STATIC_ROOT`     | `/home/muhammadnumansubhan1/yourproject/static/` (replace **yourproject** with your actual project directory name) |
| `CORS_EXTRA_ORIGINS` | Your frontend URL(s), comma-separated (optional)                            |

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

1. **Source code**: set to your project root (the directory that contains `manage.py`).
2. **Working directory**: set to the same project root.
3. **Virtualenv**: set to the path of your venv, e.g. `/home/yourusername/your-repo/venv`.
4. **WSGI configuration file**: click the link to edit the WSGI file (e.g. `/var/www/yourusername_pythonanywhere_com_wsgi.py`).

Replace the contents of that WSGI file with (adjust paths and project name if needed):

```python
import sys
import os

# Project root (directory containing manage.py)
path = '/home/yourusername/your-repo'  # <-- CHANGE THIS
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'vpulse_backend.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `yourusername` and `your-repo` with your actual PythonAnywhere username and project directory name.

## 7. Static and media files (Web tab)

In the **Web** tab, under **Static files**, add mappings that match `STATIC_ROOT` and `MEDIA_ROOT`:

- **URL**: `/static/`  
  **Directory**: `/home/muhammadnumansubhan1/yourproject/static/`  
  (same path as `STATIC_ROOT`; replace **yourproject** with your actual project directory)
- **URL**: `/media/`  
  **Directory**: `/home/muhammadnumansubhan1/yourproject/media`

Then click **Reload** so static files are served correctly.

## 8. Reload the app

Click **Reload** for your web app. The API should be available at:

- API: `https://yourusername.pythonanywhere.com/api/`
- Admin: `https://yourusername.pythonanywhere.com/admin/`
- API docs: `https://yourusername.pythonanywhere.com/api/docs/`

## Troubleshooting

- **500 error**: Check **Web** tab → **Error log** and **Server log**.
- **Static files 404**: Confirm `collectstatic` was run and the static URL/directory mappings match your paths.
- **Import errors**: Ensure the path in the WSGI file is the project root (where `manage.py` and `vpulse_backend` live) and that the virtualenv is set correctly.
