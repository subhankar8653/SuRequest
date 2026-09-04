from os import environ

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
ADMINS = int(environ.get("ADMINS", ""))

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "suhani_joinbot")

# If this is True Then Bot Accept New Join Request
# NOTE: bool("False") is True in Python (any non-empty string is truthy),
# so the old `bool(environ.get(...))` made this ALWAYS True whenever the
# env var was set to anything at all — including the literal text "False".
# Compare the string value instead.
NEW_REQ_MODE = environ.get('NEW_REQ_MODE', 'False').strip().lower() in ('1', 'true', 'yes', 'on')
