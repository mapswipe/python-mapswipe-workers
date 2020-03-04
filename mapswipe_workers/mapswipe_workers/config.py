import os

SERVICE_ACCOUNT_KEY_PATH = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

FIREBASE_API_KEY = os.environ["FIREBASE_API_KEY"]
FIREBASE_DB = os.getenv("FIREBASE_DB", default="mapswipe")

POSTGRES_DB = os.getenv("POSTGRES_DB", default="mapswipe")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", default="mapswipe_workers")

FIREBASE_DB = os.getenv("FIREBASE_DB", default="mapswipe")

# TODO: Default values?
# TODO: Which are still in use?
IMAGE_BING_API_KEY = os.environ["IMAGE_BING_API_KEY"]
IMAGE_MAXAR_STANDARD_API_KEY = ["IMAGE_MAXAR_STANDARD_API_KEY"]
IMAGE_MAXAR_PREMIUM_API_KEY = ["IMAGE_MAXAR_PREMIUM_API_KEY"]

SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", default=None)
SLACK_TOKEN = os.getenv("SLACK_TOKEN", default=None)
SENTRY_DSN = os.getenv("SENTRY_DSN", default=None)
