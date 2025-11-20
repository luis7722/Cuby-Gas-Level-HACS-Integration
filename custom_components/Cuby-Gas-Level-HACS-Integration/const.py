DOMAIN = "cuby_gas"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_DEVICE_IDS = "device_ids"

DATA_COORDINATOR = "coordinator"
DATA_TOKEN = "token"
DATA_TOKEN_EXPIRATION = "token_expiration"

DEFAULT_TOKEN_EXP_SECONDS = 3600
UPDATE_INTERVAL_SECONDS = 60  # Adjust polling frequency as needed

TOKEN_URL_TEMPLATE = "https://cuby.cloud/api/v2/token/{email}"
GAS_URL_TEMPLATE = "https://cuby.cloud/api/v2/history/gas/level/{cuby_id}?token={jwt}"