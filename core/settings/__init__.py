from pathlib import Path
from decouple import config
# Load the .env file


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_ENVIRONMENT = config("DJANGO_ENVIRONMENT", "env")

if DJANGO_ENVIRONMENT == "dev":
    from .dev import *  # noqa
elif DJANGO_ENVIRONMENT == "stage":
    from .stage import *  # noqa
elif DJANGO_ENVIRONMENT == "prod":
    from .prod import *  # noqa
else:
    raise ValueError("Django Environment Not Specified")
