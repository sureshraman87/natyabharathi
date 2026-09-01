# Deploying to natyabharathi.sureshraman.com

This guide deploys the site to a single Linux server (Ubuntu/Debian
assumed) using **Gunicorn** (application server) behind **Nginx** (reverse
proxy + static files + TLS), managed by **systemd**, with **Let's Encrypt**
for HTTPS. It uses SQLite by default (fine for a low-traffic content site);
switch to Postgres by setting `DATABASE_URL` if you expect heavier load.

## 0. Before you start

- A server (VPS) with a public IP, reachable via SSH.
- DNS: create an **A record** (and `AAAA` if you have an IPv6 address)
  pointing both of these at the server's IP:
  - `natyabharathi.sureshraman.com`
  - `www.natyabharathi.sureshraman.com`
  DNS propagation can take a few minutes to a few hours.

## 1. Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git certbot python3-certbot-nginx
```

## 2. Create a deploy user and directory (optional but recommended)

```bash
sudo mkdir -p /var/www/natyabharathi
sudo chown -R "$USER":www-data /var/www/natyabharathi
```

## 3. Get the code onto the server

```bash
cd /var/www/natyabharathi
git clone <this-repo-url> .
# or: git pull origin main   (if the directory already has the repo)
```

## 4. Python environment

```bash
cd /var/www/natyabharathi
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

## 5. Configure environment variables

```bash
cp .env.example .env
nano .env   # or vim/your editor of choice
```

Set at minimum:

```ini
DJANGO_SECRET_KEY=<generate a real one, see below>
DEBUG=False
DJANGO_ALLOWED_HOSTS=natyabharathi.sureshraman.com,www.natyabharathi.sureshraman.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://natyabharathi.sureshraman.com,https://www.natyabharathi.sureshraman.com
DJANGO_SECURE_SSL_REDIRECT=True
# DATABASE_URL=postgres://user:password@localhost:5432/natyabharathi   # optional, defaults to SQLite
```

Generate a secret key:

```bash
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` is loaded automatically by Django (via `django-environ`) and is
git-ignored — it never gets committed.

## 6. Initialize the database and static files

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py collectstatic --noinput
```

Optional: seed a few sample courses to confirm things render, then replace
them with real content via `/admin/`:

```bash
.venv/bin/python manage.py seed_demo_content
```

## 7. Gunicorn as a systemd service

The unit file runs Gunicorn as `www-data`, but everything up to now (the
`git clone`, the venv, `pip install`) was done as your own login user. Give
the `www-data` group read/execute access to the project — including the
venv's `bin/` executables — before starting the service, otherwise you'll
hit `status=203/EXEC ... Permission denied`:

```bash
sudo chgrp -R www-data /var/www/natyabharathi
sudo chmod -R g+rX /var/www/natyabharathi
sudo find /var/www/natyabharathi -type d -exec chmod g+s {} \;
```

The last command sets the setgid bit on every directory so that files
created by future `git pull` / `pip install` runs (from `deploy.sh`) keep
inheriting the `www-data` group automatically — you shouldn't need to
repeat this after every deploy.

Copy the provided unit file and adjust the paths only if you didn't use
`/var/www/natyabharathi`:

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/natyabharathi.service
sudo systemctl daemon-reload
sudo systemctl enable --now natyabharathi
sudo systemctl status natyabharathi
```

This runs Gunicorn listening on a Unix socket at
`/run/natyabharathi/gunicorn.sock`, which Nginx will proxy to.

## 8. Nginx reverse proxy

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/natyabharathi
sudo ln -s /etc/nginx/sites-available/natyabharathi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

At this point `http://natyabharathi.sureshraman.com` should load the site
(over plain HTTP).

## 9. Enable HTTPS

```bash
sudo certbot --nginx -d natyabharathi.sureshraman.com -d www.natyabharathi.sureshraman.com
```

Certbot edits the Nginx config to add the HTTPS server block and redirect
HTTP → HTTPS, and sets up automatic renewal (`systemctl status certbot.timer`
to confirm). Since `.env` already has `DJANGO_SECURE_SSL_REDIRECT=True`,
Django will also enforce HTTPS at the application level.

## 10. Verify

- Visit `https://natyabharathi.sureshraman.com/` — should load with a valid
  padlock.
- Visit `https://natyabharathi.sureshraman.com/admin/` and log in.
- Add a course/lesson (see the "Adding a course and lesson" section in
  `README.md`) and confirm it appears on the public site.

## Ongoing deploys (shipping new code/content)

```bash
cd /var/www/natyabharathi
./deploy/deploy.sh
```

This script pulls the latest commit, reinstalls dependencies, runs
migrations, collects static files, and restarts Gunicorn + reloads Nginx.
Review it and adjust the branch name (`main`) if your default branch is
named differently.

## Backups

The only state that matters is the database and any uploaded media:

- SQLite: back up `db.sqlite3`.
- Postgres: use `pg_dump`.
- Uploaded course thumbnails / self-hosted videos: back up the `media/`
  directory.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| 502 Bad Gateway | Gunicorn isn't running — check `sudo systemctl status natyabharathi` and `sudo journalctl -u natyabharathi -e`. |
| `status=203/EXEC` / `Failed to execute .../gunicorn: Permission denied` | The `www-data` user can't traverse into or execute something under `/var/www/natyabharathi/.venv` (usually because the venv was created by your login user with a restrictive umask). Run `namei -l /var/www/natyabharathi/.venv/bin/gunicorn` to find the exact directory missing an `x` bit, then re-run the `chgrp`/`chmod g+rX`/`chmod g+s` commands in step 7. If `findmnt -T /var/www/natyabharathi -o OPTIONS` shows `noexec`, the fix is to move the project off that mount instead. |
| `DisallowedHost` error | The domain isn't in `DJANGO_ALLOWED_HOSTS` in `.env`. |
| CSS/images missing (plain HTML) | `collectstatic` wasn't run, or Nginx's `/static/` alias path doesn't match `STATIC_ROOT`. |
| Admin login redirects/fails oddly | `DJANGO_CSRF_TRUSTED_ORIGINS` doesn't include the `https://` origin you're visiting. |
| Certbot fails | DNS for the domain isn't pointing at this server yet, or port 80 isn't reachable (check firewall/security group). |
