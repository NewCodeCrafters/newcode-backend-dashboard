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
git clone https://github.com/NewCodeCrafters/newcode-backend-dashboard.git
cd newcode-backend-dashboard
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

Create a `.env` file in the project root directory to store environment-specific variables:

```bash
cp .env.example .env
```

Edit the `.env` file and configure the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important:** Never commit your `.env` file to version control. Ensure it's listed in `.gitignore`.

### Database Setup

Run migrations to set up your database schema:

```bash
python manage.py migrate
```

### Create Superuser (Optional)

Create an admin user to access the Django admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### Collect Static Files (Production)

If deploying to production, collect static files:

```bash
python manage.py collectstatic --no-input
```

## Running the Application

### Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

To run on a different port:

```bash
python manage.py runserver 8080
```

To make the server accessible from other devices on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

### Access Admin Interface

Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

## Development

### Project Structure

```
project-root/
├── venv/                  # Virtual environment (not in git)
├── manage.py              # Django management script
├── requirements.txt       # Poetry installation file
├── pyproject.toml         # Poetry dependencies
├── poetry.lock            # Locked dependency versions
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
├── app_name/              # Django app directory
│   ├── migrations/        # Database migrations
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   └── tests.py           # Test cases
└── project_name/          # Project settings directory
    ├── settings.py        # Django settings
    ├── urls.py            # Root URL configuration
    └── wsgi.py            # WSGI configuration
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

```bash
python manage.py startapp app_name
```

Remember to add the new app to `INSTALLED_APPS` in `settings.py`.

### Making Migrations

After modifying models, create migration files:

```bash
python manage.py makemigrations
```

Apply migrations to the database:

```bash
python manage.py migrate
```

## Testing

Run the test suite:

```bash
python manage.py test
```

Run tests with coverage:

```bash
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```

Run tests for a specific app:

```bash
python manage.py test app_name
```

## Deployment

### Pre-deployment Checklist

1. Set `DEBUG=False` in production environment
2. Configure a secure `SECRET_KEY`
3. Set up proper `ALLOWED_HOSTS`
4. Use a production-grade database (PostgreSQL recommended)
5. Configure static file serving
6. Set up HTTPS/SSL certificates
7. Configure logging and monitoring

### Environment-Specific Settings

Consider using different settings files for different environments:

```bash
python manage.py runserver --settings=project_name.settings.production
```

### WSGI Deployment

The project includes a WSGI configuration file for deployment with servers like Gunicorn, uWSGI, or mod_wsgi.

Example with Gunicorn:

```bash
poetry add gunicorn
gunicorn project_name.wsgi:application --bind 0.0.0.0:8000
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