# L'Étoile Dorée — Luxury Restaurant Web Application

A full-stack, Michelin-inspired restaurant web application built with **Django 5**, featuring interactive menus, dietary filters, real-time table reservations, a slide-over tasting cart drawer, operational staff dashboard, and production-ready configuration for **Render**.

---

## Folder Structure

```text
restraurent_project/
│
├── .gitignore                      # Git ignored files & directories (venv, db, staticfiles)
├── build.sh                        # Render deployment build script (pip, collectstatic, migrate)
├── Procfile                        # Process definition for web workers (Gunicorn)
├── render.yaml                     # Infrastructure-as-Code blueprint for Render
├── runtime.txt                     # Python runtime version pin (3.11.5)
├── requirements.txt                # Production Python dependencies
├── manage.py                       # Django CLI management script
├── README.md                       # Project overview & deployment guide
│
├── restaurant_config/              # Core Django project configuration package
│   ├── __init__.py
│   ├── asgi.py                     # ASGI configuration
│   ├── settings.py                 # Settings (WhiteNoise, dj-database-url, env vars)
│   ├── urls.py                     # Main URL router
│   └── wsgi.py                     # WSGI application for Gunicorn
│
├── restaurant/                     # Restaurant application module
│   ├── __init__.py
│   ├── admin.py                    # Custom-branded Django admin site
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Category, MenuItem, Reservation, Order, Testimonial
│   ├── urls.py                     # App routes (home, api/menu, api/reserve, api/order, dashboard)
│   ├── views.py                    # Views and JSON API endpoints
│   ├── migrations/                 # Database schema migrations
│   └── management/
│       └── commands/
│           └── populate_restaurant.py  # Seeder for 17+ dishes, categories, critic reviews
│
├── static/                         # Source static assets
│   ├── css/
│   │   └── style.css               # Haute gastronomie design system (dark luxury & gold)
│   └── js/
│       └── app.js                  # Interactive client engine (cart drawer, filters, modals)
│
├── templates/                      # HTML5 templates
│   └── restaurant/
│       ├── base.html               # Global layout, navbar, cart drawer, modals, footer
│       ├── index.html              # Landing page, hero, chef's signatures, menu, reservations
│       └── dashboard.html          # Operational staff command center
│
└── venv/                           # Python virtual environment (ignored in git)
```

---

## Deploying to Render (Step-by-Step)

### Option 1: Automatic Blueprint (Recommended)
1. Push this repository to **GitHub** or **GitLab**.
2. Log in to [Render.com](https://dashboard.render.com/).
3. Click **New +** and select **Blueprint**.
4. Connect your repository. Render will automatically detect `render.yaml` and configure:
   - **Runtime:** Python 3.11.5
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn restaurant_config.wsgi:application`
5. Click **Apply**. Render will automatically build, collect static assets, run migrations, and launch your live site!

---

### Option 2: Manual Web Service Setup
1. On the Render Dashboard, click **New +** > **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name:** `letoile-doree-restaurant`
   - **Environment / Runtime:** `Python 3`
   - **Branch:** `main`
   - **Region:** Any (e.g., Oregon or Frankfurt)
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn restaurant_config.wsgi:application`
4. In the **Environment Variables** section, add:
   - `PYTHON_VERSION`: `3.11.5`
   - `DJANGO_SETTINGS_MODULE`: `restaurant_config.settings`
   - `SECRET_KEY`: (Click *Generate* or provide a random 50-character string)
   - `DEBUG`: `false`
   - `RENDER`: `true`
5. Click **Create Web Service**.

---

## Local Development

1. **Activate the Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run Migrations & Seed Data:**
   ```powershell
   python manage.py migrate
   python manage.py populate_restaurant
   ```

4. **Start the Development Server:**
   ```powershell
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Management & Staff Credentials

- **Admin URL:** `/admin/`
- **Dashboard URL:** `/dashboard/`
- **Default Superuser:**
  - **Username:** `admin`
  - **Password:** `adminpassword123`
