# Django Project

A Django web application built with Python and managed using Poetry for dependency management.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
- **pip**: Usually comes with Python installation
- **Git**: For version control

## Installation

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment

Create a Python virtual environment to isolate project dependencies:

```bash
python -m venv venv
```

This command creates a new directory called `venv` containing the virtual environment.

### 3. Activate Virtual Environment

Activate the virtual environment using the appropriate command for your operating system:

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt, indicating the virtual environment is active.

### 4. Install Poetry

Install Poetry (Python dependency management tool) from the requirements.txt file:

```bash
pip install -r requirements.txt
```

This installs Poetry and any other essential tools specified in requirements.txt.

### 5. Install Project Dependencies

Use Poetry to install all project dependencies defined in `pyproject.toml`:

```bash
poetry install --no-root
```

The `--no-root` flag prevents Poetry from installing the project itself as a package, which is typical for Django applications.

## Configuration

### Environment Variables

The project uses split settings for different environments (development, staging, production). Create a `.env` file in the project root directory to store environment-specific variables:

```bash
cp .env.example .env
```

Edit the `.env` file and configure the following variables:

```env
DJANGO_SETTINGS_MODULE=core.settings.dev
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important:** Never commit your `.env` file to version control. Ensure it's listed in `.gitignore`.

### Settings Structure

The project uses a modular settings structure:

- **`base.py`**: Contains common settings shared across all environments
- **`dev.py`**: Development-specific settings (imports from base.py)
- **`stage.py`**: Staging environment settings (imports from base.py)
- **`prod.py`**: Production settings (imports from base.py)

To specify which settings to use, set the `DJANGO_SETTINGS_MODULE` environment variable or use the `--settings` flag.

### Database Setup

Run migrations to set up your database schema:

```bash
python manage.py migrate --settings=core.settings.dev
```

### Create Superuser (Optional)

Create an admin user to access the Django admin interface:

```bash
python manage.py createsuperuser --settings=core.settings.dev
```

Follow the prompts to set username, email, and password.

### Collect Static Files (Production)

If deploying to production, collect static files:

```bash
python manage.py collectstatic --no-input --settings=core.settings.prod
```

## Running the Application

### Development Server

Start the Django development server using development settings:

```bash
python manage.py runserver --settings=core.settings.dev
```

Or set the environment variable:

```bash
export DJANGO_SETTINGS_MODULE=core.settings.dev  # On macOS/Linux
set DJANGO_SETTINGS_MODULE=core.settings.dev     # On Windows CMD
$env:DJANGO_SETTINGS_MODULE="core.settings.dev"  # On Windows PowerShell

python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

To run on a different port:

```bash
python manage.py runserver 8080 --settings=core.settings.dev
```

To make the server accessible from other devices on your network:

```bash
python manage.py runserver 0.0.0.0:8000 --settings=core.settings.dev
```

### Access Admin Interface

Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

## Development

### Project Structure

```
.
├── venv/                  # Virtual environment (not in git)
├── core/                  # Django project settings directory
│   ├── __init__.py
│   ├── settings/          # Split settings for different environments
│   │   ├── __init__.py
│   │   ├── base.py        # Base settings (shared across all environments)
│   │   ├── dev.py         # Development settings
│   │   ├── stage.py       # Staging settings
│   │   └── prod.py        # Production settings
│   ├── urls.py            # Root URL configuration
│   ├── asgi.py            # ASGI configuration
│   └── wsgi.py            # WSGI configuration
├── apps/                  # Django applications directory
│   ├── __init__.py
│   ├── base/              # Base app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── batch/             # Batch management app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── student/           # Student management app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── users/             # User management app
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── tests.py
├── manage.py              # Django management script
├── requirements.txt       # Poetry installation file
├── pyproject.toml         # Poetry dependencies
├── poetry.lock            # Locked dependency versions
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
└── db.sqlite3             # SQLite database (not in git)
```

### Adding Dependencies

To add a new Python package to the project:

```bash
poetry add package-name
```

For development dependencies only:

```bash
poetry add --group dev package-name
```

### Creating a New Django App

Create a new app inside the `apps` directory:

```bash
cd apps
python ../manage.py startapp app_name
cd ..
```

Or create it from the root directory:

```bash
python manage.py startapp app_name apps/app_name
```

Remember to:
1. Add the new app to `INSTALLED_APPS` in `core/settings/base.py` (use the format `apps.app_name`)
2. Update the app's `apps.py` to reflect the correct path:
   ```python
   class AppNameConfig(AppConfig):
       default_auto_field = 'django.db.models.BigAutoField'
       name = 'apps.app_name'
   ```

### Making Migrations

After modifying models, create migration files:

```bash
python manage.py makemigrations --settings=core.settings.dev
```

Apply migrations to the database:

```bash
python manage.py migrate --settings=core.settings.dev
```

## Testing

Run the test suite:

```bash
python manage.py test --settings=core.settings.dev
```

Run tests with coverage:

```bash
poetry run coverage run --source='.' manage.py test --settings=core.settings.dev
poetry run coverage report
```

Run tests for a specific app:

```bash
python manage.py test apps.student --settings=core.settings.dev
python manage.py test apps.users --settings=core.settings.dev
```

## Deployment

### Pre-deployment Checklist

1. Set `DEBUG=False` in `core/settings/prod.py`
2. Configure a secure `SECRET_KEY` in production environment
3. Set up proper `ALLOWED_HOSTS` in `core/settings/prod.py`
4. Use a production-grade database (PostgreSQL recommended)
5. Configure static file serving
6. Set up HTTPS/SSL certificates
7. Configure logging and monitoring

### Environment-Specific Settings

The project uses different settings modules for each environment:

**Development:**
```bash
python manage.py runserver --settings=core.settings.dev
```

**Staging:**
```bash
python manage.py runserver --settings=core.settings.stage
```

**Production:**
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=core.settings.prod
```

### WSGI Deployment

The project includes a WSGI configuration file for deployment with servers like Gunicorn, uWSGI, or mod_wsgi.

Example with Gunicorn:

```bash
poetry add gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment, try:

```bash
deactivate  # If already in a venv
rm -rf venv  # Remove existing venv
python -m venv venv  # Recreate
```

### Poetry Installation Issues

If Poetry doesn't install correctly from requirements.txt, install it directly:

```bash
pip install poetry
```

### Database Errors

If you encounter database errors, try:

```bash
python manage.py migrate --run-syncdb
```

### Port Already in Use

If port 8000 is already in use:

```bash
python manage.py runserver 8080
```

## License

[Specify your license here]

## Contact

[Your contact information or project maintainer details]

---

**Note:** Always ensure your virtual environment is activated before running any Django or Poetry commands. You can verify this by checking for the `(venv)` prefix in your terminal.