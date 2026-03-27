import re
from os import environ

# Bot Session Name
SESSION = environ.get('SESSION', 'CodeXOTTBot')

# Your Telegram Account Api Id And Api Hash
API_ID = int(environ.get('API_ID', '34552493'))
API_HASH = environ.get('API_HASH', '1a9292b5bd04af88dae7a6d1b5a1da71')

# Bot Token, This Is Main Bot
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# Admin Telegram Account Id For Withdraw Notification Or Anything Else
ADMIN = int(environ.get('ADMIN', '8435221866'))

# Back Up Bot Token For Fetching Message When Floodwait Comes
BACKUP_BOT_TOKEN = environ.get('BACKUP_BOT_TOKEN', "")

# Log Channel, In This Channel Your All File Stored.
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003826113170'))

# Mongodb Database For User Link Click Count Etc Data Store.
MONGODB_URI = environ.get("MONGODB_URI", "")

# Stream Url Means Your Deploy Server App Url, Here You Media Will Be Stream And Ads Will Be Shown.
STREAM_URL = environ.get("STREAM_URL", "")

# This Link Used As Permanent Link That If Your Deploy App Deleted Then You Change Stream Url,
# So This Link Will Redirect To Stream Url.
LINK_URL = environ.get("LINK_URL", "https://codexottlandingpage.blogspot.com/p/codex-ott-landing-page_97.html")

# Others
PORT = environ.get("PORT", "8080")
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
